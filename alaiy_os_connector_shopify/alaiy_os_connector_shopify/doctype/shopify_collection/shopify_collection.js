frappe.ui.form.on("Shopify Collection", {
	refresh(frm) {
		const productsField = frm.get_field("members_html");
		const channelsField = frm.get_field("channels_html");
		// Fields only exist after migrate -- guard so a not-yet-migrated site
		// doesn't throw and abort the whole form script.
		if (!productsField) {
			return;
		}
		const wrapper = productsField.$wrapper;
		const chWrap = channelsField ? channelsField.$wrapper : null;

		if (frm.is_new()) {
			wrapper.html('<p class="text-muted">Save first.</p>');
			return;
		}

		function load_channels() {
			if (!chWrap) return;
			chWrap.html('<p class="text-muted">Loading channels...</p>');
			frappe.call({
				method: "alaiy_os_connector_shopify.shopify.product.collections.get_collection_channels",
				args: { collection_name: frm.doc.name },
				callback(r) {
					const chans = r.message || [];
					if (!chans.length) {
						chWrap.html('<p class="text-muted">No sales channels.</p>');
						return;
					}
					chWrap.empty();
					const note = $('<div style="font-size:11px;color:var(--text-muted);margin-bottom:4px;">Click a channel to publish / unpublish</div>');
					chWrap.append(note);
					chans.forEach((c) => {
						const on = c.published;
						const color = on ? "var(--green-500,#28a745)" : "var(--text-muted)";
						const bg = on ? "var(--green-50,#eaf7ee)" : "var(--control-bg)";
						const dot = on ? "●" : "○";
						const chip = $('<span></span>')
							.css({
								display: "inline-block", margin: "2px 4px", padding: "3px 10px",
								"border-radius": "12px", "font-size": "12px", cursor: "pointer",
								border: "1px solid " + color, color: color, background: bg,
							})
							.text(dot + " " + (c.name || ""));
						chip.on("click", () => {
							if (!c.publication_id) return;
							chip.css("opacity", 0.5).text("… " + (c.name || ""));
							frappe.call({
								method: "alaiy_os_connector_shopify.shopify.product.collections.toggle_collection_channel",
								args: {
									collection_name: frm.doc.name,
									publication_id: c.publication_id,
									publish: on ? 0 : 1,
								},
								callback(res) {
									const m = res.message || {};
									if (m.ok) {
										frappe.show_alert({
											message: (on ? "Unpublished from " : "Published to ") + c.name,
											indicator: "green",
										}, 4);
									} else {
										frappe.show_alert({ message: "Failed: " + (m.error || ""), indicator: "red" }, 6);
									}
									load_channels();
								},
							});
						});
						chWrap.append(chip);
					});
				},
			});
		}
		load_channels();

		wrapper.html('<p class="text-muted">Loading products from Shopify...</p>');
		frappe.call({
			method: "alaiy_os_connector_shopify.shopify.product.collections.get_collection_products",
			args: { collection_name: frm.doc.name },
			callback(r) {
				const items = r.message || [];
				if (!items.length) {
					wrapper.html('<p class="text-muted">No products in this collection on Shopify.</p>');
					return;
				}

				const cards = items.map((p) => {
					const img = p.image
						? '<img src="' + p.image + '" style="width:100%;height:120px;object-fit:cover;border-radius:6px 6px 0 0;">'
						: '<div style="width:100%;height:120px;background:var(--control-bg);border-radius:6px 6px 0 0;"></div>';
					const title = frappe.utils.escape_html(p.title || "");
					const sku = p.sku ? " · " + frappe.utils.escape_html(p.sku) : "";
					const price = p.price ? "₹" + p.price : "";
					const inner =
						img +
						'<div style="padding:6px 8px;">' +
						'<div style="font-size:12px;font-weight:600;line-height:1.3;">' + title + sku + "</div>" +
						'<div style="font-size:12px;color:var(--text-muted);">' + price + "</div>" +
						"</div>";
					if (p.item_code) {
						return '<a href="/app/item/' + encodeURIComponent(p.item_code) +
							'" style="text-decoration:none;color:inherit;border:1px solid var(--border-color);border-radius:6px;overflow:hidden;">' +
							inner + "</a>";
					}
					return '<div style="border:1px solid var(--border-color);border-radius:6px;overflow:hidden;">' + inner + "</div>";
				}).join("");

				wrapper.html(
					'<div style="font-weight:600;margin-bottom:8px;">' + items.length + " products</div>" +
					'<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px;">' +
					cards + "</div>"
				);
			},
		});
	},
});
