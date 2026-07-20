frappe.ui.form.on("Shopify Collection", {
	refresh(frm) {
		const wrapper = frm.get_field("members_html").$wrapper;
		wrapper.html('<p class="text-muted">Loading linked products...</p>');

		if (frm.is_new()) {
			wrapper.html('<p class="text-muted">Save first.</p>');
			return;
		}

		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Item Shopify Collection",
				filters: { shopify_collection: frm.doc.name },
				fields: ["parent"],
				parent: "Item",
				limit_page_length: 0,
			},
			callback(r) {
				const rows = (r.message || []).filter((x) => x.parent);
				if (!rows.length) {
					let msg = "No ERPNext products link this collection yet.";
					if (frm.doc.is_smart) {
						msg += " Smart collection -- membership is driven by Shopify rules; import products to populate.";
					}
					wrapper.html('<p class="text-muted">' + msg + "</p>");
					return;
				}
				let html = '<div><b>' + rows.length + " linked product(s):</b><ul>";
				rows.forEach((x) => {
					const url = "/app/item/" + encodeURIComponent(x.parent);
					html += '<li><a href="' + url + '">' + frappe.utils.escape_html(x.parent) + "</a></li>";
				});
				html += "</ul></div>";
				wrapper.html(html);
			},
		});
	},
});
