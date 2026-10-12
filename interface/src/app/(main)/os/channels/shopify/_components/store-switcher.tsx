"use client";

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@alaiy-os/ui/select";
import { Store } from "lucide-react";

import { useShopifyStore } from "../_lib/use-shopify-store";

/**
 * Store picker for the Shopify connector's screens. Renders nothing on a
 * single-store bench (or before the store list loads) -- a dropdown of one
 * is noise, matching the legacy Desk page's picker.
 */
export function StoreSwitcher() {
  const { stores, selected, setSelected, loading } = useShopifyStore();

  if (loading || stores.length <= 1) return null;

  return (
    <Select value={selected ?? undefined} onValueChange={setSelected}>
      <SelectTrigger className="w-[220px]">
        <Store className="size-3.5" />
        <SelectValue placeholder="Choose a store…" />
      </SelectTrigger>
      <SelectContent>
        {stores.map((store) => (
          <SelectItem key={store.name} value={store.name}>
            {store.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
