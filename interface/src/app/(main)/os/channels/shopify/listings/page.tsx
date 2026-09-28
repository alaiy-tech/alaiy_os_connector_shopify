import { Suspense } from "react";

import Link from "next/link";

import { PageHeader } from "@alaiy-os/layout/page-header";
import { Button } from "@alaiy-os/ui/button";
import { Sparkles } from "lucide-react";

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
            <Button size="sm" variant="outline" asChild>
              <Link href="/os/channels/shopify/listings/enrichment">
                <Sparkles /> Enrichment Review
              </Link>
            </Button>
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
