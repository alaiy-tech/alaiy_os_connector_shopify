const SHOPIFY_STATUS_COLORS = {
	queued: "grey",
	running: "blue",
	success: "green",
	failed: "red",
	skipped: "yellow",
};

frappe.pages["shopify"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "Shopify",
		single_column: true,
	});

	// single_column wraps content in Bootstrap's .container, which caps
	// width and leaves a large dead zone on wide screens -- go full width
	// instead, since this page's cards/table already manage their own layout.
	$(wrapper).find(".container").removeClass("container").addClass("container-fluid");

	$(page.body).append(`
		<div class="shopify-ops-page">
			<div class="shopify-connector-status"></div>
			<div class="shopify-action-groups"></div>
			<div class="shopify-recent-activity">
				<div class="shopify-section-title">${__("Recent Activity")}</div>
				<div class="shopify-activity-list">
					<div class="text-muted">${__("Loading...")}</div>
				</div>
			</div>
		</div>
	`);

	render_connector_status(page);
	render_action_groups(page);
	render_recent_activity(page);
};

function render_connector_status(page) {
	frappe.call({
		method: "alaiy_os.api.connectors.get_all_connectors",
		callback(r) {
			const connector = (r.message || []).find(
				(c) => c.connector_id === "shopify",
			);
			if (!connector) return;
			page.body
				.find(".shopify-connector-status")
				.html(alaiy_os.connector_card._html(connector));
		},
	});
}

function call_with_alert(method, { successMessage, successIndicator = "blue", args } = {}) {
	return frappe.call({
		method,
		args,
		callback(r) {
			const res = r.message || {};
			if (typeof res === "object" && (res.status || res.message)) {
				const indicators = {
					already_synced: "green",
					queued: "blue",
					already_running: "orange",
				};
				frappe.show_alert(
					{
						message: res.message || successMessage,
						indicator: indicators[res.status] || successIndicator,
					},
					7,
				);
			} else {
				frappe.show_alert({ message: successMessage, indicator: successIndicator }, 5);
			}
		},
	});
}

function action_group(title, description, actions) {
	const buttons = actions
		.map(
			(a) =>
				`<button type="button" class="btn btn-default btn-sm shopify-action-btn" data-action="${a.key}">${a.label}</button>`,
		)
		.join("");
	return `
		<div class="shopify-action-card">
			<div class="shopify-action-card-title">${title}</div>
			<div class="shopify-action-card-desc text-muted">${description}</div>
			<div class="shopify-action-card-buttons">${buttons}</div>
		</div>
	`;
}

function render_action_groups(page) {
	const $groups = page.body.find(".shopify-action-groups");

	$groups.html(`
		${action_group(__("Connection"), __("Check credentials and connection health."), [
			{ key: "open-settings", label: __("Open Settings") },
			{ key: "test-connection", label: __("Test Connection") },
		])}
		${action_group(__("Inventory"), __("Push current stock levels to Shopify."), [
			{ key: "sync-inventory", label: __("Sync Inventory to Shopify") },
		])}
		${action_group(
			__("Orders"),
			__("Pull orders from Shopify. Import handles your full order history; Sync only pulls what matches your configured filter."),
			[
				{ key: "sync-orders", label: __("Sync Orders from Shopify") },
				{ key: "import-orders", label: __("Import Existing Orders"), primary: true },
			],
		)}
	`);

	$groups.find('[data-action="open-settings"]').on("click", () => {
		frappe.set_route("Form", "Shopify Connector Settings");
	});

	$groups.find('[data-action="test-connection"]').on("click", (e) => {
		const $btn = $(e.currentTarget).prop("disabled", true);
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
				render_connector_status(page);
			},
			always: () => $btn.prop("disabled", false),
		});
	});

	$groups.find('[data-action="sync-inventory"]').on("click", () => {
		call_with_alert("alaiy_os_connector_shopify.api.sync.trigger_inventory_push", {
			successMessage: __("Inventory push queued"),
		});
	});

	$groups.find('[data-action="sync-orders"]').on("click", () => {
		call_with_alert("alaiy_os_connector_shopify.api.sync.trigger_orders_sync", {
			successMessage: __("Order sync queued"),
		}).then(() => setTimeout(() => render_recent_activity(page), 1500));
	});

	$groups.find('[data-action="import-orders"]').on("click", (e) => {
		const $btn = $(e.currentTarget).prop("disabled", true);
		call_with_alert("alaiy_os_connector_shopify.api.sync.import_existing_orders", {
			successMessage: __("Import started"),
		}).then(() => {
			$btn.prop("disabled", false);
			setTimeout(() => render_recent_activity(page), 1500);
		});
	});
}

function render_recent_activity(page) {
	const $list = page.body.find(".shopify-activity-list");
	frappe.call({
		method: "alaiy_os_connector_shopify.api.sync.get_sync_status",
		callback(r) {
			const rows = r.message || [];
			if (!rows.length) {
				$list.html(`<div class="text-muted">${__("No sync runs yet.")}</div>`);
				return;
			}
			$list.html(`
				<table class="table table-condensed shopify-activity-table">
					<thead>
						<tr>
							<th>${__("Type")}</th>
							<th>${__("Trigger")}</th>
							<th>${__("Status")}</th>
							<th>${__("Processed")}</th>
							<th>${__("Started")}</th>
						</tr>
					</thead>
					<tbody>
						${rows
							.map(
								(row) => `
							<tr>
								<td>${frappe.utils.escape_html(row.sync_type || "")}</td>
								<td>${frappe.utils.escape_html(row.trigger || "")}</td>
								<td><span class="indicator-pill ${SHOPIFY_STATUS_COLORS[row.status] || "darkgrey"}"><span>${frappe.utils.escape_html(row.status || "")}</span></span></td>
								<td>${row.items_processed ?? 0} (${row.items_created ?? 0} ${__("new")})</td>
								<td>${row.started_at ? frappe.datetime.comment_when(row.started_at) : ""}</td>
							</tr>
						`,
							)
							.join("")}
					</tbody>
				</table>
			`);
		},
	});
}
