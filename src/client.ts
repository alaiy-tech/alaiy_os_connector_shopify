import 'dotenv/config';

const SHOPIFY_STORE_URL = process.env.SHOPIFY_STORE_URL;
const SHOPIFY_ACCESS_TOKEN = process.env.SHOPIFY_ACCESS_TOKEN;
const API_VERSION = process.env.SHOPIFY_API_VERSION ?? '2026-04';

if (!SHOPIFY_STORE_URL) throw new Error('Missing env: SHOPIFY_STORE_URL');
if (!SHOPIFY_ACCESS_TOKEN) throw new Error('Missing env: SHOPIFY_ACCESS_TOKEN');

const endpoint = `https://${SHOPIFY_STORE_URL}/admin/api/${API_VERSION}/graphql.json`;

export interface GraphQLResponse<T = unknown> {
  data: T;
  errors?: Array<{ message: string; locations?: unknown; path?: unknown }>;
  extensions?: {
    cost?: {
      requestedQueryCost: number;
      actualQueryCost: number;
      throttleStatus: {
        maximumAvailable: number;
        currentlyAvailable: number;
        restoreRate: number;
      };
    };
  };
}

async function request<T = unknown>(
  query: string,
    variables?: object,
): Promise<T> {
  const res = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Shopify-Access-Token': SHOPIFY_ACCESS_TOKEN!,
    },
    body: JSON.stringify({ query, variables }),
  });

  if (!res.ok) {
    throw new Error(`Shopify API HTTP ${res.status}: ${await res.text()}`);
  }

    const json = (await res.json()) as GraphQLResponse<T>;

  if (json.errors?.length) {
    throw new Error(
      `Shopify GraphQL errors:\n${json.errors.map(e => e.message).join('\n')}`,
    );
  }

  return json.data;
}

export const shopifyClient = { request };
