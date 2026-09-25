# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""
The per-photo image endpoints: retouching, reverting, publishing and generating
lifestyle or worn variants of ONE photo of one product, and reading where its
imagery has got to.

None of this is the listing agent. `alaiy_os_agents` owns the one listing agent
per site and the whole-product enrichment that goes with it; these endpoints
are the other thing the image pipeline is used for — an admin working photo by
photo on a product's gallery, from a portal screen rather than from a run.

They live here because the image pipeline does. `image_stage` queues the work and
`image_generation` renders it, both in this app, and every one of these is a thin
whitelisted wrapper that resolves the photo, queues a step, and returns. The work
itself is the same stage two an agent run queues — same queue, same renderer,
same rows — so a photo retouched from a portal button and one retouched by a run
are indistinguishable afterwards, which is the point.

`enrich_listing_image` is the odd one out in one respect: it runs a single tool
rather than a whole run, and so it is the only caller that narrows the work to
named photos (`source_urls`) or pays for a photo twice (`force`). Neither is in
the listing agent's declared tool schema, deliberately — a run enriching a
product always covers all of its photos and never pays twice.

`preview_lifestyle_image` and `preview_worn_image` are a different shape
again: synchronous, not queued, because a single Photoroom call is fast
enough to just wait for. Neither touches the photo it was made from, and
neither writes anything to the enriched listing — a preview is a standalone
file nobody has agreed to keep yet (see `accept_additional_image`). The two
generators differ in what they promise about the product: a lifestyle photo
keeps the product's own pixels untouched (only the background is generated);
a worn photo does not — putting something on a model means generating the
scene around it, so it is a styled render, never a stand-in for the
authoritative product photo.

Everything else here queues and returns; poll `get_listing_images`.
"""

import base64
import json

import frappe
from frappe.utils import cint, sbool

from alaiy_os_connector_shopify.listing.handlers import ENRICHED_DOCTYPE


def _flag(value):
    """A checkbox argument as 0/1, however the caller expressed it.

    `cint` alone is not enough and fails silently, which is worse than throwing:
    frappe.call JSON-encodes any non-string argument, so a ticked box arrives as
    the string "true" — and cint("true") is 0, not 1. That turned every toggle
    from the Desk dialog off without a word. sbool resolves "true"/"false"/"1"/"0"
    first and passes anything else through for cint to handle.
    """
    return cint(sbool(value))


@frappe.whitelist()
def enrich_listing_image(item_code, source_url, force=0):
    """
    Retouch ONE photo of one product — the per-photo "Enrich" button.

        POST {"item_code": "SH-123", "source_url": "https://cdn.../a.jpg"}
        -> {item_code, source_url, image_status, queued, url, targets}

    Returns as soon as the work is queued. `url` is null when `queued` is true and
    the retouched photo lands on the listing minutes later — poll
    `get_listing_images` and watch for THAT ROW's url to fill in. Nothing else about
    the listing is touched: the enrichment writes one image row (and its variants'
    copies of the same photo), and no text, attribute or review field moves.

    `source_url` must be a photo this product actually has — one of the Shopify
    Product Listing's own images, or an enabled variant's `variant_image`. Anything
    else is refused, so this endpoint can retouch a catalog photo and nothing else;
    it is not a general "render me this url" service.

    A photo used in more than one place — the listing's own gallery and a variant's,
    or two variants sharing one shot — is rendered ONCE and written to every row that
    references it, each keeping its own `item_variant` so approval still routes it to
    the right variant. `targets` says how many rows this call will fill.

    Already retouched? Nothing is spent: the existing photo comes straight back with
    `queued: false`. Pass `force=1` to render it again anyway, which is the way to
    redo a result a reviewer was unhappy with.

    If the product has never been enriched there is no Shopify Enriched Listing to
    deliver into, so a Draft one is created holding just this image. Draft rather
    than Needs Review on purpose — retouching a photo is not a listing anyone asked
    a human to read yet, and it must not appear in the review queue as though it
    were.
    """
    from alaiy_os_connector_shopify.listing import image_stage
    from alaiy_os_connector_shopify.listing import handlers as base
    from alaiy_os_connector_shopify.listing.image_generation import (
        already_enhanced,
        generate_product_images,
    )

    if not frappe.has_permission("OS Agent Run", "create"):
        # The same gate as a run, for the same reason: this spends real money at a
        # paid image service, so it is not open to every logged-in user.
        frappe.throw("Not permitted.", frappe.PermissionError)
    if not frappe.db.exists(base.LISTING_DOCTYPE, item_code):
        frappe.throw(f"No {base.LISTING_DOCTYPE} found for item_code '{item_code}'.")

    listing = frappe.get_doc(base.LISTING_DOCTYPE, item_code)
    listing.check_permission("read")

    # Which rows this photo fills: the listing's own gallery entry, plus every
    # enabled variant using the same shot. Settled here, from the product, so the
    # caller cannot name a photo the product does not have — and so a shared photo
    # reaches all of its rows off one render.
    targets = [
        {"source_url": source_url, "item_variant": None}
        for url in base.listing_image_urls(listing)
        if url == source_url
    ]
    targets += [
        {"source_url": source_url, "item_variant": item_variant}
        for item_variant, url in base.variant_image_map(listing).items()
        if url == source_url
    ]
    if not targets:
        frappe.throw(
            f"'{source_url}' is not a photo of {item_code}. Only this product's own "
            "images and its enabled variants' images can be enriched."
        )

    force = _flag(force)
    if not force:
        existing = already_enhanced(item_code).get(source_url)
        if existing:
            # Free, and idempotent: a second click on a photo that is already done
            # costs nothing and returns the same answer as the first.
            return {
                "item_code": item_code,
                "source_url": source_url,
                "image_status": frappe.db.get_value(
                    ENRICHED_DOCTYPE, item_code, "image_status"
                ),
                "queued": False,
                "url": existing,
                "targets": len(targets),
            }

    _ensure_enriched_listing(item_code, listing)

    # Empty whatever this photo's rows already hold, so the result replaces it rather
    # than being appended beside it — see image_stage.clear_rendered. Always, not just
    # when forcing: a seeded row holds the original photo, and a re-render holds the
    # previous result, and neither would be matched by the new url.
    image_stage.clear_rendered(item_code, source_url)

    # generate_images=True because asking for this endpoint IS the opt-in — the
    # toggle exists so that a *run* does not enhance images unless someone asked.
    # source_urls narrows the tool to this one photo; without it the tool would
    # (correctly, for a run) queue every photo the product has.
    generate_product_images(
        item_code=item_code,
        generate_images=True,
        source_urls=[source_url],
        force=force,
    )

    # So the poll has something truthful to say between now and the worker starting.
    # The job itself fires on this request's commit (enqueue_after_commit), so this
    # write and the queued work stand or fall together.
    frappe.db.set_value(
        ENRICHED_DOCTYPE, item_code, "image_status", "Queued", update_modified=False
    )

    return {
        "item_code": item_code,
        "source_url": source_url,
        "image_status": "Queued",
        "queued": True,
        "url": None,
        "targets": len(targets),
    }


@frappe.whitelist(methods=["POST"])
def revert_listing_image(item_code, source_url):
    """Discard the retouched version of ONE photo — the per-photo "revert to
    original", the counterpart of enrich_listing_image.

        POST {"item_code": "SH-123", "source_url": "https://cdn.../a.jpg"}
        -> {item_code, source_url, reverted}

    This is a real revert, not a preview: the rows for this photo are emptied, and
    _sync_images publishes a row with no result as the photo it was made from. So
    approving the listing afterwards keeps the original, exactly as though this
    photo had never been enriched. Nothing else about the listing moves.

    Free and idempotent — reverting a photo that holds no result is a no-op that
    reports `reverted: 0` rather than throwing, so a double click costs nothing.

    The render itself is NOT unspent: the money went when the image was made. To
    get a retouched version back, call enrich_listing_image again, which will
    render afresh because there is no longer a result to hand back.
    """
    from alaiy_os_connector_shopify.listing import image_stage
    from alaiy_os_connector_shopify.listing import handlers as base

    if not frappe.db.exists(base.LISTING_DOCTYPE, item_code):
        frappe.throw(f"No {base.LISTING_DOCTYPE} found for item_code '{item_code}'.")
    if not frappe.db.exists(ENRICHED_DOCTYPE, item_code):
        # Never enriched, so there is nothing to take back. Not an error: the same
        # "already in the state you asked for" answer as reverting an empty row.
        return {"item_code": item_code, "source_url": source_url, "reverted": 0}

    # check_permission("write"), not "read": this changes what approval will
    # publish, so it needs the same rights as editing the enrichment by hand.
    frappe.get_doc(ENRICHED_DOCTYPE, item_code).check_permission("write")

    rows = frappe.get_all(
        "Shopify Enriched Listing Image",
        filters={"parent": item_code, "parenttype": ENRICHED_DOCTYPE, "source_url": source_url},
        fields=["name", "url"],
    )
    if not rows:
        frappe.throw(
            f"'{source_url}' has no enriched version on {item_code}, so there is "
            "nothing to revert."
        )

    filled = [row for row in rows if row.url]
    if filled:
        image_stage.clear_rendered(
            item_code,
            source_url,
            note="Reverted to the original photo by a reviewer.",
        )
        # Committed immediately: the render this discards was already paid for at
        # the image service, and a poller reading image_status right after this
        # request must see the revert, not whatever this request cycle would
        # otherwise commit on.
        frappe.db.commit()  # nosemgrep: frapsec-manual-commit

    return {"item_code": item_code, "source_url": source_url, "reverted": len(filled)}


@frappe.whitelist(methods=["POST"])
def ensure_enriched_listing(item_code):
    """
    The product's Shopify Enriched Listing, created as a seeded Draft if it has
    none. Returns its name (which is the item_code).

    Exists for the same reason the image step needs it: a record keyed to the
    product is the only place a change can be staged for approval, and a product
    nobody has enriched has none. An admin editing an attribute by hand is that
    same case, so it goes through the same seeding -- a Draft copy of what the
    product already says, which approval writes back over itself as a no-op
    except for the one field that was actually edited.
    """
    from alaiy_os_connector_shopify.listing import handlers as base

    if not frappe.db.exists(base.LISTING_DOCTYPE, item_code):
        frappe.throw(f"No {base.LISTING_DOCTYPE} found for item_code '{item_code}'.")
    listing = frappe.get_doc(base.LISTING_DOCTYPE, item_code)
    # "write", not "read": this seeds a Shopify Enriched Listing draft that an
    # admin can then edit -- the same rights as editing the enrichment by hand,
    # matching revert_listing_image and publish_listing_images below.
    listing.check_permission("write")
    # Nothing is owed on the imagery here -- no render was queued, this is a hand
    # edit -- so the row must not claim otherwise. save_listing's own rule: every
    # seeded photo already has its url, so "Ready", and no photos is "Not
    # Required". Left at the image step's "Queued" it would tell the reviewer
    # pictures were on their way that nobody asked for.
    image_status = "Ready" if base.listing_image_urls(listing) else "Not Required"
    _ensure_enriched_listing(item_code, listing, image_status=image_status)
    return item_code


def _ensure_enriched_listing(item_code, listing, image_status="Queued"):
    """The row stage two delivers into, seeded from the product if it has none.

    image_stage.run_step gives up when there is no Shopify Enriched Listing, so a
    product that has never been through the agent would render its photo and then
    have nowhere to put it.

    The new row is a COPY of what the product already says, not an empty shell. That
    matters because approval does not patch the listing, it overwrites it: it assigns
    every text field and rebuilds the images and metafields tables from this record
    (see ShopifyEnrichedListing._push_to_listing). Approving a blank record would
    therefore erase the product's title, description, category and every photo the
    image step did not happen to touch. Seeded, the same approval writes the
    product's own values back over themselves — a no-op — and the one retouched photo
    is the only thing that actually changes. Nothing here is invented: every value
    comes from the product itself.

    Draft rather than Needs Review: retouching a photo is not a listing anyone asked
    a human to read, and it must not join the review queue pretending otherwise.
    """
    from alaiy_os_connector_shopify.listing import handlers as base

    if frappe.db.exists(ENRICHED_DOCTYPE, item_code):
        return

    doc = frappe.new_doc(ENRICHED_DOCTYPE)
    doc.item_code = item_code
    doc.status = "Draft"
    # "Queued" by default because the caller this was written for is stage two of
    # the image pipeline, which is about to add a row with no url yet.
    doc.image_status = image_status

    # The listing -> enriched field mapping save_listing documents, read backwards.
    doc.title = listing.listing_title
    doc.description = listing.listing_description
    doc.category = listing.listing_category
    doc.product_type = listing.listing_product_type
    doc.seo_title = listing.get("listing_seo_title")
    doc.seo_description = listing.get("listing_seo_description")

    # Metafields are what the attributes table publishes back as, so they round-trip
    # through it. A product with none simply seeds none.
    #
    # Only the namespace this app publishes into. Approval merges the attributes
    # table into the listing's metafields under that one namespace, so seeding a
    # key another app owns (`uploadify_product.watch_papers`) would not round-trip
    # it -- it would copy it into `custom` and leave the store with two.
    for key, value in base.published_attributes(listing).items():
        doc.append("attributes", {"key": key, "value": value})

    # Every photo the product has, as a row that already holds it: `url` is the photo
    # itself, since nothing better exists yet, and `kind="hero"` is what _sync_images
    # maps back to source "Original" — so an untouched photo returns as the original
    # it is, not relabelled as something the agent made.
    for url in base.listing_image_urls(listing):
        doc.append("images", {"kind": "hero", "source_url": url, "url": url})
    for item_variant, url in base.variant_image_map(listing).items():
        doc.append("images", {
            "kind": "hero",
            "item_variant": item_variant,
            "source_url": url,
            "url": url,
        })

    # ignore_permissions=True: both callers (enrich_listing_image,
    # ensure_enriched_listing above) already check permission on the source
    # listing before reaching this private helper.
    doc.insert(ignore_permissions=True)


@frappe.whitelist(methods=["POST"])
def publish_listing_images(item_code):
    """Commit this product's retouched photos to its live listing.

        POST {"item_code": "SH-123"} -> {item_code, published, images}

    The imagery half of an approval, on its own. Retouched photos land on the
    Shopify Enriched Listing and reach the product only when something applies
    them, and until now the only thing that did was approving the whole
    enrichment. That left a photo-only retouch with no way out at all: it is
    written as a Draft (retouching a photo is not a listing anyone asked a human
    to read), and the admin's Save only approves a draft that is Needs Review —
    so the photo sat marked "pending approval" with nothing able to approve it.

    This publishes the imagery and NOTHING else. No title, no description, no
    attributes, and `is_enriched` is left alone: cleaning up a background does
    not make a listing's copy reviewed, and a product should not have to accept
    text it never asked for to get its photos.

    It shares ShopifyEnrichedListing.apply_images with approval rather than
    reimplementing the mapping, so the two routes cannot disagree about what a
    row means. Approving afterwards stays safe — it applies the same rows again,
    over themselves.

    Idempotent, and refuses rather than pretends: a product with no enrichment
    record, or one whose photos are all still rendering or failed, is told so.
    """
    if not frappe.db.exists(ENRICHED_DOCTYPE, item_code):
        frappe.throw("This product has no retouched photos to save.")

    enriched = frappe.get_doc(ENRICHED_DOCTYPE, item_code)
    enriched.check_permission("write")

    produced = [row for row in (enriched.images or []) if row.url]
    if not produced:
        frappe.throw("None of this product's photos have finished rendering yet.")

    listing = frappe.get_doc(base_listing_doctype(), item_code)
    enriched.apply_images(listing)
    # ignore_permissions=True: `enriched.check_permission("write")` above already
    # gated this call; `listing` is the same product's other doctype, not a
    # second, unchecked write surface.
    listing.save(ignore_permissions=True)
    # Committed immediately so the poll this endpoint's caller makes right after
    # sees the publish, not whatever this request cycle would otherwise commit on.
    frappe.db.commit()  # nosemgrep: frapsec-manual-commit

    return {
        "item_code": item_code,
        "published": len(produced),
        "images": [row.url for row in produced],
    }



# remove_background (the "lifestyle" capability) preserves the SOURCE photo's
# own resolution unless told otherwise - unlike stage_product/editWithAI (the
# "worn" capability), which Photoroom documents as always outputting at a
# fixed 1024x1024 regardless of input size. A hero shot uploaded at an
# unusually high resolution round-trips through Photoroom and back out
# still that large, and `save_public_image` writes it straight to a Frappe
# public File - whose 10MB cap then throws MaxFileSizeReachedError (HTTP
# 417) on save, the same failure a caller saw in production. Bounding the
# longer side here keeps every "lifestyle" output comfortably inside that
# cap without touching photos that were already a sane size.
_LIFESTYLE_MAX_DIMENSION = 2048


def _bounded_output_size(source, max_dimension=_LIFESTYLE_MAX_DIMENSION):
    """A Photoroom `outputSize` string ("WxH") capping the source photo's
    longer side at `max_dimension`, or None if it's already within it.
    """
    import io

    from PIL import Image

    with Image.open(io.BytesIO(base64.b64decode(source["data"]))) as img:
        width, height = img.size
    longest = max(width, height)
    if longest <= max_dimension:
        return None
    scale = max_dimension / longest
    return f"{max(1, round(width * scale))}x{max(1, round(height * scale))}"


def _generate_additional_image_bytes(client, kind, source_url, query):
    """Call the right Photoroom capability for `kind`. Returns (bytes, media_type).

    Shared by generation and regeneration, so the two can never drift on which
    capability or parameters a kind maps to.
    """
    from alaiy_os_connector_shopify.listing import images

    source = images.reference_source(source_url)
    if kind == "lifestyle":
        result = client.remove_background(
            images.data_uri(source),
            background_prompt=query,
            shadow="soft",
            output_size=_bounded_output_size(source),
        )
    else:
        # stage_product ("Product Staging"), not virtual_model: Photoroom
        # scopes virtual_model to clothing and stage_product to "hard goods,
        # accessories, bags, jewelry, shoes" - the better fit for a
        # watch/jewelry catalogue. Same no-pixel-fidelity caveat either way.
        # No output-size cap here: Photoroom documents editWithAI as always
        # outputting at a fixed 1024x1024 regardless of input size, so this
        # capability isn't exposed to the same oversized-file failure.
        result = client.stage_product(images.data_uri(source), prompt=query)
    return base64.b64decode(result["b64"]), result.get("media_type") or "image/png"


@frappe.whitelist(methods=["POST"])
def preview_lifestyle_image(item_code, source_url, query):
    """
    Generate a lifestyle variant of ONE photo from a free-text query, WITHOUT
    saving it anywhere on the product yet.

        POST {"item_code": "SH-123", "source_url": "https://cdn.../a.jpg",
              "query": "on a marble countertop"}
        -> {"item_code": ..., "source_url": ..., "url": "https://.../lifestyle-abc.png",
            "kind": "lifestyle", "query": "on a marble countertop"}

    The result is a standalone public File — real bytes, a real url, nothing
    fake about the preview — but nothing on the Shopify Enriched Listing
    changes. `accept_additional_image` is what actually keeps it (appends the
    row); `discard_preview_image` cleans up the file if the reviewer doesn't
    want it. Explicit accept/reject on purpose: this spends real money at a
    paid image service per attempt, and the query is often wrong the first
    try — nobody should have to "remove" a result to say no to it.

    Uses Photoroom's `background.prompt` (via `remove_background`), which keeps
    the product's own pixels untouched and only generates a new background/scene
    from the query — the same guarantee the house finish and every retouch step
    already rely on: the product is never redrawn, however the photo behind it
    changes.
    """
    url = _generate_additional_preview(item_code, source_url, "lifestyle", query, require_query=True)
    return {"item_code": item_code, "source_url": source_url, "url": url, "kind": "lifestyle", "query": query}


@frappe.whitelist(methods=["POST"])
def preview_worn_image(item_code, source_url, prompt=None):
    """
    Generate a "worn" variant of one photo — the product held, worn, or set
    in a full lifestyle scene — WITHOUT saving it anywhere yet. Same shape as
    `preview_lifestyle_image`; see its docstring for why there's a separate
    accept step.

    UNLIKE a lifestyle photo, this does NOT promise the product's own pixels
    survive untouched — staging a scene around it means regenerating the
    product too, via Photoroom's `stage_product` ("Product Staging" — its own
    docs scope this to "hard goods, accessories, bags, jewelry, shoes",
    unlike `virtual_model`, which is clothing-only and this kind used to
    call). Treat the result as a styled render for marketing, never as a
    stand-in for the authoritative product photo — one more reason an
    explicit accept matters here.

    `prompt` is optional free-text scene guidance — see
    `alaiy_os.engine.llm.stage_product`.
    """
    url = _generate_additional_preview(item_code, source_url, "worn", prompt, require_query=False)
    return {"item_code": item_code, "source_url": source_url, "url": url, "kind": "worn", "query": prompt}


@frappe.whitelist(methods=["POST"])
def preview_regenerate_additional_image(item_code, source_url, url):
    """
    Generate a FRESH candidate for an already-accepted lifestyle/worn photo,
    from its own stored query, WITHOUT touching the accepted row.

        POST {"item_code": "SH-123", "source_url": "https://cdn.../a.jpg",
              "url": "https://.../lifestyle-abc.png"}
        -> {"item_code": ..., "source_url": ..., "kind": "lifestyle",
            "url": "https://.../lifestyle-xyz.png", "query": "...",
            "original_url": "https://.../lifestyle-abc.png"}

    The accepted row (found by `source_url` + `url` + kind in
    `handlers.ADDITIONAL_IMAGE_KINDS`) is read for its kind and `brief`
    (the query to rerun) and otherwise left exactly as it is — the tile still
    shows the old accepted photo until `accept_additional_image` is called
    with `replace_url` set to this response's `original_url`, or
    `discard_preview_image` throws the candidate away and the old photo
    stands.
    """
    from alaiy_os_connector_shopify.listing import handlers as base

    if not frappe.db.exists(ENRICHED_DOCTYPE, item_code):
        frappe.throw(f"'{url}' has no additional photo to regenerate.")

    doc = frappe.get_doc(ENRICHED_DOCTYPE, item_code)
    doc.check_permission("write")

    row = next(
        (
            r for r in (doc.images or [])
            if r.source_url == source_url and r.url == url and r.kind in base.ADDITIONAL_IMAGE_KINDS
        ),
        None,
    )
    if not row:
        frappe.throw(f"'{url}' is not an additional photo on {item_code}, so it cannot be regenerated.")

    new_url = _generate_additional_preview(item_code, source_url, row.kind, row.brief, require_query=False)
    return {
        "item_code": item_code, "source_url": source_url, "kind": row.kind,
        "url": new_url, "query": row.brief, "original_url": url,
    }


def _generate_additional_preview(item_code, source_url, kind, query, require_query):
    """
    The shared body of `preview_lifestyle_image` / `preview_worn_image` /
    `preview_regenerate_additional_image`. `kind` must be one of
    `handlers.ADDITIONAL_IMAGE_KINDS`. Returns the preview's own url — never
    touches the Shopify Enriched Listing.
    """
    from alaiy_os.engine import llm

    from alaiy_os_connector_shopify.listing import handlers as base
    from alaiy_os_connector_shopify.listing import images

    if not frappe.has_permission("OS Agent Run", "create"):
        # Same gate as enrich_listing_image: this spends real money at a paid
        # image service.
        frappe.throw("Not permitted.", frappe.PermissionError)
    query = (query or "").strip() or None
    if require_query and not query:
        frappe.throw("A query describing the scene is required.")
    if not frappe.db.exists(base.LISTING_DOCTYPE, item_code):
        frappe.throw(f"No {base.LISTING_DOCTYPE} found for item_code '{item_code}'.")

    listing = frappe.get_doc(base.LISTING_DOCTYPE, item_code)
    listing.check_permission("read")

    client = llm.image_client()
    capability = "remove_background" if kind == "lifestyle" else "stage_product"
    if not client.image_support().get(capability):
        frappe.throw(
            f"{kind.capitalize()} photos are not available on this site (the "
            f"active AI client cannot {'remove backgrounds' if kind == 'lifestyle' else 'stage product photos'})."
        )

    content, media_type = _generate_additional_image_bytes(client, kind, source_url, query)
    return images.save_public_image(f"listing-{kind}", content, media_type)


@frappe.whitelist(methods=["POST"])
def accept_additional_image(item_code, source_url, kind, url, query=None, replace_url=None):
    """
    Commit a preview from `preview_lifestyle_image` / `preview_worn_image` /
    `preview_regenerate_additional_image` onto the product's gallery — the
    reviewer's explicit "keep this" for a generated photo.

        POST {"item_code": "SH-123", "source_url": "https://cdn.../a.jpg",
              "kind": "lifestyle", "url": "https://.../lifestyle-abc.png",
              "query": "on a marble countertop"}
        -> {"item_code": ..., "source_url": ..., "url": ..., "kind": "lifestyle"}

    Without `replace_url`: appends a brand-new ADDITIONAL row — the normal
    "generate, like it, keep it" path. Never a replacement of anything else:
    the same way a second variant's photo sits beside the first rather than
    overwriting it. `query` is kept on the row's `brief` field, both for a
    reviewer's benefit and because `preview_regenerate_additional_image` reads
    it back to run the same request again. Seeds a Draft Shopify Enriched
    Listing first if the product has never been enriched — an additional shot
    is not a listing anyone asked a human to read, and must not join the
    review queue pretending otherwise.

    With `replace_url`: this is accepting a REGENERATED candidate over an
    already-accepted photo — updates that row's `url` in place (matched by
    `source_url` + `replace_url` + kind), rather than appending a second row,
    so accepting a regenerated result never multiplies the gallery.
    `publish_listing_images` (or approving the listing) is what puts either
    case on the live product afterwards, the same as any other photo on this
    table.
    """
    from alaiy_os_connector_shopify.listing import handlers as base

    if kind not in base.ADDITIONAL_IMAGE_KINDS:
        frappe.throw(f"'{kind}' is not a valid additional photo kind.")
    if not frappe.db.exists(base.LISTING_DOCTYPE, item_code):
        frappe.throw(f"No {base.LISTING_DOCTYPE} found for item_code '{item_code}'.")

    listing = frappe.get_doc(base.LISTING_DOCTYPE, item_code)
    listing.check_permission("write")
    query = (query or "").strip() or None

    if replace_url:
        if not frappe.db.exists(ENRICHED_DOCTYPE, item_code):
            frappe.throw(f"'{replace_url}' has no additional photo to replace.")
        doc = frappe.get_doc(ENRICHED_DOCTYPE, item_code)
        doc.check_permission("write")
        row = next(
            (
                r for r in (doc.images or [])
                if r.source_url == source_url and r.url == replace_url and r.kind in base.ADDITIONAL_IMAGE_KINDS
            ),
            None,
        )
        if not row:
            frappe.throw(f"'{replace_url}' is not an additional photo on {item_code}, so it cannot be replaced.")
        row.url = url
        if query is not None:
            row.brief = query
    else:
        _ensure_enriched_listing(item_code, listing)
        doc = frappe.get_doc(ENRICHED_DOCTYPE, item_code)
        doc.check_permission("write")
        # Idempotent against a double accept of the SAME preview (a
        # double-click, a retried request): `url` is a freshly-generated
        # filename unique to one preview call, so two DIFFERENT previews can
        # never collide here — only the same one, accepted twice, can. Saves
        # a silent duplicate row rather than appending a second one that
        # renders as though the reviewer asked for the same photo twice.
        already = any(
            r.source_url == source_url and r.url == url and r.kind == kind
            for r in (doc.images or [])
        )
        if not already:
            doc.append("images", {"kind": kind, "source_url": source_url, "url": url, "brief": query})

    # ignore_permissions=True: `listing.check_permission("write")` above (and,
    # on the replace_url branch, `doc.check_permission("write")` too) already
    # gated this write — the same pattern _push_to_listing/enrich_listing_image
    # use, not a second, unchecked write surface.
    doc.save(ignore_permissions=True)
    # Committed immediately, like publish_listing_images/revert_listing_image:
    # a caller polling get_listing_images right after this request must see the
    # new row, not whatever this request cycle would otherwise commit on.
    frappe.db.commit()  # nosemgrep: frapsec-manual-commit

    return {"item_code": item_code, "source_url": source_url, "url": url, "kind": kind}


@frappe.whitelist(methods=["POST"])
def discard_preview_image(url):
    """
    Delete a generated-but-never-accepted preview's standalone file — the
    reviewer's explicit "no" for a generated photo they don't want, so
    rejecting one doesn't leave an orphaned upload sitting on disk forever.

        POST {"url": "https://.../lifestyle-abc.png"} -> {"discarded": 1}

    Refuses to touch anything still in use: a url any Shopify Enriched
    Listing Image row currently points at (i.e. one that WAS accepted) is
    left alone rather than deleted out from under it — this is for a preview
    nobody kept, never for an accepted photo (that's `remove_additional_image`).
    Free and idempotent: discarding a url that isn't a standalone File at all
    (already cleaned up, or never one to begin with) reports `discarded: 0`
    rather than throwing.

    Unlike every other endpoint here, there is no item_code and no listing to
    check_permission against — `images.save_public_image` deliberately
    attaches the preview to nothing. Gated instead on the same permission
    generating one required (`OS Agent Run` create), and restricted to a File
    whose name actually matches what save_public_image produces for an
    additional photo (`listing-<kind>-...`) — without both, this would be a
    generic "delete any File on the site by its public url" primitive, not a
    preview-cleanup one, for any caller who could guess or discover a url.
    """
    from alaiy_os_connector_shopify.listing import handlers as base

    if not frappe.has_permission("OS Agent Run", "create"):
        frappe.throw("Not permitted.", frappe.PermissionError)
    if frappe.db.exists("Shopify Enriched Listing Image", {"url": url}):
        return {"discarded": 0}
    file_name = frappe.db.get_value("File", {"file_url": url}, "name")
    if not file_name:
        return {"discarded": 0}
    if not any(file_name.startswith(f"listing-{kind}-") for kind in base.ADDITIONAL_IMAGE_KINDS):
        return {"discarded": 0}
    # ignore_permissions=True: the has_permission check above already gates
    # this call, and a standalone preview File — attached to nothing — has no
    # owning document a normal Frappe permission check would even evaluate
    # against.
    frappe.delete_doc("File", file_name, ignore_permissions=True, delete_permanently=True)
    frappe.db.commit()  # nosemgrep: frapsec-manual-commit
    return {"discarded": 1}


@frappe.whitelist(methods=["POST"])
def remove_additional_image(item_code, source_url, url):
    """
    Discard one ALREADY-ACCEPTED additional (lifestyle/worn) photo — the
    counterpart of `accept_additional_image` for a photo an admin kept before
    but has since changed their mind about. A preview nobody has accepted yet
    is `discard_preview_image`'s job instead; this one only ever touches a
    row that is actually on the record.

        POST {"item_code": "SH-123", "source_url": "https://cdn.../a.jpg",
              "url": "https://.../lifestyle-abc.png"}
        -> {"item_code": ..., "removed": 1}

    UNLIKE `revert_listing_image` (which blanks a hero row back to "pending"
    because stage two might still deliver into it), this DELETES the row
    outright: an additional photo has no render lifecycle to preserve — once
    it's gone, generating another one is a fresh `preview_lifestyle_image` /
    `preview_worn_image` and `accept_additional_image` call, not a re-render
    of something already queued.

    Matched on `source_url` AND `url` together, not `source_url` alone: two
    additional photos (a lifestyle shot and a worn shot, or two of the same
    kind from different queries) can share a source_url, and only the one
    actually shown for removal should go. Restricted to
    `handlers.ADDITIONAL_IMAGE_KINDS` so this can never be used to delete a
    hero or variant row — those are `revert_listing_image`'s job.

    Free and idempotent: removing a photo that's already gone (a double
    click, or one removed from another tab) reports `removed: 0` rather than
    throwing.
    """
    from alaiy_os_connector_shopify.listing import handlers as base

    if not frappe.db.exists(ENRICHED_DOCTYPE, item_code):
        return {"item_code": item_code, "removed": 0}

    doc = frappe.get_doc(ENRICHED_DOCTYPE, item_code)
    doc.check_permission("write")

    keep = []
    removed = 0
    for row in doc.images or []:
        if (
            row.source_url == source_url
            and row.url == url
            and row.kind in base.ADDITIONAL_IMAGE_KINDS
        ):
            removed += 1
            continue
        keep.append(row)

    if removed:
        doc.set("images", keep)
        # ignore_permissions=True: `doc.check_permission("write")` above
        # already gated this write, the same pattern accept_additional_image
        # uses — not a second, unchecked write surface.
        doc.save(ignore_permissions=True)
        # Committed immediately, like the accept half: a caller polling
        # get_listing_images right after this request must see it gone.
        frappe.db.commit()  # nosemgrep: frapsec-manual-commit

    return {"item_code": item_code, "removed": removed}


def base_listing_doctype():
    from alaiy_os_connector_shopify.listing import handlers as base

    return base.LISTING_DOCTYPE


@frappe.whitelist()
def get_listing_images(item_code):
    """
    One product's imagery and where it has got to — the poll for
    `enrich_listing_image`, and also how a caller sees the additional photos
    `accept_additional_image` committed (`kind` in
    `handlers.ADDITIONAL_IMAGE_KINDS`; those are never `pending`, since
    accepting one is a synchronous write, not a queued render). A preview
    nobody has accepted yet never shows up here — it exists only as the
    standalone file `preview_lifestyle_image` / `preview_worn_image` /
    `preview_regenerate_additional_image` returned, until it is accepted or
    discarded.

        {item_code, image_status, image_error, image_tokens,
         images: [{source_url, item_variant, url, cutout_url, note, kind,
                   brief, pending}, ...]}

    `brief` is free text describing how an additional photo was generated (a
    lifestyle photo's query, or a worn photo's model/scene notes) — null on
    every other row.

    `pending` is the one to watch per photo: true while that photo is still
    being rendered. A row that is mid-render and a row whose render failed both
    have no url and both carry a note, so a caller cannot tell them apart from
    `note` alone — and reading the in-flight note as a failure means giving up
    on a photo seconds before it lands.

    `cutout_url` is the retouched product clipped to a transparent background,
    when the site's house style keeps one — the same picture as `url` without the
    ground behind it, so a caller can put it on a different background without
    paying to render the photo again. Null everywhere else.

    **Watch the row, not the listing.** `image_status` is a property of the whole
    listing, and photo-by-photo enrichment puts several jobs in flight at once: the
    first to finish flips it to Ready while the others are still rendering. A caller
    waiting on one photo should poll until that photo's own row has a `url` (or a
    `note` explaining why it never will). `image_status` is for showing the listing's
    overall state, not for deciding one photo is done.

    Returns empty images and a null status for a product that has never been
    enriched, rather than throwing — "nothing here yet" is a normal answer for a UI
    asking about a product before anyone has enriched it.
    """
    # Imported here, like everywhere else in this module: image_stage reaches
    # back into bulk, which this module imports at the top.
    from alaiy_os_connector_shopify.listing import image_stage

    if not frappe.db.exists(ENRICHED_DOCTYPE, item_code):
        return {
            "item_code": item_code,
            "image_status": None,
            "image_error": None,
            "image_tokens": 0,
            "images": [],
        }

    doc = frappe.get_doc(ENRICHED_DOCTYPE, item_code)
    doc.check_permission("read")

    return {
        "item_code": item_code,
        "image_status": doc.image_status,
        "image_error": doc.image_error,
        "image_tokens": doc.image_tokens or 0,
        "images": [
            {
                "source_url": row.source_url,
                "item_variant": row.item_variant,
                "url": row.url,
                "cutout_url": row.cutout_url,
                "note": row.note,
                # How an additional photo was generated (see
                # _generate_and_save_additional_image) — null on every other row.
                "brief": row.brief,
                "kind": row.kind,
                # Whether this photo is still coming. Without it a caller has to
                # infer that from `note`, and the in-flight note reads exactly
                # like a failure note — see image_stage.is_pending.
                "pending": image_stage.is_pending(row.url, row.note),
            }
            for row in (doc.images or [])
        ],
    }