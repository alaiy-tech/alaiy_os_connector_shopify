"use client";

import { PageHeader } from "@alaiy-os/layout/page-header";

import { Badge } from "@alaiy-os/ui/badge";

import { fetchResourceList } from "@/lib/frappe/shopify-sync";

import { SimpleResourceTable } from "../_components/simple-resource-table";

interface RetryQueueEntry extends Record<string, unknown> {
  name: string;
  direction: "inbound" | "outbound";
  entity_type: string;
  synced_entity: string | null;
  status: "pending" | "in_progress" | "dead_letter" | "completed";
  attempt_count: number;
  next_attempt_at: string | null;
  last_error: string | null;
}

interface SyncedEntity extends Record<string, unknown> {
  name: string;
  entity_type: string;
  external_id: string | null;
  erpnext_doctype: string | null;
  erpnext_name: string | null;
  last_synced_at: string | null;
}

const STATUS_VARIANT: Record<RetryQueueEntry["status"], "default" | "secondary" | "destructive" | "outline"> = {
  pending: "secondary",
  in_progress: "default",
  dead_letter: "destructive",
  completed: "outline",
};

export default function Page() {
  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Shopify Retry Queue"
        subtitle="Sync operations that failed and are waiting to retry, plus the local-to-Shopify ID mapping ledger."
      />
      <SimpleResourceTable<RetryQueueEntry>
        load={() =>
          fetchResourceList<RetryQueueEntry>(
            "Shopify Retry Queue Entry",
            ["name", "direction", "entity_type", "synced_entity", "status", "attempt_count", "next_attempt_at", "last_error"],
            { orderBy: "modified desc" },
          )
        }
        rowKey={(row) => row.name}
        emptyMessage="No retry queue entries."
        columns={[
          { header: "Direction", render: (row) => <Badge variant="outline">{row.direction}</Badge> },
          { header: "Entity type", render: (row) => row.entity_type },
          { header: "Status", render: (row) => <Badge variant={STATUS_VARIANT[row.status]}>{row.status}</Badge> },
          { header: "Attempts", align: "right", render: (row) => row.attempt_count },
          {
            header: "Next attempt",
            render: (row) =>
              row.next_attempt_at ? new Date(row.next_attempt_at).toLocaleString() : <span className="text-muted-foreground">—</span>,
          },
          {
            header: "Last error",
            render: (row) =>
              row.last_error ? <span className="text-destructive">{row.last_error}</span> : <span className="text-muted-foreground">—</span>,
          },
        ]}
      />

      <PageHeader title="Synced Entity Ledger" subtitle="ID mapping between local Alaiy OS documents and their Shopify counterparts." />
      <SimpleResourceTable<SyncedEntity>
        load={() =>
          fetchResourceList<SyncedEntity>(
            "Shopify Synced Entity",
            ["name", "entity_type", "external_id", "erpnext_doctype", "erpnext_name", "last_synced_at"],
            { orderBy: "modified desc" },
          )
        }
        rowKey={(row) => row.name}
        emptyMessage="No synced entities yet."
        columns={[
          { header: "Entity type", render: (row) => row.entity_type },
          { header: "Shopify ID", render: (row) => <span className="text-muted-foreground">{row.external_id ?? "—"}</span> },
          { header: "Alaiy OS DocType", render: (row) => row.erpnext_doctype ?? "—" },
          { header: "Alaiy OS Document", render: (row) => row.erpnext_name ?? "—" },
          {
            header: "Last synced",
            render: (row) =>
              row.last_synced_at ? new Date(row.last_synced_at).toLocaleString() : <span className="text-muted-foreground">—</span>,
          },
        ]}
      />
    </div>
  );
}
