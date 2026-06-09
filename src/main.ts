import "dotenv/config";
import { shopifyClient } from "./client";

// ─── Query-scoped response types ─────────────────────────────────────────────
// In GraphQL you only request a subset of fields, so we type the response
// to match the exact selection set rather than the full object shape.

interface CustomerEdge {
  node: {
    id: string;
    email: string | null;
    firstName: string | null;
    lastName: string | null;
    createdAt: string;
    numberOfOrders: number;
    amountSpent: { amount: string; currencyCode: string };
  };
}

interface OrderEdge {
  node: {
    id: string;
    name: string;
    createdAt: string;
    displayFinancialStatus: string | null;
    displayFulfillmentStatus: string;
    totalPriceSet: { shopMoney: { amount: string; currencyCode: string } };
    customer: {
      email: string | null;
      firstName: string | null;
      lastName: string | null;
    } | null;
  };
}

interface ProductEdge {
  node: {
    id: string;
    title: string;
    status: string;
    totalInventory: number | null;
    priceRangeV2: {
      minVariantPrice: { amount: string; currencyCode: string };
      maxVariantPrice: { amount: string; currencyCode: string };
    };
  };
}

interface LocationEdge {
  node: { id: string; name: string };
}

interface InventoryLevelEdge {
  node: {
    id: string;
    quantities: Array<{ name: string; quantity: number }>;
    item: {
      sku: string | null;
      variant: { displayName: string } | null;
    };
  };
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function hr(label: string) {
  console.log(`\n${"─".repeat(60)}`);
  console.log(` ${label}`);
  console.log("─".repeat(60));
}

async function safe<T>(label: string, fn: () => Promise<T>): Promise<T | null> {
  try {
    return await fn();
  } catch (err) {
    console.error(`  ✗ ${label}: ${(err as Error).message}`);
    return null;
  }
}

// ─── Demos ───────────────────────────────────────────────────────────────────

async function demoCustomers() {
  hr("CUSTOMERS - first 5");
  const data = await safe("customers", () =>
    shopifyClient.request<{
      customers: { edges: CustomerEdge[]; pageInfo: { hasNextPage: boolean } };
    }>(`#graphql
      query {
        customers(first: 5) {
          edges {
            node {
              id
              email
              firstName
              lastName
              createdAt
              numberOfOrders
              amountSpent { amount currencyCode }
            }
          }
          pageInfo { hasNextPage }
        }
      }
    `),
  );

  if (!data) return;
  for (const { node } of data.customers.edges) {
    const name =
      [node.firstName, node.lastName].filter(Boolean).join(" ") || "(no name)";
    console.log(
      `  ${node.email ?? node.id}  |  ${name}  |  orders: ${node.numberOfOrders}`,
    );
  }
  console.log(`  hasNextPage: ${data.customers.pageInfo.hasNextPage}`);
}

async function demoOrders() {
  hr("ORDERS - last 5 (newest first)");
  const data = await safe("orders", () =>
    shopifyClient.request<{ orders: { edges: OrderEdge[] } }>(`#graphql
      query {
        orders(first: 5, sortKey: CREATED_AT, reverse: true) {
          edges {
            node {
              id
              name
              createdAt
              displayFinancialStatus
              displayFulfillmentStatus
              totalPriceSet { shopMoney { amount currencyCode } }
              customer { email firstName lastName }
            }
          }
        }
      }
    `),
  );

  if (!data) return;
  for (const { node } of data.orders.edges) {
    const customer = node.customer?.email ?? "(guest)";
    const money = node.totalPriceSet.shopMoney;
    console.log(
      `  ${node.name}  |  ${customer}  |  ${money.amount} ${money.currencyCode}  |  ${node.displayFinancialStatus ?? ""}`,
    );
  }
}

async function demoProducts() {
  hr("PRODUCTS - first 5");
  const data = await safe("products", () =>
    shopifyClient.request<{ products: { edges: ProductEdge[] } }>(`#graphql
      query {
        products(first: 5) {
          edges {
            node {
              id
              title
              status
              totalInventory
              priceRangeV2 {
                minVariantPrice { amount currencyCode }
                maxVariantPrice { amount currencyCode }
              }
            }
          }
        }
      }
    `),
  );

  if (!data) return;
  for (const { node } of data.products.edges) {
    const min = node.priceRangeV2.minVariantPrice;
    const max = node.priceRangeV2.maxVariantPrice;
    const price =
      min.amount === max.amount
        ? `${min.amount} ${min.currencyCode}`
        : `${min.amount}-${max.amount} ${min.currencyCode}`;
    console.log(
      `  ${node.title}  |  ${node.status}  |  stock: ${node.totalInventory ?? "?"}  |  ${price}`,
    );
  }
}

async function demoInventory() {
  hr("INVENTORY - first 5 levels at first location");

  const locData = await safe("locations", () =>
    shopifyClient.request<{ locations: { edges: LocationEdge[] } }>(`#graphql
      query { locations(first: 1) { edges { node { id name } } } }
    `),
  );
  if (!locData?.locations.edges.length) {
    console.log("  No locations found.");
    return;
  }

  const loc = locData.locations.edges[0].node;
  console.log(`  Location: ${loc.name}  (${loc.id})`);

  const invData = await safe("inventoryLevels", () =>
    shopifyClient.request<{
      location: { inventoryLevels: { edges: InventoryLevelEdge[] } };
    }>(
      `#graphql
      query($id: ID!) {
        location(id: $id) {
          inventoryLevels(first: 5) {
            edges {
              node {
                id
                quantities(names: ["available"]) { name quantity }
                item { sku variant { displayName } }
              }
            }
          }
        }
      }
    `,
      { id: loc.id },
    ),
  );

  if (!invData) return;
  for (const { node } of invData.location.inventoryLevels.edges) {
    const qty =
      node.quantities.find((q) => q.name === "available")?.quantity ?? "?";
    console.log(
      `  SKU: ${node.item.sku ?? "(no sku)"}  |  available: ${qty}  |  ${node.item.variant?.displayName ?? ""}`,
    );
  }
}

async function main() {
  console.log("Shopify Admin API - live demo");
  console.log(`Store: ${process.env.SHOPIFY_STORE_URL ?? "(not set)"}`);
  console.log(
    `API:   ${process.env.SHOPIFY_API_VERSION ?? "2026-04 (default)"}`,
  );

  if (!process.env.SHOPIFY_STORE_URL || !process.env.SHOPIFY_ACCESS_TOKEN) {
    console.error(
      "\nMissing credentials.  Copy .env.example → .env and fill in your values.",
    );
    process.exit(1);
  }

  await demoCustomers();
  await demoOrders();
  await demoProducts();
  await demoInventory();

  console.log("\nDone.\n");
}

main().catch((err) => {
  console.error("\nFatal error:", err);
  process.exit(1);
});
