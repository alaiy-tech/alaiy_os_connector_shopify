"""
Every GraphQL query in the connector, checked against the live schema for
fields Shopify has deprecated.

Read-only. No writes, no mutations.

  bench --site <site> execute \
      alaiy_os_connector_shopify.shopify.deprecation_audit.run

Why this exists as a sweep rather than a checklist: a deprecated field keeps
working, so nothing fails until Shopify removes it -- and then the WHOLE query
fails, not just that field, because GraphQL validates a document as a unit.
An import that ran fine for a year stops dead on an API bump. Four such
fields were already live in this connector when this was written
(Product.images, Product.featuredImage, ProductVariant.image,
Customer.email/phone), none of them causing any visible symptom.

query_audit.py answers "what could we add to the product query". This answers
"what are we selecting today that is on borrowed time", across every query
rather than one.

The check is deliberately coarse in one way, and says so rather than
pretending otherwise: field names are matched flat, so a name selected under
a different parent type still counts as a hit. That over-reports (a false
alarm is cheap to dismiss) rather than under-reports (a missed deprecation is
a future outage). Every hit names the type it was found on, so a spurious one
is obvious on sight.
"""

import importlib
import re

import frappe

_INTROSPECT = """
query IntrospectType($name: String!) {
  __type(name: $name) {
    name
    fields(includeDeprecated: true) {
      name
      isDeprecated
      deprecationReason
    }
  }
}
"""

# Every module holding query constants, and the types those queries select
# from. Adding a query to the connector means adding its module here -- there
# is no auto-discovery, deliberately: an import-everything sweep would drag in
# every module's side effects just to read a string constant.
_QUERY_MODULES = [
    "alaiy_os_connector_shopify.shopify.order.queries",
    "alaiy_os_connector_shopify.shopify.order.delivery_status",
    "alaiy_os_connector_shopify.shopify.product.queries",
    "alaiy_os_connector_shopify.shopify.product.collections",
    "alaiy_os_connector_shopify.shopify.product.stats",
    "alaiy_os_connector_shopify.shopify.product.status_audit",
    "alaiy_os_connector_shopify.shopify.product.variants",
    "alaiy_os_connector_shopify.shopify.inventory_sync",
    "alaiy_os_connector_shopify.shopify.pull_stock_from_shopify",
    "alaiy_os_connector_shopify.shopify.webhooks",
]

# The object types our queries actually select fields from. Introspecting
# every type in the schema would be thousands of round trips for no gain.
_TYPES = [
    "Order", "LineItem", "Customer", "MailingAddress", "Fulfillment",
    "FulfillmentOrder", "FulfillmentLineItem", "OrderRiskSummary",
    "OrderRiskAssessment", "TaxLine", "ShippingLine", "DiscountApplication",
    "Product", "ProductVariant", "ProductOption", "InventoryItem",
    "InventoryLevel", "InventoryQuantity", "Location", "Collection",
    "Publication", "Metafield", "Image", "MediaImage", "WebhookSubscription",
]


def _query_constants():
    """[(module, const_name, query_text)] for every query string we ship."""
    found = []
    for module_path in _QUERY_MODULES:
        try:
            module = importlib.import_module(module_path)
        except Exception as exc:
            print(f"  ! could not import {module_path}: {exc}")
            continue
        for attr in dir(module):
            if not attr.startswith("_") and not attr.isupper():
                continue
            value = getattr(module, attr, None)
            if not isinstance(value, str):
                continue
            # A query/mutation body, not an arbitrary string constant.
            if not re.search(r"\b(query|mutation)\b", value) or "{" not in value:
                continue
            found.append((module_path.rsplit(".", 1)[-1], attr, value))
    return found


def _selected_names(query_text):
    """Field names selected anywhere in a query text.

    Comments and argument lists are stripped first, so neither a name
    mentioned in a "# Product.images is deprecated" note nor an argument
    value (quantities(names: ["available"])) reads as a selected field.
    Both produced phantom findings before they were removed.
    """
    without_comments = re.sub(r"#[^\n]*", "", query_text)
    without_args = re.sub(r"\([^()]*\)", "", without_comments)
    return set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", without_args))


def run(verbose=False):
    from alaiy_os_connector_shopify.shopify.graphql_client import (
        ShopifyGraphQLClient, SHOPIFY_API_VERSION,
    )

    client = ShopifyGraphQLClient()
    print(f"[deprecation_audit] API version {SHOPIFY_API_VERSION}\n")

    queries = _query_constants()
    print(f"[deprecation_audit] {len(queries)} query/mutation constant(s) found\n")

    # {type_name: {field_name: reason}} for deprecated fields only.
    deprecated = {}
    for type_name in _TYPES:
        try:
            data = client.execute(_INTROSPECT, {"name": type_name})
        except Exception as exc:
            print(f"  ! introspection failed for {type_name}: {exc}")
            continue
        type_def = data.get("__type")
        if not type_def:
            print(f"  ! no such type in this API version: {type_name}")
            continue
        fields = type_def.get("fields") or []
        hits = {
            f["name"]: (f.get("deprecationReason") or "").strip()
            for f in fields if f.get("isDeprecated")
        }
        if hits:
            deprecated[type_name] = hits
        if verbose:
            print(f"  {type_name}: {len(fields)} fields, {len(hits)} deprecated")

    if verbose:
        print()

    findings = []
    for module_name, const_name, text in queries:
        selected = _selected_names(text)
        for type_name, fields in deprecated.items():
            for field_name, reason in fields.items():
                if field_name in selected:
                    findings.append((module_name, const_name, type_name,
                                     field_name, reason))

    if not findings:
        print("[deprecation_audit] no deprecated fields selected anywhere. Clean.")
        return {"findings": [], "queries": len(queries)}

    print(f"[deprecation_audit] {len(findings)} deprecated field selection(s):\n")
    by_query = {}
    for module_name, const_name, type_name, field_name, reason in findings:
        by_query.setdefault((module_name, const_name), []).append(
            (type_name, field_name, reason))

    for (module_name, const_name), hits in sorted(by_query.items()):
        print(f"  {module_name}.{const_name}")
        for type_name, field_name, reason in sorted(hits):
            print(f"      {type_name}.{field_name}")
            if reason:
                print(f"          {reason.splitlines()[0][:110]}")
        print()

    print("  Flat name matching: a hit whose type is not actually selected in")
    print("  that query is a false alarm -- check before changing anything.")

    return {
        "findings": [
            {"module": m, "constant": c, "type": t, "field": f, "reason": r}
            for m, c, t, f, r in findings
        ],
        "queries": len(queries),
    }


def validate():
    """Execute every read query once and report which ones the API rejects.

    The only check that proves a query still works. Deprecation is advisory;
    this is the real answer, and it is what catches a field renamed or removed
    outright rather than deprecated first.

    Mutations are skipped -- running them would change the store. Queries
    needing a specific id are skipped too, since a placeholder id proves
    nothing about field validity.

    bench --site <site> execute \
        alaiy_os_connector_shopify.shopify.deprecation_audit.validate
    """
    from alaiy_os_connector_shopify.shopify.graphql_client import (
        ShopifyGraphQLClient, SHOPIFY_API_VERSION,
    )

    client = ShopifyGraphQLClient()
    print(f"[validate] API version {SHOPIFY_API_VERSION}\n")

    ok, failed, skipped = [], [], []
    for module_name, const_name, text in _query_constants():
        label = f"{module_name}.{const_name}"

        if re.search(r"^\s*mutation\b", text.strip(), re.M):
            skipped.append((label, "mutation"))
            continue
        # A required ID! has no safe placeholder -- a made-up id returns null
        # rather than a validation error, so the run would prove nothing.
        if re.search(r"\$\w+:\s*ID!", text):
            skipped.append((label, "needs a real id"))
            continue

        variables = {}
        for name, gql_type in re.findall(r"\$(\w+):\s*([A-Za-z!\[\]]+)", text):
            if gql_type.startswith("Int"):
                variables[name] = 1
            elif gql_type.endswith("!"):
                variables[name] = ""
            else:
                variables[name] = None

        try:
            client.execute(text, variables)
            ok.append(label)
            print(f"  ok      {label}")
        except Exception as exc:
            failed.append((label, str(exc)))
            print(f"  FAILED  {label}\n            {str(exc)[:200]}")

    print(f"\n[validate] {len(ok)} ok, {len(failed)} failed, {len(skipped)} skipped")
    for label, why in skipped:
        print(f"  skipped {label}  ({why})")

    return {"ok": ok, "failed": failed, "skipped": skipped}
