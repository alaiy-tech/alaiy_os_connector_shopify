// Only let the Item picker offer template / simple Items (never variants) --
// a Listing is keyed to the template; picking a variant fails on save.
// Plain filter (not a server query) so it can't silently fall back to the
// unfiltered default. "Already has a listing" is enforced by the unique
// constraint on save.
frappe.ui.form.on("Shopify Product Listing", {
    setup(frm) {
        frm.set_query("item", () => ({
            filters: { variant_of: ["in", ["", null]] },
        }));
    },
});
