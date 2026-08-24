"use client";

import { useRef } from "react";

import { Button } from "@alaiy-os/ui/button";
import { Input } from "@alaiy-os/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@alaiy-os/ui/select";
import { ArrowDown, ArrowUp, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { uploadPrivateFile } from "@/lib/frappe/shopify-sync";
import type { ShopifyListingImage } from "@/lib/frappe/shopify-listing-detail";

const SOURCE_OPTIONS = ["Original", "AI Enhanced"];

/**
 * Editor for the Listing's `images` child table (Shopify Listing Image:
 * image / source / sort_order / generated_by_agent). Reorder is plain
 * up/down swap of `sort_order` -- no drag-and-drop dependency needed for
 * a handful of product images. `generated_by_agent` is traceability set by
 * an OS Agent Run, never hand-edited here.
 */
export function ImagesEditor({
  rows,
  onChange,
  disabled,
}: {
  rows: ShopifyListingImage[];
  onChange: (rows: ShopifyListingImage[]) => void;
  disabled?: boolean;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const sorted = rows.slice().sort((a, b) => (a.sort_order ?? 0) - (b.sort_order ?? 0));

  function withReindexedOrder(next: ShopifyListingImage[]) {
    onChange(next.map((row, i) => ({ ...row, sort_order: i })));
  }

  function move(index: number, delta: number) {
    const target = index + delta;
    if (target < 0 || target >= sorted.length) return;
    const next = sorted.slice();
    [next[index], next[target]] = [next[target], next[index]];
    withReindexedOrder(next);
  }

  function updateRow(index: number, patch: Partial<ShopifyListingImage>) {
    withReindexedOrder(sorted.map((row, i) => (i === index ? { ...row, ...patch } : row)));
  }

  function removeRow(index: number) {
    withReindexedOrder(sorted.filter((_, i) => i !== index));
  }

  async function addRow(file: File) {
    try {
      const url = await uploadPrivateFile(file);
      withReindexedOrder([...sorted, { name: null, image: url, source: "Original", sort_order: sorted.length }]);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Could not upload the image.");
    }
  }

  return (
    <div className="space-y-3">
      {sorted.length === 0 ? (
        <p className="text-muted-foreground text-sm">No images.</p>
      ) : (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 md:grid-cols-6">
          {sorted.map((row, index) => (
            // biome-ignore lint/suspicious/noArrayIndexKey: rows have no stable id until saved
            <div key={index} className="flex flex-col gap-1 rounded-md border p-2">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={row.image} alt={row.source ?? ""} className="aspect-square w-full rounded-md object-cover" />
              <Select value={row.source ?? "Original"} onValueChange={(v) => updateRow(index, { source: v })} disabled={disabled}>
                <SelectTrigger size="sm" className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {SOURCE_OPTIONS.map((option) => (
                    <SelectItem key={option} value={option}>
                      {option}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <div className="flex items-center justify-between">
                <div className="flex">
                  <Button variant="ghost" size="icon" className="size-7" disabled={disabled || index === 0} onClick={() => move(index, -1)} aria-label="Move earlier">
                    <ArrowUp />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="size-7"
                    disabled={disabled || index === sorted.length - 1}
                    onClick={() => move(index, 1)}
                    aria-label="Move later"
                  >
                    <ArrowDown />
                  </Button>
                </div>
                <Button variant="ghost" size="icon" className="size-7" disabled={disabled} onClick={() => removeRow(index)} aria-label="Remove image">
                  <Trash2 />
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="flex items-center gap-2">
        <Input
          ref={inputRef}
          type="file"
          accept="image/*"
          className="hidden"
          disabled={disabled}
          onChange={(e) => {
            const file = e.target.files?.[0];
            e.target.value = "";
            if (file) void addRow(file);
          }}
        />
        <Button variant="outline" size="sm" disabled={disabled} onClick={() => inputRef.current?.click()}>
          <Plus /> Add image
        </Button>
      </div>
    </div>
  );
}
