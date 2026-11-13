---
name: powerbi-tmdl
description: "Reading and editing Power BI semantic models in TMDL (Tabular Model Definition Language) inside a PBIP project: syntax, indentation, tables, columns, measures, relationships, Power Query partitions, calculation groups, DAX user-defined functions, RLS roles, descriptions and verification. Use whenever .tmdl files or a *.SemanticModel/definition folder are read, written, compared or fixed, or when working in the TMDL view of Power BI Desktop. Triggers: TMDL, .tmdl, PBIP, SemanticModel, definition, model.tmdl, relationships.tmdl, functions.tmdl, TMDL view, createOrReplace, lineageTag, git, model diff."
---

# TMDL — editing semantic models

Apply `powerbi-conventions` (naming, descriptions, approval). To publish to Fabric / the Power BI service, delegate to `semantic-model-authoring` (Microsoft) when installed; otherwise publish from Power BI Desktop.

## Structure of a PBIP project

```
SalesReport.pbip
SalesReport.SemanticModel/
├── definition.pbism
└── definition/
    ├── database.tmdl          # compatibility level
    ├── model.tmdl             # model options, culture, table order (ref table …)
    ├── relationships.tmdl     # all relationships
    ├── expressions.tmdl       # parameters and shared M queries
    ├── functions.tmdl         # DAX user-defined functions (compatibility level 1702 or higher) → see powerbi-dax-udf
    ├── tables/<Table>.tmdl    # one table per file: columns, measures, partitions, hierarchies
    ├── roles/<Role>.tmdl      # RLS
    └── cultures/<language>.tmdl # translations / Q&A synonyms
SalesReport.Report/            # report (PBIR) → see powerbi-report-cli
```

## Essential syntax rules

- **Indentation = structure.** Use **tabs**, consistently: object at level N, its properties at level N+1, a multi-line expression at level N+2.
- Declaration: `<type> <Name>`; with an expression: `<type> <Name> = <expression>`.
- Names with spaces or special characters go between **single quotes**: `measure 'Net Sales'`; a single quote inside the name is doubled: `'Customer''s Sales'`.
- Properties: `name: value`; boolean true = the property alone (`isHidden`); false = `isActive: false`.
- **Descriptions**: `///` lines right above the object.
- Column references in relationships: `Table.Column`, with single quotes if needed (`Fact_Sales.'Order Date'`).
- `lineageTag`: **never copy** the one of another object. For a new object, omit it (Power BI Desktop generates it) or create a fresh GUID.

Complete examples: [references/syntax.md](references/syntax.md).

## Editing process

1. **Synchronization with Power BI Desktop** (recent Desktop versions): **save** in Desktop before writing (the agent reads the files on disk, not the window). Two distinct mechanisms:
   - **Reloading external changes** (**preview** feature, Desktop **August 2026 or later**): turn on *Detect and reload external PBIP changes* (Options → Preview features, then restart Desktop). After writing, Desktop offers to **apply the external changes**. On an older version or without this option: **close Desktop** before writing.
   - **Desktop Bridge** (programmatic reload and screenshots for the agent): *Enable external tool access to Power BI Desktop through secure local APIs* in Options → **Security** → Desktop Bridge, **on by default**; the documentation also flags it as a preview.

   In every case, never save from Desktop while the agent is writing (overwrite).
2. Check that the project is under **Git** and that the tree is clean (`git status`) so the change can be rolled back.
3. Read `model.tmdl`, `relationships.tmdl` and the tables involved before writing.
4. Propose the changes (diff) and **wait for approval** for any deletion, rename or relationship change.
5. Write following the existing indentation of the file (tabs).
6. Adding a table: create `tables/<Name>.tmdl` and, if `model.tmdl` contains `ref table …` lines, add `ref table <Name>` to it.
7. **Rename**: update every reference (DAX measures, relationships, `sortByColumn`, hierarchies, roles, cultures, PBIR report). Search for the old name in the whole `definition/` folder **and** in `*.Report/`.
8. Apply the external changes (or reopen the `.pbip`): syntax errors show up on load. Fix them, then check the values with a DAX query.
9. `git diff` to review, then commit.

## TMDL view in Power BI Desktop

TMDL view is generally available in Power BI Desktop and in preview on the web (Power BI service); check the Microsoft documentation for the current status.

Alternative that does not require closing Desktop: **TMDL view** tab → drag an object from the Data pane to generate its `createOrReplace` script, edit it, then **Apply**. Handy for targeted changes; the PBIP files are updated on save.

## Common pitfalls

| Error | Cause | Fix |
|---|---|---|
| File rejected on open | Mixed spaces / tabs | Re-indent with tabs |
| Multi-line measure truncated to one line | Multi-line expression not indented enough | Expression at property level + 1 |
| Relationship ignored | Columns of different types or badly quoted name | Check `dataType` and the single quotes |
| Duplicate lineageTag | Copy-paste of an existing object | Delete the `lineageTag` line of the new object |
| Broken visuals after a rename | PBIR references not updated | Search for the old name in `*.Report/` |
