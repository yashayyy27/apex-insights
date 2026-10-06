(relativePath as text, types as list, keyColumns as list, nullableColumns as list, permittedClasses as list) as table =>
let
    Source = Csv.Document(File.Contents(DataRoot & relativePath),[Delimiter=",",Encoding=65001,QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source,[PromoteAllScalars=true]),
    Expected = List.Transform(types, each _{0}),
    SchemaChecked = if List.Sort(Table.ColumnNames(Headers)) <> List.Sort(Expected) then error "CSV schema mismatch: " & relativePath else Headers,
    Trimmed = Table.TransformColumns(SchemaChecked,List.Transform(Expected,(c)=>{c,each if _=null then null else Text.Trim(Text.From(_)),type nullable text})),
    EmptyToNull = Table.ReplaceValue(Trimmed,"",null,Replacer.ReplaceValue,Expected),
    Typed = Table.TransformColumnTypes(EmptyToNull,types,"en-AU"),
    RequiredColumns = List.Difference(Expected,nullableColumns),
    InvalidNulls = Table.SelectRows(Typed,(row)=>List.AnyTrue(List.Transform(RequiredColumns,(c)=>Record.Field(row,c)=null))),
    NullChecked = if Table.RowCount(InvalidNulls)>0 then error "Missing required value: " & relativePath else Typed,
    KeyGroups = Table.Group(NullChecked,keyColumns,{{"Rows",each Table.RowCount(_),Int64.Type}}),
    DuplicateKeys = Table.SelectRows(KeyGroups,each [Rows]>1),
    KeyChecked = if Table.RowCount(DuplicateKeys)>0 then error "Duplicate logical key: " & relativePath else NullChecked,
    InvalidClasses = Table.SelectRows(KeyChecked,each not List.Contains(permittedClasses,[DataClass])),
    Result = if Table.RowCount(InvalidClasses)>0 then error "Provenance mismatch: " & relativePath else KeyChecked
in Result
