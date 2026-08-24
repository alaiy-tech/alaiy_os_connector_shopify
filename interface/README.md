# Shopify connector — frontend contribution

This app's slice of the Alaiy OS frontend. It is **not** a Next.js app of its
own: `src/` overlays path-for-path onto `alaiy_os/interface` at deploy time and
builds as part of that app. See
`alaiy_os/interface/CONNECTOR_TO_BASE_UI_COMPOSITION.md` for the architecture.

```
src/
├── app/(main)/os/channels/shopify/
│   ├── page.tsx              Dashboard: local + live Shopify stats, sync triggers, order backfill, sync log
│   ├── listings/              Every synced listing: search, status tabs, bulk enable, CSV export/import
│   ├── categories/            Shopify's standard taxonomy (read-only)
│   ├── collections/           Manual + smart collections
│   ├── locations/             Fulfillment locations, mapped to a warehouse in settings
│   └── tags/                  Tags Shopify has reported across products
├── app/(main)/os/settings/connectors/shopify/
│                              connection, defaults, sync behaviour, import/export filters, test connection
├── constants/shopify.ts       status → badge tone mappings, built on the base's STATUS_TONE
└── lib/frappe/shopify-sync.ts the API layer over this app's whitelisted methods
```

## Screens

These rebuild the Desk page (`/app/shopify`) and its sidebar (Dashboard,
Listings, Categories, Collections, Locations, Tags) on the platform's own
primitives; Settings replaces the Desk form for **Shopify Connector Settings**.

The Desk pages themselves still ship and still work — nothing here deletes them
yet.

Backend contract lives in `alaiy_os_connector_shopify/api/` (`sync.py`,
`export.py`, `update_listings.py`) and `alaiy_os_connector_shopify/shopify/sync_guard.py`.

## Where it sits in the sidebar

`interface.config.json` contributes a **Channels** group with the six screens
above — Shopify is a sales channel (`connector_type: "channel"` in
`connector_meta.py`), so its screens sit with the rest of storefront sync
rather than under procurement.

The composer merges that block into the base's sidebar. The base itself has no
idea this app exists.

## The settings screen

It sits at `/os/settings/connectors/shopify`, not beside the channel screens.
The base owns that namespace and indexes it under Settings → Connectors, so a
connector is configured from the same place as every other connector no matter
where the rest of its screens live.

It needs no endpoints of its own. The platform's connector API
(`alaiy_os.api.connectors`) is generic over `OS Connector Registry`: it reads
the field metadata and values of whatever settings DocType a connector
registered, writes them back, and runs that connector's own `test_method` — the
one this app declares in `connector_meta.py`. So the screen is pure frontend
over `@alaiy-os/frappe/connectors`.

The stored Client Secret and Webhook Secret never come back from the server —
the API answers only whether one is set — so leaving those fields blank on
save keeps the existing value.

Not covered yet: `sh_location_map` (a child table mapping warehouses to
Shopify locations) and `sh_access_token` (set by the OAuth flow, not typed in
by hand). Both are real follow-up work, not omissions by accident.

## Working on it

There is no `npm run dev` here. Compose a workspace and run the base's:

```bash
cd devbench
python3 devbench.py compose <client>
cd builds/<client> && npm run dev          # http://localhost:3000/os/channels/shopify
```

`tsconfig.json` in this directory is for your editor only; the typecheck that
counts is `npx tsc --noEmit` inside a composed workspace.
