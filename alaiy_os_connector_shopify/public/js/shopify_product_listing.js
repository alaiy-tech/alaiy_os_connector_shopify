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
        add_populate_button(frm);
    },

    item(frm) {
        // Re-render the button the moment a template is picked on a new doc
        // (refresh doesn't re-fire on field change).
        add_populate_button(frm);
    },
});

function add_populate_button(frm) {
    if (!frm.doc.item) {
        return;
    }
    if (frm.custom_buttons[__("Populate from Item")]) {
        return; // already added -- don't duplicate
    }
    // Pull the Item's images + variants into the grids, visible before save.
    // Auto-fill on insert is the safety net; this is the explicit path.
    frm.add_custom_button(__("Populate from Item"), () => {
        frappe.call({
            method: "alaiy_os_connector_shopify.shopify.product.listing.get_item_children",
            args: { item: frm.doc.item },
            callback(r) {
                if (!r.message) {
                    return;
                }
                // Never clear -- merge only. The Listing's own images can
                // hold more than the Item ever knows about (upload.py
                // populates the Listing directly with every parent image
                // URL, not just the one the Item itself stores), so
                // rebuilding this table from the Item's more limited view
                // was silently dropping real images that only ever lived
                // here. Same reasoning already applied to variants below.
                (r.message.images || []).forEach((row) => {
                    const exists = (frm.doc.images || []).some(
                        (x) => x.image && row.image && x.image.trim() === row.image.trim()
                    );
                    if (!exists) {
                        frm.add_child("images", row);
                    }
                });
                (r.message.variants || []).forEach((row) => {
                    const existing_row = (frm.doc.variants || []).find(
                        (x) => x.item_variant && row.item_variant && x.item_variant.trim() === row.item_variant.trim()
                    );
                    if (!existing_row) {
                        frm.add_child("variants", row);
                    } else if (!existing_row.variant_image && row.variant_image) {
                        // Fill in a missing variant image without touching
                        // an existing one -- same never-remove, never-
                        // clobber principle as the rest of this button.
                        frappe.model.set_value(existing_row.doctype, existing_row.name, "variant_image", row.variant_image);
                    }
                });
                if (r.message.listing_category) {
                    frm.set_value("listing_category", r.message.listing_category);
                }
                if (r.message.listing_product_type) {
                    frm.set_value("listing_product_type", r.message.listing_product_type);
                }
                frm.refresh_field("images");
                frm.refresh_field("variants");
                frappe.show_alert({ message: __("Pulled from Item"), indicator: "green" });
            },
        });
    });
}
