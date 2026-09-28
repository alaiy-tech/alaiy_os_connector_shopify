/**
 * Typed client over alaiy_os_connector_shopify.api.connection_settings --
 * per-connection settings CRUD, replacing the platform's generic
 * single-doctype connector API (which cannot address one named Shopify
 * Connection on a multi-store bench). Response shapes deliberately mirror
 * @alaiy-os/frappe/connectors' ConnectorConfig so field-rendering logic
 * (Password masking, RENDERABLE fieldtypes) transfers over unchanged.
 */

export interface StoreListRow {
  name: string;
  label: string;
  shop_url: string;
  is_enabled: number;
  last_status: string;
}

export interface ConnectorField {
  fieldname: string;
  label: string;
  fieldtype: string;
  options: string | null;
  reqd: number;
  description: string | null;
}

export type PasswordValue = { _type: "password"; _set: boolean };

export interface StoreConfig {
  fields: ConnectorField[];
  values: Record<string, unknown>;
}

export function isPasswordValue(value: unknown): value is PasswordValue {
  return typeof value === "object" && value !== null && (value as { _type?: string })._type === "password";
}

async function callMethod<T>(method: string, body?: Record<string, unknown>): Promise<T> {
  const res = await fetch(`/api/method/${method}`, {
    method: body ? "POST" : "GET",
    headers: body ? { "content-type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
    cache: "no-store",
  });

  const text = await res.text();
  let payload: { message?: T; _server_messages?: string; exception?: string } | null = null;
  try {
    payload = JSON.parse(text) as typeof payload;
  } catch {
    payload = null;
  }

  if (!res.ok) throw new Error(serverMessage(payload) ?? `${method} failed (${res.status}).`);
  if (!payload || payload.message === undefined) throw new Error(`${method} returned nothing.`);
  return payload.message;
}

function serverMessage(payload: { _server_messages?: string; exception?: string } | null): string | null {
  if (!payload) return null;
  try {
    const messages = JSON.parse(payload._server_messages ?? "[]") as string[];
    const first = messages.map((entry) => JSON.parse(entry) as { message?: string }).find((entry) => entry.message);
    if (first?.message) return first.message.replace(/<[^>]+>/g, "");
  } catch {
    // fall through to the raw exception line
  }
  return payload.exception ?? null;
}

export function fetchStoreList(): Promise<StoreListRow[]> {
  return callMethod<StoreListRow[]>("alaiy_os_connector_shopify.api.connection_settings.list_stores");
}

export function fetchStoreConfig(connection: string): Promise<StoreConfig> {
  return callMethod<StoreConfig>(
    `alaiy_os_connector_shopify.api.connection_settings.get_store_config?connection=${encodeURIComponent(connection)}`,
  );
}

export function saveStoreConfig(connection: string, values: Record<string, unknown>): Promise<{ success: boolean; message: string }> {
  return callMethod("alaiy_os_connector_shopify.api.connection_settings.save_store_config", { connection, values });
}

export function testStoreConnection(connection: string): Promise<{ success: boolean; message: string }> {
  return callMethod(
    `alaiy_os_connector_shopify.api.test_connection.test_connection?connection=${encodeURIComponent(connection)}`,
  );
}

export function createStore(connectionId: string, label?: string): Promise<{ name: string }> {
  return callMethod("alaiy_os_connector_shopify.api.connection_settings.create_store", {
    connection_id: connectionId,
    label,
  });
}
