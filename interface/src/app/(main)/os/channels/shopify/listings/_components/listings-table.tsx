"use client";

import { useEffect, useState } from "react";

import Link from "next/link";

import { Badge } from "@alaiy-os/ui/badge";
import { Button } from "@alaiy-os/ui/button";
import { Card, CardContent, CardHeader } from "@alaiy-os/ui/card";
import { InputGroup, InputGroupAddon, InputGroupInput } from "@alaiy-os/ui/input-group";
import { Skeleton } from "@alaiy-os/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@alaiy-os/ui/table";
import { Tabs, TabsList, TabsTrigger } from "@alaiy-os/ui/tabs";
import { cn } from "@alaiy-os/utils";
import { Search, Zap } from "lucide-react";
import { toast } from "sonner";

import { getListingStatusBadgeClass } from "@/constants/shopify";
import { enableListingsByStatus, fetchResourceList, shopifyErrorMessage } from "@/lib/frappe/shopify-sync";

interface ShopifyListing extends Record<string, unknown> {
  name: string;
  item: string;
  is_enabled: 0 | 1;
  sh_shopify_status: string;
  listing_title: string | null;
  listing_price: number | null;
  sh_shopify_product_id: string | null;
  last_synced_at: string | null;
}

const STATUS_TABS = ["All", "Active", "Draft", "Archived"] as const;
type StatusTab = (typeof STATUS_TABS)[number];

// Not full server-side pagination yet (see DESIGN.md's list-page pattern for
// the target shape) — this is a first pass over the raw doctype. Fine while
// this fits comfortably on one page; if a store's real listing count grows
// past this, that is the signal to build the paginated version, not to raise
// the cap silently.
const ROW_LIMIT = 200;

export function ListingsTable() {
  const [tab, setTab] = useState<StatusTab>("All");
  const [search, setSearch] = useState("");
  const [rows, setRows] = useState<ShopifyListing[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [enabling, setEnabling] = useState(false);
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setRows(null);
    setError(null);

    const timeout = setTimeout(() => {
      const filters: Array<[string, string, unknown]> = [];
      if (tab !== "All") filters.push(["sh_shopify_status", "=", tab]);
      if (search.trim()) filters.push(["listing_title", "like", `%${search.trim()}%`]);

      fetchResourceList<ShopifyListing>(
        "Shopify Product Listing",
        ["name", "item", "is_enabled", "sh_shopify_status", "listing_title", "listing_price", "sh_shopify_product_id", "last_synced_at"],
        { orderBy: "modified desc", filters },
      )
        .then((result) => {
          if (!cancelled) setRows(result.slice(0, ROW_LIMIT));
        })
        .catch((err) => {
          if (cancelled) return;
          const message = shopifyErrorMessage(err, "Could not load listings.");
          setError(message);
          toast.error(message);
        });
    }, 300);

    return () => {
      cancelled = true;
      clearTimeout(timeout);
    };
  }, [tab, search, reloadToken]);

  async function enableCurrentTab() {
    setEnabling(true);
    try {
      await enableListingsByStatus(tab === "All" ? undefined : [tab]);
      toast.success(
        tab === "All" ? "Enabling every disabled listing — this runs in the background." : `Enabling every disabled ${tab} listing.`,
      );
      setTimeout(() => setReloadToken((token) => token + 1), 2000);
    } catch (error) {
      toast.error(shopifyErrorMessage(error, "Could not start the bulk enable."));
    } finally {
      setEnabling(false);
    }
  }

  return (
    <Card className="gap-0">
      <CardHeader className="border-b">
        <InputGroup className="h-7 w-full md:w-64">
          <InputGroupAddon>
            <Search className="size-4" />
          </InputGroupAddon>
          <InputGroupInput placeholder="Search listings..." value={search} onChange={(e) => setSearch(e.target.value)} />
        </InputGroup>
      </CardHeader>
      <CardContent className="gap-0 px-0">
        <div className="flex items-center justify-between gap-2 border-b px-4 py-2">
          <Tabs value={tab} onValueChange={(v) => setTab(v as StatusTab)}>
            <TabsList>
              {STATUS_TABS.map((t) => (
                <TabsTrigger key={t} value={t}>
                  {t}
                </TabsTrigger>
              ))}
            </TabsList>
          </Tabs>
          <Button size="sm" variant="outline" disabled={enabling} onClick={() => void enableCurrentTab()}>
            <Zap /> Enable {tab === "All" ? "all disabled" : tab.toLowerCase()}
          </Button>
        </div>

        {error ? (
          <p className="p-4 text-muted-foreground text-sm">{error}</p>
        ) : (
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Item</TableHead>
                  <TableHead>Title</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Enabled</TableHead>
                  <TableHead className="text-right">Price</TableHead>
                  <TableHead>Shopify Product ID</TableHead>
                  <TableHead>Last synced</TableHead>
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
                      {tab === "All" ? "No listings synced yet." : `No ${tab.toLowerCase()} listings.`}
                    </TableCell>
                  </TableRow>
                ) : (
                  rows.map((row) => (
                    <TableRow key={row.name}>
                      <TableCell className="font-medium">
                        <Link href={`/os/channels/shopify/listings/${encodeURIComponent(row.name)}`} className="hover:underline">
                          {row.item}
                        </Link>
                      </TableCell>
                      <TableCell className="max-w-64 truncate" title={row.listing_title ?? undefined}>
                        {row.listing_title ? (
                          <Link href={`/os/channels/shopify/listings/${encodeURIComponent(row.name)}`} className="hover:underline">
                            {row.listing_title}
                          </Link>
                        ) : (
                          <span className="text-muted-foreground">—</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant="outline"
                          className={cn("border-0 font-medium", getListingStatusBadgeClass(row.sh_shopify_status))}
                        >
                          {row.sh_shopify_status || "Active"}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant={row.is_enabled ? "outline" : "secondary"}>{row.is_enabled ? "Enabled" : "Disabled"}</Badge>
                      </TableCell>
                      <TableCell className="text-right tabular-nums">
                        {row.listing_price != null ? row.listing_price.toFixed(2) : <span className="text-muted-foreground">—</span>}
                      </TableCell>
                      <TableCell className="font-mono text-xs">
                        {row.sh_shopify_product_id || <span className="text-muted-foreground">—</span>}
                      </TableCell>
                      <TableCell>
                        {row.last_synced_at ? new Date(row.last_synced_at).toLocaleString() : <span className="text-muted-foreground">—</span>}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
