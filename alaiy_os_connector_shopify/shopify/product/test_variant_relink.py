# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""
Self-check for the re-link decisions in _ensure_variant_exists_locally when a
variant's SKU already exists locally.

Runs standalone (no frappe, no site):

    python shopify/product/test_variant_relink.py

The case that motivated it: a merchant deletes a duplicate product and keeps
the other one. The SKU survives, but Shopify's product id, variant id and the
template all change. Matching on "has no id yet" left those items bound to a
deleted product forever, and the surviving template ended up with no children
even though the import reported every variant as handled.
"""


def _decisions(current, v_id, product_id, template_name):
    """Which fields the existing-SKU branch would write, given what's stored."""
    writes = {}
    if v_id and current.get("sh_shopify_variant_id") != v_id:
        writes["sh_shopify_variant_id"] = v_id
    if product_id and current.get("sh_shopify_product_id") != product_id:
        writes["sh_shopify_product_id"] = product_id
    if template_name and current.get("variant_of") and current["variant_of"] != template_name:
        writes["variant_of"] = template_name
    return writes


def demo():
    # The real case: every Shopify id changed, template changed, SKU did not.
    stale = {"sh_shopify_variant_id": "62537106915697",
             "sh_shopify_product_id": "15228207006065",
             "variant_of": "old-template-15228207006065"}
    w = _decisions(stale, "70000000000001", "15468380619121", "new-template-15468380619121")
    assert w == {"sh_shopify_variant_id": "70000000000001",
                 "sh_shopify_product_id": "15468380619121",
                 "variant_of": "new-template-15468380619121"}, w

    # Nothing changed -- must write nothing, or every re-import re-timestamps
    # every item in the catalogue.
    fresh = {"sh_shopify_variant_id": "70000000000001",
             "sh_shopify_product_id": "15468380619121",
             "variant_of": "new-template-15468380619121"}
    assert _decisions(fresh, "70000000000001", "15468380619121",
                      "new-template-15468380619121") == {}

    # The original case this branch was written for: item exists, has no ids.
    blank = {"sh_shopify_variant_id": None, "sh_shopify_product_id": None, "variant_of": None}
    w = _decisions(blank, "70000000000001", "15468380619121", "tpl")
    assert w == {"sh_shopify_variant_id": "70000000000001",
                 "sh_shopify_product_id": "15468380619121"}, w
    assert "variant_of" not in w, "a standalone item must not be forced under a template"

    # Missing incoming ids must never blank out good stored values.
    assert _decisions(fresh, "", "", "new-template-15468380619121") == {}

    # Only the variant id moved (Shopify can reissue one within a product).
    w = _decisions(fresh, "70000000000009", "15468380619121", "new-template-15468380619121")
    assert w == {"sh_shopify_variant_id": "70000000000009"}, w

    print("OK: repoint on change, no-op when identical, no blanking, "
          "no template forced onto a standalone item")


if __name__ == "__main__":
    demo()
