"""
Item doc_event hooks (validate/on_update/after_insert/on_trash) and the
sync-enabled gate -- moved verbatim from product_sync.py, unchanged.
"""

import frappe


def validate_item_uoms(doc, method=None):
    """
    Validation hook on Item before saving to automatically deduplicate
    the UOM conversion factors for both template and variant Items.
    This prevents standard Alaiy OS validation errors from blocking
    Desk UI saves and webhook runs.
    """
    # 1. Clean up the document's own in-memory UOMs list first
    seen_uoms = set()
    deduped = []
    has_duplicates = False
    for row in doc.get("uoms") or []:
        if row.uom in seen_uoms:
            has_duplicates = True
            continue
        seen_uoms.add(row.uom)
        deduped.append(row)

    if has_duplicates:
        doc.set("uoms", deduped)

    # 2. Database level cleanup for the current Item and all variants
    all_item_names = [doc.name]
    if doc.has_variants:
        all_item_names += frappe.get_all("Item", filters={"variant_of": doc.name}, pluck="name")
    elif doc.variant_of:
        # If it's a variant, also clean the template and other sibling variants
        all_item_names.append(doc.variant_of)
        all_item_names += frappe.get_all("Item", filters={"variant_of": doc.variant_of}, pluck="name")
        all_item_names = list(set(all_item_names))

    for name in all_item_names:
        duplicates = frappe.db.sql("""
            SELECT uom, MIN(name) as keep_name
            FROM `tabUOM Conversion Detail`
            WHERE parent = %s
            GROUP BY uom
            HAVING COUNT(*) > 1
        """, name, as_dict=True)

        for dup in duplicates:
            frappe.db.sql("""
                DELETE FROM `tabUOM Conversion Detail`
                WHERE parent = %s AND uom = %s AND name != %s
            """, (name, dup.uom, dup.keep_name))


def on_item_change(doc, method=None):
    if doc.flags.from_shopify_sync:
        # This save originated from an inbound webhook update (see
        # _update_item_from_shopify) -- pushing it back to Shopify would
        # create an infinite create/update ping-pong between the two sides.
        return

    template_name = doc.variant_of or doc.name
    template_enabled = bool(
        frappe.db.get_value("Item", template_name, "sync_to_shopify")
    ) and not frappe.db.get_value("Item", template_name, "disabled")
    has_shopify_id = bool(
        frappe.db.get_value("Item", template_name, "sh_shopify_product_id")
    )

    if doc.variant_of:
        # A brand-new variant added under an already-syncing product must
        # flow to Shopify without someone remembering to tick its own
        # checkbox -- otherwise _variants_of's filter would silently leave
        # it out of every future push (this exact regression, confirmed by
        # walking the flow: "add variant in Alaiy OS -> appears on Shopify"
        # worked before the per-variant filter existed).
        current_sync = doc.get("sync_to_shopify")
        frappe.logger().info(
            f"Shopify variant check: variant={doc.name}, template={template_name}, "
            f"template_enabled={template_enabled}, method={method}, current_sync={current_sync}"
        )
        if method == "after_insert" and template_enabled and not current_sync:
            doc.sync_to_shopify = 1
            frappe.db.set_value("Item", doc.name, "sync_to_shopify", 1)
            frappe.logger().info(f"Shopify auto-checked variant {doc.name}")

        # The template is the master switch: a variant's own checkbox only
        # controls whether THAT variant is included the next time the
        # template pushes (see _variants_of's own sync_to_shopify filter),
        # never whether the product as a whole is syncing. So re-push
        # whenever the template is enabled, regardless of which way this
        # variant's own flag just moved -- unchecking it here is exactly
        # what should make the rebuilt variant set drop it from Shopify.
        if template_enabled:
            frappe.enqueue(
                "alaiy_os_connector_shopify.shopify.product_sync.push_item",
                queue="short",
                timeout=120,
                item_code=template_name,
            )
        return

    # doc is the template itself
    if template_enabled:
        # The template's own checkbox just turned on (not just re-saved
        # while already on) -- auto-check every variant that isn't already
        # explicitly on, so a fresh product syncs all its variants by
        # default instead of requiring each one ticked by hand. Only
        # fires on the actual on-transition so it never re-checks a
        # variant someone deliberately unchecked afterward.
        sync_changed = doc.has_value_changed("sync_to_shopify")
        disabled_changed = doc.has_value_changed("disabled")

        # Self-healing: if the template is enabled but 100% of its variants are unchecked,
        # we must auto-check them to prevent the sync from skipping/stucking.
        all_variants_unchecked = False
        if doc.has_variants:
            all_variants_unchecked = not frappe.db.exists(
                "Item",
                {"variant_of": doc.name, "sync_to_shopify": 1}
            )

        frappe.logger().info(
            f"Shopify auto-check: template={doc.name}, sync_changed={sync_changed}, "
            f"disabled_changed={disabled_changed}, all_variants_unchecked={all_variants_unchecked}, method={method}"
        )
        if sync_changed or disabled_changed or all_variants_unchecked:
            variant_names = frappe.get_all(
                "Item",
                filters={"variant_of": doc.name, "sync_to_shopify": 0},
                pluck="name",
            )
            frappe.logger().info(
                f"Shopify auto-check: found {len(variant_names)} unchecked variants to auto-check"
            )
            for variant_name in variant_names:
                frappe.db.set_value("Item", variant_name, "sync_to_shopify", 1)
            if variant_names:
                frappe.db.commit()

        frappe.enqueue(
            "alaiy_os_connector_shopify.shopify.product_sync.push_item",
            queue="short",
            timeout=120,
            item_code=doc.name,
        )
    elif has_shopify_id:
        # Either sync_to_shopify turned off, or the item itself got
        # disabled -- both mean "this product should not be live on
        # Shopify anymore."
        frappe.enqueue(
            "alaiy_os_connector_shopify.shopify.product_sync.archive_item",
            queue="short",
            timeout=60,
            item_code=doc.name,
        )


def on_item_delete(doc, method=None):
    """
    Deleting a variant in Alaiy OS should remove it from Shopify too,
    rather than silently diverging. push_item always rebuilds the FULL
    variant list from the template's current children before calling
    productSet, which Shopify treats as the complete desired state -- so
    simply re-pushing the template right after this variant is gone
    naturally drops it from Shopify as well, with no separate delete
    mutation needed.

    Scoped to variant deletions only. Deleting the template itself (the
    whole product) is a bigger, more destructive call -- not handled
    here.
    """
    if not doc.variant_of:
        return
    if not doc.get("sh_shopify_variant_id"):
        return  # Never synced to Shopify -- nothing to remove there
    template_name = doc.variant_of
    if not frappe.db.get_value("Item", template_name, "sync_to_shopify"):
        return  # Outbound push disabled for this product -- leave Shopify alone

    frappe.enqueue(
        "alaiy_os_connector_shopify.shopify.product_sync.push_item",
        queue="short",
        timeout=120,
        item_code=template_name,
    )


def on_item_price_change(doc, method=None):
    settings = frappe.get_single("Shopify Connector Settings")
    if doc.price_list != (settings.sh_selling_price_list or "Standard Selling"):
        return
    if not frappe.db.exists("Item", doc.item_code):
        return
    item = frappe.get_doc("Item", doc.item_code)
    if not _sync_enabled(item):
        return
    frappe.enqueue(
        "alaiy_os_connector_shopify.shopify.product_sync.push_item",
        queue="short",
        timeout=120,
        item_code=doc.item_code,
    )


# ── Sync-enable gate ─────────────────────────────────────────────────────────

def _sync_enabled(item) -> bool:
    """
    Whether this product as a whole should be live on Shopify: the
    template's own sync_to_shopify checkbox AND not disabled. Deliberately
    does NOT stay true forever just because it already has a Shopify ID --
    unchecking (or disabling) is meant to archive it, not be ignored. A
    variant's own checkbox never factors in here -- it only controls
    whether that one variant is included in the rebuilt set once the
    template itself is enabled (see _variants_of, on_item_change).
    """
    if item.get("variant_of"):
        template_name = item.variant_of
        return bool(frappe.db.get_value("Item", template_name, "sync_to_shopify")) \
            and not frappe.db.get_value("Item", template_name, "disabled")
    return bool(item.get("sync_to_shopify")) and not item.get("disabled")
