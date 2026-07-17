// Loaded via hooks.py's doctype_list_js AFTER Sales Order's own list
// settings, so this only ADDS formatters for our own fields rather than
// replacing whatever ERPNext's core Sales Order list view already configured.
frappe.listview_settings["Sales Order"] = frappe.listview_settings["Sales Order"] || {};
frappe.listview_settings["Sales Order"].formatters = frappe.listview_settings["Sales Order"].formatters || {};

const SH_FINANCIAL_STATUS_COLORS = {
	paid: "green",
	partially_paid: "orange",
	pending: "orange",
	refunded: "grey",
	partially_refunded: "grey",
	voided: "grey",
	authorized: "blue",
	expired: "red",
};

// Keys match Shopify's DisplayFulfillmentStatus enum, lowercased
// (displayFulfillmentStatus in order_sync.py) -- unknown values fall
// back to grey via shopify_status_badge's `colors[value] || "grey"`.
const SH_FULFILLMENT_STATUS_COLORS = {
	fulfilled: "green",
	partially_fulfilled: "orange",
	in_progress: "orange",
	open: "orange",
	pending_fulfillment: "orange",
	scheduled: "blue",
	restocked: "blue",
	on_hold: "red",
	unfulfilled: "grey",
};

function shopify_status_badge(value, colors, fieldname) {
	if (!value) return "";
	const color = colors[value] || "grey";
	const label = value.replace(/_/g, " ");
	return `<span class="indicator-pill ${color} filterable" data-filter="${fieldname},=,${value}">
		<span>${__(label)}</span>
	</span>`;
}

frappe.listview_settings["Sales Order"].formatters.sh_financial_status = function (value) {
	return shopify_status_badge(value, SH_FINANCIAL_STATUS_COLORS, "sh_financial_status");
};

frappe.listview_settings["Sales Order"].formatters.sh_fulfillment_status = function (value) {
	return shopify_status_badge(value, SH_FULFILLMENT_STATUS_COLORS, "sh_fulfillment_status");
};
