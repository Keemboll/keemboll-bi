---
name: powerbi-testing
description: "Tests, data quality and acceptance of a Power BI semantic model or report: model integrity (unique keys, blank keys, referential integrity, date table), reconciliation with the source, DAX measure tests, regression testing before / after a change, RLS role tests, report verification, the tests/ folder of DAX check queries and the tests/ACCEPTANCE.md acceptance record. Use it to verify a model or a measure, prove that a change broke nothing, test security, prepare or run an acceptance before publication. Triggers: test, tests, testing, verify, verification, check, data quality, reconciliation, regression, non-regression, acceptance, UAT, validation, EVALUATE, DAX query, check query, variance, discrepancy, before after values, referential integrity, duplicate key, orphan rows, test RLS, View as."
---

# Tests, data quality and acceptance

Goal: no publication without **proof** that the numbers are right, that the change broke nothing and that everyone sees only their own scope.

Applies `powerbi-conventions` (validation, confidentiality). Refers to: `powerbi-governance` (role design), `powerbi-performance` (slowness), `powerbi-lean` (`DEBT.md`), `powerbi-alm` (deployment, continuous integration), `powerbi-project` (phases, `KPI.md`), `powerbi-dax-library` (reference formulas).

## Rules

1. **Never claim to have verified** what was not executed. Without a DAX engine available, provide the queries for the user to run (DAX Studio, or the DAX query view of Power BI Desktop) and state it clearly: "not run".
2. A query executed by the agent (MCP server, XMLA endpoint) returns **real data**: ask for the user's agreement, limit it to the necessary aggregates, do not copy the results into files.
3. **No real sensitive value** in versioned files (`tests/`, `ACCEPTANCE.md`, `DEBT.md`): record *pass / fail* and the order of magnitude of the gap if useful, not the figures.
4. A failing test is **not** "fixed" **by changing the expected result**. Either the model is wrong, or the expected result was wrong and it is the business that says so.
5. The **expected result comes from the business or the source** (definition in `KPI.md`, total from the source system), never from the measure under test.
6. An unresolved, accepted gap goes into `DEBT.md` with its presumed cause; it is not passed over in silence.
7. **Acceptance signed by the business** before publication to production.
8. Tests are **read-only**: a check query never changes the model.

## The six levels

| # | Level | Question | When |
|---|---|---|---|
| 1 | **Model integrity** | Unique keys in dimensions? Blank keys? Does every fact find its dimension? Is the date table continuous and does it cover the facts? | After any model or source change; at every refresh if automated |
| 2 | **Source reconciliation** | Do the control totals per period equal those of the source system? | New model, new source, Power Query change |
| 3 | **Measures** | Known cases correct? Total = sum of details (if additive)? Edges: empty period, missing prior year, division by zero, multiple selection? | Any measure created or changed |
| 4 | **Regression** | Same query before and after: same values? | Refactoring, renaming, optimization, merging duplicates |
| 5 | **RLS / OLS** | Does each role see exactly its scope? Does the user with no rights see nothing? | Any change to a role, a security table or a relationship |
| 6 | **Report** | Filters, slicers, interactions, bookmarks, drillthrough, tooltips, displayed values = tested values? Acceptable load time? | Before acceptance |

Ready-to-adjust queries for each level: [references/check-queries.md](references/check-queries.md).

Details:

- **Level 1** — a duplicate key on the "one" side prevents the relationship; an orphan fact shows up under a **blank** row in visuals and distorts shares. The blank row is the symptom to look for.
- **Level 2** — reconcile at the **finest useful grain** (month × company, for example): a correct grand total can hide two errors that cancel out. Agree on a rounding tolerance. Default: 0.01 currency unit per control row.
- **Level 3** — a non-additive measure (distinct customer count, ratio, average) does **not** have to satisfy "total = sum of details": test its definition, not additivity.
- **Level 4** — capture the "before" **before** changing anything (backup commit, result kept outside the repository), or define the new version in the query with `DEFINE MEASURE` to compare both side by side.
- **Level 5** — a test run in the service by a workspace Admin, Member or Contributor proves nothing: RLS does not apply to them. Protocol below.
- **Level 6** — slowness is diagnosed with `powerbi-performance`. Default acceptance threshold: page displayed in under 5 s.

## RLS test protocol (per role)

1. List from `SECURITY_MODEL.md` (`powerbi-governance`): role, expected scope, test profile.
2. In Power BI Desktop: Modeling → **View as** → check the role (and "Other user" with a test UPN for a dynamic role). In the service: **Test as role** on the model's security. Beware with a dynamic role: in the service, this test uses the tester's own identity by default; pick a person under "Now viewing as" or, failing that, sign in with a test Viewer account. Labels vary by version.
3. Run the role's check query: list of visible values of the filtered dimension + total of the main measure.
4. Check: (a) visible scope = expected scope, no more, no less; (b) the total = sum of the authorized scopes only; (c) detail pages, drillthrough and export respect the filter.
5. Mandatory cases: user **missing** from the security table (sees nothing), viewer **attached to no role** (no data — to be tested with a real Viewer account, "View as" does not simulate it), user with **several scopes**, user who is a member of **two RLS roles** (union), "see everything" role if there is one.
6. OLS: check that the object is invisible and record which visuals fail with an error for this role.
7. Record in `tests/ACCEPTANCE.md` and carry the date over to `SECURITY_MODEL.md`.

## Organization in the project

```
<project>/
├── tests/
│   ├── T-001_key_integrity.dax
│   ├── T-010_reconciliation_monthly_net_sales.dax
│   ├── T-020_net_sales_py.dax
│   └── ACCEPTANCE.md
```

- One `.dax` file per test, named `T-xxx_<subject>.dax`; by default, numbering goes by tens according to the level.
- Mandatory header:

```dax
// WHAT: no duplicate customer in Dim_Customer.
// EXPECTED: zero rows.
EVALUATE
FILTER (
    SUMMARIZECOLUMNS ( Dim_Customer[CustomerKey], "Row Count", COUNTROWS ( Dim_Customer ) ),
    [Row Count] > 1
)
```

- Prefer tests that return **zero rows when all is well**: the result reads at a glance and can be automated (`powerbi-alm`).
- `tests/ACCEPTANCE.md`: acceptance record — case, expected, result, who, date, decision. Template: [references/acceptance-template.md](references/acceptance-template.md).

## Process

1. **Scope**: which change, which objects are touched (`powerbi-lean`, `usage` subcommand), which test levels apply.
2. **Write or reuse** the queries in `tests/`; show them before execution.
3. **Execute** (with agreement) or **hand over** the queries to the user; for a regression test, capture the "before" first.
4. **Compare** with the expected result; if there is a gap, look for the cause in this order: query filter → relationship / grain → Power Query → source → business definition.
5. **Record** in `ACCEPTANCE.md`; accepted gaps in `DEBT.md`.
6. **Report** a table test / level / result / run by (agent, user, not run), then a verdict: *ready for business acceptance* / *to be fixed*.

## Business acceptance

- Who: the business owner named in `SCOPE.md` (`powerbi-project`), not the report author.
- What: the cases of `ACCEPTANCE.md` readable by a non-technical person ("March net sales for the North region equal those of the management report").
- Decision: *accepted* / *accepted with reservations* (reservations → `DEBT.md` with a due date) / *rejected*.
- Without a written, dated decision: no release to production.
