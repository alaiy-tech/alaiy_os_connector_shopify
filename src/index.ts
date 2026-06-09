/**
 * Shopify Connector - fully-typed client for the Shopify Admin GraphQL API 2026-04
 *
 * Quick start:
 *   1. Copy .env.example → .env and fill in SHOPIFY_STORE_URL + SHOPIFY_ACCESS_TOKEN
 *   2. Run the live demo:  npx ts-node src/main.ts
 *
 * Usage in your own code:
 *   import { customers, createCustomer, shopifyClient } from './index';
 *   import type { Customer, CustomerInput } from './index';
 *
 *   // Typed helper (fill field selection inside src/customers.ts first):
 *   const list = await customers({ first: 10, query: 'email:*@example.com' });
 *
 *   // Raw client for custom queries with full control:
 *   const data = await shopifyClient.request<{ customer: Customer }>(`#graphql
 *     query($id: ID!) { customer(id: $id) { id email firstName } }
 *   `, { id: 'gid://shopify/Customer/123' });
 *
 * Sections (original 7):
 *   customers | discounts-marketing | inventory | orders |
 *   products-collections | retail | shipping-fulfillment
 *
 * Sections (new 11):
 *   app | cms | channels | metafields | shop | themes |
 *   webhooks | markets | files | redirects | misc
 *
 * Types:  src/types/ (enums, interfaces, inputs, objects, connections, unions, payloads)
 */

export * from './types';

// Re-export the raw client for advanced / custom queries
export { shopifyClient } from './client';
export type { GraphQLResponse } from './client';

// ── Original section modules ──────────────────────────────────────────────────
export * from './customers';
export * from './discounts-marketing';
export * from './inventory';
export * from './orders';
export * from './products-collections';
export * from './retail';
export * from './shipping-fulfillment';

// ── New section modules ───────────────────────────────────────────────────────
export * from './app';
export * from './cms';
export * from './channels';
export * from './metafields';
export * from './shop';
export * from './themes';
export * from './webhooks';
export * from './markets';
export * from './files';
export * from './redirects';
export * from './misc';
