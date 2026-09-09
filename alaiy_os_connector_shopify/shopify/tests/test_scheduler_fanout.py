"""
Scheduled work runs for every store, not for whichever one is first.

Each of these jobs used to ask connections.enabled_connection() for "the"
store and act on it. With one store that is the same thing as "every store".
With two it silently means the sync only ever runs for one seller, and the
other's stock, orders and caches quietly stop updating with nothing in the
logs to say why -- the job completes successfully every tick.

for_each is what makes that safe: one store's failure is logged against that
store and the rest still run. A shared pass would let one seller's expired
token stop everybody's sync.
"""

import ast
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _hooks_methods():
    src = (ROOT / "hooks.py").read_text(encoding="utf-8")
    out = []
    for n in ast.parse(src).body:
        if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "scheduler_events":
            for v in n.value.values:
                if isinstance(v, ast.Dict):
                    for vv in v.values:
                        out += [e.value for e in vv.elts]
                else:
                    out += [e.value for e in v.elts]
    return out


def _function(dotted):
    mod, fn = dotted.rsplit(".", 1)
    path = ROOT / (mod.replace("alaiy_os_connector_shopify.", "").replace(".", "/") + ".py")
    if not path.exists():
        return None, None
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name == fn:
            return n, path
    for n in ast.walk(tree):                       # follow a re-export shim
        if isinstance(n, ast.ImportFrom):
            for al in n.names:
                if (al.asname or al.name) == fn:
                    return _function(f"{n.module}.{al.name}")
    return None, None


# Genuinely bench-wide: Shopify's own product taxonomy is the same catalogue
# for every seller, so fanning it out would fetch identical data N times.
GLOBAL = {"scheduled_fetch_shopify_taxonomy"}


class TestEveryScheduledJobResolves(unittest.TestCase):
    def test_no_hook_points_at_a_missing_function(self):
        # A renamed function leaves the hook pointing at nothing, and the
        # scheduler logs it once and moves on -- the sync just stops.
        missing = [m for m in _hooks_methods() if _function(m)[0] is None]
        self.assertEqual(missing, [])


class TestEveryScheduledJobCoversEveryStore(unittest.TestCase):
    def test_each_job_fans_out_or_is_deliberately_global(self):
        singles = []
        for dotted in _hooks_methods():
            name = dotted.rsplit(".", 1)[1]
            if name in GLOBAL:
                continue
            fn, _ = _function(dotted)
            code = ast.unparse(fn)
            # connections_summary is for_each plus a per-store result dict,
            # which the two delivery sweeps need because they report a summary.
            if "for_each" not in code and "connections_summary" not in code:
                singles.append(name)
        self.assertEqual(
            singles, [],
            "scheduled but running for only one store:\n  " + "\n  ".join(singles))

    def test_the_global_exemption_still_exists(self):
        names = {m.rsplit(".", 1)[1] for m in _hooks_methods()}
        for name in GLOBAL:
            self.assertIn(name, names, f"{name} is exempt but no longer scheduled")


class TestReconcileDoesNotDedupeAcrossStores(unittest.TestCase):
    def test_the_queued_job_id_carries_the_store(self):
        # deduplicate=True with one shared job_id means the first store's
        # queued sweep suppresses every other store's, so only one seller's
        # stock is ever reconciled -- and nothing reports a problem.
        fn, _ = _function(
            "alaiy_os_connector_shopify.shopify.inventory_sync.enqueue_reconcile_inventory")
        code = ast.unparse(fn)
        self.assertIn("for_each", code)
        self.assertIn("job_id", code)
        self.assertNotIn("job_id='shopify_reconcile_inventory'", code)


if __name__ == "__main__":
    unittest.main()
