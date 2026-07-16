frappe.ui.form.on("Shopify Connector Settings", {
  refresh(frm) {
    frm.page.set_title(__("Shopify Settings"));
    alaiy_os.connector_card.mount(frm, "shopify");
    alaiy_os.connector_card.setup_password_reveal(
      frm,
      "sh_client_secret",
      "shopify",
    );
    alaiy_os.connector_card.setup_password_reveal(
      frm,
      "sh_access_token",
      "shopify",
    );
    alaiy_os.connector_card.setup_password_reveal(
      frm,
      "sh_webhook_secret",
      "shopify",
    );

    // Auto-fill Company with the default company if empty
    if (!frm.doc.sh_company) {
      frappe.db
        .get_single_value("Global Defaults", "default_company")
        .then((company) => {
          if (company) frm.set_value("sh_company", company);
        });
    }

    frm.add_custom_button(
      __("Test Connection"),
      () => {
        frappe.call({
          // Goes through the registry wrapper (not test_connection directly)
          // so a successful test also flips the "Connector Status" card at
          // the top of this form from "Not configured" to "Connected" --
          // calling test_connection directly ran the real check but left
          // OS Connector Registry.connection_status untouched.
          method: "alaiy_os.api.connectors.test_connector",
          args: { connector_id: "shopify" },
          callback(r) {
            const res = r.message || {};
            if (res.success) {
              frappe.show_alert(
                { message: res.message || __("Connected"), indicator: "green" },
                5,
              );
            } else {
              frappe.show_alert(
                {
                  message: res.message || __("Connection failed"),
                  indicator: "red",
                },
                7,
              );
            }
            frm.reload_doc();
          },
        });
      },
      __("Actions"),
    );

    frm.add_custom_button(
      __("Sync to Shopify Inventory"),
      () => {
        frappe.call({
          method: "alaiy_os_connector_shopify.api.sync.trigger_inventory_push",
          callback: () =>
            frappe.show_alert(
              { message: __("Inventory push queued"), indicator: "blue" },
              5,
            ),
        });
      },
      __("Actions"),
    );

    frm.add_custom_button(
      __("Sync Orders from Shopify"),
      () => {
        frappe.call({
          method: "alaiy_os_connector_shopify.api.sync.trigger_orders_sync",
          callback: () =>
            frappe.show_alert(
              { message: __("Order sync queued"), indicator: "blue" },
              5,
            ),
        });
      },
      __("Actions"),
    );
  },
});
