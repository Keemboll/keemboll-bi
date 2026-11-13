# Team rules — template for `TEAM_RULES.md`

Put a `TEAM_RULES.md` at the root of the BI project to replace the defaults of the skills. The agent reads it **before** applying any skill; where it is silent, the skill's default applies. Keep only the lines you actually decide on and delete the rest: an empty line is not a rule.

Each section names the skill that states the default being replaced; read that skill to see the current default value. Do not put secrets, tenant or workspace identifiers, e-mail addresses or personal data in this file.

```markdown
# Team rules — <team or project name>

Version: <yyyy-mm-dd> · Owner: <role>

## Language and locale (default in powerbi-conventions)
- Language of visible labels (columns, measures, pages): <English | French | ...>
- Currency and amount format: <$#,##0 | #,##0 € | ...>
- Percentage / integer format: <0.0% | ...> / <#,##0 | ...>
- Date format: <yyyy-MM-dd | dd/MM/yyyy | ...>
- Locale used by date labels (month and day names): <en-US | fr-FR | ...>

## Naming (powerbi-conventions)
- Fact tables: <Fact_ + plural process | other scheme>
- Dimensions: <Dim_ + singular entity | other scheme>
- Parameter and calculation group tables: <Param_ / CG_ | other scheme>
- Technical columns, intermediate measures, DAX variables: <scheme>
- RLS roles: <RLS_<scope> | other scheme>
- Exceptions: <legacy prefixes kept on existing models>

## Measures (powerbi-conventions)
- Location: <_Measures table | measures live in their fact table>
- Display folders: <01 Sales, 02 Margin, ... | other scheme>
- Comment header: <WHAT / HOW / NOTE on non-trivial measures | on every measure>

## Date table and history (powerbi-data-modeling)
- Fiscal year start: <month>
- History kept in the model: <from year ... to ...>

## Repository, branches and releases (powerbi-alm)
- Repository layout: <one repository per BI product | one repository for several projects>
- Branches: <main + feature/<topic> + fix/<topic> | other scheme>
- Commit message format: <conventional commits | other>
- Review before merging: <who reviews, how many approvals>
- Version tags and what counts as major / minor / patch: <vX.Y.Z rules>
- CI: what fails the build: <which findings block, which are only displayed>
- Data extracts in the repository (`*.csv`, `*.xlsx`, `*.parquet`): <ignored | listed exceptions>

## Environments (powerbi-alm)
- Environments: <dev -> test -> prod | other>
- Promotion path: <deployment pipelines | Git integration | both>
- Required approvals before production: <role(s)>
- Data in dev: <sample | anonymized | ...>

## Refresh and operations (powerbi-power-query, powerbi-operations)
- Incremental refresh policy: <history kept, window refreshed>
- Refresh failure: who is told, within which delay: <rule>
- Usage and capacity review: <frequency, owner>

## Security, sensitivity and endorsement (powerbi-governance, powerbi-conventions)
- Sensitivity labels in use: <list>
- Publishing without a label: <forbidden | allowed for ...>
- Publishing without a named owner: <forbidden | ...>
- Workspace roles and distribution: <who is Admin / Member; apps or direct sharing>
- Build permission: <who may get it>
- Endorsement: <who may promote, who may certify, conditions>
- Export of underlying data: <allowed | disabled for ...>
- Static or dynamic RLS: <above how many scopes a dynamic role is required>
- Small counts: <minimum group size displayed for personal data>
- Who approves a new RLS / OLS role: <role>

## Report design (powerbi-report-design, powerbi-mockup)
- Theme file: <path or name>
- Canvas size, margins and grid: <values>
- Design tokens: <accent color, good / bad colors, text colors, page and card backgrounds>
- Fonts and sizes: <titles, body, KPI>
- Visuals per page: <limit>
- Mobile layout: <required for which pages>

## Custom visuals (powerbi-html-visuals)
- Custom visuals policy: <none | certified only | organization-approved list: ...>
- HTML / SVG measures: <allowed | restricted to ...>

## Testing and acceptance (powerbi-testing)
- Rounding tolerance for reconciliation: <value per control line>
- Page load-time threshold: <seconds>
- Test levels that block acceptance when not executed: <list>
- Test file naming and numbering: <scheme>

## Documentation (powerbi-documentation)
- Location of the project documents: <project root | docs/>
- Refresh schedule shown on the report sheet: <frequency and time>

## AI and Copilot exposure (powerbi-ai-readiness, powerbi-conventions)
- AI tools authorized to read real project metadata: <list | none>
- Models that may be exposed to Copilot or data agents: <none | list | all endorsed models>
- Who approves the AI instructions and verified answers: <role>

## Tooling
- DAX engine / test tool available: <Tabular Editor CLI | DAX Studio | MCP modeling server | none>

## Other decisions
- <yyyy-mm-dd> — <decision> — <who decided, by role>
```

## How skills use it

- `powerbi-conventions` owns the mechanism: the agent reads `TEAM_RULES.md` first and applies it over the defaults of every skill of the plugin.
- The other skills only state their defaults; they do not describe the override again.
- A line that contradicts a **safety** rule of the skills (read-only first, approval before deleting or renaming, no secrets in files, no change directly in production) is ignored and reported to the user.
- A team rule that the agent cannot apply (tool missing, feature unavailable in the tenant) is reported, not silently replaced by the default.
