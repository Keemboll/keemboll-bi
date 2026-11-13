# `MIGRATION.md` template

One file at the project root, next to the `.pbip`, versioned with it. It tracks every asset from inventory to retirement. **No personal names** (owners by function), **no real values**, **no server names, paths with user names, workspace identifiers or connection strings**.

```markdown
# Migration — <programme name>

**Source platform**: <Tableau | Qlik Sense | Excel / Power Pivot | SSRS | PBIX | ...>
**Target**: <Name>.SemanticModel + reports (PBIP)
**Business owner**: <function, e.g. Head of Sales Controlling>
**Source archive**: <archive location described by function, e.g. "BI team archive share, folder Migration/2026">
**Status**: inventory | rationalised | mapping | rebuild | parity | parallel run | retired

## 1. Assets

| ID | Asset | Type | Owner (function) | Usage (last 90 days) | Refresh | Sources | Security | Embedded logic | Decision | Target | Mapping | Parity | Cut-over |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A-001 | Sales overview | dashboard | Sales Controlling | ~40 viewers / week | daily | ERP sales, CRM | by region | 12 calculated fields, 2 LOD | keep | Sales model / Overview page | done | passed | planned |
| A-002 | Sales by rep (copy) | dashboard | Sales Ops | 0 views | daily | ERP sales | none | copy of A-001 | retire | — | — | — | — |
| A-003 | Monthly sales pack | paginated | Finance | month-end only | monthly | ERP sales | by entity | print layout | keep (paginated) | paginated report | in progress | — | — |

Decision: `keep` / `merge into A-xxx` / `retire` / `to decide`. Only the business owner turns `to decide` into a decision.
Mapping / Parity / Cut-over: `—` / `to do` / `in progress` / `done` (`passed`, `accepted with differences`, `failed` for parity).

## 2. Shared models

| Model | Replaces | Grain | Storage mode | Reports connected |
|---|---|---|---|---|
| Sales | A-001, A-002 data sources | one row per order line | Import | Overview, Detail |

## 3. Calculation mapping

| Source calculation | Asset | Intent (business words) | Target object | Pattern | KPI | Test |
|---|---|---|---|---|---|---|
| `SUM([Sales])` | A-001 | Net sales excluding tax | `[Net Sales]` | measure | K-001 | T-010 |
| `{FIXED [Customer] : SUM([Sales])}` | A-001 | Total sales of the customer, whatever the view | `[Net Sales per Customer]` | LOD → CALCULATE | K-004 | T-021 |
| Manual target column | A-003 | Monthly sales target | `Fact_Budget` (owned reference table) | reference table | K-008 | T-030 |

## 4. Security

| Source rule | Target | Test |
|---|---|---|
| User filter on region | `RLS_Region` | T-050 |

## 5. Accepted differences

| ID | Asset | Difference (no values) | Cause | Accepted by (function) | Date |
|---|---|---|---|---|---|

## 6. Cut-over and retirement

| Asset | Parallel run from / to | Communication sent | Redirect | Old asset frozen | Access removed | Decommissioned |
|---|---|---|---|---|---|---|

## 7. Platform moves to plan

| Change announced by Microsoft | Affected assets | Doc checked on | Action | Due |
|---|---|---|---|---|
```

## Filling rules

- **Usage**: from an activity log, a server log or view counts, not from memory. Write the order of magnitude and the period; "unknown" is allowed and becomes a question for the owner.
- **Embedded logic**: count and name the calculations, filters, parameters, scripts and macros; their content goes to section 3, not here.
- **Security**: describe the rule ("each manager sees their region"), never the list of users.
- An asset with no owner cannot be `keep`: find an owner or propose `retire`.
