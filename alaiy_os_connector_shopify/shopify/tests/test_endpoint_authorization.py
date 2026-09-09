"""
Every whitelisted endpoint checks who is asking.

`@frappe.whitelist()` only requires a session -- any logged-in user on the
site can call any of these, whatever their role. The doctypes behind them
grant access to System Manager alone, but the calls they make (frappe.get_all,
frappe.db.*, get_cached_doc) all bypass doctype permissions. The check has to
be in the endpoint or it is not made at all.

On a self-serve bench that is not a role question but a tenancy one: the
endpoints take a store, or a record belonging to one, and act on it with that
store's own credentials. An unauthorised call does not fail at Shopify -- it
succeeds, against the wrong merchant's shop.

This walks the source rather than calling anything, because what has to hold
is a property of every endpoint, including ones added later.
"""

import ast
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]

# Checked for in an endpoint's body. _enqueue_sync resolves and authorises the
# connection itself before queueing.
GUARDS = ("require_access", "require_access_to_record", "_enqueue_sync",
          "get_roles", "PermissionError")

# The ones that legitimately carry no caller check, and why.
EXEMPT = {
    # Authenticated by HMAC against the named store's own secret, and refuses
    # any delivery it cannot attribute. Shopify has no session, so a
    # permission check here would reject every real webhook.
    "handle_webhook",
    # A link picker. Refusing is the wrong shape -- it filters to the caller's
    # store instead, which test_item_picker_is_store_scoped pins.
    "item_without_listing_query",
    # Same shape as handle_webhook: Shopify's browser redirect carries no
    # Alaiy OS session, so every guarantee here comes from
    # oauth.verify_callback_hmac (against the app's own secret) and the
    # single-use state token, not from require_access. The scanner cannot
    # see through the oauth module boundary, so this is named rather than
    # silently passing.
    "callback",
    # Returns one boolean -- whether the OAuth app is configured on this
    # site -- with no store name, no secret, no write. Nothing to authorise.
    "is_configured",
}


def _endpoints():
    for f in sorted(ROOT.rglob("*.py")):
        rel = str(f.relative_to(ROOT)).replace("\\", "/")
        if "__pycache__" in rel or "/tests/" in rel:
            continue
        for n in ast.walk(ast.parse(f.read_text(encoding="utf-8", errors="replace"))):
            if isinstance(n, ast.FunctionDef) and any(
                    "whitelist" in ast.unparse(d) for d in n.decorator_list):
                yield rel, n


class TestEveryEndpointIsGuarded(unittest.TestCase):
    def test_no_endpoint_is_reachable_without_a_check(self):
        unguarded = [
            f"{rel}:{fn.lineno} {fn.name}"
            for rel, fn in _endpoints()
            if fn.name not in EXEMPT
            and not any(g in ast.unparse(fn) for g in GUARDS)
        ]
        self.assertEqual(
            unguarded, [],
            "whitelisted and reachable by any logged-in user:\n  "
            + "\n  ".join(unguarded))

    def test_the_exemptions_still_exist(self):
        # If one is renamed or deleted, the exemption silently starts
        # excusing nothing -- or worse, a future endpoint with the same name.
        names = {fn.name for _, fn in _endpoints()}
        for name in EXEMPT:
            self.assertIn(name, names, f"{name} is exempt but no longer exists")


class TestWritePathsRequireWriteAccess(unittest.TestCase):
    """The endpoints that push to somebody's real shop."""

    WRITES = {
        "toggle_collection_channel": "shopify/product/collections.py",
        "push_fulfillment_for_delivery_note": "shopify/order/fulfillment_push.py",
        "trigger_update_listings": "api/update_listings.py",
        "backfill_all_product_metafields": "shopify/product/metafields.py",
        "sync_shopify_tags": "shopify/product/tags.py",
        "sync_shopify_locations": "shopify/inventory_sync.py",
        "sync_shopify_collections": "shopify/product/collections.py",
        # Mints and stores a fresh access token -- split out of
        # test_connection, which is read-only and correctly asks for "read".
        "authenticate": "api/test_connection.py",
    }

    def test_each_asks_for_write_not_read(self):
        for name, relative in self.WRITES.items():
            tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
            fn = next((n for n in ast.walk(tree)
                       if isinstance(n, ast.FunctionDef) and n.name == name), None)
            self.assertIsNotNone(fn, f"{name} missing from {relative}")
            # ast.unparse normalises string quotes, so match either form.
            code = ast.unparse(fn)
            self.assertTrue(
                '"write"' in code or "'write'" in code,
                f"{name} pushes to a real shop but only asks for read access")


class TestRecordAddressedEndpointsAuthoriseTheOwner(unittest.TestCase):
    """
    Endpoints named by a record, not a store.

    The store is not in the request -- it is on the row -- so the check has to
    load it first. Without that, naming somebody else's record is enough.
    """

    BY_RECORD = {
        "toggle_collection_channel": "shopify/product/collections.py",
        "get_collection_products": "shopify/product/collections.py",
        "get_collection_channels": "shopify/product/collections.py",
        "push_fulfillment_for_delivery_note": "shopify/order/fulfillment_push.py",
        "effective_values": "shopify/product/listing.py",
    }

    def test_each_authorises_against_the_record_owner(self):
        for name, relative in self.BY_RECORD.items():
            tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
            fn = next((n for n in ast.walk(tree)
                       if isinstance(n, ast.FunctionDef) and n.name == name), None)
            self.assertIsNotNone(fn, f"{name} missing from {relative}")
            self.assertIn("require_access_to_record", ast.unparse(fn),
                          f"{name} is addressed by record but never checks its owner")


class TestItemPickerIsStoreScoped(unittest.TestCase):
    def test_the_picker_filters_on_the_connection(self):
        # Typing one letter into the Listing's item field must not list every
        # other seller's product names back to the caller.
        tree = ast.parse((ROOT / "shopify/product/listing.py").read_text(encoding="utf-8"))
        fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                  and n.name == "item_without_listing_query")
        code = ast.unparse(fn)
        self.assertIn("sh_shopify_connection", code)
        self.assertIn("resolve_optional_name", code)


if __name__ == "__main__":
    unittest.main()
