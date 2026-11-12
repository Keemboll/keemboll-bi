# KPI catalog — template for `KPI.md`

`KPI.md` is the **reference business definition** of each indicator: what the business approved, independently of the DAX. The measure's code stays in the model; the technical catalog of measures (generated from the model) belongs to `powerbi-documentation`.

## Statuses

| Status | Meaning | Who moves it |
|---|---|---|
| `proposed` | Definition drafted by the agent or analyst, not yet approved | — |
| `approved` | Definition, formula and thresholds approved by the owner | **The user / the KPI owner** |
| `implemented` | Measure created in the model **and** value checked (`powerbi-testing`) | The agent, after verification |
| `dropped` | Removed from scope; keep the entry and the reason | The user |

Only an `approved` KPI can be implemented. Changing the definition of an `implemented` KPI sets it back to `proposed` until it is approved again.

## Template

```markdown
# KPI catalog — <project name>

| ID | KPI | Status | Measure | Owner |
|---|---|---|---|---|
| K-001 | Net sales | implemented | `[Net Sales]` | Sales management |
| K-002 | Gross margin rate | approved | `[Gross Margin %]` | Finance management |

## K-001 — Net sales

- **Status**: implemented
- **Business question**: Q1 (see `SCOPE.md`)
- **Business definition**: amount excluding tax of the invoiced sales over the period, net of credit notes.
- **Formula in plain words**: sum of the net amounts of invoice lines − sum of credit notes.
- **Included / excluded**: includes inter-site sales; excludes orders not yet invoiced.
- **Target DAX measure**: `[Net Sales]`
- **Grain**: invoice line; analyzable by day, customer, product.
- **Variants**: prior year, year to date, % change (same definition, derived measures)
- **Source**: <invoicing system>, invoice lines table.
- **Owner**: <role or team>
- **Target / thresholds**: target = budget of the period; alert below 90% of the target — ADAPT.
- **Favorable direction**: increase
- **Format**: amount without decimals (see `powerbi-conventions`)
- **Approved on**: <yyyy-mm-dd> by <role>
```

## Rules

- Identifiers `K-001`, `K-002`... are **never reused**, even after a KPI is dropped.
- **Business definition**: one sentence understandable without knowing the model. **Formula in plain words**: in words, without DAX.
- **Included / excluded**: this is where disagreements hide (credit notes, taxes, intercompany, cancellations, incomplete periods). Ask the question rather than assume.
- **Target DAX measure**: name compliant with `powerbi-conventions`; look first for an existing pattern in `powerbi-dax-library`.
- **Target / thresholds** and **favorable direction**: provided by the owner; otherwise leave `TO CONFIRM` — do not invent a threshold.
- A derived KPI (prior year, year to date, % change) **has no entry of its own**: it inherits the definition of the base KPI; note it on the "Variants" line if useful.
- No real value in this file.
