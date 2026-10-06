let
    Base = fnLoadCsv("fmcg/DimProduct.csv",{{"ProductKey",Int64.Type},{"Product",type text},{"Brand",type text},{"CategoryKey",Int64.Type},{"Category",type text},{"PackMl",Int64.Type},{"Innovation",Int64.Type},{"LaunchDate",type date},{"RegularPrice",type number},{"UnitCost",type number},{"DataClass",type text}},{"ProductKey"},{},{"SYNTHETIC"}),
    Joined = Table.NestedJoin(Base,{"CategoryKey"},DimCategory,{"CategoryKey"},"CategoryMap",JoinKind.LeftOuter),
    BadMappings = Table.SelectRows(Joined,each Table.RowCount([CategoryMap])<>1),
    Checked = if Table.RowCount(BadMappings)>0 then error "Invalid category mapping" else Joined,
    NoOldCategory = Table.RemoveColumns(Checked,{"Category"}),
    Result = Table.ExpandTableColumn(NoOldCategory,"CategoryMap",{"Category"},{"Category"})
in Result
