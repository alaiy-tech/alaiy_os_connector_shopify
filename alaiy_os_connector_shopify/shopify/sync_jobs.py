import frappe
from frappe.utils import now_datetime, add_to_date

_INTERVAL_MINUTES = {
    "5 min": 5,
    "15 min": 15,
    "30 min": 30,
    "60 min": 60,
}

_TOKEN_REFRESH_INTERVAL_MINUTES = {
    "6 hours": 6 * 60,
    "12 hours": 12 * 60,
    "24 hours": 24 * 60,
}


def check_and_enqueue():
    """
    Called every minute by the Frappe scheduler.
    Checks whether the inventory push or a proactive token refresh is due.
    """
    if not frappe.db.exists("DocType", "Shopify Sync Log"):
        return

    settings = frappe.get_single("Shopify Connector Settings")
    if not settings.is_enabled:
        return

    _maybe_enqueue_inventory(settings.sh_inventory_sync_interval or "Disabled")
    _maybe_refresh_token(settings)
    _maybe_ensure_webhooks(settings)


def _maybe_ensure_webhooks(settings):
    """
    Self-healing check for webhook registration, which otherwise only
    ever runs once automatically (on Shopify Connector Settings.is_enabled
    flipping on) with no retry if that single attempt fails -- confirmed
    in production: it failed because the Shop URL field wasn't filled in
    yet at that exact instant, and inbound sync then silently never
    worked. One read-only list query per minute is cheap; the create
    calls only fire for genuinely missing topics.
    """
    if not settings.sh_shop_url or not settings.sh_access_token:
        return
    from alaiy_os_connector_shopify.shopify.webhooks import ensure_webhooks_registered
    try:
        ensure_webhooks_registered()
    except Exception:
        frappe.log_error(
            title="Shopify: webhook self-heal check failed",
            message=frappe.get_traceback(),
        )


def _maybe_refresh_token(settings):
    """
    Proactively mint a fresh access token on the configured interval, so a
    sync never has to hit (and recover from) an expired-token 401 first --
    ShopifyGraphQLClient's own retry-on-401 already guarantees correctness,
    this just avoids the wasted failed request.
    """
    interval_minutes = _TOKEN_REFRESH_INTERVAL_MINUTES.get(
        settings.sh_token_refresh_interval or "Disabled")
    if not interval_minutes:
        return
    if not settings.sh_client_id or not settings.sh_client_secret:
        return

    if settings.sh_token_refreshed_at:
        due_at = add_to_date(settings.sh_token_refreshed_at,
                             minutes=interval_minutes)
        if now_datetime() < due_at:
            return

    from alaiy_os_connector_shopify.shopify.auth import refresh_and_store_access_token
    try:
        refresh_and_store_access_token()
    except Exception:
        frappe.log_error(
            title="Shopify: scheduled token refresh failed",
            message=frappe.get_traceback(),
        )


def _maybe_enqueue_inventory(interval_setting):
    interval_minutes = _INTERVAL_MINUTES.get(interval_setting)
    if not interval_minutes:
        return

    now = now_datetime()

    running = frappe.db.get_value(
        "Shopify Sync Log",
        {"sync_type": "inventory", "status": "running"},
        "started_at",
        order_by="started_at desc",
    )
    if running:
        elapsed = (now - running).total_seconds()
        if elapsed < 1800:
            return

    last_success = frappe.db.get_value(
        "Shopify Sync Log",
        {"sync_type": "inventory", "status": "success"},
        "started_at",
        order_by="started_at desc",
    )
    if last_success:
        due_at = add_to_date(last_success, minutes=interval_minutes)
        if now < due_at:
            return

    frappe.enqueue(
        "alaiy_os_connector_shopify.shopify.inventory_sync.run_inventory_push",
        queue="long",
        timeout=3600,
        trigger="scheduled",
    )
