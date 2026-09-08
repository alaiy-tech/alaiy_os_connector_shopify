"""
fill_children_from_item merges rather than rebuilds.

It used to run on before_insert only and skip any table that already had
rows, so a Listing created before its Item gained a variant never picked
that variant up -- the "Populate from Item" button was the only way to fix
it. Now it runs on every save, which makes the merge semantics the thing
holding the whole change up: it has to ADD what is missing without
disturbing anything a merchant set by hand.

These pin both halves. A frappe stub stands in for the DB so the merge
logic can be exercised on its own.
"""

import sys
import types
import unittest


def _install_frappe_stub(template, variant_items, price=None):
    """Minimal frappe whose reads answer for one template Item."""
    frappe = types.ModuleType("frappe")

    def get_value(doctype, name=None, fieldname=None, **kwargs):
        if doctype == "Item":
            return template
        return None

    def get_all(doctype, filters=None, fields=None, **kwargs):
        return list(variant_items)

    frappe.db = types.SimpleNamespace(
        get_value=get_value, get_all=get_all, exists=lambda *a, **k: None)
    frappe.get_all = get_all
    frappe.get_single = lambda *a, **k: types.SimpleNamespace(
        sh_selling_price_list="Standard Selling")
    frappe.get_meta = lambda *a, **k: types.SimpleNamespace(
        has_field=lambda f: False)
    frappe.get_doc = lambda *a, **k: None
    frappe.whitelist = lambda *a, **k: (lambda fn: fn)
    frappe.validate_and_sanitize_search_inputs = lambda fn: fn
    sys.modules["frappe"] = frappe

    utils = types.ModuleType("frappe.utils")
    utils.flt = lambda v, *a, **k: float(v or 0)
    sys.modules["frappe.utils"] = utils
    frappe.utils = utils
    return frappe


class _Row(dict):
    """A child row that behaves like a Frappe child doc for attribute access."""

    def __init__(self, **kw):
        super().__init__(**kw)
        self.__dict__.update(kw)

    def __getattr__(self, name):
        return None


class _Listing:
    def __init__(self, item="TSHIRT", images=None, variants=None, **fields):
        self.item = item
        self.images = images or []
        self.variants = variants or []
        self.listing_category = fields.get("listing_category")
        self.listing_product_type = fields.get("listing_product_type")
        self.sh_shopify_product_id = fields.get("sh_shopify_product_id")

    def append(self, table, row):
        getattr(self, table).append(_Row(**row))
        return row


def _fill(listing, template=None, variants=None, monkey_price=None):
    template = template or types.SimpleNamespace(
        name="TSHIRT", image=None, has_variants=1,
        sh_shopify_product_id=None, sh_shopify_category=None,
        sh_shopify_product_type=None)
    # get_value(as_dict=True) is read with attribute access in the function.
    tmpl_dict = types.SimpleNamespace(**vars(template)) if not isinstance(
        template, types.SimpleNamespace) else template
    _install_frappe_stub(tmpl_dict, variants or [])
    for mod in list(sys.modules):
        if mod.startswith("alaiy_os_connector_shopify"):
            del sys.modules[mod]
    from alaiy_os_connector_shopify.shopify.product import listing as mod
    mod._variant_price = lambda *a, **k: monkey_price
    mod._template_image_urls = lambda t: getattr(t, "_urls", [])
    mod.fill_children_from_item(listing)
    return listing


class TestVariantMerge(unittest.TestCase):
    def test_empty_listing_gets_every_variant(self):
        listing = _Listing()
        _fill(listing, variants=[
            types.SimpleNamespace(name="TSHIRT-S", sh_shopify_variant_id=None, image=None),
            types.SimpleNamespace(name="TSHIRT-M", sh_shopify_variant_id=None, image=None),
        ])
        self.assertEqual([r.item_variant for r in listing.variants],
                         ["TSHIRT-S", "TSHIRT-M"])

    def test_a_new_variant_is_added_to_a_listing_that_already_has_rows(self):
        # The whole point of the change. The old code skipped the table
        # entirely once it held anything, so TSHIRT-L never arrived and
        # never reached Shopify.
        listing = _Listing(variants=[_Row(item_variant="TSHIRT-S", is_enabled=1)])
        _fill(listing, variants=[
            types.SimpleNamespace(name="TSHIRT-S", sh_shopify_variant_id=None, image=None),
            types.SimpleNamespace(name="TSHIRT-L", sh_shopify_variant_id=None, image=None),
        ])
        self.assertEqual([r.item_variant for r in listing.variants],
                         ["TSHIRT-S", "TSHIRT-L"])

    def test_an_existing_row_is_not_duplicated(self):
        listing = _Listing(variants=[_Row(item_variant="TSHIRT-S", is_enabled=1)])
        _fill(listing, variants=[
            types.SimpleNamespace(name="TSHIRT-S", sh_shopify_variant_id=None, image=None),
        ])
        self.assertEqual(len(listing.variants), 1)

    def test_a_variant_switched_off_stays_off(self):
        # Re-enabling on the next save would silently undo a merchant's
        # deliberate decision to stop selling that size.
        listing = _Listing(variants=[_Row(item_variant="TSHIRT-S", is_enabled=0)])
        _fill(listing, variants=[
            types.SimpleNamespace(name="TSHIRT-S", sh_shopify_variant_id=None, image=None),
        ])
        self.assertEqual(listing.variants[0].is_enabled, 0)

    def test_a_price_override_is_never_overwritten(self):
        listing = _Listing(variants=[
            _Row(item_variant="TSHIRT-S", is_enabled=1, variant_price=99.0)])
        _fill(listing, variants=[
            types.SimpleNamespace(name="TSHIRT-S", sh_shopify_variant_id=None, image=None),
        ], monkey_price=10.0)
        self.assertEqual(listing.variants[0].variant_price, 99.0)

    def test_a_blank_field_on_an_existing_row_is_backfilled(self):
        listing = _Listing(variants=[
            _Row(item_variant="TSHIRT-S", is_enabled=1, sh_shopify_variant_id=None)])
        _fill(listing, variants=[
            types.SimpleNamespace(name="TSHIRT-S", sh_shopify_variant_id="777", image=None),
        ])
        self.assertEqual(listing.variants[0].sh_shopify_variant_id, "777")

    def test_no_row_is_ever_removed(self):
        # A variant the Item no longer reports must not vanish from the
        # Listing -- removing it would silently delist it on Shopify.
        listing = _Listing(variants=[_Row(item_variant="TSHIRT-OLD", is_enabled=1)])
        _fill(listing, variants=[
            types.SimpleNamespace(name="TSHIRT-S", sh_shopify_variant_id=None, image=None),
        ])
        self.assertIn("TSHIRT-OLD", [r.item_variant for r in listing.variants])


class TestNoItemIsANoOp(unittest.TestCase):
    def test_listing_without_an_item_does_nothing(self):
        listing = _Listing(item=None)
        _fill(listing)
        self.assertEqual(listing.variants, [])
        self.assertEqual(listing.images, [])


if __name__ == "__main__":
    unittest.main()
