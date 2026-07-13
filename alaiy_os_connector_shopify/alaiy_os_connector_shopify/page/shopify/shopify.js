frappe.pages["shopify"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "Shopify",
		single_column: true,
	});

	render_connector_status(page);
	render_actions(page);
};

function render_connector_status(page) {
	frappe.call({
		method: "alaiy_os.api.connectors.get_all_connectors",
		callback(r) {
			const connector = (r.message || []).find(
				(c) => c.connector_id === "shopify",
			);
			if (!connector) return;
			$(page.body).append(alaiy_os.connector_card._html(connector));
		},
	});
}

function render_actions(page) {
	page.add_button(
		__("Open Settings"),
		() => frappe.set_route("Form", "Shopify Connector Settings"),
	);

	page.add_button(__("Test Connection"), () => {
		frappe.call({
			method: "alaiy_os.api.connectors.test_connector",
			args: { connector_id: "shopify" },
			callback(r) {
				const res = r.message || {};
				frappe.show_alert(
					{
						message: res.message || (res.success ? __("Connected") : __("Connection failed")),
						indicator: res.success ? "green" : "red",
					},
					res.success ? 5 : 7,
				);
			},
		});
	});

	page.add_button(__("Sync Inventory to Shopify"), () => {
		frappe.call({
			method: "alaiy_os_connector_shopify.api.sync.trigger_inventory_push",
			callback: () =>
				frappe.show_alert({ message: __("Inventory push queued"), indicator: "blue" }, 5),
		});
	});

	page.add_button(__("Sync Orders from Shopify"), () => {
		frappe.call({
			method: "alaiy_os_connector_shopify.api.sync.trigger_orders_sync",
			callback: () =>
				frappe.show_alert({ message: __("Order sync queued"), indicator: "blue" }, 5),
		});
	});

	page.add_button(__("Import Existing Orders from Shopify"), () => {
		frappe.call({
			method: "alaiy_os_connector_shopify.api.sync.import_existing_orders",
			callback(r) {
				const res = r.message || {};
				const indicators = {
					already_synced: "green",
					queued: "blue",
					already_running: "orange",
				};
				frappe.show_alert(
					{
						message: res.message || __("Import started"),
						indicator: indicators[res.status] || "blue",
					},
					7,
				);
			},
		});
	});

	$(page.body).append(`
		<div class="shopify-ops-page" style="margin-top: 20px;">
			<p class="text-muted">${__(
				"Manual triggers for the Shopify connector. Recent runs are tracked in Shopify Sync Log.",
			)}</p>
		</div>
	`);
}
