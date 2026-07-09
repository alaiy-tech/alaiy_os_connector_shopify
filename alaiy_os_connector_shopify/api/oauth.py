import frappe
import requests


@frappe.whitelist()
def exchange_code_for_token(shop_domain: str, code: str) -> dict:
    """
    Exchange a Shopify OAuth authorization code for a permanent access token.
    Stores the resulting shpat_ token in Shopify Connector Settings.
    """
    settings = frappe.get_single("Shopify Connector Settings")
    client_id = (settings.sh_client_id or "").strip()
    client_secret = settings.get_password("sh_client_secret") if settings.sh_client_secret else None

    if not client_id or not client_secret:
        return {"success": False, "message": "Client ID and Client Secret must be saved before exchanging the token."}

    shop_domain = shop_domain.strip().rstrip("/")
    if not shop_domain.startswith("http"):
        shop_domain = f"https://{shop_domain}"

    try:
        resp = requests.post(
            f"{shop_domain}/admin/oauth/access_token",
            json={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code.strip(),
            },
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        if resp.status_code != 200:
            return {"success": False, "message": f"Shopify returned HTTP {resp.status_code}: {resp.text[:300]}"}

        data = resp.json()
        access_token = data.get("access_token", "")
        if not access_token:
            return {"success": False, "message": "No access_token in Shopify response."}

        frappe.db.set_single_value("Shopify Connector Settings", "sh_access_token", access_token)
        frappe.db.commit()
        return {"success": True, "access_token": access_token}

    except requests.exceptions.Timeout:
        return {"success": False, "message": "Request timed out."}
    except Exception as e:
        return {"success": False, "message": str(e)[:300]}
