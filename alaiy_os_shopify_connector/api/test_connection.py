import frappe


@frappe.whitelist()
def test_connection():
    from alaiy_os_shopify_connector.shopify.client import ShopifyClient

    try:
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
