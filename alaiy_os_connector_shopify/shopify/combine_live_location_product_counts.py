"""
Combines the per-slice CSVs from scan_live_location_product_counts.py
into one Excel workbook, mapped from Shopify location -> supplier
(Shopify Location.linked_supplier), and compares against our local
per-supplier product counts (same ownership logic used everywhere
else in this app) side by side.

  bench --site <site> execute \
      alaiy_os_connector_shopify.shopify.combine_live_location_product_counts.run
"""

import csv
import glob
import shutil

import frappe


def run():
    import openpyxl
    from openpyxl.styles import Font, PatternFill

    from alaiy_os_connector_shopify.shopify.scan_supplier_totals import _local_product_counts_by_supplier

    site_files_dir = frappe.utils.get_site_path("private/files")
    csv_paths = sorted(glob.glob(f"{site_files_dir}/live_location_product_counts*.csv"))
    if not csv_paths:
        print("No live_location_product_counts*.csv files found -- run scan_live_location_product_counts.py first.")
        return

    print(f"Combining {len(csv_paths)} file(s): {[p.split('/')[-1] for p in csv_paths]}")

    location_rows = []
    for path in csv_paths:
        with open(path, newline="", encoding="utf-8") as f:
            location_rows.extend(csv.DictReader(f))

    gid_to_supplier = {
        r.sh_location_gid: r.linked_supplier
        for r in frappe.get_all(
            "Shopify Location", filters={"linked_supplier": ["!=", ""]},
            fields=["sh_location_gid", "linked_supplier"],
        )
        if r.sh_location_gid
    }

    local_counts = _local_product_counts_by_supplier()

    supplier_shopify_counts = {}
    unmapped_locations = []
    for row in location_rows:
        supplier = gid_to_supplier.get(row["location_gid"])
        count = int(row["product_count"] or 0)
        if supplier:
            supplier_shopify_counts[supplier] = supplier_shopify_counts.get(supplier, 0) + count
        else:
            unmapped_locations.append(row)

    all_suppliers = sorted(set(local_counts) | set(supplier_shopify_counts))

    wb = openpyxl.Workbook()
    red_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
    header_font = Font(bold=True)

    ws1 = wb.active
    ws1.title = "Summary"
    ws1.append(["Supplier", "Local Products", "Shopify Products (real stock)", "Mismatch"])
    for supplier in all_suppliers:
        local = local_counts.get(supplier, 0)
        shopify = supplier_shopify_counts.get(supplier, 0)
        mismatch = local != shopify
        r_idx = ws1.max_row + 1
        ws1.append([supplier, local, shopify, mismatch])
        if mismatch:
            for col in range(1, 5):
                ws1.cell(row=r_idx, column=col).fill = red_fill

    ws2 = wb.create_sheet("By Location")
    ws2.append(["Location GID", "Location Name", "Product Count", "Linked Supplier"])
    for row in sorted(location_rows, key=lambda r: -int(r["product_count"] or 0)):
        ws2.append([row["location_gid"], row["location_name"], row["product_count"],
                    gid_to_supplier.get(row["location_gid"], "")])

    if unmapped_locations:
        ws3 = wb.create_sheet("Unmapped Locations")
        ws3.append(["Location GID", "Location Name", "Product Count"])
        for row in unmapped_locations:
            ws3.append([row["location_gid"], row["location_name"], row["product_count"]])

    for ws in wb.worksheets:
        for cell in ws[1]:
            cell.font = header_font
        for col_cells in ws.columns:
            length = max((len(str(c.value)) if c.value is not None else 0) for c in col_cells)
            ws.column_dimensions[col_cells[0].column_letter].width = min(length + 2, 50)

    filename = "live_location_product_counts_combined.xlsx"
    private_path = frappe.utils.get_site_path(f"private/files/{filename}")
    wb.save(private_path)
    public_path = frappe.utils.get_site_path(f"public/files/{filename}")
    shutil.copy(private_path, public_path)

    print(f"\nWrote {len(all_suppliers)} supplier row(s), "
          f"{sum(1 for s in all_suppliers if local_counts.get(s, 0) != supplier_shopify_counts.get(s, 0))} mismatch(es), "
          f"{len(unmapped_locations)} unmapped location(s) to {private_path}")
    print(f"Downloadable at /files/{filename}")

    return {"suppliers": len(all_suppliers), "unmapped_locations": len(unmapped_locations)}
