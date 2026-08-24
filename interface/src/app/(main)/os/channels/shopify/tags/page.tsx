"use client";

import { PageHeader } from "@alaiy-os/layout/page-header";

import { fetchResourceList, refreshShopifyTags } from "@/lib/frappe/shopify-sync";

import { RefreshableList } from "../_components/refreshable-list";
import { SimpleResourceTable } from "../_components/simple-resource-table";

interface ShopifyTag extends Record<string, unknown> {
  name: string;
  tag_name: string;
}

export default function Page() {
  return (
    <div className="flex flex-col gap-4">
      <PageHeader title="Shopify Tags" subtitle="Every tag Shopify has reported across your products." />
      <RefreshableList refresh={refreshShopifyTags}>
        {(reloadToken) => (
          <SimpleResourceTable<ShopifyTag>
            key={reloadToken}
            load={() => fetchResourceList<ShopifyTag>("Shopify Tag", ["name", "tag_name"], { orderBy: "tag_name asc" })}
            rowKey={(row) => row.name}
            emptyMessage="No tags synced yet."
            columns={[{ header: "Tag", render: (row) => row.tag_name }]}
          />
        )}
      </RefreshableList>
    </div>
  );
}
