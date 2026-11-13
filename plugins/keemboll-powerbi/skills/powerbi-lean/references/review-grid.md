# Review grid for a PBIP diff

| # | Question | Where to look |
|---|---|---|
| 1 | Does a new measure recompute what an existing measure already does? | `tables/*.tmdl`: look for the same aggregate / the same column |
| 2 | Does a measure copy the logic of other measures instead of referencing them? | SWITCH, long IF chains |
| 3 | Hardcoded values added (dates, identifiers, data labels)? | DAX, M partitions |
| 4 | Documentation removed or missing (`///` description, `// WHAT:` / `// HOW:` / `// NOTE:` comment, format, folder)? | deleted lines of the diff |
| 5 | Rename: every reference updated (DAX, `*.Report/`, relationships, sort order, roles, cultures)? | `lean.py usage --field` on the old name |
| 6 | Relationship added or changed: direction, cardinality, bidirectional filtering justified? | `relationships.tmdl` |
| 7 | Duplicated `lineageTag` (copy-pasted object)? | new `lineageTag` lines |
| 8 | Objects created and never used? | `lean.py audit --changed` |
| 9 | Visuals: bound fields exist, titles phrased as questions, theme colours? | changed `visual.json` files |
| 10 | Secrets, e-mails or person names added (roles, parameters)? | `roles/`, `expressions.tmdl` |
