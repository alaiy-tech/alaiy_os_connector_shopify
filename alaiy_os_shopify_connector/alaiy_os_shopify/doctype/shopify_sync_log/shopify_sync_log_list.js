const SHOPIFY_SYNC_TYPE_COLORS = {
	orders: "pink",
	inventory: "blue",
	webhook: "cyan",
};

const SHOPIFY_TRIGGER_COLORS = {
	scheduled: "purple",
	manual: "orange",
	webhook: "cyan",
};

const SHOPIFY_STATUS_COLORS = {
	queued: "grey",
	running: "blue",
	success: "green",
	failed: "red",
	skipped: "yellow",
};

function alaiy_pill(value, colors) {
	if (!value) return "";
	const color = colors[value] || "darkgrey";
	return `<span class="indicator-pill ${color} filterable" data-filter="=,${value}">
		<span>${frappe.utils.escape_html(value)}</span>
	</span>`;
}

frappe.listview_settings["Shopify Sync Log"] = {
	get_indicator(doc) {
		const map = {
			queued: "grey",
			running: "blue",
			success: "green",
			failed: "red",
			skipped: "yellow",
		};
		return [__(doc.status), map[doc.status] || "darkgrey", `status,=,${doc.status}`];
	},
	formatters: {
		sync_type: (value) => alaiy_pill(value, SHOPIFY_SYNC_TYPE_COLORS),
		trigger: (value) => alaiy_pill(value, SHOPIFY_TRIGGER_COLORS),
		status: (value) => alaiy_pill(value, SHOPIFY_STATUS_COLORS),
	},
};
