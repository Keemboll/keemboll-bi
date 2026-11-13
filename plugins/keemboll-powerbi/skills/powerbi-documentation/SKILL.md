---
name: powerbi-documentation
description: "Documentation of a Power BI project: data dictionary generated from the model (DATA_DICTIONARY.md), measure catalog, report sheet (pages, audience, question answered by each page, filters, known limits), release notes drawn from the change log, and handover file. Use to document a semantic model or a report, prepare a publication, an acceptance phase or a handover, fill in missing descriptions, or explain a model to a newcomer. Triggers: documentation, document, data dictionary, measure catalog, report sheet, release notes, handover, onboarding, missing description, glossary, lineage."
---

# powerbi-documentation — document without rewriting the model

Goal: anyone taking over the project understands **what each KPI measures, where it comes from and what each page is for**, without opening Power BI Desktop. Documentation is **generated** from the model wherever possible, and **written** only for what the model does not know (the business why, the audience, the limits).

Apply `powerbi-conventions` (mandatory descriptions, confidentiality of metadata, validation before any change) and `powerbi-tmdl` (writing `///` descriptions). **Read-only by default**: this skill only writes Markdown documentation files, after agreement.

## The deliverables

Default location: the project root, next to the `.pbip`, versioned with it (a `docs/` folder is also possible):

| File | Content | Origin |
|---|---|---|
| `DATA_DICTIONARY.md` | Tables, columns, measures and their DAX, relationships, roles, objects without a description | **Generated** by `lean.py catalog` |
| `REPORT.md` | Report sheet: audience, question answered by each page, filters, known limits | Written — [report-sheet-template.md](references/report-sheet-template.md) |
| `RELEASE_NOTES.md` | What changes for users at each publication | Drawn from `CHANGES.md` — [release-notes-template.md](references/release-notes-template.md) |
| `HANDOVER.md` | What one needs to know to take over the project | Written — [handover-template.md](references/handover-template.md) |

The **measure catalog** is not a separate file: it is the "Measures" sections of `DATA_DICTIONARY.md`, grouped by table and display folder. For a business audience, extract from it a *measure / definition / format* table without the DAX.

Do not duplicate what other files already hold: requirements and KPIs (`SCOPE.md`, `KPI.md` — skill `powerbi-project`), security (`SECURITY_MODEL.md` — `powerbi-governance`), tests and acceptance (`tests/`, `tests/ACCEPTANCE.md` — `powerbi-testing`), branches and deployment (`powerbi-alm`), debt and change log (`DEBT.md`, `CHANGES.md` — `powerbi-lean`). The documentation **points** to them.

## Generate the dictionary

The script belongs to the neighbouring skill `powerbi-lean` (same plugin), is read-only and writes to standard output:

```bash
python "<powerbi-lean skill folder>/scripts/lean.py" catalog "<project folder>"          # Markdown
python "<powerbi-lean skill folder>/scripts/lean.py" catalog "<project folder>" --json   # machine-readable output
```

On Windows `python` (or `py`), elsewhere `python3`. Redirect the output to `DATA_DICTIONARY.md` in UTF-8 (in Windows PowerShell 5.1, `>` writes UTF-16: use `| Out-File -Encoding utf8 DATA_DICTIONARY.md`), or read it back and write it with the file-writing tool.

The dictionary contains: counters, list of tables (type derived from the prefix, hidden or not), columns (type, description, hidden, aggregation, sort-by column, format), measures (description, format, hidden, used by the report, DAX), relationships (cardinality, cross-filtering, active), RLS roles and the **"Without a description"** section. The filter of a role that contains an e-mail address is not copied.

## Process

1. **Generate** `DATA_DICTIONARY.md` with `lean.py catalog`. Never write it by hand or from assumptions.
2. **Read the "Without a description" section** and present it to the user. For each object: ask for the business definition, or propose a wording **marked as a proposal** to validate. Never invent a definition.
3. **Fix in the model**: validated descriptions are written as `///` in the TMDL files (`powerbi-tmdl`), following the validation process of `powerbi-conventions`. Never in `DATA_DICTIONARY.md`.
4. **Regenerate** the dictionary; the "Without a description" section must have shrunk.
5. **Write or update** `REPORT.md` from the actual pages of the report (`lean.py usage` gives the fields per page and per visual) and from the user's answers about the audience and the questions.
6. **Before publication**: release notes from the `C-xxx` entries added since the last publication.
7. A single commit for the model change and the regenerated documentation.

## When to regenerate

- Before each publication (see `powerbi-alm`).
- After each `C-xxx` change that touches the model: measure, column, relationship, role, description.
- Before an acceptance phase or a handover.

A dictionary older than the last commit of the model is wrong: say so rather than use it.

## Rules

- **Source of truth = the model.** A wrong description is fixed in the TMDL, then the dictionary is regenerated. Any correction made directly in `DATA_DICTIONARY.md` will be lost.
- **Document the why, do not paraphrase the DAX.** "Customers who ordered at least once in the period, excluding internal accounts" — not "DISTINCTCOUNT of CustomerKey". The DAX is already in the dictionary.
- A measure description states: **business definition, calculation rule, scope, source**. A column description states what the value contains and its unit.
- **No real value** (amounts, names of customers or employees) and no personal data in the documentation: fictitious examples only. If the script reports a masked filter, do not go and copy it.
- **Flag** what is missing (description, format, owner of a KPI) rather than fill the gap with an assumption.
- "Used by the report: no" = not referenced by **this** report; another report connected to the published model may use it (see `powerbi-lean`).
- Vocabulary: reuse the labels of the model and of `KPI.md` verbatim; a KPI has only one name.
- No screenshot containing real data; prefer the mockup (`powerbi-mockup`) to illustrate a page.

## References

- [references/report-sheet-template.md](references/report-sheet-template.md) — report sheet, page by page.
- [references/release-notes-template.md](references/release-notes-template.md) — release notes for users.
- [references/handover-template.md](references/handover-template.md) — handover file.
