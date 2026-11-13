---
name: powerbi-data-modeling
description: "Dimensional data modeling for Power BI and Fabric: star schema design, choice of grain, fact tables and dimensions, surrogate keys, slowly changing dimensions (SCD), role-playing dimensions, many-to-many bridge tables, date table, storage mode choice (Import / DirectQuery / Direct Lake, summary only). Use to design, critique or rework a semantic model, or to turn source tables into an analytical model. Triggers: data modeling, star schema, fact, dimension, grain, relationship, cardinality, surrogate key, SCD, role-playing dimension, many-to-many, bridge table, snowflake, date table, storage mode, Kimball."
---

# Data modeling — Power BI

Also apply `powerbi-conventions` (naming, approval). To write the changes into a PBIP project, use `powerbi-tmdl`; to publish them, `semantic-model-authoring`.

## Design approach (Kimball, 4 steps)

1. **Business process**: which event is being measured? (sale, order, daily stock, support ticket).
2. **Grain**: what does **one row** of the fact table represent? Write it in one sentence ("one row = one invoice line"). Never mix two grains in the same table.
3. **Dimensions**: who, what, where, when, how? Each dimension describes the context of the fact at the chosen grain.
4. **Facts**: numeric measures consistent with the grain (additive, semi-additive like balances, non-additive like rates → to recompute as a DAX measure, never stored).

Deliver the design as a **table / type / grain / key / relationships** table and a diagram (Mermaid `erDiagram`) before changing anything.

## Rules

- **Star schema**: dimensions linked directly to facts, **1 → \*** relationships (dimension → fact), **single-direction filtering**.
- **No snowflake**: denormalize hierarchies (Product → Subcategory → Category) into a single `Dim_Product`.
- **No fact ↔ fact relationship.** Two facts share **conformed dimensions** (`Dim_Date`, `Dim_Product`).
- **Keys**: surrogate integers (`ProductKey`) on the model side; keep the business key as an attribute column. One "Unknown" row (key −1) per dimension for orphan facts.
- **Date table**: a continuous `Dim_Date` (from January 1st of the first year to December 31st of the last), one row per day, marked as the date table. See [references/dim-date.md](references/dim-date.md).
- **Columns**: load only useful columns; split date and time; round unneeded decimals.
- **Measures rather than calculated columns** for anything that aggregates.
- Transform upstream (source, Lakehouse/Warehouse, Power Query) rather than in DAX. `powerbi-power-query` is authoritative for transformation code (M, query folding).

## Special cases

| Situation | Solution | Details |
|---|---|---|
| Several dates on a fact (order, delivery) | Role-playing dimension: one active relationship + inactive ones activated by `USERELATIONSHIP` | [patterns](references/patterns.md#role-playing-dimensions) |
| Attribute history (customer region that changes) | SCD type 2: surrogate key per version + `StartDate` / `EndDate` / `IsCurrent` | [patterns](references/patterns.md#scd) |
| Many-to-many (customer ↔ accounts) | Bridge table + controlled filtering | [patterns](references/patterns.md#many-to-many) |
| Facts at different grains (monthly budget vs daily sales) | Separate fact tables, relationship at the common level (month) through a dimension column | [patterns](references/patterns.md#different-grains) |
| Header / detail (order / lines) | Flatten the header into the lines table; allocate header amounts if needed | [patterns](references/patterns.md#header--detail) |
| Small scattered attributes (flags) | "Junk" dimension or degenerate attributes in the fact | [patterns](references/patterns.md#junk-and-degenerate-dimensions) |

## Storage mode

Short summary to choose a mode; the star schema rules above apply to all of them.

| Mode | When | Watch points |
|---|---|---|
| **Import** | Default | Plan the refresh; incremental refresh on large facts |
| **Direct Lake** (Fabric) | Data already in Delta tables in a Fabric Lakehouse / Warehouse | Two variants (on OneLake, on SQL analytics endpoint) with different limits and fallback behavior; only Direct Lake on OneLake can be combined with Import tables; transformations done upstream in the Delta tables |
| **DirectQuery** | Strict real time, or volumes impossible to import | Performance depends on the source; limit visuals; aggregations |
| **Composite** | Mix: facts in DirectQuery + dimensions in Dual, or Direct Lake on OneLake tables + Import tables | DirectQuery variant: dimensions in **Dual** mode |

`powerbi-direct-lake` is authoritative for Direct Lake design details and limits (variants, fallback, guardrails, unsupported features): do not decide on Direct Lake from this table alone. Limits of every mode change: confirm them in the Microsoft documentation.

## Expected deliverables

1. Design table (tables, grain, keys, relationships).
2. Mermaid diagram of the target model.
3. List of gaps between the existing model and the target, prioritized.
4. Migration plan (order of changes, report impacts) — **user approval required** before execution.
