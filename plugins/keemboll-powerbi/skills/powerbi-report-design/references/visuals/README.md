# Visual references

The reference loop is what makes reports "ours": the agent knows the basics, not our patterns. Each reference = **one precise pattern** (a KPI card, a variance chart, a ranking), **its exact settings** and **an image** of the result.

## Adding a reference

1. Find a visual you like (internal report, community challenge, video, Dribbble / Figma). Note the **source** and check that you may draw on it.
2. If the file is available: save it as **PBIP** in a `references/` folder outside the project, then ask the agent:
   > Open the PBIP project in [folder]. Find the visual on page "[page]" that shows [description]. Explain how it is built: type, fields and measures, formatting (colours, fonts, borders, padding), tricks (conditional formatting, hidden elements, layering). Say which files and which JSON properties control each part.
3. Create `visuals/<pattern-name>.md` from [_template.md](_template.md): when to use it, the useful `visual.json` settings, measures as generic patterns, any pitfall.
4. Add **the image** in `visuals/images/<pattern-name>.png` and link it right under the title. Without images, references become vague.
5. Add a row to the catalogue below, bump the plugin version, commit.

A short, exact reference beats a long one: keep only what reproduces the pattern.

## Catalogue

| Pattern | When to use it | File |
|---|---|---|
| KPI card with comparison | Headline number + variance to target and to PY | [kpi-comparison-card.md](kpi-comparison-card.md) |
