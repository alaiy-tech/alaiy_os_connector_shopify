"""
Per-order MySQL advisory lock.

The lock name carries the store as well as the order id. A Shopify order id is
only unique inside one shop, so two sellers both have an order 1001 -- and a
name built from the id alone makes each of them wait on the other for two
unrelated orders on two unrelated shops. That is not a correctness bug, it is
a throughput one, but on a bench filling with sellers it is the kind that gets
worse with every store added.
"""

import frappe


def _lock_name(order_id: str, connection=None) -> str:
    """
    The advisory lock for one order in one store.

    A missing connection keeps the old bench-wide name rather than inventing a
    store. It has to: both halves of a lock/release pair must agree on the
    name, and a caller that cannot name its store still needs the two calls to
    match. It over-locks -- exactly today's behaviour -- instead of silently
    failing to lock at all, which is the safe direction for a guard whose job
    is to serialise a real race.

    MySQL truncates a lock name past 64 characters, and a truncated name is a
    silently *shared* lock, so a long connection id is hashed rather than
    trusted to fit.
    """
    if not connection:
        return f"shopify_order_{order_id}"
    store = getattr(connection, "name", connection)
    name = f"shopify_order_{store}_{order_id}"
    if len(name) <= 64:
        return name
    import hashlib

    digest = hashlib.sha1(f"{store}_{order_id}".encode()).hexdigest()[:32]
    return f"shopify_order_{digest}"


def _acquire_order_lock(order_id: str, timeout: int = 30, connection=None) -> bool:
    """
    MySQL-native advisory lock shared by BOTH _upsert_order and
    _update_order for the same Shopify order_id -- enforced by the DB
    server itself, so it holds across separate worker processes
    regardless of how redis-cache is configured. A single shared lock
    name per order_id serializes our own outbound push (which can itself
    trigger Shopify to send back an echoed orders/updated webhook) against
    the inbound webhook handler for that very echo: observed live, the
    inbound handler loaded the Sales Order before an in-flight local save
    (removing an item) had committed, computed a stale diff against it,
    and then failed with TimestampMismatchError trying to cancel/amend a
    document that had changed underneath it by the time it got there.

    `connection` scopes the lock to one store, so two sellers' unrelated
    orders that happen to share an id do not serialise against each other.
    """
    return bool(frappe.db.sql(
        "SELECT GET_LOCK(%s, %s)", (_lock_name(order_id, connection), timeout))[0][0])


def _release_order_lock(order_id: str, connection=None):
    frappe.db.sql("SELECT RELEASE_LOCK(%s)", (_lock_name(order_id, connection),))
