# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""This app's own roles, and the gate that reads them.

Two facts live here rather than in the two places that need them. `api/agent.py`
asks "may this caller spend a live Shopify call", and `setup/install.py` asks
"which roles does this app create" — the Amazon connector keeps those in
`api.py:MANAGER_ROLES` and `install.py:APP_ROLES` respectively, and nothing stops
the two drifting apart. One module, imported by both, cannot drift.

App root rather than inside `api/` or `shopify/`, because both packages import it
and neither imports the other.

## Why a role and not a doctype permission

`OS Agent Tool.required_permissions` is a list of `{doctype, ptype}` pairs, which
the engine checks before it will build a runnable. That covers every tool reading
rows the sync already wrote: the doctype the tool reads is the permission it
declares, and `alaiy_os/engine/permissions.py` enforces it without this module.

It cannot express "may spend a live Shopify GraphQL call", because that is not a
read of any doctype — the cost is Shopify's rate limit, not our data. Those tools
declare `[]` and call `require_manager()` themselves, which is the same split the
Amazon pack draws and the reason its `get_amazon_order_metrics` declares nothing.

## Creating the role is not the same as granting it

A new Role row grants nothing on its own. Every doctype in this app shipped with
`System Manager` as its only permission row, so a Shopify Manager who is not also
a System Manager fails `frappe.has_permission("Shopify Product Listing", "read")`
— and the visible symptom is not an error but an absence: `factory.build_runnable`
refuses the run, and `alaiy_os/chat/tools.py` quietly drops every tool from Ask
Alaiy. The permission rows in the doctype JSONs are the other half of this file.
"""

import frappe
from frappe import _

#: Roles this app creates on install. `Shopify Manager` is the operator role —
#: it may spend live Shopify calls and edit the register. `Shopify Viewer` reads
#: only, and is the intended `run_as_user` role for a read-only agent pack.
APP_ROLES = ("Shopify Manager", "Shopify Viewer")

#: Who may spend a live Shopify API call. `System Manager` is here because a
#: fresh site has one before it has ever heard of this app, and locking an admin
#: out of their own connector to enforce a role they can grant themselves is
#: ceremony, not security.
MANAGER_ROLES = ("System Manager", "Shopify Manager")


def require_manager():
    """Throw unless the caller may spend a live Shopify call.

    Used by the handlers in `api/agent.py` that reach Shopify rather than the
    database. A tool behind this gate declares `required_permissions: []`,
    because the field cannot express a role — so this call is the only thing
    between an agent run and the store's rate limit.
    """
    if not set(frappe.get_roles()).intersection(MANAGER_ROLES):
        frappe.throw(_("You are not permitted to perform this action."), frappe.PermissionError)
