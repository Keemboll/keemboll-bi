# Scoping brief — template for `SCOPE.md`

To be filled in **with** the requester, in blocks of 3 to 5 questions. Whatever has no answer stays marked `TO CONFIRM`: invent nothing. No real values, no names of private individuals other than project owners, no tenant or workspace identifiers.

## Questions to ask

| Block | Questions |
|---|---|
| Audience | Who reads the report? How often, on which medium (screen, mobile, PDF export, meeting)? How familiar are they with the numbers? |
| Decisions | Which decisions must the report help make? What does the reader do when a number is bad? |
| Business questions | Which 3 to 7 questions does the report answer? (one question = one sentence ending with "?") |
| Scope | Which entities, how much history, which regions, which products? What is explicitly **out of scope**? |
| Sources | Where does the data come from (system, database, file)? Who owns it? Is it reliable, complete, documented? |
| Grain | What does one row of each source represent (an order line, a day × store...)? How far down does the reader want to drill? |
| Freshness | By what time must the data be up to date? How often is it refreshed? How much delay is acceptable? |
| Security | Who may see what? Personal or sensitive data? Filtering by scope (region, department)? |
| Success | How will we know the report is a success? Which report or file does it replace? |

The "grain" answers feed `powerbi-data-modeling`; "security" feeds `powerbi-governance`; "freshness" feeds `powerbi-alm` and `powerbi-performance`.

## Template

```markdown
# Scope — <project name>

**Requester**: <role or team>
**Business owner**: <role or team> — signs the acceptance (`powerbi-testing`)
**Technical owner**: <role or team>
**Date**: <yyyy-mm-dd>
**Status**: draft | approved on <yyyy-mm-dd> by <role>

## Audience

- <Who>, <frequency>, <medium>.

## Decisions to make

- <Decision the report informs>.

## Business questions

| # | Question | Planned page | KPI |
|---|---|---|---|
| Q1 | <Question?> | <page> | K-001, K-002 |

## Scope

- **Included**: <entities, history, regions>.
- **Out of scope**: <what will not be done, and why>.

## Sources

| Source | Content | Grain | Owner | Reliability |
|---|---|---|---|---|
| <system> | <tables / files> | <one row = ...> | <role> | <known / TO CONFIRM> |

## Freshness and refresh

- Data up to date by <time>, refreshed <frequency>, tolerated delay <duration>.

## Security

- Sensitivity level: <public / internal / confidential — ADAPT>.
- Personal data: <yes / no; which>.
- Filtering by scope: <rule in plain words> (details in `SECURITY_MODEL.md`).

## Success criteria

- <Verifiable criterion: "the 5 questions are answered in under 3 clicks">.

## Open points

| # | Point | Who decides | Due |
|---|---|---|---|
| 1 | <TO CONFIRM: ...> | <role> | <yyyy-mm-dd> |
```

## Rules

- A **business question with no KPI** or a **KPI with no question** is a signal: go back to the requester.
- The scope is **explicitly approved** (date and role in `Status`) before modeling. Any later change of scope is a new, dated decision.
- Three to seven questions per report; beyond that, propose splitting into several reports or several batches.
