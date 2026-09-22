"""
The client's detailed-value -> storefront-filter bucket mapping, as this app
sees it.

Mirrors `matrix.py` (the mandatory-attribute matrix): the mapping is the
client's own storefront taxonomy, not this app's, so it arrives at runtime
through the `listing_filter_matrix` hook.

    # in the client app's hooks.py
    listing_filter_matrix = ["<client_app>.agents.filter_matrix.matrix"]

Unlike `matrix.py`, no client providing this hook is a normal, silent
no-op: filter-bucket writing is an addition on top of the (mandatory)
detailed attributes, not a check anything depends on, so a bench with no
client app -- or a client that hasn't built a filter matrix yet -- simply
never calls `_sync_filter_attributes_as_metafields`.
"""

import frappe

HOOK = "listing_filter_matrix"

REQUIRED_KEYS = ("fields", "buckets", "case_size", "bucket_for", "parse_case_size_mm")

_UNSET = object()


def load():
	"""The installed filter matrix, or None. Validated once per request."""
	cached = getattr(frappe.local, "_listing_filter_matrix", _UNSET)
	if cached is not _UNSET:
		return cached

	spec = _build()
	frappe.local._listing_filter_matrix = spec
	return spec


def _build():
	providers = frappe.get_hooks(HOOK) or []
	if not providers:
		return None

	if len(providers) > 1:
		frappe.throw(
			f"More than one app provides {HOOK}: {providers}. A site has one "
			"storefront and one filter vocabulary, so leave only the customer "
			"app whose store this site is."
		)

	spec = frappe.get_attr(providers[0])()

	missing = [key for key in REQUIRED_KEYS if key not in spec]
	if missing:
		frappe.throw(f"{HOOK} ({providers[0]}) is missing: {', '.join(missing)}.")

	return spec


# ── what the rest of the app asks ─────────────────────────────────────────────


def fields():
	"""{attribute_key: {"metafield_key", "type", "multi"}}, or {} when no matrix."""
	spec = load()
	return dict(spec["fields"]) if spec else {}


def case_size_field():
	"""{"attribute_key", "metafield_key", "type"}, or None when no matrix."""
	spec = load()
	return spec["case_size"] if spec else None


def secondary_fields():
	"""{attribute_key: {"metafield_key", "type", "multi", "fn"}} for an
	attribute that feeds a SECOND metafield besides its `fields()` entry
	(e.g. `gemstones` also feeds Stone Color, not just Stone Type). Optional
	on the client's matrix -- {} for a matrix that predates this or has none."""
	spec = load()
	return dict((spec or {}).get("secondary_fields") or {})


def secondary_value_for(attribute_key, detailed_value):
	"""The bucket(s) this attribute's SECOND metafield gets from this value,
	via that field's own extraction function, or [] (no matrix, no secondary
	field for this key, or no match)."""
	spec = secondary_fields().get(attribute_key)
	if not spec:
		return []
	return frappe.get_attr(spec["fn"])(detailed_value)


def pilot_item_codes():
	"""Item codes `_sync_filter_attributes_as_metafields` is allowed to run
	for, or frozenset() (no matrix, or a matrix with none listed -- both mean
	the feature is a no-op). Optional on the client's matrix, same as
	`secondary_fields`."""
	spec = load()
	return frozenset((spec or {}).get("pilot_item_codes") or ())


def bucket_for(attribute_key, detailed_value):
	"""The filter buckets this value maps onto, or [] (no matrix, or no match --
	the caller cannot tell those apart and must treat both as "leave it")."""
	spec = load()
	if not spec:
		return []
	return frappe.get_attr(spec["bucket_for"])(attribute_key, detailed_value)


def parse_case_size_mm(detailed_value):
	"""The bare integer mm `custom.case_size` reduces to, or None."""
	spec = load()
	if not spec:
		return None
	return frappe.get_attr(spec["parse_case_size_mm"])(detailed_value)
