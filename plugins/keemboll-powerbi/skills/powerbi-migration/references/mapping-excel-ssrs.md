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

### Excel formulas → DAX / Power Query

Each mapping is a pattern to test (parity per cell block, not per workbook). Write the **intent** first, then pick the tool.

| Excel | Power BI | Notes |
|---|---|---|
| `VLOOKUP`, `XLOOKUP`, `INDEX` / `MATCH` | Relationship (preferred), merge in Power Query, `RELATED` in a calculated column | A lookup chain usually reveals a missing dimension. `RELATED` works in row context, from the many side to the one side, and needs a relationship (otherwise `LOOKUPVALUE`). Approximate-match lookups have no direct equivalent: rebuild the intent. |
| `SUMIFS`, `COUNTIFS`, `AVERAGEIFS` | `CALCULATE` with filters on dimension columns | e.g. `CALCULATE ( [Net Sales], Dim_Product[Category] = "Bikes" )` (`Category` is illustrative). The filter overrides a slicer on the same column (`KEEPFILTERS` to keep both). `COUNTIFS`: `CALCULATE ( COUNTROWS ( Fact_Sales ), ... )`. Wildcards and OR conditions need `CONTAINSSTRING` or `IN { ... }`. |
| `SUMPRODUCT` | `SUMX` over the table | The row-level expression must name its grain, e.g. `SUMX ( Fact_Sales, Fact_Sales[Quantity] * RELATED ( Dim_Product[ListPrice] ) )` (`ListPrice` is illustrative). |
| `IFERROR`, `IF` chains | `DIVIDE` for divisions, `IFERROR`, `IF`, `SWITCH ( TRUE (), ... )` | Do not hide errors silently: ask what the error means. Excel error values (`#N/A`, `#DIV/0!`) have no DAX counterpart. |
| `TEXT`, `LEFT`, `MID`, `&` | Power Query text functions upstream (`Text.Start`, `Text.Middle`), or `FORMAT`, `LEFT`, `MID` | Prefer Power Query for row-level cleaning. Avoid `FORMAT` in measures: it returns text (no summing, no numeric sorting) and depends on the locale; use the model's format string. |
| `EOMONTH`, `EDATE`, `NETWORKDAYS` | `Dim_Date` columns, `EOMONTH`, `EDATE` | `EOMONTH` and `EDATE` are scalar functions, not time intelligence: for period logic use `Dim_Date` and `powerbi-dax-library`. `NETWORKDAYS` has no equivalent: business-day logic belongs in the calendar table. |
| Array / dynamic array formulas (`FILTER`, `UNIQUE`, `SORT`) | Power Query steps or table expressions (`VALUES`, `DISTINCT`, `TOPN`) | Not one to one: DAX `FILTER` is an iterator returning a table, and `SORT` has no direct equivalent. |
| `GETPIVOTDATA`, hard-coded cell references | Measures | The reference hides the business rule: document it. |
| Cube functions (`CUBEVALUE`, `CUBEMEMBER`) on a model | May keep working against the published semantic model | Test them before replacing a workbook. |
| Named ranges, hidden sheets, `INDIRECT` | Reference tables, or retire | List each in `MIGRATION.md`. |

### Excel inventory and parity

- **Inventory**: external links, hidden sheets and columns, macros, data connections and their refresh, manual inputs and who types them, copies of the same workbook with small differences. Usage comes from the file store or, for a published model, the tenant audit log, not from memory.
- **Parity**: the Excel test cases and procedure are in [excel-parity-tests.md](excel-parity-tests.md). Keep the manual-input values out of the repository (rule 4 of `SKILL.md`).

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

### Paginated report concepts

| SSRS / RDL | Power BI | Notes |
|---|---|---|
| Report server, folders | Workspace | Permissions become workspace roles or app audiences (`powerbi-governance`). |
| Shared data source | Embedded data source | Credentials re-created in the target. |
| Shared dataset (`.rsd`) | Embedded dataset, or a semantic model as the source | |
| Linked reports, custom fonts | Not supported | See the Microsoft paginated reports FAQ. |
| Dataset (SQL, stored procedure) | Dataset on the semantic model (DAX) or on the source | Prefer the semantic model so numbers match the interactive reports. |
| Report parameters, cascading parameters | Paginated report parameters | Available values come from a dataset. |
| Expressions (VB) | Expressions | Embedded code blocks are supported, custom assemblies are not: convert assembly logic to embedded code. |
| Subreports, drillthrough, document map | Supported, with limits | Subreports and drillthrough targets must be in the same workspace, drillthrough parameter names must match, and drillthrough links are inactive in exports. Check the current Microsoft pages. |
| Headers, footers, page breaks | Same | The reason to choose paginated: keep them. |
| Data-driven subscriptions | Dynamic per-recipient subscriptions, or Power Automate | SSRS-style data-driven subscriptions are not supported. Dynamic subscriptions need a capacity-backed workspace and a recipient list kept in a maintained semantic model with a named owner (check current limits). Record the rule, not the addresses. |
| Report Builder / SSDT authoring | Power BI Report Builder | |

**Inventory**: the report server catalog and execution logs give usage per report (the `ExecutionLog3` view in the `ReportServer` database is the usual source; check the SSRS documentation for your version). List per report: datasets, parameters, subscriptions, custom code, and rendering formats used (PDF, Excel).

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

### Looker concepts in more detail

| Looker | Power BI | Notes |
|---|---|---|
| `dimension_group` (timeframes) | Columns of `Dim_Date` | Only if the shared calendar table has the same attributes. |
| `relationship: many_to_one` in an explore join | Relationship cardinality and filter direction | Check the grain: see above. |
| Persistent derived tables (PDT) | Upstream tables, dataflows or Power Query | Heavy logic belongs upstream. |
| Parameters, templated filters (Liquid) | `Param_*` tables read with `SELECTEDVALUE` | Dynamic SQL has no equivalent: rebuild the intent. With several values selected, `SELECTEDVALUE` returns its default (or blank): decide the multi-select behaviour. |
| Table calculations | Visual calculations or measures | `powerbi-dax-library`; check the current Microsoft documentation for the status of visual calculations. |
| `access_filter` with user attributes | RLS roles (`RLS_<scope>`) | Test "sees exactly" and "sees nothing" (`powerbi-testing`). |
| `sql_always_where` (fixed for everyone), `always_filter` (visible, changeable) | A filter in the source query or view; a default slicer or filter | Not RLS. |
| Schedules, alerts | Subscriptions, data alerts | |

- Looker Studio is a different product: confirm which one the source is.
- **Inventory**: Looker's System Activity Explores (History, Content Usage; retention is limited) can give content usage; check the Looker documentation for the current model names. List per Look or dashboard: explores, filters, schedules, and access rules (as rules, not user lists).

## SSAS / AAS tabular

- Same engine family: the model (tables, relationships, measures, roles) moves with little translation. Power BI project definitions cannot be deployed to SSAS / AAS, and AAS / SSAS projects are not PBIP projects: bring the model into a Power BI semantic model, then save as PBIP.
- Microsoft provides an **AAS to Power BI migration feature** and guidance, including permission mapping (database roles in Power BI only enforce RLS / OLS; read and admin permissions become semantic model permissions) and data source providers that are not supported in Power BI. Read [Migrate from Azure Analysis Services to Power BI](https://learn.microsoft.com/power-bi/guidance/migrate-azure-analysis-services-to-power-bi) before planning.
- Dynamic RLS: check that the identity in the security table matches what Power BI returns for `USERPRINCIPALNAME()`; Microsoft notes AAS and Power BI do not use the same identity claim.
- Multidimensional SSAS (cubes, MDX): no direct conversion to a tabular model; treat as a rebuild (map dimensions, measures, calculated members to measures).

### SSAS / AAS: MDX and operations

| SSAS / AAS | Power BI | Notes |
|---|---|---|
| MDX queries, calculated members (tabular) | DAX measures | Translate intent, then test. |
| KPIs | Measures with status logic, or KPI visuals | |
| Perspectives, translations | Kept in the model metadata | Not authored in Power BI Desktop: use an external tool or the XMLA endpoint (read / write enabled). Test client behaviour (for example Excel) before promising it. |
| Partitions, processing schedules | Refresh policy, incremental refresh | `powerbi-power-query`. |
| Client connections (Excel, third-party tools) | Connect to the published semantic model | List the clients: the connection string changes. |
| Roles and members | RLS / OLS and workspace permissions | See the permission mapping above. |

- **Inventory**: which clients query the model and how often (server traces or Azure metrics, check the current documentation), which roles exist, and which refreshes run.
- **Parity**: run the same DAX or MDX queries on both models and compare results at the finest useful grain (`powerbi-testing`).
