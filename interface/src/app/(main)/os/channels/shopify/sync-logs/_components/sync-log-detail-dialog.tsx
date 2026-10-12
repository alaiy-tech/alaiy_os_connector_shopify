"use client";

import { Badge } from "@alaiy-os/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@alaiy-os/ui/dialog";
import { cn } from "@alaiy-os/utils";

import { getSyncStatusBadgeClass } from "@/constants/shopify";

import type { SyncLogFullRow } from "../page";

export function SyncLogDetailDialog({
  log,
  open,
  onOpenChange,
}: {
  log: SyncLogFullRow;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 capitalize">
            {log.sync_type}
            <Badge variant="outline" className={cn("border-0 font-medium capitalize", getSyncStatusBadgeClass(log.status))}>
              {log.status}
            </Badge>
          </DialogTitle>
          <DialogDescription>{log.name}</DialogDescription>
        </DialogHeader>

        <div className="grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
          <Stat label="Processed" value={log.items_processed} />
          <Stat label="Created" value={log.items_created} />
          <Stat label="Failed" value={log.items_failed} />
          <Stat label="Pages" value={log.pages_total ? `${log.pages_done}/${log.pages_total}` : "—"} />
        </div>

        <div className="grid grid-cols-2 gap-3 text-muted-foreground text-xs">
          <div>Started: {log.started_at ? new Date(log.started_at).toLocaleString() : "—"}</div>
          <div>Finished: {log.finished_at ? new Date(log.finished_at).toLocaleString() : "—"}</div>
        </div>

        {log.error_message && (
          <div>
            <p className="mb-1 font-medium text-sm">Error</p>
            <p className="whitespace-pre-wrap rounded-md border border-destructive/30 bg-destructive/5 p-3 text-destructive text-xs">
              {log.error_message}
            </p>
          </div>
        )}

        {log.log_messages && (
          <div>
            <p className="mb-1 font-medium text-sm">Log</p>
            <pre className="max-h-64 overflow-y-auto whitespace-pre-wrap rounded-md border bg-muted/30 p-3 text-xs">
              {log.log_messages}
            </pre>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-md border p-2">
      <div className="text-muted-foreground text-xs">{label}</div>
      <div className="tabular-nums">{value}</div>
    </div>
  );
}
