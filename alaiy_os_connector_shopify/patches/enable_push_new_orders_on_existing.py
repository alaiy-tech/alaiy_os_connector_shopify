# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""
Keep existing stores on the behaviour they already have.

Creating a Shopify order from an Alaiy OS Sales Order is now a per-store
setting that defaults to off. A store already running this connector was
getting that push before the setting existed, so it is switched on here and
nothing changes until someone turns it off. New connections start off.
"""

import frappe


def execute():
	frappe.db.sql("update `tabShopify Connection` set sh_push_new_orders = 1")
