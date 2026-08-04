// Small status banner above the standard list view -- Active/Draft/Archived
// counts of the underlying templates, clicking one filters the list to that
// status. Refetched on every onload/refresh so it never needs a page reload
// to catch up with a bulk-enable or an import just having run.
frappe.listview_settings["Shopify Product Listing"] = frappe.listview_settings["Shopify Product Listing"] || {};

function render_shopify_status_banner(listview) {
	frappe.call({
		method: "alaiy_os_connector_shopify.api.sync.get_dashboard_stats",
		callback: function (r) {
			var s = r.message;
			if (!s) return;
			var pills = [
				{ label: "Active", value: s.templates_active, status: "Active" },
				{ label: "Draft", value: s.templates_draft, status: "Draft" },
				{ label: "Archived", value: s.templates_archived, status: "Archived" },
			].map(function (c) {
				return '<span class="shopify-listing-status-pill filterable" data-status="' + c.status +
					'" style="cursor:pointer;">' + __(c.label) + ": <b>" + c.value + "</b></span>";
			}).join("");
			listview.page.add_inner_message(
				'<div class="shopify-listing-status-banner" style="display:flex;gap:14px;">' + pills + "</div>"
			);
			listview.page.wrapper.find(".shopify-listing-status-pill").off("click").on("click", function () {
				frappe.set_route("List", "Shopify Product Listing", { sh_shopify_status: $(this).data("status") });
			});
		},
	});
}

frappe.listview_settings["Shopify Product Listing"].onload = function (listview) {
	render_shopify_status_banner(listview);
};

frappe.listview_settings["Shopify Product Listing"].refresh = function (listview) {
	render_shopify_status_banner(listview);
};
