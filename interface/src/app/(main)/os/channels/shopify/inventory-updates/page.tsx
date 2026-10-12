"use client";

import Link from "next/link";

import { PageHeader } from "@alaiy-os/layout/page-header";
import { Badge } from "@alaiy-os/ui/badge";

import { getSyncStatusBadgeClass } from "@/constants/shopify";
import { fetchResourceList } from "@/lib/frappe/shopify-sync";

import { useShopifyStore } from "../_lib/use-shopify-store";
import { StoreSwitcher } from "../_components/store-switcher";
import { SimpleResourceTable } from "../_components/simple-resource-table";

interface InventoryUpdateRow extends Record<string, unknown> {
  name: string;
  item_code: string;
  warehouse: string;
  shopify_qty: number;
  status: "Pending" | "Applied" | "Skipped" | "Failed";
  stock_reconciliation: string | null;
  error: string | null;
}

const STATUS_TONE: Record<string, string> = {
  Applied: "success",
  Failed: "failed",
  Pending: "queued",
  Skipped: "skipped",
};

export default function Page() {
  const { selected } = useShopifyStore();

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <PageHeader
          title="Shopify Inventory Updates"
          subtitle="Per-item stock corrections pulled from Shopify, and which Stock Reconciliation applied each one."
        />
        <StoreSwitcher />
      </div>
      <SimpleResourceTable<InventoryUpdateRow>
        key={selected}
        load={() =>
          fetchResourceList<InventoryUpdateRow>(
            "Shopify Inventory Update",
            ["name", "item_code", "warehouse", "shopify_qty", "status", "stock_reconciliation", "error"],
            { orderBy: "modified desc", filters: selected ? [["connection", "=", selected]] : [] },
          )
        }
        rowKey={(row) => row.name}
        emptyMessage="No inventory updates recorded yet."
        columns={[
          { header: "Item", render: (row) => row.item_code },
          { header: "Warehouse", render: (row) => row.warehouse },
          { header: "Shopify Qty", align: "right", render: (row) => row.shopify_qty },
          {
            header: "Status",
            render: (row) => (
              <Badge variant="outline" className={`border-0 font-medium ${getSyncStatusBadgeClass(STATUS_TONE[row.status] ?? "Queued")}`}>
                {row.status}
              </Badge>
            ),
          },
          {
            header: "Applied via",
            render: (row) =>
              row.stock_reconciliation ? (
                <Link
                  href={`/os/open/stock-reconciliation/${encodeURIComponent(row.stock_reconciliation)}`}
                  className="hover:underline"
                >
                  {row.stock_reconciliation}
                </Link>
              ) : (
                <span className="text-muted-foreground">—</span>
              ),
          },
          {
            header: "Error",
            render: (row) => (row.error ? <span className="text-destructive text-xs">{row.error}</span> : <span className="text-muted-foreground">—</span>),
          },
        ]}
      />
    </div>
  );
}
