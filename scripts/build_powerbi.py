"""Build a native PBIP/PBIR report with either invented or authorized local data."""
import argparse
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
SUBGROUP = (EVENT, "Disaster Subgroup")
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
    for line in (SOURCE / "Measures.dax").read_text(encoding="utf-8").splitlines():
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
    event_names = ["Event ID", "Disaster Type", "Disaster Subgroup", "Start Year", "Decade", "Reporting era"]
    event_types = ["string", "string", "string", "int64", "int64", "string"]
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
    def __init__(self, parent, title, intro, mode, original=None, width=1440, height=900):
        self.key = original["name"] if original else ident(title)
        self.path = parent / self.key
        self.order = 100_000 if original else 0
        metadata = original or {"$schema": SCHEMA + "item/report/definition/page/2.1.0/schema.json",
                                "name": self.key, "displayOption": "FitToPage"}
        write(self.path / "page.json", {**metadata, "displayName": title, "height": height, "width": width})
        if intro:
            self.text(title, (24, 12, width - 48, 62), 29)
            self.text(intro, (24, 75, width - 48, 43), 15)
        self.text(mode, (24, height - 44, width - 48, 36), 12)

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
        specs = [("Start year", Y, 247, "Between"), ("Hazard", HAZARD, 214, "Dropdown"),
                 ("Subgroup", SUBGROUP, 205, "Dropdown"), ("Country", COUNTRY, 245, "Dropdown"),
                 ("Region", REGION, 207, "Dropdown"), ("Decade", (EVENT, "Decade"), 196, "Dropdown")]
        x = 24
        for name, field, width, mode in specs:
            self.slicer(name, field, (x, 120, width, 97), mode=mode, sync=True)
            x += width + 15

    def table(self, title, bounds, fields):
        self.visual("tableEx", title, bounds, {"Values": fields})

    def chart(self, kind, title, bounds, category, values, **roles):
        self.visual(kind, title, bounds, {"Category": [category], "Y": values, **roles})

    def metric(self, x=24, width=310):
        self.slicer("Impact metric", ("ImpactMetric", "Metric"), (x, 220, width, 80), sync=True, single=True)


def mapped_filter(visual_key):
    field = projection((FACT, "Map coverage"))["field"]
    constraint = {"In": {"Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "f"}},
                                                        "Property": "Map coverage"}}],
                         "Values": [[{"Literal": {"Value": "'Mapped'"}}]]}}
    return {"name": "Filter" + ident(visual_key + ":map-coverage"), "field": field,
        "type": "Categorical", "howCreated": "User",
        "filter": {"Version": 2, "From": [{"Name": "f", "Entity": FACT, "Type": 0}],
                   "Where": [{"Condition": constraint}]}}


ORIGINAL_FACT = "cleaned_natural_disaster_impacts"
EVENT_FIELDS = {"Start Year", "Decade", "Disaster Type", "Disaster Subgroup"}
DONOR_MEASURES = {"Total Disaster Events": COUNT, "Total Deaths Measure": DEATHS,
                  "Total Affected Measure": AFFECTED, "Total Economic Damage Measure": DAMAGE}
AGGREGATES = {
    (2, "Event ID"): COUNT, (2, "Country"): ROWS,
    (0, "Total Deaths"): DEATHS, (0, "Total Affected"): AFFECTED,
    (0, "Total Damage, Adjusted (million US$)"): DAMAGE,
    (1, "Total Deaths"): "Deaths per reporting event",
    (1, "Total Affected"): "Affected per reporting event",
    (1, "Total Damage, Adjusted (million US$)"): "Adjusted damage USD million per reporting event",
}
SLICER_GROUPS = {"Start Year": "Startyear", "Disaster Type": "Hazard", "Disaster Subgroup": "Subgroup",
                 "Country": "Country"}


def rebind_donor(value):
    if isinstance(value, list):
        return [rebind_donor(child) for child in value]
    if not isinstance(value, dict):
        return value
    if "Aggregation" in value and len(value) == 1:
        aggregate = value["Aggregation"]
        column = aggregate["Expression"]["Column"]
        measure = AGGREGATES[aggregate["Function"], column["Property"]]
        return projection(measure)["field"]
    for kind in ("Column", "Measure"):
        if kind in value and len(value) == 1:
            field = value[kind]
            source = field["Expression"]["SourceRef"]
            name = field["Property"]
            if source.get("Entity") == ORIGINAL_FACT or "Source" in source:
                table = EVENT if kind == "Column" and name in EVENT_FIELDS else FACT
                if "Source" in source and table != FACT:
                    raise ValueError(f"An aliased expression needs a separate event-table binding: {name}")
                return {kind: {"Expression": {"SourceRef": {"Entity": table} if "Entity" in source else source},
                               "Property": DONOR_MEASURES[name] if kind == "Measure" else name}}
    result = {key: rebind_donor(child) for key, child in value.items()}
    if result.get("Entity") == ORIGINAL_FACT:
        result["Entity"] = FACT
    if "queryRef" in result and "field" in result:
        kind, field = next(iter(result["field"].items()))
        name = field["Property"]
        table = field["Expression"]["SourceRef"]["Entity"]
        result.update(queryRef=f"{table}.{name}", nativeQueryRef=name)
        if kind == "Measure":
            result.pop("displayName", None)
            result.pop("format", None)
    return result


def set_title(visual, title):
    visual.setdefault("visualContainerObjects", {})["title"] = props(show=True, text=title)


def use_measure(query, role, name):
    query[role] = {"projections": [projection(name)]}


def write_donor(page, item, bounds, title=None):
    item["$schema"] = SCHEMA + "item/report/definition/visualContainer/2.9.0/schema.json"
    if bounds:
        item["position"].update(dict(zip(("x", "y", "width", "height"), bounds)))
    if title:
        set_title(item["visual"], title)
    write(page.path / "visuals" / item["name"] / "visual.json", item)


def sync_donor_slicer(item):
    visual = item["visual"]
    if visual["visualType"] in {"slicer", "listSlicer", "advancedSlicerVisual"}:
        field = visual["query"]["queryState"]["Values"]["projections"][0]["nativeQueryRef"]
        visual["syncGroup"] = {"groupName": SLICER_GROUPS[field], "fieldChanges": True, "filterChanges": True}


def analytical_page(parent, source, mode, index):
    metadata = source["page"]
    if index == 0:
        metadata = {**metadata, "visualInteractions": [{"source": "96ba834ff9b0a6a81654",
                     "target": "94a940d981597197da42", "type": "HighlightFilter"}]}
    elif index == 1:
        metadata = {**metadata, "visualInteractions": [{"source": "20e3106732e317d087a2",
                     "target": "03d8d43a3e9c1d439cee", "type": "DataFilter"}]}
    page = Page(parent, metadata["displayName"], None, mode, original=metadata, width=1280, height=1157)
    page.slicer("Region", REGION, (12, 143, 345, 78), sync=True)
    page.slicer("Decade", (EVENT, "Decade"), (373, 143, 285, 78), sync=True)
    page.text("Worldwide frequency counts each event once. Losses and coverage follow the selected country records.",
              (680, 154, 586, 48), 13)
    for definition in source["visuals"]:
        item = rebind_donor(definition)
        visual, key, position = item["visual"], item["name"], item["position"]
        sync_donor_slicer(item)
        if position["y"] >= 130:
            position["y"] += 172 if index == 1 and position["y"] >= 240 else 92
        title = None
        if key == "03d8d43a3e9c1d439cee":
            query = visual["query"]["queryState"]
            use_measure(query, "Y", "Selected impact summary")
            query["Tooltips"] = {"projections": [projection(name) for name in
                                 ("Selected impact reporting events", "Selected impact coverage")]}
            title = "Frequency vs selected impact · bubble size is mean affected"
        elif key == "f43d8d4d1ad49b175c85":
            title = "Mean deaths per reporting event"
        write_donor(page, item, None, title)
    if index == 0:
        page.table("Reporting denominators and coverage by hazard", (12, 813, 1256, 288),
                   [HAZARD, COUNT, ROWS, "Deaths reporting events", "Deaths event coverage",
                    "Affected reporting events", "Affected event coverage", "Adjusted damage USD million reporting events",
                    "Adjusted damage USD million event coverage"])
    elif index == 1:
        page.slicer("Impact metric", ("ImpactMetric", "Metric"), (12, 333, 360, 78), sync=True, single=True)
        page.slicer("Total, mean or median", ("ImpactSummary", "Statistic"), (385, 333, 370, 78), single=True)
        page.table("Compare total, mean and median by hazard", (12, 889, 1256, 218),
                   [HAZARD, COUNT, "Selected impact", "Selected impact mean", "Selected impact median",
                    "Selected impact reporting events", "Selected impact coverage"])
    else:
        page.chart("lineChart", "Annual population reported affected", (12, 816, 622, 288), Y, [AFFECTED],
                   Tooltips=["Affected reporting events", "Affected event coverage"])
        page.chart("lineChart", "Annual adjusted damage (USD millions)", (646, 816, 622, 288), Y, [DAMAGE],
                   Tooltips=["Adjusted damage USD million reporting events", "Adjusted damage USD million event coverage"])
    return page


GEO_LAYOUT = {
    "3477b47821a0eb1e8d0d": (24, 120, 247, 97),
    "ce17bae6cadc2ee0ee1d": (286, 120, 214, 97),
    "6e122e0be96860760d20": (515, 120, 205, 97),
    "5540586200eb90326aa4": (24, 224, 250, 71),
    "3861bc63e7a894b55dbe": (287, 224, 250, 71),
    "aa650244ae4c99249998": (550, 224, 270, 71),
    "38fad0a20bd3e020b5c4": (24, 302, 688, 294),
    "4618535f5a4d546b0659": (728, 302, 688, 294),
    "2a77265447a136330b71": (24, 604, 456, 231),
    "4be409d3686d46c90ad0": (492, 604, 456, 231),
    "ddadb0af689445aa685b": (960, 604, 456, 231),
}


def geographic_page(parent, source, mode):
    metadata = source["page"]
    interactions = [{"source": map_id, "target": bar_id, "type": "DataFilter"}
                    for map_id in ("38fad0a20bd3e020b5c4", "4618535f5a4d546b0659")
                    for bar_id in ("2a77265447a136330b71", "4be409d3686d46c90ad0", "ddadb0af689445aa685b")]
    metadata = {**metadata, "visualInteractions": metadata["visualInteractions"] + interactions}
    geo = Page(parent, "Geographic Analysis", "Explore country impacts by ISO. Rankings and region comparisons work when map services are unavailable.",
               mode, original=metadata, height=1124)
    geo.slicer("Country", COUNTRY, (735, 120, 245, 97), sync=True)
    geo.slicer("Region", REGION, (995, 120, 207, 97), sync=True)
    geo.slicer("Decade", (EVENT, "Decade"), (1217, 120, 196, 97), sync=True)
    geo.slicer("Filled map measure", ("MapMetric", "Metric"), (833, 224, 265, 76), single=True)
    geo.visual("card", "Map record coverage", (1111, 224, 305, 71), {"Values": ["Mapped record coverage"]})
    titles = {"map": "Country damage by hazard (USD millions)", "filledMap": "Countries by selected measure",
              "advancedSlicerVisual": "Hazard", "listSlicer": "Subgroup"}
    for definition in source["visuals"]:
        item = rebind_donor(definition)
        visual, key = item["visual"], item["name"]
        kind = visual["visualType"]
        sync_donor_slicer(item)
        title = titles.get(kind)
        if key == "3477b47821a0eb1e8d0d":
            visual["objects"]["data"] = props(mode="Between")
            title = "Start year"
        elif key == "aa650244ae4c99249998":
            title = "Adjusted damage (USD millions)"
        elif kind in {"map", "filledMap"}:
            query = visual["query"]["queryState"]
            query["Category"] = {"projections": [projection((FACT, "Map ISO"))]}
            query["Tooltips"] = {"projections": [projection(name) for name in
                                 (COUNT, DEATHS, AFFECTED, DAMAGE, "Deaths record coverage",
                                  "Affected record coverage", "Adjusted damage USD million record coverage")]}
            item["filterConfig"]["filters"].append(mapped_filter(key))
            if kind == "filledMap":
                fill = visual["objects"]["dataPoint"][1]["properties"]["fill"]["solid"]["color"]["expr"]["FillRule"]
                fill["Input"] = projection("Selected map value")["field"]
                fill["FillRule"].pop("nullColoringStrategy", None)
        write_donor(geo, item, GEO_LAYOUT[key], title)
    geo.table("Country rankings and unmatched ISO codes", (24, 845, 688, 228),
              [COUNTRY, ISO, (FACT, "Map coverage"), "Selected map value", COUNT, DEATHS, AFFECTED, DAMAGE])
    geo.table("Region comparison and reporting coverage", (728, 845, 688, 228),
              [REGION, COUNT, ROWS, DEATHS, AFFECTED, DAMAGE, "Adjusted damage USD million record coverage"])
    return geo


def visuals(parent, mode):
    overview, frequency, time, geography = read(SOURCE / "team_visuals.json")
    all_pages = [analytical_page(parent, source, mode, index) for index, source in enumerate((overview, frequency, time))]
    all_pages.append(geographic_page(parent, geography, mode))
    story = Page(parent, "Guided Findings", "Read left to right, then use the report tabs to inspect the denominator, time series and map.", mode)
    story.filters()
    story.metric()
    story.chart("clusteredBarChart", "1   Start with recorded frequency", (24, 305, 457, 265), HAZARD, [COUNT])
    story.chart("clusteredBarChart", "2   Compare total reported severity", (492, 300, 457, 265), HAZARD, ["Selected impact"],
        Tooltips=["Selected impact coverage"])
    story.chart("clusteredBarChart", "3   Compare mean severity among reporting events", (960, 300, 456, 265), HAZARD,
        ["Selected impact mean"], Tooltips=["Selected impact reporting events", "Selected impact coverage"])
    story.chart("lineChart", "4   Check changes over time", (24, 577, 457, 260), Y, [COUNT])
    story.chart("clusteredBarChart", "5   Inspect geographic concentration", (492, 577, 457, 260), REGION, ["Selected impact"])
    story.text("6   State the conclusion\nA hazard can lead the count, the accumulated burden or typical severity. The leaders depend on the metric. Check missing reports and partial 2026 before interpreting the ranks.", (974, 610, 391, 193), 20)
    all_pages.append(story)
    write(parent / "pages.json", {"$schema": SCHEMA + "item/report/definition/pagesMetadata/1.1.0/schema.json",
                                  "pageOrder": [page.key for page in all_pages], "activePageName": all_pages[0].key})


def build(destination, data_folder=None):
    if data_folder:
        for name in ("natural_disaster_events.csv", "cleaned_natural_disaster_impacts.csv"):
            if not (data_folder / name).is_file():
                raise FileNotFoundError(f"Run preparation first. Missing {data_folder / name}")
    if (destination / f"{NAME}.pbip").exists():
        raise FileExistsError(f"Choose a new output folder to preserve the existing Power BI project: {destination}")
    report = f"{NAME}.Report"
    # The checked-in PBIP is the source for shared report metadata. Copy only
    # these files so a local Desktop cache or generated model cannot carry over.
    for relative in (
        f"{NAME}.pbip",
        f"{report}/.platform",
        f"{report}/definition.pbir",
        f"{report}/definition/report.json",
        f"{report}/definition/version.json",
        f"{report}/StaticResources/SharedResources/BaseThemes/Fluent2-CY26SU10.json",
    ):
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(DEMO / relative, target)
    report = destination / report
    visuals(report / "definition/pages", "SYNTHETIC DEMONSTRATION · Invented rows · Research results are in the academic report."
            if not data_folder else "EM-DAT data, 2026 · CRED / UCLouvain · www.emdat.be · Partial 2026 and uneven historical reporting.")
    theme_path = report / "StaticResources/RegisteredResources/WhenNatureStrikes.json"
    theme = read(SOURCE / "theme.json")
    write(theme_path, {**theme, "name": theme_path.name})
    model(destination, data_folder)
    return destination / f"{NAME}.pbip"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--processed-data", type=Path, help="Omit to use invented demonstration rows.")
    options = parser.parse_args()
    print(build(options.output.resolve(), options.processed_data.resolve() if options.processed_data else None))
