frappe.ui.form.on("Shopify Connector Settings", {
	refresh(frm) {
		// Auto-fill Company with the default company if empty
		if (!frm.doc.sh_company) {
			frappe.db.get_single_value("Global Defaults", "default_company").then(company => {
				if (company) frm.set_value("sh_company", company);
			});
		}

		frm.add_custom_button(__("Test Connection"), () => {
			frappe.call({
				method: "alaiy_os_shopify_connector.api.test_connection.test_connection",
				callback(r) {
					const res = r.message || {};
					if (res.success) {
						frappe.show_alert({ message: res.message || __("Connected"), indicator: "green" }, 5);
					} else {
						frappe.show_alert({ message: res.message || __("Connection failed"), indicator: "red" }, 7);
					}
				},
			});
		}, __("Actions"));
	},
});
