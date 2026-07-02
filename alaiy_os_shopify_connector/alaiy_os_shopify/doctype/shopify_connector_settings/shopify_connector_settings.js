frappe.ui.form.on("Shopify Connector Settings", {
	refresh(frm) {
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

		frm.add_custom_button(__("Connect to Shopify (OAuth)"), () => {
			_show_oauth_dialog(frm);
		}, __("Actions"));
	},
});

function _show_oauth_dialog(frm) {
	const shop_url = (frm.doc.sh_shop_url || "").trim().replace(/\/$/, "");
	const client_id = (frm.doc.sh_client_id || "").trim();

	if (!shop_url || !client_id) {
		frappe.show_alert({
			message: __("Save the form with Shop URL and Client ID filled in before connecting."),
			indicator: "orange",
		}, 6);
		return;
	}

	// Normalise shop URL to just the myshopify.com domain
	let shop_domain = shop_url.replace(/^https?:\/\//, "").split("/")[0];
	if (!shop_domain.includes(".")) {
		shop_domain = `${shop_domain}.myshopify.com`;
	}

	const scopes = [
		"read_products", "write_products",
		"read_orders", "write_orders",
		"read_inventory", "write_inventory",
		"read_fulfillments", "write_fulfillments",
	].join(",");

	const redirect_uri = "http://localhost/callback";
	const auth_url = `https://${shop_domain}/admin/oauth/authorize`
		+ `?client_id=${encodeURIComponent(client_id)}`
		+ `&scope=${encodeURIComponent(scopes)}`
		+ `&redirect_uri=${encodeURIComponent(redirect_uri)}`;

	const d = new frappe.ui.Dialog({
		title: __("Connect to Shopify"),
		fields: [
			{
				fieldtype: "HTML",
				fieldname: "instructions",
				options: `
					<div style="margin-bottom:16px;line-height:1.6">
						<b>Step 1.</b> Open the authorization URL below in your browser, install the app, then copy the <code>code=...</code> value from the redirect URL.<br><br>
						<a href="${auth_url}" target="_blank" style="word-break:break-all;font-size:12px">${auth_url}</a>
					</div>
					<div style="margin-bottom:8px"><b>Step 2.</b> Paste the authorization code here:</div>
				`,
			},
			{
				fieldname: "auth_code",
				fieldtype: "Data",
				label: "Authorization Code",
				reqd: 1,
			},
		],
		primary_action_label: __("Exchange for Token"),
		primary_action(values) {
			const code = (values.auth_code || "").trim();
			if (!code) return;
			d.disable_primary_action();
			frappe.call({
				method: "alaiy_os_shopify_connector.api.oauth.exchange_code_for_token",
				args: { shop_domain, code },
				callback(r) {
					d.enable_primary_action();
					const res = r.message || {};
					if (res.success) {
						frappe.show_alert({ message: __("Access token saved. Save the form to apply."), indicator: "green" }, 7);
						frm.set_value("sh_access_token", res.access_token);
						d.hide();
					} else {
						frappe.show_alert({ message: res.message || __("Token exchange failed"), indicator: "red" }, 7);
					}
				},
				error() {
					d.enable_primary_action();
					frappe.show_alert({ message: __("Token exchange failed — check the console."), indicator: "red" }, 7);
				},
			});
		},
	});
	d.show();
}
