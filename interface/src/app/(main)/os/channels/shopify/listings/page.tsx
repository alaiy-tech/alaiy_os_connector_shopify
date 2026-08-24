import { PageHeader } from "@alaiy-os/layout/page-header";

import { ListingCsvActions } from "./_components/listing-csv-actions";
import { ListingsTable } from "./_components/listings-table";

export default function Page() {
  return (
    <div className="flex flex-col gap-4">
      <PageHeader
        title="Shopify Listings"
        subtitle="Every product listed on your Shopify storefront."
        action={<ListingCsvActions />}
      />
      <ListingsTable />
    </div>
  );
}
