---
name: powerbi-report-design
description: "Style guide and design rules for Power BI reports: JSON theme (colours, fonts), the four questions of a page, design tokens (grid, cards, colours), page structure, SVG backgrounds, reusable visual references, choosing the right visual, titles and labels, slicers, tooltips, navigation and accessibility (contrast, alt text, tab order). Use to plan, build, review or harmonise a Power BI report or page, alongside powerbi-report-cli (PBIR mechanics). Triggers: report, page, dashboard, style guide, theme, colours, colors, layout, visual, chart, accessibility, design, mockup, page background, background, reference, page review."
---

# Report design

> Default style guide: a project replaces the colours and fonts with its brand. PBIR file mechanics, preview and publishing are handled by `powerbi-report-cli` (Microsoft). HTML/SVG visuals belong to `powerbi-html-visuals`.

## Process

1. **Four questions**: before any layout, write down what the page answers. A visual that serves no question goes to a detail page or disappears.
   1. **How did we perform?** The headline number, top left.
   2. **Is that good?** Compared with the target and the prior year — a number without a comparison says nothing.
   3. **Why?** Who or what explains it: which month, which category, which customer / store.
   4. **What should we do?** The largest gap, where to act first (Bottom / Top ranking).
2. **Page plan**: one page = one subject. List the pages and their four answers; wait for approval.
3. **HTML mockup** of each page with the model's real fields → skill `powerbi-mockup`. Iterate on the mockup (one sentence per change) until approved, **before** touching the PBIP.
4. **References**: look in [references/visuals/](references/visuals/README.md) for an approved pattern for each visual (KPI cards, variances, rankings...) and reuse it.
5. **Build** in the PBIP with `powerbi-report-cli`, theme [references/theme-keemboll.json](references/theme-keemboll.json), tokens below, SVG background if needed ([references/svg-backgrounds.md](references/svg-backgrounds.md)).
6. **Check visually**: reload in Desktop ("Apply external changes", preview, or Desktop Bridge; two separate mechanisms, see `powerbi-tmdl`), take a screenshot, fix alignment, data and labels; repeat until compliant.
7. **Check** with [references/accessibility-checklist.md](references/accessibility-checklist.md), then **human review**: numbers against the source. File validation is not enough.
8. **Capture**: every notable fix becomes a new reference in `references/visuals/`.

To review an existing page without changing it: list the **5 biggest problems** (alignment, colour, visual hierarchy, clutter, labels), ranked by impact, with a proposed fix for each.

## Default design tokens

| Decision | Value |
|---|---|
| Canvas | 1280 × 720 (standard) or 1300 × 900 (dense dashboard) |
| Side rail (navigation, filters) | 60 px, optional |
| Outer margin / gap between cards | 20 px / 16 px |
| Cards | white background, 12 px radius, 1 px border `#E5E7EB` |
| Page background | `#F5F6F8` |
| Accent colour | **a single one** (`#1F4E79`); everything else in grey |
| Good / bad | `#2E7D32` / `#C62828`, only for a variance against a reference |
| Text titles / body / muted | `#1F2933` / `#3C4650` / `#8A939B` |
| Fonts | Segoe UI Semibold (titles), Segoe UI (body) — **two sizes that matter**: 12 pt titles, 10 pt everything else; KPI 28 pt |

These values must be identical in the theme, the SVG background and the HTML mockup.

## Typical page structure (Z reading)

```
┌────┬─────────────────────────────────────────────────────────┐
│    │ Title · period                 [Plan | PY]   [filters] │
│ N  ├──────────┬──────────┬──────────┬──────────────────────┤
│ a  │ KPI 1 ★  │ KPI 2    │ KPI 3    │ KPI 4                │  Q1 + Q2
│ v  ├──────────┴──────────┴──┬───────┴──────────────────────┤
│    │ Trend vs reference      │ Which months deviate?        │  Q2 + Q3
│    ├─────────────────────────┼──────────────────────────────┤
│    │ Which X are below?      │ Which Y are below?           │  Q3 + Q4
│    │ [Bottom | Top]          │ [Bottom | Top]               │
└────┴─────────────────────────┴──────────────────────────────┘
```

- **Z** reading for dashboards; **F** for pages made mostly of tables and text.
- **Most important KPI top left.** Same size = same importance: differentiate on purpose, never by accident.
- **One page, several views**: toggles (Plan / PY, Top / Bottom, Monthly / Cumulative) rather than duplicated pages → `powerbi-dax-library` (switches).
- **6 to 8 visuals** at most (in-house heuristic, not a Microsoft rule); strict alignment on the grid.

## Choosing the visual

| Question | Visual | Avoid |
|---|---|---|
| Change over time | Line (continuous), clustered column (discrete periods) | Pie |
| Comparing categories | Sorted horizontal bars | 3D, radar |
| Part of a whole (≤ 5 parts) | 100 % bars, donut at a pinch | Pie > 5 parts |
| Variance to a target | KPI card with target, bars with a reference line | Multiple gauges |
| Correlation | Scatter chart | Unjustified dual axis |
| Exact values | Table / matrix with restrained conditional formatting | 50-column tables |
| Geography | Filled map (choropleth) if the areas are known | Overlapping bubbles |

## Formatting rules

- **Visual titles = question, with the answer** when possible ("Are we above PY? No, 78 %"), through a dynamic title measure.
- Unit and period visible (title, subtitle or label).
- Sort bars by descending value unless there is a natural order (months, bands).
- Value axis starts at 0 for bars/columns.
- Colour = information: the accent colour **highlights**, the rest is grey/neutral. Red/green reserved for variances (good/bad), always paired with a sign or an icon.
- Data labels rather than gridlines when there are few points; remove superfluous borders, shadows and backgrounds.
- Abbreviated numbers (k, M) in KPIs and axes; full precision in the tooltip.

## Interactions and navigation

- Slicers: 3 to 5 at most per page, synced only when needed; show the active filters in the subtitle (text DAX measure).
- Page navigation buttons and bookmarks for predefined views; a "Reset filters" button.
- Drillthrough to a detail page rather than giant tables.
- Report page tooltips for context (measure definition, mini trend).

## Deliverables

- Approved page plan + sketches.
- Report with the theme applied.
- Completed accessibility checklist.
