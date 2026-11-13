# Storage mode decision guide

Capabilities are stated **at the time of writing — check the current documentation**: [comparison of storage modes](https://learn.microsoft.com/fabric/fundamentals/direct-lake-overview#comparison-of-storage-modes) and [choose the right Direct Lake type](https://learn.microsoft.com/fabric/fundamentals/direct-lake-develop#choose-the-right-storage-mode).

## Decision table

| Criterion | Import | Direct Lake on OneLake | Direct Lake on SQL endpoint | DirectQuery | Composite (Direct Lake on OneLake + Import) |
|---|---|---|---|---|---|
| Where the data lives | Any connector | Delta tables in one or more Fabric items (natively or via shortcuts) | Delta tables or SQL views of **one** Fabric item with a SQL analytics endpoint | Any source with DirectQuery support | Large facts in OneLake, small tables anywhere |
| Licence | Any | Fabric capacity only | Fabric capacity only | Any | Fabric capacity only |
| Volume | Fits the model memory and the refresh window | Beyond what is practical to copy; bounded by the SKU guardrails per table | Same; above guardrails it falls back | Very large or not copyable | Facts large, dimensions small |
| Freshness | As of the last refresh (copy of the data) | As of the last framing (seconds, no copy); automatic updates possible | Same, or live data when falling back | Live | Mix of both |
| Power Query transformations | Yes, in the model | No: transform upstream | No: transform upstream (SQL views fall back) | Limited (folding) | Only on the Import tables |
| Calculated columns / tables | Yes | Preview, with limits | No (except calculation groups, what-if and field parameters) | Columns yes; calculated tables become Import | Yes on Import tables |
| Security location | Model roles | Model roles and/or OneLake security | Model roles and/or SQL endpoint (fallback) | Model roles and/or source | Model roles; OneLake security on the Direct Lake tables |
| Capacity | Memory for the whole model plus refresh | Guardrails per SKU; memory for paged columns | Same | Source load | Both |
| Mixed with other modes in one model | Yes | Yes (Import; DirectQuery through XMLA tools) | No in the same model | Yes | — |

## Reasoning

1. **Start from Import.** It works with any licence and source, keeps Power Query and calculated columns, and the team already knows it. Large facts are handled with incremental refresh (`powerbi-power-query`).
2. **Move to Direct Lake on OneLake** when all of these hold: the data is already curated Delta in OneLake (gold layer, star schema); the team owns those tables or has an agreement with their owner; the largest table fits the guardrails of the SKU with a margin; no logic needs Power Query or calculated columns. The gain is no data copy, short framing instead of long refreshes, and one copy of the data shared with other Fabric engines.
3. **Direct Lake on SQL endpoint** only if the model must reuse security defined on the SQL analytics endpoint or SQL views that cannot be materialized, and you accept DirectQuery performance on those queries. Microsoft recommends Direct Lake on OneLake for new models.
4. **DirectQuery** only for strict real time or a source that cannot land in OneLake. Real-time analysis in Fabric is often better served by Real-Time Intelligence (Eventhouse); see the Microsoft documentation.
5. **Composite Direct Lake on OneLake + Import** when the facts are in OneLake but some small tables come from elsewhere or need Power Query (a budget file, a mapping table maintained by the business). Relationships between Direct Lake and Import tables are regular relationships at the time of writing.

Also consider [OneLake integration for Import models](https://learn.microsoft.com/power-bi/enterprise/onelake-integration-overview): it writes Import tables to Delta in OneLake, a way to share data with Fabric without redesigning the model.

Validate any choice other than Import with a proof of concept on real volumes: cold and warm query times, framing time, guardrail counts.

## Worked scenarios

| Scenario | Choice | Why |
|---|---|---|
| Sales data from an ERP, 30 million rows in `Fact_Sales`, refreshed nightly, no Fabric capacity | Import | No Fabric licence; volume comfortable for Import |
| Gold lakehouse built by the data engineering team, `Fact_Sales` 2 billion rows, star schema in Delta, F-SKU capacity | Direct Lake on OneLake | Data already curated; copying it is impractical; check rows per table against the SKU guardrail |
| Same lakehouse, plus `Fact_Budget` maintained in an Excel file by finance | Composite: Direct Lake on OneLake + `Fact_Budget` in Import | The budget needs Power Query; facts stay in Direct Lake |
| Warehouse where the DBA defined RLS in T-SQL, and the same rules must apply in reports and in SQL queries | Direct Lake on SQL endpoint, or OneLake security + Direct Lake on OneLake | SQL endpoint RLS forces fallback; moving rules to OneLake security keeps Direct Lake speed. Decide with `powerbi-governance` |
| Model built on SQL views that join several lakehouse tables | Materialize the views as Delta tables, then Direct Lake on OneLake; or keep Import | Non-materialized views are not supported by Direct Lake on OneLake and fall back on the SQL flavour |
| Self-service analyst without write access to the lakehouse who needs extra columns | Import (or Import tables added to the composite model) | Direct Lake cannot transform; the analyst cannot change the source |
| Telemetry that must show events within seconds | DirectQuery or Real-Time Intelligence | Freshness beyond what framing provides |
