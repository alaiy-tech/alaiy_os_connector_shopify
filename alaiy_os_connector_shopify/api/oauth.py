"""
Whitelisted entry points for the Connect to Shopify OAuth flow.

start_install builds the authorize URL the desk redirects the browser to;
callback is what Shopify redirects back to once the seller approves. See
shopify/oauth.py for the flow itself and why each check exists.
"""

import frappe
from frappe import _

from alaiy_os_connector_shopify.shopify import oauth
from alaiy_os_connector_shopify.api import require_access


@frappe.whitelist()
def is_configured():
    """Whether the desk should offer the Connect to Shopify button at all."""
    return {"configured": oauth.oauth_configured()}


@frappe.whitelist()
def start_install(shop: str, connection_id: str = None, label: str = None):
    """
    Builds the Shopify authorize URL for this shop and returns it for the
    browser to redirect to.

    `connection_id`, when given, must already be this caller's -- an install
    that lands on someone else's connection would move their store's
    credentials under this session's click, so the same ownership check
    every other record-addressed endpoint uses applies here too.
    """
    if connection_id:
        require_access(connection_id, "write")
    url, _state = oauth.build_install_url(shop, connection_id=connection_id, label=label)
    return {"redirect_url": url}


@frappe.whitelist(allow_guest=True)
def callback():
    """
    Shopify redirects here once the seller approves (or denies) the install.
    allow_guest -- the browser arrives from Shopify's own domain with no
    Alaiy OS session, and the request itself carries no useful identity;
    every guarantee here comes from the HMAC and the state token instead of
    frappe.session.user.
    """
    params = frappe.local.request.args.to_dict()
    # A form route, not the list -- show_oauth_result_if_returning only runs
    # from Shopify Connection's own refresh handler, which needs an open
    # form to fire on. "new" always resolves to one even when nothing was
    # ever created (the failure path has no saved row to point at instead).
    failure_route = "/app/shopify-connection/new"

    try:
        if not oauth.verify_callback_hmac(params):
            frappe.throw(_("Could not verify this request came from Shopify."))

        state_payload = oauth.consume_state(params.get("state"))
        if not state_payload:
            frappe.throw(_("This connection attempt has expired or was already used. Please try Connect to Shopify again."))

        shop = params.get("shop") or state_payload.get("shop")
        shop = oauth.normalize_shop_domain(shop)
        if shop != state_payload.get("shop"):
            # Shopify's own shop param must match what we sent the seller to
            # authorise -- a mismatch means the state was replayed against a
            # different shop than it was issued for.
            frappe.throw(_("This connection attempt does not match the store it was started for."))

        code = params.get("code")
        if not code:
            frappe.throw(_("Shopify did not send back an authorization code."))

        token_data = oauth.exchange_code_for_token(shop, code)
        shop_identity = oauth.fetch_shop_identity(shop, token_data["access_token"])

        conn = oauth.upsert_oauth_connection(
            shop,
            token_data["access_token"],
            shop_identity.get("id") or "",
            scope=token_data.get("scope") or "",
            connection_id=state_payload.get("connection_id") or None,
            label=state_payload.get("label") or shop_identity.get("name") or None,
        )

        # The connection's own form, not the list -- show_oauth_result_if_returning
        # only runs from Shopify Connection's refresh handler, which needs an
        # open form to fire on at all.
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = f"/app/shopify-connection/{conn.name}?shopify_connected={conn.name}"
    except Exception:
        frappe.log_error(
            title="Shopify OAuth: install failed",
            message=frappe.get_traceback(),
        )
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = f"{failure_route}?shopify_connect_error=1"
