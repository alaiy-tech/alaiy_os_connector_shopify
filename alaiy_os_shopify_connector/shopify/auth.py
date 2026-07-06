import requests
import frappe


def get_client_credentials_token(shop_url: str, client_id: str, client_secret: str) -> str:
    """
    Exchange the connector's Client ID/Secret for a fresh Shopify access
    token via the client_credentials grant. Shopify custom-app tokens minted
    this way are short-lived, so this is called both from Test Connection and
    transparently by ShopifyClient whenever a request comes back 401.
    """
    resp = requests.post(
        f"{shop_url}/admin/oauth/access_token",
        params={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        },
        timeout=15,
    )
    if resp.status_code != 200:
        try:
            err = resp.json().get("error_description") or resp.json().get("error") or ""
        except Exception:
            err = ""
        raise RuntimeError(f"Shopify authentication failed ({resp.status_code}){': ' + err if err else ''}")

    access_token = (resp.json().get("access_token") or "").strip()
    if not access_token:
        raise RuntimeError("No access token in Shopify response.")
    return access_token


def refresh_and_store_access_token() -> str:
    """Mint a fresh token from the connector's stored Client ID/Secret and persist it."""
    settings = frappe.get_single("Shopify Connector Settings")

    shop_url = (settings.sh_shop_url or "").strip().rstrip("/")
    if not shop_url.startswith("http"):
        shop_url = f"https://{shop_url}"

    client_id = (settings.sh_client_id or "").strip()
    client_secret = settings.get_password("sh_client_secret") if settings.sh_client_secret else None
    if not client_id or not client_secret:
        raise RuntimeError("Client ID and Client Secret must be saved before authenticating.")

    access_token = get_client_credentials_token(shop_url, client_id, client_secret)

    frappe.db.set_single_value("Shopify Connector Settings", "sh_access_token", access_token)
    frappe.db.commit()
    return access_token
