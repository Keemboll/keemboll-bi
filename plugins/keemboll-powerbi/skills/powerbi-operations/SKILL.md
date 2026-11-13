---
name: powerbi-operations
description: "Keep published Power BI content healthy after go-live: refresh monitoring, refresh failure triage, incident handling and post-incident notes, capacity and performance watch, usage and adoption, access reviews, retirement of unused reports, and the RUNBOOK.md of the project. Load it when a refresh failed or runs longer and longer, when users report stale or wrong numbers, when a capacity is throttled, when asked whether a report is healthy or still used, when preparing a monthly or quarterly health review, or when writing the runbook before handing a report over to support. It says what to watch, how often, who acts and what to record; the mechanics (APIs, monitoring tools) stay with the Microsoft skills or the portal. Triggers: operations, run, monitoring, refresh failed, refresh failure, scheduled refresh, gateway, capacity, throttling, Capacity Metrics, usage metrics, adoption, incident, outage, stale data, runbook, health check, alert, Activator, retire report, access review, support."
---

# powerbi-operations — keep published content healthy

This skill is authoritative for **phase 8 (Operations)** of `powerbi-project`: what to watch once a report is live, how to handle a failure, and when to retire content. Its deliverable is `RUNBOOK.md` at the project root. The **mechanics** (REST and admin APIs, Fabric CLI, monitoring items, notebooks) belong to the Microsoft Fabric skills when installed; otherwise to the Fabric portal, operated by the user. Apply `powerbi-conventions` before any write.

## When to use

- A refresh failed, was disabled, or takes longer every week; users report stale or wrong numbers.
- "Is this report healthy?", "is it still used?", "why is the capacity throttled?"
- Writing `RUNBOOK.md`, a post-incident note, or a monthly / quarterly health review.
- Not for: pre-release gates and rollback mechanics → `powerbi-alm`; diagnosing a slow measure or page → `powerbi-performance`; M and incremental refresh design → `powerbi-power-query`; Direct Lake framing and fallback → `powerbi-direct-lake`; role and audience design → `powerbi-governance`; the debt register → `powerbi-lean`.

## Rules for the agent

1. **Read-only on production.** Never trigger a refresh, change a schedule, take over a semantic model, change a gateway or data source binding, or modify access without an explicit request for **that precise action**. "Fix the refresh" is not such a request: diagnose, propose, wait.
2. **Refresh error messages and activity logs contain personal and sensitive data** (user e-mails, server names, data values). Ask for them with personal data removed; never copy them into versioned files — record the error *category* and the object names only.
3. **No tenant, workspace, capacity or gateway identifiers in `RUNBOOK.md`**, and no names of people: refer to each by name of the item and by role ("production workspace", "platform admin on call").
4. **An incident is closed when the cause is recorded and the data is confirmed correct** (reconciliation, `powerbi-testing`) — not when the refresh goes green.
5. **Wrong numbers are always more severe than stale numbers.** A stale report announces its age; a wrong one is trusted.
6. Say what could not be verified. The agent rarely sees the service: a diagnosis built on a pasted error message is a hypothesis until the owner confirms it.

## What to watch

Default cadences; the targets come from `SCOPE.md` (freshness) and are copied into `RUNBOOK.md`.

| Signal | Why | Where to look | Default cadence |
|---|---|---|---|
| Refresh success, warnings, **duration trend** | Duration creeping up is the early signal, long before the timeout | Refresh history of the semantic model; Monitoring hub | Daily (alert on failure), trend weekly |
| Data freshness vs target | A green refresh on an empty or late source is still stale | Freshness query in `tests/`; upstream pipeline status | Daily |
| Capacity utilisation and throttling | Overload delays, then rejects, operations | Fabric Capacity Metrics app; capacity events for alerts | Weekly; daily during an incident |
| Model size growth | Growth ends in memory errors at refresh | Capacity Metrics app (storage); workspace storage; Semantic Link | Monthly |
| Slow queries and visuals | Degradation is gradual and unreported | Report usage metrics (opening time); workspace monitoring | Monthly |
| Usage: views, distinct viewers, unused reports and pages | Adoption, and candidates for retirement | Report usage metrics; activity log / audit log | Monthly, reviewed quarterly |
| Gateway health and version | An offline or outdated gateway fails every refresh behind it | Gateway management pages | Weekly; before each monthly update |
| Expiring credentials and service principal secrets | Predictable failure with a known date | Data source credentials; the secret's expiry date in `RUNBOOK.md` | Monthly, alert 30 days ahead |
| RLS membership drift | People change jobs, groups do not | Security groups behind roles and app audiences | Quarterly |
| Orphaned content (owner left) | Refresh and credentials stop with the account | Semantic model owner; lineage / impact analysis view | Quarterly, and at each departure |

Tool by tool — what each one answers, its retention, what is preview, and the Microsoft Learn links: [references/health-review-checklist.md](references/health-review-checklist.md). Do not describe click-paths or API signatures from memory: labels move; point to the documentation.

Alerting: refresh failure notifications on the semantic model go to a **shared mailbox or group**, not to one person. Data-driven alerts (dashboard tiles) and Fabric Activator rules cover business thresholds and freshness; availability and licensing vary — check the documentation before promising one.

## Refresh failure triage

Classify the symptom first, then confirm before fixing. Detailed tables (how to confirm, usual fix, who acts, prevention): [references/refresh-triage.md](references/refresh-triage.md).

| Symptom family | First question | Usually acts |
|---|---|---|
| Credentials, expired token or secret | Did anything expire or did the owner change? | Platform admin |
| Gateway offline or outdated | Do other models on the same gateway fail too? | Platform admin |
| Source unavailable or timeout | Was the source up and loaded at that time? | Data engineering |
| Schema change at the source | Which column was renamed, removed or retyped? | Data engineering, then BI developer |
| Data error (duplicate key on the one-side, conversion error) | Which table, which key? | Data engineering |
| Memory or capacity limit, refresh time limit, concurrency | Did size, schedule or neighbours change? | BI developer, platform admin |
| Incremental refresh partition | Did a historical date change at the source? | BI developer |
| Direct Lake framing or fallback | Did the Delta tables change shape or size? | Data engineering → `powerbi-direct-lake` |

Repeated failures disable the schedule: after the fix, the schedule must be re-enabled by its owner — check it, do not assume.

## Incident process

Detect → qualify → communicate → contain → fix → verify → write up → prevent.

| Severity (default scale) | Definition |
|---|---|
| **S1** | Wrong numbers visible to users, or a security exposure (data shown to someone who should not see it) |
| **S2** | Data stale beyond the freshness agreed in `SCOPE.md` |
| **S3** | Degraded performance; report usable |
| **S4** | Cosmetic |

1. **Qualify**: severity, who is affected, since when. When unsure between wrong and stale, treat as S1.
2. **Communicate** before fixing: the business owner and the support channel named in `RUNBOOK.md`; for S1 and S2, a visible notice on the report or app.
3. **Contain**: S1 — withdraw or flag the affected pages, or roll back to the previous tag (`powerbi-alm`); a security exposure goes to `powerbi-governance` and the organisation's security process at once. S2 — state the date of the data on the report.
4. **Fix** in dev, promote through the normal path (`powerbi-alm`). No direct edit in production, incident or not.
5. **Verify the numbers** against the source (`powerbi-testing`), then tell users it is resolved.
6. **Write the post-incident note** ([references/incident-template.md](references/incident-template.md)) — blameless, no personal data, no real values.
7. **Record prevention**: a test in `tests/`, an alert, or an entry in `DEBT.md` / `CHANGES.md` (`powerbi-lean`). Add the failure mode to `RUNBOOK.md`.

## Capacity watch

- A capacity runs **interactive** operations (a user opens a report, a query) and **background** operations (refreshes, scheduled jobs). Their cost is **smoothed** over time, so a heavy refresh keeps weighing on the capacity after it ends.
- When smoothed usage exceeds what the capacity provides for long enough, **throttling** applies in stages: interactive operations are delayed, then rejected, then background operations are rejected too. Operations already running finish. The thresholds and durations change — read them in the [throttling documentation](https://learn.microsoft.com/fabric/enterprise/throttling), do not quote them from memory.
- Slowness is more often a design problem than throttling: confirm in the Capacity Metrics app before blaming the capacity.
- Levers, in this order: (1) fix the heaviest queries and refreshes (`powerbi-performance`); (2) spread refresh schedules away from peak hours and from each other; (3) reduce model size (`powerbi-data-modeling`, `powerbi-power-query`); (4) only then scale or move the workspace — a decision for the platform admin and the budget owner.

## Usage and lifecycle

- **Quarterly review** (default) of usage and access, with the business owner; monthly health review by the BI developer. Checklists: [references/health-review-checklist.md](references/health-review-checklist.md).
- **Retirement**: a report with no views over a default **90-day** window is a *candidate*, not a decision. The built-in usage metrics report keeps a shorter history than that: a 90-day statement needs retained activity-log history or the audit log. Rule out seasonal use (year-end, budget).
- Retirement steps: confirm with the owner → announce with a date → tag the PBIP state in Git as the archive (`powerbi-alm`) → remove from the app → delete after a grace period (default: 30 days). Each step in production is done by the user or on explicit request. Check downstream dependencies in the lineage / impact analysis view before removing a semantic model.
- **Access review**: app audiences, direct shares and the groups behind `RLS_<scope>` roles, against `SECURITY_MODEL.md`, with the business owner (`powerbi-governance` is authoritative for what the roles should be).

## Process

### "The refresh failed" / "is this report healthy?"

1. **Ask for**: the error text with personal data removed, the refresh history (status and duration of the recent runs), whether other models on the same gateway or source fail, and what changed recently — read `CHANGES.md` and `git log` yourself. Read `RUNBOOK.md` if it exists: the failure may be a known one.
2. **Classify** with the triage table; state the confirmation step for the top hypothesis rather than a list of guesses.
3. **Output**: a diagnosis table (symptom / likely cause / how to confirm / confidence), an action list **by owner** (BI developer, data engineering, platform admin, business owner), the severity, and **what could not be verified**.
4. Stop. Actions in production are taken by the user, or by the agent on explicit request, one action at a time.

### Writing or updating `RUNBOOK.md`

Fill [references/runbook-template.md](references/runbook-template.md) from `SCOPE.md`, `SECURITY_MODEL.md`, `RELEASE_NOTES.md` and the user's answers. Mark `TO CONFIRM` whatever has no answer; invent no schedule, no duration, no contact. Update it after each incident and at each review.

## References

- [references/runbook-template.md](references/runbook-template.md) — `RUNBOOK.md` template.
- [references/refresh-triage.md](references/refresh-triage.md) — refresh failure decision tables.
- [references/incident-template.md](references/incident-template.md) — post-incident note.
- [references/health-review-checklist.md](references/health-review-checklist.md) — monthly and quarterly reviews, monitoring tools, read-only queries, Microsoft Learn links.
