"use client";

import { Fragment, useState } from "react";

import { Button } from "@alaiy-os/ui/button";
import { Input } from "@alaiy-os/ui/input";
import { Switch } from "@alaiy-os/ui/switch";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@alaiy-os/ui/table";
import { ChevronDown, ChevronRight, Plus, Trash2 } from "lucide-react";

import { LinkField } from "../../../../../settings/connectors/shopify/_components/link-field";
import type { ShopifyListingVariant } from "@/lib/frappe/shopify-listing-detail";
import { MetafieldsEditor } from "./metafields-editor";

/**
 * Editor for the Listing's `variants` child table (Shopify Listing Variant:
 * item_variant / is_enabled / variant_price / variant_image /
 * sh_shopify_variant_id / metafields). sh_shopify_variant_id is owned by the
 * connector (read_only in the doctype) -- shown, never editable. Metafields
 * are Shopify Variant Metafield rows, same shape as the product-level
 * MetafieldsEditor, so that same editor is reused per-variant.
 */
export function VariantsEditor({
  rows,
  onChange,
  disabled,
}: {
  rows: ShopifyListingVariant[];
  onChange: (rows: ShopifyListingVariant[]) => void;
  disabled?: boolean;
}) {
  const [expanded, setExpanded] = useState<Set<number>>(new Set());

  function updateRow(index: number, patch: Partial<ShopifyListingVariant>) {
    onChange(rows.map((row, i) => (i === index ? { ...row, ...patch } : row)));
  }

  function addRow() {
    onChange([
      ...rows,
      { name: null, item_variant: "", is_enabled: 1, variant_price: null, variant_image: null, sh_shopify_variant_id: null, metafields: [] },
    ]);
  }

  function removeRow(index: number) {
    onChange(rows.filter((_, i) => i !== index));
  }

  function toggleExpanded(index: number) {
    setExpanded((current) => {
      const copy = new Set(current);
      if (copy.has(index)) copy.delete(index);
      else copy.add(index);
      return copy;
    });
  }

  return (
    <div className="space-y-3">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-8" />
            <TableHead>Item variant</TableHead>
            <TableHead>Enabled</TableHead>
            <TableHead>Price override</TableHead>
            <TableHead>Image override</TableHead>
            <TableHead>Shopify Variant ID</TableHead>
            <TableHead className="w-10" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.length === 0 ? (
            <TableRow>
              <TableCell colSpan={7} className="h-24 text-center text-muted-foreground">
                No variants.
              </TableCell>
            </TableRow>
          ) : (
            rows.map((row, index) => (
              // biome-ignore lint/suspicious/noArrayIndexKey: rows have no stable id until saved
              <Fragment key={index}>
                <TableRow>
                  <TableCell>
                    <Button variant="ghost" size="icon" className="size-7" onClick={() => toggleExpanded(index)} aria-label="Toggle metafields">
                      {expanded.has(index) ? <ChevronDown className="size-3.5" /> : <ChevronRight className="size-3.5" />}
                    </Button>
                  </TableCell>
                  <TableCell className="min-w-48">
                    <LinkField doctype="Item" value={row.item_variant} onChange={(v) => updateRow(index, { item_variant: v })} disabled={disabled} />
                  </TableCell>
                  <TableCell>
                    <Switch
                      checked={Boolean(row.is_enabled)}
                      onCheckedChange={(v) => updateRow(index, { is_enabled: v ? 1 : 0 })}
                      disabled={disabled}
                    />
                  </TableCell>
                  <TableCell>
                    <Input
                      type="number"
                      step="0.01"
                      placeholder="Inherits Item Price"
                      value={row.variant_price ?? ""}
                      disabled={disabled}
                      onChange={(e) => updateRow(index, { variant_price: e.target.value === "" ? null : Number(e.target.value) })}
                    />
                  </TableCell>
                  <TableCell className="min-w-40">
                    <Input
                      placeholder="Uses product images"
                      value={row.variant_image ?? ""}
                      disabled={disabled}
                      onChange={(e) => updateRow(index, { variant_image: e.target.value || null })}
                    />
                  </TableCell>
                  <TableCell className="font-mono text-xs text-muted-foreground">{row.sh_shopify_variant_id || "—"}</TableCell>
                  <TableCell>
                    <Button variant="ghost" size="icon" disabled={disabled} onClick={() => removeRow(index)} aria-label="Remove variant">
                      <Trash2 />
                    </Button>
                  </TableCell>
                </TableRow>
                {expanded.has(index) && (
                  <TableRow>
                    <TableCell colSpan={7} className="bg-muted/30">
                      <p className="mb-2 text-muted-foreground text-xs">Metafields for this variant</p>
                      <MetafieldsEditor
                        rows={row.metafields ?? []}
                        onChange={(metafields) => updateRow(index, { metafields })}
                        disabled={disabled}
                      />
                    </TableCell>
                  </TableRow>
                )}
              </Fragment>
            ))
          )}
        </TableBody>
      </Table>
      <Button variant="outline" size="sm" onClick={addRow} disabled={disabled}>
        <Plus /> Add variant
      </Button>
    </div>
  );
}
