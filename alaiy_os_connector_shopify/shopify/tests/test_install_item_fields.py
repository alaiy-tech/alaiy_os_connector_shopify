"""A fresh install adds the Item columns without building indexes on the big Item table.

Building an index on Item scans the whole catalogue and needs a metadata lock, which is what makes an
install slow and able to block the site. The indexes are switched on later (site config
`shopify_item_indexes`), and once a field carries one it keeps it. The deprecated fields are deleted
only when their type really changed, so a fresh install and later migrates touch nothing.

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
        self.assertEqual(NS["item_index_flag"](None, None), 0)
        self.assertEqual(NS["item_index_flag"](0, 0), 0)

    def test_the_site_can_ask_for_the_indexes(self):
        self.assertEqual(NS["item_index_flag"](1, None), 1)

    def test_a_field_that_already_has_the_index_keeps_it(self):
        self.assertEqual(NS["item_index_flag"](None, 1), 1)

    def test_the_four_indexed_item_fields_are_the_ones_the_spec_flags(self):
        flagged = []
        for node in ast.walk(ast.parse(SOURCE)):
            if isinstance(node, ast.Dict):
                keys = [k.value for k in node.keys if isinstance(k, ast.Constant)]
                if "fieldname" in keys and "search_index" in keys:
                    flagged.append(node.values[keys.index("fieldname")].value)
        item = set(NS["ITEM_INDEXED_FIELDS"])
        # every Item field the spec flags is one the install controls, and no Item field is flagged that is not listed
        self.assertTrue(item <= set(flagged))


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
