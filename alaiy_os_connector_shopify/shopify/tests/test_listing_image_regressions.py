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


class _Listing:
	"""Stands in for a Shopify Product Listing being written to.

	Records whether anything touched its image table. `set` and `append` are the
	only two methods _sync_images uses.
	"""

	def __init__(self, images):
		self.images = list(images)
		self.set_calls = []

	def set(self, field, value):
		self.set_calls.append(field)
		if field == "images":
			self.images = list(value)

	def append(self, field, row):
		self.images.append(row)
		return row


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


class SyncImagesLeavesUntouchedPhotosAlone(unittest.TestCase):
	"""A draft with no image rows must not clear the listing's photos.

	_sync_images REPLACES the listing's image table rather than adding to it. The
	per-row fallback (a row with no url publishes the photo it was made from)
	covers a render that failed, but it is per row — and a text-only enrichment,
	which is what you get with the image toggle off, has no rows at all. Emptying
	the table and refilling it from nothing stripped the product of every photo it
	had, on approval, reporting success.
	"""

	def test_no_image_rows_leaves_the_listing_untouched(self):
		listing = _Listing(["existing-a.jpg", "existing-b.jpg"])

		ShopifyEnrichedListing._sync_images(_Draft([]), listing)

		self.assertEqual(
			listing.images,
			["existing-a.jpg", "existing-b.jpg"],
			"a text-only enrichment must leave the product's photos alone",
		)
		self.assertEqual(
			listing.set_calls, [], "the image table must not even be cleared"
		)

	def test_a_row_that_failed_to_render_still_publishes_its_original(self):
		"""The per-row fallback this sits beside must keep working.

		Guarding the empty case would be worth nothing if it also swallowed the
		case the guard is NOT for: rows exist, but none of them rendered.
		"""
		listing = _Listing(["existing-a.jpg"])
		draft = _Draft([_Row(source_url="original.jpg", url=None, kind="generated")])

		ShopifyEnrichedListing._sync_images(draft, listing)

		self.assertEqual(len(listing.images), 1)
		self.assertEqual(listing.images[0]["image"], "original.jpg")
		self.assertEqual(
			listing.images[0]["source"],
			"Original",
			"a row with no result publishes as the original it actually is",
		)

	def test_a_rendered_row_replaces_the_table(self):
		listing = _Listing(["existing-a.jpg", "existing-b.jpg"])
		draft = _Draft([_Row(source_url="original.jpg", url="enhanced.jpg", kind="generated")])

		ShopifyEnrichedListing._sync_images(draft, listing)

		self.assertEqual(len(listing.images), 1)
		self.assertEqual(listing.images[0]["image"], "enhanced.jpg")
		self.assertEqual(listing.images[0]["source"], "AI Enhanced")


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
