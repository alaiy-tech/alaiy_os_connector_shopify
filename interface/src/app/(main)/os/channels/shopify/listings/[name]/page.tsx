"use client";

import { use, useEffect, useState } from "react";

import Link from "next/link";

import { PageHeader } from "@alaiy-os/layout/page-header";

import { Badge } from "@alaiy-os/ui/badge";
import { Card, CardContent, CardHeader } from "@alaiy-os/ui/card";
import { Skeleton } from "@alaiy-os/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@alaiy-os/ui/table";
import { cn } from "@alaiy-os/utils";
import { ArrowLeft } from "lucide-react";
import { toast } from "sonner";

import { getListingStatusBadgeClass } from "@/constants/shopify";
import { fetchListingDetail, type ShopifyListingDetail } from "@/lib/frappe/shopify-listing-detail";
import { shopifyErrorMessage } from "@/lib/frappe/shopify-sync";

export default function Page({ params }: { params: Promise<{ name: string }> }) {
  const { name } = use(params);
  const decodedName = decodeURIComponent(name);

  const [listing, setListing] = useState<ShopifyListingDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setListing(null);
    setError(null);

    fetchListingDetail(decodedName)
      .then((result) => {
        if (!cancelled) setListing(result);
      })
      .catch((err) => {
        if (cancelled) return;
        const message = shopifyErrorMessage(err, "Could not load this listing.");
        setError(message);
        toast.error(message);
      });

    return () => {
      cancelled = true;
    };
  }, [decodedName]);

  return (
    <div className="flex flex-col gap-4">
      <PageHeader
        title={listing?.listing_title || decodedName}
        subtitle={listing?.item ? `Item: ${listing.item}` : undefined}
        action={
          <Link href="/os/channels/shopify/listings" className="flex items-center gap-1 text-muted-foreground text-sm hover:text-foreground">
            <ArrowLeft className="size-4" /> Back to Listings
          </Link>
        }
      />

      {error ? (
        <Card>
          <CardContent className="p-4 text-muted-foreground text-sm">{error}</CardContent>
        </Card>
      ) : listing === null ? (
        <Card>
          <CardContent className="p-4">
            <Skeleton className="h-48 w-full" />
          </CardContent>
        </Card>
      ) : (
        <>
          <Card>
            <CardHeader className="grid grid-cols-2 gap-4 border-b md:grid-cols-4">
              <Field label="Status">
                <Badge variant="outline" className={cn("border-0 font-medium", getListingStatusBadgeClass(listing.sh_shopify_status))}>
                  {listing.sh_shopify_status || "Active"}
                </Badge>
              </Field>
              <Field label="Enabled">
                <Badge variant={listing.is_enabled ? "outline" : "secondary"}>{listing.is_enabled ? "Enabled" : "Disabled"}</Badge>
              </Field>
              <Field label="Price">{listing.listing_price != null ? listing.listing_price.toFixed(2) : "—"}</Field>
              <Field label="Shopify Product ID">
                <span className="font-mono text-xs">{listing.sh_shopify_product_id || "—"}</span>
              </Field>
              <Field label="Last synced">
                {listing.last_synced_at ? new Date(listing.last_synced_at).toLocaleString() : "—"}
              </Field>
              <Field label="Category">{listing.listing_category || "—"}</Field>
              <Field label="Product type">{listing.listing_product_type || "—"}</Field>
            </CardHeader>
            <CardContent className="grid gap-4 pt-4 md:grid-cols-2">
              <Field label="SEO title">{listing.listing_seo_title || "—"}</Field>
              <Field label="SEO description">{listing.listing_seo_description || "—"}</Field>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="border-b font-medium text-sm">Images ({listing.images.length})</CardHeader>
            <CardContent className="pt-4">
              {listing.images.length === 0 ? (
                <p className="text-muted-foreground text-sm">No images.</p>
              ) : (
                <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 md:grid-cols-6">
                  {listing.images
                    .slice()
                    .sort((a, b) => (a.sort_order ?? 0) - (b.sort_order ?? 0))
                    .map((row) => (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img key={row.name} src={row.image} alt={row.source ?? ""} className="aspect-square w-full rounded-md border object-cover" />
                    ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="gap-0">
            <CardHeader className="border-b font-medium text-sm">Variants ({listing.variants.length})</CardHeader>
            <CardContent className="px-0">
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Item variant</TableHead>
                      <TableHead>Enabled</TableHead>
                      <TableHead className="text-right">Price</TableHead>
                      <TableHead>Shopify Variant ID</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {listing.variants.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={4} className="h-24 text-center text-muted-foreground">
                          No variants.
                        </TableCell>
                      </TableRow>
                    ) : (
                      listing.variants.map((row) => (
                        <TableRow key={row.name}>
                          <TableCell className="font-medium">{row.item_variant}</TableCell>
                          <TableCell>
                            <Badge variant={row.is_enabled ? "outline" : "secondary"}>{row.is_enabled ? "Enabled" : "Disabled"}</Badge>
                          </TableCell>
                          <TableCell className="text-right tabular-nums">
                            {row.variant_price != null ? row.variant_price.toFixed(2) : <span className="text-muted-foreground">—</span>}
                          </TableCell>
                          <TableCell className="font-mono text-xs">
                            {row.sh_shopify_variant_id || <span className="text-muted-foreground">—</span>}
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>

          <Card className="gap-0">
            <CardHeader className="border-b font-medium text-sm">Metafields ({listing.metafields.length})</CardHeader>
            <CardContent className="px-0">
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Namespace</TableHead>
                      <TableHead>Key</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Value</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {listing.metafields.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={4} className="h-24 text-center text-muted-foreground">
                          No metafields.
                        </TableCell>
                      </TableRow>
                    ) : (
                      listing.metafields.map((row) => (
                        <TableRow key={row.name}>
                          <TableCell className="text-muted-foreground">{row.namespace || "—"}</TableCell>
                          <TableCell className="font-medium">{row.key}</TableCell>
                          <TableCell>{row.type || "—"}</TableCell>
                          <TableCell className="max-w-96 truncate" title={row.value ?? undefined}>
                            {row.value || "—"}
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1">
      <span className="text-muted-foreground text-xs">{label}</span>
      <span className="text-sm">{children}</span>
    </div>
  );
}
