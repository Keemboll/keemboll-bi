# KPI card with comparison

> Image to add: `images/kpi-comparison-card.png` (screenshot of the first approved render).

- **When to use it**: questions 1 and 2 of a page — "how much?" and "is that good?".
- **Triggers**: KPI, card, key figure, vs target, vs PY.
- **Source**: internal, inspired by "value + attainment + variances" cards.

## Construction

- One card per KPI, on a card of the SVG background (transparent visual).
- Content, top to bottom: muted label (10 pt, grey), **value** (28 pt), then two lines "vs target" and "vs PY" with the variance in value and in %, coloured good / bad **with a sign** (▲ / ▼).
- Option: attainment % donut on the right, 12-month sparkline at the bottom.
- Implementation:
  - **native**: *Card (new)* visual with reference labels;
  - **rich**: one HTML measure per card in the *HTML Content* visual (see `powerbi-html-visuals`, "KPI card" template), sparkline and donut in SVG.
- Measures: `[Net Sales]`, `[Sales Target]`, `[Net Sales PY]`, variances and `%` (see `powerbi-dax-library`), possibly `[Net Sales Comparison]` if a Plan / PY toggle exists.

## Key settings

- Visual background: off; border: none (the SVG background carries the card).
- Inner padding: 12 px.
- Alt text: a measure that summarises "Net Sales €436M, 101 % of target, −24 % vs PY".

## Pitfall

Value and comparisons must respond to the same filters: do not mix an `ALL` measure into the card without saying so in the label.
