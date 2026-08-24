"use client";

import { useCallback, useEffect, useState } from "react";

import { Badge } from "@alaiy-os/ui/badge";
import { Button } from "@alaiy-os/ui/button";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@alaiy-os/ui/card";
import { Input } from "@alaiy-os/ui/input";
import { Label } from "@alaiy-os/ui/label";
import { Skeleton } from "@alaiy-os/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@alaiy-os/ui/table";
import { cn } from "@alaiy-os/utils";
import { Package, RefreshCw, ShoppingCart, Store, Warehouse } from "lucide-react";
import { toast } from "sonner";

import { getSyncStatusBadgeClass } from "@/constants/shopify";
import {
  type DashboardStats,
  type ShopifySideStats,
  type SyncLogRow,
  fetchDashboardStats,
  fetchShopifySideStats,
  fetchSyncStatus,
  importExistingOrders,
  requestCancelSync,
  shopifyErrorMessage,
  triggerInventoryPush,
  triggerOrdersSync,
  triggerProductExport,
  triggerProductImport,
} from "@/lib/frappe/shopify-sync";

const CANCELLABLE_STATUSES = new Set(["queued", "running"]);

export function SyncDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [shopifyStats, setShopifyStats] = useState<ShopifySideStats | null>(null);
  const [log, setLog] = useState<SyncLogRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [shopifyLoading, setShopifyLoading] = useState(true);
  const [triggering, setTriggering] = useState<string | null>(null);
  const [cancelling, setCancelling] = useState<string | null>(null);
  const [importFrom, setImportFrom] = useState("");
  const [importTo, setImportTo] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [dashboard, syncLog] = await Promise.all([fetchDashboardStats(), fetchSyncStatus()]);
      setStats(dashboard);
      setLog(syncLog);
    } catch (error) {
      toast.error(shopifyErrorMessage(error, "Could not load the Shopify dashboard."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  // Live Shopify counts are their own slower call — fetched separately so they
  // never hold up the fast local numbers above.
  useEffect(() => {
    let cancelled = false;
    setShopifyLoading(true);
    fetchShopifySideStats()
      .then((result) => {
        if (!cancelled) setShopifyStats(result);
      })
      .catch(() => {
        if (!cancelled) setShopifyStats(null);
      })
      .finally(() => {
        if (!cancelled) setShopifyLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function trigger(key: string, run: () => Promise<unknown>, label: string) {
    setTriggering(key);
    try {
      await run();
      toast.success(`${label} started.`);
      setTimeout(() => void load(), 1500);
    } catch (error) {
      toast.error(shopifyErrorMessage(error, `Could not start ${label.toLowerCase()}.`));
    } finally {
      setTriggering(null);
    }
  }

  async function cancel(logName: string) {
    setCancelling(logName);
    try {
      const outcome = await requestCancelSync(logName);
      if (outcome.cancelled) toast.success("Cancel requested — the job stops on its next check.");
      else toast.info(outcome.reason ?? "That job already finished.");
      void load();
    } catch (error) {
      toast.error(shopifyErrorMessage(error, "Could not cancel this sync."));
    } finally {
      setCancelling(null);
    }
  }

  async function runImportExistingOrders() {
    setTriggering("import-orders");
    try {
      await importExistingOrders(importFrom || undefined, importTo || undefined);
      toast.success("Order backfill started.");
      setTimeout(() => void load(), 1500);
    } catch (error) {
      toast.error(shopifyErrorMessage(error, "Could not start the order backfill."));
    } finally {
      setTriggering(null);
    }
  }

  if (loading) {
    return (
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          // biome-ignore lint/suspicious/noArrayIndexKey: fixed-length skeleton placeholder
          <Skeleton key={i} className="h-[122px] w-full rounded-xl" />
        ))}
      </div>
    );
  }

  if (!stats) {
    return <p className="text-muted-foreground text-sm">Could not load the Shopify dashboard. Make sure you're signed in and try again.</p>;
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard
          icon={<Package className="size-4" />}
          label="Products"
          value={stats.templates_total}
          comparison={`${stats.templates_pushed} pushed to Shopify · ${stats.templates_pending} pending`}
        />
        <StatCard
          icon={<Store className="size-4" />}
          label="Listings"
          value={stats.listings_total}
          comparison={`${stats.listings_enabled} enabled`}
        />
        <StatCard
          icon={<Warehouse className="size-4" />}
          label="Variants"
          value={stats.variants_total}
          comparison={`${stats.variants_pushed} pushed to Shopify`}
        />
        <StatCard
          icon={<ShoppingCart className="size-4" />}
          label="Orders synced"
          value={stats.orders_synced}
          comparison="Linked to a Shopify order"
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Live on Shopify</CardTitle>
          <CardDescription>Counted from the store itself, not this database — separate from the numbers above on purpose.</CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          {shopifyLoading ? (
            <>
              <Skeleton className="h-16 w-full" />
              <Skeleton className="h-16 w-full" />
              <Skeleton className="h-16 w-full" />
            </>
          ) : shopifyStats ? (
            <>
              <MiniStat label="Products" value={shopifyStats.shopify_products} />
              <MiniStat label="Orders" value={shopifyStats.shopify_orders} />
              <MiniStat label="Variants" value={shopifyStats.shopify_variants} />
            </>
          ) : (
            <p className="text-muted-foreground text-sm sm:col-span-3">Could not reach Shopify to fetch live counts.</p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Sync</CardTitle>
          <CardDescription>Trigger a sync now, or check the recent runs below.</CardDescription>
          <CardAction className="flex flex-wrap gap-2">
            <Button
              size="sm"
              variant="outline"
              disabled={triggering !== null}
              onClick={() => void trigger("orders", triggerOrdersSync, "Order sync")}
            >
              <RefreshCw className={cn(triggering === "orders" && "animate-spin")} /> Sync Orders
            </Button>
            <Button
              size="sm"
              variant="outline"
              disabled={triggering !== null}
              onClick={() => void trigger("inventory", triggerInventoryPush, "Inventory push")}
            >
              <RefreshCw className={cn(triggering === "inventory" && "animate-spin")} /> Push Inventory
            </Button>
            <Button
              size="sm"
              variant="outline"
              disabled={triggering !== null}
              onClick={() => void trigger("products", () => triggerProductImport(), "Product import")}
            >
              <RefreshCw className={cn(triggering === "products" && "animate-spin")} /> Import Products
            </Button>
            <Button
              size="sm"
              variant="outline"
              disabled={triggering !== null}
              onClick={() => void trigger("export-products", () => triggerProductExport(), "Product export")}
            >
              <RefreshCw className={cn(triggering === "export-products" && "animate-spin")} /> Export Products
            </Button>
          </CardAction>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-end gap-2 rounded-lg border p-3">
            <div className="space-y-1">
              <Label htmlFor="import-from" className="text-muted-foreground text-xs">
                Backfill orders from
              </Label>
              <Input id="import-from" type="date" value={importFrom} onChange={(e) => setImportFrom(e.target.value)} className="h-8" />
            </div>
            <div className="space-y-1">
              <Label htmlFor="import-to" className="text-muted-foreground text-xs">
                to
              </Label>
              <Input id="import-to" type="date" value={importTo} onChange={(e) => setImportTo(e.target.value)} className="h-8" />
            </div>
            <Button size="sm" variant="outline" disabled={triggering !== null} onClick={() => void runImportExistingOrders()}>
              <RefreshCw className={cn(triggering === "import-orders" && "animate-spin")} /> Import Existing Orders
            </Button>
            <p className="text-muted-foreground text-xs">
              A one-off backfill for a date range — separate from the regular incremental Sync Orders above.
            </p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Recent runs</CardTitle>
        </CardHeader>
        <CardContent className="px-0">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Type</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Started</TableHead>
                  <TableHead className="text-right">Processed</TableHead>
                  <TableHead className="text-right">Created</TableHead>
                  <TableHead className="text-right">Failed</TableHead>
                  <TableHead />
                </TableRow>
              </TableHeader>
              <TableBody>
                {log.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="h-24 text-center text-muted-foreground">
                      No sync runs yet.
                    </TableCell>
                  </TableRow>
                ) : (
                  log.map((row) => (
                    <TableRow key={row.name}>
                      <TableCell className="capitalize">{row.sync_type}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className={cn("border-0 font-medium", getSyncStatusBadgeClass(row.status))}>
                          {row.status}
                        </Badge>
                      </TableCell>
                      <TableCell>{row.started_at ? new Date(row.started_at).toLocaleString() : "—"}</TableCell>
                      <TableCell className="text-right tabular-nums">{row.items_processed}</TableCell>
                      <TableCell className="text-right tabular-nums">{row.items_created}</TableCell>
                      <TableCell className="text-right tabular-nums">{row.items_failed}</TableCell>
                      <TableCell>
                        {CANCELLABLE_STATUSES.has(row.status) && (
                          <Button
                            size="sm"
                            variant="ghost"
                            className="h-7 px-2 text-xs"
                            disabled={cancelling === row.name}
                            onClick={() => void cancel(row.name)}
                          >
                            {cancelling === row.name ? "Cancelling..." : "Cancel"}
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
  comparison,
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
  comparison: string;
}) {
  return (
    <Card>
      <CardHeader>
        <CardDescription>{label}</CardDescription>
        <CardAction>{icon}</CardAction>
      </CardHeader>
      <CardContent>
        <div className="text-2xl leading-none tracking-tight tabular-nums">{value.toLocaleString()}</div>
        <p className="text-muted-foreground text-sm">{comparison}</p>
      </CardContent>
    </Card>
  );
}

function MiniStat({ label, value }: { label: string; value: number | null }) {
  return (
    <div>
      <div className="text-muted-foreground text-xs">{label}</div>
      <div className="text-2xl leading-none tracking-tight tabular-nums">{value === null ? "—" : value.toLocaleString()}</div>
    </div>
  );
}
