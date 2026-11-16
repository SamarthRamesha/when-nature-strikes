"""Build a native PBIP/PBIR report with either invented or authorized local data."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "dashboard" / "powerbi"
NAME = "When_Nature_Strikes"
DEMO = ROOT / "submission" / "powerbi" / "demo"
SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/"
FACT, EVENT = "FactImpacts", "DimEvent"
DEATHS, AFFECTED, DAMAGE = "Deaths", "Affected", "Adjusted damage USD million"
COUNT, ROWS = "Distinct events", "Country impact records"
Y = (EVENT, "Start Year")
HAZARD = (EVENT, "Disaster Type")
ISO = (FACT, "ISO")
REGION = (FACT, "Region")
COUNTRY = (FACT, "Country")
VALUES = ["Reported deaths", "Reported affected", "Adjusted damage (USD m)"]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def ident(value):
    return hashlib.sha256(value.encode()).hexdigest()[:20]


def m_string(value):
    return '"' + value.replace('"', '""').replace("\r\n", "\n").replace("\n", "#(lf)") + '"'


def column(name, kind="string", category=None):
    spec = {"name": name, "dataType": kind, "sourceColumn": name, "summarizeBy": "none"}
    if category:
        spec["dataCategory"] = category
    return spec


def partition(name, expression):
    return {"name": name, "mode": "import", "source": {"type": "m", "expression": expression.splitlines()}}


def selector(table_name, column_name, values):
    rows = ", ".join("{" + m_string(x) + "}" for x in values)
    expression = f"#table(type table [{column_name}=text], {{{rows}}})"
    return {"name": table_name, "columns": [column(column_name)],
            "partitions": [partition(table_name, expression)]}


def measures():
    records = []
    for line in (SOURCE / "Measures.dax").read_text().splitlines():
        if not line or line.startswith("//"):
            continue
        name, expression = line.split(" = ", 1)
        if "coverage" in name.lower():
            fmt = "0.0%"
        elif "mean" in name or "median" in name or name.startswith("Selected") or name == DAMAGE:
            fmt = "#,0.##"
        else:
            fmt = "#,0"
        records.append({"name": name, "expression": expression, "formatString": fmt})
    return records


def model(destination, local_folder):
    root = destination / f"{NAME}.SemanticModel"
    world = read(ROOT / "dashboard/world.geojson")
    codes = sorted({feature["properties"]["ISO_A3_EH"] for feature in world["features"]} - {"-99"})
    expressions = [{"name": "MapCountries", "kind": "m",
                    "expression": "{" + ", ".join(map(m_string, codes)) + "}"}]
    if local_folder:
        expressions.append({"name": "DataFolder", "kind": "m", "expression":
                            m_string(local_folder.as_posix()) + ' meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'})
    fact_names = ["Event ID", "ISO", "Country", "Region", "Total Deaths", "Total Affected",
                  "Total Damage, Adjusted (million US$)", "Map ISO", "Map coverage"]
    fact_types = ["string"] * 4 + ["int64", "int64", "double", "string", "string"]
    event_names = ["Event ID", "Disaster Type", "Start Year", "Decade", "Reporting era"]
    event_types = ["string", "string", "int64", "int64", "string"]
    tables = []
    for name, names, types, fixture, csv_name in [
        (FACT, fact_names, fact_types, "synthetic_impacts.csv", "cleaned_natural_disaster_impacts.csv"),
        (EVENT, event_names, event_types, "synthetic_events.csv", "natural_disaster_events.csv"),
    ]:
        expression = (SOURCE / f"{name}.m").read_text(encoding="utf-8")
        if not local_folder:
            expression = expression.replace(f'File.Contents(DataFolder & "/{csv_name}")',
                f'Text.ToBinary({m_string((SOURCE / fixture).read_text(encoding="utf-8"))})')
        columns = [column(key, kind, "Country" if key == "Map ISO" else None)
                   for key, kind in zip(names, types)]
        tables.append({"name": name, "columns": columns, "partitions": [partition(name, expression)]})
    tables[0]["measures"] = measures()
    tables.extend([selector("ImpactMetric", "Metric", VALUES),
                   selector("ImpactSummary", "Statistic", ["Total", "Mean", "Median"]),
                   selector("MapMetric", "Metric", [COUNT, *VALUES])])
    write(root / "model.bim", {"name": NAME, "compatibilityLevel": 1567, "model": {
        "culture": "en-US", "sourceQueryCulture": "en-US", "defaultPowerBIDataSourceVersion": "powerBI_V3",
        "annotations": [{"name": "PBI_QueryOrder", "value": json.dumps([x["name"] for x in expressions + tables])}],
        "tables": tables, "expressions": expressions,
        "relationships": [{"name": "2bf3ba1e-ecbb-46ca-8198-052cb946a5a0",
            "fromTable": FACT, "fromColumn": "Event ID", "fromCardinality": "many",
            "toTable": EVENT, "toColumn": "Event ID", "toCardinality": "one", "crossFilteringBehavior": "oneDirection"}]}})
    write(root / "definition.pbism", {"$schema": SCHEMA + "item/semanticModel/definitionProperties/1.0.0/schema.json",
                                     "version": "1.0", "settings": {}})
    write(root / ".platform", {"$schema": SCHEMA + "gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "SemanticModel", "displayName": NAME},
        "config": {"version": "2.0", "logicalId": "1a2c904e-4160-431c-8745-cfc601bc0f6d"}})


def literal(value):
    if isinstance(value, str):
        value = "'" + value.replace("'", "''") + "'"
    elif isinstance(value, bool):
        value = str(value).lower()
    else:
        value = f"{value}D"
    return {"expr": {"Literal": {"Value": value}}}


def props(**values):
    return [{"properties": {k: literal(v) for k, v in values.items()}}]


def projection(item):
    kind, table, name = ("Measure", FACT, item) if isinstance(item, str) else ("Column", *item)
    return {"field": {kind: {"Expression": {"SourceRef": {"Entity": table}}, "Property": name}},
            "queryRef": f"{table}.{name}", "nativeQueryRef": name, "active": True}


class Page:
    def __init__(self, parent, title, intro, mode):
        self.key = ident(title)
        self.path = parent / self.key
        self.order = 0
        write(self.path / "page.json", {"$schema": SCHEMA + "item/report/definition/page/2.1.0/schema.json",
            "name": self.key, "displayName": title, "displayOption": "FitToPage", "height": 900, "width": 1440})
        self.text(title, (24, 12, 1392, 62), 29)
        self.text(intro, (24, 75, 1392, 43), 15)
        self.text(mode, (24, 856, 1392, 36), 12)

    def visual(self, kind, title, bounds, roles=None, objects=None, options=None, config=None):
        self.order += 1
        key = ident(f"{self.key}:{self.order}")
        x, y, width, height = bounds
        visual = {"visualType": kind, "drillFilterOtherVisuals": True}
        if kind != "textbox":
            visual["visualContainerObjects"] = {"title": props(show=True, text=title)}
        if roles:
            visual["query"] = {"queryState": {role: {"projections": [projection(v) for v in items]}
                                             for role, items in roles.items()}}
        if objects:
            visual["objects"] = objects
        if options:
            visual.update(options)
        write(self.path / "visuals" / key / "visual.json", {"$schema": SCHEMA + "item/report/definition/visualContainer/2.9.0/schema.json",
            "name": key, "position": {"x": x, "y": y, "width": width, "height": height,
                                       "z": self.order, "tabOrder": self.order}, "visual": visual, **(config or {})})

    def text(self, title, bounds, fontsize):
        options = {"general": [{"properties": {"paragraphs": [{"textRuns": [{
            "value": title, "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": f"{fontsize}px",
                                          "color": "#182942"}}], "horizontalTextAlignment": "left"}]}}]}
        self.visual("textbox", "", bounds, objects=options)

    def slicer(self, name, field, bounds, mode="Dropdown", sync=False, single=False):
        values = {"data": props(mode=mode), "header": props(show=True, text=name)}
        if single:
            values["selection"] = props(singleSelect=True)
        self.visual("slicer", name, bounds, {"Values": [field]}, values,
                    {"syncGroup": {"groupName": name.replace(" ", ""), "fieldChanges": True, "filterChanges": True}} if sync else None)

    def filters(self):
        specs = [("Start year", Y, 312, "Between"), ("Hazard", HAZARD, 248, "Dropdown"),
                 ("Region", REGION, 248, "Dropdown"), ("Country", COUNTRY, 320, "Dropdown")]
        x = 24
        for name, field, width, mode in specs:
            self.slicer(name, field, (x, 120, width, 97), mode=mode, sync=True)
            x += width + 15
        self.slicer("Decade", (EVENT, "Decade"), (x, 120, 193, 97), sync=True)

    def table(self, title, bounds, fields):
        self.visual("tableEx", title, bounds, {"Values": fields})

    def chart(self, kind, title, bounds, category, values, **roles):
        self.visual(kind, title, bounds, {"Category": [category], "Y": values, **roles})

    def metric(self, x=24, width=310):
        self.slicer("Impact metric", ("ImpactMetric", "Metric"), (x, 220, width, 80), sync=True, single=True)


def mapped_filter():
    field = projection((FACT, "Map coverage"))["field"]
    constraint = {"In": {"Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "f"}},
                                                        "Property": "Map coverage"}}],
                         "Values": [[{"Literal": {"Value": "'Mapped'"}}]]}}
    return {"filterConfig": {"filters": [{"name": "Filter" + ident("map-coverage"), "field": field,
        "type": "Categorical", "howCreated": "User",
        "filter": {"Version": 2, "From": [{"Name": "f", "Entity": FACT, "Type": 0}],
                   "Where": [{"Condition": constraint}]}}]}}


def visuals(parent, mode):
    overview = Page(parent, "Disaster overview", "Count distinct events worldwide, then compare reported losses and their coverage.", mode)
    for i, value in enumerate([COUNT, ROWS, DEATHS, AFFECTED, DAMAGE]):
        overview.visual("card", value, (24 + 280*i, 228, 266, 116), {"Values": [value]})
    overview.chart("clusteredBarChart", "Distinct events by primary hazard", (24, 352, 692, 488), HAZARD, [COUNT])
    overview.table("Impact ranking and denominators by hazard", (730, 352, 686, 488),
                   [HAZARD, COUNT, DEATHS, AFFECTED, DAMAGE, "Deaths event coverage",
                    "Affected event coverage", "Adjusted damage USD million event coverage"])

    frequency = Page(parent, "Frequency vs destructiveness", "Totals combine occurrence and reported severity. Means and medians use reporting events.", mode)
    frequency.metric()
    frequency.slicer("Total, mean or median", ("ImpactSummary", "Statistic"), (350, 220, 310, 80), single=True)
    frequency.visual("scatterChart", "Frequency vs selected severity", (24, 305, 686, 535), {
        "Category": [HAZARD], "X": [COUNT], "Y": ["Selected impact summary"],
        "Tooltips": ["Selected impact reporting events", "Selected impact coverage"]})
    frequency.table("Compare total, mean and median by hazard", (728, 305, 688, 535),
        [HAZARD, COUNT, "Selected impact", "Selected impact mean", "Selected impact median",
         "Selected impact reporting events", "Selected impact coverage"])

    time = Page(parent, "Temporal analysis", "2026 is partial. Compare reporting eras before interpreting changes in recorded counts.", mode)
    time.chart("columnChart", "Annual event composition", (24, 225, 692, 302), Y, [COUNT], Series=[HAZARD])
    time.chart("lineChart", "Annual reported deaths and affected population", (730, 225, 686, 302), Y,
        [DEATHS], Y2=[AFFECTED], Tooltips=["Deaths event coverage", "Affected event coverage"])
    time.chart("lineChart", "Annual adjusted damage (USD millions)", (24, 535, 692, 303), Y, [DAMAGE],
               Tooltips=["Adjusted damage USD million reporting events", "Adjusted damage USD million event coverage"])
    time.table("Decades and reporting eras", (730, 535, 686, 303),
        [(EVENT, "Reporting era"), (EVENT, "Decade"), COUNT, DEATHS, AFFECTED, DAMAGE,
         "Adjusted damage USD million event coverage"])

    geo = Page(parent, "Geographic analysis", "Map ISO is restricted to matched codes. All country-impact records remain in the tables.", mode)
    geo.slicer("Map measure", ("MapMetric", "Metric"), (24, 220, 330, 80), single=True)
    geo.visual("card", "Mapped record coverage", (370, 220, 240, 72), {"Values": ["Mapped record coverage"]})
    geo.visual("card", "Unmatched country-impact records", (624, 220, 330, 72), {"Values": ["Unmatched records"]})
    geo.visual("azureMap", "Affected countries by ISO · marker size is the selected measure", (24, 302, 692, 536), {
        "Category": [(FACT, "Map ISO")], "Size": ["Selected map value"], "Tooltips": [
            COUNT, DEATHS, AFFECTED, DAMAGE, "Deaths record coverage", "Affected record coverage",
            "Adjusted damage USD million record coverage"]}, {"bubbleLayer": props(show=True, sizeByValue=True, clusteringEnabled=False)}, config=mapped_filter())
    geo.table("Country rankings, including unmatched ISO codes", (732, 302, 684, 322),
        [COUNTRY, ISO, (FACT, "Map coverage"), "Selected map value", COUNT, DEATHS, AFFECTED, DAMAGE])
    geo.table("Region comparison · event counts are non-additive", (732, 636, 684, 202),
        [REGION, COUNT, "Selected map value", ROWS, DEATHS, AFFECTED, DAMAGE])

    story = Page(parent, "Guided findings", "Read left to right, then use the report tabs to inspect the denominator, time series and map.", mode)
    story.metric()
    story.chart("clusteredBarChart", "1   Start with recorded frequency", (24, 305, 457, 265), HAZARD, [COUNT])
    story.chart("clusteredBarChart", "2   Compare total reported severity", (492, 300, 457, 265), HAZARD, ["Selected impact"],
        Tooltips=["Selected impact coverage"])
    story.chart("clusteredBarChart", "3   Compare mean severity among reporting events", (960, 300, 456, 265), HAZARD,
        ["Selected impact mean"], Tooltips=["Selected impact reporting events", "Selected impact coverage"])
    story.chart("lineChart", "4   Check changes over time", (24, 577, 457, 260), Y, [COUNT])
    story.chart("clusteredBarChart", "5   Inspect geographic concentration", (492, 577, 457, 260), REGION, ["Selected impact"])
    story.text("6   State the conclusion\nA hazard can lead the count, the accumulated burden or typical severity. The leaders depend on the metric. Check missing reports and partial 2026 before interpreting the ranks.", (974, 610, 391, 193), 20)
    all_pages = [overview, frequency, time, geo, story]
    for page in all_pages:
        page.filters()
    write(parent / "pages.json", {"$schema": SCHEMA + "item/report/definition/pagesMetadata/1.1.0/schema.json",
                                  "pageOrder": [page.key for page in all_pages], "activePageName": overview.key})


def build(destination, data_folder=None):
    if data_folder:
        for name in ("natural_disaster_events.csv", "cleaned_natural_disaster_impacts.csv"):
            if not (data_folder / name).is_file():
                raise FileNotFoundError(f"Run preparation first. Missing {data_folder / name}")
    if (destination / f"{NAME}.pbip").exists():
        raise FileExistsError(f"Choose a new output folder to preserve the existing Power BI project: {destination}")
    shutil.copytree(SOURCE / "template", destination, dirs_exist_ok=True)
    report = destination / f"{NAME}.Report"
    defn = report / "definition"
    visuals(defn / "pages", "SYNTHETIC DEMONSTRATION · Invented rows · Research results are in the academic report."
            if not data_folder else "EM-DAT data, 2026 · CRED / UCLouvain · www.emdat.be · Partial 2026 and uneven historical reporting.")
    report_def = read(defn / "report.json")
    report_def["themeCollection"]["customTheme"] = {"name": "WhenNatureStrikes.json",
        "reportVersionAtImport": deepcopy(report_def["themeCollection"]["baseTheme"]["reportVersionAtImport"]),
        "type": "RegisteredResources"}
    report_def["resourcePackages"].append({"name": "RegisteredResources", "type": "RegisteredResources",
        "items": [{"name": "WhenNatureStrikes.json", "path": "WhenNatureStrikes.json", "type": "CustomTheme"}]})
    report_def["settings"]["exportDataMode"] = "None"
    theme_path = report / "StaticResources/RegisteredResources/WhenNatureStrikes.json"
    theme = read(SOURCE / "theme.json")
    write(theme_path, {**theme, "name": theme_path.name})
    write(defn / "report.json", report_def)
    model(destination, data_folder)
    return destination / f"{NAME}.pbip"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--processed-data", type=Path, help="Omit to use invented demonstration rows.")
    options = parser.parse_args()
    print(build(options.output.resolve(), options.processed_data.resolve() if options.processed_data else None))
