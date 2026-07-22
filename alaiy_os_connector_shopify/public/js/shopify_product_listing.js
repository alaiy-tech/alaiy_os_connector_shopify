frappe.ui.form.on("Shopify Product Listing", {
    setup(frm) {
        // Item picker: template / simple Items only (never variants) -- a
        // Listing is keyed to the template; a variant fails on save.
        frm.set_query("item", () => ({
            filters: { variant_of: ["in", ["", null]] },
        }));
        // Variant-row picker: only this template's own variants. If the
        // product is simple (no variants), this list is empty -- which is
        // correct, a simple product needs no variant rows (it pushes as its
        // own single variant).
        frm.set_query("item_variant", "variants", () => ({
            filters: { variant_of: frm.doc.item || "__no_item__" },
        }));
    },

    refresh(frm) {
        if (!frm.doc.item) {
            return;
        }
        // Pull the Item's images + variants into the grids, visible before
        // save. Auto-fill on insert is the safety net; this is the explicit,
        // visible path. Skips rows already present.
        frm.add_custom_button(__("Populate from Item"), () => {
            frappe.call({
                method: "alaiy_os_connector_shopify.shopify.product.listing.get_item_children",
                args: { item: frm.doc.item },
                callback(r) {
                    if (!r.message) {
                        return;
                    }
                    (r.message.images || []).forEach((row) => {
                        if (!(frm.doc.images || []).some((x) => x.image === row.image)) {
                            frm.add_child("images", row);
                        }
                    });
                    (r.message.variants || []).forEach((row) => {
                        if (!(frm.doc.variants || []).some((x) => x.item_variant === row.item_variant)) {
                            frm.add_child("variants", row);
                        }
                    });
                    frm.refresh_field("images");
                    frm.refresh_field("variants");
                    frappe.show_alert({ message: __("Pulled from Item"), indicator: "green" });
                },
            });
        });
    },
});
