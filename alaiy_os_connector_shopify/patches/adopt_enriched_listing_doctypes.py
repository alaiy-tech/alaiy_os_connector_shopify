# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""Move the four enriched-listing doctypes onto this app's module, early.

The work itself lives in `setup/install.py` and runs from `after_migrate` on
EVERY migrate, which is what actually makes the old app safe to uninstall — see
`adopt_enriched_listing_doctypes` there for why once was not enough.

This patch exists only so the adoption also happens during the post-model-sync
phase of the migrate that first ships it, rather than waiting for the
`after_migrate` hook at the end of the same run. Nothing between the two
depends on it; it is a few seconds, and it means a migrate that dies partway
through for an unrelated reason has still moved the doctypes out of the old
app's reach.

Calling the same function rather than repeating it is the point. Two copies of
a rule about which app owns a table is exactly the kind of duplication that
drifts, and the failure mode here is silent data loss.
"""

from alaiy_os_connector_shopify.setup.install import adopt_enriched_listing_doctypes


def execute():
	adopt_enriched_listing_doctypes()
