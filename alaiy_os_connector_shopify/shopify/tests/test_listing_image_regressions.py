"""Two regressions in the listing image path, pinned so they cannot come back.

Both were found by reading the code during the migration from
`alaiy_os_agent_shopify_listing`, not by a failing test — which is exactly why
they are worth a test now. Each one is silent in production: the first destroys
data and reports success, the second hangs a batch forever without an error
anywhere.

Run via `bench run-tests`, but neither test needs a site: they call the methods
directly with stand-in objects, because what is being pinned is a decision, not
a database write.
"""

import ast
import inspect
import os
import unittest

from alaiy_os_connector_shopify.alaiy_os_connector_shopify.doctype.shopify_enriched_listing.shopify_enriched_listing import (
	ShopifyEnrichedListing,
)
from alaiy_os_connector_shopify.listing import image_stage


class _ListingImage:
	def __init__(self, image, source="Original", generated_by_agent=None):
		self.image = image
		self.source = source
		self.generated_by_agent = generated_by_agent


class _Listing:
	"""Stands in for a Shopify Product Listing being written to.

	Records whether anything touched its image table. `set` and `append` are the
	only two methods _sync_images uses. Photos it starts with are rows (read by
	attribute, as a child row is); photos written to it are the dicts
	_sync_images appends.
	"""

	def __init__(self, images):
		self.images = [_ListingImage(url) for url in images]
		self.set_calls = []

	def set(self, field, value):
		self.set_calls.append(field)
		if field == "images":
			self.images = list(value)

	def append(self, field, row):
		self.images.append(row)
		return row

	def urls(self):
		return [row["image"] if isinstance(row, dict) else row.image for row in self.images]


class _Row:
	def __init__(self, **kw):
		self.item_variant = kw.get("item_variant")
		self.url = kw.get("url")
		self.source_url = kw.get("source_url")
		self.kind = kw.get("kind")


class _Draft:
	"""Stands in for the enriched listing doing the pushing."""

	def __init__(self, images):
		self.images = images
		self.name = "SH-123"


def _sync(draft_rows, listing):
	ShopifyEnrichedListing._sync_images(_Draft(draft_rows), listing)


class SyncImagesLeavesUntouchedPhotosAlone(unittest.TestCase):
	"""A draft with no image rows must not clear the listing's photos.

	The per-row fallback (a row with no url publishes the photo it was made from)
	covers a render that failed, but it is per row — and a text-only enrichment,
	which is what you get with the image toggle off, has no rows at all. Emptying
	the table and refilling it from nothing stripped the product of every photo it
	had, on approval, reporting success.
	"""

	def test_no_image_rows_leaves_the_listing_untouched(self):
		listing = _Listing(["existing-a.jpg", "existing-b.jpg"])

		_sync([], listing)

		self.assertEqual(
			listing.urls(),
			["existing-a.jpg", "existing-b.jpg"],
			"a text-only enrichment must leave the product's photos alone",
		)
		self.assertEqual(
			listing.set_calls, [], "the image table must not even be cleared"
		)

	def test_variant_rows_alone_leave_the_gallery_untouched(self):
		"""Variant photos are delivered to variant rows, never to the gallery."""
		listing = _Listing(["a.jpg"])

		_sync([_Row(item_variant="V1", source_url="v.jpg", url="v-enhanced.jpg")], listing)

		self.assertEqual(listing.set_calls, [])

	def test_a_row_that_failed_to_render_still_publishes_its_original(self):
		"""The per-row fallback this sits beside must keep working.

		Guarding the empty case would be worth nothing if it also swallowed the
		case the guard is NOT for: rows exist, but none of them rendered.
		"""
		listing = _Listing(["original.jpg"])

		_sync([_Row(source_url="original.jpg", url=None, kind="generated")], listing)

		self.assertEqual(listing.urls(), ["original.jpg"])
		self.assertEqual(
			listing.images[0]["source"],
			"Original",
			"a row with no result publishes as the original it actually is",
		)

	def test_a_rendered_row_replaces_the_photo_it_was_made_from(self):
		listing = _Listing(["a.jpg", "b.jpg"])

		_sync([
			_Row(source_url="a.jpg", url="a-enhanced.jpg", kind="generated"),
			_Row(source_url="b.jpg", url="b.jpg", kind="hero"),
		], listing)

		self.assertEqual(listing.urls(), ["a-enhanced.jpg", "b.jpg"])
		self.assertEqual(listing.images[0]["source"], "AI Enhanced")
		self.assertEqual(listing.images[1]["source"], "Original")

	def test_a_draft_speaking_for_every_photo_sets_the_order(self):
		"""The full-draft case keeps its draft order - a dragged worn photo stays put."""
		listing = _Listing(["a.jpg", "b.jpg"])

		_sync([
			_Row(source_url="a.jpg", url="/files/worn-1.jpeg", kind="worn"),
			_Row(source_url="b.jpg", url="b.jpg", kind="hero"),
			_Row(source_url="a.jpg", url="a.jpg", kind="hero"),
		], listing)

		self.assertEqual(listing.urls(), ["/files/worn-1.jpeg", "b.jpg", "a.jpg"])


class SyncImagesNeverDropsAPhotoTheDraftDoesNotKnow(unittest.TestCase):
	"""A draft holding fewer photos than the listing must not shrink the gallery.

	Found in production (Z058-03285, 2026-09-29): a text-only re-run rebuilt the
	draft's image table to nothing, an admin then kept a worn photo, and approving
	published that one row as the product's entire gallery. Retouching a single
	photo after such a run, or uploading one after the draft was seeded, left the
	draft just as short of the real gallery.
	"""

	def test_worn_only_draft_adds_to_the_end_of_the_gallery(self):
		listing = _Listing(["a.png", "b.png", "c.png"])

		_sync([_Row(source_url="a.png", url="/files/listing-worn-1.jpeg", kind="worn")], listing)

		self.assertEqual(listing.urls(), ["a.png", "b.png", "c.png", "/files/listing-worn-1.jpeg"])
		self.assertEqual(listing.images[-1]["source"], "AI Enhanced")
		self.assertEqual(listing.images[0]["source"], "Original", "kept photos keep their own source")

	def test_one_retouched_photo_is_replaced_in_place(self):
		listing = _Listing(["a.png", "b.png", "c.png"])

		_sync([_Row(source_url="b.png", url="b-enhanced.png", kind="generated")], listing)

		self.assertEqual(listing.urls(), ["a.png", "b-enhanced.png", "c.png"])

	def test_a_photo_uploaded_after_the_draft_was_seeded_is_kept(self):
		listing = _Listing(["a.png", "b.png", "/files/upload.jpg"])

		_sync([
			_Row(source_url="a.png", url="a-enhanced.png", kind="generated"),
			_Row(source_url="b.png", url="b.png", kind="hero"),
		], listing)

		self.assertEqual(listing.urls(), ["a-enhanced.png", "b.png", "/files/upload.jpg"])

	def test_a_worn_photo_already_on_the_listing_is_not_added_twice(self):
		"""Publishing the same worn-only draft again - after a Shopify push swapped
		the local file for its CDN copy - must not duplicate it."""
		listing = _Listing([
			"a.png",
			"https://cdn.shopify.com/s/files/1/0/files/listing-worn-1.jpg?v=179",
		])

		_sync([_Row(source_url="a.png", url="/files/listing-worn-1.jpeg", kind="worn")], listing)

		self.assertEqual(len(listing.images), 2)

	def test_a_draft_seeded_before_a_shopify_push_still_matches_its_photos(self):
		listing = _Listing([
			"https://cdn.shopify.com/s/files/1/0/files/a.jpg?v=1",
			"https://cdn.shopify.com/s/files/1/0/files/b.jpg?v=1",
		])

		_sync([
			_Row(source_url="/files/a.jpg", url="/files/a-enhanced.png", kind="generated"),
			_Row(source_url="/files/b.jpg", url="/files/b.jpg", kind="hero"),
		], listing)

		self.assertEqual(listing.urls(), ["/files/a-enhanced.png", "/files/b.jpg"])


class RunStepAlwaysNotifiesBatching(unittest.TestCase):
	"""Every exit from run_step must tell bulk enrichment the imagery settled.

	Stage two renders photos after a batch's runs have already finished, so a
	batch parks in "Generating Images" and waits to be told each product is done
	(alaiy_os_agents' bulk._images_pending / finalize_images). Stage two is the
	only thing that knows, so if run_step returns without calling _nudge_batches
	the batch never closes — no error, no log line, just a progress bar that
	never completes.

	Checked as a property of the source rather than by running the job, because
	what broke was a call being *deleted*: three call sites existed, one was
	removed with the rest, and nothing failed. An assertion about the shape of
	the function is what would have caught that; a test that exercises the happy
	path would not.
	"""

	def test_every_return_in_run_step_is_preceded_by_a_nudge(self):
		source = inspect.getsource(image_stage.run_step)
		tree = ast.parse(source.lstrip())
		func = tree.body[0]

		# Every statement in the body, paired with the block it sits in, so a
		# `return` can be checked against what runs immediately before it.
		def check(block):
			for i, node in enumerate(block):
				if isinstance(node, ast.Return):
					before = block[:i]
					self.assertTrue(
						any(_is_nudge(stmt) for stmt in before),
						f"the return at line {node.lineno} of run_step leaves without "
						"calling _nudge_batches, so a bulk batch waiting on this "
						"product's imagery would never close",
					)
				for attr in ("body", "orelse", "finalbody"):
					inner = getattr(node, attr, None)
					if inner:
						check(inner)
				for handler in getattr(node, "handlers", []):
					check(handler.body)

		check(func.body)

	def test_the_function_ends_by_nudging(self):
		"""The success path falls off the end rather than returning."""
		source = inspect.getsource(image_stage.run_step)
		func = ast.parse(source.lstrip()).body[0]
		self.assertTrue(
			_is_nudge(func.body[-1]),
			"run_step must finish by calling _nudge_batches on the success path",
		)

	def test_the_nudge_target_still_exists_upstream(self):
		"""_nudge_batches imports finalize_images by dotted path.

		The call it was restored for lives in another app, so a rename there would
		break this silently — the import is deliberately guarded, and a guarded
		import of a function that no longer exists looks exactly like the app not
		being installed.
		"""
		try:
			from alaiy_os_agents.agents.listing import bulk
		except ImportError:
			self.skipTest("alaiy_os_agents is not installed on this bench")

		self.assertTrue(
			callable(getattr(bulk, "finalize_images", None)),
			"alaiy_os_agents.agents.listing.bulk.finalize_images has moved or gone; "
			"_nudge_batches is now a silent no-op and batches will hang",
		)


class ApiMatchesTheControllerItCalls(unittest.TestCase):
	"""Every method listing/api.py calls on an enriched listing must exist.

	publish_listing_images shipped calling `enriched.apply_images(listing)` on a
	controller that had no such method, and every check in this repo passed: the
	module imported, test_no_undefined_names walks NAMES and an attribute on an
	instance is not one, and no test exercised that endpoint. It surfaced as a 500
	the first time someone pressed Save on the Media card.

	The api module and the doctype controller are two halves of one contract that
	nothing else pins, so it is pinned here — by reading the calls out of the
	source rather than by listing them, so a method added to api.py tomorrow is
	covered without anyone remembering to add it.
	"""

	#: Inherited from frappe's Document, so absent from the controller's own
	#: class body and not a defect.
	_DOCUMENT_METHODS = {
		"save", "insert", "set", "get", "append", "db_set", "reload", "delete",
		"check_permission", "run_method", "get_doc_before_save", "set_onload",
	}

	def test_every_enriched_listing_method_api_calls_exists(self):
		api_src = _read("alaiy_os_connector_shopify/listing/api.py")
		ctrl_src = _read(
			"alaiy_os_connector_shopify/alaiy_os_connector_shopify/doctype/"
			"shopify_enriched_listing/shopify_enriched_listing.py"
		)

		defined = {
			node.name
			for node in ast.walk(ast.parse(ctrl_src))
			if isinstance(node, ast.FunctionDef)
		}

		# `enriched` is the name api.py binds an enriched listing document to.
		called = {
			node.func.attr
			for node in ast.walk(ast.parse(api_src))
			if isinstance(node, ast.Call)
			and isinstance(node.func, ast.Attribute)
			and isinstance(node.func.value, ast.Name)
			and node.func.value.id == "enriched"
		}

		missing = sorted(called - defined - self._DOCUMENT_METHODS)
		self.assertEqual(
			missing,
			[],
			f"listing/api.py calls {missing} on a Shopify Enriched Listing, and the "
			"controller defines no such method — every call site is a 500 waiting "
			"for someone to press the button",
		)

	def test_both_publish_routes_share_apply_images(self):
		"""Approval and a photo-only publish must apply imagery the same way.

		apply_images exists precisely so the two cannot drift; an approval that
		inlined the two syncs again would start the drift silently.
		"""
		ctrl_src = _read(
			"alaiy_os_connector_shopify/alaiy_os_connector_shopify/doctype/"
			"shopify_enriched_listing/shopify_enriched_listing.py"
		)
		tree = ast.parse(ctrl_src)
		push = next(
			n for n in ast.walk(tree)
			if isinstance(n, ast.FunctionDef) and n.name == "_push_to_listing"
		)
		calls = {
			n.func.attr
			for n in ast.walk(push)
			if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
		}
		self.assertIn("apply_images", calls)
		self.assertNotIn(
			"_sync_images",
			calls,
			"_push_to_listing should reach the image syncs through apply_images, "
			"not call them itself",
		)


class FirstImportSeedsListingImagesDirectly(unittest.TestCase):
	"""A brand-new import must seed the Listing's own images, not rely on the
	Item/slideshow download path.

	_import_product_inner writes a first-time import's images to Item.image
	and a Website Slideshow, because no Listing exists yet at that point
	(has_listing=False). ensure_listing then creates an empty Listing right
	after -- with no image rows -- and both the admin product page
	(_listing_images_for) and push_item's own effective_images() read ONLY
	the Listing's image rows once a Listing exists; neither falls back to
	Item.image/slideshow past that point. Confirmed live: a first-time
	import showed zero photos in the admin UI, and a later Enable Sync push
	replaced Shopify's own real photos with whatever the fallback DID
	resolve (often just one), since productSet has no partial-update mode
	-- _set_item_slideshow's silent multi-image failure modes (no
	`slideshow` field on this site, every image download failing) made
	things worse but weren't the root cause: even a fully successful
	slideshow write is still invisible to a Listing that already exists.

	Fixed by having _import_product call apply_inbound_from_shopify on the
	freshly-created Listing, seeding it with Shopify's own real URLs
	directly (no download/re-upload) -- pinned here so a future refactor
	can't drop that call silently.
	"""

	def test_new_listing_branch_calls_apply_inbound_from_shopify(self):
		src = _read("alaiy_os_connector_shopify/shopify/product/importer.py")
		tree = ast.parse(src)
		func = next(
			n for n in ast.walk(tree)
			if isinstance(n, ast.FunctionDef) and n.name == "_import_product"
		)

		# The call must sit inside an `if is_new_listing:` block, not
		# unconditionally -- an existing Listing's images are handled by the
		# update path (_update_existing_product) and must not be
		# reset/overwritten here.
		if_new_listing = next(
			(n for n in ast.walk(func)
			 if isinstance(n, ast.If)
			 and isinstance(n.test, ast.Name)
			 and n.test.id == "is_new_listing"),
			None,
		)
		self.assertIsNotNone(
			if_new_listing,
			"_import_product must branch on is_new_listing before seeding "
			"Listing images -- an existing Listing's images belong to the "
			"update path, not here",
		)

		calls = {
			n.func.attr
			for n in ast.walk(if_new_listing)
			if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
		}
		self.assertIn(
			"apply_inbound_from_shopify",
			calls,
			"_import_product's new-listing branch no longer seeds the "
			"Listing's images from Shopify's own URLs -- a first-time "
			"import will again show zero photos in the admin UI and risk "
			"a later Enable Sync push wiping Shopify's real photos",
		)


def _read(relpath):
	root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
	with open(os.path.join(root, relpath), encoding="utf-8") as fh:
		return fh.read()


def _is_nudge(stmt):
	return (
		isinstance(stmt, ast.Expr)
		and isinstance(stmt.value, ast.Call)
		and isinstance(stmt.value.func, ast.Name)
		and stmt.value.func.id == "_nudge_batches"
	)


if __name__ == "__main__":
	unittest.main()


class _EnrichedRow:
	def __init__(self, **kw):
		for key in ("kind", "item_variant", "source_url", "url", "brief", "note"):
			setattr(self, key, kw.get(key))


class _Enriched:
	"""Stands in for the Shopify Enriched Listing save_listing is writing."""

	def __init__(self, images, image_status=None):
		self.images = list(images)
		self.image_status = image_status
		self.image_error = "earlier error"

	def set(self, field, value):
		setattr(self, field, list(value))

	def append(self, field, row):
		row = _EnrichedRow(**row)
		getattr(self, field).append(row)
		return row


class TextOnlyRunLeavesTheDraftsPhotosAlone(unittest.TestCase):
	"""A run that produced no imagery must not rebuild the draft's photos.

	Found in production (Z058-03285, 2026-09-29): "Enrich" and "Enrich + images"
	ran over the same product; the text-only run saved last and emptied the
	draft's image table, taking four retouches with it.
	"""

	def test_no_imagery_keeps_every_row_and_the_status(self):
		from alaiy_os_connector_shopify.listing import handlers

		retouched = _EnrichedRow(source_url="a.png", url="a-enhanced.png")
		worn = _EnrichedRow(source_url="a.png", url="worn.jpeg", kind="worn")
		doc = _Enriched([retouched, worn], image_status="Ready")

		handlers._rebuild_images(doc, [])

		self.assertEqual(doc.images, [retouched, worn])
		self.assertEqual(doc.image_status, "Ready")

	def test_no_imagery_on_a_fresh_record_is_not_required(self):
		from alaiy_os_connector_shopify.listing import handlers

		doc = _Enriched([])

		handlers._rebuild_images(doc, [])

		self.assertEqual(doc.image_status, "Not Required")

	def test_imagery_rebuilds_and_keeps_additional_photos(self):
		from alaiy_os_connector_shopify.listing import handlers

		doc = _Enriched([
			_EnrichedRow(source_url="a.png", url="old.png"),
			_EnrichedRow(source_url="a.png", url="worn.jpeg", kind="worn"),
		])

		handlers._rebuild_images(doc, [{"kind": None, "source_url": "a.png", "url": None}])

		self.assertEqual([(r.kind, r.url) for r in doc.images], [(None, None), ("worn", "worn.jpeg")])
		self.assertEqual(doc.image_status, "Queued")
		self.assertIsNone(doc.image_error)
