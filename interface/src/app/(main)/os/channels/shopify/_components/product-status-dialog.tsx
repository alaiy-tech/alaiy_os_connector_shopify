"use client";

import { useState } from "react";

import { Button } from "@alaiy-os/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@alaiy-os/ui/dialog";
import { Label } from "@alaiy-os/ui/label";
import { Switch } from "@alaiy-os/ui/switch";
import { toast } from "sonner";

const STATUS_OPTIONS = ["Active", "Draft", "Archived"] as const;

/**
 * Shared status-picker dialog for Import/Export Products — mirrors the old
 * Desk page's ask_statuses() (shopify.js): all three ticked by default,
 * refuses to confirm with none picked.
 */
export function ProductStatusDialog({
  open,
  onOpenChange,
  title,
  blurb,
  primaryLabel,
  onConfirm,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  blurb: string;
  primaryLabel: string;
  onConfirm: (statuses: string[]) => void;
}) {
  const [checked, setChecked] = useState<Record<string, boolean>>({ Active: true, Draft: true, Archived: true });

  function confirm() {
    const statuses = STATUS_OPTIONS.filter((status) => checked[status]);
    if (statuses.length === 0) {
      toast.warning("Pick at least one status.");
      return;
    }
    onConfirm(statuses);
    onOpenChange(false);
  }

  function handleOpenChange(next: boolean) {
    if (next) setChecked({ Active: true, Draft: true, Archived: true });
    onOpenChange(next);
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>{blurb}</DialogDescription>
        </DialogHeader>
        <div className="flex flex-col gap-3">
          {STATUS_OPTIONS.map((status) => (
            <div key={status} className="flex items-center justify-between rounded-lg border p-3">
              <Label htmlFor={`status-${status}`}>{status}</Label>
              <Switch
                id={`status-${status}`}
                checked={checked[status]}
                onCheckedChange={(v) => setChecked((prev) => ({ ...prev, [status]: v }))}
              />
            </div>
          ))}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={confirm}>{primaryLabel}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
