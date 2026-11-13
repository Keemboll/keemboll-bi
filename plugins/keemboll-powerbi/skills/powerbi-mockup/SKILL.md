---
name: powerbi-mockup
description: "HTML mockup of a Power BI report page built from the real semantic model, before anything is built in Power BI: inventory of tables, measures and columns, a self-contained HTML page at canvas size, every element labelled with the exact field it will use, list of missing measures, fast iterations, then hand-over to the PBIP. Use to plan or prototype a page, compare layout variants or prepare a report build. Triggers: mockup, mock-up, prototype, wireframe, HTML, plan a page, report sketch, layout, before building."
---

# HTML mockup from the model

Changing a layout in Power BI takes time; in an HTML mockup, one sentence is enough. Iterate here until approved, **then** build. Apply `powerbi-report-design` (four questions, design tokens) and `powerbi-conventions` (metadata confidentiality).

## Process

1. **Read the model** (`*.SemanticModel/definition/` or the published model through MCP) and produce the **inventory**: tables, measures (with display folder and format), key dimension columns, date table. Show it to the user once.
2. **Four questions** of the page (see `powerbi-report-design`): have them confirmed.
3. **Map** each question to elements (KPI cards, trend, variances, rankings) and to **existing fields**. If a field is missing: **do not invent it**, add it to the "Missing measures" list with a proposed DAX (`powerbi-dax-library`).
4. **Generate a single self-contained HTML file** (inline CSS and JS, no external resource) from [references/mockup-template.html](references/mockup-template.html):
   - exact canvas size and design tokens (colours, radius, margins);
   - **every element carries a label** `Table[Field]` / `[Measure]` (`data-fields` attribute + discreet visible text);
   - titles phrased as **questions**;
   - **plausible, fictitious** sample values (never real data copied from the cache);
   - simulated toggles (Plan / PY, Top / Bottom, Monthly / Cumulative) and filter pane if planned;
   - a closing box "Missing measures" and "Assumptions".
5. **Save** next to the project: `mockups/<page>-v1.html`; the user opens it in the browser.
6. **Iterate**: one request = one new version (`-v2`, `-v3`); keep the field labels. Typical changes: order and size, chart type (donut → sorted bars), question titles, colours (one accent, green / red for good / bad), toggles.
7. **Approve** with the [checklist](references/mockup-checklist.md), then move on to the build.

## Hand-over to the PBIP

Typical request to run with `powerbi-report-cli`:

> Build the mockup `mockups/<page>-vN.html` as a new page of the PBIP project [path]. Follow the layout, sizes and colours. Use the mockup's field labels to bind each visual to the model. If a field or measure does not exist, list it instead of guessing. Validate the report files, reload the report in Power BI Desktop, take a screenshot of the page and fix what is wrong: data, visuals, alignment.

Then `powerbi-report-design` step 6 (visual check) and capture of the fixes as references.

## Rules

- The mockup uses **only fields that exist**; everything else is explicitly marked missing.
- One mockup = one page. No framework, no CDN: one file that opens offline.
- Fictitious sample data: never read `.pbi/cache.abf` nor copy real values, especially for sensitive data.
- Do not change the PBIP during the mockup phase.
