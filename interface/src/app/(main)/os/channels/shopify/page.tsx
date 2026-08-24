import { PageHeader } from "@alaiy-os/layout/page-header";

import { SyncDashboard } from "./_components/sync-dashboard";

export default function Page() {
  return (
    <div className="flex flex-col gap-4">
      <PageHeader title="Shopify" subtitle="Sync status, live Shopify counts, and manual sync triggers." />
      <SyncDashboard />
    </div>
  );
}
