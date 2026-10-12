"use client";

import { use } from "react";

import Link from "next/link";

import { PageHeader } from "@alaiy-os/layout/page-header";
import { Button } from "@alaiy-os/ui/button";
import { ArrowLeft } from "lucide-react";

import { EnrichmentWorkspace } from "./_components/enrichment-workspace";

export default function Page({ params }: { params: Promise<{ item: string }> }) {
  const { item } = use(params);
  const itemCode = decodeURIComponent(item);

  return (
    <div className="flex flex-col gap-4">
      <PageHeader
        title={itemCode}
        subtitle="Review the AI-drafted content and photos before approving."
        action={
          <Button size="sm" variant="outline" asChild>
            <Link href="/os/channels/shopify/listings/enrichment">
              <ArrowLeft /> Queue
            </Link>
          </Button>
        }
      />
      <EnrichmentWorkspace itemCode={itemCode} />
    </div>
  );
}
