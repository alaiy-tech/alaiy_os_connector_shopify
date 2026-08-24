"use client";

import { Button } from "@alaiy-os/ui/button";
import { Input } from "@alaiy-os/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@alaiy-os/ui/table";
import { Plus, Trash2 } from "lucide-react";

import type { ShopifyProductMetafield } from "@/lib/frappe/shopify-listing-detail";

/**
 * Editor for the Listing's `metafields` child table (Shopify Product
 * Metafield: namespace / key / type / value). Pushed back in full via
 * metafieldsSet on export (metafields.py:build_metafields_input) -- type
 * defaults to "single_line_text_field" server-side if left blank.
 */
export function MetafieldsEditor({
  rows,
  onChange,
  disabled,
}: {
  rows: ShopifyProductMetafield[];
  onChange: (rows: ShopifyProductMetafield[]) => void;
  disabled?: boolean;
}) {
  function updateRow(index: number, patch: Partial<ShopifyProductMetafield>) {
    onChange(rows.map((row, i) => (i === index ? { ...row, ...patch } : row)));
  }

  function addRow() {
    onChange([...rows, { name: null, namespace: "", key: "", type: "", value: "" }]);
  }

  function removeRow(index: number) {
    onChange(rows.filter((_, i) => i !== index));
  }

  return (
    <div className="space-y-3">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Namespace</TableHead>
            <TableHead>Key</TableHead>
            <TableHead>Type</TableHead>
            <TableHead>Value</TableHead>
            <TableHead className="w-10" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.length === 0 ? (
            <TableRow>
              <TableCell colSpan={5} className="h-24 text-center text-muted-foreground">
                No metafields.
              </TableCell>
            </TableRow>
          ) : (
            rows.map((row, index) => (
              // biome-ignore lint/suspicious/noArrayIndexKey: rows have no stable id until saved
              <TableRow key={index}>
                <TableCell>
                  <Input value={row.namespace} disabled={disabled} onChange={(e) => updateRow(index, { namespace: e.target.value })} />
                </TableCell>
                <TableCell>
                  <Input value={row.key} disabled={disabled} onChange={(e) => updateRow(index, { key: e.target.value })} />
                </TableCell>
                <TableCell>
                  <Input
                    placeholder="single_line_text_field"
                    value={row.type ?? ""}
                    disabled={disabled}
                    onChange={(e) => updateRow(index, { type: e.target.value })}
                  />
                </TableCell>
                <TableCell className="min-w-48">
                  <Input value={row.value ?? ""} disabled={disabled} onChange={(e) => updateRow(index, { value: e.target.value })} />
                </TableCell>
                <TableCell>
                  <Button variant="ghost" size="icon" disabled={disabled} onClick={() => removeRow(index)} aria-label="Remove metafield">
                    <Trash2 />
                  </Button>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
      <Button variant="outline" size="sm" onClick={addRow} disabled={disabled}>
        <Plus /> Add metafield
      </Button>
    </div>
  );
}
