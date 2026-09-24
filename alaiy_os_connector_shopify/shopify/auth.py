import requests
import frappe
from frappe.utils import add_to_date, now_datetime
from frappe.utils.password import set_encrypted_password

from alaiy_os_connector_shopify import connections

# Everything the connector calls today (orders, inventory, locations) plus
# what the approved product/order-push roadmap needs next. Shopify's
# client_credentials grant only returns a token scoped to what's requested
# here -- it does NOT automatically inherit every scope enabled on the
# custom app, so omitting one here means every call using it 403s even
# though the app itself is configured with full access.
REQUIRED_SCOPES = ",".join([
    "read_products", "write_products",
    "read_orders", "write_orders",
    "read_inventory", "write_inventory",
    "read_locations",
    # WEBHOOK_TOPICS registers fulfillments/create and fulfillments/update
    # unconditionally -- without this scope Shopify refuses both topics on
    # every registration attempt ("cannot create a webhook subscription
    # with the specified topic"), not just once.
    "read_fulfillments",
    # fulfillmentCreate/fulfillmentCancel/fulfillmentTrackingInfoUpdate
    # (order/queries.py) -- read alone doesn't cover mutating a fulfillment.
    "write_fulfillments",
    "read_customers", "write_customers",
    # productSet's `files` field (product images) overlaps with fileCreate's
    # scope gating -- Shopify's own product-media guide pairs write_products
    # with this for the same mutation.
    "write_files",
    # publishablePublish/publishableUnpublish (collections.py) -- publishing
    # a collection to a sales channel is a separate scope from write_products.
    "write_publications",
])


def scopes_for(connection=None) -> str:
    """REQUIRED_SCOPES plus whatever a connection's own sh_extra_scopes asks
    for on top -- a one-off script or an unreleased feature that needs a
    scope the connector's code doesn't call yet shouldn't have to wait on a
    code change and redeploy to get it requested."""
    extra = (getattr(connection, "sh_extra_scopes", None) or "").strip()
    if not extra:
        return REQUIRED_SCOPES
    extra_list = [s.strip() for s in extra.replace("\n", ",").split(",") if s.strip()]
    return ",".join(dict.fromkeys(REQUIRED_SCOPES.split(",") + extra_list))


def get_client_credentials_token(shop_url: str, client_id: str, client_secret: str, connection=None) -> dict:
    """
    Exchange the connector's Client ID/Secret for a fresh Shopify access
    token via the client_credentials grant. Shopify custom-app tokens minted
    this way are short-lived, so this is called both from Test Connection and
    transparently by ShopifyGraphQLClient whenever a request comes back 401.

    Returns {"access_token": str, "expires_in": int | None} -- expires_in is
    Shopify's own reported lifetime in seconds (observed ~86400 for this app).
    """
    resp = requests.post(
        f"{shop_url}/admin/oauth/access_token",
        params={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scopes_for(connection),
        },
        timeout=15,
    )
    if resp.status_code != 200:
        try:
            err = resp.json().get("error_description") or resp.json().get("error") or ""
        except Exception:
            err = ""
        raise RuntimeError(f"Shopify authentication failed ({resp.status_code}){': ' + err if err else ''}")

    data = resp.json()
    access_token = (data.get("access_token") or "").strip()
    if not access_token:
        raise RuntimeError("No access token in Shopify response.")
    return {"access_token": access_token, "expires_in": data.get("expires_in")}


def store_access_token(connection, access_token: str, expires_in=None) -> None:
    """
    Persist a freshly minted token on a connection, encrypted.

    Written through __Auth rather than straight into the column. The Single
    this replaced was updated with `frappe.db.set_single_value`, which writes
    the raw value to tabSingles and never touches __Auth -- so the store's
    Admin API token sat in the database in plaintext, and `get_password` only
    appeared to work because Document.get_password hands back a field value
    that is set. Moving to a real row is the moment to stop doing that: the
    secret goes to __Auth encrypted with the site key, and the column keeps the
    masked placeholder a Password field is supposed to show.
    """
    set_encrypted_password(
        connection.doctype, connection.name, access_token, "sh_access_token"
    )

    now = now_datetime()
    connection.db_set(
        {
            "sh_access_token": "*" * len(access_token),
            "sh_token_refreshed_at": now,
            "sh_token_expires_at": add_to_date(now, seconds=expires_in) if expires_in else None,
        },
        update_modified=False,
    )
    # Explicit commit, not left to the caller's own transaction: this runs
    # mid-sync, sometimes deep inside an hours-long product/order import
    # (graphql_client.py) or a scheduled proactive-refresh job (sync_jobs.py).
    # If the rest of that operation later fails and rolls back, the freshly
    # minted token must not roll back with it -- losing it would force a
    # re-auth even though the token is still genuinely valid on Shopify's
    # side. # nosemgrep: frapsec-manual-commit
    frappe.db.commit()
    # The in-memory document still holds whatever it was loaded with; a caller
    # that reads the token straight after this must see the new one.
    connection.reload()


def refresh_and_store_access_token(connection=None) -> str:
    """
    Mint a fresh token from a store's stored Client ID/Secret and persist it,
    along with when it was refreshed and (per Shopify's own expires_in) when it
    will next expire -- both shown on the connection form and used by the
    scheduled proactive-refresh check in sync_jobs.py.

    `connection` is a Shopify Connection, its id, or None for the only store on
    a single-store bench.
    """
    settings = connections.for_write(connection)

    shop_url = (settings.sh_shop_url or "").strip().rstrip("/")
    if not shop_url.startswith("http"):
        shop_url = f"https://{shop_url}"

    client_id = (settings.sh_client_id or "").strip()
    client_secret = settings.get_password("sh_client_secret", raise_exception=False)
    if not client_id or not client_secret:
        raise RuntimeError(
            f"Client ID and Client Secret must be saved on Shopify connection "
            f"'{settings.name}' before authenticating."
        )

    result = get_client_credentials_token(shop_url, client_id, client_secret, connection=settings)
    store_access_token(settings, result["access_token"], result.get("expires_in"))
    return result["access_token"]
