# REPORT.md template

Report sheet, at the project root. It describes **who the report is for and which question each page answers**; the fields used per visual are found with `lean.py usage` and are not copied here.

```markdown
# Report sheet — <report name>

- **Semantic model**: <name> (see `DATA_DICTIONARY.md`)
- **Audience**: <roles or teams, no person names>
- **Decisions supported**: <what the reader does after reading the report>
- **Reading frequency**: <daily / weekly / monthly>
- **Data refresh**: <frequency and time>
- **Business owner**: <job title> · **Technical lead**: <job title>
- **Security**: see `SECURITY_MODEL.md`

## Pages

| # | Page | Question it answers | Main KPIs | Filters and slicers |
|---|---|---|---|---|
| 1 | Overview | Where do we stand against the target? | `Net Sales`, `Gross Margin %` | Year, Region |
| 2 | Customer detail | Which customers explain the gap? | `Customer Count`, `Net Sales` | Year, Segment |

## Navigation and interactions

- Drill-through: <source page → target page, field>
- Report tooltips: <tooltip page → visuals concerned>
- Bookmarks and toggles: <e.g. Target / Previous year>

## Known limits

- <excluded scope, date from which data is available, refresh lag>
- <KPI not comparable before a given date>
- Open debt: see `DEBT.md`
```

## Rules

- A page without a clear question is a finding to raise, not a row to fill in by default (see the four questions of `powerbi-report-design`).
- KPI names are those of the model, in backticks.
- Known limits are written for a business reader: what they must **not** conclude from the report.
- No real value and no screenshot with real data.
