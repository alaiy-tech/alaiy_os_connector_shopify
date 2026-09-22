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

    frappe.shopify_connection.show_oauth_result_if_returning();
    frappe.shopify_connection.show_status_banner(frm);

    // Redirects the whole page to Shopify, so there is nothing to await --
    // reconnecting an existing row (auth method already OAuth, or the
    // seller is fixing a revoked install) sends its own name along so the
    // callback updates this row instead of creating a second one.
    frappe.call({
      method: "alaiy_os_connector_shopify.api.oauth.is_configured",
    }).then((r) => {
      if (!(r.message && r.message.configured)) return;
      frm.add_custom_button(__("Connect to Shopify"), () => {
        frappe.shopify_connection.start_install(frm);
      }).addClass("btn-primary");
    });

    if (frm.is_new()) return;

    // Settings-page buttons, not grouped under Actions -- both are about the
    // credentials on this form, not a sync to run.
    frm.add_custom_button(__("Get Access Token"), () => {
      frappe.call({
        // Mints (or re-mints) the token via client_credentials and stores
        // it -- a real write against this store's credentials, split out
        // of Test Connection so a click labelled "Test" is not silently
        // the thing that generates and saves a new token.
        method: "alaiy_os_connector_shopify.api.test_connection.authenticate",
        args: { connection: frm.doc.name },
        freeze: true,
        freeze_message: __("Authenticating with Shopify..."),
        callback(r) {
          const res = r.message || {};
          frappe.show_alert(
            {
              message: res.message || (res.success ? __("Access token obtained") : __("Authentication failed")),
              indicator: res.success ? "green" : "red",
            },
            res.success ? 5 : 7,
          );
          frm.reload_doc();
        },
      });
    });

    frm.add_custom_button(__("Test Connection"), () => {
      frappe.call({
        // Straight to the connector, not through Alaiy OS's generic
        // `test_connector` wrapper. That wrapper takes a connector_id and
        // nothing else, so it cannot say which store to test -- on a bench
        // with several it would test the default one and report the answer
        // on this form. test_connection records the result on the
        // connection itself, which is what keeps the status card above in
        // step either way. Read-only: verifies whatever token already
        // exists rather than minting one -- see Get Access Token for that.
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
    });

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

// Kept off frm rather than nested in the handler above, so start_install has
// one place to live regardless of which button (new-connection page,
// existing row) calls it.
frappe.shopify_connection = {
  start_install(frm) {
    frappe.prompt(
      {
        fieldname: "shop",
        fieldtype: "Data",
        label: __("Shopify store domain"),
        description: __("e.g. your-store.myshopify.com"),
        reqd: 1,
        default: frm.doc.sh_shop_url || "",
      },
      (values) => {
        frappe.call({
          method: "alaiy_os_connector_shopify.api.oauth.start_install",
          args: {
            shop: values.shop,
            // Only a saved, non-new row can be reconnected -- a fresh,
            // unsaved form has nothing yet for the callback to find.
            connection_id: frm.is_new() ? null : frm.doc.name,
            label: frm.doc.label || null,
          },
          freeze: true,
          freeze_message: __("Redirecting to Shopify..."),
        }).then((r) => {
          const url = r.message && r.message.redirect_url;
          if (!url) {
            frappe.msgprint(__("Could not start the Shopify connection."));
            return;
          }
          // Full navigation, not a popup -- Shopify's own approval page
          // does not render inside an iframe/popup for every store.
          window.location.href = url;
        });
      },
      __("Connect to Shopify"),
      __("Continue"),
    );
  },

  // The callback redirects back here with ?shopify_connected=<name> or
  // ?shopify_connect_error=1 rather than trying to render anything itself
  // -- Shopify's redirect has no session, so the desk is the first place
  // that can show a real message and open the resulting row.
  show_oauth_result_if_returning() {
    const params = new URLSearchParams(window.location.search);
    const connected = params.get("shopify_connected");
    const failed = params.get("shopify_connect_error");
    if (!connected && !failed) return;

    // Strip the query string so a refresh does not re-show the same
    // message or re-trigger this on every subsequent load of the page.
    const clean_url = window.location.pathname + window.location.hash;
    window.history.replaceState({}, "", clean_url);

    if (connected) {
      // Already on this exact form -- the OAuth callback redirected here by
      // name. Just the confirmation, no navigation needed.
      frappe.show_alert({ message: __("Shopify connected"), indicator: "green" }, 6);
    } else {
      frappe.msgprint({
        title: __("Shopify connection failed"),
        message: __("Something went wrong connecting to Shopify. Check the Error Log for details, or try Connect to Shopify again."),
        indicator: "red",
      });
    }
  },

  // A persistent read of last_status/last_status_message, shown on every
  // load rather than only right after a Test Connection click -- a
  // connection that went bad since the last time someone opened this form
  // (a revoked OAuth grant, an expired token) should be visible without
  // clicking anything.
  show_status_banner(frm) {
    if (frm.is_new() || !frm.doc.last_status) return;
    const indicator = { connected: "green", error: "red", not_configured: "orange" }[frm.doc.last_status] || "blue";
    frm.dashboard.set_headline_alert(
      `<div class="indicator-pill ${indicator}">${frappe.utils.escape_html(
        frm.doc.last_status_message || frm.doc.last_status,
      )}</div>`,
    );
  },
};
