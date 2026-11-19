"""A fresh install adds the Item columns without building indexes on the big Item table.

Building an index on Item scans the whole catalogue and needs a metadata lock, which is what makes an
install slow and able to block the site. The background build (setup/item_indexes.py) adds them later, and
once a field carries one it keeps it. The deprecated fields are deleted only when their type really
changed, so a fresh install and later migrates touch nothing.

No site: the decisions are plain functions. Stdlib unittest.
"""

import ast
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = (ROOT / "setup" / "install.py").read_text(encoding="utf-8")


def _load():
    """The two pure functions and the two tuples, without importing frappe."""
    tree = ast.parse(SOURCE)
    keep = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in ("item_index_flag", "deprecated_fields_to_replace"):
            keep.append(node)
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") in ("ITEM_INDEXED_FIELDS", "DEPRECATED_ITEM_FIELDS"):
            keep.append(node)
    ns = {}
    exec(compile(ast.Module(body=keep, type_ignores=[]), "install.py", "exec"), ns)
    return ns


NS = _load()


class TestItemIndexFlag(unittest.TestCase):
    def test_a_fresh_install_builds_no_index(self):
        self.assertEqual(NS["item_index_flag"](None), 0)
        self.assertEqual(NS["item_index_flag"](0), 0)

    def test_a_field_whose_index_was_built_keeps_it(self):
        self.assertEqual(NS["item_index_flag"](1), 1)

    def test_the_install_queues_the_background_build_and_never_fails_on_it(self):
        self.assertIn("_start_item_indexes()", SOURCE)
        self.assertIn("enqueue_build(after_commit=True)", SOURCE)
        self.assertIn("could not queue the Item index build", SOURCE)


class TestDeprecatedFields(unittest.TestCase):
    wanted = {"sh_country_of_origin": "Link", "sh_harmonized_system_code": "Data",
              "sh_shopify_tags": "Table MultiSelect", "sh_shopify_category": "Link"}

    def test_nothing_exists_on_a_fresh_install_so_nothing_is_deleted(self):
        self.assertEqual(NS["deprecated_fields_to_replace"]({}, self.wanted), [])
        self.assertEqual(NS["deprecated_fields_to_replace"]({k: None for k in self.wanted}, self.wanted), [])

    def test_fields_already_of_the_wanted_type_are_left_alone(self):
        self.assertEqual(NS["deprecated_fields_to_replace"](dict(self.wanted), self.wanted), [])

    def test_only_a_field_whose_type_changed_is_replaced(self):
        existing = {**self.wanted, "sh_country_of_origin": "Data"}
        self.assertEqual(NS["deprecated_fields_to_replace"](existing, self.wanted), ["sh_country_of_origin"])


if __name__ == "__main__":
    unittest.main()
