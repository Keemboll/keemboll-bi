# Refresh failure triage

How to go from a failed refresh to a confirmed cause, a fix, an owner and a prevention. The rules of [../SKILL.md](../SKILL.md) apply: read-only on production, no error text with personal data in versioned files.

Roles: **BI dev** (owns the semantic model and reports), **Data eng** (owns sources, pipelines, lakehouse / warehouse), **Platform admin** (owns capacity, gateways, connections, tenant settings), **Business owner** (decides on communication and priorities).

## Step 0 — before any hypothesis

1. **One model or several?** Several models failing together on the same gateway, source or capacity points away from the model.
2. **What changed?** `CHANGES.md`, `git log`, the last deployment date; on the source side, ask data engineering. A failure the day after a release is a release problem until proven otherwise.
3. **Failed, or completed with warnings?** A refresh can complete with warnings (for example a measure referencing a missing column): the data is loaded but some calculations may be broken. Treat a new warning as an incident to qualify, not as noise.
4. **Is the schedule still enabled?** The service disables a scheduled refresh after repeated consecutive failures ([Configure scheduled refresh](https://learn.microsoft.com/power-bi/connect-data/refresh-scheduled-refresh)). Fixing the cause does not re-enable it.
5. **Is the data wrong, or only late?** Decides the severity (S1 vs S2).

## Step 1 — classify by symptom

The error wording changes between versions: match on meaning, and check the current list in [Troubleshoot refresh scenarios](https://learn.microsoft.com/power-bi/connect-data/refresh-troubleshooting-refresh-scenarios).

### A. Access to the source

| Symptom | How to confirm | Usual fix | Who acts | Prevent recurrence |
|---|---|---|---|---|
| **Credentials rejected, expired token, access forbidden** | Data source credentials of the model show an error; password or secret changed; the owner of the model or connection left or lost access | Re-enter credentials; renew the secret; move ownership to a durable identity | Platform admin (BI dev if they own the connection) | Expiry dates in `RUNBOOK.md`, alert 30 days ahead; no personal account as owner of production refreshes; entry in `DEBT.md` if a personal account remains |
| **Credential error on a long load with OAuth** | Fails after a long, roughly constant duration, not at start | Shorten the load (folding, incremental refresh → `powerbi-power-query`) or change the authentication method | BI dev, Platform admin | Duration trend watched; alert when duration passes a threshold |
| **Gateway offline or unreachable** | Gateway shows offline in the gateway management pages; every model behind it fails | Restart or repair the gateway machine or service; fail over to another cluster member | Platform admin | Cluster with more than one member; gateway health check weekly |
| **Gateway outdated** | Gateway version is older than the supported versions ([monthly updates](https://learn.microsoft.com/data-integration/gateway/service-gateway-monthly-updates)); a refresh warning may announce it beforehand | Update the gateway | Platform admin | Monthly update in the platform calendar; read refresh warnings |
| **Data source not bound to the gateway / connection missing** | Model settings show no gateway or connection selected, typically after a deployment that changed a server or database parameter | Bind the connection for the target environment | Platform admin, BI dev | Step in the release checklist (`powerbi-alm`); parameters per environment documented in `RUNBOOK.md` |
| **Source unavailable** | Source was down, in maintenance or being loaded at refresh time; upstream pipeline failed or ran late | Wait and re-run once the source is ready (on explicit request) | Data eng | Schedule after the upstream load with a margin, or chain the refresh to the pipeline; dependency listed in `RUNBOOK.md` |
| **Source query timeout** | The same query is slow when run at the source; no folding, so the whole table is read | Restore query folding, filter earlier, add an index or a view at the source → `powerbi-power-query` | BI dev, Data eng | Duration trend; debt entry if the timeout was only raised |

### B. The data or its shape changed

| Symptom | How to confirm | Usual fix | Who acts | Prevent recurrence |
|---|---|---|---|---|
| **Column not found / renamed / removed** | Error names a column; compare the source schema with the query; ask what was released upstream | Restore the column at the source (preferred), or adapt the query and the model; check every measure and visual using it (`powerbi-lean`, `usage`) | Data eng, then BI dev | Schema contract with data engineering; a schema test in `tests/`; a view layer between source and model |
| **Type change / conversion error** | Error names a column and a value that does not convert (do not copy the value) | Fix at the source; otherwise handle the type explicitly in M → `powerbi-power-query` | Data eng, BI dev | Data-quality test on the column in `tests/` |
| **Duplicate value on the one-side of a relationship** (e.g. `Dim_Customer[CustomerKey]`) | Count keys at the source; see the query below | Deduplicate at the source; never "fix" by changing the relationship to many-to-many | Data eng | Uniqueness test per dimension key in `tests/` (`powerbi-testing`); see `powerbi-data-modeling` for SCD2 keys |
| **Completed, but numbers are wrong or rows are missing** | Reconcile totals with the source (`powerbi-testing`); look for a truncated or partially loaded source | Treat as **S1**; reload after the source is complete | Data eng, BI dev | Row-count and total reconciliation after each refresh; freshness and completeness alert |

Uniqueness check, run by the user in DAX query view or through the Microsoft skills when installed — it returns keys only, no personal data:

```dax
EVALUATE
FILTER (
    SUMMARIZECOLUMNS (
        Dim_Customer[CustomerKey],
        "Rows", COUNTROWS ( Dim_Customer )
    ),
    [Rows] > 1
)
```

On a model that refuses to load because of the duplicate, the check has to be run at the source instead.

### C. Limits of the platform

Limits depend on the licence and the capacity size and change over time: read the numbers in the documentation, do not quote them from memory.

| Symptom | How to confirm | Usual fix | Who acts | Prevent recurrence |
|---|---|---|---|---|
| **Out of memory during refresh** | Error mentions memory; model has grown; a full refresh needs room for the existing copy and the new one; workspace recently moved to another capacity | Reduce the model (columns, rows, cardinality → `powerbi-data-modeling`, `powerbi-performance`); refresh less at once (incremental refresh, less parallelism); only then a larger capacity | BI dev, Platform admin | Model size tracked monthly with a threshold in `RUNBOOK.md`; debt entry |
| **Refresh time limit reached** | Duration trend reaches the limit of the licence or capacity ([refresh scenarios](https://learn.microsoft.com/power-bi/connect-data/refresh-troubleshooting-refresh-scenarios)) | Incremental refresh, folding, smaller model → `powerbi-power-query` | BI dev | Alert when duration exceeds a share of the limit (default: 60 %) |
| **Too many refreshes at once** | Error says the capacity limit for refreshes is exceeded; other refreshes were running at the same time | Spread the schedules; refresh off-peak | Platform admin, BI dev | Refresh calendar per capacity; schedule recorded in `RUNBOOK.md` |
| **Capacity throttled, operations rejected** | Capacity Metrics app shows throttling at that time; error mentions capacity limits ([throttling](https://learn.microsoft.com/fabric/enterprise/throttling)) | Wait for the overload to burn down; remove the cause (see "Capacity watch" in the skill); scaling is a platform decision | Platform admin | Capacity alerts routed to the platform team; heaviest items reviewed monthly |
| **Capacity paused or workspace moved** | Capacity state; recent admin change | Resume or reassign; re-enable the schedule | Platform admin | Change announced to model owners; noted in `RUNBOOK.md` |

### D. Incremental refresh

Design rules: `powerbi-power-query`. Reference: [Troubleshoot incremental refresh](https://learn.microsoft.com/power-bi/connect-data/incremental-refresh-troubleshoot).

| Symptom | How to confirm | Usual fix | Who acts | Prevent recurrence |
|---|---|---|---|---|
| **First refresh after publish times out** | Only the initial load fails; queries are not folded, or history is very large | Restore folding; reduce the stored period; bootstrap the partitions through the XMLA endpoint where available | BI dev | Folding verified before release (`powerbi-alm` gate) |
| **Duplicate values or partition-key conflict** | The date used for partitioning was updated at the source, so a row now exists in two partitions | Refresh the affected historical partitions (needs partition-level tooling; on a shared capacity, a full reload); partition on a date that never changes | BI dev, Data eng | Partition column documented in `RUNBOOK.md` as immutable; uniqueness test |
| **History silently differs from the source** | Reconciliation by period shows a gap outside the refresh window | Refresh the affected partitions; widen the refresh window if late changes are normal | BI dev | Periodic reconciliation on closed periods; a scheduled full refresh (default: yearly) if the source rewrites history |
| **Policy lost after a deployment** | Partitions were replaced by the deployed definition | Redeploy without overwriting partitions (tooling-dependent — check the documentation of the deployment method) | BI dev | Step in the release checklist (`powerbi-alm`) |

### E. Direct Lake

`powerbi-direct-lake` is authoritative. Reference: [How Direct Lake works](https://learn.microsoft.com/fabric/fundamentals/direct-lake-how-it-works).

| Symptom | How to confirm | Usual fix | Who acts | Prevent recurrence |
|---|---|---|---|---|
| **Report shows old data although the lakehouse is up to date** | The model was not framed since the Delta tables changed; automatic updates are off, or were suspended after a failed refresh | A successful refresh (framing) resumes it — on explicit request | BI dev | Freshness check on the model, not only on the pipeline; framing as the last step of the pipeline when automatic updates are off |
| **Framing / refresh fails** | The Direct Lake section of the refresh history; a table or column was dropped or renamed, or a table exceeds the guardrails of the capacity | Restore the schema; optimise the Delta tables; adapt the model | Data eng, BI dev | Schema contract; table maintenance scheduled by data engineering |
| **Suddenly slow, no error** | Queries fall back to DirectQuery (where the model type allows fallback); fallback reason per table — see the query in [health-review-checklist.md](health-review-checklist.md) | Remove the fallback cause | Data eng, BI dev | Fallback check in the monthly review |

## Step 2 — after the fix

1. The refresh succeeds **and** the schedule is enabled.
2. The numbers are reconciled (`powerbi-testing`): totals, row counts, the period that was missing.
3. Users are told, in the channel where they were told about the problem.
4. The prevention is real: a test, an alert or a `D-xxx` entry — not a sentence in a chat.
5. `RUNBOOK.md` lists the failure mode under "Known failure modes".
