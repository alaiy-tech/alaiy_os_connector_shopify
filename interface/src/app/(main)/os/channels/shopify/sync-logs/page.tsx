"use client";

import { useState } from "react";

import { PageHeader } from "@alaiy-os/layout/page-header";
import { Badge } from "@alaiy-os/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@alaiy-os/ui/select";
import { cn } from "@alaiy-os/utils";

import { getSyncStatusBadgeClass } from "@/constants/shopify";
import { fetchResourceList } from "@/lib/frappe/shopify-sync";

import { useShopifyStore } from "../_lib/use-shopify-store";
import { StoreSwitcher } from "../_components/store-switcher";
import { SimpleResourceTable } from "../_components/simple-resource-table";
import { SyncLogDetailDialog } from "./_components/sync-log-detail-dialog";

export interface SyncLogFullRow extends Record<string, unknown> {
  name: string;
  sync_type: string;
  trigger: string;
  status: string;
  started_at: string | null;
  finished_at: string | null;
  items_processed: number;
  items_created: number;
  items_failed: number;
  pages_total: number;
  pages_done: number;
  error_message: string | null;
  log_messages: string | null;
}

const SYNC_TYPE_OPTIONS = [
  "orders", "inventory", "inventory_pull", "products", "product_export",
  "listing_bulk_enable", "update_listings", "collections", "locations",
  "webhook", "taxonomy",
];
const STATUS_OPTIONS = ["queued", "running", "success", "failed", "skipped", "cancelled"];

export default function Page() {
  const { selected } = useShopifyStore();
  const [syncType, setSyncType] = useState<string>("");
  const [status, setStatus] = useState<string>("");
  const [detail, setDetail] = useState<SyncLogFullRow | null>(null);

  const filters: Array<[string, string, unknown]> = [];
  if (selected) filters.push(["connection", "=", selected]);
  if (syncType) filters.push(["sync_type", "=", syncType]);
  if (status) filters.push(["status", "=", status]);

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <PageHeader title="Shopify Sync Logs" subtitle="Full history of every sync run, filterable by type and status." />
        <StoreSwitcher />
      </div>

      <div className="flex flex-wrap gap-2">
        <Select value={syncType || "all"} onValueChange={(v) => setSyncType(v === "all" ? "" : v)}>
          <SelectTrigger size="sm" className="w-44">
            <SelectValue placeholder="All types" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All types</SelectItem>
            {SYNC_TYPE_OPTIONS.map((t) => (
              <SelectItem key={t} value={t}>
                {t}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={status || "all"} onValueChange={(v) => setStatus(v === "all" ? "" : v)}>
          <SelectTrigger size="sm" className="w-40">
            <SelectValue placeholder="All statuses" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All statuses</SelectItem>
            {STATUS_OPTIONS.map((s) => (
              <SelectItem key={s} value={s}>
                {s}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <SimpleResourceTable<SyncLogFullRow>
        key={`${selected}-${syncType}-${status}`}
        load={() =>
          fetchResourceList<SyncLogFullRow>(
            "Shopify Sync Log",
            [
              "name", "sync_type", "trigger", "status", "started_at", "finished_at",
              "items_processed", "items_created", "items_failed", "pages_total", "pages_done",
              "error_message", "log_messages",
            ],
            { orderBy: "started_at desc", filters },
          )
        }
        rowKey={(row) => row.name}
        emptyMessage="No sync runs match this filter."
        columns={[
          {
            header: "Type",
            render: (row) => (
              <button type="button" className="capitalize hover:underline" onClick={() => setDetail(row)}>
                {row.sync_type}
              </button>
            ),
          },
          { header: "Trigger", render: (row) => <span className="text-muted-foreground capitalize">{row.trigger}</span> },
          {
            header: "Status",
            render: (row) => (
              <Badge variant="outline" className={cn("border-0 font-medium", getSyncStatusBadgeClass(row.status))}>
                {row.status}
              </Badge>
            ),
          },
          { header: "Started", render: (row) => (row.started_at ? new Date(row.started_at).toLocaleString() : "—") },
          { header: "Processed", align: "right", render: (row) => row.items_processed },
          { header: "Created", align: "right", render: (row) => row.items_created },
          { header: "Failed", align: "right", render: (row) => row.items_failed },
        ]}
      />

      {detail && <SyncLogDetailDialog log={detail} open={!!detail} onOpenChange={(next) => !next && setDetail(null)} />}
    </div>
  );
}
