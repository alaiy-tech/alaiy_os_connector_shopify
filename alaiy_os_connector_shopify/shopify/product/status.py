"""
The single mapping between Shopify's product status and `sh_shopify_status`.

Kept in one place because three call sites need to agree: the importer writing the
field, the canonical builder deciding what a push sends, and the export mutation
that has to unarchive a product before Shopify will accept other changes. They
previously each hardcoded `"DRAFT" if Draft else "ACTIVE"`, which is how ARCHIVED
came to be silently unrepresentable.
"""

# Shopify status -> the value stored locally. Shopify's documented ProductStatus
# enum is ACTIVE / ARCHIVED / DRAFT, but a real store also returned UNLISTED, so
# the unknown case is handled explicitly rather than assumed away.
TO_LOCAL = {
    "ACTIVE": "Active",
    "DRAFT": "Draft",
    "ARCHIVED": "Archived",
}

TO_SHOPIFY = {local: remote for remote, local in TO_LOCAL.items()}

# What the Select offers, in the order it should read in the form.
LOCAL_VALUES = ["Active", "Draft", "Archived"]

DEFAULT_LOCAL = "Active"


def to_local(shopify_status):
    """Local value for a Shopify status, or None when it is not one we model.

    Returning None rather than falling back to Active is the point: the caller
    must decide to leave the field alone and say so, instead of recording a
    status the store never reported. Treating an unknown status as Active is the
    original bug -- an archived product read Active because ARCHIVED matched no
    branch and the field kept its default.
    """
    return TO_LOCAL.get((shopify_status or "").strip().upper())


def to_shopify(local_status):
    """Shopify status for a local value, defaulting to ACTIVE for a blank field."""
    return TO_SHOPIFY.get((local_status or "").strip(), "ACTIVE")


def check_status_mapping():
    """Self-check. No DB, no API.

    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.product.status.check_status_mapping
    """
    assert to_local("ACTIVE") == "Active"
    assert to_local("DRAFT") == "Draft"
    assert to_local("ARCHIVED") == "Archived"
    assert to_local("archived") == "Archived"
    assert to_local("  Archived  ") == "Archived"

    # The case this whole module exists for: an unmodelled status must NOT come
    # back as Active.
    assert to_local("UNLISTED") is None
    # Falling back to the settings checkboxes, it must not be excluded: no
    # checkbox covers it, so nobody chose to skip it, and dropping the product
    # would be silent data loss.
    assert import_allows("UNLISTED") is True
    # But a caller naming its statuses made a closed choice. Letting an
    # unrecognised status through that widens the import past what was asked
    # for -- confirmed live, 116 UNLISTED products arrived in an Active-only
    # import and landed with a blank status field.
    assert import_allows("UNLISTED", {"Active"}) is False
    assert import_allows("ACTIVE", {"Active"}) is True
    assert import_allows("DRAFT", {"Active"}) is False
    assert to_local("") is None
    assert to_local(None) is None

    assert to_shopify("Active") == "ACTIVE"
    assert to_shopify("Draft") == "DRAFT"
    assert to_shopify("Archived") == "ARCHIVED"
    # A blank field is a product nobody set a status on -- ACTIVE matches what
    # Shopify itself defaults a new product to.
    assert to_shopify("") == "ACTIVE"
    assert to_shopify(None) == "ACTIVE"

    # Round trip, so the two directions cannot drift apart.
    for remote, local in TO_LOCAL.items():
        assert to_shopify(local) == remote, (local, remote)
    assert set(LOCAL_VALUES) == set(TO_LOCAL.values())
    assert DEFAULT_LOCAL in LOCAL_VALUES

    print("status mapping self-check passed")


_IMPORT_FIELD = {
    "Active": "sh_import_status_active",
    "Draft": "sh_import_status_draft",
    "Archived": "sh_import_status_archived",
}
_EXPORT_FIELD = {
    "Active": "sh_export_status_active",
    "Draft": "sh_export_status_draft",
    "Archived": "sh_export_status_archived",
}


def _selected(field_map, local_status):
    import frappe

    field = field_map.get(local_status)
    if not field:
        # Unreachable by design -- import_allows returns early for an unmodelled
        # status and export_allows substitutes DEFAULT_LOCAL for a blank one. Kept
        # as a guard, and permissive: a status with no checkbox is one nobody
        # chose to exclude.
        return True
    value = frappe.db.get_single_value("Shopify Connector Settings", field)
    # A field added to the settings after the single row already existed reads
    # back as None, not its declared default -- Frappe only applies a default
    # when a document is created. None means "never set", which for these
    # checkboxes has to mean selected, or upgrading would silently stop
    # importing everything.
    return True if value is None else bool(value)


def parse_statuses(statuses):
    """A caller-supplied status list -> set of local values, or None.

    Accepts a list or a comma-separated string, since a value arriving from a
    desk dialog is JSON-encoded by the time it reaches Python. None or empty
    means "no explicit choice", and the settings checkboxes decide instead.
    """
    if statuses is None or statuses == "":
        return None
    if isinstance(statuses, str):
        statuses = [p for p in statuses.replace("[", "").replace("]", "")
                    .replace('"', "").split(",") if p.strip()]
    chosen = {to_local(s) or str(s).strip().title() for s in statuses}
    return {c for c in chosen if c in LOCAL_VALUES} or None


def search_filter(allowed=None):
    """Shopify product-search string for the statuses being imported, or None.

    Lets Shopify do the filtering instead of fetching every product and
    discarding most of them locally. Confirmed live: an Active-only import
    walked all 288 pages of a 14,382-product catalogue to find 2,503 Active
    ones, skipping 11,879 it had already paid to fetch.

    Returns None when no explicit choice was made, so the caller falls back
    to the settings checkboxes and the unfiltered query -- import_allows
    still applies either way, so this is purely an optimisation and never
    the thing deciding what gets imported.
    """
    if not allowed:
        return None
    statuses = sorted(TO_SHOPIFY[v] for v in allowed if v in TO_SHOPIFY)
    if not statuses:
        return None
    return " OR ".join(f"status:{s.lower()}" for s in statuses)


def import_allows(shopify_status, allowed=None):
    """True when a product with this Shopify status should be imported.

    allowed -- an explicit set from parse_statuses (a per-run choice on the
    dashboard). When given it wins outright; the settings checkboxes are the
    default for a scheduled run, not an extra gate on top of a deliberate one.

    A status we do not model is skipped only when the caller named the
    statuses it wants. Asking for Active is a deliberate, closed choice, and
    letting an unrecognised status through it is not caution -- it silently
    widens the import past what was asked for. Confirmed live: a real store
    returned UNLISTED on 116 products, which arrived in an Active-only import
    and landed with a blank status field, every one of them out of stock at
    every location.

    Falling back to the settings checkboxes it is the opposite: nobody chose
    to exclude a status that has no checkbox, so an unmodelled one is
    imported rather than dropped, with _apply_product_meta logging that its
    status field was left unset.
    """
    local = to_local(shopify_status)
    if allowed is not None:
        return local is not None and local in allowed
    if local is None:
        return True
    return _selected(_IMPORT_FIELD, local)


def export_allows(local_status, allowed=None):
    """True when a Listing holding this local status should be pushed."""
    local = (local_status or "").strip() or DEFAULT_LOCAL
    if allowed is not None:
        return local in allowed
    return _selected(_EXPORT_FIELD, local)
