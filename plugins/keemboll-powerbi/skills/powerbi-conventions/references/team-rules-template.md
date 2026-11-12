# Team rules — template for `TEAM_RULES.md`

Put a `TEAM_RULES.md` at the root of the BI project to replace the defaults marked **ADAPT** in the skills. The agent reads it **before** applying any skill; where it is silent, the skill's default applies. Keep only the lines you actually decide on, delete the rest.

Do not put secrets, tenant or workspace identifiers, or personal data in this file.

```markdown
# Team rules — <team or project name>

Version: <yyyy-mm-dd> · Owner: <role>

## Language and locale
- Language of visible labels (columns, measures, pages): <English | French | ...>
- Currency and amount format: <$#,##0 | #,##0 € | ...>
- Percentage format: <0.0% | ...>
- Date format: <yyyy-MM-dd | dd/MM/yyyy>

## Naming
- Fact tables: <Fact_ + plural process>
- Dimensions: <Dim_ + singular entity>
- Measures table: <_Measures | measures live in their fact table>
- Display folders: <01 Sales, 02 Margin, ... | other scheme>
- Other: <exceptions, legacy prefixes kept on existing models>

## Environments and release
- Environments: <dev -> test -> prod>
- Deployment path: <deployment pipelines | Git integration>
- Required approvals before production: <role(s)>

## Security and sensitivity
- Sensitivity labels in use: <list>
- Rule for publishing without a label: <forbidden | allowed for ...>
- Who approves a new RLS role: <role>

## Report design
- Theme file: <path or name>
- Visuals per page: <limit>
- Page size and grid: <values>

## Tooling
- Authorized AI tools for real projects: <list>
- DAX engine / test tool available: <Tabular Editor CLI | DAX Studio | MCP modeling server | none>

## Other decisions
- <date> — <decision> — <who decided>
```

## How skills use it

- `powerbi-conventions` reads it first and applies it over its own defaults.
- Every other skill defers to `powerbi-conventions` for style, so a rule written here reaches the whole plugin.
- A rule that contradicts a **safety** rule of the skills (read-only by default, approval before deleting, no secrets in files) is ignored and reported to the user.
