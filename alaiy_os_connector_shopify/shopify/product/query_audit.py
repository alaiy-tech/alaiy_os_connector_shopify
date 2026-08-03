"""
Diff what our GraphQL queries ask for against what the store's API actually
offers, by introspecting the live schema.

Read-only. No writes, no mutations.

  bench --site <site> execute \
      alaiy_os_connector_shopify.shopify.product.query_audit.run

Why introspection rather than a hand-written list: the field set depends on the
API version the client is pinned to, and a list maintained by hand goes stale
silently -- which is how a field ends up missing for months. Asking the schema is
the only answer that stays true after a version bump.

The report is deliberately blunt about the difference between:
  * a SCALAR we could add to the query today, one line, and
  * an OBJECT or CONNECTION that needs a sub-selection and a decision about where
    the data would even live locally.

It does NOT decide what should be added. A field being available is not a reason
to import it.
"""

import re

import frappe

_INTROSPECT = """
query IntrospectType($name: String!) {
  __type(name: $name) {
    name
    fields(includeDeprecated: false) {
      name
      description
      type {
        kind
        name
        ofType { kind name ofType { kind name ofType { kind name } } }
      }
    }
  }
}
"""

# The types worth auditing, and the query text each is selected inside.
_TYPES = ["Product", "ProductVariant", "InventoryItem"]


def _unwrap(type_ref):
    """(kind, name) for a possibly NON_NULL/LIST-wrapped type."""
    kind = type_ref.get("kind")
    name = type_ref.get("name")
    inner = type_ref.get("ofType")
    while inner:
        if kind in ("NON_NULL", "LIST"):
            kind, name = inner.get("kind"), inner.get("name")
        inner = inner.get("ofType")
    return kind, name


def _selected_field_names(query_text):
    """Field names selected anywhere in a query.

    A flat set, not a tree: this is a "did we ever ask for X" check, so a field
    selected under the wrong parent would read as present. Good enough to find
    what is missing entirely, which is the question being asked -- and stated here
    so nobody reads more into the output than it supports.
    """
    without_args = re.sub(r"\([^()]*\)", "", query_text)
    return set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", without_args))


def run(show_descriptions=False):
    from alaiy_os_connector_shopify.shopify.graphql_client import (
        ShopifyGraphQLClient, SHOPIFY_API_VERSION,
    )
    from alaiy_os_connector_shopify.shopify.product.queries import _PRODUCTS_QUERY

    client = ShopifyGraphQLClient()
    selected = _selected_field_names(_PRODUCTS_QUERY)

    print(f"[query_audit] API version {SHOPIFY_API_VERSION}")
    print(f"[query_audit] our product query selects {len(selected)} distinct names\n")

    summary = {}
    for type_name in _TYPES:
        data = client.execute(_INTROSPECT, {"name": type_name})
        type_def = data.get("__type") or {}
        fields = type_def.get("fields") or []
        if not fields:
            print(f"=== {type_name}: introspection returned nothing "
                  f"(is introspection disabled on this token?)\n")
            continue

        missing_scalar, missing_object, have = [], [], []
        for field in fields:
            kind, name = _unwrap(field["type"])
            entry = (field["name"], name or kind, field.get("description") or "")
            if field["name"] in selected:
                have.append(entry)
            elif kind in ("SCALAR", "ENUM"):
                missing_scalar.append(entry)
            else:
                missing_object.append(entry)

        print(f"=== {type_name}: {len(fields)} field(s) available, "
              f"{len(have)} selected, {len(missing_scalar) + len(missing_object)} not")

        print(f"\n  NOT SELECTED -- scalar/enum, one line each to add ({len(missing_scalar)}):")
        for fname, ftype, desc in sorted(missing_scalar):
            line = f"    {fname:<34} {ftype}"
            if show_descriptions and desc:
                line += f"  -- {desc.splitlines()[0][:80]}"
            print(line)

        print(f"\n  NOT SELECTED -- object/connection, needs a sub-selection ({len(missing_object)}):")
        for fname, ftype, desc in sorted(missing_object):
            print(f"    {fname:<34} {ftype}")

        print()
        summary[type_name] = {
            "available": len(fields),
            "selected": len(have),
            "missing_scalar": len(missing_scalar),
            "missing_object": len(missing_object),
        }

    print("\nCAPS IN THE CURRENT QUERY -- silent truncation, not a missing field")
    for pattern, note in [
        (r"images\(first: (\d+)\)", "images per product"),
        (r"variants\(first: (\d+)\)", "variants per product"),
        (r"collections\(first: (\d+)\)", "collections per product"),
        (r"metafields\(first: (\d+)\)", "metafields per product"),
        (r"inventoryLevels\(first: (\d+)\)", "inventory levels per variant"),
        (r"products\(first: (\d+)", "products per page"),
    ]:
        found = re.search(pattern, _PRODUCTS_QUERY)
        if found:
            print(f"  {note:<34} first: {found.group(1)}")
    print("  A product exceeding one of these caps loses the remainder with no error.")

    return summary


def probe():
    """Which fields exist on the types the product query uses.

    Introspects the live schema and prints each type's field names, so a candidate
    can be checked before it goes into the query. GraphQL validates a document as a
    whole, so ONE bad field name fails the entire product import rather than
    degrading -- confirmed live, `giftCard` on Product does not exist in this API
    version and took the whole query down with it.

    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.product.query_audit.probe
    """
    from alaiy_os_connector_shopify.shopify.graphql_client import (
        ShopifyGraphQLClient, SHOPIFY_API_VERSION,
    )
    from alaiy_os_connector_shopify.shopify.product.queries import _PRODUCTS_QUERY

    client = ShopifyGraphQLClient()
    print(f"[probe] API version {SHOPIFY_API_VERSION}\n")

    out = {}
    for type_name in _TYPES:
        data = client.execute(_INTROSPECT, {"name": type_name})
        fields = (data.get("__type") or {}).get("fields") or []
        names = sorted(f["name"] for f in fields)
        out[type_name] = names
        print(f"=== {type_name} -- {len(names)} field(s)")
        for i in range(0, len(names), 4):
            print("   " + "".join(f"{n:<32}" for n in names[i:i + 4]).rstrip())
        print()

    # The only check that actually matters: does the query we ship validate? The
    # field lists above are advisory, since a name can exist on one type and not
    # the one it is selected under.
    print("[probe] running the real product query...")
    try:
        client.execute(_PRODUCTS_QUERY, {"after": None})
        print("[probe] query is valid against this API version")
        out["query_valid"] = True
    except Exception as exc:
        print(f"[probe] QUERY IS INVALID -- the product import would fail:\n  {exc}")
        out["query_valid"] = False
    return out
