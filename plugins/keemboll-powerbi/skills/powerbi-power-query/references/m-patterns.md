# M patterns

Examples on the shared model (`Fact_Sales`, `Dim_Customer`, `Dim_Product`, `Dim_Date`). Source names (`dbo.FactSales`, `dbo.Customer`) are placeholders; server and database always come from parameters. Check folding on your own connector after copying a pattern ([query-folding.md](query-folding.md)).

## 1. Parameters

A text parameter, as written in M (in a PBIP project this expression lives in `expressions.tmdl`, see `powerbi-tmdl`). The value is a placeholder, replaced per environment at deployment (`powerbi-alm`).

```powerquery
"sql-dev.example.local" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]
```

`pDatabase` and `pFolderPath` follow the same form. Never a password, key or token in a parameter.

## 2. Parameterised SQL source, early column selection and filter

```powerquery
let
    Source = Sql.Database(pServer, pDatabase),
    SourceSales = Source{[Schema = "dbo", Item = "FactSales"]}[Data],
    // Only the columns the model uses: fewer columns = smaller model and faster transfer.
    #"Kept model columns" = Table.SelectColumns(
        SourceSales,
        {"OrderDate", "DeliveryDate", "CustomerKey", "ProductKey", "StoreKey", "Quantity", "NetAmount"}
    ),
    // History before 2021 is out of scope (SCOPE.md).
    #"Kept scope years" = Table.SelectRows(
        #"Kept model columns",
        each [OrderDate] >= #datetime(2021, 1, 1, 0, 0, 0)
    ),
    #"Set types" = Table.TransformColumnTypes(
        #"Kept scope years",
        {
            {"OrderDate", type date},
            {"DeliveryDate", type date},
            {"CustomerKey", Int64.Type},
            {"ProductKey", Int64.Type},
            {"StoreKey", Int64.Type},
            {"Quantity", Int64.Type},
            {"NetAmount", Currency.Type}
        }
    )
in
    #"Set types"
```

All three steps usually fold on SQL Server; confirm with *View Native Query* on `#"Set types"`.

## 3. Incremental-refresh fact query

`RangeStart` / `RangeEnd` are Date/Time parameters ([incremental-refresh.md](incremental-refresh.md)). The filter comes right after the navigation step so that it folds.

```powerquery
let
    Source = Sql.Database(pServer, pDatabase),
    SourceSales = Source{[Schema = "dbo", Item = "FactSales"]}[Data],
    // One inclusive bound only: a row on the boundary belongs to exactly one partition.
    #"Kept refresh window" = Table.SelectRows(
        SourceSales,
        each [OrderDate] >= RangeStart and [OrderDate] < RangeEnd
    ),
    #"Kept model columns" = Table.SelectColumns(
        #"Kept refresh window",
        {"OrderDate", "DeliveryDate", "CustomerKey", "ProductKey", "StoreKey", "Quantity", "NetAmount"}
    ),
    #"Set types" = Table.TransformColumnTypes(
        #"Kept model columns",
        {
            {"OrderDate", type date},
            {"DeliveryDate", type date},
            {"CustomerKey", Int64.Type},
            {"ProductKey", Int64.Type},
            {"StoreKey", Int64.Type},
            {"Quantity", Int64.Type},
            {"NetAmount", Currency.Type}
        }
    )
in
    #"Set types"
```

Here `OrderDate` is `datetime` at the source and becomes `date` only after the filter. If the source column is already a `date`, M cannot compare it with a `datetime` parameter: convert the **parameter**, not the column (`each [OrderDate] >= Date.From(RangeStart) and [OrderDate] < Date.From(RangeEnd)`), then check that the filter still folds.

Integer date key (`yyyymmdd`) at the source — function documented by Microsoft:

```powerquery
// Query fnDateKey
(x as datetime) as number => Date.Year(x) * 10000 + Date.Month(x) * 100 + Date.Day(x)
```

```powerquery
#"Kept refresh window" = Table.SelectRows(
    SourceSales,
    each [OrderDateKey] >= fnDateKey(RangeStart) and [OrderDateKey] < fnDateKey(RangeEnd)
)
```

## 4. Date dimension in M

The columns and requirements of `Dim_Date` are owned by `powerbi-data-modeling` ([dim-date.md](../../powerbi-data-modeling/references/dim-date.md)). What M adds: bounds from parameters (`pStartYear`, `pEndYear`, numbers) rather than `DateTime.LocalNow()`, which runs in UTC in the service and makes the table change silently.

```powerquery
let
    StartDate = #date(pStartYear, 1, 1),
    EndDate = #date(pEndYear, 12, 31),
    DateList = List.Dates(StartDate, Duration.Days(EndDate - StartDate) + 1, #duration(1, 0, 0, 0)),
    #"Converted to table" = Table.FromList(DateList, Splitter.SplitByNothing(), type table [Date = date]),
    #"Added Year" = Table.AddColumn(#"Converted to table", "Year", each Date.Year([Date]), Int64.Type),
    #"Added MonthNum" = Table.AddColumn(#"Added Year", "MonthNum", each Date.Month([Date]), Int64.Type),
    #"Added Month" = Table.AddColumn(#"Added MonthNum", "Month", each Date.MonthName([Date], "en-US"), type text)
in
    #"Added Month"
```

## 5. Staging + reference

`stg_Customer` (load disabled) reads and cleans; `Dim_Customer` references it and adds the Unknown member (key −1, rule in `powerbi-data-modeling`).

```powerquery
// Query stg_Customer — Enable load: off
let
    Source = Sql.Database(pServer, pDatabase),
    SourceCustomer = Source{[Schema = "dbo", Item = "Customer"]}[Data],
    #"Kept model columns" = Table.SelectColumns(
        SourceCustomer,
        {"CustomerKey", "CustomerCode", "CustomerName", "Region"}
    ),
    #"Set types" = Table.TransformColumnTypes(
        #"Kept model columns",
        {{"CustomerKey", Int64.Type}, {"CustomerCode", type text}, {"CustomerName", type text}, {"Region", type text}}
    )
in
    #"Set types"
```

```powerquery
// Query Dim_Customer — loaded
let
    Source = stg_Customer,
    // Trim after the source steps: Text.Trim may not fold on every connector.
    #"Cleaned business key" = Table.TransformColumns(Source, {{"CustomerCode", Text.Trim, type text}}),
    UnknownMember = #table(
        type table [CustomerKey = Int64.Type, CustomerCode = text, CustomerName = text, Region = text],
        {{-1, "UNKNOWN", "Unknown", "Unknown"}}
    ),
    #"Added unknown member" = Table.Combine({#"Cleaned business key", UnknownMember})
in
    #"Added unknown member"
```

## 6. Function with documentation metadata

```powerquery
// Query fnCleanKey
let
    CleanKey = (key as nullable text) as nullable text =>
        if key = null then null else Text.Upper(Text.Trim(Text.Clean(key))),
    CleanKeyType = type function (
        key as (type nullable text meta [
            Documentation.FieldCaption = "Business key",
            Documentation.SampleValues = {" c-0042 "}
        ])
    ) as nullable text
        meta [
            Documentation.Name = "fnCleanKey",
            Documentation.LongDescription = "Removes non-printable characters and surrounding spaces, then upper-cases a business key. Returns null for null.",
            Documentation.Examples = {
                [Description = "Clean a customer code", Code = "fnCleanKey("" c-0042 "")", Result = """C-0042"""]
            }
        ]
in
    Value.ReplaceType(CleanKey, CleanKeyType)
```

Applied to a column (`Table.TransformColumns`), a custom function is evaluated row by row in the engine: put it after the folding steps.

## 7. Safe type conversion with a culture, and rejected rows

A CSV export with French formats (`31/12/2024`, `1 234,50`). The culture makes the conversion independent of the machine or service locale.

```powerquery
// Query stg_SalesFile — Enable load: off
let
    Source = Csv.Document(
        File.Contents(pFolderPath & "sales.csv"),
        [Delimiter = ";", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    #"Promoted headers" = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    #"Set types" = Table.TransformColumnTypes(
        #"Promoted headers",
        {{"OrderDate", type date}, {"CustomerKey", Int64.Type}, {"NetAmount", Currency.Type}},
        "fr-FR"
    )
in
    #"Set types"
```

```powerquery
// Query stg_SalesFile_Rejected — Enable load: off; read by tests (powerbi-testing)
let
    Source = stg_SalesFile,
    #"Rows with errors" = Table.SelectRowsWithErrors(Source, {"OrderDate", "CustomerKey", "NetAmount"}),
    RejectedCount = Table.RowCount(#"Rows with errors")
in
    RejectedCount
```

The loaded query decides what to do with those rows (`Table.RemoveRowsWithErrors` only if dropping them is the agreed rule, and the count is reported).

## 8. Folder of CSV files with an explicit schema

The column list in the expand step is the schema: a new column in a file is ignored, a missing one comes back as null instead of breaking the refresh.

```powerquery
let
    Source = Folder.Files(pFolderPath),
    #"Kept CSV files" = Table.SelectRows(Source, each Text.Lower([Extension]) = ".csv"),
    #"Parsed files" = Table.AddColumn(
        #"Kept CSV files",
        "Data",
        each Table.PromoteHeaders(
            Csv.Document([Content], [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
            [PromoteAllScalars = true]
        )
    ),
    #"Kept file data" = Table.SelectColumns(#"Parsed files", {"Name", "Data"}),
    #"Expanded rows" = Table.ExpandTableColumn(
        #"Kept file data",
        "Data",
        {"OrderDate", "CustomerKey", "ProductKey", "Quantity", "NetAmount"}
    ),
    #"Set types" = Table.TransformColumnTypes(
        #"Expanded rows",
        {
            {"Name", type text},
            {"OrderDate", type date},
            {"CustomerKey", Int64.Type},
            {"ProductKey", Int64.Type},
            {"Quantity", Int64.Type},
            {"NetAmount", Currency.Type}
        },
        "en-US"
    )
in
    #"Set types"
```

Files do not fold: keep the folder small (filter files by name or date in `#"Kept CSV files"`), or move the combine upstream (dataflow, lakehouse).
