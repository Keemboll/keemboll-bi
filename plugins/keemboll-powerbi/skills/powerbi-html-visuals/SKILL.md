---
name: powerbi-html-visuals
description: "Building HTML and SVG visuals in Power BI reports from DAX measures: sparklines, progress bars, KPI indicators, badges, bullet charts in tables and matrices (Image URL data category), and HTML cards through the HTML Content custom visual. Use when a native visual is not enough and SVG or HTML must be generated in DAX, or to fix an SVG/HTML visual that does not render. Triggers: HTML, SVG, sparkline, image URL, data URI, progress bar, KPI card, badge, HTML Content, custom visual, infographic, bullet chart."
---

# HTML / SVG visuals in DAX

Apply `powerbi-report-design` (theme colours, accessibility) and `powerbi-conventions` (naming: `SVG ` or `HTML ` prefix for these measures, display folder `80 Visuals`). Watch the cost with `powerbi-performance`.

## Two techniques

| Technique | Renders in | Prerequisite | Use |
|---|---|---|---|
| **SVG as data URI** | Table, matrix, other visuals that accept a dynamic image URL | Measure with the **Image URL** data category | Sparklines, bars, dots, arrows in table rows |
| **HTML** | *HTML Content* custom visual (AppSource) | Custom visuals allowed by the tenant administrator (check the tenant setting) | Rich KPI cards, formatted text blocks, lists |

Prefer **native visuals** first (conditional formatting, icons, data bars, native table/matrix sparklines). Only move to SVG/HTML when the native option cannot produce the intended render.

## SVG rules

1. The measure returns: `"data:image/svg+xml;utf8," & <svg …>`.
2. Set the **data category = Image URL** (Measure tools → Data category; in TMDL: `dataCategory: ImageUrl`).
3. Use **single quotes** for SVG attributes (`width='120'`): double quotes must be doubled in DAX.
4. Encode `#` as **`%23`** in colours (`fill='%231F4E79'`) — otherwise the image is truncated. Other special characters (`%`, `<` in text) must also be encoded or avoided.
5. Always `xmlns='http://www.w3.org/2000/svg'` and a `viewBox`.
6. Numbers formatted with a **decimal point**: `FORMAT ( x, "0.0", "en-US" )` (a model with a comma-decimal locale would produce `12,5` → invalid SVG).
7. Image size in the table: Format → *Image size* (height/width) consistent with the `viewBox`.
8. Colours from [theme-keemboll.json](../powerbi-report-design/references/theme-keemboll.json); never colour alone to carry meaning.
9. Keep the SVG short (a few hundred characters): it is recomputed for every cell.

Ready-to-adapt templates: [references/svg-templates.md](references/svg-templates.md).

## HTML rules (HTML Content visual)

- The visual renders HTML + inline CSS; **no JavaScript**.
- Build the HTML in a measure (or a column) and put it in the *Values* field.
- **Escape** text coming from the data (`&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`) with `SUBSTITUTE` before inserting it.
- Inline styles, theme font and colours; width in `%` to fit the visual.
- Provide **alt text** on the visual, since screen readers do not read the HTML content reliably.

Templates: [references/html-templates.md](references/html-templates.md).

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| The URL shows as text | Data category ≠ Image URL |
| Empty or broken image | `#` not encoded, quotes badly doubled, decimal comma, missing `xmlns` |
| Tiny / clipped image | Table image size ≠ `viewBox` |
| Slow page | Long SVG × many rows; limit rows or simplify |
| Raw HTML displayed | Native visual used instead of HTML Content |
