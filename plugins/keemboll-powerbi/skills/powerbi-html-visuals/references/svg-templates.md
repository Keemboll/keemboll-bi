# SVG templates (DAX)

Replace `[Net Sales]`, `[Sales Target]`, `Dim_Date` with the model's objects. All these measures: **Image URL** data category, display folder `80 Visuals`.

## Progress bar towards a target

```dax
SVG Target Progress =
VAR _pct = MIN ( MAX ( DIVIDE ( [Net Sales], [Sales Target] ), 0 ), 1 )
VAR _w = FORMAT ( _pct * 100, "0.0", "en-US" )
VAR _color = IF ( _pct >= 1, "%232E7D32", "%231F4E79" )
VAR _label = FORMAT ( DIVIDE ( [Net Sales], [Sales Target] ), "0 %", "en-US" )
RETURN
    IF (
        NOT ISBLANK ( [Sales Target] ),
        "data:image/svg+xml;utf8,"
            & "<svg xmlns='http://www.w3.org/2000/svg' width='140' height='20' viewBox='0 0 140 20'>"
            & "<rect x='0' y='4' width='100' height='12' rx='3' fill='%23E5E7EB'/>"
            & "<rect x='0' y='4' width='" & _w & "' height='12' rx='3' fill='" & _color & "'/>"
            & "<text x='106' y='15' font-family='Segoe UI' font-size='11' fill='%231F2933'>"
            & SUBSTITUTE ( _label, "%", "%25" )
            & "</text></svg>"
    )
```

## 12-month sparkline

```dax
SVG Sales Sparkline =
VAR _w = 120
VAR _h = 30
VAR _months =
    CALCULATETABLE (
        ADDCOLUMNS (
            SUMMARIZE ( Dim_Date, Dim_Date[Year], Dim_Date[MonthNum] ),
            "@k", Dim_Date[Year] * 12 + Dim_Date[MonthNum],
            "@v", [Net Sales]
        ),
        DATESINPERIOD ( Dim_Date[Date], MAX ( Dim_Date[Date] ), -12, MONTH )
    )
VAR _kMin = MINX ( _months, [@k] )
VAR _kMax = MAXX ( _months, [@k] )
VAR _vMin = MINX ( _months, [@v] )
VAR _vMax = MAXX ( _months, [@v] )
VAR _points =
    CONCATENATEX (
        _months,
        FORMAT ( DIVIDE ( [@k] - _kMin, _kMax - _kMin ) * ( _w - 4 ) + 2, "0.0", "en-US" )
            & ","
            & FORMAT ( _h - 2 - DIVIDE ( [@v] - _vMin, _vMax - _vMin ) * ( _h - 4 ), "0.0", "en-US" ),
        " ",
        [@k], ASC
    )
RETURN
    IF (
        COUNTROWS ( _months ) > 1,
        "data:image/svg+xml;utf8,"
            & "<svg xmlns='http://www.w3.org/2000/svg' width='" & _w & "' height='" & _h
            & "' viewBox='0 0 " & _w & " " & _h & "'>"
            & "<polyline fill='none' stroke='%231F4E79' stroke-width='2' stroke-linejoin='round' points='"
            & _points
            & "'/></svg>"
    )
```

Works because `Dim_Date` is marked as a date table: the `DATESINPERIOD` filter on `Dim_Date[Date]` replaces the current row's filters (month, year).

## Change arrow vs PY

```dax
SVG Trend =
VAR _change = [Net Sales Change %]
VAR _up = _change >= 0
VAR _color = IF ( _up, "%232E7D32", "%23C62828" )
VAR _shape =
    IF (
        _up,
        "<polygon points='8,2 14,12 2,12' fill='" & _color & "'/>",
        "<polygon points='2,4 14,4 8,14' fill='" & _color & "'/>"
    )
RETURN
    IF (
        NOT ISBLANK ( _change ),
        "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 16 16'>"
            & _shape & "</svg>"
    )
```

The shape (up/down) carries the meaning in addition to the colour — accessibility compliant.

## Bullet chart (actual / target / PY)

```dax
SVG Bullet =
VAR _actual = [Net Sales]
VAR _target = [Sales Target]
VAR _py = [Net Sales PY]
VAR _max = MAX ( MAX ( _actual, _target ), _py )
VAR _scale = 130
VAR _xActual = FORMAT ( DIVIDE ( _actual, _max ) * _scale, "0.0", "en-US" )
VAR _xTarget = FORMAT ( COALESCE ( DIVIDE ( _target, _max ), 0 ) * _scale, "0.0", "en-US" )
VAR _xPY = FORMAT ( COALESCE ( DIVIDE ( _py, _max ), 0 ) * _scale, "0.0", "en-US" )
RETURN
    IF (
        NOT ISBLANK ( _actual ),
        "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='140' height='20' viewBox='0 0 140 20'>"
            & "<rect x='0' y='2' width='" & _xPY & "' height='16' fill='%23E5E7EB'/>"
            & "<rect x='0' y='7' width='" & _xActual & "' height='6' fill='%231F4E79'/>"
            & "<rect x='" & _xTarget & "' y='3' width='2' height='14' fill='%23E76F51'/>"
            & "</svg>"
    )
```

Grey background = PY, blue bar = actual, orange tick = target.

## Status dot

```dax
SVG Status =
VAR _color =
    SWITCH (
        TRUE (),
        [Gross Margin %] >= 0.30, "%232E7D32",
        [Gross Margin %] >= 0.15, "%23E9C46A",
        "%23C62828"
    )
RETURN
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'>"
        & "<circle cx='6' cy='6' r='5' fill='" & _color & "'/></svg>"
```

Default thresholds: 30 % and 15 %. Show the value in a neighbouring column (colour alone is not enough).
