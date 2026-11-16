let
    Source = Csv.Document(File.Contents(DataFolder & "/cleaned_natural_disaster_impacts.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Selected = Table.SelectColumns(Headers, {"Event ID", "ISO", "Country", "Region", "Total Deaths",
        "Total Affected", "Total Damage, Adjusted (million US$)"}),
    Typed = Table.TransformColumnTypes(Selected, {{"Event ID", type text}, {"ISO", type text},
        {"Country", type text}, {"Region", type text}, {"Total Deaths", Int64.Type},
        {"Total Affected", Int64.Type}, {"Total Damage, Adjusted (million US$)", type number}}, "en-US")
in
    Typed
