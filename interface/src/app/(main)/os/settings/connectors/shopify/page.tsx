"use client";

import { useEffect, useState } from "react";

import Link from "next/link";
import { useRouter } from "next/navigation";

import { PageHeader } from "@alaiy-os/layout/page-header";
import { Badge } from "@alaiy-os/ui/badge";
import { Button } from "@alaiy-os/ui/button";
import { Card, CardContent } from "@alaiy-os/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@alaiy-os/ui/dialog";
import { Input } from "@alaiy-os/ui/input";
import { Label } from "@alaiy-os/ui/label";
import { Skeleton } from "@alaiy-os/ui/skeleton";
import { Plus, Store } from "lucide-react";
import { toast } from "sonner";

import { getSyncStatusBadgeClass } from "@/constants/shopify";
import { shopifyErrorMessage } from "@/lib/frappe/shopify-sync";
import { createStore, fetchStoreList, type StoreListRow } from "@/lib/frappe/shopify-connection-settings";

export default function Page() {
  const router = useRouter();
  const [stores, setStores] = useState<StoreListRow[] | null>(null);
  const [addOpen, setAddOpen] = useState(false);
  const [connectionId, setConnectionId] = useState("");
  const [label, setLabel] = useState("");
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetchStoreList()
      .then((rows) => {
        if (!cancelled) setStores(rows);
      })
      .catch((error) => {
        if (!cancelled) {
          setStores([]);
          toast.error(shopifyErrorMessage(error, "Could not load Shopify stores."));
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function submitCreate() {
    if (!connectionId.trim()) {
      toast.warning("Give the connection an id first.");
      return;
    }
    setCreating(true);
    try {
      const { name } = await createStore(connectionId.trim(), label.trim() || undefined);
      setAddOpen(false);
      setConnectionId("");
      setLabel("");
      router.push(`/os/settings/connectors/shopify/${encodeURIComponent(name)}`);
    } catch (error) {
      toast.error(shopifyErrorMessage(error, "Could not create the connection."));
    } finally {
      setCreating(false);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <PageHeader
        title="Shopify Settings"
        subtitle="Every Shopify store connected to this bench."
        action={
          <Button size="sm" onClick={() => setAddOpen(true)}>
            <Plus /> Add store
          </Button>
        }
      />

      {stores === null ? (
        <div className="grid gap-3">
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-20 w-full" />
        </div>
      ) : stores.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center gap-2 py-10 text-center">
            <Store className="size-8 text-muted-foreground" />
            <p className="font-medium text-sm">No Shopify store connected yet.</p>
            <p className="text-muted-foreground text-sm">Add one to start syncing orders, products and inventory.</p>
            <Button size="sm" className="mt-2" onClick={() => setAddOpen(true)}>
              <Plus /> Add store
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-3">
          {stores.map((store) => (
            <Link key={store.name} href={`/os/settings/connectors/shopify/${encodeURIComponent(store.name)}`}>
              <Card className="transition-colors hover:bg-accent">
                <CardContent className="flex items-center justify-between gap-4 py-4">
                  <div className="flex items-center gap-3">
                    <span className="flex size-8 items-center justify-center rounded-md border bg-background">
                      <Store className="size-4" />
                    </span>
                    <div>
                      <p className="font-medium text-sm">{store.label}</p>
                      <p className="text-muted-foreground text-xs">{store.shop_url || "Not configured yet"}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {!store.is_enabled && <Badge variant="outline">Disabled</Badge>}
                    <Badge variant="outline" className={getSyncStatusBadgeClass(store.last_status === "connected" ? "Success" : "Failed")}>
                      {store.last_status === "connected" ? "Connected" : store.last_status === "error" ? "Error" : "Not configured"}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}

      <Dialog open={addOpen} onOpenChange={setAddOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add a Shopify store</DialogTitle>
            <DialogDescription>Creates a disabled connection you can then configure and enable.</DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-2">
            <div className="space-y-2">
              <Label htmlFor="new-connection-id">Connection ID</Label>
              <Input
                id="new-connection-id"
                placeholder="e.g. my-store"
                value={connectionId}
                onChange={(e) => setConnectionId(e.target.value)}
                disabled={creating}
              />
              <p className="text-muted-foreground text-xs">A stable id, not shown to sellers. Can't be changed later.</p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="new-connection-label">Label</Label>
              <Input
                id="new-connection-label"
                placeholder="e.g. My Store"
                value={label}
                onChange={(e) => setLabel(e.target.value)}
                disabled={creating}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setAddOpen(false)} disabled={creating}>
              Cancel
            </Button>
            <Button onClick={() => void submitCreate()} disabled={creating}>
              {creating ? "Creating..." : "Create"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
