# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""
The `prepare_product_images` tool: supplier photos run through alphashop —
translating their printed Chinese text into English, putting the main image on
a plain white background, or both, on two independent toggles.

One of the two image steps this app ships. It does not retouch photos — that
is `generate_product_images`, a deliberately different capability living in
`image_generation.py`. All three toggles (`translate_images`, `white_bg_images`
and `generate_images`) are always registered; the listing agent's prompt is
what decides which ones a given run turns on, and this module only ever acts
on the first two.

Both operations go through Alaiy OS core's `ai_client` seam
(`llm.translate_image` / `llm.white_background`), the same seam the agent's
text turns use. This app holds no vendor credential: on a managed bench the
call is served by the billing service, which owns the alphashop key and meters
the spend. A BYOK bench has no such provider and the tool reports that rather
than half-working.

Each processed photo is stored as its own public File, so the original
supplier photo is never overwritten and a bad result is always recoverable.

Two halves, split across two stages. `prepare_product_images` runs inside the
agent's run: it decides what needs doing and to which photos, and queues it.
The actual work is `render_prepared`, which runs later on the image queue —
see image_stage.py for why.

## Why white background only ever touches the main image

Amazon's compliance rule (a plain white main tile) is the reason this exists
at all, but nothing stops a seller wanting it on Shopify too — hence it lives
here, not on a per-channel toggle. What IS channel-agnostic is the "main
image" restriction: translating every photo is cheap insurance against
shipping Chinese text on a variant nobody reviewed (see the gate-3 note
below), but putting every gallery photo on a flat white background would
strip the lifestyle/detail shots sellers actually want. So `white_bg_images`
only ever applies to the first of the listing's own photos — the one a
storefront treats as the hero tile.

## Ops, not a single boolean

Each photo target carries an `ops` tuple — `()`, `("translate",)`,
`("white_bg",)` or `("translate", "white_bg")` — computed once in
`prepare_product_images` from the two toggles and whether the target is the
main image. `render_prepared` runs a target's ops IN ORDER: translate first,
then white-background the translated result, so a main image needing both
ends up with English text on a white background rather than either op
clobbering the other's work. The ops tuple round-trips through the queued job
and through the `kind` column on `Shopify Enriched Listing Image`, which is
what lets gate 3 (see below) tell "translated" apart from "translated AND
white-backgrounded" — turning white_bg_images on for a photo already
translated must redo the compositing, not skip it as already-done.
"""

from concurrent.futures import ThreadPoolExecutor

import frappe
from alaiy_os.engine import llm

from alaiy_os_connector_shopify.listing import image_stage
from alaiy_os_connector_shopify.listing import handlers as base
from alaiy_os_connector_shopify.listing import images

# Every photo a product has is translated when the toggle is on — the listing's
# own and each enabled variant's. There is deliberately no per-product cap: a
# variant whose photo was left untranslated is a variant that ships with
# Chinese text on it, which is worse than the cost of translating it. Spend is
# bounded by gate 3 instead (a photo/op pair is never paid for twice) and by
# both toggles being off by default.

# How many photos go through the service at once — see render_prepared. This is
# a paid third-party API, and firing every photo of every product in a batch at
# it simultaneously is a good way to get throttled.
_RENDER_CONCURRENCY = 4

# What stage one puts on an image row that stage two has not produced yet. It is
# read by a human on the Desk form, so it says what is happening, not "queued".
_QUEUED_NOTE = "Being processed in the background; the image will appear here when ready."

# What goes on a photo an earlier run already produced this exact result for.
# Also read by a human, so it explains why this one has a url when its
# siblings do not.
_REUSED_NOTE = "Processed on an earlier run; reused rather than paid for again."

# ops tuple <-> the `kind` column, so gate 3 can tell "translated" apart from
# "translated and put on a white background" and redo only what changed.
_OPS_KIND = {
	("translate",): "translated",
	("white_bg",): "white_bg",
	("translate", "white_bg"): "translated_white_bg",
}
_KIND_OPS = {v: k for k, v in _OPS_KIND.items()}


def prepare_product_images(
	item_code=None, image_urls=None, translate_images=False, white_bg_images=False
):
	"""
	Queue a product's supplier photos for alphashop translation and/or
	white-backgrounding, and return immediately. Returns
	{"images": [{source_url, item_variant, url, note}, ...]} — copy that list
	verbatim into the final `images` array.

	`url` comes back null for anything queued: the photos are processed after
	this run finishes, by image_stage.run_step, and attached to the listing
	then. That is by design — alphashop takes minutes, and holding the run open
	for it would block a worker that could be enriching other products. The
	work itself is render_prepared() below.

	EVERY photo is translated when `translate_images` is on — the listing's
	own PLUS each enabled variant's `variant_image`. `white_bg_images` only
	ever applies to the FIRST of the listing's own photos (the main/hero tile)
	— see the module docstring. The two toggles are independent; a photo that
	is both the main image and gets both toggles ends up translated THEN
	white-backgrounded, in that order.

	Which photo belongs to which variant is settled HERE, in code, and travels
	with the queued job: stage two writes the rows from that plan, not from the
	`images` array the model returns. So a variant's processed photo reaches
	its variant even if the model drops the entry, or drops its
	`item_variant`, on the way out. The entries returned below are the same
	plan, for the model to report — they are its copy of the truth, not the
	truth itself.

	A row's `item_variant` is what routes the result to that variant's
	`variant_image` when an admin approves the listing (see
	ShopifyEnrichedListing._sync_variant_images); nothing is written to the
	Shopify Product Listing before that approval.

	The exception is a URL-only product: it has no listing record for stage
	two to deliver into, so its photos are processed inline and come back with
	real urls.

	Whether anything happens at all is decided HERE, deterministically — not
	left to the model's judgement — by three gates:

	  1. There must be at least one photo. For an item_code run those are the
	     listing's own photos plus each enabled variant's; for a URL-only
	     product they are image_urls. No photos → empty list, nothing done.
	     This gate is airtight: it holds regardless of what the model passes.
	  2. Both toggles are opt-in per request. When photos exist but both
	     `translate_images` and `white_bg_images` are off, we return empty too.
	  3. A photo already processed with the SAME ops on an earlier run is never
	     paid for again — its existing result is returned as-is. This is keyed
	     on (photo, ops), not just the photo, so turning white_bg_images on for
	     a photo already translated redoes the compositing rather than
	     skipping it as done. A photo that FAILED has no url and so is not
	     "already processed": it is retried.

	Per-image failures degrade rather than raise: that entry comes back with
	url=None and a note, and the remaining photos still process. If a needed
	capability isn't configured at all (and gates 1/2 pass), the model is told
	via the thrown message not to retry and to fall back to null placeholders
	instead of stalling the rest of the listing.
	"""
	# ── Gate 1 (airtight): resolve the photos; no photos → nothing to do.
	targets = _resolve_targets(item_code, image_urls)
	if not targets:
		return {
			"images": [],
			"note": "This product has no photos, so nothing was processed.",
		}

	# ── Gate 2: both toggles are opt-in per request.
	if not translate_images and not white_bg_images:
		return {
			"images": [],
			"note": (
				"The product has photos, but translate_images and white_bg_images "
				"are both off, so no images were processed."
			),
		}

	# Checked while the model is still listening, rather than leaving it to
	# discover a misconfigured site minutes later in the background. Only the
	# capability is checked, not a credential — the credential lives off-bench now.
	support = llm.image_client().image_support()
	if translate_images and not support.get("translate"):
		frappe.throw(
			"Image translation is not available on this site (the active AI client "
			"cannot translate images). Do NOT retry; return each image with url=null "
			"so the team can translate it manually."
		)
	if white_bg_images and not support.get("white_bg"):
		frappe.throw(
			"White background is not available on this site (the active AI client "
			"cannot do this). Do NOT retry; return each image with url=null so the "
			"team can process it manually."
		)

	for target in targets:
		target["ops"] = _ops_for(target, translate_images, white_bg_images)

	# A URL-only product has no Shopify Enriched Listing for stage two to patch,
	# so there is nowhere to deliver the results later — process inline, as before.
	if not item_code:
		return {"images": render_prepared(None, {"targets": targets})["images"]}

	# ── Gate 3: never pay for the same (photo, ops) twice.
	done = _already_processed(item_code)
	plan = [dict(target, url=done.get((target["source_url"], target["ops"]))) for target in targets]
	image_stage.queue_step(item_code, image_stage.PREPARE, {"targets": plan})

	# The same plan, for the model to report. Every entry is returned — including
	# the ones reused from an earlier run — because save_listing rebuilds the
	# image table from what this run reports; an entry left out here would
	# disappear from the listing the model returns, even though stage two will
	# still deliver it.
	result = {
		"images": [
			{
				"source_url": entry["source_url"],
				"item_variant": entry["item_variant"],
				"url": entry["url"],
				"note": _note_for(entry),
			}
			for entry in plan
		]
	}

	queued = sum(1 for e in plan if e["ops"] and not e["url"])
	reused = sum(1 for e in plan if e["url"])
	variants = sum(1 for e in plan if e["item_variant"])
	notes = []
	if queued:
		notes.append(
			f"{queued} photo(s) queued for processing. They are being processed in "
			"the background and will be attached to this listing when they are ready "
			"— this is normal and is NOT a failure. Copy these entries verbatim "
			"(including each entry's item_variant), leave url as null, and do NOT "
			"record them in needs_review."
		)
	if reused:
		notes.append(
			f"{reused} entr(ies) were processed on an earlier run and are reused "
			"as-is, with their existing url. Copy them verbatim too."
		)
	if variants:
		notes.append(
			f"{variants} of these entries are variant photos, each carrying the "
			"item_variant it belongs to."
		)
	if notes:
		result["note"] = " ".join(notes)

	return result


def _note_for(entry):
	if entry["url"]:
		return _REUSED_NOTE
	if entry["ops"]:
		return _QUEUED_NOTE
	return "No image operation was requested for this photo."


def _ops_for(target, translate_images, white_bg_images):
	"""Which operations apply to this target, in the order they must run."""
	ops = []
	if translate_images:
		ops.append("translate")
	if white_bg_images and target.get("is_main"):
		ops.append("white_bg")
	return tuple(ops)


def _resolve_targets(item_code, image_urls):
	"""(source_url, item_variant, is_main) for every photo this product has.

	Targets are the listing's own photos first (item_variant None), then each
	enabled variant's photo tagged with its variant. `is_main` marks the one
	`base.primary_listing_image_url` picks -- the same "main photo" notion the
	rest of this app already uses (an Original over an AI Enhanced render,
	falling back to the first row) -- rather than assuming index 0, which is
	what makes white_bg_images apply to exactly the right one. For a
	URL-only product there is no such preference, so the first URL given
	stands in for it.
	"""
	targets = []
	if item_code and frappe.db.exists(base.LISTING_DOCTYPE, item_code):
		listing = frappe.get_doc(base.LISTING_DOCTYPE, item_code)
		main_url = base.primary_listing_image_url(listing)
		targets = [
			{"source_url": url, "item_variant": None, "is_main": url == main_url}
			for url in base.listing_image_urls(listing)
		]
		targets += [
			{"source_url": url, "item_variant": item_variant, "is_main": False}
			for item_variant, url in base.variant_image_map(listing).items()
		]
	if not targets and image_urls:
		urls = [u for u in image_urls if u]
		targets = [
			{"source_url": u, "item_variant": None, "is_main": i == 0}
			for i, u in enumerate(urls)
		]
	return targets


def _already_processed(item_code):
	"""{(source_url, ops): url} for (photo, operation) pairs a previous run
	already produced.

	"Already done" means the listing holds a result for that exact photo AND
	that exact combination of operations — read back off `kind`, which is what
	makes turning white_bg_images on for an already-translated photo redo the
	compositing rather than skip it as done. A photo that FAILED has no url
	and so is absent from this map, which is the retry behaviour we want
	without a flag for it.
	"""
	if not frappe.db.exists(base.ENRICHED_DOCTYPE, item_code):
		return {}

	rows = frappe.get_all(
		"Shopify Enriched Listing Image",
		filters={"parent": item_code, "parenttype": base.ENRICHED_DOCTYPE},
		fields=["source_url", "url", "kind"],
	)
	return {
		(row.source_url, _KIND_OPS[row.kind]): row.url
		for row in rows
		if row.source_url and row.url and row.kind in _KIND_OPS
	}


def render_prepared(item_code, work):
	"""Run the queued ops on each target. Stage two's worker — see image_stage.py.

	`work` holds the plan (`targets`: every use of every photo as
	{source_url, item_variant, ops, url-already-known}).

	Returns {"images": [{source_url, item_variant, url, note, kind}, ...],
	"image_tokens": 0} — ONE ENTRY PER USE, not per (photo, ops) pair. A photo
	the listing and two variants share is processed once per distinct ops
	tuple and comes back as three entries, so image_stage._apply writes it
	onto all three rows and each variant's row carries its own item_variant. A
	photo that failed comes back with url=None and a note, so one bad photo
	costs one photo rather than the whole product.

	The (photo, ops) pairs go through concurrently. Each is an independent
	call to a service that fetches, rewrites and returns an image — slow, and
	slow in parallel just as well.
	"""
	targets = work.get("targets") or []
	todo = [t for t in targets if t.get("ops") and not t.get("url")]

	client = llm.image_client() if todo else None
	if todo:
		# Both resolved on THIS thread, before the pool starts: the client
		# reads site config and the Frappe hook registry, and expanding a
		# local File path needs the site context. Neither works inside a
		# worker thread — the client instance is thread-safe by contract once
		# built.
		support = client.image_support()
		if any("translate" in t["ops"] for t in todo) and not support.get("translate"):
			frappe.throw("Image translation is not available on this site.")
		if any("white_bg" in t["ops"] for t in todo) and not support.get("white_bg"):
			frappe.throw("White background is not available on this site.")

	public_urls = {t["source_url"]: images.public_image_url(t["source_url"]) for t in todo}

	fresh = {}
	if todo:
		with ThreadPoolExecutor(max_workers=min(_RENDER_CONCURRENCY, len(todo))) as pool:
			outcomes = list(
				pool.map(lambda t: _try_prepare(client, public_urls[t["source_url"]], t["ops"]), todo)
			)
		for target, (payload, error) in zip(todo, outcomes, strict=True):
			key = (target["source_url"], target["ops"])
			if error:
				# Logged here rather than in the worker thread: frappe.log_error
				# needs the request context that only this thread has.
				frappe.log_error(
					title="Shopify listing: image preparation failed",
					message=f"{item_code} / {target['source_url']} / {target['ops']}\n{error}",
				)
				fresh[key] = {"url": None, "note": f"Image preparation failed: {error}"[:200]}
				continue

			out_bytes, out_media_type = payload
			# Saving writes a File row, so it stays on this thread too.
			fresh[key] = {
				"url": images.save_public_image(
					"listing-prepared", out_bytes, out_media_type, default_ext=".jpg"
				),
				"note": None,
			}

	out = []
	for target in targets:
		ops = target.get("ops") or ()
		key = (target["source_url"], ops)
		if key in fresh:
			produced = fresh[key]
		else:
			# Nothing was owed for this target: either no op applies to it, or
			# an earlier run already produced this exact result and the url
			# came along in the plan.
			produced = {
				"url": target.get("url"),
				"note": _REUSED_NOTE if target.get("url") else None,
			}
		out.append({
			"source_url": target["source_url"],
			"item_variant": target.get("item_variant"),
			"kind": _OPS_KIND.get(ops),
			**produced,
		})

	return {"images": out, "image_tokens": 0}


def _try_prepare(client, public_url, ops):
	"""One (photo, ops) pair, in a worker thread. Returns (payload, error) —
	never raises.

	Runs `ops` IN ORDER on the same url, chaining each step's output into the
	next: translate first, then white-background the translated result, never
	the reverse — see the module docstring. Both calls and the final fetch are
	pure HTTP, so all of it belongs here; nothing in this function touches
	Frappe, which has no context in a worker thread. The client was built on
	the calling thread and is thread-safe by contract. Re-hosting the bytes is
	the caller's job.
	"""
	try:
		url = public_url
		if "translate" in ops:
			url = client.translate_image(url)["translated_url"]
		if "white_bg" in ops:
			url = client.white_background(url)["white_bg_url"]
		# Re-host the result: the provider's URL is theirs and may expire, and we
		# want the reviewed listing to keep working regardless.
		return images.fetch_image_bytes(url), None
	except Exception as exc:
		return None, str(exc)
