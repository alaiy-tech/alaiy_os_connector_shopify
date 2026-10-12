"use client";

import { useEffect, useState } from "react";

import { Badge } from "@alaiy-os/ui/badge";
import { Button } from "@alaiy-os/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@alaiy-os/ui/dialog";
import { InputGroup, InputGroupAddon, InputGroupInput } from "@alaiy-os/ui/input-group";
import { Skeleton } from "@alaiy-os/ui/skeleton";
import { Download, Search } from "lucide-react";
import { toast } from "sonner";

import {
  type ShopifyProductSearchResult,
  importShopifyProduct,
  searchShopifyProducts,
  shopifyErrorMessage,
} from "@/lib/frappe/shopify-sync";

const SEARCH_DEBOUNCE_MS = 350;

/**
 * "Search for a product…" -- pull in exactly one Shopify product by title/SKU
 * instead of running a full or missing-only sweep to find it. Mirrors
 * search_shopify_products + import_shopify_product's own two-step design:
 * search returns lightweight matches, importing one is a second, separate
 * synchronous call.
 */
export function ProductSearchDialog({
  open,
  onOpenChange,
  connection,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  connection?: string;
}) {
  const [term, setTerm] = useState("");
  const [results, setResults] = useState<ShopifyProductSearchResult[] | null>(null);
  const [searching, setSearching] = useState(false);
  const [importingId, setImportingId] = useState<string | null>(null);

  useEffect(() => {
    const trimmed = term.trim();
    if (!trimmed) {
      setResults(null);
      setSearching(false);
      return;
    }
    let cancelled = false;
    setSearching(true);
    const timeout = setTimeout(() => {
      searchShopifyProducts(trimmed, connection)
        .then((rows) => {
          if (!cancelled) setResults(rows);
        })
        .catch((error) => {
          if (cancelled) return;
          setResults([]);
          toast.error(shopifyErrorMessage(error, "Could not search Shopify."));
        })
        .finally(() => {
          if (!cancelled) setSearching(false);
        });
    }, SEARCH_DEBOUNCE_MS);
    return () => {
      cancelled = true;
      clearTimeout(timeout);
    };
  }, [term, connection]);

  async function importProduct(result: ShopifyProductSearchResult) {
    setImportingId(result.product_id);
    try {
      const outcome = await importShopifyProduct(result.product_id, connection);
      toast.success(outcome.created ? `Imported ${result.title}.` : `${result.title}: ${outcome.reason}`);
    } catch (error) {
      toast.error(shopifyErrorMessage(error, "Could not import this product."));
    } finally {
      setImportingId(null);
    }
  }

  function handleOpenChange(next: boolean) {
    if (!next) {
      setTerm("");
      setResults(null);
    }
    onOpenChange(next);
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Search for a product</DialogTitle>
          <DialogDescription>Pull in one specific Shopify product by title or SKU, instead of running a full sweep.</DialogDescription>
        </DialogHeader>
        <InputGroup className="h-9">
          <InputGroupAddon>
            <Search className="size-4" />
          </InputGroupAddon>
          <InputGroupInput placeholder="Search Shopify products..." value={term} onChange={(e) => setTerm(e.target.value)} autoFocus />
        </InputGroup>
        <div className="flex max-h-80 flex-col gap-2 overflow-y-auto">
          {searching ? (
            <>
              <Skeleton className="h-14 w-full" />
              <Skeleton className="h-14 w-full" />
            </>
          ) : results === null ? (
            <p className="py-6 text-center text-muted-foreground text-sm">Start typing to search Shopify.</p>
          ) : results.length === 0 ? (
            <p className="py-6 text-center text-muted-foreground text-sm">No matches on Shopify.</p>
          ) : (
            results.map((result) => (
              <div key={result.product_id} className="flex items-center gap-3 rounded-md border p-2">
                <div className="flex size-12 shrink-0 items-center justify-center overflow-hidden rounded-md bg-muted">
                  {result.image && (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={result.image} alt="" className="h-full w-full object-cover" />
                  )}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate font-medium text-sm">{result.title}</p>
                  <div className="flex items-center gap-1.5">
                    <Badge variant="outline" className="border-0 bg-muted font-normal text-xs">
                      {result.status}
                    </Badge>
                    <span className="truncate text-muted-foreground text-xs">{result.handle}</span>
                  </div>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  disabled={importingId !== null}
                  onClick={() => void importProduct(result)}
                >
                  {importingId === result.product_id ? "Importing..." : <Download />}
                </Button>
              </div>
            ))
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
