"use client";

import { useEffect, useState } from "react";

import Link from "next/link";

import { PageHeader } from "@alaiy-os/layout/page-header";
import { Badge } from "@alaiy-os/ui/badge";
import { Button } from "@alaiy-os/ui/button";
import { Card, CardContent } from "@alaiy-os/ui/card";
import { Checkbox } from "@alaiy-os/ui/checkbox";
import { Skeleton } from "@alaiy-os/ui/skeleton";
import { Spinner } from "@alaiy-os/ui/spinner";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@alaiy-os/ui/table";
import { cn } from "@alaiy-os/utils";
import { Check } from "lucide-react";
import { toast } from "sonner";

import { fetchEnrichmentQueue, type EnrichedListingQueueRow } from "@/lib/frappe/shopify-enrichment";
import { approveListings } from "@/lib/frappe/shopify-enrichment-review";

import { useShopifyStore } from "../../_lib/use-shopify-store";
import { StoreSwitcher } from "../../_components/store-switcher";

const STATUS_TONE: Record<string, string> = {
  "Needs Review": "bg-amber-500/15 text-amber-700 dark:text-amber-400",
  Approved: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-400",
  Draft: "bg-muted text-muted-foreground",
};

const CONFIDENCE_TONE: Record<string, string> = {
  high: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-400",
  medium: "bg-amber-500/15 text-amber-700 dark:text-amber-400",
  low: "bg-red-500/15 text-red-700 dark:text-red-400",
};

export default function Page() {
  const { selected } = useShopifyStore();
  const [rows, setRows] = useState<EnrichedListingQueueRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [checked, setChecked] = useState<Set<string>>(new Set());
  const [approving, setApproving] = useState(false);

  function load() {
    setRows(null);
    setChecked(new Set());
    fetchEnrichmentQueue(selected ?? undefined)
      .then(setRows)
      .catch((err) => {
        const message = err instanceof Error ? err.message : "Could not load the enrichment queue.";
        setError(message);
        toast.error(message);
      });
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selected]);

  function toggle(name: string, next: boolean) {
    setChecked((current) => {
      const copy = new Set(current);
      if (next) copy.add(name);
      else copy.delete(name);
      return copy;
    });
  }

  function toggleAll(next: boolean) {
    if (!rows) return;
    setChecked(next ? new Set(rows.filter((r) => r.status !== "Approved").map((r) => r.name)) : new Set());
  }

  async function bulkApprove() {
    if (checked.size === 0) return;
    setApproving(true);
    try {
      const result = await approveListings(Array.from(checked), selected ?? undefined);
      if (result.failed > 0) {
        toast.error(`Approved ${result.approved}, ${result.failed} failed. Check Error Log for details.`);
      } else {
        toast.success(`Approved ${result.approved}${result.skipped ? `, ${result.skipped} already approved` : ""}.`);
      }
      load();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Could not approve.");
    } finally {
      setApproving(false);
    }
  }

  const approvableCount = rows?.filter((r) => r.status !== "Approved").length ?? 0;

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <PageHeader title="Enrichment Review" subtitle="AI-drafted listing content and photos, waiting for a human to approve." />
        <div className="flex items-center gap-2">
          <StoreSwitcher />
          {checked.size > 0 && (
            <Button size="sm" disabled={approving} onClick={() => void bulkApprove()}>
              {approving ? <Spinner /> : <Check />} Approve {checked.size}
            </Button>
          )}
        </div>
      </div>

      {error ? (
        <p className="text-muted-foreground text-sm">{error}</p>
      ) : (
        <Card className="gap-0">
          <CardContent className="px-0">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-10">
                      <Checkbox
                        checked={rows !== null && approvableCount > 0 && checked.size === approvableCount}
                        onCheckedChange={(v) => toggleAll(!!v)}
                        disabled={!rows || approvableCount === 0}
                        aria-label="Select all"
                      />
                    </TableHead>
                    <TableHead>Item</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Confidence</TableHead>
                    <TableHead>Images</TableHead>
                    <TableHead>Needs review</TableHead>
                    <TableHead>Last updated</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {rows === null ? (
                    <TableRow>
                      <TableCell colSpan={7} className="p-4">
                        <Skeleton className="h-24 w-full" />
                      </TableCell>
                    </TableRow>
                  ) : rows.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="h-24 text-center text-muted-foreground">
                        Nothing waiting for review.
                      </TableCell>
                    </TableRow>
                  ) : (
                    rows.map((row) => (
                      <TableRow key={row.name}>
                        <TableCell>
                          <Checkbox
                            checked={checked.has(row.name)}
                            onCheckedChange={(v) => toggle(row.name, !!v)}
                            disabled={row.status === "Approved"}
                            aria-label={`Select ${row.item_code}`}
                          />
                        </TableCell>
                        <TableCell className="font-medium">
                          <Link href={`/os/channels/shopify/listings/enrichment/${encodeURIComponent(row.item_code)}`} className="hover:underline">
                            {row.title || row.item_code}
                          </Link>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className={cn("border-0 font-medium", STATUS_TONE[row.status] ?? "")}>
                            {row.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {row.confidence ? (
                            <Badge variant="outline" className={cn("border-0 font-medium capitalize", CONFIDENCE_TONE[row.confidence] ?? "")}>
                              {row.confidence}
                            </Badge>
                          ) : (
                            <span className="text-muted-foreground">—</span>
                          )}
                        </TableCell>
                        <TableCell>{row.image_status}</TableCell>
                        <TableCell>
                          {row.needs_review ? (
                            <span className="text-muted-foreground text-xs">{row.needs_review}</span>
                          ) : (
                            <span className="text-muted-foreground">—</span>
                          )}
                        </TableCell>
                        <TableCell>{new Date(row.modified).toLocaleString()}</TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
