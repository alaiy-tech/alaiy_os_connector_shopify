"""
Nothing in this connector may assume the bench has one store.

Twenty multi-store bugs shipped past a green suite, and they had one thing in
common: every existing test runs against a bench with a single connection, so
a single-store assumption is invisible to all of them. Each bug was found by
reading, one at a time, after a real two-store bench started refusing calls.

These tests are the structural version of that reading. They walk the source
rather than exercising behaviour, because what has to hold is a property of
every call site -- including ones written next month by someone who has not
read any of this.

Three failure shapes, each of which actually happened:

  * a lookup keyed on a Shopify id with no store, which returns another
    seller's record rather than nothing -- plausible, silent, wrong;
  * `enabled_connection()` / `enabled_value()` read as "the connector is
    off", so on a multi-store bench the feature stops instead of erroring;
  * a UI call that names no store, which is refused outright the moment a
    second store is enabled.
"""

import ast
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _sources():
    for f in sorted(ROOT.rglob("*.py")):
        rel = str(f.relative_to(ROOT)).replace("\\", "/")
        if "__pycache__" in rel or "/tests/" in rel:
            continue
        yield rel, f.read_text(encoding="utf-8", errors="replace")


def _js_sources():
    for f in sorted(ROOT.rglob("*.js")):
        rel = str(f.relative_to(ROOT)).replace("\\", "/")
        if "node_modules" in rel:
            continue
        yield rel, f.read_text(encoding="utf-8", errors="replace")


class TestResolversRequireAStore(unittest.TestCase):
    """
    The two id-to-Item resolvers take `connection` positionally, with no
    default.

    Both used to default to None, which searches every store. A caller that
    had not been converted got a real Item back for somebody else's product,
    with nothing to suggest it was the wrong one -- an order line silently
    attributed to another tenant. Making the argument required is what turned
    that into five import-time failures instead of a production incident.
    """

    RESOLVERS = ("item_by_variant_id", "template_by_product_id")

    def test_neither_resolver_has_a_default_connection(self):
        src = (ROOT / "shopify/product/listing.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        found = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in self.RESOLVERS:
                found[node.name] = node
        self.assertEqual(set(found), set(self.RESOLVERS),
                         "resolver renamed or removed -- update this test with it")

        for name, node in found.items():
            args = [a.arg for a in node.args.args]
            self.assertIn("connection", args, f"{name} lost its connection argument")
            # A default on `connection` means "search every store", which is
            # the behaviour this whole test exists to keep out of reach.
            defaults = dict(zip(args[-len(node.args.defaults):], node.args.defaults)) \
                if node.args.defaults else {}
            self.assertNotIn(
                "connection", defaults,
                f"{name}(connection=...) has a default again: an unconverted "
                f"caller would silently resolve across every store",
            )


class TestNoSilentDisableOnAMultiStoreBench(unittest.TestCase):
    """
    `enabled_connection()` and `enabled_value()` return None where several
    stores are enabled -- there is no single answer to give.

    The bug was never in those two functions. It was that callers treated the
    None as "switched off": new Items stopped getting a Listing, orders
    stopped pushing, the daily inventory backstop reported "connector
    disabled" for every store and never ran. Nothing failed, so nothing was
    noticed.

    Any new use has to be deliberate, so the allow-list is explicit.
    """

    # Where reading "no single store" as "nothing to do" is the correct
    # answer, with the reason it is correct.
    ALLOWED = {
        # Resolution itself: this IS the function that answers the question.
        "connections.py",
        # A single-store bench's registry card. On a bench with several there
        # is no one connection entitled to speak for a shared row, and not
        # writing it is the intended outcome.
        "alaiy_os_connector_shopify/doctype/shopify_connection/shopify_connection.py",
        # One-shot migrate backfills. They run before anyone has named a
        # store and must not fail a migrate on a site that has none, so
        # asking rather than requiring is right. Worth knowing that on a
        # multi-store bench they backfill nothing and say nothing -- these
        # predate multi-store and nobody has needed them since.
        "patches/backfill_listing_title_description.py",
        "patches/backfill_simple_listing_price.py",
    }

    CALLS = re.compile(r"\b(enabled_connection|enabled_value)\s*\(")

    # A fallback is fine; being the ONLY thing consulted is not. These read a
    # store off the document first and reach the fallback only when the
    # document has none -- which is the shape every fix in this area took.
    PRECEDED_BY_A_DOCUMENT_CHECK = re.compile(
        r"(sh_shopify_connection|\.get\(\s*['\"]connection['\"]|"
        r"resolve\(\s*conn|_dn_connection|if conn\b|if connection\b|"
        r"connection\s+if\s+connection|conn\s+if\s+conn|"
        # "there is no document at all" -- a caller asking before one exists,
        # which is the one case where the enabled store is all there is.
        r"doc is None|dn is None)")

    def test_uses_are_confined_to_where_none_really_means_off(self):
        offenders = []
        for rel, src in _sources():
            if any(rel.endswith(a) for a in self.ALLOWED):
                continue
            lines = src.splitlines()
            for i, line in enumerate(lines, start=1):
                if line.lstrip().startswith("#") or not self.CALLS.search(line):
                    continue
                # The document check sits just above, or on this same line as
                # the left-hand side of a conditional fallback.
                window = "\n".join(lines[max(0, i - 12):i])
                if self.PRECEDED_BY_A_DOCUMENT_CHECK.search(window):
                    continue
                offenders.append(f"{rel}:{i}")
        self.assertEqual(
            offenders, [],
            "these consult the enabled store WITHOUT first reading the one on "
            "the document they were handed, so on a multi-store bench they "
            "read None as 'connector disabled' and silently stop:\n  "
            + "\n  ".join(offenders),
        )


class TestDeskCallsNameTheirStore(unittest.TestCase):
    """
    Every UI call to a connector endpoint carries a connection.

    On a bench with several enabled stores an unnamed call is refused, so a
    page that forgets is not subtly wrong -- it is a wall of error dialogs,
    which is how the desk page was found. The fix was to stamp the connection
    in one place per page rather than at each call site; this checks nobody
    has gone back to the call sites.
    """

    # Each page routes its calls through one wrapper that adds the store.
    # Named here so a NEW page cannot quietly skip having one.
    WRAPPERS = {
        "alaiy_os_connector_shopify/page/shopify/shopify.js": "scoped_call",
        "public/js/shopify_product_listing_list.js": "with_shopify_connection",
    }

    CONNECTOR_CALL = re.compile(
        r"""method:\s*['"]alaiy_os_connector_shopify\.([\w.]+)['"]""")

    # Endpoints that genuinely take no store.
    STORELESS = {
        # How a page learns which stores exist -- it cannot already know.
        "api.sync.list_connections",
        # Whether the OAuth app is configured on this site at all. One
        # boolean, no store, asked before any connection exists to name.
        "api.oauth.is_configured",
    }

    # A form passes the record it is open on, and the endpoint reads the store
    # off that record. Nothing to choose and nothing to prompt for -- the
    # document already answers the question.
    NAMES_A_RECORD = re.compile(
        r"\b(collection_name|listing_name|delivery_note|item_code|log_name|"
        r"sales_order|name)\s*:")

    def test_every_page_making_connector_calls_has_a_wrapper(self):
        missing = []
        for rel, src in _js_sources():
            if not self.CONNECTOR_CALL.search(src):
                continue
            wrapper = next((w for path, w in self.WRAPPERS.items()
                            if rel.endswith(path)), None)
            if wrapper is not None:
                self.assertIn(
                    wrapper, src,
                    f"{rel} lost {wrapper}(), the one place its calls get a store",
                )
                continue
            # No wrapper is fine if every connector call names a record the
            # endpoint can resolve the store from.
            for match in re.finditer(r"frappe\.call\(\{(.{0,600}?)\}\)", src, re.S):
                block = match.group(1)
                found = self.CONNECTOR_CALL.search(block)
                if not found or found.group(1) in self.STORELESS:
                    continue
                if "connection" in block or self.NAMES_A_RECORD.search(block):
                    continue
                line = src[:match.start()].count("\n") + 1
                missing.append(f"{rel}:{line} {found.group(1)}")
        self.assertEqual(
            missing, [],
            "these call connector endpoints with no way to name a store -- no "
            "connection, and no record to derive one from -- so every call is "
            "refused once a second store is enabled:\n  " + "\n  ".join(missing),
        )

    def test_every_connector_call_carries_a_connection(self):
        """
        What matters is that a store reaches the endpoint, not the shape of
        the call. A page may stamp it centrally (the desk page wraps
        frappe.call) or pass it per call inside a callback that resolved one
        (the list view does) -- both are fine. What is not fine is a call
        where the argument is nowhere to be seen.
        """
        offenders = []
        for rel, src in _js_sources():
            for match in re.finditer(r"(?:frappe|scoped)\.?call\(\{(.{0,600}?)\}\)",
                                     src, re.S):
                block = match.group(1)
                found = self.CONNECTOR_CALL.search(block)
                if not found or found.group(1) in self.STORELESS:
                    continue
                # Either the call names it, or the page stamps every call.
                if "connection" in block:
                    continue
                if any(rel.endswith(p) and w in src
                       for p, w in self.WRAPPERS.items()):
                    continue
                line = src[:match.start()].count("\n") + 1
                offenders.append(f"{rel}:{line} {found.group(1)}")
        self.assertEqual(
            offenders, [],
            "these name no store, so they are refused once a second store is "
            "enabled:\n  " + "\n  ".join(offenders),
        )


class TestChildTablesAreNotScopedDirectly(unittest.TestCase):
    """
    owned_by() sets a connection column on the doctype it is given, so it is
    only meaningful for a doctype that HAS one.

    Passing it a child table is worse than useless: the filter matches no
    rows at all, so the query comes back empty and whatever it fed silently
    falls back. That shipped once already, against Shopify Listing Variant in
    the inventory push, where an empty variant map meant every variant used
    the Item's own id instead. A child row is scoped through its parent.
    """

    CHILD_TABLES = ("Shopify Listing Variant", "Shopify Listing Image",
                    "Shopify Location Map", "Shopify Listing Metafield")

    def test_owned_by_is_never_called_on_a_child_table(self):
        offenders = []
        for rel, src in _sources():
            for i, line in enumerate(src.splitlines(), start=1):
                for child in self.CHILD_TABLES:
                    if f'owned_by("{child}"' in line:
                        offenders.append(f"{rel}:{i} {child}")
        self.assertEqual(
            offenders, [],
            "a child row carries no connection column, so this filter matches "
            "nothing and the caller silently gets an empty result -- scope "
            "through the parent instead:\n  " + "\n  ".join(offenders),
        )
