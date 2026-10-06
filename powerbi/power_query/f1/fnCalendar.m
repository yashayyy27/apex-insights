(startDate as date,endDate as date,dataClass as text) as table =>
let
    Dates = Table.FromList(List.Dates(startDate,Duration.Days(endDate-startDate)+1,#duration(1,0,0,0)),Splitter.SplitByNothing(),{"Date"}),
    Typed = Table.TransformColumnTypes(Dates,{{"Date",type date}}),
    Year = Table.AddColumn(Typed,"Year",each Date.Year([Date]),Int64.Type),
    MonthNumber = Table.AddColumn(Year,"MonthNumber",each Date.Month([Date]),Int64.Type),
    Month = Table.AddColumn(MonthNumber,"Month",each Date.ToText([Date],"MMM","en-AU"),type text),
    YearMonth = Table.AddColumn(Month,"YearMonth",each Date.ToText([Date],"yyyy-MM","en-AU"),type text),
    Quarter = Table.AddColumn(YearMonth,"Quarter",each "Q" & Text.From(Date.QuarterOfYear([Date])),type text),
    WeekStart = Table.AddColumn(Quarter,"WeekStart",each Date.StartOfWeek([Date],Day.Monday),type date),
    Provenance = Table.AddColumn(WeekStart,"DataClass",each dataClass,type text)
in Provenance
