"""Site-context tests for the agent pack: handlers, signatures, roles, permissions.

Separate from `test_agent_pack.py` because everything here needs a real site --
`frappe.get_attr` imports the handler module, and the role and permission checks
read the database. Run with:

    bench --site <site> run-tests \
        --module alaiy_os_connector_shopify.shopify.tests.test_agent_handlers

These are the checks that catch a manifest which parses fine and fails mid-run.
`bench migrate` catches most of them too -- the OS Agent Tool child controller
validates every handler and schema on save -- but a test says which tool and why
without needing a migrate to fail.
"""

import inspect
import unittest

import frappe

from alaiy_os_connector_shopify import pack_meta, roles


class TestHandlersResolve(unittest.TestCase):
    def test_every_handler_resolves_and_is_callable(self):
        for tool in pack_meta.TOOLS:
            handler = frappe.get_attr(tool["handler"])
            self.assertTrue(callable(handler), f"{tool['tool_id']} is not callable")

    def test_every_handler_is_whitelisted(self):
        """The executor calls these as the run's user, not as Administrator."""
        for tool in pack_meta.TOOLS:
            handler = frappe.get_attr(tool["handler"])
            self.assertTrue(
                getattr(handler, "__wrapped__", None) is not None
                or handler.__name__ in frappe.whitelisted
                or handler in frappe.whitelisted,
                f"{tool['tool_id']} handler is not @frappe.whitelist()'d",
            )

    def test_every_schema_argument_exists_on_the_handler(self):
        """`engine/executor.py` calls handler(**input).

        A schema key the endpoint does not accept is a TypeError at run time,
        not a hint the model can recover from.
        """
        for tool in pack_meta.TOOLS:
            handler = frappe.get_attr(tool["handler"])
            accepted = set(inspect.signature(handler).parameters)
            declared = set(tool["parameters_schema"].get("properties", {}))
            self.assertEqual(
                declared - accepted,
                set(),
                f"{tool['tool_id']} declares arguments its handler does not take",
            )

    def test_every_required_handler_argument_is_declared_required(self):
        """A parameter with no default is one the model must be told to pass."""
        for tool in pack_meta.TOOLS:
            handler = frappe.get_attr(tool["handler"])
            without_default = {
                name
                for name, param in inspect.signature(handler).parameters.items()
                if param.default is inspect.Parameter.empty
            }
            declared_required = set(tool["parameters_schema"].get("required", []))
            self.assertEqual(
                without_default - declared_required,
                set(),
                f"{tool['tool_id']} has required arguments the schema does not mark required",
            )


class TestRolesAndPermissions(unittest.TestCase):
    def test_the_app_roles_exist(self):
        for role in roles.APP_ROLES:
            self.assertTrue(frappe.db.exists("Role", role), f"{role} was not created on install")

    def test_the_manager_gate_includes_system_manager(self):
        """A fresh site has a System Manager before it has heard of this app."""
        self.assertIn("System Manager", roles.MANAGER_ROLES)
        self.assertIn("Shopify Manager", roles.MANAGER_ROLES)

    def test_the_doctypes_the_pack_reads_grant_the_roles(self):
        """Creating a Role grants nothing; the DocPerm rows are the other half.

        Without these, `factory.build_runnable` refuses the run and
        `chat/tools.py` silently drops every tool from Ask Alaiy -- an absence,
        not an error, which is the hard version to debug.
        """
        for doctype in (
            "Shopify Product Listing",
            "Shopify Sync Log",
            "Shopify Collection",
            "Shopify Location",
        ):
            granted = set(
                frappe.get_all(
                    "DocPerm",
                    filters={"parent": doctype, "read": 1},
                    pluck="role",
                )
            )
            for role in roles.APP_ROLES:
                self.assertIn(role, granted, f"{doctype} does not grant read to {role}")

    def test_a_declared_permission_names_a_real_doctype(self):
        for tool in pack_meta.TOOLS:
            for entry in tool["required_permissions"]:
                self.assertTrue(
                    frappe.db.exists("DocType", entry["doctype"]),
                    f"{tool['tool_id']} declares unknown doctype {entry['doctype']}",
                )


class TestRegistryRow(unittest.TestCase):
    def test_the_pack_is_registered_after_migrate(self):
        if not frappe.db.exists("DocType", "OS Agent Registry"):
            self.skipTest("alaiy_os predates the agent engine on this site")
        self.assertTrue(
            frappe.db.exists("OS Agent Registry", pack_meta.PACK_ID),
            "sync_agent_registry did not run, or the row was deleted",
        )
        doc = frappe.get_doc("OS Agent Registry", pack_meta.PACK_ID)
        self.assertEqual(len(doc.tools), len(pack_meta.TOOLS))
        for row in doc.tools:
            self.assertEqual(row.connector, pack_meta.CONNECTOR_ID)

    def test_the_connector_row_the_tools_link_to_exists(self):
        """engine/factory.py throws when a tool's connector is missing or disabled."""
        if not frappe.db.exists("DocType", "OS Connector Registry"):
            self.skipTest("alaiy_os predates the connector registry on this site")
        self.assertTrue(frappe.db.exists("OS Connector Registry", pack_meta.CONNECTOR_ID))
