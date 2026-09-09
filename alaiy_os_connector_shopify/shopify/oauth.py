"""
Shopify OAuth (authorization code) install flow.

The existing connection method -- a seller creates their own Shopify custom
app and pastes its Client ID/Secret, exchanged via client_credentials -- lives
in shopify/auth.py and is untouched by this module. This adds a second,
self-serve method: one Shopify app that Alaiy OS owns, which every seller
installs on their own store by clicking Connect and approving on Shopify's
own page. No seller ever creates an app or sees a secret.

That one app's own Client ID/Secret are read from site_config
(shopify_oauth_client_id / shopify_oauth_client_secret) -- set once by whoever
runs the bench, not per seller, and never stored on a Shopify Connection row.
Each seller's resulting token is stored on THEIR OWN Shopify Connection,
scoped like every other per-store credential in this connector.

Why the token is not refreshed
-------------------------------
The existing client_credentials path mints a short-lived token from a secret
the connection holds, so it can silently re-mint on a 401. An
authorization-code offline token has no expiry and no refresh grant -- there
is nothing to re-mint it from. A 401 on an OAuth-connected store means the
seller uninstalled or revoked the app; the only remedy is reconnecting.
"""

import hashlib
import hmac
import json
import re
import secrets
from urllib.parse import urlencode

import requests

import frappe
from frappe import _
from frappe.utils import now_datetime

from alaiy_os_connector_shopify.shopify.graphql_client import SHOPIFY_API_VERSION


def _oauth_scopes() -> str:
    """
    Scopes requested at install time. Shopify grants exactly what is asked
    for here and nothing else -- an app configured with a scope in the
    Partner Dashboard has NOT granted it to an installed store.

    Not hardcoded here: site_config's shopify_oauth_scopes wins when set, so
    a bench can widen or narrow what OAuth requests without a code change or
    redeploy. Falls back to shopify/auth.py's REQUIRED_SCOPES -- the same
    list the existing client_credentials path already requires -- so a
    store connected either way ends up with the same access by default,
    defined in exactly one place.
    """
    configured = frappe.conf.get("shopify_oauth_scopes")
    if configured:
        return configured
    from alaiy_os_connector_shopify.shopify.auth import REQUIRED_SCOPES
    return REQUIRED_SCOPES

_REDIRECT_PATH = "/api/method/alaiy_os_connector_shopify.api.oauth.callback"

_STATE_TTL_SECONDS = 600
_STATE_CACHE_PREFIX = "shopify_connector_oauth_state"

# A shop domain, and nothing else. Anchored, no dots in the label, and the
# host must end in .myshopify.com -- this is what stops an attacker handing
# us something like "evil.com#.myshopify.com" and having the backend post
# the app's client secret, or later an access token, to a host they own.
_SHOP_DOMAIN_RE = r"^[a-z0-9][a-z0-9-]*\.myshopify\.com$"


def _app_client_id() -> str:
    """The Alaiy OS Shopify app's Client ID. One app, set once in
    site_config -- never stored on a Shopify Connection row, so it cannot be
    seen or changed by anyone editing a seller's connection."""
    return (frappe.conf.get("shopify_oauth_client_id") or "").strip()


def _app_client_secret() -> str:
    return (frappe.conf.get("shopify_oauth_client_secret") or "").strip()


def _require(value, what):
    if not value:
        # Names what is missing, never a value -- this can surface to a
        # seller, so it must not leak anything about the app itself.
        frappe.throw(
            _("Shopify Connect is not configured on this site. Ask an admin to set {0} in site_config.json.").format(what)
        )
    return value


def oauth_configured() -> bool:
    """Whether the Alaiy OS Shopify app is set up on this site. Drives
    whether the desk offers the one-click Connect button at all -- without
    this it would appear and fail on the first click."""
    return bool(_app_client_id() and _app_client_secret())


def _redirect_uri() -> str:
    configured = frappe.conf.get("shopify_oauth_redirect_uri")
    if configured:
        return configured
    return f"{frappe.utils.get_url().rstrip('/')}{_REDIRECT_PATH}"


def normalize_shop_domain(shop: str) -> str:
    """Reduce whatever the seller typed to a bare myshopify.com host, or
    throw. Accepts a pasted admin URL, a scheme, a trailing path.

    Everything downstream (the authorize URL, the token exchange, the
    connection row) is built from the return value, so this is the only
    place the domain is trusted from user input."""
    shop = (shop or "").strip().lower()
    if not shop:
        frappe.throw(_("Enter your Shopify store domain."))

    shop = shop.split("://", 1)[-1]      # drop scheme
    shop = shop.split("/", 1)[0]         # drop path
    shop = shop.split("?", 1)[0]         # drop query
    shop = shop.split("#", 1)[0]         # drop fragment
    shop = shop.split("@")[-1]           # drop any userinfo
    shop = shop.split(":", 1)[0]         # drop port

    if "." not in shop:
        shop = f"{shop}.myshopify.com"

    if not re.match(_SHOP_DOMAIN_RE, shop):
        frappe.throw(
            _("That doesn't look like a Shopify store domain. It should end in .myshopify.com, for example your-store.myshopify.com")
        )
    return shop


def _state_key(state: str) -> str:
    return f"{_STATE_CACHE_PREFIX}:{state}"


def _store_state(state: str, payload: dict) -> None:
    frappe.cache().set_value(
        _state_key(state), json.dumps(payload), expires_in_sec=_STATE_TTL_SECONDS
    )


def consume_state(state: str):
    """Reads and immediately deletes the state, so a replayed callback finds
    nothing. Returns None when absent -- never issued, already used, or
    expired are indistinguishable to the caller, and all three are failures."""
    if not state:
        return None
    key = _state_key(state)
    # expires=True keeps the value out of frappe.local's in-process cache.
    # Without it a state that has already expired in Redis can still be
    # served from local cache within the same request, defeating the TTL.
    raw = frappe.cache().get_value(key, expires=True)
    frappe.cache().delete_value(key)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None


def build_install_url(shop: str, connection_id: str = None, label: str = None):
    """Authorization URL plus the state bound to this session and shop.

    `connection_id` names an existing Shopify Connection to reconnect
    (installing on the same shop again after a revoke); left blank, the
    callback creates a new one, named from the shop domain.
    """
    client_id = _require(_app_client_id(), "shopify_oauth_client_id")
    shop = normalize_shop_domain(shop)

    state = secrets.token_urlsafe(32)
    _store_state(state, {
        "shop": shop,
        "user": frappe.session.user,
        "connection_id": connection_id or "",
        "label": label or "",
    })

    query = urlencode({
        "client_id": client_id,
        "scope": _oauth_scopes(),
        "redirect_uri": _redirect_uri(),
        "state": state,
    })
    return f"https://{shop}/admin/oauth/authorize?{query}", state


def verify_callback_hmac(query_params: dict) -> bool:
    """Shopify signs the callback query string with the app's Client Secret.

    The signature covers every parameter except hmac itself, sorted by key
    and joined as a query string. Compared in constant time. Returns True
    only on an exact match -- a missing or malformed hmac is a failure, not
    a skip.
    """
    received = query_params.get("hmac")
    if not received:
        return False

    secret = _require(_app_client_secret(), "shopify_oauth_client_secret")
    message = "&".join(
        f"{key}={query_params[key]}"
        for key in sorted(k for k in query_params if k not in ("hmac", "signature"))
    )
    digest = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, received)


def exchange_code_for_token(shop: str, code: str) -> dict:
    """Trade the one-time authorization code for this shop's offline access
    token. `shop` must already have passed normalize_shop_domain -- this
    posts the app's client secret to it."""
    resp = requests.post(
        f"https://{shop}/admin/oauth/access_token",
        json={
            "client_id": _require(_app_client_id(), "shopify_oauth_client_id"),
            "client_secret": _require(_app_client_secret(), "shopify_oauth_client_secret"),
            "code": code,
        },
        timeout=15,
    )
    if resp.status_code != 200:
        # Shopify's error body can echo the request back; never surface it.
        raise RuntimeError(f"Shopify token exchange failed (HTTP {resp.status_code}).")

    data = resp.json()
    token = (data.get("access_token") or "").strip()
    if not token:
        raise RuntimeError("Shopify returned no access token.")
    return {"access_token": token, "scope": data.get("scope") or ""}


def fetch_shop_identity(shop: str, access_token: str) -> dict:
    """The shop's stable id and name, read with the token just obtained.
    Doubles as proof the token actually authenticates before anything is
    saved."""
    resp = requests.post(
        f"https://{shop}/admin/api/{SHOPIFY_API_VERSION}/graphql.json",
        json={"query": "query { shop { id name myshopifyDomain } }"},
        headers={"X-Shopify-Access-Token": access_token, "Content-Type": "application/json"},
        timeout=30,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Could not read shop details from Shopify (HTTP {resp.status_code}).")
    payload = resp.json()
    if payload.get("errors"):
        raise RuntimeError("Could not read shop details from Shopify.")
    return (payload.get("data") or {}).get("shop") or {}


def _connection_id_from_shop(shop: str) -> str:
    """A stable, readable connection id from a shop domain, e.g.
    my-store.myshopify.com -> my-store. Matches DEFAULT_ITEM_CODE_CONNECTION's
    "default" only by coincidence if a shop is literally named that; the
    Connection ID field is set_only_once + unique, so a second OAuth install
    that happens to produce the same id falls through to a numeric suffix."""
    base = shop.split(".", 1)[0]
    base = re.sub(r"[^a-z0-9-]", "-", base) or "shopify-store"
    if not frappe.db.exists("Shopify Connection", base):
        return base
    n = 2
    while frappe.db.exists("Shopify Connection", f"{base}-{n}"):
        n += 1
    return f"{base}-{n}"


def upsert_oauth_connection(shop: str, access_token: str, shop_gid: str, scope: str = "", connection_id: str = None, label: str = None):
    """Create or update a Shopify Connection from a completed OAuth install.

    `connection_id` reconnects an existing row (e.g. after a revoke) without
    creating a duplicate for the same shop; blank creates a fresh one named
    from the shop domain.

    is_enabled is deliberately left OFF here. Turning ERPNext sync on for a
    freshly connected store is a decision this connector already gates
    behind mandatory_depends_on fields (Company, Default Warehouse, Customer
    Group, ...) that OAuth has no way to supply -- the seller still opens the
    connection once to fill those in and flip the switch themselves.
    """
    existing_name = connection_id or frappe.db.get_value(
        "Shopify Connection", {"sh_shop_url": shop}, "name"
    )
    if existing_name and frappe.db.exists("Shopify Connection", existing_name):
        conn = frappe.get_doc("Shopify Connection", existing_name)
    else:
        conn = frappe.new_doc("Shopify Connection")
        conn.connection_id = _connection_id_from_shop(shop)
        conn.label = label or shop.split(".", 1)[0]

    conn.sh_shop_url = shop
    conn.sh_auth_method = "OAuth"
    conn.sh_shop_gid = shop_gid or ""
    conn.sh_granted_scopes = scope or ""
    conn.last_status = "connected"
    conn.last_status_message = f"Connected via Shopify OAuth{': ' + scope if scope else ''}"[:140]
    conn.connected_at = now_datetime()
    conn.flags.ignore_permissions = True
    conn.save()

    # Through the same encrypted path shopify/auth.py uses for a
    # client_credentials token -- straight to __Auth, not the plain column.
    from alaiy_os_connector_shopify.shopify.auth import store_access_token
    store_access_token(conn, access_token, expires_in=None)
    return conn
