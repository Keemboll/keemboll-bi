# AI readiness checklist

One line = one check. "Authoritative skill" is where the rule lives: this file says **what to check for AI**, not how to model, name or test. State of each line: *ok*, *gap*, *not applicable*, *not checked*.

Everything said about Prep data for AI reflects the Microsoft documentation at the time of writing (preview feature). Check the current pages before quoting a label, a limit or a prerequisite:

- "Prepare your data for AI" and its three sub-pages (AI data schemas, verified answers, AI instructions) — Power BI documentation.
- "Semantic model best practices for data agent" — Fabric documentation.

## Tier 1 — Model hygiene

Serves every consumer, including an external agent that only reads the metadata.

| # | Check | How to check | Authoritative skill |
|---|---|---|---|
| 1.1 | Every visible table, column and measure has a description that states the business meaning, not the name again | `lean.py catalog`, section "Without a description" | `powerbi-conventions` (rule), `powerbi-documentation` (dictionary) |
| 1.2 | Descriptions of measures give unit, currency, tax basis and sign convention when the name does not | Read the catalog | `powerbi-conventions` |
| 1.3 | Visible names are business terms users say, with no code or abbreviation | Read the catalog with the business owner | `powerbi-conventions` (and its restraint on renaming an existing model) |
| 1.4 | No two visible fields share a name across tables (`Name` in `Dim_Customer` and in `Dim_Product`), no measure named like a column | Read the catalog | `powerbi-conventions` |
| 1.5 | Keys, sort columns, flags and intermediate measures are hidden | `lean.py audit` | `powerbi-conventions` |
| 1.6 | Star schema; no ambiguous relationship path; bidirectional and many-to-many relationships justified | Model review | `powerbi-data-modeling` |
| 1.7 | One marked date table; when the fact has several dates (`Fact_Sales[OrderDate]`, `Fact_Sales[DeliveryDate]`), the default one is documented | Model review | `powerbi-data-modeling` |
| 1.8 | Every figure users ask for is an explicit measure; numeric columns that must not be summed have their default summarization set to none | `lean.py audit` | `powerbi-conventions` |
| 1.9 | No two measures compute the same or nearly the same thing under different names | `lean.py audit`, then reading | `powerbi-lean` |
| 1.10 | Unused tables, columns and measures are removed | `lean.py audit` and `usage` | `powerbi-lean` |
| 1.11 | Business logic sits in measures (or user-defined functions), not left to be rebuilt from columns | Compare `KPI.md` with the measures | `powerbi-dax-library`, `powerbi-dax-udf` |
| 1.12 | Patterns that confuse AI are identified: disconnected tables, field parameters (`Param_*`), calculation groups (`CG_*`), role-playing dimensions | Model review | `powerbi-data-modeling` |
| 1.13 | Measures answer fast enough for a conversation: generated queries run against the model as it is | Performance review | `powerbi-performance` |
| 1.14 | Report visuals have descriptive titles (the data agent documentation lists visual metadata among its inputs) | Report review | `powerbi-report-design` |
| 1.15 | No personal data, secret or internal-only remark in names and descriptions | Read the catalog | `powerbi-conventions`, `powerbi-governance` |

## Tier 2 — AI data schema

The subset of tables, columns and measures the AI should prioritize. Record the scope in the register of `AI_INSTRUCTIONS.md`.

| # | Check | Note |
|---|---|---|
| 2.1 | Prerequisites met | At the time of writing the Prep data for AI tabs require Q&A to be enabled on the model; a replacement setting is announced with the Q&A retirement. Check the documentation |
| 2.2 | Scope decided first: which questions the model must answer (`SCOPE.md`), which it must not | Decision of the business owner |
| 2.3 | **Included**: the measure of each approved KPI (`KPI.md`), the dimension attributes users name, the default date columns | |
| 2.4 | **Included**: the objects those measures depend on | The data agent documentation asks for dependent objects to be part of the schema |
| 2.5 | **Excluded**: intermediate and helper measures, keys, technical columns, duplicate or legacy measures, `Param_*` and `CG_*` tables | For an ambiguous term, keeping one measure and excluding the others is the most direct fix |
| 2.6 | Every field used by a verified answer, filters included, is in the schema and visible in the model | See tier 3 |
| 2.7 | In a Fabric data agent, the tables selected for the model match the AI data schema | Same documentation |
| 2.8 | The team knows what the schema does **not** cover | Per the documentation it applies to features that answer from the model schema, not to report-page creation or report summaries |

## Tier 3 — Verified answers

A verified answer ties trigger phrases to a specific visual. Record each one in the register of `AI_INSTRUCTIONS.md`: at the time of writing the documentation states they are not carried by Git integration, REST APIs or deployment pipelines, so the register is what allows them to be recreated in another environment.

| # | Check | Note |
|---|---|---|
| 3.1 | Candidates come from the top business questions of `SCOPE.md` and from questions scored `wrong` in the test set | Not one per visual |
| 3.2 | The visual is the approved one for that question and uses only model measures | The documentation excludes visuals built on report-level measures and several visual types; check the list |
| 3.3 | Triggers are complete questions, in the users' words, formal and conversational variants | Microsoft suggests five to seven per answer; check the current limits |
| 3.4 | Triggers contain no real customer, person or amount | Rule 4 of the skill |
| 3.5 | Filters users may change are declared on the answer; filters fixed at setup are intended | A fixed filter cannot be overridden by the user's question |
| 3.6 | No AI instruction contradicts a verified answer (a forced default filter, for example) | Conflicts make matching unreliable |
| 3.7 | After renaming a table, column or measure, the verified answers that use it are saved again | Same documentation |
| 3.8 | Verified answers are not counted as a security control | Roles are re-tested with `powerbi-testing` |

## Tier 4 — AI instructions

Template: [ai-instructions-template.md](ai-instructions-template.md).

| # | Check | Note |
|---|---|---|
| 4.1 | `AI_INSTRUCTIONS.md` exists, is versioned, and matches what is applied to the model | Compare with the dialog content, with the user |
| 4.2 | Every definition traces to a `K-xxx` of `KPI.md` or to `SCOPE.md` | No invented rule |
| 4.3 | Each ambiguous business term maps to exactly one model object | "sales" → `[Net Sales]` |
| 4.4 | Default date, period, calendar and currency are stated | |
| 4.5 | What must not be answered, and when to ask for clarification, is stated | |
| 4.6 | Instructions are short, grouped by theme, free of contradictions, and reference objects by their exact name | The documentation notes that instructions are interpreted, not guaranteed, and that long or conflicting ones degrade results. A character limit applies: check it |
| 4.7 | Model-specific instructions are in the model, not at the data agent level | Agent-level instructions are for cross-source guidance |
| 4.8 | No real value, personal data, secret or internal-only remark | Rule 4 of the skill |
| 4.9 | Q&A synonyms still useful have been carried into the glossary | Before the Q&A retirement |

## Tier 5 — Test set and approval

Template: [ai-question-set-template.md](ai-question-set-template.md).

| # | Check | Authoritative skill |
|---|---|---|
| 5.1 | `tests/AI_QUESTIONS.md` holds 15 to 30 questions confirmed by the business owner | this skill |
| 5.2 | A baseline run exists from before the changes | this skill |
| 5.3 | The last run is later than the last change to the model or to the AI settings | this skill |
| 5.4 | Pass rate meets the target (default: 90%), with no `wrong` on an approved KPI question | this skill |
| 5.5 | RLS / OLS tests re-run after the changes; the question set includes one question per profile | `powerbi-testing`, `powerbi-governance` |
| 5.6 | Results and the decision are recorded in `tests/ACCEPTANCE.md` | `powerbi-testing` |
| 5.7 | Approved for Copilot is set by the user, after 5.4 to 5.6 | `powerbi-governance` for who may decide |
| 5.8 | The question set is re-run after each release that touches the model | `powerbi-alm` |
