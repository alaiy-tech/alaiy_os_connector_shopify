"use client";

import { useEffect, useState } from "react";

import { Card, CardContent } from "@alaiy-os/ui/card";
import { Skeleton } from "@alaiy-os/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@alaiy-os/ui/table";
import { toast } from "sonner";

import { shopifyErrorMessage } from "@/lib/frappe/shopify-sync";

export interface ResourceColumn<T> {
  header: string;
  align?: "left" | "right";
  render: (row: T) => React.ReactNode;
}

/**
 * A single read-only table for one of the simple Shopify masters
 * (Category, Collection, Location, Tag) — no filtering, sorting, or
 * pagination, because none of these lists run into the thousands the way
 * Listings does. If one ever does, promote it to the full list-page
 * pattern in DESIGN.md instead of bolting features onto this.
 */
export function SimpleResourceTable<T extends Record<string, unknown>>({
  load,
  columns,
  emptyMessage,
  rowKey,
}: {
  load: () => Promise<T[]>;
  columns: ResourceColumn<T>[];
  emptyMessage: string;
  rowKey: (row: T) => string;
}) {
  const [rows, setRows] = useState<T[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    load()
      .then((result) => {
        if (!cancelled) setRows(result);
      })
      .catch((err) => {
        if (cancelled) return;
        const message = shopifyErrorMessage(err, "Could not load this list.");
        setError(message);
        toast.error(message);
      });
    return () => {
      cancelled = true;
    };
    // `load` is a fresh closure per render by design (it captures the doctype/fields for this page);
    // re-running on every render would loop, so this intentionally only runs once per mount.
    // biome-ignore lint/correctness/useExhaustiveDependencies: see above
  }, []);

  if (error) {
    return <p className="text-muted-foreground text-sm">{error}</p>;
  }

  return (
    <Card className="gap-0">
      <CardContent className="px-0">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                {columns.map((col) => (
                  <TableHead key={col.header} className={col.align === "right" ? "text-right" : undefined}>
                    {col.header}
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {rows === null ? (
                <TableRow>
                  <TableCell colSpan={columns.length} className="p-4">
                    <Skeleton className="h-24 w-full" />
                  </TableCell>
                </TableRow>
              ) : rows.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={columns.length} className="h-24 text-center text-muted-foreground">
                    {emptyMessage}
                  </TableCell>
                </TableRow>
              ) : (
                rows.map((row) => (
                  <TableRow key={rowKey(row)}>
                    {columns.map((col) => (
                      <TableCell key={col.header} className={col.align === "right" ? "text-right tabular-nums" : undefined}>
                        {col.render(row)}
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
