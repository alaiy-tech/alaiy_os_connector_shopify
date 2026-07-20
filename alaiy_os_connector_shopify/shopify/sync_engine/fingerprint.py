"""
Echo detection: compute a stable hash of the fields that actually matter for
a given entity, so a webhook/doc-event carrying data we JUST wrote ourselves
can be recognized and skipped, instead of bouncing back and forth forever
between Alaiy OS and Shopify.
"""

import hashlib
import json


def _money(value) -> str:
    """
    Normalize a price to a 2-decimal string so "20.0" (Alaiy OS float) and
    "20.00" (Shopify string) produce the same fingerprint.
    """
    if value is None or value == "":
        return ""
    return f"{float(value):.2f}"


# Field names that get money-normalized wherever they appear in a canonical
# dict, regardless of entity type.
_MONEY_FIELDS = {"price", "rate", "amount", "price_list_rate"}


def _normalize(value):
    if isinstance(value, dict):
        return {k: (_money(v) if k in _MONEY_FIELDS else _normalize(v)) for k, v in sorted(value.items())}
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    return value


def fingerprint(canonical: dict) -> str:
    """SHA256 over a normalized, key-sorted JSON encoding of `canonical`."""
    normalized = _normalize(canonical or {})
    encoded = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
