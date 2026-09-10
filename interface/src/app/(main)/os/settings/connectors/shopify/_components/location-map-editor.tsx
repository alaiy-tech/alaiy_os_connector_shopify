"use client";

import { Button } from "@alaiy-os/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@alaiy-os/ui/table";
import { Plus, Trash2 } from "lucide-react";

import { LinkField } from "./link-field";

export type LocationMapRow = {
  warehouse: string;
  shopify_location: string;
};

/**
 * Editor for `sh_location_map` (child table "Shopify Location Map"): maps
 * Alaiy OS Warehouses to Shopify Locations for multi-location inventory sync.
 * Value shape on save is the standard Frappe Table convention -- an array of
 * plain row objects keyed by the child doctype's fieldnames, no `name`/`parent`.
 */
export function LocationMapEditor({
  rows,
  onChange,
  disabled,
}: {
  rows: LocationMapRow[];
  onChange: (rows: LocationMapRow[]) => void;
  disabled?: boolean;
}) {
  function updateRow(index: number, patch: Partial<LocationMapRow>) {
    onChange(rows.map((row, i) => (i === index ? { ...row, ...patch } : row)));
  }

  function addRow() {
    onChange([...rows, { warehouse: "", shopify_location: "" }]);
  }

  function removeRow(index: number) {
    onChange(rows.filter((_, i) => i !== index));
  }

  return (
    <div className="space-y-3">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Alaiy OS Warehouse</TableHead>
            <TableHead>Shopify Location</TableHead>
            <TableHead className="w-10" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.length === 0 && (
            <TableRow>
              <TableCell colSpan={3} className="text-muted-foreground text-sm">
                No mappings yet -- single-location mode (Default Warehouse only).
              </TableCell>
            </TableRow>
          )}
          {rows.map((row, index) => (
            // biome-ignore lint/suspicious/noArrayIndexKey: rows have no stable id until saved
            <TableRow key={index}>
              <TableCell>
                <LinkField
                  doctype="Warehouse"
                  value={row.warehouse}
                  onChange={(v) => updateRow(index, { warehouse: v })}
                  disabled={disabled}
                />
              </TableCell>
              <TableCell>
                <LinkField
                  doctype="Shopify Location"
                  value={row.shopify_location}
                  onChange={(v) => updateRow(index, { shopify_location: v })}
                  disabled={disabled}
                />
              </TableCell>
              <TableCell>
                <Button
                  variant="ghost"
                  size="icon"
                  disabled={disabled}
                  onClick={() => removeRow(index)}
                  aria-label="Remove mapping"
                >
                  <Trash2 />
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <Button variant="outline" size="sm" onClick={addRow} disabled={disabled}>
        <Plus /> Add mapping
      </Button>
    </div>
  );
}
