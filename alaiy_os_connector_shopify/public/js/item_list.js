// Loaded via hooks.py's doctype_list_js AFTER Item's own list settings, so
// this only ADDS a formatter for our own field rather than replacing
// whatever Alaiy OS's core Item list view already configured.
frappe.listview_settings["Item"] = frappe.listview_settings["Item"] || {};
frappe.listview_settings["Item"].formatters = frappe.listview_settings["Item"].formatters || {};

// sync_to_shopify is in_list_view already (so it's fetched), but the ID
// fields aren't -- add them to the query without making them visible columns.
frappe.listview_settings["Item"].add_fields = (frappe.listview_settings["Item"].add_fields || [])
	.concat(["sh_shopify_product_id", "sh_shopify_variant_id"]);

frappe.listview_settings["Item"].formatters.sync_to_shopify = function (value, df, doc) {
	const hasShopifyId = doc.sh_shopify_product_id || doc.sh_shopify_variant_id;
	let label, color;
	if (value && hasShopifyId) {
		label = __("On Shopify");
		color = "green";
	} else if (value) {
		label = __("Uploading to Shopify");
		color = "orange";
	} else if (hasShopifyId) {
		// Imported from Shopify (still linked), but the opt-in outbound
		// checkbox is off -- edits made here won't be sent back until
		// it's turned on. Distinct from a genuinely local item that has
		// never touched Shopify at all (the else branch below).
		label = __("Shopify (paused)");
		color = "blue";
	} else {
		label = __("Not on Shopify");
		color = "grey";
	}
	return `<span class="indicator-pill ${color} filterable" data-filter="sync_to_shopify,=,${value ? 1 : 0}">
		<span>${label}</span>
	</span>`;
};
