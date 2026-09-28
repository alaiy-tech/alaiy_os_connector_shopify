"use client";

import { use } from "react";

import Link from "next/link";

import { PageHeader } from "@alaiy-os/layout/page-header";
import { Button } from "@alaiy-os/ui/button";
import { ArrowLeft } from "lucide-react";

import { StoreSettings } from "./_components/store-settings";

export default function Page({ params }: { params: Promise<{ name: string }> }) {
  const { name } = use(params);
  const decodedName = decodeURIComponent(name);

  return (
    <div className="flex flex-col gap-4">
      <PageHeader
        title={decodedName}
        subtitle="Connection, defaults, and sync behaviour for this Shopify store."
        action={
          <Button size="sm" variant="outline" asChild>
            <Link href="/os/settings/connectors/shopify">
              <ArrowLeft /> All stores
            </Link>
          </Button>
        }
      />
      <StoreSettings connection={decodedName} />
    </div>
  );
}
