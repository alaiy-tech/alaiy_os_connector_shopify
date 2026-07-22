// Only let the Item picker offer template/simple Items that don't already
// have a Listing -- variants and already-listed products would fail on save
// (one listing per template Item).
frappe.ui.form.on("Shopify Product Listing", {
    setup(frm) {
        frm.set_query("item", () => ({
            query: "alaiy_os_connector_shopify.shopify.product.listing.item_without_listing_query",
        }));
    },
});
