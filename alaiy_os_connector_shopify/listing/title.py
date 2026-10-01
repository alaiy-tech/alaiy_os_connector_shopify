# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""
The client's last word on an enriched title, applied in code after the model.

Some of what a store wants in a title is not the model's to decide, because the
answer is already a value on the product: a store that ends every title with
the product's own barcode wants exactly that value, not whatever code the model
read off a description or a photo of a hallmark. So the model writes the
title without it, and the store's rule is applied here, at the one place the
agent's listing is written (`handlers.save_listing`).

    # in the client app's hooks.py
    listing_title = ["<client_app>.agents.title.title"]

Each provider is called as `fn(item_code=..., title=...)` and returns the title
to save. Providers run in hook order, each receiving the previous one's result.

Only the agent's save runs this. A title a person edits during review is theirs
and is saved as typed.

No provider is the normal case and changes nothing. A provider that raises is
logged and skipped rather than allowed to fail the save -- the same rule as the
rest of `save_listing`: a refused save makes the model rebuild the payload, and
a rebuilt payload silently drops work it had already got right.
"""

import frappe

HOOK = "listing_title"


def apply(item_code, title):
    """`title`, after every installed provider has had its say."""
    for provider in frappe.get_hooks(HOOK) or []:
        try:
            result = frappe.get_attr(provider)(item_code=item_code, title=title)
        except Exception:
            frappe.log_error(title=f"{HOOK}: {provider} failed for {item_code}")
            continue
        if isinstance(result, str) and result.strip():
            title = result
    return title
