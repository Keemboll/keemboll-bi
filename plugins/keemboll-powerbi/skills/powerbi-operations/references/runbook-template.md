# `RUNBOOK.md` template

One `RUNBOOK.md` per BI product, at the project root, versioned with the `.pbip`. It answers one question: *what does someone who did not build this report need in order to keep it running?*

Rules:

- **No identifiers** (tenant, workspace, capacity, gateway, item), no connection strings, no secrets, no URLs containing an identifier.
- **No names of people and no e-mail addresses**: functions, teams and shared channels only. People change; the runbook should not.
- No real data values. Durations, sizes and thresholds are fine.
- Do not repeat what another file owns: point to `SCOPE.md` (need, freshness target), `SECURITY_MODEL.md` (roles and access), `RELEASE_NOTES.md` (versions), `DEBT.md` (known weaknesses).
- `TO CONFIRM` on anything unknown. An invented schedule is worse than a blank.

Copy from the line below.

---

```markdown
# Runbook — <product name>

**Last reviewed**: <YYYY-MM-DD> — **Next review**: <YYYY-MM-DD> (default: quarterly)
**Version in production**: <tag vX.Y.Z> — see RELEASE_NOTES.md

## 1. Owners by function

| Function | Team or role | Reached through |
|---|---|---|
| Business owner (decides on priorities, communication, retirement) | <role> | <channel> |
| BI developer (semantic model, reports) | <team> | <channel> |
| Data engineering (sources, pipelines) | <team> | <channel> |
| Platform admin (capacity, gateway, connections) | <team> | <channel> |
| User support (first contact) | <team> | <channel> |

Owner of the semantic model and of the scheduled refresh: <durable identity type: service account / service principal / named team account — never a personal account>.

## 2. What runs where

| Environment | Workspace (by name) | Capacity (by name or size class) | Storage mode |
|---|---|---|---|
| Dev | | | |
| Test | | | |
| Prod | | | |

Distribution: <app name, audiences — detail in SECURITY_MODEL.md>.

## 3. Refresh

| Item | Schedule (time zone) | Expected duration | Investigate above | Type |
|---|---|---|---|---|
| <semantic model> | <e.g. daily 06:00 CET> | <e.g. 12 min> | <e.g. 25 min> | <full / incremental / Direct Lake framing> |

- **Freshness target** (from SCOPE.md): <e.g. data of day D-1 available by 08:00 on working days>.
- Incremental refresh: partition column <table[column]>, stored period <...>, refreshed period <...>.
- Triggered by: <service schedule / pipeline after upstream load>.

## 4. Upstream dependencies

| Source | Type | Loaded by | Ready at | Through gateway? | Owner function |
|---|---|---|---|---|---|
| <source system or lakehouse> | | <pipeline name> | <time> | <yes: gateway cluster by name / no> | Data engineering |

Parameters that differ per environment: <parameter names only, no values>.

## 5. Credentials and expiry

| What | Kind | Expires | Renewed by |
|---|---|---|---|
| <connection to source X> | <service principal secret / OAuth / key> | <YYYY-MM-DD or "no expiry"> | Platform admin |

## 6. Monitoring checks

| Check | How | Cadence | Threshold | Done by |
|---|---|---|---|---|
| Refresh status and warnings | Refresh history | Daily | Any failure or new warning | BI developer |
| Refresh duration | Refresh history, trend | Weekly | Above "Investigate above" | BI developer |
| Freshness | <test T-xxx in tests/> | Daily | Older than target | BI developer |
| Capacity utilisation, throttling | Capacity Metrics app | Weekly | Any throttling | Platform admin |
| Model size | <where> | Monthly | <threshold> | BI developer |
| Report opening time | Usage metrics | Monthly | <threshold> | BI developer |
| Gateway status and version | Gateway management pages | Weekly | Offline / unsupported version | Platform admin |
| Usage | Usage metrics, activity log | Monthly | See section 10 | BI developer |

## 7. Alert routing

| Alert | Sent to | Expected reaction |
|---|---|---|
| Refresh failure notification | <shared mailbox or group — never one person> | Triage the same working day |
| Freshness / business threshold alert | <channel> | |
| Capacity alert | <platform channel> | |

## 8. Known failure modes

| Symptom | Cause | Fix | Who | Last seen | Reference |
|---|---|---|---|---|---|
| <e.g. refresh fails on Monday> | <upstream weekly load ends late> | <re-run after 07:30> | BI developer | <YYYY-MM> | I-001, D-004 |

## 9. Incidents

- Severity scale and process: <default of the skill, or the team's own in TEAM_RULES.md>.
- User notice: <where it is posted: app notice, report banner page, channel>.
- **Rollback**: redeploy the previous tag — procedure in <release checklist / PR of the last release> (powerbi-alm). A rollback of the model does not restore data: plan a refresh.
- **Escalation**: support → BI developer → platform admin / data engineering → business owner; vendor support through <function that may open a ticket>.
- Post-incident notes: `incidents/`.

## 10. Reviews and lifecycle

| Review | Cadence | With | Last done |
|---|---|---|---|
| Health review | Monthly | BI developer | |
| Usage and access review | Quarterly | Business owner | |
| Runbook review | Quarterly, and after each incident | BI developer | |

Retirement rule: no views for <90 days (default)> → candidate, confirmed by the business owner. Seasonal use to rule out: <e.g. year-end closing>.
```
