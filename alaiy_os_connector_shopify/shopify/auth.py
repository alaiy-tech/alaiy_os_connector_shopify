import requests
import frappe
from frappe.utils import now_datetime, add_to_date

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


def refresh_and_store_access_token() -> str:
    """
    Mint a fresh token from the connector's stored Client ID/Secret and
    persist it, along with when it was refreshed and (per Shopify's own
    expires_in) when it will next expire -- both shown on the settings form
    and used by the scheduled proactive-refresh check in sync_jobs.py.
    """
    settings = frappe.get_single("Shopify Connector Settings")

    shop_url = (settings.sh_shop_url or "").strip().rstrip("/")
    if not shop_url.startswith("http"):
        shop_url = f"https://{shop_url}"

    client_id = (settings.sh_client_id or "").strip()
    client_secret = settings.get_password("sh_client_secret") if settings.sh_client_secret else None
    if not client_id or not client_secret:
        raise RuntimeError("Client ID and Client Secret must be saved before authenticating.")

    result = get_client_credentials_token(shop_url, client_id, client_secret)
    access_token = result["access_token"]
    expires_in = result.get("expires_in")

    now = now_datetime()
    updates = {
        "sh_access_token": access_token,
        "sh_token_refreshed_at": now,
        "sh_token_expires_at": add_to_date(now, seconds=expires_in) if expires_in else None,
    }
    for field, value in updates.items():
        frappe.db.set_single_value("Shopify Connector Settings", field, value)
    frappe.db.commit()
    return access_token
