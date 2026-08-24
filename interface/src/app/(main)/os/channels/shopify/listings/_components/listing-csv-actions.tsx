"use client";

import { useRef, useState } from "react";

import { Button } from "@alaiy-os/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@alaiy-os/ui/dialog";
import { Input } from "@alaiy-os/ui/input";
import { Spinner } from "@alaiy-os/ui/spinner";
import { Download, Upload } from "lucide-react";
import { toast } from "sonner";

import {
  exportListingsCsv,
  shopifyErrorMessage,
  triggerUpdateListingsCsv,
  uploadPrivateFile,
} from "@/lib/frappe/shopify-sync";

/**
 * Export and bulk-update actions for the Listings page.
 *
 * Both run as background jobs on the Frappe side (a whole-catalogue export
 * or update has no place inside one request/response cycle), so neither
 * call returns a result to show inline — the outcome lands in Shopify
 * Sync Log, same as every other sync trigger on the dashboard.
 */
export function ListingCsvActions() {
  const [exporting, setExporting] = useState(false);
  const [importOpen, setImportOpen] = useState(false);

  async function runExport() {
    setExporting(true);
    try {
      await exportListingsCsv();
      toast.success("Export started — check the Shopify dashboard's sync log for the result.");
    } catch (error) {
      toast.error(shopifyErrorMessage(error, "Could not start the export."));
    } finally {
      setExporting(false);
    }
  }

  return (
    <div className="flex flex-wrap gap-2">
      <Button size="sm" variant="outline" disabled={exporting} onClick={() => void runExport()}>
        {exporting ? <Spinner /> : <Download />} Export CSV
      </Button>
      <Button size="sm" variant="outline" onClick={() => setImportOpen(true)}>
        <Upload /> Update from CSV
      </Button>
      <ImportDialog open={importOpen} onOpenChange={setImportOpen} />
    </div>
  );
}

function ImportDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (open: boolean) => void }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState(false);

  async function run() {
    const file = inputRef.current?.files?.[0];
    if (!file) {
      toast.warning("Choose a CSV file first.");
      return;
    }
    setBusy(true);
    try {
      const fileUrl = await uploadPrivateFile(file);
      await triggerUpdateListingsCsv(fileUrl);
      toast.success("Update queued — every change is logged as a before/after diff on the sync log once it runs.");
      onOpenChange(false);
    } catch (error) {
      toast.error(shopifyErrorMessage(error, "Could not start the update."));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={(next) => !busy && onOpenChange(next)}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Update listings from CSV</DialogTitle>
          <DialogDescription>
            Same format the Export CSV button produces — edit the fields you want to change and re-upload.
          </DialogDescription>
        </DialogHeader>
        <Input ref={inputRef} type="file" accept=".csv,text/csv" disabled={busy} />
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={busy}>
            Cancel
          </Button>
          <Button onClick={() => void run()} disabled={busy}>
            {busy ? (
              <>
                <Spinner /> Uploading...
              </>
            ) : (
              "Update"
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
