"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { Badge } from "@alaiy-os/ui/badge";
import { Button } from "@alaiy-os/ui/button";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@alaiy-os/ui/card";
import { Input } from "@alaiy-os/ui/input";
import { Label } from "@alaiy-os/ui/label";
import { Skeleton } from "@alaiy-os/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@alaiy-os/ui/table";
import { cn } from "@alaiy-os/utils";
import {
  Calendar as CalendarIcon,
  Download,
  List as ListIcon,
  Package,
  RefreshCw,
  ShoppingCart,
  Store,
  Tag as TagIcon,
  Upload,
  Warehouse,
} from "lucide-react";
import { toast } from "sonner";

import { getSyncStatusBadgeClass } from "@/constants/shopify";
import { testShopifyConnection } from "@/lib/frappe/shopify-connection";
import {
  type DashboardStats,
  type ShopifySideStats,
  type SyncLogRow,
  fetchDashboardStats,
  fetchShopifySideStats,
  fetchSyncStatus,
  importExistingOrders,
  refreshShopifyCollections,
  refreshShopifyLocations,
  refreshShopifyTags,
  refreshShopifyTaxonomy,
  requestCancelSync,
  shopifyErrorMessage,
  triggerInventoryPush,
  triggerProductExport,
  triggerProductImport,
} from "@/lib/frappe/shopify-sync";
import { ProductStatusDialog } from "./product-status-dialog";

const CANCELLABLE_STATUSES = new Set(["queued", "running"]);
const ACTIVE_LOG_STATUSES = new Set(["queued", "running"]);
const POLL_MS = 2000;

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
  const [connection, setConnection] = useState<{ success: boolean; message: string } | null>(null);
  const [progress, setProgress] = useState<Record<string, SyncLogRow | undefined>>({});
  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [exportDialogOpen, setExportDialogOpen] = useState(false);
  const [orderImportMode, setOrderImportMode] = useState<"All orders" | "Date range">("All orders");

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

  useEffect(() => {
    testShopifyConnection()
      .then(setConnection)
      .catch(() => setConnection({ success: false, message: "Could not reach the connection test." }));
  }, []);

  // Polls the sync log for one job every 2s while it's queued/running, same
  // cadence as the old Desk page's poll_import_progress, stopping once the
  // job leaves that state.
  function pollLog(key: string, logName: string) {
    fetchSyncStatus()
      .then((rows) => {
        const row = rows.find((r) => r.name === logName);
        setProgress((prev) => ({ ...prev, [key]: row }));
        if (row && ACTIVE_LOG_STATUSES.has(row.status)) {
          setTimeout(() => pollLog(key, logName), POLL_MS);
        } else {
          void load();
        }
      })
      .catch(() => {
        // transient — the next manual refresh will pick the final state up
      });
  }

  async function trigger(key: string, run: () => Promise<unknown>, label: string) {
    setTriggering(key);
    setProgress((prev) => ({ ...prev, [key]: undefined }));
    try {
      const result = (await run()) as { log_name?: string } | undefined;
      toast.success(`${label} started.`);
      if (result?.log_name) {
        pollLog(key, result.log_name);
      } else {
        setTimeout(() => void load(), 1500);
      }
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
    if (orderImportMode === "Date range" && (!importFrom || !importTo)) {
      toast.warning("Pick both a From and To date.");
      return;
    }
    await trigger(
      "import-orders",
      () => (orderImportMode === "Date range" ? importExistingOrders(importFrom, importTo) : importExistingOrders()),
      "Order import",
    );
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
      <div className="flex items-center gap-2 rounded-lg border p-3 text-sm">
        {connection === null ? (
          <span className="text-muted-foreground">Checking connection…</span>
        ) : (
          <>
            <Badge variant="outline" className={cn("border-0 font-medium", connection.success ? getSyncStatusBadgeClass("Success") : getSyncStatusBadgeClass("Failed"))}>
              {connection.success ? "Connected" : "Not connected"}
            </Badge>
            <span className="text-muted-foreground">{connection.message}</span>
          </>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4 xl:grid-cols-4">
        <StatCard icon={<Package className="size-4" />} label="Total items" value={stats.items_total} comparison="Every Item in the catalog" />
        <StatCard icon={<Package className="size-4" />} label="Product templates" value={stats.templates_total} comparison="Templates only, not variants" />
        <StatCard icon={<RefreshCw className="size-4" />} label="Pushed to Shopify" value={stats.templates_pushed} comparison="Templates linked to a Shopify product" />
        <StatCard icon={<RefreshCw className="size-4" />} label="Pending export" value={stats.templates_pending} comparison="Not yet linked to Shopify" />
        <StatCard icon={<Warehouse className="size-4" />} label="Variants" value={stats.variants_total} comparison="Total variants across all templates" />
        <StatCard icon={<Warehouse className="size-4" />} label="Variants pushed" value={stats.variants_pushed} comparison="Variants linked to a Shopify variant" />
        <StatCard icon={<Store className="size-4" />} label="Listings" value={stats.listings_total} comparison={`${stats.listings_enabled} enabled`} />
        <StatCard icon={<ShoppingCart className="size-4" />} label="Orders synced" value={stats.orders_synced} comparison="Linked to a Shopify order" />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Templates by status</CardTitle>
          <CardDescription>Click a status to jump to those listings.</CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-3 gap-4">
          {(
            [
              { label: "Active", value: stats.templates_active },
              { label: "Draft", value: stats.templates_draft },
              { label: "Archived", value: stats.templates_archived },
            ] as const
          ).map((s) => (
            <Link
              key={s.label}
              href={`/os/channels/shopify/listings?status=${encodeURIComponent(s.label)}`}
              className="rounded-lg border p-3 transition-colors hover:bg-accent"
            >
              <div className="text-2xl leading-none tracking-tight tabular-nums">{s.value.toLocaleString()}</div>
              <div className="text-muted-foreground text-sm">{s.label}</div>
            </Link>
          ))}
        </CardContent>
      </Card>

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

      <div className="grid grid-cols-1 items-stretch gap-4 lg:grid-cols-2">
        <Card className="flex flex-col">
          <CardHeader>
            <div className="flex items-center gap-2.5">
              <span className="flex size-7 items-center justify-center rounded-md border bg-background">
                <ShoppingCart className="size-3.5" />
              </span>
              <div>
                <CardTitle className="text-base">Orders</CardTitle>
                <CardDescription>Import Shopify orders into Alaiy OS.</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="flex flex-1 flex-col items-start gap-3">
            <div className="flex gap-1.5">
              <Button
                type="button"
                size="sm"
                variant={orderImportMode === "All orders" ? "secondary" : "outline"}
                onClick={() => setOrderImportMode("All orders")}
              >
                <ListIcon /> All orders
              </Button>
              <Button
                type="button"
                size="sm"
                variant={orderImportMode === "Date range" ? "secondary" : "outline"}
                onClick={() => setOrderImportMode("Date range")}
              >
                <CalendarIcon /> Date range
              </Button>
            </div>

            {orderImportMode === "Date range" && (
              <div className="flex flex-wrap gap-2">
                <div className="space-y-1">
                  <Label htmlFor="import-from" className="text-muted-foreground text-xs">
                    From
                  </Label>
                  <Input id="import-from" type="date" value={importFrom} onChange={(e) => setImportFrom(e.target.value)} className="h-8" />
                </div>
                <div className="space-y-1">
                  <Label htmlFor="import-to" className="text-muted-foreground text-xs">
                    To
                  </Label>
                  <Input id="import-to" type="date" value={importTo} onChange={(e) => setImportTo(e.target.value)} className="h-8" />
                </div>
              </div>
            )}

            <p className="text-muted-foreground text-xs">Brings in Sales Orders, Invoices &amp; Payments, and Fulfillments.</p>

            {progress["import-orders"] && (
              <p className="text-muted-foreground text-xs">{formatProgress(progress["import-orders"])}</p>
            )}

            <Button size="sm" className="mt-auto" disabled={triggering !== null} onClick={() => void runImportExistingOrders()}>
              {triggering === "import-orders" ? <RefreshCw className="animate-spin" /> : <Download />} Import Orders from Shopify
            </Button>
          </CardContent>
        </Card>

        <Card className="flex flex-col">
          <CardHeader>
            <div className="flex items-center gap-2.5">
              <span className="flex size-7 items-center justify-center rounded-md border bg-background">
                <Warehouse className="size-3.5" />
              </span>
              <div>
                <CardTitle className="text-base">Inventory</CardTitle>
                <CardDescription>Push stock levels from Alaiy OS to Shopify.</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="flex flex-1 flex-col items-start gap-3">
            <p className="text-muted-foreground text-sm">Send the latest stock updates from Alaiy OS to Shopify.</p>
            {progress.inventory && <p className="text-muted-foreground text-xs">{formatProgress(progress.inventory)}</p>}
            <Button size="sm" className="mt-auto" disabled={triggering !== null} onClick={() => void trigger("inventory", triggerInventoryPush, "Inventory sync")}>
              <RefreshCw className={cn(triggering === "inventory" && "animate-spin")} /> Sync Inventory
            </Button>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2.5">
            <span className="flex size-7 items-center justify-center rounded-md border bg-background">
              <Package className="size-3.5" />
            </span>
            <div>
              <CardTitle className="text-base">Products</CardTitle>
              <CardDescription>Manage Shopify products and variants.</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-2">
          <div className="flex flex-col items-start gap-2 rounded-lg border p-3">
            <p className="font-medium text-sm">Import</p>
            <p className="text-muted-foreground text-xs">Import products from Shopify.</p>
            {progress.products && <p className="text-muted-foreground text-xs">{formatProgress(progress.products)}</p>}
            <Button size="sm" disabled={triggering !== null} onClick={() => setImportDialogOpen(true)}>
              {triggering === "products" ? <RefreshCw className="animate-spin" /> : <Download />} Import Products from Shopify
            </Button>
          </div>
          <div className="flex flex-col items-start gap-2 rounded-lg border p-3">
            <p className="font-medium text-sm">Export</p>
            <p className="text-muted-foreground text-xs">Push local (not-yet-linked) products to Shopify.</p>
            {progress["export-products"] && (
              <p className="text-muted-foreground text-xs">{formatProgress(progress["export-products"])}</p>
            )}
            <Button size="sm" variant="outline" disabled={triggering !== null} onClick={() => setExportDialogOpen(true)}>
              {triggering === "export-products" ? <RefreshCw className="animate-spin" /> : <Upload />} Export Products to Shopify
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2.5">
              <span className="flex size-7 items-center justify-center rounded-md border bg-background">
                <Store className="size-3.5" />
              </span>
              <div>
                <CardTitle className="text-base">Listings</CardTitle>
                <CardDescription>Per-marketplace product listings (title, price, images, variants).</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <Button size="sm" variant="outline" asChild>
              <Link href="/os/channels/shopify/listings">Manage Listings</Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2.5">
              <span className="flex size-7 items-center justify-center rounded-md border bg-background">
                <TagIcon className="size-3.5" />
              </span>
              <div>
                <CardTitle className="text-base">Categories &amp; Tags</CardTitle>
                <CardDescription>Refresh cached taxonomy, tags, collections and locations</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="flex flex-col items-start gap-3">
            <div className="flex flex-wrap gap-2">
            <Button
              size="sm"
              variant="outline"
              disabled={triggering !== null}
              onClick={() => void trigger("categories", refreshShopifyTaxonomy, "Category sync")}
            >
              <RefreshCw className={cn(triggering === "categories" && "animate-spin")} /> Sync Categories
            </Button>
            <Button
              size="sm"
              variant="outline"
              disabled={triggering !== null}
              onClick={() => void trigger("tags", refreshShopifyTags, "Tags sync")}
            >
              <RefreshCw className={cn(triggering === "tags" && "animate-spin")} /> Sync Tags
            </Button>
            <Button
              size="sm"
              variant="outline"
              disabled={triggering !== null}
              onClick={() => void trigger("collections", refreshShopifyCollections, "Collections sync")}
            >
              <RefreshCw className={cn(triggering === "collections" && "animate-spin")} /> Sync Collections
            </Button>
            <Button
              size="sm"
              variant="outline"
              disabled={triggering !== null}
              onClick={() => void trigger("locations", refreshShopifyLocations, "Locations sync")}
            >
              <RefreshCw className={cn(triggering === "locations" && "animate-spin")} /> Sync Locations
            </Button>
          </div>
          {(progress.categories || progress.tags || progress.collections || progress.locations) && (
            <div className="flex flex-col gap-1 text-muted-foreground text-xs">
              {progress.categories && <p>Categories: {formatProgress(progress.categories)}</p>}
              {progress.tags && <p>Tags: {formatProgress(progress.tags)}</p>}
              {progress.collections && <p>Collections: {formatProgress(progress.collections)}</p>}
              {progress.locations && <p>Locations: {formatProgress(progress.locations)}</p>}
            </div>
          )}
          </CardContent>
        </Card>
      </div>

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
                  <TableHead>Trigger</TableHead>
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
                    <TableCell colSpan={8} className="h-24 text-center text-muted-foreground">
                      No sync runs yet.
                    </TableCell>
                  </TableRow>
                ) : (
                  log.map((row) => (
                    <TableRow key={row.name}>
                      <TableCell className="capitalize">
                        <a
                          href={`/app/shopify-sync-log/${row.name}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="underline underline-offset-2 hover:text-foreground"
                        >
                          {row.sync_type}
                        </a>
                      </TableCell>
                      <TableCell className="capitalize text-muted-foreground">{row.trigger}</TableCell>
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

      <ProductStatusDialog
        open={importDialogOpen}
        onOpenChange={setImportDialogOpen}
        title="Import Products from Shopify"
        blurb="New products are created, changed products are updated, unchanged ones are left alone. On the very first run only, any stray unlinked product data is wiped first as a safety net."
        primaryLabel="Import"
        onConfirm={(statuses) => void trigger("products", () => triggerProductImport(statuses), "Product import")}
      />
      <ProductStatusDialog
        open={exportDialogOpen}
        onOpenChange={setExportDialogOpen}
        title="Export Products to Shopify"
        blurb="Pushes every local product that is not yet linked to Shopify. Only listings whose status is ticked below are sent."
        primaryLabel="Export"
        onConfirm={(statuses) => void trigger("export-products", () => triggerProductExport(statuses), "Product export")}
      />
    </div>
  );
}

function formatProgress(row: SyncLogRow): string {
  const parts = [row.status];
  if (row.items_processed) parts.push(`${row.items_processed} processed`);
  if (row.items_created) parts.push(`${row.items_created} created`);
  if (row.items_failed) parts.push(`${row.items_failed} failed`);
  return parts.join(" · ");
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
