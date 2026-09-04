frappe.ui.form.on("Shopify Connection", {
  refresh(frm) {
    frm.page.set_title(frm.doc.label || __("Shopify Connection"));
    alaiy_os.connector_card.mount(frm, "shopify");
    ["sh_client_secret", "sh_access_token", "sh_webhook_secret"].forEach(
      (field) => alaiy_os.connector_card.setup_password_reveal(frm, field, "shopify"),
    );

    // Auto-fill Company with the default company if empty
    if (!frm.doc.sh_company) {
      frappe.db
        .get_single_value("Global Defaults", "default_company")
        .then((company) => {
          if (company) frm.set_value("sh_company", company);
        });
    }

    if (frm.is_new()) return;

    frm.add_custom_button(
      __("Test Connection"),
      () => {
        frappe.call({
          // Straight to the connector, not through Alaiy OS's generic
          // `test_connector` wrapper. That wrapper takes a connector_id and
          // nothing else, so it cannot say which store to test -- on a bench
          // with several it would test the default one and report the answer
          // on this form. test_connection records the result on the
          // connection itself, which is what keeps the status card above in
          // step either way.
          method: "alaiy_os_connector_shopify.api.test_connection.test_connection",
          args: { connection: frm.doc.name },
          callback(r) {
            const res = r.message || {};
            frappe.show_alert(
              {
                message:
                  res.message || (res.success ? __("Connected") : __("Connection failed")),
                indicator: res.success ? "green" : "red",
              },
              res.success ? 5 : 7,
            );
            frm.reload_doc();
          },
        });
      },
      __("Actions"),
    );

    const queue = (method, message) => () =>
      frappe.call({
        method,
        args: { connection: frm.doc.name },
        callback: () => frappe.show_alert({ message, indicator: "blue" }, 5),
      });

    frm.add_custom_button(
      __("Sync to Shopify Inventory"),
      queue(
        "alaiy_os_connector_shopify.api.sync.trigger_inventory_push",
        __("Inventory push queued"),
      ),
      __("Actions"),
    );

    frm.add_custom_button(
      __("Sync Orders from Shopify"),
      queue(
        "alaiy_os_connector_shopify.api.sync.trigger_orders_sync",
        __("Order sync queued"),
      ),
      __("Actions"),
    );
  },
});
