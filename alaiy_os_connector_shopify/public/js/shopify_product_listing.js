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
        show_effective_values(frm);
    },
});

// The "Populate from Item" button used to live here. Images, variants,
// category and product type are now filled server-side on every save
// (Shopify Product Listing.validate -> fill_children_from_item), so a
// Listing tracks its Item on its own and there is nothing left for the
// button to do that saving does not already do.
//
// It was never only a convenience: fill was before_insert-only, so a
// Listing created before its Item gained a variant would never pick that
// variant up, and pressing the button was the sole way to fix it. A
// variant missing from a Listing never reaches Shopify, which made
// keeping the catalogue correct depend on someone remembering to press
// something. Doing it on save removes that dependency.


// A blank override field reads as "nothing will be sent" when it actually means
// "inherited from the Item". Show the resolved value under each field instead of
// writing it in: filling the field would freeze the value and stop it tracking a
// later change to the Item's own title or description.
function show_effective_values(frm) {
    if (frm.is_new() || !frm.doc.item) {
        return;
    }
    frappe.call({
        method: "alaiy_os_connector_shopify.shopify.product.listing.effective_values",
        args: { listing_name: frm.doc.name },
        callback(r) {
            const eff = r.message;
            if (!eff) {
                return;
            }
            const pairs = [
                ["listing_title", eff.title],
                ["listing_description", eff.description],
                ["listing_product_type", eff.product_type],
                ["listing_category", eff.category],
                ["listing_seo_title", eff.seo_title],
                ["listing_seo_description", eff.seo_description],
            ];
            pairs.forEach(([fieldname, value]) => {
                const field = frm.get_field(fieldname);
                if (!field || !value) {
                    return;
                }
                const inherited = !frm.doc[fieldname];
                const shown = frappe.utils.escape_html(String(value)).slice(0, 300);
                field.set_new_description(
                    inherited
                        ? `<b>Inherited, this is what will be sent:</b> ${shown}`
                        : `<b>Overridden.</b> Clear the field to inherit instead.`
                );
            });
            frm.dashboard.clear_headline();
            frm.dashboard.set_headline(
                `Push would send ${eff.image_count} image(s).`
            );
        },
    });
}
