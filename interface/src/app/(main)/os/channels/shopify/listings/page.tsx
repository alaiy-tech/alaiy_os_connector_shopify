import { Suspense } from "react";

import { PageHeader } from "@alaiy-os/layout/page-header";

import { CreateListingDialog } from "./_components/create-listing-dialog";
import { ListingCsvActions } from "./_components/listing-csv-actions";
import { ListingsTable } from "./_components/listings-table";

export default function Page() {
  return (
    <div className="flex flex-col gap-4">
      <PageHeader
        title="Shopify Listings"
        subtitle="Every product listed on your Shopify storefront."
        action={
          <div className="flex flex-wrap gap-2">
            <ListingCsvActions />
            <CreateListingDialog />
          </div>
        }
      />
      <Suspense>
        <ListingsTable />
      </Suspense>
    </div>
  );
}
