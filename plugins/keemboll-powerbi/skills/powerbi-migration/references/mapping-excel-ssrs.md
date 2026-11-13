# Excel / Power Pivot, SSRS / paginated, Looker, SSAS / AAS → Power BI

## Excel and Power Pivot

| Excel | Power BI | Notes |
|---|---|---|
| Power Pivot data model | Semantic model — imports almost as is (same tabular engine) | Power BI Desktop: **File → Import → Power Query, Power Pivot, Power View**. Microsoft documents objects that are skipped or changed (for example hierarchies, binary columns, some data categories); read the summary page shown after import and the [import documentation](https://learn.microsoft.com/power-bi/connect-data/desktop-import-excel-workbooks). |
| Power Query queries | Power Query queries | Imported with the workbook. |
| Worksheet formulas, `VLOOKUP` / `XLOOKUP` chains | Power Query (merge, relationships) + measures | Formulas spread across cells hide business rules: write each rule's intent in `MIGRATION.md` before rebuilding. |
| Manual inputs (targets, mappings, adjustments typed into cells) | A **maintained reference table** with a named owner (function), refreshed like any source | An input with no owner is a risk to raise, not to migrate silently. Targets → `Fact_Budget`. |
| Pivot tables, pivot charts | Matrix and chart visuals | Rebuild for interaction (`powerbi-report-design`). |
| Slicers, timelines | Slicers | |
| Macros (VBA), Office scripts | **Out of scope** | List them in `MIGRATION.md` with what they do; the owner decides (upstream automation, Power Automate, or drop). |
| Linked tables, `Excel.CurrentWorkbook()` | Import as a snapshot or keep a connection to the workbook | Microsoft documents both options; a snapshot is no longer refreshed. |

Users who need Excel afterwards can analyse the published semantic model from Excel instead of keeping a private copy of the data.

## SSRS / paginated reports

Decision rule:

| Report is mainly... | Target |
|---|---|
| Pixel-perfect, print- or PDF-oriented, long tables over many pages, exported or e-mailed on a schedule | **Power BI paginated report** (`.rdl`), not interactive pages |
| Exploration, few numbers, cross-filtering, drill | Power BI report (interactive) |
| Both | One semantic model, an interactive report **and** a paginated report on it |

- Microsoft documents migration paths for `.rdl` reports (built-in publishing from recent Reporting Services / Power BI Report Server versions, and the RDL Migration Tool for older ones), and lists **unsupported item types and report features** (for example custom code assemblies, shared data sources converted to embedded ones). Check the current list in [Plan to migrate .rdl reports to Power BI](https://learn.microsoft.com/power-bi/guidance/migrate-ssrs-reports-to-power-bi) before promising a straight migration.
- Before migrating, find unused reports (Microsoft provides guidance for SSRS) and retire them (step 2 of the skill).
- Re-create data source credentials in the target; never copy them from the report server.
- Parity for paginated reports: same rows, same totals, same page breaks where the layout is contractual, and a check of the PDF output (fonts).

## Looker

No Microsoft migration tool. Map by concept and test:

| Looker | Power BI |
|---|---|
| LookML views, explores | Tables and relationships of a semantic model |
| Dimensions | Columns (Power Query or calculated) |
| Measures | Measures |
| Derived tables | Power Query, upstream views or tables |
| Access filters, user attributes | RLS |
| Looks, dashboards | Report pages |

LookML joins define the grain per explore; in Power BI the grain is fixed by the model: decide it explicitly (`powerbi-data-modeling`).

## SSAS / AAS tabular

- Same engine family: the model (tables, relationships, measures, roles) moves with little translation. Power BI project definitions cannot be deployed to SSAS / AAS, and AAS / SSAS projects are not PBIP projects: bring the model into a Power BI semantic model, then save as PBIP.
- Microsoft provides an **AAS to Power BI migration feature** and guidance, including permission mapping (database roles in Power BI only enforce RLS / OLS; read and admin permissions become semantic model permissions) and data source providers that are not supported in Power BI. Read [Migrate from Azure Analysis Services to Power BI](https://learn.microsoft.com/power-bi/guidance/migrate-azure-analysis-services-to-power-bi) before planning.
- Dynamic RLS: check that the identity in the security table matches what Power BI returns for `USERPRINCIPALNAME()`; Microsoft notes AAS and Power BI do not use the same identity claim.
- Multidimensional SSAS (cubes, MDX): no direct conversion to a tabular model; treat as a rebuild (map dimensions, measures, calculated members to measures).
