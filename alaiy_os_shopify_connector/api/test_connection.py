import requests
import frappe

from alaiy_os_shopify_connector.shopify.auth import refresh_and_store_access_token


@frappe.whitelist()
def test_connection():
    settings = frappe.get_single("Shopify Connector Settings")

    if not (settings.sh_shop_url or "").strip():
        return {"success": False, "message": "Shop URL is not configured."}
    if not (settings.sh_client_id or "").strip() or not settings.sh_client_secret:
        return {"success": False, "message": "Client ID and Client Secret must be saved before testing."}

    # Step 1: Authenticate via client_credentials grant (same helper
    # ShopifyClient falls back to automatically once a token expires).
    try:
        refresh_and_store_access_token()
    except requests.exceptions.Timeout:
        return {"success": False, "message": "Authentication request timed out."}
    except Exception as e:
        return {"success": False, "message": f"Authentication error: {str(e)[:200]}"}

    # Step 2: Verify the token works
    try:
        from alaiy_os_shopify_connector.shopify.client import ShopifyClient
        client = ShopifyClient()
        resp = client.get("shop.json", {"fields": "id,name,email"})
        shop = resp.get("shop", {})
        if shop.get("id"):
            return {"success": True, "message": f"Connected to {shop.get('name', 'Shopify')}"}
        return {"success": False, "message": "Unexpected response from Shopify API"}
    except RuntimeError as e:
        return {"success": False, "message": str(e)}
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
            return {"success": False, "message": messages.get(code, f"HTTP {code} error")}
        return {"success": False, "message": str(e)}
