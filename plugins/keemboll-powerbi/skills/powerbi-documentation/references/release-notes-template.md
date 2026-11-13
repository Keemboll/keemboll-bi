# RELEASE_NOTES.md template

Notes for the **users of the report**, written at each publication. They are built from the `C-xxx` entries of `CHANGES.md` (skill `powerbi-lean`) added since the previous publication: the change log is technical, the notes say what changes for the reader. Newest first.

```markdown
# Release notes — <report name>

## <version or publication date> · 2026-11-15

### New
- "Customer detail" page: customers tracked by segment. (C-014)

### Changed
- `Gross Margin %` now excludes credit notes: earlier values may differ. (C-012)

### Fixed
- The year-to-date total stopped at the last complete month. (C-013)

### Good to know
- <known limit, provisional KPI, action expected from the user>
```

## Procedure

1. List the `C-xxx` entries since the last publication (date or Git tag, see `powerbi-alm`).
2. Set aside those with no effect for the reader (refactoring, hiding, descriptions): they stay in the change log.
3. Rephrase each retained entry as a **visible effect**: which page, which KPI, what changes in how it reads.
4. Explicitly flag any **change of definition** of a KPI: it is the most important information in the notes.
5. Cite the `C-xxx` identifier for traceability.

## Rules

- Nothing in the notes that is not in `CHANGES.md`: if a change is missing there, complete the change log first.
- No real values; describe the direction of the change, not the amounts.
- Version numbering: that of the tags of `powerbi-alm` (default: `vX.Y.Z`), followed by the publication date.
