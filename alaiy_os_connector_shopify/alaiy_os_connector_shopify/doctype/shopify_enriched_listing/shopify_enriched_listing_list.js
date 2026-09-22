// "Approve" in the Shopify Enriched Listing list view: tick any number of
// listings and approve them in one go. Each approval runs server-side through a
// normal document save, so the same on_update hook that serves a one-at-a-time
// approval pushes every listing to its Shopify Product Listing
// (api.approve_listings).

frappe.listview_settings["Shopify Enriched Listing"] = {
	onload(listview) {
		listview.page.add_actions_menu_item(__("Approve"), () => approve_selected(listview), false);
	},
};

// This list view has no store in scope the way a Listing form does, and
// predates multi-store, so approve_listings took no connection at all. Same
// convention as public/js/shopify_product_listing_list.js's
// with_shopify_connection: ask list_connections, skip the prompt on a
// single-store bench, and cache the answer for the life of the page. Kept
// local rather than shared -- that file's helper isn't loaded on this list
// view's page bundle.
let shopify_enriched_listing_connection = null;

function with_shopify_connection(callback) {
	if (shopify_enriched_listing_connection) {
		callback(shopify_enriched_listing_connection);
		return;
	}
	frappe.call({
		method: "alaiy_os_connector_shopify.api.sync.list_connections",
		callback: function (r) {
			const message = r.message || {};
			const rows = message.connections || [];
			if (message.selected) {
				shopify_enriched_listing_connection = message.selected;
				callback(shopify_enriched_listing_connection);
				return;
			}
			if (!rows.length) {
				frappe.msgprint(__("No Shopify store is switched on for you on this site."));
				return;
			}
			frappe.prompt(
				[{
					fieldtype: "Select",
					fieldname: "connection",
					label: __("Shopify Store"),
					reqd: 1,
					options: rows.map((c) => ({
						label: c.label + (c.shop_url ? " (" + c.shop_url + ")" : ""),
						value: c.name,
					})),
					default: rows[0].name,
				}],
				(values) => {
					shopify_enriched_listing_connection = values.connection;
					callback(shopify_enriched_listing_connection);
				},
				__("Which store?"),
				__("Continue")
			);
		},
	});
}

function approve_selected(listview) {
	const names = listview.get_checked_items(true);
	if (!names.length) {
		frappe.msgprint({
			title: __("Nothing selected"),
			message: __("Tick the listings you want to approve, then choose Approve again."),
			indicator: "orange",
		});
		return;
	}

	frappe.confirm(
		__(
			"Approve {0} listing(s)? Each one is pushed to its Shopify Product Listing immediately.",
			[names.length]
		),
		() => {
			with_shopify_connection((connection) => frappe.call({
				method: "alaiy_os_connector_shopify.listing.review.approve_listings",
				args: { names: names, connection: connection },
				freeze: true,
				freeze_message: __("Approving…"),
				callback: (r) => {
					const res = r.message || {};
					const parts = [__("{0} approved", [res.approved || 0])];
					if (res.skipped) parts.push(__("{0} already approved", [res.skipped]));
					if (res.failed) parts.push(__("{0} failed", [res.failed]));

					frappe.show_alert({
						message: parts.join(", "),
						indicator: res.failed ? "orange" : "green",
					});

					// A failure names its listing so the admin can open it, fix, and
					// re-approve — the successes have already gone through.
					if (res.failed) {
						const rows = Object.entries(res.errors)
							.map(([name, err]) => `<li><b>${frappe.utils.escape_html(name)}</b>: ${frappe.utils.escape_html(err)}</li>`)
							.join("");
						frappe.msgprint({
							title: __("Some approvals failed"),
							message: `<ul>${rows}</ul>`,
							indicator: "orange",
						});
					}
					listview.refresh();
				},
			}));
		}
	);
}
