"use client";

import { useCallback, useEffect, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

import { fetchShopifyStores, type ShopifyStore } from "@/lib/frappe/shopify-store";

/**
 * Which Shopify store every Shopify page/component call is about.
 *
 * Backed by the `?connection=` URL param (not component state) so a
 * deep-linked or shared page keeps the right store on reload. Hidden UI
 * (the switcher renders nothing) when there's zero or one store, matching
 * the legacy Desk page's "no dropdown noise on a single-store bench" rule.
 */
export function useShopifyStore() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const [stores, setStores] = useState<ShopifyStore[]>([]);
  const [loading, setLoading] = useState(true);

  const fromUrl = searchParams.get("connection");

  useEffect(() => {
    let cancelled = false;
    fetchShopifyStores()
      .then((result) => {
        if (cancelled) return;
        setStores(result.connections);
        // No store named in the URL yet, and the backend can resolve one on
        // its own (exactly one enabled store) -- adopt it so the URL becomes
        // shareable/reload-safe from the first render, same as picking one
        // by hand would.
        if (!fromUrl && result.selected) {
          const params = new URLSearchParams(searchParams);
          params.set("connection", result.selected);
          router.replace(`${pathname}?${params.toString()}`, { scroll: false });
        }
      })
      .catch(() => {
        if (!cancelled) setStores([]);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
    // Runs once per mount -- store list rarely changes mid-session, and
    // re-fetching on every URL change would refetch on the very navigation
    // this effect itself triggers.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const setSelected = useCallback(
    (name: string) => {
      const params = new URLSearchParams(searchParams);
      params.set("connection", name);
      router.replace(`${pathname}?${params.toString()}`, { scroll: false });
    },
    [router, pathname, searchParams],
  );

  return { stores, selected: fromUrl, setSelected, loading };
}
