import requests
import frappe


@frappe.whitelist()
def test_connection():
    settings = frappe.get_single("Shopify Connector Settings")

    shop_url = (settings.sh_shop_url or "").strip().rstrip("/")
    if not shop_url:
        return {"success": False, "message": "Shop URL is not configured."}
    if not shop_url.startswith("http"):
        shop_url = f"https://{shop_url}"

    client_id = (settings.sh_client_id or "").strip()
    client_secret = settings.get_password("sh_client_secret") if settings.sh_client_secret else None

    if not client_id or not client_secret:
        return {"success": False, "message": "Client ID and Client Secret must be saved before testing."}

    # Step 1: Authenticate via client_credentials grant
    try:
        auth_resp = requests.post(
            f"{shop_url}/admin/oauth/access_token",
            params={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            },
            timeout=15,
        )
        if auth_resp.status_code != 200:
            try:
                err = auth_resp.json().get("error_description") or auth_resp.json().get("error") or ""
            except Exception:
                err = ""
            return {"success": False, "message": f"Authentication failed ({auth_resp.status_code}){': ' + err if err else ''}"}

        auth_data = auth_resp.json()
        access_token = (auth_data.get("access_token") or "").strip()
        if not access_token:
            return {"success": False, "message": "No access token in Shopify response."}

        # Step 2: Persist the new token
        frappe.db.set_single_value("Shopify Connector Settings", "sh_access_token", access_token)
        frappe.db.commit()

    except requests.exceptions.Timeout:
        return {"success": False, "message": "Authentication request timed out."}
    except Exception as e:
        return {"success": False, "message": f"Authentication error: {str(e)[:200]}"}

    # Step 3: Verify the token works
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
