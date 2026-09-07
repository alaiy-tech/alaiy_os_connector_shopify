# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""Shopify, as a channel-agnostic listing agent sees it.

The intended consumer owns one listing agent and knows nothing about any
marketplace. Everything Shopify wants -- its fields, its rules, its validator,
and how to read and write a listing -- arrives from here, through the
`listing_channels` hook in this app's hooks.py.

    prompts/listing.md        Shopify's rules, handed to the model by the spec
    listing/fields.json       Shopify's own output fields
    listing/validate.py       the same rules again, in Python, enforced on save
    listing/handlers.py       reading a product and writing the enriched one
    doctype/shopify_enriched_listing/   the review record itself

## Why this lives in the connector

It used to be its own app, `alaiy_os_agent_shopify_listing`. What was genuinely
Shopify's in it -- the fields, the rules, the doctypes -- is knowledge about *the
channel*, and the app that already owns the channel is this one: it holds
`Shopify Product Listing`, it speaks the Admin API, and it is what a site
installs when it decides to sell on Shopify. The Amazon connector made the same
move for the same reason.

## One listing agent, and it is not ours

`alaiy_os_agents` owns a single channel-agnostic listing agent (`agent_id:
listing`) for the whole site, and reaches this connector through the
`listing_channels` hook. It owns the run, the prompt scaffolding and the desk
surfaces; this app owns the channel knowledge and nothing else.

So the standalone `shopify_listing` agent that came with the retired app is
**not** re-registered here, and neither are its run-agent page, its Enrich
buttons or its bulk-enrichment flow. Keeping them would put two listing agents
on one bench, which is the thing the migration existed to remove. The Amazon
connector draws the same line.

`listing/review.py` is the one exception, and it is not part of the agent: the
list view's bulk Approve is a human act on the review record, and nothing in the
handlers below can reach it.

## The keyword names below are the contract's, not this app's

Every handler is called with keywords fixed by `alaiy_os_agents`'s `channels.py`
-- `fn(product=...)`, `fn(product=..., listing=...)`, `fn(product=...,
enabled=..., image_urls=...)`. An adapter is free to give the function it wraps
whatever signature suits it, and translating between the two vocabularies is the
whole job of the wrappers here: core never learns that Amazon calls its
identifier `sku` and Shopify calls it `item_code`.

## Shopify is the first channel with an image step

Amazon declares no `prepare_images` handler, because the producing side never
moved across, and its prompt tells the model the step is absent. Here it did move:
`image_generation.py`, `image_translation.py` and `image_stage.py` came over with
everything else, so the handler is declared.

Declaring it is the whole signal -- `has_image_step` is not a key in the returned
dict on either side, it is what the consumer derives from this handler being
present. That makes Shopify the first channel to exercise that half of the
contract, which is where an interface gap will show up first.

## No health handler

Amazon declares one because Amazon adjudicates listings and publishes an issues
feed per SKU. Shopify reports no equivalent -- it does not review listings and
does not suppress them -- which is why `health` is an optional capability in the
contract rather than part of it. `pack_meta.py`'s `get_listing_gaps` is the
nearest thing and it is deliberately our own judgement, not the channel's.

## Why validate() and not a stricter schema

JSON Schema cannot express most of what makes a Shopify listing bad. It can say
`maxLength: 320`; it cannot say "no promotional filler from this list of
phrases", "state the unit inside the value", or "the SEO copy is not the on-page
copy repeated". Those are the rules a listing gets rejected or embarrassed by,
and they are all ordinary Python. See `validate.py`.

The rules being written twice -- once as prose for the model, once as code -- is
deliberate and not duplication to remove. The prose is what gets the listing
right the first time; the code is what makes sure.
"""

import json
from pathlib import Path

import frappe

_APP = "alaiy_os_connector_shopify"
_DIR = Path(__file__).resolve().parent
_SELF = f"{_APP}.listing.channel"

CHANNEL = "shopify"
LABEL = "Shopify"
LISTING_DOCTYPE = "Shopify Product Listing"
ENRICHED_DOCTYPE = "Shopify Enriched Listing"


def channel():
    """The adapter. Registered via `listing_channels` in hooks.py."""
    return {
        "channel": CHANNEL,
        "label": LABEL,
        # Amazon's is "seller SKU". Here the identifier is the item code, which is
        # also the Shopify Product Listing's own name.
        "identifier_label": "item code",
        "source_doctype": LISTING_DOCTYPE,
        "enriched_doctype": ENRICHED_DOCTYPE,
        "spec": {
            "fields": json.loads((_DIR / "fields.json").read_text(encoding="utf-8")),
            "rules": (_DIR.parent / "prompts" / "listing.md").read_text(encoding="utf-8"),
        },
        "handlers": {
            "get_product": f"{_SELF}.get_product",
            "get_reference_values": f"{_SELF}.get_reference_values",
            "save_listing": f"{_SELF}.save_listing",
            "validate": f"{_SELF}.validate",
            "register": f"{_SELF}.register",
            "prepare_images": f"{_SELF}.prepare_images",
            # No "health" -- see the module docstring.
        },
    }


# --- handler adapters ---------------------------------------------------------
# Thinner than Amazon's, because there is less to translate: `handlers.py` already
# speaks `item_code`, which is what this channel's identifier actually is. Amazon's
# adapters exist to turn core's `product` into its `sku`; these mostly just rename.


def get_product(product):
    from alaiy_os_connector_shopify.listing import handlers

    return handlers.get_product(item_code=product)


def get_reference_values():
    from alaiy_os_connector_shopify.listing import handlers

    return handlers.get_reference_values()


def save_listing(product, listing):
    """Write the enriched listing.

    Deliberately does NOT call `validate` first. The consumer already does --
    `alaiy_os_agents/agents/listing/tools.py:save_listing` runs the adapter's
    validate, and on defects throws "…and was NOT saved. Fix these and call
    save_listing again" without ever reaching here. Validating again would run
    the same check twice and report the same defects from two places.
    """
    from alaiy_os_connector_shopify.listing import handlers

    return handlers.save_listing(listing=listing, item_code=product)


def validate(listing):
    """Every rule this listing breaks, as sentences a model can act on."""
    from alaiy_os_connector_shopify.listing.validate import validate as _validate

    return _validate(listing)


def prepare_images(product=None, enabled=False, image_urls=None):
    """Retouch the product's own photos and its variants'.

    The keyword names are the contract's, not this app's: the consumer calls
    every handler with keywords fixed by `channels.py`, and this one arrives as
    `fn(product=..., enabled=..., image_urls=...)`. Underneath,
    `generate_product_images` calls the same toggle `generate_images`, and
    translating between the two names is exactly what this wrapper is for.

    Whether anything is produced is the tool's decision, not the caller's -- it
    enhances only when the product already has photos and the toggle is on.
    """
    from alaiy_os_connector_shopify.listing import image_generation

    return image_generation.generate_product_images(
        item_code=product, image_urls=image_urls, generate_images=bool(enabled)
    )


def register(product):
    """Give an Item a Shopify listing row, so there is something to enrich.

    The supplier connectors put products into the catalogue as ERPNext Items;
    everything on this channel is keyed to a `Shopify Product Listing`. Without
    this hop a product sourced from a supplier can never be enriched, because
    there is nothing for the enrichment to be written onto.

    **Local only. Nothing is sent to Shopify.** `ensure_listing` creates the row
    with `is_enabled = 0`, so the connector will not push it: publishing stays a
    separate, deliberate act on an enrichment somebody has reviewed.

    Idempotent: an Item that already has a listing gets that listing back,
    untouched. An existing listing is never edited here -- whatever is already on
    it beats anything the Item can offer.
    """
    from alaiy_os_connector_shopify.shopify.product import listing as listing_resolver

    existing = listing_resolver.get_listing(product)
    if existing:
        return {
            "product": existing.name,
            "created": False,
            "channel": CHANNEL,
            "note": f"'{product}' already had a {LISTING_DOCTYPE}; it was left as it is.",
        }

    created = listing_resolver.ensure_listing(product)
    if not created:
        frappe.throw(f"No Item '{product}', so there is nothing to create a listing for.")

    return {
        "product": created.name,
        "created": True,
        "channel": CHANNEL,
        "note": (
            f"Created a local {LISTING_DOCTYPE} for '{created.name}', disabled so the "
            "connector will not push it. Nothing has been sent to Shopify; it is a "
            "draft record to enrich and review."
        ),
    }
