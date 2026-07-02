import urllib.parse

import requests
import frappe


class ShopifyClient:
    """Thin wrapper over the Shopify Admin REST API."""

    def __init__(self):
        settings = frappe.get_single("Shopify Connector Settings")
        if not settings.sh_shop_url:
            raise RuntimeError("Shopify Shop URL is not configured.")
        if not settings.sh_access_token:
            raise RuntimeError("Shopify Access Token is not configured.")

        shop_url = settings.sh_shop_url.strip().rstrip("/")
        if not shop_url.startswith("http"):
            shop_url = f"https://{shop_url}"

        api_version = (settings.sh_api_version or "2024-01").strip()
        self.base_url = f"{shop_url}/admin/api/{api_version}"
        self.token = settings.get_password("sh_access_token")

        self.session = requests.Session()
        self.session.headers.update({
            "X-Shopify-Access-Token": self.token,
            "Content-Type": "application/json",
        })

    def get(self, endpoint, params=None):
        resp = self.session.get(f"{self.base_url}/{endpoint}", params=params)
        resp.raise_for_status()
        return resp.json()

    def post(self, endpoint, data=None):
        resp = self.session.post(f"{self.base_url}/{endpoint}", json=data)
        resp.raise_for_status()
        return resp.json()

    def put(self, endpoint, data=None):
        resp = self.session.put(f"{self.base_url}/{endpoint}", json=data)
        resp.raise_for_status()
        return resp.json()

    def delete(self, endpoint):
        resp = self.session.delete(f"{self.base_url}/{endpoint}")
        resp.raise_for_status()
        return resp

    def get_paginated(self, endpoint, params=None):
        """
        Generator over all pages using Shopify cursor-based pagination.
        Yields the full response dict for each page.
        """
        params = dict(params or {})
        params.setdefault("limit", 250)

        while True:
            resp = self.session.get(f"{self.base_url}/{endpoint}", params=params)
            resp.raise_for_status()
            yield resp.json()

            link_header = resp.headers.get("Link", "")
            if 'rel="next"' not in link_header:
                break

            next_url = None
            for part in link_header.split(","):
                if 'rel="next"' in part:
                    next_url = part.split(";")[0].strip().strip("<>")
                    break
            if not next_url:
                break

            parsed = urllib.parse.urlparse(next_url)
            page_info_list = urllib.parse.parse_qs(parsed.query).get("page_info")
            if not page_info_list:
                break
            # cursor pagination: only page_info + limit allowed
            params = {"limit": 250, "page_info": page_info_list[0]}
