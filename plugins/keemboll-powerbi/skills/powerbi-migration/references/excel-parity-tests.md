# Excel migration — parity tests

Excel workbooks are the most common migration source and the most fragile to prove: logic lives in cells, values can be typed over formulas, and the tool recalculates silently. This page lists the **Excel-specific** traps to test. The generic plan, tolerances, accepted differences and parallel run are in [parity-and-cutover.md](parity-and-cutover.md); test mechanics (query files, `tests/ACCEPTANCE.md`, RLS protocol) belong to `powerbi-testing` (`references/check-queries.md`).

## 1. Freeze the reference

The expected value comes from the **workbook**, never from the new measure (rule 5 of `SKILL.md`).

1. Archive the workbook untouched (rule 1) and work on a copy.
2. Decide with the owner which value is the reference: **what users saw in the archived original**, or the **fully recalculated** copy (force a full calculation and note the calculation mode). Record the choice in `MIGRATION.md`; a recalculation can change cached values, and in manual calculation mode cells can be stale.
3. Refresh external links and data connections, or record that they could not be refreshed (stale cached values are a finding).
4. Write down the filters and selections in force (hidden rows, autofilters, pivot slicers, as-of date).
5. Take the expected values from the sheet blocks under test at the finest useful grain, and keep them **outside the repository** (rule 4).

## 2. Catalogue of Excel traps

These entries are a **catalogue** (`X-01` to `X-13`), not test IDs. Each project turns the relevant ones into real tests numbered by the `powerbi-testing` scheme (`T-xxx`) and lists those IDs next to each mapped formula block in `MIGRATION.md` section 3. Counts, control totals and generic edge cases are already in `parity-and-cutover.md`.

| Entry | Trap to test | Expected from | Typical finding |
|---|---|---|---|
| X-01 | Blank rows, repeated headers or a totals row inside the data range | The sheet's data block | Totals row loaded as data |
| X-02 | Hidden rows and filtered ranges against the model's filter context (`SUBTOTAL` versus `SUM`) | Workbook with the same filters | `SUBTOTAL` always ignores filtered-out rows, and manually hidden rows only with function numbers 101-111: record which one is used. Filter context reproduces the first, not the second |
| X-03 | Hard-coded values typed over formulas in a range | Workbook block, cell by cell on a sample | Formula range with a few overridden cells |
| X-04 | Lookup keys: duplicates, missing keys, trailing spaces, numbers stored as text | Workbook lookup column | `VLOOKUP` returns a single match for a duplicated key (in practice the first), with no warning; a one-side key with duplicates is refused by the model, or needs a many-to-many relationship, which filters differently. Power Query and the model may compare text differently (case, trailing spaces): test keys on both sides |
| X-05 | Error values (`#N/A`, `#DIV/0!`) and `IFERROR` fallbacks | Workbook with the same inputs | Excel error replaced by `0` where the measure returns blank |
| X-06 | Blank, zero and empty string compared case by case | Workbook | Some DAX operations treat blank as 0 or as an empty string (see the Microsoft `BLANK` function remarks): check each against the workbook |
| X-07 | Dates stored as text or serial numbers, regional formats, as-of date (`Dim_Date[Date]`, `Fact_Sales[OrderDate]`) | Workbook | Text dates that do not relate to the calendar table |
| X-08 | Rounding applied at each step versus once at the end | Workbook | Small gap from a different rounding step: accepted difference once explained |
| X-09 | Volatile or context-dependent cells (`TODAY`, `NOW`, `RAND`, `OFFSET`, `INDIRECT`, `CELL`, `INFO`) | Workbook with the as-of date frozen or overridden | Result changes with the refresh date |
| X-10 | Manual inputs (targets, mappings): present in the model, owned, same content | Workbook input range | Input left in the workbook, or copied without an owner |
| X-11 | Access controlled only by who holds the file, or by hidden sheets | Source rule description | Security that never existed as a rule; apply the RLS protocol of `powerbi-testing` |
| X-12 | Pivot tables and slicers synced inside the workbook | Workbook with the same slicer states | Interaction differs in Power BI: test the selections users actually make |
| X-13 | Circular references, iterative calculation, Data Tables (what-if) | Workbook | Logic with no direct counterpart: rebuild from the intent |

## 3. Procedure

1. Pick the sheet blocks under test with the owner; one block = one test per grain.
2. Run the check query on the model at the same grain and filters, and compare to the frozen expected value.
3. Classify each gap and record it as `parity-and-cutover.md` describes. A defect found in the workbook is raised immediately (rule 2).
4. The workbook stays frozen and read-only from the first day of the parallel run.
