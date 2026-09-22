"use client";

import { use, useEffect, useState } from "react";

import { useRouter } from "next/navigation";
import Link from "next/link";

import { PageHeader } from "@alaiy-os/layout/page-header";

import { Badge } from "@alaiy-os/ui/badge";
import { Button } from "@alaiy-os/ui/button";
import { Card, CardContent, CardHeader } from "@alaiy-os/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@alaiy-os/ui/dialog";
import { Input } from "@alaiy-os/ui/input";
import { Label } from "@alaiy-os/ui/label";
import { Skeleton } from "@alaiy-os/ui/skeleton";
import { cn } from "@alaiy-os/utils";
import { ArrowLeft, Loader2, Trash2, Wand2 } from "lucide-react";
import { toast } from "sonner";

import { getListingStatusBadgeClass } from "@/constants/shopify";
import {
  deleteListing,
  fetchEffectiveValues,
  fetchItemChildren,
  fetchListingDetail,
  saveListing,
  type ShopifyListingDetail,
  type ShopifyListingEffectiveValues,
} from "@/lib/frappe/shopify-listing-detail";
import { shopifyErrorMessage } from "@/lib/frappe/shopify-sync";

import { LinkField } from "../../../../settings/connectors/shopify/_components/link-field";
import { ImagesEditor } from "./_components/images-editor";
import { MetafieldsEditor } from "./_components/metafields-editor";
import { VariantsEditor } from "./_components/variants-editor";

export default function Page({ params }: { params: Promise<{ name: string }> }) {
  const { name } = use(params);
  const decodedName = decodeURIComponent(name);
  const router = useRouter();

  const [listing, setListing] = useState<ShopifyListingDetail | null>(null);
  const [effective, setEffective] = useState<ShopifyListingEffectiveValues>({});
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [populating, setPopulating] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setListing(null);
    setError(null);

    fetchListingDetail(decodedName)
      .then((result) => {
        if (cancelled) return;
        setListing(result);
        // Best-effort: the resolved-values preview is a nice-to-have hint,
        // not something that should block the page on failure.
        fetchEffectiveValues(decodedName)
          .then((values) => !cancelled && setEffective(values))
          .catch(() => {});
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

  function set<K extends keyof ShopifyListingDetail>(key: K, value: ShopifyListingDetail[K]) {
    setListing((prev) => (prev ? { ...prev, [key]: value } : prev));
  }

  async function handleSave() {
    if (!listing) return;
    setSaving(true);
    try {
      const patch = {
        listing_title: listing.listing_title || "",
        listing_description: listing.listing_description || "",
        listing_price: listing.listing_price,
        listing_category: listing.listing_category || "",
        listing_product_type: listing.listing_product_type || "",
        listing_seo_title: listing.listing_seo_title || "",
        listing_seo_description: listing.listing_seo_description || "",
        images: listing.images.map(({ name: rowName, image, source, sort_order, generated_by_agent }) => ({
          ...(rowName ? { name: rowName } : {}),
          image,
          source,
          sort_order,
          generated_by_agent,
        })),
        variants: listing.variants.map(
          ({ name: rowName, item_variant, is_enabled, variant_price, variant_image, sh_shopify_variant_id }) => ({
            ...(rowName ? { name: rowName } : {}),
            item_variant,
            is_enabled,
            variant_price,
            variant_image,
            sh_shopify_variant_id,
          }),
        ),
        metafields: listing.metafields.map(({ name: rowName, namespace, key, type, value }) => ({
          ...(rowName ? { name: rowName } : {}),
          namespace,
          key,
          type,
          value,
        })),
      };
      const saved = await saveListing(decodedName, patch);
      setListing(saved);
      toast.success("Listing saved.");
      fetchEffectiveValues(decodedName)
        .then(setEffective)
        .catch(() => {});
    } catch (error) {
      toast.error(shopifyErrorMessage(error, "Could not save the listing."));
    } finally {
      setSaving(false);
    }
  }

  async function handlePopulateFromItem() {
    if (!listing) return;
    setPopulating(true);
    try {
      const data = await fetchItemChildren(listing.item);
      setListing((prev) =>
        prev
          ? {
              ...prev,
              images: data.images.map((row) => ({ name: null, image: row.image, source: row.source, sort_order: row.sort_order })),
              variants: data.variants.map((row) => ({
                name: null,
                item_variant: row.item_variant,
                is_enabled: row.is_enabled,
                variant_price: row.variant_price,
                variant_image: row.variant_image,
                sh_shopify_variant_id: row.sh_shopify_variant_id,
              })),
              listing_category: data.listing_category ?? prev.listing_category,
              listing_product_type: data.listing_product_type ?? prev.listing_product_type,
            }
          : prev,
      );
      toast.success("Replaced images, variants, category and product type from the Item. Review and Save to apply.");
    } catch (error) {
      toast.error(shopifyErrorMessage(error, "Could not load the Item's current data."));
    } finally {
      setPopulating(false);
    }
  }

  async function handleDelete() {
    setDeleting(true);
    try {
      await deleteListing(decodedName);
      toast.success("Listing deleted.");
      router.push("/os/channels/shopify/listings");
    } catch (error) {
      toast.error(shopifyErrorMessage(error, "Could not delete the listing."));
      setDeleting(false);
    }
  }

  const simpleProduct = !listing || listing.variants.length <= 1;

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
              <Field label="Shopify Product ID">
                <span className="font-mono text-xs">{listing.sh_shopify_product_id || "—"}</span>
              </Field>
              <Field label="Last synced">{listing.last_synced_at ? new Date(listing.last_synced_at).toLocaleString() : "—"}</Field>
            </CardHeader>
            <CardContent className="grid gap-5 pt-4 md:grid-cols-2">
              <EditableField label="Title" hint={effective.title}>
                <Input value={listing.listing_title ?? ""} onChange={(e) => set("listing_title", e.target.value)} disabled={saving} />
              </EditableField>

              {simpleProduct && (
                <EditableField label="Price" hint="the Item Price on the connector's selling price list">
                  <Input
                    type="number"
                    step="0.01"
                    value={listing.listing_price ?? ""}
                    disabled={saving}
                    onChange={(e) => set("listing_price", e.target.value === "" ? null : Number(e.target.value))}
                  />
                </EditableField>
              )}

              <EditableField label="Category" hint={effective.category}>
                <LinkField
                  doctype="Shopify Category"
                  value={listing.listing_category ?? ""}
                  onChange={(v) => set("listing_category", v)}
                  disabled={saving}
                />
              </EditableField>

              <EditableField label="Product type" hint={effective.product_type}>
                <Input
                  value={listing.listing_product_type ?? ""}
                  onChange={(e) => set("listing_product_type", e.target.value)}
                  disabled={saving}
                />
              </EditableField>

              <EditableField label="SEO title" hint={effective.seo_title}>
                <Input value={listing.listing_seo_title ?? ""} onChange={(e) => set("listing_seo_title", e.target.value)} disabled={saving} />
              </EditableField>

              <EditableField label="SEO description" hint={effective.seo_description}>
                <textarea
                  className="min-h-20 w-full rounded-md border bg-transparent px-3 py-2 text-sm shadow-xs"
                  value={listing.listing_seo_description ?? ""}
                  disabled={saving}
                  onChange={(e) => set("listing_seo_description", e.target.value)}
                />
              </EditableField>

              <EditableField label="Description" hint={effective.description} className="md:col-span-2">
                <textarea
                  className="min-h-32 w-full rounded-md border bg-transparent px-3 py-2 text-sm shadow-xs"
                  value={listing.listing_description ?? ""}
                  disabled={saving}
                  onChange={(e) => set("listing_description", e.target.value)}
                />
              </EditableField>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between border-b font-medium text-sm">
              Images ({listing.images.length})
              <Button variant="outline" size="sm" onClick={() => void handlePopulateFromItem()} disabled={populating || saving}>
                {populating ? <Loader2 className="animate-spin" /> : <Wand2 />} Populate from Item
              </Button>
            </CardHeader>
            <CardContent className="pt-4">
              <ImagesEditor rows={listing.images} onChange={(images) => set("images", images)} disabled={saving} />
            </CardContent>
          </Card>

          <Card className="gap-0">
            <CardHeader className="border-b font-medium text-sm">Variants ({listing.variants.length})</CardHeader>
            <CardContent className="pt-4">
              <VariantsEditor rows={listing.variants} onChange={(variants) => set("variants", variants)} disabled={saving} />
            </CardContent>
          </Card>

          <Card className="gap-0">
            <CardHeader className="border-b font-medium text-sm">Metafields ({listing.metafields.length})</CardHeader>
            <CardContent className="pt-4">
              <MetafieldsEditor rows={listing.metafields} onChange={(metafields) => set("metafields", metafields)} disabled={saving} />
            </CardContent>
          </Card>

          <div className="flex items-center justify-between gap-2">
            <Button variant="destructive" onClick={() => setConfirmDelete(true)} disabled={saving || deleting}>
              <Trash2 /> Delete listing
            </Button>
            <Button onClick={() => void handleSave()} disabled={saving}>
              {saving && <Loader2 className="animate-spin" />} Save
            </Button>
          </div>

          <Dialog open={confirmDelete} onOpenChange={setConfirmDelete}>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Delete this listing?</DialogTitle>
                <DialogDescription>
                  {listing.sh_shopify_product_id
                    ? "This archives the product on Shopify (hidden, order history kept intact) and removes this listing from Alaiy OS. This cannot be undone."
                    : "This listing hasn't been pushed to Shopify yet. Deleting it only removes it from Alaiy OS. This cannot be undone."}
                </DialogDescription>
              </DialogHeader>
              <DialogFooter>
                <Button variant="outline" onClick={() => setConfirmDelete(false)} disabled={deleting}>
                  Cancel
                </Button>
                <Button variant="destructive" onClick={() => void handleDelete()} disabled={deleting}>
                  {deleting && <Loader2 className="animate-spin" />} Delete
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
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

function EditableField({
  label,
  hint,
  className,
  children,
}: {
  label: string;
  hint?: string;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <div className={cn("space-y-1.5", className)}>
      <Label>{label}</Label>
      {children}
      {hint ? <p className="text-muted-foreground text-xs">Blank uses: {hint}</p> : null}
    </div>
  );
}
