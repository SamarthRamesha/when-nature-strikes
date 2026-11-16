let
    Source = Csv.Document(File.Contents(DataFolder & "/natural_disaster_events.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Selected = Table.SelectColumns(Headers, {"Event ID", "Disaster Type", "Start Year", "Decade"}),
    Typed = Table.TransformColumnTypes(Selected, {{"Event ID", type text}, {"Disaster Type", type text},
        {"Start Year", Int64.Type}, {"Decade", Int64.Type}}, "en-US"),
    Era = Table.AddColumn(Typed, "Reporting era", each if [Start Year] < 2000 then "1900–1999"
        else if [Start Year] <= 2025 then "2000–2025" else "2026 partial", type text)
in
    Era
