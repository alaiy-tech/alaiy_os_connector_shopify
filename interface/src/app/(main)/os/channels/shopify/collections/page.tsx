import { PageHeader } from "@alaiy-os/layout/page-header";

import { Badge } from "@alaiy-os/ui/badge";

import { fetchResourceList, refreshShopifyCollections } from "@/lib/frappe/shopify-sync";

import { RefreshableList } from "../_components/refreshable-list";
import { SimpleResourceTable } from "../_components/simple-resource-table";

interface ShopifyCollection extends Record<string, unknown> {
  name: string;
  collection_title: string;
  handle: string;
  is_smart: 0 | 1;
  product_count: number;
  last_synced: string | null;
}

export default function Page() {
  return (
    <div className="flex flex-col gap-4">
      <PageHeader title="Shopify Collections" subtitle="Manual and smart collections pulled from your Shopify storefront." />
      <RefreshableList refresh={refreshShopifyCollections}>
        {(reloadToken) => (
          <SimpleResourceTable<ShopifyCollection>
            key={reloadToken}
            load={() =>
              fetchResourceList<ShopifyCollection>(
                "Shopify Collection",
                ["name", "collection_title", "handle", "is_smart", "product_count", "last_synced"],
                { orderBy: "collection_title asc" },
              )
            }
            rowKey={(row) => row.name}
            emptyMessage="No collections synced yet."
            columns={[
              { header: "Title", render: (row) => row.collection_title },
              { header: "Handle", render: (row) => <span className="text-muted-foreground">{row.handle}</span> },
              { header: "Type", render: (row) => <Badge variant="outline">{row.is_smart ? "Smart" : "Manual"}</Badge> },
              { header: "Products", align: "right", render: (row) => row.product_count },
              {
                header: "Last synced",
                render: (row) =>
                  row.last_synced ? new Date(row.last_synced).toLocaleString() : <span className="text-muted-foreground">—</span>,
              },
            ]}
          />
        )}
      </RefreshableList>
    </div>
  );
}
