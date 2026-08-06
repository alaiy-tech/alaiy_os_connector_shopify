// Small banner above the standard list view -- Enabled/Disabled/Total counts
// of the Listings themselves (is_enabled, the actual push gate), clicking one
// filters the list to that state. Refetched on every onload/refresh so it
// never needs a page reload to catch up with a bulk-enable or an import just
// having run.
frappe.listview_settings["Shopify Product Listing"] = frappe.listview_settings["Shopify Product Listing"] || {};

// Own block below the header/filter row -- add_inner_message shares the
// narrow header title slot with whatever else writes there (confirmed live,
// other connectors on this same page also use it, squeezing our pills out
// of view). Rendered into a dedicated div inserted once, refreshed in place
// on every onload/refresh rather than re-inserted, so it never duplicates.
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
				return '<span class="shopify-listing-status-pill filterable" style="cursor:pointer;margin-right:16px;" data-filter=\'' +
					JSON.stringify(c.filter) + "'>" + __(c.label) + ": <b>" + c.value + "</b></span>";
			}).join("");

			var $container = listview.page.wrapper.find(".shopify-listing-status-block");
			if (!$container.length) {
				$container = $(
					'<div class="shopify-listing-status-block" style="padding:8px 20px;border-bottom:1px solid var(--border-color);"></div>'
				);
				// listview.$result is the stable, documented reference to the
				// actual list rows container -- the earlier ".page-content
				// .list-area" guess didn't match this Frappe version's DOM at
				// all, so the block silently never got inserted.
				listview.$result.before($container);
			}
			$container.html(pills);
			$container.find(".shopify-listing-status-pill").off("click").on("click", function () {
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

var SHOPIFY_EXPORT_SYNC_LIMIT = 200; // keep in step with export.py's _SYNC_ROW_LIMIT

function export_listings(listview, scope) {
	var checked = listview.get_checked_items().map(function (d) { return d.name; });
	var args = {};
	if (checked.length) args.listing_names = JSON.stringify(checked);
	if (scope === "enabled") args.only_enabled = "1";
	if (scope === "disabled") args.only_disabled = "1";

	// A checked selection is bounded by hand -- safe to download directly,
	// UNLESS it's still large enough to risk hanging the request (someone
	// can check hundreds of rows just as easily as a handful).
	if (checked.length && checked.length <= SHOPIFY_EXPORT_SYNC_LIMIT) {
		download_export_csv(args);
		return;
	}

	frappe.show_alert({ message: __("Building export in the background -- you'll get a download link when it's ready."), indicator: "blue" }, 6);
	frappe.call({
		method: "alaiy_os_connector_shopify.api.export.trigger_background_export",
		args: args,
	});
}

function download_export_csv(args) {
	// A file download needs a real GET navigation, not frappe.call (which
	// parses the response as JSON) -- build the URL directly and let the
	// browser handle the resulting file response, same pattern Frappe's own
	// report/list exports use.
	var params = new URLSearchParams(args);
	window.open("/api/method/alaiy_os_connector_shopify.api.export.export_listings_csv?" + params.toString());
}

frappe.realtime.on("shopify_listings_export_ready", function (data) {
	frappe.show_alert({
		message: __("Export ready ({0} listings) -- <a href='{1}' target='_blank'>Download CSV</a>", [data.row_count, data.file_url]),
		indicator: "green",
	}, 15);
});

frappe.listview_settings["Shopify Product Listing"].onload = function (listview) {
	render_shopify_status_banner(listview);
	listview.page.add_inner_button(__("Enable Listings by Status"), function () {
		open_enable_by_status_dialog(listview);
	});
	listview.page.add_inner_button(__("All"), function () {
		export_listings(listview, "all");
	}, __("Export"));
	listview.page.add_inner_button(__("Enabled Only"), function () {
		export_listings(listview, "enabled");
	}, __("Export"));
	listview.page.add_inner_button(__("Disabled Only"), function () {
		export_listings(listview, "disabled");
	}, __("Export"));
};

frappe.listview_settings["Shopify Product Listing"].refresh = function (listview) {
	render_shopify_status_banner(listview);
};
