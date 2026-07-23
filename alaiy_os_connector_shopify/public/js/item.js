// Placeholder entry point (issue #62): from a template Item, open its
// Shopify Product Listing or create one. Full listings UI is deferred --
// this is just a route/link so the record is reachable from the desk.
frappe.ui.form.on("Item", {
    refresh(frm) {
        if (frm.is_new() || frm.doc.variant_of) {
            return; // listings are keyed to templates / simple items only
        }
        frm.add_custom_button(
            __("Shopify Listing"),
            () => {
                frappe.db.exists("Shopify Product Listing", frm.doc.name).then((exists) => {
                    if (exists) {
                        frappe.set_route("Form", "Shopify Product Listing", frm.doc.name);
                    } else {
                        frappe.new_doc("Shopify Product Listing", { item: frm.doc.name });
                    }
                });
            },
            __("Shopify")
        );
    },
});
