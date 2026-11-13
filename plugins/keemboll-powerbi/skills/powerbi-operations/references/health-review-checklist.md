# Health review — checklists, tools and read-only queries

Two reviews by default: **monthly** (technical, BI developer) and **quarterly** (usage, access and lifecycle, with the business owner). The agent prepares the review from what the user provides and from the repository; it reports each line as *checked* / *not checked* / *finding*, and never ticks a line it could not verify.

Findings go to `DEBT.md` (`powerbi-lean`); nothing is fixed during the review itself.

## Monthly review

**Refresh**
- [ ] No failed refresh left unexplained since the last review; every failure has a cause recorded.
- [ ] No new "completed with warnings".
- [ ] Duration trend flat, or the increase explained; below the "investigate above" value of `RUNBOOK.md`.
- [ ] Schedule enabled; still placed after the upstream load.
- [ ] Freshness target of `SCOPE.md` met on every working day of the period.

**Capacity and performance**
- [ ] No throttling on the capacity during the period; this product is not among the heaviest items, or it is and there is a `D-xxx`.
- [ ] Model size below the threshold of `RUNBOOK.md`; growth rate noted.
- [ ] Report opening time stable. A page that became slow → `powerbi-performance`.
- [ ] Direct Lake models: no unexpected fallback (`powerbi-direct-lake`).

**Platform**
- [ ] Gateway online and on a supported version.
- [ ] No credential or secret expiring within 60 days without a renewal planned.
- [ ] Semantic model and connections still owned by a durable identity.

**Project hygiene**
- [ ] `RUNBOOK.md` reflects reality (schedule, durations, owners by function).
- [ ] Open incidents have an owner; prevention actions of closed incidents are done or tracked.
- [ ] `powerbi-lean` debt status reviewed.

## Quarterly review (with the business owner)

**Usage and adoption**
- [ ] Views and distinct viewers per report, trend over the quarter, against the audience expected in `SCOPE.md`.
- [ ] Pages with no or almost no views: remove, merge or explain.
- [ ] Reports with no views over the retirement window (default: 90 days): candidates listed, seasonal use ruled out, decision taken by the owner.
- [ ] Questions the report was built for (`SCOPE.md`, `KPI.md`) still current.

**Access**
- [ ] App audiences and direct shares match `SECURITY_MODEL.md`.
- [ ] Membership of the groups behind each `RLS_<scope>` role reviewed by the business owner: leavers and movers removed.
- [ ] Workspace roles: no more admins and members than needed; no departed account.
- [ ] RLS still tested after any role change (`powerbi-governance`, `powerbi-testing`).

**Lifecycle**
- [ ] Orphaned content: items whose owner left, personal workspaces feeding production.
- [ ] Downstream dependencies of the semantic model known (other reports, other workspaces) before any change or retirement.
- [ ] Retirements in progress: announced, archived by tag, removed from the app, deleted after the grace period.
- [ ] Next review date written in `RUNBOOK.md`.

## Where to look — the Microsoft tools

Names, availability, licences and retention **change**: the links are the reference, not this table. Items marked *preview* were in preview when this file was written. Never describe a click-path from memory.

| Tool | Answers | To know | Documentation |
|---|---|---|---|
| Refresh history of the semantic model | Status, start, duration, error and warnings of each refresh | History is limited in depth; store the trend elsewhere if a long history matters | [Data refresh in Power BI](https://learn.microsoft.com/power-bi/connect-data/refresh-data) |
| Monitoring hub (shown as *Monitor* in the Fabric navigation) | Recent runs across items, including semantic model refreshes and their detail page | Shows what the signed-in user is allowed to see | [Monitoring hub](https://learn.microsoft.com/fabric/admin/monitoring-hub) |
| Refresh summaries (admin portal) | Refresh schedule and history across a capacity | Capacity admins | [Refresh summaries](https://learn.microsoft.com/power-bi/connect-data/refresh-summaries) |
| Fabric Capacity Metrics app | Utilisation, throttling, heaviest items and operations, storage | Installed and read by capacity admins; recent days only; **does not send alerts**; may show user e-mails | [Capacity Metrics app](https://learn.microsoft.com/fabric/enterprise/metrics-app) |
| Capacity events (Real-Time hub) | Alerts on capacity state and thresholds | The way to be alerted on capacity health | [Capacity overview events](https://learn.microsoft.com/fabric/real-time-hub/explore-fabric-capacity-overview-events) |
| Report usage metrics (*preview* for the current version) | Views, page views, distinct viewers, opening time, unused reports in the workspace | Short retention (30 days at the time of writing): export it to cover a quarter; per-user data can be masked by the tenant admin; contributors and above | [Usage metrics](https://learn.microsoft.com/power-bi/collaborate-share/service-modern-usage-metrics) |
| Activity log / audit log | Who did what on which item, tenant-wide | Fabric admins (activity log) or audit roles (audit log); retention differs between the two and is limited — a long history must be extracted and stored by the platform team; contains user e-mails | [Track user activities in Power BI](https://learn.microsoft.com/fabric/enterprise/powerbi/service-admin-auditing), [in Fabric](https://learn.microsoft.com/fabric/admin/track-user-activities) |
| Workspace monitoring (*preview*) | Query and refresh logs of semantic models, queryable in KQL | Must be enabled per workspace, consumes capacity, no backfill, limited retention; logs can contain sensitive data — restrict access | [Workspace monitoring](https://learn.microsoft.com/fabric/fundamentals/workspace-monitoring-overview) |
| Lineage view and impact analysis | Upstream sources and downstream reports of an item; notify the contacts of affected workspaces | Use before any change or retirement of a shared semantic model | [Data lineage](https://learn.microsoft.com/power-bi/collaborate-share/service-data-lineage), [Impact analysis](https://learn.microsoft.com/fabric/governance/impact-analysis) |
| Data alerts on dashboard tiles | Notification when a card, KPI or gauge passes a threshold | Personal to the user who sets them; evaluated when data refreshes | [Data alerts](https://learn.microsoft.com/power-bi/create-reports/service-set-data-alerts) |
| Fabric Activator | Rules on report visuals or queries, with notifications or actions | Needs a Fabric capacity; alerts set from reports were in *preview* | [Activator](https://learn.microsoft.com/fabric/real-time-intelligence/data-activator/activator-introduction) |
| Gateway management pages | Gateway cluster and member status, version, connections | Gateway admins | [Troubleshoot the on-premises data gateway](https://learn.microsoft.com/data-integration/gateway/service-gateway-tshoot) |
| Semantic Link in notebooks | Scripted checks: refresh history, model metadata, DAX queries, on a schedule | Needs a Fabric capacity; a scheduled notebook is itself a production item to own and monitor | [Semantic link](https://learn.microsoft.com/fabric/data-science/semantic-link-overview) |

If the Microsoft Fabric skills or a Power BI MCP server are installed, the agent may use them **for reads** on request. Otherwise the user reads the tool and reports the result with personal data removed.

## Read-only DAX queries

Run by the user in DAX query view (or through the Microsoft skills when installed). They read metadata or one aggregate; they change nothing. The `INFO` functions need sufficient permissions on the semantic model — see [INFO functions](https://learn.microsoft.com/dax/info-functions-dax). **Model size is not available this way**: use the Capacity Metrics app, the workspace storage view or Semantic Link.

Freshness and volume of the fact table — compare with the target of `SCOPE.md` and with the previous review:

```dax
EVALUATE
ROW (
    "Last order date", MAX ( Fact_Sales[OrderDate] ),
    "Row count", COUNTROWS ( Fact_Sales )
)
```

Tables and their storage mode — an unexpected mode after a deployment is a finding:

```dax
EVALUATE
SELECTCOLUMNS (
    INFO.VIEW.TABLES (),
    "Table", [Name],
    "Storage mode", [StorageMode],
    "Hidden", [IsHidden]
)
ORDER BY [Table]
```

Relationships — an inactive or unexpected relationship after a deployment:

```dax
EVALUATE
SELECTCOLUMNS (
    INFO.VIEW.RELATIONSHIPS (),
    "Relationship", [Relationship],
    "Active", [IsActive],
    "State", [State]
)
```

Measures and their state — a measure broken by a schema change shows here before a user finds it:

```dax
EVALUATE
SELECTCOLUMNS (
    INFO.VIEW.MEASURES (),
    "Measure", [Name],
    "State", [State]
)
ORDER BY [Measure]
```

Direct Lake only — fallback reason per table (column `[DirectLakeFallbackInfo]`; interpretation in `powerbi-direct-lake`):

```dax
EVALUATE
TABLETRAITS ()
```

## Review output

A short note, not a new file type: date, period covered, a table *check / status / finding / action / owner function*, the list of what was **not checked** and why, and the `D-xxx` entries created. Store it where the team keeps review notes (default: a dated section appended to `RUNBOOK.md` section 10, keeping the last four).
