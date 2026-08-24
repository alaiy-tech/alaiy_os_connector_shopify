"use client";

import { useState } from "react";

import { Button } from "@alaiy-os/ui/button";
import { cn } from "@alaiy-os/utils";
import { RefreshCw } from "lucide-react";
import { toast } from "sonner";

import { shopifyErrorMessage } from "@/lib/frappe/shopify-sync";

/**
 * Wraps one of the simple Shopify master lists with a "Refresh from
 * Shopify" action. Bumping `reloadToken` and passing it as the child
 * table's `key` is what triggers a re-fetch — simpler than threading a
 * reload callback through `SimpleResourceTable`, and the same remount-on-key
 * trick NayaGlobal's own settings screen uses via `reloadToken`.
 */
export function RefreshableList({
  refresh,
  refreshLabel = "Refresh from Shopify",
  children,
}: {
  refresh: () => Promise<unknown>;
  refreshLabel?: string;
  children: (reloadToken: number) => React.ReactNode;
}) {
  const [reloadToken, setReloadToken] = useState(0);
  const [busy, setBusy] = useState(false);

  async function run() {
    setBusy(true);
    try {
      await refresh();
      toast.success("Refresh started — this can take a moment for a large catalogue.");
      // The refresh itself runs as a background job on the Frappe side, so
      // give it a moment before re-reading the list rather than racing it.
      setTimeout(() => setReloadToken((token) => token + 1), 2000);
    } catch (error) {
      toast.error(shopifyErrorMessage(error, "Could not start the refresh."));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex justify-end">
        <Button size="sm" variant="outline" disabled={busy} onClick={() => void run()}>
          <RefreshCw className={cn(busy && "animate-spin")} /> {refreshLabel}
        </Button>
      </div>
      {children(reloadToken)}
    </div>
  );
}
