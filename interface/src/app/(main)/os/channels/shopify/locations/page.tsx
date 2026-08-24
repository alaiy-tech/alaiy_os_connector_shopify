import { PageHeader } from "@alaiy-os/layout/page-header";

import { Badge } from "@alaiy-os/ui/badge";

import { fetchResourceList, refreshShopifyLocations } from "@/lib/frappe/shopify-sync";

import { RefreshableList } from "../_components/refreshable-list";
import { SimpleResourceTable } from "../_components/simple-resource-table";

interface ShopifyLocation extends Record<string, unknown> {
  name: string;
  location_name: string;
  is_active: 0 | 1;
  fulfillment_service_name: string | null;
  fulfillment_service_type: string | null;
  last_synced: string | null;
}

export default function Page() {
  return (
    <div className="flex flex-col gap-4">
      <PageHeader title="Shopify Locations" subtitle="Fulfillment locations Shopify reports, mapped to a warehouse per the connector settings." />
      <RefreshableList refresh={refreshShopifyLocations}>
        {(reloadToken) => (
          <SimpleResourceTable<ShopifyLocation>
            key={reloadToken}
            load={() =>
              fetchResourceList<ShopifyLocation>(
                "Shopify Location",
                ["name", "location_name", "is_active", "fulfillment_service_name", "fulfillment_service_type", "last_synced"],
                { orderBy: "location_name asc" },
              )
            }
            rowKey={(row) => row.name}
            emptyMessage="No locations synced yet."
            columns={[
              { header: "Location", render: (row) => row.location_name },
              {
                header: "Status",
                render: (row) => (
                  <Badge variant="outline" className={row.is_active ? undefined : "text-muted-foreground"}>
                    {row.is_active ? "Active" : "Inactive"}
                  </Badge>
                ),
              },
              {
                header: "Fulfillment service",
                render: (row) =>
                  row.fulfillment_service_name ? (
                    `${row.fulfillment_service_name} (${row.fulfillment_service_type})`
                  ) : (
                    <span className="text-muted-foreground">—</span>
                  ),
              },
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
