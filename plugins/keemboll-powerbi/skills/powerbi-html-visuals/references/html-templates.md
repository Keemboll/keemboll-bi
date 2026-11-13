# HTML templates (HTML Content visual)

The *HTML Content* visual (AppSource) displays the HTML returned by a measure. Inline CSS only, no script. Check that custom visuals are allowed in the tenant.

## KPI card

```dax
HTML Sales Card =
VAR _sales = FORMAT ( [Net Sales], "€#,##0" )
VAR _change = [Net Sales Change %]
VAR _color = IF ( _change >= 0, "#2E7D32", "#C62828" )
VAR _sign = IF ( _change >= 0, "▲", "▼" )
RETURN
    "<div style='font-family:Segoe UI;padding:12px;border-left:4px solid #1F4E79;background:#FFFFFF'>"
        & "<div style='font-size:12px;color:#52606D'>Net Sales</div>"
        & "<div style='font-size:28px;font-weight:600;color:#1F2933'>" & _sales & "</div>"
        & IF (
            NOT ISBLANK ( _change ),
            "<div style='font-size:12px;color:" & _color & "'>" & _sign & " "
                & FORMAT ( ABS ( _change ), "0.0 %" ) & " vs PY</div>"
        )
        & "</div>"
```

Here `#` does **not** need encoding: this is not a data URI.

## Top 5 list with escaped text

```dax
HTML Top 5 Products =
VAR _top =
    TOPN ( 5, ALLSELECTED ( Dim_Product[Product] ), [Net Sales], DESC )
VAR _rows =
    CONCATENATEX (
        _top,
        VAR _name =
            SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( Dim_Product[Product], "&", "&amp;" ), "<", "&lt;" ), ">", "&gt;" )
        RETURN
            "<li style='display:flex;justify-content:space-between;padding:2px 0'>"
                & "<span>" & _name & "</span>"
                & "<span style='font-weight:600'>" & FORMAT ( [Net Sales], "€#,##0" ) & "</span></li>",
        "",
        [Net Sales], DESC
    )
RETURN
    "<ol style='font-family:Segoe UI;font-size:12px;margin:0;padding-left:18px;color:#1F2933'>"
        & _rows & "</ol>"
```

## Good practices

- One HTML visual = one measure; do not concatenate whole pages.
- Use the colours of the `theme-keemboll.json` theme.
- Fill in the visual's alt text (a DAX measure that summarises the content).
- If custom visuals are not allowed, fall back to native cards + SVG.
