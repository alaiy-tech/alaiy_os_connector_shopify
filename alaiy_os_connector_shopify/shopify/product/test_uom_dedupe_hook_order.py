"""Self-check: the UOM dedupe must run before the doctype's own validate().

Frappe runs a doctype's own validate() BEFORE the `validate` doc_event hooks.
So a heal registered on `validate` cannot repair anything ERPNext's own
validation rejects -- the throw has already happened.

That is what went wrong here. validate_item_uoms was registered on `validate`,
so ERPNext's validate_conversion_factor raised "Unit of Measure ... entered more
than once" and the heal never ran. It only looked like it worked because the
import path calls it explicitly before saving; every other path -- Desk, the
supplier portal, editing a title -- just failed.

Measured live: 1,860 of 3,517 items carry a duplicated UOM row, so over half the
catalogue was unsaveable.

`before_validate` runs ahead of the doctype's validate(), which is the only
place a heal for a doctype-level validation error can work.

    python alaiy_os_connector_shopify/shopify/product/test_uom_dedupe_hook_order.py
"""

import ast
import pathlib

_HOOKS = pathlib.Path(__file__).resolve().parents[2] / "hooks.py"

_DEDUPE = "validate_item_uoms"


def _doc_events(tree):
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "doc_events":
                return ast.literal_eval(node.value)
    raise AssertionError("doc_events not found in hooks.py")


def _flatten(value):
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple)):
        return [v for v in value if isinstance(v, str)]
    return []


def demo():
    tree = ast.parse(_HOOKS.read_text(encoding="utf-8"))
    item_events = _doc_events(tree).get("Item") or {}

    before = _flatten(item_events.get("before_validate"))
    during = _flatten(item_events.get("validate"))

    assert any(_DEDUPE in h for h in before), (
        f"{_DEDUPE} must be registered on Item's before_validate. Frappe runs "
        f"the doctype's own validate() before the `validate` hooks, so a heal "
        f"registered there cannot repair what ERPNext has already thrown on."
    )

    assert not any(_DEDUPE in h for h in during), (
        f"{_DEDUPE} is still on Item's `validate` as well. Running it twice is "
        f"wasted work, and leaving it there invites someone to delete the "
        f"before_validate entry as a duplicate."
    )

    # The other Item validate hooks are unaffected by ordering -- they set
    # fields rather than repair a doctype-level validation error -- so they
    # should stay where they are rather than being swept along with the move.
    assert during, (
        "Item's `validate` hooks vanished. Only the UOM dedupe needed moving; "
        "the category/tag/collection hooks belong on validate."
    )

    print("uom dedupe hook order self-check: OK")


if __name__ == "__main__":
    demo()
