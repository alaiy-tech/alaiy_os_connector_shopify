"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@alaiy-os/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@alaiy-os/ui/dialog";
import { Label } from "@alaiy-os/ui/label";
import { Plus } from "lucide-react";
import { toast } from "sonner";

import { createListing } from "@/lib/frappe/shopify-listing-create";
import { shopifyErrorMessage } from "@/lib/frappe/shopify-sync";

import { LinkField } from "../../../../settings/connectors/shopify/_components/link-field";

/**
 * Manual "+ New" for Shopify Product Listing -- Desk's generic list view
 * always had this (create: 1 in the doctype, item is the only required
 * field); the custom table replaced that list view without an equivalent.
 */
export function CreateListingDialog() {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [item, setItem] = useState("");
  const [busy, setBusy] = useState(false);

  function handleOpenChange(next: boolean) {
    if (next) setItem("");
    setOpen(next);
  }

  async function create() {
    if (!item) {
      toast.warning("Pick an Item first.");
      return;
    }
    setBusy(true);
    try {
      const { name } = await createListing(item);
      toast.success("Listing created.");
      setOpen(false);
      router.push(`/os/channels/shopify/listings/${encodeURIComponent(name)}`);
    } catch (error) {
      toast.error(shopifyErrorMessage(error, "Could not create the listing."));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <Button size="sm" onClick={() => handleOpenChange(true)}>
        <Plus /> New Listing
      </Button>
      <Dialog open={open} onOpenChange={handleOpenChange}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>New Shopify Listing</DialogTitle>
            <DialogDescription>
              Creates a listing row for an Item that isn't synced from Shopify yet. Everything else (title, price,
              images) fills in the next time this listing syncs.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-2">
            <Label>Item</Label>
            <LinkField doctype="Item" value={item} onChange={setItem} disabled={busy} />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)} disabled={busy}>
              Cancel
            </Button>
            <Button onClick={() => void create()} disabled={busy}>
              Create
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
