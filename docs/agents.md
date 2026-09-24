# Agents

This connector owns **no** agent. It supplies Shopify's half of two agents that
`alaiy_os_agents` builds: the read-only question-answering agent, and the listing
channel.

| | `shopify` (the question-answering agent) | the listing channel |
|---|---|---|
| Owned by | `alaiy_os_agents` (`agent_id: shopify`) | `alaiy_os_agents` (`agent_id: listing`) |
| Declared in | `hooks.py: connector_agents` → `agent_export.py` | `hooks.py: listing_channels` → `listing/channel.py` |
| Prompt | the shared connector prompt in `alaiy_os_agents`, with `prompts/rules.md` handed over as `rules` | `prompts/listing.md`, handed over as `spec.rules` |
| Purpose | Answers questions about listings and sales | Writes an enriched listing for review |
| Tools | 17, all read-only bar a CSV export | 6 handlers, called by the host agent |

`alaiy_os_agents` reads the `connector_agents` hook and upserts the `OS Agent
Registry` row on every `bench migrate` (`registry.sync`), so editing a tool
description or `prompts/rules.md` and migrating is still the whole reconcile loop.
The model, the turn budget, the prompt structure and the reply contract are that
app's, decided once for every connector agent on the bench.

---

## The question-answering agent

One registry row whose `tools` child rows name `api/agent.py` functions as
dotted-path handlers. `agent_export.export()` declares them; `alaiy_os_agents`
writes the row. `alaiy_os/engine/factory.py` resolves the handlers and
`engine/executor.py` calls `handler(**input)`. Ask Alaiy reaches the agent by
delegating a question to it through `run_agent`; the tools themselves are not on
the chat surface.

This app still owns one piece of the row's lifecycle: `setup/install.py:
unregister_agent` drops it on uninstall. `alaiy_os_agents` cannot, because its
`registry.sync` does not prune rows a hook has stopped declaring.

### It changes nothing

No tool pushes, publishes, archives or starts a sync. `OS Agent Tool` has no
`effect` field, so nothing in a row can tell an orchestrator that a tool writes
to Shopify, and there is no per-tool toggle a site could use to switch one off.
Registering a push tool would hand an agent a publish button nobody granted and
nothing can take away.

The sync entry points are excluded for a different reason: they page whole
catalogues, already run on the scheduler, and enqueue rather than answer
(`trigger_product_import` has a four-hour timeout). They are jobs, not tool
calls. `get_orders_sync_status` and `get_catalog_health` are how the agent answers
questions about them.

`export_csv` is the single exception, and what it writes is a private File out of
rows the model already holds. It is gated on `File` create so a site can withhold
it by withholding that permission.

### Shopify has no listing issues

Worth stating plainly, because the sibling Amazon agent has `get_listing_issues`
and it is real there: Amazon adjudicates listings, suppresses them, and publishes
an issues feed per SKU.

**Shopify does none of that.** Two tools occupy the space and neither is
Shopify's opinion:

- `get_listing_gaps` — *this app's* judgement: no image, no description, no
  price, no product type, never pushed. Computed from the register.
- `get_listing_drift` — local data has changed since the last push, read out of
  the fingerprint `product/export.py` already stores. Free, exact, and unable to
  say which field.

`compare_listing` is the only tool that reads Shopify's live state, and it
excludes images and category from the diff by design — see `not_compared` on
every result.

### Sales figures are paid-only and gross

`shopify/order/pull.py` queries Shopify with `financial_status:paid`, so unpaid
and pending orders are absent from every sales figure regardless of the period
asked for. `sales.py:_coverage_note` says so on every result. See
[Orders](orders.md).

Fees are not deducted and refunds are counted, not netted.

---

## The listing channel

`alaiy_os_agents` owns a single channel-agnostic listing agent for the whole site.
Everything Shopify-specific it needs — the output fields, the prose rules, the
Python validator, and how to read a product and write an enriched listing —
arrives from here through the `listing_channels` hook. Core never learns that
Amazon keys its products by `sku` and Shopify by `item_code`; the wrappers in
`listing/channel.py` are the whole of that translation.

Adopted from the retired standalone `alaiy_os_agent_shopify_listing` app: the
enrichment tools (`listing/`), the image pipeline, and the four
`Shopify Enriched Listing` DocTypes.

**What deliberately did not come across** is the agent itself. The standalone app
registered its own `shopify_listing` agent and shipped a run-agent page, Enrich
buttons and a bulk-enrichment flow. Re-registering that here would put two listing
agents on one bench, which is what the migration existed to remove — so this app
provides the adapter and nothing else, and the host owns the run and the desk
surfaces. The Amazon connector draws the same line.

`listing/review.py` is the one exception, and it is not part of the agent: the
enriched-listing list view's bulk **Approve** is a human act on the review record,
and nothing in the adapter's handlers can reach it.

### The contract

`alaiy_os_agents/agents/listing/channels.py` is the authority. Two details worth
knowing before editing the adapter:

- Handlers are called with **keywords fixed by the host** — `fn(product=...)`,
  `fn(product=..., listing=...)`, `fn(product=..., enabled=..., image_urls=...)`.
  A wrapper named for this app's own vocabulary would `TypeError` mid-run.
- The host calls `validate` **itself** before `save_listing`, so `save_listing`
  here is a bare passthrough. There is no `has_image_step` key either; the host
  derives it from whether `prepare_images` is declared.

Shopify declares `prepare_images` (Amazon's producing side never moved across) and
declares no `health` handler, because there is no issues feed to report.

### validate()

`listing/validate.py` restates the prompt's rules as Python, and the host returns
its defects as an `is_error` tool result the model reads and fixes.

The duplication is deliberate. JSON Schema can say `maxLength: 320`; it cannot say
"no promotional filler from this list", "state the unit inside the value", or "the
SEO copy is not the on-page copy repeated" — and those are the rules a listing
gets embarrassed by. The prose is what gets it right the first time; the code is
what makes sure.

---

## Roles

`Shopify Manager` and `Shopify Viewer` are created on install by
`setup/install.py:_create_roles`, and granted read on this app's DocTypes through
permission rows in each doctype's JSON.

**Both halves are needed.** Creating the Role grants nothing on its own, and the
symptom of missing permission rows is not an error but an absence:
`factory.build_runnable` refuses the run and `chat/tools.py` silently drops every
tool from Ask Alaiy.

`Shopify Manager` additionally gates the live-Shopify tools through
`roles.require_manager()`. Those tools declare `required_permissions: []`, because
the field is a list of `{doctype, ptype}` and cannot express a role — what they
guard is Shopify's rate limit, not our data.

The connector's other ~29 whitelisted methods are **not** gated; tightening them
is a separate change, because `api/sync.py:get_dashboard_stats` has three live UI
callers and `api/webhooks.py:handle_webhook` authenticates by HMAC and must stay
`allow_guest`.

---

## Turning it on

`bench migrate` registers the agent, provided `alaiy_os_agents` is installed —
without it the `connector_agents` hook is never read and there is no agent. It
does not run until **two** rows are enabled:

1. `OS Connector Registry` → `shopify` → `is_enabled = 1`. `factory.build_runnable`
   throws when a tool's connector is disabled.
2. `OS Agent Registry` → `shopify` → `is_enabled = 1`. `alaiy_os_agents` inserts
   the row disabled and never sets this again; it is admin-owned (the Agents
   settings screen) and survives migrates by design.

The listing channel needs neither: it is reached through the host agent, so what
has to be enabled is `alaiy_os_agents`'s own `listing` row.

This is the usual cause of "I migrated and nothing happened".
