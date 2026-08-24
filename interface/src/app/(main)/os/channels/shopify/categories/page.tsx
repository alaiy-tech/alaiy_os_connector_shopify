"use client";

import { PageHeader } from "@alaiy-os/layout/page-header";

import { fetchResourceList, refreshShopifyTaxonomy } from "@/lib/frappe/shopify-sync";

import { RefreshableList } from "../_components/refreshable-list";
import { SimpleResourceTable } from "../_components/simple-resource-table";

interface ShopifyCategory extends Record<string, unknown> {
  name: string;
  shopify_category_name: string;
  shopify_category_id: string;
  parent_shopify_category: string | null;
}

export default function Page() {
  return (
    <div className="flex flex-col gap-4">
      <PageHeader title="Shopify Categories" subtitle="Shopify's standard product taxonomy, synced read-only." />
      <RefreshableList refresh={refreshShopifyTaxonomy}>
        {(reloadToken) => (
          <SimpleResourceTable<ShopifyCategory>
            key={reloadToken}
            load={() =>
              fetchResourceList<ShopifyCategory>(
                "Shopify Category",
                ["name", "shopify_category_name", "shopify_category_id", "parent_shopify_category"],
                { orderBy: "shopify_category_name asc" },
              )
            }
            rowKey={(row) => row.name}
            emptyMessage="No categories synced yet."
            columns={[
              { header: "Category", render: (row) => row.shopify_category_name },
              { header: "Parent", render: (row) => row.parent_shopify_category || <span className="text-muted-foreground">—</span> },
              { header: "Shopify Category ID", render: (row) => <span className="font-mono text-xs">{row.shopify_category_id}</span> },
            ]}
          />
        )}
      </RefreshableList>
    </div>
  );
}
