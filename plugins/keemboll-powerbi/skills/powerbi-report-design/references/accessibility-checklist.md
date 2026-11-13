# Quality and accessibility checklist

## Accessibility

- [ ] Text / background contrast ≥ 4.5:1 (≥ 3:1 for large text and graphical elements).
- [ ] No information carried **only** by colour (add an icon, sign or label).
- [ ] **Alt text** filled in on every visual that carries information (can be a dynamic DAX measure).
- [ ] **Tab order** defined (View → Selection pane → Tab order); decorative elements hidden from tab order.
- [ ] Explicit visual titles; no text inside images.
- [ ] Font size ≥ 10 pt for labels, ≥ 12 pt for titles.
- [ ] Report tested with a Windows high-contrast theme.

## Quality

- [ ] Theme `theme-keemboll.json` applied, no hard-coded colours outside the theme.
- [ ] Alignment on the 8 px grid, consistent margins.
- [ ] Unit and period visible for every number.
- [ ] Active filters visible.
- [ ] Interactions between visuals checked (Edit interactions).
- [ ] Hidden pages: tooltips and drillthrough only.
- [ ] Performance analyzer: no visual > 2 s (see `powerbi-performance`).
- [ ] Mobile layout created for pages viewed on a phone.
- [ ] Short, explicit page names; a home or contents page if > 5 pages.
