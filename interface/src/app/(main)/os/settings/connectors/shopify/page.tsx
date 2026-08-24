import { PageHeader } from "@alaiy-os/layout/page-header";

import { ConnectorSettings } from "./_components/connector-settings";

export default function Page() {
  return (
    <div className="flex flex-col gap-4">
      <PageHeader title="Shopify Settings" subtitle="Connection, defaults, and sync behaviour for your Shopify storefront." />
      <ConnectorSettings />
    </div>
  );
}
