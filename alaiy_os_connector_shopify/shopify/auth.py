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
    "read_customers", "write_customers",
    # productSet's `files` field (product images) overlaps with fileCreate's
    # scope gating -- Shopify's own product-media guide pairs write_products
    # with this for the same mutation.
    "write_files",
])


def get_client_credentials_token(shop_url: str, client_id: str, client_secret: str) -> dict:
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
            "scope": REQUIRED_SCOPES,
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

    result = get_client_credentials_token(shop_url, client_id, client_secret)
    store_access_token(settings, result["access_token"], result.get("expires_in"))
    return result["access_token"]
