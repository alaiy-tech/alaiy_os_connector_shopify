"""
Where a repriced product's new price actually comes from, as this connector
sees it.

This app is handed a number, never asked to compute one. A landed cost, an
NLC, a margin band on top of freight and duty -- whatever a store's pricing
configuration works out to -- is that store's business logic, living in
whichever client app owns it (NayaGlobal's landed-cost calculator, or
anything else a future client wants to price with). A base connector that
knows how to calculate a price is a base connector only that one client can
install.

So the number arrives at runtime through the `shopify_price_resolver` hook,
the same seam `listing/matrix.py`, `listing/image_style.py` and
`listing/filter_matrix.py` already use for their own per-client policy:

    # in the client app's hooks.py
    shopify_price_resolver = "<client_app>.pricing.shopify.resolve_prices"

    def resolve_prices(connection, item_codes: list[str]) -> dict:
        '''{item_code: price} for whatever this store's pricing
        configuration is willing to price right now. An item_code left out
        of the answer is not being priced -- the caller skips it, never
        zeroes it and never fails it.'''
        ...

Unlike the attribute matrix, no provider is not a normal, silent no-op here.
A repricing run with nothing to compute a price from is a misconfigured
bench, not a store with no opinion -- so, unlike `matrix.load()`, this
throws rather than degrading to None when zero apps provide the hook, same
as it throws when more than one does.
"""

import frappe

HOOK = "shopify_price_resolver"

_UNSET = object()


def _load():
    """The installed resolver's dotted path, or None. Validated once per
    request -- exactly one provider is a passing state, and that answer is
    reused for the life of the request rather than re-walking the hook
    registry on every batch a repricing run calls it with."""
    cached = getattr(frappe.local, "_shopify_price_resolver_provider", _UNSET)
    if cached is not _UNSET:
        return cached

    providers = frappe.get_hooks(HOOK) or []
    if len(providers) > 1:
        # Two calculators would silently take turns depending on which
        # batch landed last -- a store's live prices would drift between
        # two different apps' arithmetic with no record of which decided.
        frappe.throw(
            f"More than one app provides {HOOK}: {providers}. A store has one "
            "pricing configuration, so leave only the client app whose "
            "calculator prices this store."
        )

    provider = providers[0] if providers else None
    frappe.local._shopify_price_resolver_provider = provider
    return provider


def resolve(connection, item_codes: list) -> dict:
    """{item_code: price} for as many of `item_codes` as this store's
    resolver is willing to price right now.

    `connection` is the Shopify Connection document the run is scoped to
    (the same object export.py's own push paths call `settings`) -- handed
    over as-is so a provider can read whatever store-level configuration it
    needs off it.

    An item_code missing from the answer means the resolver declined to
    price it, not that it costs 0 -- callers must skip those, never push a
    zero and never count them as a failure.

    Throws when no app (or more than one) provides the hook: repricing a
    store with nothing installed to price it, or two apps disagreeing about
    how, is a configuration error worth stopping the run for rather than a
    condition to quietly do nothing about.
    """
    provider = _load()
    if not provider:
        frappe.throw(
            f"No app provides {HOOK}. Repricing a store's live listings needs "
            "exactly one client app registering this hook -- see this "
            "module's docstring for the contract."
        )
    return frappe.get_attr(provider)(connection, list(item_codes)) or {}
