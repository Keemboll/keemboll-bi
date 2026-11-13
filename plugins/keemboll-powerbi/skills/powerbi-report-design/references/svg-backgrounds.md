# SVG page backgrounds

A good background carries the **cards, borders and side rail**: the visuals placed on top stay simple (transparent background and border). The background is an SVG image at the exact canvas size.

## Process

1. Start from the **approved HTML mockup** (`powerbi-mockup`) or a screenshot of a reference report.
2. Read the positions and sizes of the page's visuals (`*.Report/definition/pages/<page>/visuals/*/visual.json` → `position`).
3. Generate an SVG at the canvas size, with one card per area, following the **design tokens** (radius, border, margins, colours).
4. Save the file in the project (e.g. `*.Report/StaticResources/RegisteredResources/background-<page>.svg` through `powerbi-report-cli`) and set it as the **page background**, image fit *Fit*, transparency 0 %.
5. Make the visuals transparent (background off, no border) and check alignment with a screenshot.

## Template (1280 × 720, 60 px side rail, 4 KPIs + 2 + 2)

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">
  <rect width="1280" height="720" fill="#F5F6F8"/>
  <rect width="60" height="720" fill="#1F4E79"/>
  <!-- KPI row: y=80, h=130; usable width 1280-60-2*20 = 1180; 4 cards, 3 gaps of 16 -->
  <g fill="#FFFFFF" stroke="#E5E7EB" stroke-width="1">
    <rect x="80"  y="80" width="283" height="130" rx="12"/>
    <rect x="379" y="80" width="283" height="130" rx="12"/>
    <rect x="678" y="80" width="283" height="130" rx="12"/>
    <rect x="977" y="80" width="283" height="130" rx="12"/>
    <rect x="80"  y="226" width="582" height="220" rx="12"/>
    <rect x="678" y="226" width="582" height="220" rx="12"/>
    <rect x="80"  y="462" width="582" height="238" rx="12"/>
    <rect x="678" y="462" width="582" height="238" rx="12"/>
  </g>
</svg>
```

Calculation rules: card width = (usable width − (n − 1) × gap) / n; keep the same coordinates as the visuals (the visual fills the card with 8 to 12 px of inner padding).

## Watch points

- Positions in the SVG and in the `visual.json` files must be **identical**: any layout change means regenerating the background.
- No text in the background (not accessible, not translatable): titles stay in visuals or text boxes.
- Keep the SVG simple (a few kilobytes).
- Graphic alternative: design the background in Figma (some agents have a Figma connector) and export it as SVG.
