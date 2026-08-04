// Small banner above the standard list view -- Enabled/Disabled/Total counts
// of the Listings themselves (is_enabled, the actual push gate), clicking one
// filters the list to that state. Refetched on every onload/refresh so it
// never needs a page reload to catch up with a bulk-enable or an import just
// having run.
frappe.listview_settings["Shopify Product Listing"] = frappe.listview_settings["Shopify Product Listing"] || {};

function render_shopify_status_banner(listview) {
	frappe.call({
		method: "alaiy_os_connector_shopify.api.sync.get_dashboard_stats",
		callback: function (r) {
			var s = r.message;
			if (!s) return;
			var disabled = s.listings_total - s.listings_enabled;
			var pills = [
				{ label: "Enabled", value: s.listings_enabled, filter: { is_enabled: 1 } },
				{ label: "Disabled", value: disabled, filter: { is_enabled: 0 } },
				{ label: "Total", value: s.listings_total, filter: {} },
			].map(function (c) {
				return '<span class="shopify-listing-status-pill filterable" data-filter=\'' + JSON.stringify(c.filter) +
					"\" style=\"cursor:pointer;\">" + __(c.label) + ": <b>" + c.value + "</b></span>";
			}).join(" ");
			listview.page.add_inner_message(
				'<div class="shopify-listing-status-banner" style="display:flex;gap:10px;">' + pills + "</div>"
			);
			listview.page.wrapper.find(".shopify-listing-status-pill").off("click").on("click", function () {
				frappe.set_route("List", "Shopify Product Listing", JSON.parse($(this).attr("data-filter")));
			});
		},
	});
}

function open_enable_by_status_dialog(listview) {
	var dialog = new frappe.ui.Dialog({
		title: "Enable Listings by Status",
		fields: [
			{
				fieldtype: "HTML",
				fieldname: "help",
				options: "<p class='text-muted'>Enables every currently-disabled Listing whose status matches what you tick below -- each save fires its normal push, same as ticking one enabled by hand.</p>",
			},
			{ fieldtype: "Check", fieldname: "Active", label: "Active", default: 1,
				description: "Visible and purchasable on Shopify's storefront." },
			{ fieldtype: "Check", fieldname: "Draft", label: "Draft", default: 1,
				description: "Hidden from customers -- not yet published." },
			{ fieldtype: "Check", fieldname: "Archived", label: "Archived", default: 1,
				description: "Taken off sale, but order history is kept." },
		],
		primary_action_label: "Enable",
		primary_action: function (values) {
			var statuses = ["Active", "Draft", "Archived"].filter(function (s) { return values[s]; });
			if (!statuses.length) {
				frappe.msgprint(__("Pick at least one status."));
				return;
			}
			frappe.call({
				method: "alaiy_os_connector_shopify.api.sync.enable_listings_by_status",
				args: { statuses: statuses },
				callback: function (r) {
					if (r.message && r.message.log_name) {
						frappe.show_alert({ message: __("Enabling Listings in the background -- check Shopify Sync Log for progress."), indicator: "blue" }, 7);
					}
				},
			});
			dialog.hide();
		},
	});
	dialog.show();
}

frappe.listview_settings["Shopify Product Listing"].onload = function (listview) {
	render_shopify_status_banner(listview);
	listview.page.add_inner_button(__("Enable Listings by Status"), function () {
		open_enable_by_status_dialog(listview);
	});
};

frappe.listview_settings["Shopify Product Listing"].refresh = function (listview) {
	render_shopify_status_banner(listview);
};
