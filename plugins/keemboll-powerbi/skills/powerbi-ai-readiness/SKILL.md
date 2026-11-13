---
name: powerbi-ai-readiness
description: "Make a Power BI semantic model ready to be queried by AI: Copilot in Power BI, Fabric data agents and external agents reaching the model through an MCP server. Covers the readiness checklist (model hygiene, AI data schema, verified answers, AI instructions), the versioned AI_INSTRUCTIONS.md file, the tests/AI_QUESTIONS.md question set scored before and after each change, and the conditions for marking a model Approved for Copilot. Load it when users will ask questions in natural language, when AI answers are wrong or inconsistent, before exposing a model to a data agent, or to move Q&A synonyms to Prep data for AI. Not for writing a model with AI assistance. Triggers: Copilot, Prep data for AI, AI data schema, verified answers, AI instructions, data agent, Fabric data agent, AI-ready, AI readiness, natural language, Q&A, synonyms, semantic layer, MCP, agentic BI, Approved for Copilot."
---

# powerbi-ai-readiness — a semantic model that AI can query

Goal: when a user asks a business question in natural language, the AI consumer picks **the right measure, the right date and the right filters**. The semantic model is the grounding layer: answer quality depends on its metadata far more than on the prompt. AI output is non-deterministic: this work **improves** answers, it never guarantees them.

Three consumers, one model:

| Consumer | What it reads |
|---|---|
| Copilot in Power BI | Model metadata + the **Prep data for AI** settings saved on the model |
| Fabric data agent | The same metadata and Prep data for AI settings. Per the Microsoft documentation, its DAX generation ignores instructions written at the agent level: the work belongs **in the model** |
| External agent through an MCP server | Names, descriptions, relationships, DAX. Do not assume it reads the Prep data for AI settings: tier 1 below is what serves every consumer |

Prep data for AI is a **preview** feature at the time of writing: labels, limits and prerequisites move. Check the current Microsoft documentation ("Prepare your data for AI", "Semantic model best practices for data agent") before asserting any of them.

## When to use it

- Users will query the model with Copilot, a data agent or another agent, or already do and get wrong or inconsistent answers.
- Before marking a model **Approved for Copilot**, or before adding it to a data agent.
- To move a Q&A linguistic schema (synonyms) to Prep data for AI: the legacy Q&A feature is announced for retirement (the Microsoft pages give dates between December 2026 and February 2027 at the time of writing; to be confirmed there).
- Do **not** use it for: building a model or a report with AI assistance (authoring is not this skill); who may access the model, sharing, endorsement, sensitivity (`powerbi-governance`); removing unused or duplicate objects (`powerbi-lean`); naming and description rules (`powerbi-conventions`); the data dictionary (`powerbi-documentation`); role and acceptance tests (`powerbi-testing`).

## Rules

1. **Never change** the AI data schema, verified answers, AI instructions or the Approved for Copilot setting without an explicit request. Default mode is read-only: inventory, gap list, plan.
2. **`AI_INSTRUCTIONS.md` at the project root is the source of truth** for AI instructions, versioned with the `.pbip`. The text is applied to the model by the user (pasted in the Prep data for AI dialog) or by tooling when available; the model is never edited first and the file "caught up" later.
3. **Business definitions come from `KPI.md`** (`powerbi-project`). The agent never invents a definition, a synonym, a fiscal calendar or a default filter: a missing one is marked `TO CONFIRM` and asked.
4. **No real values, no personal data, no secrets, no internal-only remarks** in descriptions, AI instructions, trigger phrases or the question set. Metadata lives in the model and in Git and is readable by whoever can read them, even where the product does not display it to report consumers.
5. **Never claim an improvement without running the test set** before and after. Without access to the AI consumer, the agent hands the questions to the user and writes "not executed".
6. **AI readiness is not security.** RLS and OLS keep applying to AI-generated queries: a consumer only gets what the user may see. But at the time of writing Microsoft states that verified answers must not be relied on as a security feature. Re-test the roles (`powerbi-testing`) after any change.
7. Model changes made for AI readiness (renames, hiding, descriptions) follow `powerbi-conventions`: approval, Git, and the "existing model" restraint on renames. When an object cannot be renamed, its description and the glossary of `AI_INSTRUCTIONS.md` carry the business term.

## The five tiers

Work in this order: each tier is worth less if the previous one is skipped. Every line, with how to check it and the authoritative skill: [references/readiness-checklist.md](references/readiness-checklist.md).

| # | Tier | What "ready" means |
|---|---|---|
| 1 | **Model hygiene** | Every visible table, column and measure has a description (`lean.py catalog` of `powerbi-lean`, section "Without a description"); unambiguous business names, unique across tables; technical objects hidden; star schema; one marked date table; explicit measures; no duplicate measure logic; unit and currency in the name or the description |
| 2 | **AI data schema** | A focused subset: approved KPI measures, the attributes users name, and the objects those measures depend on. Excluded: helper measures, keys, duplicates, `Param_*` and `CG_*` tables |
| 3 | **Verified answers** | One per top business question of `SCOPE.md` that the AI gets wrong or that must always be answered the same way; triggers written as complete questions |
| 4 | **AI instructions** | `AI_INSTRUCTIONS.md`: purpose, glossary, time and currency defaults, measure to use for each ambiguous term, what not to answer |
| 5 | **Test set and approval** | `tests/AI_QUESTIONS.md` run, pass-rate target met, RLS re-tested, then Approved for Copilot, decided by the user |

Two points that are easy to miss:

- **Hiding and verified answers pull in opposite directions**: at the time of writing a verified answer does not work when it uses a field hidden in the model or left out of the AI data schema. Hide helpers, not the fields a verified answer shows or filters on.
- **Package business logic in measures** (and in DAX user-defined functions where the project uses them, see `powerbi-dax-udf`). Practitioners report that an AI consumer which only has to pick `[Net Sales]` has less room to get the logic wrong than one which rebuilds it from columns. This is field advice, not a Microsoft guarantee.

## Test protocol

`tests/AI_QUESTIONS.md` holds the question set; template: [references/ai-question-set-template.md](references/ai-question-set-template.md).

1. **15 to 30 real business questions**, taken from `SCOPE.md` and from what users actually ask, in their words. Include ambiguous terms, time questions, a few questions the model must **not** answer, and at least one per RLS profile.
2. Each question states the **expected measure, filters and answer shape** (a number, a table by month, a refusal, a clarifying question). Never a real value.
3. **Run the whole set before and after each change** (one tier, or one edit of `AI_INSTRUCTIONS.md`), on the same consumer, in a fresh session per run. Changes take time to propagate: follow the documented delay before re-testing.
4. **Score each question**: `pass` (right measure, filters and shape, or the expected refusal), `wrong` (an answer built on the wrong object or filter, the dangerous case), `refused` (no answer where one was expected). Judge the generated DAX or the "how the answer was produced" detail when the consumer shows it, not only the wording. Default: a question whose result changes between two runs is scored `wrong`.
5. **Record** date, consumer, pass rate and the questions that changed status in `tests/ACCEPTANCE.md` (file owned by `powerbi-testing`, whose rules on real values apply).
6. **Approved for Copilot only when** the pass rate meets the target (default: 90% of the set, and no `wrong` on a question tied to an approved KPI), the RLS tests have been re-run, and the user decides. A regression after a change means the change is reverted or fixed, not that the expected answer is edited.

## Process

1. **Inventory** (read-only): `lean.py catalog` and `lean.py audit` (`powerbi-lean`), existing Prep data for AI settings and Q&A synonyms (ask the user when they cannot be read from the project files), `SCOPE.md`, `KPI.md`, `SECURITY_MODEL.md`.
2. **Gap list** per tier against the checklist; what belongs to another skill is named with that skill.
3. **Plan**: objects changed, AI settings changed, expected effect on which questions, impact on reports for any rename or hiding. Draft `tests/AI_QUESTIONS.md` and get it confirmed by the business owner.
4. **Wait for approval.**
5. **Baseline**: run the question set before touching anything.
6. **Execute tier by tier**, model changes through the authoritative skills; AI settings applied by the user, or by tooling when installed and authorized.
7. **Test** after each tier; **record** in `tests/ACCEPTANCE.md`; unresolved gaps go to `DEBT.md` (`powerbi-lean`).
8. **Summarize**: tier / state / pass rate before and after / executed by (agent, user, not executed) / open points.

## Deliverables

| File | Content | Owner |
|---|---|---|
| `AI_INSTRUCTIONS.md` | Instructions applied to the model + register of the AI data schema scope and of the verified answers | this skill |
| `tests/AI_QUESTIONS.md` | Question set and run history | this skill |
| `tests/ACCEPTANCE.md` | Results and approval decision | `powerbi-testing` |
| Model descriptions, names, visibility | In the TMDL | `powerbi-conventions`, `powerbi-tmdl` |

## References

- [references/readiness-checklist.md](references/readiness-checklist.md) — the detailed checklist, with how to check each line and the authoritative skill.
- [references/ai-instructions-template.md](references/ai-instructions-template.md) — `AI_INSTRUCTIONS.md` template and a short example.
- [references/ai-question-set-template.md](references/ai-question-set-template.md) — `tests/AI_QUESTIONS.md` template and scoring.
