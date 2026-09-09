import requests
import frappe

from alaiy_os_connector_shopify.api import require_access

from alaiy_os_connector_shopify import connections
from alaiy_os_connector_shopify.shopify.auth import refresh_and_store_access_token


@frappe.whitelist()
def authenticate(connection=None):
    """
    Mint a fresh access token via the client_credentials grant and store it.

    Split out from test_connection: minting is a write against the store's
    own credentials (a new token, a new sh_token_refreshed_at/expires_at) --
    a button labelled "Test" doing that as a hidden first step was honest
    about neither what it changed nor when. This is that step alone; the
    caller runs test_connection after to actually prove the result works.

    `connection` names which store. Left out it means the only store on a
    single-store bench, or the one marked default -- and on a bench with
    several and no default it refuses rather than minting a token for
    somebody else's credentials.
    """
    try:
        settings = connections.resolve(connection)
        require_access(settings.name, "write")
    except Exception as e:
        return {"success": False, "message": str(e)}

    if not (settings.sh_shop_url or "").strip():
        return {"success": False, "message": "Shop URL is not configured."}
    if not (settings.sh_client_id or "").strip() or not settings.sh_client_secret:
        return {"success": False, "message": "Client ID and Client Secret must be saved before authenticating."}

    try:
        refresh_and_store_access_token(settings)
    except requests.exceptions.Timeout:
        return _failed(settings, "Authentication request timed out.")
    except Exception as e:
        return _failed(settings, f"Authentication error: {str(e)[:200]}")

    return {"success": True, "message": "Access token obtained."}


@frappe.whitelist()
def test_connection(connection=None):
    """
    Prove the store's CURRENT access token works. Read-only: does not mint,
    refresh, or change anything about the stored credentials -- run
    authenticate first if there is no token yet, or the current one is bad.

    `connection` names which. Left out it means the only store on a
    single-store bench, or the one marked default -- and on a bench with
    several and no default it refuses rather than testing somebody else's
    credentials and reporting the result as yours.
    """
    try:
        settings = connections.resolve(connection)
        require_access(settings.name)
    except Exception as e:
        return {"success": False, "message": str(e)}

    if not settings.get_password("sh_access_token", raise_exception=False):
        return {"success": False, "message": "No access token yet -- click Get Access Token first."}

    try:
        from alaiy_os_connector_shopify.shopify.graphql_client import ShopifyGraphQLClient
        client = ShopifyGraphQLClient(settings.name)
        data = client.execute("{ shop { id name email } }")
        shop = data.get("shop") or {}
        if shop.get("id"):
            connections.for_write(settings.name).set_status(
                "connected", f"OK ({shop.get('name') or settings.sh_shop_url})"
            )
            return {"success": True, "message": f"Connected to {shop.get('name', 'Shopify')}"}
        return _failed(settings, "Unexpected response from Shopify API")
    except RuntimeError as e:
        return _failed(settings, str(e))
    except Exception as e:
        response = getattr(e, "response", None)
        if response is not None:
            code = response.status_code
            messages = {
                401: "Invalid access token (401 Unauthorized)",
                402: "Shop is on a frozen plan (402)",
                403: "Access token lacks required scopes (403)",
                404: "Shop not found — check the Shop URL (404)",
            }
            return _failed(settings, messages.get(code, f"HTTP {code} error"))
        return _failed(settings, str(e))


def _failed(settings, message: str) -> dict:
    """
    Record the failure on the connection, then report it.

    Every outcome is written here rather than by the caller. Alaiy OS's generic
    `test_connector` wrapper used to be what updated the connector card, but it
    takes only a connector_id -- it has no way to say *which store* was tested,
    so on a bench with several it cannot be the thing that records the result.
    Writing it from inside means the card is right whichever route the test
    came in by.
    """
    connections.for_write(settings.name).set_status("error", message)
    return {"success": False, "message": message}
