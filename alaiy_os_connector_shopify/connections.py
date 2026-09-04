# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""
Which Shopify Connection a call is about.

Shopify Connector Settings was a Single: one store per site, and every caller
could say `frappe.get_single("Shopify Connector Settings")` and be right. That
is now Shopify Connection, a normal DocType, so one bench can hold many stores
-- which self-serve needs, where every seller shares a site.

Benches are already running the single-store shape, so `resolve()` answers the
old question too. A caller that names no connection gets:

  1. the one flagged `is_default`, if any -- which the upgrade patch sets on the
     row it migrates out of tabSingles;
  2. the only connection, when there is exactly one, which is every
     single-store bench and is why none of them had to change;

and otherwise a refusal. That last case is the important one: on a bench with
several stores, an unnamed call is a bug, and guessing which store it meant
would push one seller's stock to another seller's shop. It has to be louder
than that.

There is deliberately no third rule falling back to the connection *named*
"default". It looks harmless -- that is what the patch calls the migrated row
-- but on a multi-tenant bench it would quietly hand an unnamed call the first
store instead of refusing, which is the whole failure this is meant to prevent.
Rules 1 and 2 already cover every upgraded bench between them.

`resolve_optional` exists for the callers that must not raise: document events
fire on every Item and Sales Order save on the bench, including saves that have
nothing to do with Shopify, so an ambiguous connection there has to mean "do
nothing" rather than "break the save".
"""

import frappe
from frappe import _

DOCTYPE = "Shopify Connection"

# What the upgrade patch names the connection it migrates from tabSingles, and
# what a fresh single-store install gets.
DEFAULT_ID = "default"


class NoConnection(frappe.ValidationError):
    """No connection could be resolved. Distinct from 'not connected yet'."""


def installed() -> bool:
    return bool(frappe.db.exists("DocType", DOCTYPE))


def exists(connection=None) -> bool:
    """True when `resolve` would return a document, without raising."""
    try:
        resolve_name(connection)
        return True
    except Exception:
        return False


def names() -> list[str]:
    """Every connection on this site, oldest first."""
    if not installed():
        return []
    return frappe.get_all(DOCTYPE, pluck="name", order_by="creation asc")


def resolve_name(connection=None) -> str:
    """The name of the connection this call is about."""
    if connection:
        # A Document, not an id -- callers pass either.
        name = getattr(connection, "name", connection)
        if not frappe.db.exists(DOCTYPE, name):
            frappe.throw(_("No Shopify connection {0}.").format(name), NoConnection)
        return name

    default = frappe.db.get_value(DOCTYPE, {"is_default": 1}, "name")
    if default:
        return default

    all_names = names()
    if len(all_names) == 1:
        return all_names[0]

    if not all_names:
        frappe.throw(
            _("No Shopify connection has been set up on this site."), NoConnection
        )

    # Several, none marked default. Picking one would act on the wrong store,
    # which is worse than failing.
    frappe.throw(
        _(
            "This site has {0} Shopify connections, so the call has to name one. "
            "Mark one as the default connection, or pass its id."
        ).format(len(all_names)),
        NoConnection,
    )


def resolve(connection=None):
    """The connection document this call is about."""
    if connection is not None and not isinstance(connection, str):
        # Already a document; hand it straight back so a caller that loaded it
        # for writing does not get a cached copy in its place.
        return connection
    return frappe.get_cached_doc(DOCTYPE, resolve_name(connection))


def resolve_optional(connection=None):
    """
    Like `resolve`, but None instead of a throw.

    For the document events. `on_sales_order_submit` runs on every Sales Order
    on the bench; on a multi-tenant site most of them are not Shopify's, and
    raising NoConnection there would turn "this connector has nothing to say
    about this document" into a failed save for an unrelated app.
    """
    if not installed():
        return None
    try:
        return resolve(connection)
    except Exception:
        return None


def resolve_optional_name(connection=None) -> str | None:
    """
    The connection's name when one can be resolved, else None.

    For the rows that record which store something was for. On a single-store
    bench the caller passes nothing and still gets the stamp, so those logs are
    attributed from the day of the upgrade rather than only once somebody
    starts naming connections.
    """
    doc = resolve_optional(connection)
    return doc.name if doc else None


def for_write(connection=None):
    """Like `resolve`, but never cached -- for a caller about to save."""
    return frappe.get_doc(DOCTYPE, resolve_name(connection))


def by_shop(shop_domain: str):
    """
    The connection for a store domain, or None.

    How an inbound webhook is attributed: Shopify names the store it came from
    in X-Shopify-Shop-Domain, and that is the only thing in the request that
    can say which seller it belongs to. The controller keeps sh_shop_url as a
    bare lowercase host so this is a plain equality match.
    """
    if not shop_domain or not installed():
        return None
    shop = shop_domain.strip().lower()
    shop = shop.removeprefix("https://").removeprefix("http://").split("/")[0]
    name = frappe.db.get_value(DOCTYPE, {"sh_shop_url": shop}, "name")
    return frappe.get_cached_doc(DOCTYPE, name) if name else None


def enabled_names() -> list[str]:
    """
    Connections with the connector switched on for them.

    What the ERPNext-facing scheduled jobs iterate. A self-serve bench holds
    connections that exist only to read a seller's orders through the API and
    deliberately leave `is_enabled` off, so that none of the connector's
    ERPNext writing -- Sales Orders, Delivery Notes, inventory pushes -- runs
    for them.
    """
    if not installed():
        return []
    return frappe.get_all(
        DOCTYPE, filters={"is_enabled": 1}, pluck="name", order_by="creation asc"
    )


def enabled_connection():
    """
    The one store this bench writes ERPNext data for, or None.

    The connector's ERPNext side -- Sales Orders, Delivery Notes, invoices, the
    inventory push, the Item and Sales Order document events -- is written
    around a single store, and several of the records it keeps (Shopify
    Location, the ids stamped on Item and Sales Order) have no room in them to
    say which store they belong to. So exactly one connection may be
    `is_enabled` at a time; the controller enforces it, and this is how those
    paths ask which one it is.

    Multiple connections are still supported, and are the point of this module
    -- they just hold credentials and answer API reads. A self-serve bench has
    one per seller, all with `is_enabled` off, and none of the machinery above
    ever runs for them.

    Never raises. Its callers are document events firing on saves that have
    nothing to do with Shopify, where "no store" has to mean "do nothing".
    """
    names_ = enabled_names()
    if len(names_) != 1:
        return None
    return frappe.get_cached_doc(DOCTYPE, names_[0])


def require_enabled():
    """
    The enabled store, or a refusal that says what to do about it.

    What the ERPNext-facing code uses where it used to say
    `frappe.get_single("Shopify Connector Settings")`. On a single-store bench
    that is the same document it always was. On a bench holding many
    connections it is still exactly one -- the enabled one -- so none of that
    code has to reason about which store it is acting on, and a bench with no
    enabled store is told so instead of quietly acting on somebody's.
    """
    doc = enabled_connection()
    if doc:
        return doc
    if not names():
        frappe.throw(
            _("No Shopify connection has been set up on this site."), NoConnection
        )
    frappe.throw(
        _(
            "No Shopify store is switched on for Alaiy OS on this site. Open the "
            "Shopify Connection you want orders and inventory to sync with and "
            "tick Enable Shopify."
        ),
        NoConnection,
    )


def enabled_value(fieldname: str):
    """
    One field off the enabled store, or None when there is no enabled store.

    Stands in for `frappe.db.get_single_value("Shopify Connector Settings", ...)`
    in the places that read a single flag to decide whether to act. None reads
    as "off", which is the right answer for a bench with no store switched on.
    """
    doc = enabled_connection()
    return doc.get(fieldname) if doc else None


def connected_names() -> list[str]:
    """
    Connections that can actually call Shopify, enabled or not.

    Separate from `enabled_names` because keeping an access token alive is not
    an ERPNext-sync concern: a self-serve connection is never `is_enabled` and
    still needs its token refreshed before it expires.
    """
    ready = []
    for name in names():
        if frappe.get_cached_doc(DOCTYPE, name).is_connected():
            ready.append(name)
    return ready


def for_each(label: str, run, *, only_enabled: bool = True) -> None:
    """
    Run something once per connection, logging failures per store.

    A single-store bench iterates a list of one, so it behaves exactly as it
    did when the settings were a Single. On a bench with several, one store's
    failure is logged against that store and the rest still run -- the
    alternative is one broken connection silently stopping everyone's sync.
    """
    for name in (enabled_names() if only_enabled else connected_names()):
        try:
            run(name)
        except Exception:
            frappe.log_error(
                title=f"Shopify scheduled {label} failed ({name})"[:140],
                message=frappe.get_traceback(),
            )


def create(
    connection_id: str,
    *,
    shop_url: str = None,
    label: str = None,
    owner_app: str = None,
    is_default: bool = False,
    is_enabled: bool = False,
):
    """
    Make a connection. Idempotent on `connection_id`.

    Used by any app that manages stores on this bench; `owner_app` records
    which, so a multi-tenant bench can tell its rows from ones created by hand
    in the desk.

    `is_default` is off unless asked for, and deliberately so. Flagging the
    first connection would look harmless on a single-store bench and be a
    cross-tenant write on a multi-tenant one: every later call that named no
    connection would quietly act on the first seller's store instead of
    refusing. A bench with exactly one connection already resolves it without
    the flag, so nothing needs it.

    `is_enabled` is off for the same shape of reason. Switching a connection on
    registers webhooks and arms this connector's Item/Sales Order document
    events; an app that wants the API client and nothing else must not get
    those by default.
    """
    if frappe.db.exists(DOCTYPE, connection_id):
        return frappe.get_doc(DOCTYPE, connection_id)

    doc = frappe.new_doc(DOCTYPE)
    doc.connection_id = connection_id
    doc.label = label or connection_id
    doc.sh_shop_url = shop_url
    doc.owner_app = owner_app
    doc.is_default = 1 if is_default else 0
    doc.is_enabled = 1 if is_enabled else 0
    doc.insert(ignore_permissions=True)
    return doc
