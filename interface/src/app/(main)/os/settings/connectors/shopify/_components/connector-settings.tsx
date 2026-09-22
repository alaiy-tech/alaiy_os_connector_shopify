"use client";

import { useEffect, useState } from "react";

import {
  type ConnectorConfig,
  fetchConnectorConfig,
  isPasswordValue,
  saveAndTestConnector,
  testConnector,
} from "@alaiy-os/frappe/connectors";
import { Alert, AlertDescription, AlertTitle } from "@alaiy-os/ui/alert";
import { Button } from "@alaiy-os/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@alaiy-os/ui/card";
import { Input } from "@alaiy-os/ui/input";
import { Label } from "@alaiy-os/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@alaiy-os/ui/select";
import { Skeleton } from "@alaiy-os/ui/skeleton";
import { Spinner } from "@alaiy-os/ui/spinner";
import { Switch } from "@alaiy-os/ui/switch";
import { CircleCheck, CircleX, Plug } from "lucide-react";
import { toast } from "sonner";

import { shopifyErrorMessage } from "@/lib/frappe/shopify-sync";

import { LinkField } from "./link-field";
import { LocationMapEditor, type LocationMapRow } from "./location-map-editor";

const CONNECTOR_ID = "shopify";

// Real Select options, pulled from the DocType — never hand-guessed. Keep in
// step with alaiy_os_connector_shopify/.../shopify_connector_settings.json.
const INVOICE_TRIGGER_OPTIONS = ["Paid and Fulfilled", "Paid"];
const ORDER_STATUS_FILTER_OPTIONS = ["Open", "Any", "Closed", "Cancelled"];
const FULFILLMENT_SYNC_DIRECTION_OPTIONS = ["Shopify → Alaiy OS (default)", "Alaiy OS → Shopify (two-way)"];
const INVENTORY_SYNC_INTERVAL_OPTIONS = ["Disabled", "5 min", "15 min", "30 min", "60 min"];
const TOKEN_REFRESH_INTERVAL_OPTIONS = ["Disabled", "6 hours", "12 hours", "24 hours"];

type Form = {
  enabled: boolean;
  shopUrl: string;
  clientId: string;
  clientSecret: string;
  webhookSecret: string;
  company: string;
  defaultWarehouse: string;
  returnWarehouse: string;
  customerGroup: string;
  defaultTerritory: string;
  sellingPriceList: string;
  costCenter: string;
  taxAccount: string;
  autoSalesInvoice: boolean;
  invoiceTrigger: string;
  orderStatusFilter: string;
  fulfillmentSyncDirection: string;
  inventorySyncInterval: string;
  tokenRefreshInterval: string;
  importActive: boolean;
  importDraft: boolean;
  importArchived: boolean;
  exportActive: boolean;
  exportDraft: boolean;
  exportArchived: boolean;
  locationMap: LocationMapRow[];
};

const EMPTY: Form = {
  enabled: false,
  shopUrl: "",
  clientId: "",
  clientSecret: "",
  webhookSecret: "",
  company: "",
  defaultWarehouse: "",
  returnWarehouse: "",
  customerGroup: "",
  defaultTerritory: "",
  sellingPriceList: "",
  costCenter: "",
  taxAccount: "",
  autoSalesInvoice: false,
  invoiceTrigger: "",
  orderStatusFilter: "",
  fulfillmentSyncDirection: "",
  inventorySyncInterval: "",
  tokenRefreshInterval: "",
  importActive: false,
  importDraft: false,
  importArchived: false,
  exportActive: false,
  exportDraft: false,
  exportArchived: false,
  locationMap: [],
};

/**
 * Connection, defaults, and sync behaviour for the Shopify connector.
 *
 * Reads and saves through the platform's registry-driven connector API
 * (`alaiy_os.api.connectors`), same as every other connector's settings
 * screen — Shopify needs no bespoke settings endpoint of its own.
 *
 * Not covered here: `sh_access_token` (set by the OAuth flow, not typed in
 * by hand).
 */
export function ConnectorSettings() {
  const [config, setConfig] = useState<ConnectorConfig | null>(null);
  const [form, setForm] = useState<Form>(EMPTY);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);
  const [reloadToken, setReloadToken] = useState(0);

  // biome-ignore lint/correctness/useExhaustiveDependencies: reloadToken is a trigger, not a value read here — bumping it is how a save re-reads.
  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      try {
        const settings = await fetchConnectorConfig(CONNECTOR_ID);
        if (cancelled) return;
        setConfig(settings);
        const v = settings.values;
        setForm({
          enabled: Boolean(v.is_enabled),
          shopUrl: asText(v.sh_shop_url),
          clientId: asText(v.sh_client_id),
          // Never prefilled: the stored secret doesn't come back, and blank means "keep it" on save.
          clientSecret: "",
          webhookSecret: "",
          company: asText(v.sh_company),
          defaultWarehouse: asText(v.sh_default_warehouse),
          returnWarehouse: asText(v.sh_return_warehouse),
          customerGroup: asText(v.sh_customer_group),
          defaultTerritory: asText(v.sh_default_territory),
          sellingPriceList: asText(v.sh_selling_price_list),
          costCenter: asText(v.sh_cost_center),
          taxAccount: asText(v.sh_tax_account),
          autoSalesInvoice: Boolean(v.sh_auto_sales_invoice),
          invoiceTrigger: asText(v.sh_invoice_trigger),
          orderStatusFilter: asText(v.sh_order_status_filter),
          fulfillmentSyncDirection: asText(v.sh_fulfillment_sync_direction),
          inventorySyncInterval: asText(v.sh_inventory_sync_interval),
          tokenRefreshInterval: asText(v.sh_token_refresh_interval),
          importActive: Boolean(v.sh_import_status_active),
          importDraft: Boolean(v.sh_import_status_draft),
          importArchived: Boolean(v.sh_import_status_archived),
          exportActive: Boolean(v.sh_export_status_active),
          exportDraft: Boolean(v.sh_export_status_draft),
          exportArchived: Boolean(v.sh_export_status_archived),
          locationMap: asLocationMapRows(v.sh_location_map),
        });
      } catch (error) {
        if (!cancelled) toast.error(shopifyErrorMessage(error, "Could not load the connector settings."));
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, [reloadToken]);

  const clientSecretSet = config
    ? isPasswordValue(config.values.sh_client_secret) && config.values.sh_client_secret._set
    : false;
  const webhookSecretSet = config
    ? isPasswordValue(config.values.sh_webhook_secret) && config.values.sh_webhook_secret._set
    : false;

  function set<K extends keyof Form>(key: K, value: Form[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  async function saveAndTest() {
    if (!form.shopUrl.trim()) {
      toast.warning("Add the shop URL first.");
      return;
    }
    if (!form.clientId.trim()) {
      toast.warning("Add the Client ID first.");
      return;
    }

    setBusy(true);
    setResult(null);
    try {
      const values: Record<string, unknown> = {
        is_enabled: form.enabled ? 1 : 0,
        sh_shop_url: form.shopUrl.trim(),
        sh_client_id: form.clientId.trim(),
        sh_company: form.company,
        sh_default_warehouse: form.defaultWarehouse,
        sh_return_warehouse: form.returnWarehouse,
        sh_customer_group: form.customerGroup,
        sh_default_territory: form.defaultTerritory,
        sh_selling_price_list: form.sellingPriceList,
        sh_cost_center: form.costCenter,
        sh_tax_account: form.taxAccount,
        sh_auto_sales_invoice: form.autoSalesInvoice ? 1 : 0,
        sh_invoice_trigger: form.invoiceTrigger,
        sh_order_status_filter: form.orderStatusFilter,
        sh_fulfillment_sync_direction: form.fulfillmentSyncDirection,
        sh_inventory_sync_interval: form.inventorySyncInterval,
        sh_token_refresh_interval: form.tokenRefreshInterval,
        sh_import_status_active: form.importActive ? 1 : 0,
        sh_import_status_draft: form.importDraft ? 1 : 0,
        sh_import_status_archived: form.importArchived ? 1 : 0,
        sh_export_status_active: form.exportActive ? 1 : 0,
        sh_export_status_draft: form.exportDraft ? 1 : 0,
        sh_export_status_archived: form.exportArchived ? 1 : 0,
        sh_location_map: form.locationMap,
      };
      // A blank Password field is read as "no change" upstream, so only send one the user actually typed.
      if (form.clientSecret) values.sh_client_secret = form.clientSecret;
      if (form.webhookSecret) values.sh_webhook_secret = form.webhookSecret;

      const outcome = await saveAndTestConnector(CONNECTOR_ID, values);
      setResult(outcome);
      if (outcome.success) toast.success("Saved. Shopify accepted the credentials.");
      else toast.error(outcome.message || "Saved, but the connection test failed.");
      setForm((current) => ({ ...current, clientSecret: "", webhookSecret: "" }));
      setReloadToken((token) => token + 1);
    } catch (error) {
      toast.error(shopifyErrorMessage(error, "Could not save the connector settings."));
    } finally {
      setBusy(false);
    }
  }

  async function test() {
    setBusy(true);
    setResult(null);
    try {
      const outcome = await testConnector(CONNECTOR_ID);
      setResult(outcome);
      if (outcome.success) toast.success("Connected.");
      else toast.error(outcome.message || "The connection test failed.");
      setReloadToken((token) => token + 1);
    } catch (error) {
      toast.error(shopifyErrorMessage(error, "Could not test the connection."));
    } finally {
      setBusy(false);
    }
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      {result && (
        <Alert variant={result.success ? "default" : "destructive"}>
          {result.success ? <CircleCheck /> : <CircleX />}
          <AlertTitle>{result.success ? "Connected" : "Connection failed"}</AlertTitle>
          <AlertDescription>{result.message}</AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Connection</CardTitle>
          <CardDescription>The Shopify store this connector talks to, and its API credentials.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-5 md:grid-cols-2">
          <div className="flex items-center justify-between gap-4 rounded-lg border p-3 md:col-span-2">
            <div>
              <Label htmlFor="sh-enabled">Enable Shopify</Label>
              <p className="text-muted-foreground text-sm">Off means sync jobs and webhooks stop running.</p>
            </div>
            <Switch id="sh-enabled" checked={form.enabled} onCheckedChange={(v) => set("enabled", v)} disabled={busy} />
          </div>

          <div className="space-y-2">
            <Label htmlFor="sh-shop-url">Shop URL</Label>
            <Input
              id="sh-shop-url"
              placeholder="your-store.myshopify.com"
              value={form.shopUrl}
              disabled={busy}
              onChange={(e) => set("shopUrl", e.target.value)}
            />
            <p className="text-muted-foreground text-xs">Your Shopify store domain, e.g. myshop.myshopify.com</p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="sh-client-id">Client ID</Label>
            <Input
              id="sh-client-id"
              autoComplete="off"
              value={form.clientId}
              disabled={busy}
              onChange={(e) => set("clientId", e.target.value)}
            />
            <p className="text-muted-foreground text-xs">Client ID from your Shopify custom app (Developer Dashboard)</p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="sh-client-secret">Client Secret</Label>
            <Input
              id="sh-client-secret"
              type="password"
              autoComplete="new-password"
              placeholder={clientSecretSet ? "•••••••• (leave blank to keep)" : "Not set"}
              value={form.clientSecret}
              disabled={busy}
              onChange={(e) => set("clientSecret", e.target.value)}
            />
            <p className="text-muted-foreground text-xs">Client Secret from your Shopify custom app</p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="sh-webhook-secret">Webhook Secret</Label>
            <Input
              id="sh-webhook-secret"
              type="password"
              autoComplete="new-password"
              placeholder={webhookSecretSet ? "•••••••• (leave blank to keep)" : "Not set"}
              value={form.webhookSecret}
              disabled={busy}
              onChange={(e) => set("webhookSecret", e.target.value)}
            />
            <p className="text-muted-foreground text-xs">
              Shared secret used to validate the X-Shopify-Hmac-Sha256 header on incoming webhooks. Must match the secret
              configured on the Shopify webhook subscriptions. Required: webhooks are rejected outright if this isn't set.
            </p>
          </div>

          <div className="space-y-1 md:col-span-2">
            <p className="text-muted-foreground text-xs">
              Token last refreshed: {formatDatetime(config?.values.sh_token_refreshed_at)} · Token expires:{" "}
              {formatDatetime(config?.values.sh_token_expires_at)}
            </p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Defaults</CardTitle>
          <CardDescription>Where synced orders, items, and taxes land in Alaiy OS.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-5 md:grid-cols-2">
          <div className="space-y-2">
            <Label>Company</Label>
            <LinkField doctype="Company" value={form.company} onChange={(v) => set("company", v)} disabled={busy} />
          </div>
          <div className="space-y-2">
            <Label>Default Warehouse</Label>
            <LinkField
              doctype="Warehouse"
              value={form.defaultWarehouse}
              onChange={(v) => set("defaultWarehouse", v)}
              disabled={busy}
            />
          </div>
          <div className="space-y-2">
            <Label>Return Warehouse</Label>
            <LinkField
              doctype="Warehouse"
              value={form.returnWarehouse}
              onChange={(v) => set("returnWarehouse", v)}
              disabled={busy}
            />
            <p className="text-muted-foreground text-xs">
              Where a Shopify refund's Sales Return lands. Leave blank to use Default Warehouse instead.
            </p>
          </div>
          <div className="space-y-2">
            <Label>Default Customer Group</Label>
            <LinkField
              doctype="Customer Group"
              value={form.customerGroup}
              onChange={(v) => set("customerGroup", v)}
              disabled={busy}
            />
          </div>
          <div className="space-y-2">
            <Label>Default Territory</Label>
            <LinkField
              doctype="Territory"
              value={form.defaultTerritory}
              onChange={(v) => set("defaultTerritory", v)}
              disabled={busy}
            />
            <p className="text-muted-foreground text-xs">
              Territory assigned to Customers auto-created from Shopify orders. Falls back to any existing Territory if
              left blank.
            </p>
          </div>
          <div className="space-y-2">
            <Label>Selling Price List</Label>
            <LinkField
              doctype="Price List"
              value={form.sellingPriceList}
              onChange={(v) => set("sellingPriceList", v)}
              disabled={busy}
            />
          </div>
          <div className="space-y-2">
            <Label>Cost Center</Label>
            <LinkField
              doctype="Cost Center"
              value={form.costCenter}
              onChange={(v) => set("costCenter", v)}
              disabled={busy}
            />
          </div>
          <div className="space-y-2">
            <Label>Tax Account</Label>
            <LinkField doctype="Account" value={form.taxAccount} onChange={(v) => set("taxAccount", v)} disabled={busy} />
            <p className="text-muted-foreground text-xs">
              Account that tax lines pulled from Shopify orders (CGST, SGST, VAT, ...) are booked against. Leave blank
              to auto-resolve/create a "Shopify Tax" account under the company.
            </p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Inventory Locations</CardTitle>
          <CardDescription>
            Map Alaiy OS warehouses to Shopify locations for multi-location inventory sync. Run "Sync Locations" first
            to load Shopify locations. Leave empty to push only the Default Warehouse to Shopify's primary location
            (single-location mode).
          </CardDescription>
        </CardHeader>
        <CardContent>
          <LocationMapEditor rows={form.locationMap} onChange={(rows) => set("locationMap", rows)} disabled={busy} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Sync behaviour</CardTitle>
          <CardDescription>Direction, timing, and invoicing rules for orders and inventory.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-5 md:grid-cols-2">
          <div className="flex items-center justify-between gap-4 rounded-lg border p-3 md:col-span-2">
            <div>
              <Label htmlFor="sh-auto-invoice">Auto-create Sales Invoice</Label>
              <p className="text-muted-foreground text-sm">
                Auto-create + submit a Sales Invoice for Shopify orders. Submitting that invoice in Alaiy OS also marks
                the order Paid on Shopify.
              </p>
            </div>
            <Switch
              id="sh-auto-invoice"
              checked={form.autoSalesInvoice}
              onCheckedChange={(v) => set("autoSalesInvoice", v)}
              disabled={busy}
            />
          </div>

          <SelectField
            label="Generate Invoice When"
            description="When to generate the invoice. 'Paid and Fulfilled' (recommended) waits for both payment and shipment -- correct for Cash on Delivery, where payment lands only on delivery. 'Paid' invoices as soon as the order is paid."
            value={form.invoiceTrigger}
            onChange={(v) => set("invoiceTrigger", v)}
            options={INVOICE_TRIGGER_OPTIONS}
            disabled={busy || !form.autoSalesInvoice}
          />
          <SelectField
            label="Sync Orders With Status"
            description="Filter for which orders to pull from Shopify"
            value={form.orderStatusFilter}
            onChange={(v) => set("orderStatusFilter", v)}
            options={ORDER_STATUS_FILTER_OPTIONS}
            disabled={busy}
          />
          <SelectField
            label="Fulfillment Sync Direction"
            description="'Shopify → Alaiy OS' (default): a Shopify fulfillment auto-creates a submitted Delivery Note here -- today's only behavior, unchanged when left at default. 'Alaiy OS → Shopify (two-way)': in addition, submitting a Delivery Note here (e.g. a warehouse scanning items out against a Sales Order) creates a real Shopify fulfillment with tracking info. Safe to switch either way at any time -- no reinstall needed."
            value={form.fulfillmentSyncDirection}
            onChange={(v) => set("fulfillmentSyncDirection", v)}
            options={FULFILLMENT_SYNC_DIRECTION_OPTIONS}
            disabled={busy}
          />
          <SelectField
            label="Inventory Sync Interval"
            description="How often to push Alaiy OS stock levels to Shopify"
            value={form.inventorySyncInterval}
            onChange={(v) => set("inventorySyncInterval", v)}
            options={INVENTORY_SYNC_INTERVAL_OPTIONS}
            disabled={busy}
          />
          <SelectField
            label="Token Refresh Interval"
            description="How often to proactively mint a fresh access token, so a sync never has to hit an expired-token error first. Shopify's client_credentials tokens for this app were observed to last ~24h."
            value={form.tokenRefreshInterval}
            onChange={(v) => set("tokenRefreshInterval", v)}
            options={TOKEN_REFRESH_INTERVAL_OPTIONS}
            disabled={busy}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Import / export filters</CardTitle>
          <CardDescription>Which product statuses are pulled from Shopify, and which are pushed to it.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-5 md:grid-cols-2">
          <div className="space-y-3">
            <Label>Import from Shopify</Label>
            <CheckRow label="Active products" checked={form.importActive} onChange={(v) => set("importActive", v)} disabled={busy} />
            <CheckRow label="Draft products" checked={form.importDraft} onChange={(v) => set("importDraft", v)} disabled={busy} />
            <CheckRow
              label="Archived products"
              checked={form.importArchived}
              onChange={(v) => set("importArchived", v)}
              disabled={busy}
            />
          </div>
          <div className="space-y-3">
            <Label>Export to Shopify</Label>
            <CheckRow label="Active products" checked={form.exportActive} onChange={(v) => set("exportActive", v)} disabled={busy} />
            <CheckRow label="Draft products" checked={form.exportDraft} onChange={(v) => set("exportDraft", v)} disabled={busy} />
            <CheckRow
              label="Archived products"
              checked={form.exportArchived}
              onChange={(v) => set("exportArchived", v)}
              disabled={busy}
            />
          </div>
        </CardContent>
      </Card>

      <div className="flex flex-wrap items-center gap-2">
        <Button onClick={() => void saveAndTest()} disabled={busy}>
          {busy ? (
            <>
              <Spinner /> Working...
            </>
          ) : (
            "Save and test"
          )}
        </Button>
        <Button variant="outline" onClick={() => void test()} disabled={busy}>
          <Plug /> Test connection
        </Button>
      </div>
    </div>
  );
}

function SelectField({
  label,
  description,
  value,
  onChange,
  options,
  disabled,
}: {
  label: string;
  description?: string;
  value: string;
  onChange: (value: string) => void;
  options: string[];
  disabled?: boolean;
}) {
  return (
    <div className="space-y-2">
      <Label>{label}</Label>
      <Select value={value || undefined} onValueChange={onChange} disabled={disabled}>
        <SelectTrigger className="w-full">
          <SelectValue placeholder="Not set" />
        </SelectTrigger>
        <SelectContent>
          {options.map((option) => (
            <SelectItem key={option} value={option}>
              {option}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {description && <p className="text-muted-foreground text-xs">{description}</p>}
    </div>
  );
}

function CheckRow({
  label,
  checked,
  onChange,
  disabled,
}: {
  label: string;
  checked: boolean;
  onChange: (value: boolean) => void;
  disabled?: boolean;
}) {
  return (
    <div className="flex items-center justify-between gap-4">
      <span className="text-sm">{label}</span>
      <Switch checked={checked} onCheckedChange={onChange} disabled={disabled} />
    </div>
  );
}

function asLocationMapRows(value: unknown): LocationMapRow[] {
  if (!Array.isArray(value)) return [];
  return value.map((row) => ({
    warehouse: asText((row as Record<string, unknown>)?.warehouse),
    shopify_location: asText((row as Record<string, unknown>)?.shopify_location),
  }));
}

function formatDatetime(value: unknown): string {
  const text = asText(value);
  if (!text) return "—";
  const date = new Date(text);
  return Number.isNaN(date.getTime()) ? "—" : date.toLocaleString();
}

function asText(value: unknown): string {
  if (value === null || value === undefined) return "";
  if (typeof value === "object") return "";
  return String(value);
}
