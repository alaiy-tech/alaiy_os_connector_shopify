import hashlib
import hmac
import os
import urllib.parse

import requests
import frappe

# Scopes requested during OAuth install. Shopify only asks the merchant to
# approve the combination once; these must match what was declared on the
# Partners dashboard app configuration.
_REQUIRED_SCOPES = ",".join([
    "read_orders", "read_draft_orders",
    "read_customers", "read_customer_events", "read_customer_merge",
    "read_products", "read_product_listings", "read_product_feeds",
    "read_inventory", "read_locations",
    "read_fulfillments",
    "read_assigned_fulfillment_orders",
    "read_merchant_managed_fulfillment_orders",
    "read_third_party_fulfillment_orders",
    "read_shipping", "read_returns",
    "read_discounts", "read_price_rules", "read_gift_cards",
    "read_analytics", "read_reports", "read_marketing_events",
    "read_checkouts", "read_custom_fulfillment_services",
    "read_payment_terms", "read_legal_policies",
    "read_locales", "read_markets", "read_themes",
    "read_translations", "read_content", "read_files",
    "read_metaobjects", "read_metaobject_definitions",
    "read_online_store_pages", "read_script_tags",
    "read_resource_feedbacks", "read_purchase_options",
    "read_customer_data_erasure",
])

_OPTIONAL_SCOPES = ",".join([
    "write_orders", "write_draft_orders",
    "write_customers",
    "write_products", "write_inventory",
    "write_fulfillments",
    "write_assigned_fulfillment_orders",
    "write_merchant_managed_fulfillment_orders",
    "write_third_party_fulfillment_orders",
    "write_shipping", "write_returns",
    "write_discounts", "write_price_rules", "write_gift_cards",
    "write_marketing_events", "write_checkouts",
    "write_custom_fulfillment_services", "write_payment_terms",
    "write_metaobjects", "write_metaobject_definitions",
    "write_online_store_pages", "write_script_tags",
    "write_resource_feedbacks", "write_purchase_options",
    "write_translations", "write_content", "write_files",
    "write_themes", "write_markets", "write_locales",
    "write_customer_merge", "write_customer_data_erasure",
])

# Where Shopify sends the merchant after they click Install.
_CALLBACK_URL = "https://desk.os.alaiy.com/api/method/alaiy_os_connector_shopify.api.oauth.handle_callback"

# Where we send the merchant once the token is saved.
_SUCCESS_REDIRECT = "https://os.alaiy.com/onboarding/connect?connected=shopify"

# Nonce lifetime — enough for a merchant to complete the install screen.
_NONCE_TTL_SECONDS = 600


def _app_credentials() -> tuple[str, str]:
    api_key = (frappe.conf.get("shopify_app_api_key") or "").strip()
    api_secret = (frappe.conf.get("shopify_app_api_secret") or "").strip()
    if not api_key or not api_secret:
        frappe.throw(
            "Shopify OAuth app credentials are not configured. "
            "Add shopify_app_api_key and shopify_app_api_secret to site_config.json."
        )
    return api_key, api_secret


def _normalise_shop(shop: str) -> str:
    """Return the bare myshopify.com hostname, no scheme or trailing slash."""
    shop = shop.strip().lower()
    for prefix in ("https://", "http://"):
        if shop.startswith(prefix):
            shop = shop[len(prefix):]
    shop = shop.rstrip("/")
    if not shop.endswith(".myshopify.com"):
        shop = f"{shop}.myshopify.com"
    return shop


@frappe.whitelist()
def get_connect_url(workspace: str, shop: str) -> dict:
    """
    Build the Shopify OAuth authorisation URL for a given workspace and shop.

    Called internally by alaiy_os_self_serve_apis.api.connections.shopify_connect_url,
    which mirrors the same pattern already in place for Amazon SP-API.

    The nonce is stored in the Frappe Redis cache keyed to the workspace so the
    callback can recover which workspace completed the install.
    """
    api_key, _ = _app_credentials()
    shop = _normalise_shop(shop)

    nonce = os.urandom(16).hex()
    frappe.cache().set_value(
        f"shopify_oauth_nonce:{nonce}",
        workspace,
        expires_in_sec=_NONCE_TTL_SECONDS,
    )

    url = (
        f"https://{shop}/admin/oauth/authorize"
        f"?client_id={api_key}"
        f"&scope={urllib.parse.quote(_REQUIRED_SCOPES)}"
        f"&optional_scopes={urllib.parse.quote(_OPTIONAL_SCOPES)}"
        f"&redirect_uri={urllib.parse.quote(_CALLBACK_URL, safe='')}"
        f"&state={nonce}"
    )
    return {"url": url}


@frappe.whitelist(allow_guest=True)
def handle_callback():
    """
    OAuth callback — Shopify redirects the merchant's browser here after Install.

    Validates the HMAC Shopify signs the callback params with, recovers the
    workspace from the nonce, exchanges the one-time code for a permanent access
    token, then calls alaiy_os_self_serve_apis to store it against the workspace
    before redirecting back to the self-serve app.

    Error redirects carry ?error=<slug> so the self-serve app can surface a
    human-readable message. Shopify does not retry OAuth callbacks, so every
    failure path must redirect rather than return a 4xx — a non-2xx here leaves
    the merchant on an error screen with no way back.
    """
    args = frappe.request.args

    shop = args.get("shop", "")
    code = args.get("code", "")
    state = args.get("state", "")
    hmac_param = args.get("hmac", "")

    _, api_secret = _app_credentials()

    # --- HMAC validation ---
    # Shopify signs every callback: all params except `hmac` are sorted
    # alphabetically, joined as key=value&..., then HMAC-SHA256 with the
    # app secret. The digest is hex, not base64 (unlike webhook validation).
    message = "&".join(
        f"{k}={v}"
        for k, v in sorted(args.items())
        if k != "hmac"
    )
    computed = hmac.new(
        api_secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(computed, hmac_param):
        frappe.log_error(
            title="Shopify OAuth: HMAC validation failed",
            message=f"shop={shop!r}",
        )
        return _redirect(_error_url("invalid_request"))

    # --- Nonce / state validation ---
    nonce_key = f"shopify_oauth_nonce:{state}"
    workspace = frappe.cache().get_value(nonce_key)
    if not workspace:
        frappe.log_error(
            title="Shopify OAuth: nonce expired or not found",
            message=f"shop={shop!r} state={state!r}",
        )
        return _redirect(_error_url("state_mismatch"))
    frappe.cache().delete_value(nonce_key)

    # --- Token exchange ---
    api_key, api_secret = _app_credentials()
    try:
        resp = requests.post(
            f"https://{shop}/admin/oauth/access_token",
            json={"client_id": api_key, "client_secret": api_secret, "code": code},
            timeout=15,
        )
    except requests.exceptions.Timeout:
        frappe.log_error(
            title="Shopify OAuth: token exchange timed out",
            message=f"shop={shop!r}",
        )
        return _redirect(_error_url("shopify_timeout"))

    if resp.status_code != 200:
        frappe.log_error(
            title="Shopify OAuth: token exchange failed",
            message=f"shop={shop!r} status={resp.status_code} body={resp.text[:500]}",
        )
        return _redirect(_error_url("shopify_failed"))

    access_token = (resp.json().get("access_token") or "").strip()
    if not access_token:
        frappe.log_error(
            title="Shopify OAuth: no access_token in Shopify response",
            message=f"shop={shop!r} body={resp.text[:500]}",
        )
        return _redirect(_error_url("shopify_failed"))

    # --- Store the connection ---
    # alaiy_os_self_serve_apis owns the workspace → channel-connection mapping.
    # Call its connect_shopify directly as an in-process Python call — no HTTP
    # round-trip needed since both apps are on the same bench.
    try:
        from alaiy_os.api.connections import connect_shopify as _store
        _store(workspace=workspace, shop=shop, access_token=access_token)
    except Exception:
        frappe.log_error(
            title="Shopify OAuth: failed to store connection",
            message=frappe.get_traceback(),
        )
        return _redirect(_error_url("shopify_failed"))

    return _redirect(_SUCCESS_REDIRECT)


def _redirect(url: str):
    frappe.local.response["type"] = "redirect"
    frappe.local.response["location"] = url


def _error_url(slug: str) -> str:
    return f"https://os.alaiy.com/onboarding/connect?error={slug}"
