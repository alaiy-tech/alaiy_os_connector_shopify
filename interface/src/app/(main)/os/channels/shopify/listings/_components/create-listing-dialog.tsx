"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Button } from "@alaiy-os/ui/button";
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@alaiy-os/ui/command";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@alaiy-os/ui/dialog";
import { Label } from "@alaiy-os/ui/label";
import { Popover, PopoverContent, PopoverTrigger } from "@alaiy-os/ui/popover";
import { cn } from "@alaiy-os/utils";
import { Check, ChevronsUpDown, Plus } from "lucide-react";
import { toast } from "sonner";

import { createListing } from "@/lib/frappe/shopify-listing-create";
import { searchItemsWithoutListing } from "@/lib/frappe/shopify-item-picker";
import { shopifyErrorMessage } from "@/lib/frappe/shopify-sync";

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
            <UnlistedItemPicker value={item} onChange={setItem} disabled={busy} />
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

const SEARCH_DEBOUNCE_MS = 300;

/** Item picker scoped to this store: template/simple Items only, not already
 * listed -- see item_without_listing_query for why a bare Item LinkField
 * would be wrong here (offers variants, already-listed Items, and on a
 * multi-store bench, other sellers' Items). */
function UnlistedItemPicker({
  value,
  onChange,
  disabled,
}: {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}) {
  const [open, setOpen] = useState(false);
  const [term, setTerm] = useState("");
  const [options, setOptions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!open) return;
    let cancelled = false;
    setLoading(true);

    const timeout = setTimeout(() => {
      searchItemsWithoutListing(term)
        .then((results) => {
          if (!cancelled) setOptions(results);
        })
        .catch(() => {
          if (!cancelled) setOptions([]);
        })
        .finally(() => {
          if (!cancelled) setLoading(false);
        });
    }, SEARCH_DEBOUNCE_MS);

    return () => {
      cancelled = true;
      clearTimeout(timeout);
    };
  }, [term, open]);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          disabled={disabled}
          aria-expanded={open}
          className={cn("h-8 w-full justify-between font-normal", !value && "text-muted-foreground")}
        >
          <span className="truncate">{value || "Pick an Item"}</span>
          <ChevronsUpDown className="opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-(--radix-popover-trigger-width) p-0" align="start">
        <Command shouldFilter={false}>
          <CommandInput placeholder="Search items..." value={term} onValueChange={setTerm} />
          <CommandList>
            <CommandEmpty>{loading ? "Searching..." : "No unlisted items found."}</CommandEmpty>
            <CommandGroup>
              {options.map((option) => (
                <CommandItem
                  key={option}
                  value={option}
                  onSelect={() => {
                    onChange(option);
                    setOpen(false);
                  }}
                >
                  <Check className={cn("size-3.5", option === value ? "opacity-100" : "opacity-0")} />
                  {option}
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
