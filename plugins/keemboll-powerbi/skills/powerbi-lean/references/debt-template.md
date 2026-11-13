# DEBT.md template

Goes at the project root, next to the `.pbip`. Versioned with the project.

```markdown
# Technical debt — <project name>

## Open

### D-003 · Hardcoded value in [Gross Margin]
- **Object**: `_Measures[Gross Margin]`
- **Shortcut**: product category identifier `= 16` hardcoded.
- **Why**: reference table of categories not available yet.
- **Planned fix**: add the category to `Dim_Product` and filter by code.
- **Priority**: medium · **Due**: 2026-12-31
- **Added on**: 2026-10-13 · **By**: <name>

## Closed

### D-002 · Duplicate measures
- **Closed on**: 2026-10-20 · **Change**: C-002

### D-001 · Date table not marked
- **Closed on**: 2026-10-15 · **Change**: C-001
```

Rules: one identifier per entry (D-001…, next number given by `python lean.py debt <project>`), a mandatory "why" line, a realistic due date. A closed entry always points to its entry in `CHANGES.md` ([template](changes-template.md)). Never copy data (real values, names) into this file.
