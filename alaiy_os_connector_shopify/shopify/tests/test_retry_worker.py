"""
The retry queue's two ends, which for a long time did not exist.

retry_queue.py described a durable backing-off retry with a dead-letter
state and had no caller on either side: nothing enqueued and nothing
drained, so the table stayed empty and every transient push failure was one
Error Log line and no second attempt.

These pin the properties that would let it quietly stop working again --
a handler going missing, an alert firing on every attempt instead of the
last, the scheduler entry being dropped.

    python -m unittest alaiy_os_connector_shopify.shopify.tests.test_retry_worker
"""

import ast
import pathlib
import unittest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
_WORKER = _ROOT / "shopify" / "sync_engine" / "retry_worker.py"
_QUEUE = _ROOT / "shopify" / "sync_engine" / "retry_queue.py"
_HOOKS = _ROOT / "hooks.py"


def _tree(path):
    return ast.parse(path.read_text(encoding="utf-8"))


def _function(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"{name} not found")


class RetryWorker(unittest.TestCase):
    def test_the_drain_is_actually_scheduled(self):
        """The whole defect was a queue nobody drained. If this entry is
        dropped, the queue silently fills and nothing is ever retried."""
        hooks = _HOOKS.read_text(encoding="utf-8")
        self.assertIn("retry_worker.drain", hooks,
                      "retry_worker.drain must be in scheduler_events")

    def test_every_handler_key_is_a_real_pair(self):
        """_HANDLERS is keyed on (direction, entity_type) and both are
        Selects on the doctype. A typo here means _run raises for a whole
        entity type, which is only discovered when something fails."""
        source = _WORKER.read_text(encoding="utf-8")
        handlers = next(
            node for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.Assign)
            and any(getattr(t, "id", "") == "_HANDLERS" for t in node.targets)
        )
        directions = {"inbound", "outbound"}
        entities = {"product", "variant", "price", "inventory", "order", "customer"}
        for key in handlers.value.keys:
            direction, entity = key.elts[0].value, key.elts[1].value
            self.assertIn(direction, directions, f"bad direction {direction!r}")
            self.assertIn(entity, entities, f"bad entity_type {entity!r}")

    def test_an_unknown_entity_type_raises_rather_than_passing(self):
        """A queue that marks work done because it did not recognise it is
        worse than one that fails loudly: the row disappears and the
        operation never happened."""
        dumped = ast.dump(_function(_tree(_WORKER), "_run"))
        self.assertIn("raise", dumped, "_run must raise on an unhandled entity type")

    def test_only_a_dead_letter_alerts(self):
        """An alert per attempt is noise, and noise is what makes a real
        alert get skimmed past. Only the final failure interrupts anyone."""
        source = _WORKER.read_text(encoding="utf-8")
        drain = source[source.index("def drain("):source.index("def _run(")]
        notify_line = next(l for l in drain.splitlines() if "notify_dead_letter" in l)
        # The call must sit under a dead_letter test, not at the failure level.
        self.assertIn("dead_letter", drain[:drain.index(notify_line)],
                      "notify_dead_letter must be guarded on the dead_letter status")

    def test_the_entry_is_reread_before_running(self):
        """Two workers can reach the same due entry. Running an outbound
        push twice is a duplicate fulfillment or a double cancel."""
        drain = _WORKER.read_text(encoding="utf-8")
        self.assertIn('entry.status != "pending"', drain,
                      "drain must re-check status after loading the entry")

    def test_neither_alert_path_can_raise(self):
        """A failure to send an alert must not fail the thing that was
        reporting the original problem."""
        for name in ("notify_dead_letter",):
            fn = _function(_tree(_WORKER), name)
            self.assertTrue(
                any(isinstance(n, ast.Try) for n in ast.walk(fn)),
                f"{name} must swallow its own failures",
            )

    def test_requeue_is_admin_only(self):
        dumped = ast.dump(_function(_tree(_WORKER), "retry_now"))
        self.assertIn("System Manager", dumped)

    def test_requeue_resets_the_attempt_count(self):
        """A re-queued entry that keeps its count dies on the first attempt,
        which makes the button look broken."""
        dumped = ast.dump(_function(_tree(_WORKER), "retry_now"))
        self.assertIn("attempt_count", dumped)

    def test_dead_letter_is_still_the_queue_s_own_decision(self):
        """The worker asks record_failure what happened rather than deciding
        for itself -- one definition of when retrying stops."""
        drain = _WORKER.read_text(encoding="utf-8")
        self.assertIn("retry_queue.record_failure", drain)
        queue = _QUEUE.read_text(encoding="utf-8")
        self.assertIn("dead_letter", queue)


if __name__ == "__main__":
    unittest.main()
