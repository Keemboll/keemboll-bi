# Post-incident note

One note per incident of severity S1 or S2 (default; S3 and S4 only if they recur). Default location: `incidents/I-001-<short-slug>.md` at the project root, numbered `I-001`, `I-002`… and versioned with the project.

Rules:

- **Blameless**: functions and systems, never names. "The schedule was changed without a check" — not who changed it.
- **No personal data, no real values, no identifiers.** No pasted error message or log extract: summarise the error category and name the objects (`Fact_Sales`, `Dim_Customer[CustomerKey]`, `[Net Sales]`). To express an impact, use a relative size ("totals overstated by about 3 % for one region"), not the figures.
- Written within a default of **5 working days** after resolution, by the person who led the fix, reviewed by someone else.
- An incident is **closed** only when the cause is recorded **and** the data is confirmed correct. A note with "cause: unknown" stays open, with a `D-xxx` entry for the investigation.

Copy from the line below.

---

```markdown
# I-001 — <one-line summary: what users saw>

| | |
|---|---|
| **Severity** | S1 / S2 / S3 / S4 |
| **Status** | open / closed |
| **Product** | <report or semantic model, by name> |
| **Version in production** | <tag vX.Y.Z> |
| **Detected** | <YYYY-MM-DD HH:MM, time zone> — by <alert / user report / review> |
| **Started** | <when the problem actually began, if different> |
| **Resolved** | <YYYY-MM-DD HH:MM> |
| **Data confirmed correct** | <YYYY-MM-DD> — test(s) T-xxx |

## Impact

- Who was affected: <audiences, number of users as an order of magnitude>.
- What they saw: <stale since ... / wrong totals on page ... / access error / slow>.
- Decisions possibly taken on wrong data: <yes / no / unknown — who was informed>.

## Timeline

| Time | Event |
|---|---|
| | <upstream change, refresh run, first report, notice posted, containment, fix deployed, verification> |

## Cause

- **Direct cause**: <what failed — category from the triage table>.
- **Why it was possible**: <missing test, missing alert, undocumented dependency, personal account as owner…>.
- **Why it was not detected earlier**: <...>.

## What was done

- **Containment**: <notice, pages withdrawn, rollback to tag ...>.
- **Fix**: <change C-xxx in CHANGES.md / action on the platform by which function>.
- **Verification**: <reconciliation performed — which totals against which source, test T-xxx; no values>.
- **Communication**: <who was told, where, when; resolution message sent>.

## Prevention

| Action | Type | Owner function | Tracked in | Due |
|---|---|---|---|---|
| <uniqueness test on Dim_Customer[CustomerKey]> | test | BI developer | tests/ T-xxx | |
| <freshness alert routed to the shared channel> | alert | Platform admin | D-xxx | |
| <refresh chained to the upstream pipeline> | design | Data engineering | D-xxx | |

RUNBOOK.md updated (section "Known failure modes"): yes / no.

## Not verified

<What could not be checked, and by whom it should be.>
```
