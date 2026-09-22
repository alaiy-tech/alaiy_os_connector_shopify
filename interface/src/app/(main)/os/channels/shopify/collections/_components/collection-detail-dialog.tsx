"use client";

import { useEffect, useState } from "react";

import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@alaiy-os/ui/dialog";
import { Label } from "@alaiy-os/ui/label";
import { Skeleton } from "@alaiy-os/ui/skeleton";
import { Switch } from "@alaiy-os/ui/switch";
import { toast } from "sonner";

import { shopifyErrorMessage } from "@/lib/frappe/shopify-sync";
import {
  type CollectionChannel,
  type CollectionProduct,
  fetchCollectionChannels,
  fetchCollectionProducts,
  toggleCollectionChannel,
} from "@/lib/frappe/shopify-collections";

/**
 * Product list + per-channel publish toggles for one Shopify Collection.
 * Both lists are live-fetched from Shopify on open (see collections.py) —
 * not stored locally, so they're re-fetched every time the dialog opens.
 */
export function CollectionDetailDialog({
  collectionName,
  collectionTitle,
  open,
  onOpenChange,
}: {
  collectionName: string;
  collectionTitle: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const [products, setProducts] = useState<CollectionProduct[] | null>(null);
  const [channels, setChannels] = useState<CollectionChannel[] | null>(null);
  const [togglingId, setTogglingId] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    let cancelled = false;
    setProducts(null);
    setChannels(null);
    fetchCollectionProducts(collectionName)
      .then((rows) => !cancelled && setProducts(rows))
      .catch((err) => !cancelled && toast.error(shopifyErrorMessage(err, "Could not load products.")));
    fetchCollectionChannels(collectionName)
      .then((rows) => !cancelled && setChannels(rows))
      .catch((err) => !cancelled && toast.error(shopifyErrorMessage(err, "Could not load channels.")));
    return () => {
      cancelled = true;
    };
  }, [open, collectionName]);

  async function toggle(channel: CollectionChannel, nextPublished: boolean) {
    if (!channel.publication_id) return;
    setTogglingId(channel.publication_id);
    // Optimistic update, rolled back on failure.
    setChannels((prev) =>
      prev?.map((c) => (c.publication_id === channel.publication_id ? { ...c, published: nextPublished } : c)) ?? prev,
    );
    try {
      const result = await toggleCollectionChannel(collectionName, channel.publication_id, nextPublished);
      if (!result.ok) throw new Error(result.error ?? "Toggle failed.");
      toast.success(`${channel.name}: ${nextPublished ? "published" : "unpublished"}.`);
    } catch (error) {
      setChannels((prev) =>
        prev?.map((c) => (c.publication_id === channel.publication_id ? { ...c, published: !nextPublished } : c)) ?? prev,
      );
      toast.error(shopifyErrorMessage(error, "Could not update the channel."));
    } finally {
      setTogglingId(null);
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>{collectionTitle}</DialogTitle>
          <DialogDescription>Products in this collection and the sales channels it's published to.</DialogDescription>
        </DialogHeader>

        <div className="flex flex-col gap-6">
          <div>
            <h3 className="mb-2 text-sm font-medium">Products</h3>
            {products === null ? (
              <Skeleton className="h-24 w-full" />
            ) : products.length === 0 ? (
              <p className="text-muted-foreground text-sm">No products in this collection.</p>
            ) : (
              <div className="flex max-h-64 flex-col gap-2 overflow-y-auto">
                {products.map((product, i) => (
                  // biome-ignore lint/suspicious/noArrayIndexKey: no stable id on this live-fetched, non-persisted shape
                  <div key={i} className="flex items-center gap-3 rounded-lg border p-2">
                    {product.image ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img src={product.image} alt={product.title ?? ""} className="h-10 w-10 rounded object-cover" />
                    ) : (
                      <div className="bg-muted h-10 w-10 rounded" />
                    )}
                    <div className="flex min-w-0 flex-1 flex-col">
                      <span className="truncate text-sm font-medium">{product.title}</span>
                      <span className="text-muted-foreground truncate text-xs">{product.sku}</span>
                    </div>
                    <span className="text-sm tabular-nums">{product.price ? `$${product.price}` : "—"}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div>
            <h3 className="mb-2 text-sm font-medium">Sales channels</h3>
            {channels === null ? (
              <Skeleton className="h-24 w-full" />
            ) : channels.length === 0 ? (
              <p className="text-muted-foreground text-sm">No sales channels found.</p>
            ) : (
              <div className="flex flex-col gap-2">
                {channels.map((channel) => (
                  <div key={channel.publication_id} className="flex items-center justify-between rounded-lg border p-3">
                    <Label htmlFor={`channel-${channel.publication_id}`}>{channel.name}</Label>
                    <Switch
                      id={`channel-${channel.publication_id}`}
                      checked={channel.published}
                      disabled={togglingId === channel.publication_id}
                      onCheckedChange={(v) => void toggle(channel, v)}
                    />
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
