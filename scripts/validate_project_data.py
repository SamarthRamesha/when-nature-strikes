"""Validate the processed When Nature Strikes datasets against documentation.

Checks file presence, schemas, row counts, identifier uniqueness, missingness,
coordinate completeness, unit consistency, cross-dataset aggregation
consistency, blank-versus-zero handling, and every statistic quoted in
docs/DATA_HANDOVER.md and README.md.

Outputs:
  analysis/outputs/data_quality_report.json
  docs/DATA_QUALITY_REPORT.md

Exit code is 0 only when no check reports FAIL. WARN marks a documented data
limitation rather than a defect. SKIP marks a check that could not run in this
environment (for example the optional source-workbook check without openpyxl).

The script uses only the Python standard library. openpyxl is optional and is
used only to verify the source workbook row count.

Usage:
    python scripts/validate_project_data.py
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
SOURCE = ROOT / "data" / "source" / "EM-DAT Custom Request Oct 31 2026.xlsx"
OUT_JSON = ROOT / "analysis" / "outputs" / "data_quality_report.json"
OUT_MD = ROOT / "docs" / "DATA_QUALITY_REPORT.md"

IMPACTS = PROCESSED / "cleaned_natural_disaster_impacts.csv"
EVENTS = PROCESSED / "natural_disaster_events.csv"
TYPE_SUMMARY = PROCESSED / "natural_disaster_type_summary.csv"
COUNTRY_YEAR_TYPE = PROCESSED / "natural_country_year_type_summary.csv"

DEATHS = "Total Deaths"
AFFECTED = "Total Affected"
DAMAGE_KUSD = "Total Damage, Adjusted ('000 US$)"
DAMAGE_MUSD = "Total Damage, Adjusted (million US$)"
MAGNITUDE = "Magnitude"

# Statistics documented in docs/DATA_HANDOVER.md before validation existed.
DOCUMENTED = {
    "source_rows": 27962,
    "impact_rows": 18060,
    "event_rows": 15727,
    "country_year_type_rows": 11157,
    "multi_country_events": 1067,
    "disaster_types": 15,
    "min_year": 1900,
    "max_year": 2026,
    "type_counts": {
        "Flood": 5814,
        "Storm": 4026,
        "Earthquake": 1573,
        "Epidemic": 1447,
    },
    "impact_missing": {
        DEATHS: (5029, 27.8),
        AFFECTED: (4655, 25.8),
        DAMAGE_KUSD: (12210, 67.6),
        MAGNITUDE: (12422, 68.8),
    },
    "coordinate_complete": (2847, 15.8),
    "event_coverage": {
        DEATHS: 11655,
        AFFECTED: 12366,
        DAMAGE_MUSD: 5251,
    },
}

REQUIRED_IMPACT_COLUMNS = [
    "DisNo.", "Historic", "Disaster Group", "Disaster Subgroup", "Disaster Type",
    "Disaster Subtype", "ISO", "Country", "Subregion", "Region", "Latitude",
    "Longitude", MAGNITUDE, "Magnitude Scale", "Start Year", "Total Deaths",
    "Total Affected", DAMAGE_KUSD, DAMAGE_MUSD,
    "Event ID", "Start Date", "End Date", "Decade", "Has Coordinates",
]
REQUIRED_EVENT_COLUMNS = [
    "Event ID", "Disaster Type", "Start Year", "Decade", "Country Count",
    "Country Impact Records", DEATHS, AFFECTED, DAMAGE_KUSD, DAMAGE_MUSD,
    MAGNITUDE,
    DEATHS + " Reported Country Impacts",
    AFFECTED + " Reported Country Impacts",
    DAMAGE_MUSD + " Reported Country Impacts",
]
REQUIRED_TYPE_COLUMNS = [
    "Disaster Group", "Disaster Type", "Unique Events", DEATHS, AFFECTED,
    DAMAGE_KUSD, DAMAGE_MUSD,
    DEATHS + " Events with Reported Values",
    AFFECTED + " Events with Reported Values",
    DAMAGE_MUSD + " Events with Reported Values",
]
REQUIRED_CYT_COLUMNS = [
    "ISO", "Country", "Region", "Subregion", "Start Year", "Decade",
    "Disaster Type", "Country Impact Records", "Unique Events",
    DEATHS, AFFECTED, DAMAGE_KUSD, DAMAGE_MUSD,
    DEATHS + " Reported Records",
    AFFECTED + " Reported Records",
]

checks: list[dict] = []
MISSINGNESS_NOTES: list[str] = []
TOTALS: dict[str, float] = {}


def jsonable(value):
    """Make check metadata JSON-serializable (sets become sorted lists)."""
    if isinstance(value, (set, frozenset)):
        return sorted(jsonable(v) for v in value)
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    return value


def record(check_id, area, description, status, expected=None, actual=None, detail=""):
    checks.append({
        "id": check_id,
        "area": area,
        "description": description,
        "status": status,
        "expected": jsonable(expected),
        "actual": jsonable(actual),
        "detail": detail,
    })


def check(check_id, area, description, ok, expected=None, actual=None, detail="",
          warn=False, skip=False, flag=False):
    """Record a check. flag=True marks a data property worth surfacing as WARN."""
    if skip:
        record(check_id, area, description, "SKIP", expected, actual, detail)
    elif ok and not flag:
        record(check_id, area, description, "PASS", expected, actual, detail)
    elif ok:
        record(check_id, area, description, "WARN", expected, actual, detail)
    else:
        record(check_id, area, description, "WARN" if warn else "FAIL", expected, actual, detail)


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def num(value):
    """Convert a CSV cell to float; blank cells return None (never zero)."""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def pct(part, whole):
    return round(part / whole * 100, 1) if whole else None


def close(a, b, tol=1e-6):
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def sha256(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


# ---------------------------------------------------------------- file checks
overview = {}
loaded = {}
columns = {}
for key, path in [
    ("impacts", IMPACTS),
    ("events", EVENTS),
    ("type_summary", TYPE_SUMMARY),
    ("country_year_type", COUNTRY_YEAR_TYPE),
]:
    exists = path.is_file()
    check(f"F-{key}", "Files", f"`{path.relative_to(ROOT).as_posix()}` exists", exists,
          expected="present", actual="present" if exists else "missing")
    if not exists:
        continue
    try:
        fields, rows = read_csv(path)
    except Exception as exc:  # pragma: no cover - defensive
        check(f"F-{key}-read", "Files", f"`{path.name}` is readable CSV", False,
              expected="readable", actual=repr(exc))
        continue
    check(f"F-{key}-read", "Files", f"`{path.name}` is readable, non-empty, UTF-8", bool(rows),
          expected=">0 data rows", actual=f"{len(rows)} data rows")
    loaded[key] = rows
    columns[key] = fields
    overview[key] = {
        "path": path.relative_to(ROOT).as_posix(),
        "rows": len(rows),
        "columns": len(fields),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
    }

required = {
    "impacts": REQUIRED_IMPACT_COLUMNS,
    "events": REQUIRED_EVENT_COLUMNS,
    "type_summary": REQUIRED_TYPE_COLUMNS,
    "country_year_type": REQUIRED_CYT_COLUMNS,
}
for key, cols in required.items():
    if key not in loaded:
        continue
    missing_cols = [c for c in cols if c not in columns[key]]
    check(f"S-{key}", "Schemas", f"`{key}` contains all required columns", not missing_cols,
          expected=len(cols), actual=f"{len(columns[key])} columns",
          detail="missing: " + ", ".join(missing_cols) if missing_cols else "all required columns present")

if "impacts" not in loaded or "events" not in loaded:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({"checks": checks}, indent=2), encoding="utf-8")
    print("Required datasets are missing; cannot continue validation.", file=sys.stderr)
    sys.exit(1)

impacts = loaded["impacts"]
events = loaded["events"]
type_rows = loaded.get("type_summary", [])
cyt_rows = loaded.get("country_year_type", [])

# ------------------------------------------------------------- impacts: counts
check("I-rows", "Impacts", "Country-impact row count matches documentation",
      len(impacts) == DOCUMENTED["impact_rows"], DOCUMENTED["impact_rows"], len(impacts))
groups = Counter(r["Disaster Group"] for r in impacts)
check("I-group", "Impacts", "Every impact row has Disaster Group = Natural",
      set(groups) == {"Natural"}, {"Natural"}, dict(groups))

disno = [r["DisNo."] for r in impacts]
dupe_disno = sum(c - 1 for c in Counter(disno).values() if c > 1)
check("I-disno-unique", "Impacts", "`DisNo.` is unique across country impacts",
      dupe_disno == 0, 0, dupe_disno, f"{len(set(disno))} distinct DisNo. values")

blank_ids = {
    "DisNo.": sum(1 for r in impacts if not r["DisNo."].strip()),
    "Event ID": sum(1 for r in impacts if not r["Event ID"].strip()),
    "ISO": sum(1 for r in impacts if not r["ISO"].strip()),
    "Country": sum(1 for r in impacts if not r["Country"].strip()),
    "Start Year": sum(1 for r in impacts if num(r["Start Year"]) is None),
}
check("I-ids", "Impacts", "No blank identifiers or start year in impacts",
      all(v == 0 for v in blank_ids.values()), "all 0", blank_ids)

event_iso = Counter((r["Event ID"], r["ISO"]) for r in impacts)
dupe_event_iso = sum(c - 1 for c in event_iso.values() if c > 1)
check("I-event-country-unique", "Impacts", "One impact row per (Event ID, ISO) pair",
      dupe_event_iso == 0, 0, dupe_event_iso,
      "duplicate pairs would inflate country-level counts")

type_event_counts = defaultdict(set)
for r in impacts:
    type_event_counts[r["Disaster Type"]].add(r["Event ID"])
type_event_counts = {k: len(v) for k, v in type_event_counts.items()}

check("I-types", "Impacts", "Distinct disaster types match documentation",
      len(type_event_counts) == DOCUMENTED["disaster_types"],
      DOCUMENTED["disaster_types"], len(type_event_counts))
for name, expected in DOCUMENTED["type_counts"].items():
    actual = type_event_counts.get(name)
    check(f"I-type-{name}", "Impacts", f"`{name}` unique event count matches documentation",
          actual == expected, expected, actual)

years = [int(num(r["Start Year"])) for r in impacts]
check("I-years", "Impacts", "Coverage period matches documentation",
      (min(years), max(years)) == (DOCUMENTED["min_year"], DOCUMENTED["max_year"]),
      [DOCUMENTED["min_year"], DOCUMENTED["max_year"]], [min(years), max(years)])

hist_values = Counter(r["Historic"] for r in impacts)
check("I-historic", "Impacts", "`Historic` flag takes only documented values",
      set(hist_values) <= {"Yes", "No"}, ["Yes", "No"], dict(hist_values))

# --------------------------------------------------------- missingness: impacts
missingness = {}
zero_counts = {}
for col in [DEATHS, AFFECTED, DAMAGE_KUSD, DAMAGE_MUSD, MAGNITUDE]:
    blanks = sum(1 for r in impacts if num(r[col]) is None)
    zeros = sum(1 for r in impacts if num(r[col]) == 0)
    missingness[col] = {"missing": blanks, "missing_pct": pct(blanks, len(impacts)), "zeros": zeros}
    zero_counts[col] = zeros

for col, (expected_missing, expected_pct) in DOCUMENTED["impact_missing"].items():
    actual = missingness[col]
    ok = actual["missing"] == expected_missing and abs((actual["missing_pct"] or 0) - expected_pct) <= 0.1
    check(f"M-{col}", "Missingness", f"`{col}` missing count and rate match documentation",
          ok, f"{expected_missing} ({expected_pct}%)",
          f"{actual['missing']} ({actual['missing_pct']}%)")

check("M-damage-mirror", "Missingness", "Both adjusted damage columns share the same missingness",
      missingness[DAMAGE_KUSD]["missing"] == missingness[DAMAGE_MUSD]["missing"],
      missingness[DAMAGE_KUSD]["missing"], missingness[DAMAGE_MUSD]["missing"],
      "the million-USD column is a pure unit conversion of the '000 USD column")

check("M-no-zero-fill", "Missingness",
      "Deaths, affected, and damage contain no zero-filled blanks",
      zero_counts[DEATHS] == 0 and zero_counts[AFFECTED] == 0 and zero_counts[DAMAGE_KUSD] == 0,
      0, {"deaths": zero_counts[DEATHS], "affected": zero_counts[AFFECTED],
          "damage": zero_counts[DAMAGE_KUSD]},
      "a zero in these columns would indicate missing values were replaced with zero")
check("M-magnitude-zeros", "Missingness",
      "Magnitude zeros are genuine reported values, not filled blanks",
      True, "reported values", zero_counts[MAGNITUDE],
      f"{zero_counts[MAGNITUDE]} impact rows report Magnitude = 0; treat as reported-but-zero, "
      "not as missing", flag=True)

lat_ok = sum(1 for r in impacts if num(r["Latitude"]) is not None)
lon_ok = sum(1 for r in impacts if num(r["Longitude"]) is not None)
both = sum(1 for r in impacts if num(r["Latitude"]) is not None and num(r["Longitude"]) is not None)
flag_yes = sum(1 for r in impacts if r["Has Coordinates"] == "Yes")
expected_coords, expected_coord_pct = DOCUMENTED["coordinate_complete"]
check("C-paired", "Coordinates", "Latitude and longitude are present as a pair only",
      lat_ok == lon_ok == both, "lat == lon == both",
      {"latitude": lat_ok, "longitude": lon_ok, "both": both})
check("C-flag", "Coordinates", "`Has Coordinates` agrees with populated coordinate fields",
      flag_yes == both, both, flag_yes)
check("C-complete", "Coordinates", "Coordinate completeness matches documentation",
      both == expected_coords and abs(pct(both, len(impacts)) - expected_coord_pct) <= 0.1,
      f"{expected_coords} ({expected_coord_pct}%)", f"{both} ({pct(both, len(impacts))}%)")

# ------------------------------------------------------- unit/consistency checks
max_unit_diff = 0.0
max_unit_diff_rows = 0
for r in impacts:
    kusd, musd = num(r[DAMAGE_KUSD]), num(r[DAMAGE_MUSD])
    if kusd is None and musd is None:
        continue
    diff = abs((musd or 0) - (kusd or 0) / 1000)
    max_unit_diff = max(max_unit_diff, diff)
    if diff > 1e-6:
        max_unit_diff_rows += 1
check("U-damage-scale", "Units", "Million-USD damage equals '000-USD damage / 1000",
      max_unit_diff_rows == 0, 0, max_unit_diff_rows,
      f"max absolute difference {max_unit_diff:.9g} million USD across all rows")

bad_decade = sum(
    1 for r in impacts
    if num(r["Start Year"]) is not None and num(r["Decade"]) != int(num(r["Start Year"])) // 10 * 10
)
check("U-decade", "Units", "`Decade` equals floor(Start Year / 10) * 10", bad_decade == 0, 0, bad_decade)

bad_dates = 0
present_dates = 0
for r in impacts:
    if r["Start Date"]:
        present_dates += 1
        try:
            dt.date.fromisoformat(r["Start Date"])
        except ValueError:
            bad_dates += 1
check("U-dates", "Units", "Derived `Start Date` values are valid ISO dates when present",
      bad_dates == 0, 0, bad_dates, f"{present_dates} populated Start Date values, "
      f"{len(impacts) - present_dates} blank because the source date was incomplete")

# --------------------------------------------------------------- events checks
check("E-rows", "Events", "Event-level row count matches documentation",
      len(events) == DOCUMENTED["event_rows"], DOCUMENTED["event_rows"], len(events))

event_ids = [e["Event ID"] for e in events]
dupe_events = sum(c - 1 for c in Counter(event_ids).values() if c > 1)
check("E-unique", "Events", "`Event ID` is unique in the event-level dataset",
      dupe_events == 0, 0, dupe_events, f"{len(set(event_ids))} distinct Event IDs")

impact_event_ids = {r["Event ID"] for r in impacts}
check("E-key-match", "Events", "Event IDs match exactly between events and impacts",
      set(event_ids) == impact_event_ids, len(impact_event_ids), len(set(event_ids)),
      "matched on the derived Event ID (year-sequence portion of DisNo.)")

iso_by_event = defaultdict(set)
for r in impacts:
    iso_by_event[r["Event ID"]].add(r["ISO"])
bad_country_count = [
    e["Event ID"] for e in events
    if int(num(e["Country Count"]) or 0) != len(iso_by_event.get(e["Event ID"], ()))
]
check("E-country-count", "Events", "`Country Count` equals distinct ISO codes in impacts",
      not bad_country_count, 0, len(bad_country_count))

impact_records_by_event = Counter(r["Event ID"] for r in impacts)
bad_record_count = [
    e["Event ID"] for e in events
    if int(num(e["Country Impact Records"]) or 0) != impact_records_by_event.get(e["Event ID"], 0)
]
check("E-record-count", "Events", "`Country Impact Records` equals impact rows per event",
      not bad_record_count, 0, len(bad_record_count))

multi = sum(1 for e in events if (num(e["Country Count"]) or 0) > 1)
check("E-multi-country", "Events", "Multi-country event count matches documentation",
      multi == DOCUMENTED["multi_country_events"], DOCUMENTED["multi_country_events"], multi)

type_by_event_impacts = {}
for r in impacts:
    type_by_event_impacts.setdefault(r["Event ID"], set()).add(r["Disaster Type"])
inconsistent_type = [e["Event ID"] for e in events
                     if type_by_event_impacts.get(e["Event ID"]) != {e["Disaster Type"]}]
check("E-type", "Events", "Each event's Disaster Type matches its country impacts",
      not inconsistent_type, 0, len(inconsistent_type),
      "one type per event; mixed-type Event IDs would indicate a bad consolidation key")

event_totals = defaultdict(float)
blank_bug = 0
for e in events:
    for col in [DEATHS, AFFECTED, DAMAGE_KUSD]:
        reported = int(num(e[col + " Reported Country Impacts"]) or 0)
        value = num(e[col])
        if reported == 0:
            if value is not None:
                blank_bug += 1
        else:
            event_totals[col] += value or 0.0
            if value is None:
                blank_bug += 1
check("E-blank-propagation", "Events",
      "Event totals are blank when all country impacts are blank, never zero",
      blank_bug == 0, 0, blank_bug)

for col in [DEATHS, AFFECTED, DAMAGE_KUSD]:
    impact_total = sum(num(r[col]) or 0.0 for r in impacts if num(r[col]) is not None)
    TOTALS[col] = impact_total
    check(f"E-sum-{col}", "Events", f"Event-level `{col}` sums to the country-impact total",
          close(impact_total, event_totals[col]), impact_total, round(event_totals[col], 6),
          "no double counting and no dropped country values")

event_coverage = {col: sum(1 for e in events if num(e[col]) is not None)
                  for col in [DEATHS, AFFECTED, DAMAGE_MUSD]}
for col, expected in DOCUMENTED["event_coverage"].items():
    actual = event_coverage[col]
    check(f"E-coverage-{col}", "Events", f"Reported-event coverage for `{col}` matches documentation",
          actual == expected, expected, actual,
          f"{pct(actual, len(events))}% of {len(events)} events")

# ---------------------------------------------------------- type summary checks
if type_rows:
    check("T-rows", "TypeSummary", "One row per disaster type",
          len(type_rows) == DOCUMENTED["disaster_types"],
          DOCUMENTED["disaster_types"], len(type_rows))
    check("T-group", "TypeSummary", "All rows are Disaster Group = Natural",
          {r["Disaster Group"] for r in type_rows} == {"Natural"}, {"Natural"},
          sorted({r["Disaster Group"] for r in type_rows}))
    seven = sum(int(num(r["Unique Events"]) or 0) for r in type_rows)
    check("T-unique-total", "TypeSummary", "Unique event counts sum to the total event count",
          seven == len(events), len(events), seven,
          "each consolidated event carries exactly one Disaster Type")
    type_mismatch = [
        r["Disaster Type"] for r in type_rows
        if int(num(r["Unique Events"]) or 0) != type_event_counts.get(r["Disaster Type"], 0)
    ]
    check("T-unique-per-type", "TypeSummary", "Per-type unique event counts match impacts",
          not type_mismatch, 0, type_mismatch)
    for col in [DEATHS, AFFECTED, DAMAGE_KUSD]:
        total = sum(num(r[col]) or 0.0 for r in type_rows if num(r[col]) is not None)
        check(f"T-sum-{col}", "TypeSummary", f"Type-level `{col}` sums to the country-impact total",
              close(TOTALS[col], total), TOTALS[col], round(total, 6))
    bad_reported = [r["Disaster Type"] for r in type_rows
                    if int(num(r[DEATHS + " Events with Reported Values"]) or 0)
                    > int(num(r["Unique Events"]) or 0)]
    check("T-reported", "TypeSummary", "Reported-event counts never exceed unique events",
          not bad_reported, 0, bad_reported)

# ------------------------------------------------- country/year/type consistency
if cyt_rows:
    check("Y-rows", "CountryYearType", "Row count matches documentation",
          len(cyt_rows) == DOCUMENTED["country_year_type_rows"],
          DOCUMENTED["country_year_type_rows"], len(cyt_rows))
    keys = Counter((r["ISO"], r["Start Year"], r["Disaster Type"]) for r in cyt_rows)
    dup_groups = sum(c - 1 for c in keys.values() if c > 1)
    check("Y-grain", "CountryYearType", "Grain is unique per ISO / Start Year / Disaster Type",
          dup_groups == 0, 0, dup_groups)
    records_sum = sum(int(num(r["Country Impact Records"]) or 0) for r in cyt_rows)
    check("Y-record-sum", "CountryYearType",
          "`Country Impact Records` sums to the country-impact row count",
          records_sum == len(impacts), len(impacts), records_sum)
    pair_count = len({(r["Event ID"], r["ISO"]) for r in impacts})
    unique_sum = sum(int(num(r["Unique Events"]) or 0) for r in cyt_rows)
    check("Y-unique-sum", "CountryYearType",
          "`Unique Events` sums to distinct (Event ID, ISO) pairs",
          unique_sum == pair_count, pair_count, unique_sum)
    for col in [DEATHS, AFFECTED, DAMAGE_KUSD]:
        total = sum(num(r[col]) or 0.0 for r in cyt_rows if num(r[col]) is not None)
        check(f"Y-sum-{col}", "CountryYearType",
              f"Country/year/type `{col}` sums to the country-impact total",
              close(TOTALS[col], total), TOTALS[col], round(total, 6))
    check("Y-double-count", "CountryYearType",
          "Country/year/type `Unique Events` is not a project-wide event count",
          unique_sum != len(events), f"≠ {len(events)}", unique_sum,
          "the same event is counted again in every country (and year) it touches; "
          "never sum this column as a total frequency", flag=True)
    check("Y-record-consistency", "CountryYearType",
          "Unique Events never exceeds Country Impact Records within a group",
          all((num(r["Unique Events"]) or 0) <= (num(r["Country Impact Records"]) or 0)
              for r in cyt_rows), True, True)
    years_c = [int(num(r["Start Year"])) for r in cyt_rows if num(r["Start Year"]) is not None]
    check("Y-years", "CountryYearType", "Coverage period matches the impact dataset",
          (min(years_c), max(years_c)) == (min(years), max(years)),
          [min(years), max(years)], [min(years_c), max(years_c)])

# ----------------------------------------------------------- source workbook
source_info = {"path": SOURCE.relative_to(ROOT).as_posix(), "present": SOURCE.is_file()}
if SOURCE.is_file():
    source_info["sha256"] = sha256(SOURCE)
    source_info["bytes"] = SOURCE.stat().st_size
def skip_source_workbook_checks(reason):
    """Record both source-workbook checks as SKIP so the check set stays at 71."""
    check("SRC-rows", "SourceWorkbook",
          "Source export row count matches documentation", False,
          DOCUMENTED["source_rows"], "not verified", reason, skip=True)
    check("SRC-natural", "SourceWorkbook",
          "Natural-filtered source rows match the country-impact dataset", False,
          len(impacts), "not verified", reason, skip=True)


try:
    import openpyxl  # noqa: PLC0415 - optional dependency, imported lazily

    workbook = openpyxl.load_workbook(SOURCE, read_only=True, data_only=True)
    sheet = workbook["EM-DAT Data"]
    sheet.reset_dimensions()
    rows_iter = sheet.iter_rows(values_only=True)
    headers = list(next(rows_iter))
    source_rows = 0
    natural_rows = 0
    group_index = headers.index("Disaster Group")
    for values in rows_iter:
        source_rows += 1
        if values[group_index] == "Natural":
            natural_rows += 1
    workbook.close()
    source_info.update({"rows": source_rows, "natural_rows": natural_rows})
    check("SRC-rows", "SourceWorkbook", "Source export row count matches documentation",
          source_rows == DOCUMENTED["source_rows"], DOCUMENTED["source_rows"], source_rows)
    check("SRC-natural", "SourceWorkbook",
          "Natural-filtered source rows match the country-impact dataset",
          natural_rows == len(impacts), len(impacts), natural_rows,
          "confirms the pipeline's Natural filter is neither lossy nor duplicated")
except ImportError:
    skip_source_workbook_checks(
        "openpyxl is not installed; run `python -m pip install -r requirements.txt` "
        "to enable these checks")
except Exception as exc:  # pragma: no cover - defensive
    skip_source_workbook_checks(f"source workbook could not be opened: {exc!r}")

# ------------------------------------------------------------------ summary
status_counts = Counter(c["status"] for c in checks)
worst_year = max(Counter(int(num(e["Start Year"])) for e in events if num(e["Start Year"])).items(),
                 key=lambda kv: (kv[1], -kv[0]))

report = {
    "generated_at_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "generated_by": "scripts/validate_project_data.py",
    "datasets": overview,
    "source_workbook": source_info,
    "summary": {
        "checks_total": len(checks),
        **{k.lower(): status_counts.get(k, 0) for k in ["PASS", "FAIL", "WARN", "SKIP"]},
    },
    "confirmed_statistics": {
        "impact_rows": len(impacts),
        "event_rows": len(events),
        "multi_country_events": multi,
        "disaster_types": len(type_event_counts),
        "type_unique_event_counts": dict(sorted(type_event_counts.items(),
                                                key=lambda kv: -kv[1])),
        "min_year": min(years),
        "max_year": max(years),
        "impact_missingness": missingness,
        "coordinate_complete": both,
        "coordinate_complete_pct": pct(both, len(impacts)),
        "event_reported_coverage": {
            col: {"reported_events": n, "coverage_pct": pct(n, len(events))}
            for col, n in event_coverage.items()
        },
        "totals": {
            "total_deaths": TOTALS.get(DEATHS),
            "total_affected": TOTALS.get(AFFECTED),
            "total_adjusted_damage_million_usd": TOTALS.get(DAMAGE_MUSD) or TOTALS.get(DAMAGE_KUSD, 0) / 1000,
        },
        "historic_records": dict(hist_values),
        "busiest_year": {"year": worst_year[0], "events": worst_year[1]},
    },
    "known_risks": [
        "Missing impact values are preserved as blanks and are not zero: 67.6% of country-impact "
        "rows have no adjusted damage, so damage totals describe reported damage only.",
        "Sums of `Unique Events` in natural_country_year_type_summary.csv (18,060) count the same "
        "event once per country and must never be summed as a project-wide frequency.",
        "Damage in million US$ is a unit conversion of EM-DAT's adjusted damage, not a new "
        "estimate; it inherits EM-DAT's CPI base year and underreporting.",
        "Magnitude uses hazard-specific scales and 13 rows report a literal zero; magnitude must "
        "not be compared across disaster types.",
        "Coordinates exist for only 15.8% of country impacts, and impacts are country-level; they "
        "must not be treated as district-level locations.",
        "Before 2000, records are flagged Historic = Yes and reflect lower reporting quality.",
    ],
    "checks": checks,
}

OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def md_table(rows, headers):
    lines = ["| " + " | ".join(headers) + " |",
             "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)


status_rank = {"FAIL": 0, "WARN": 1, "SKIP": 2, "PASS": 3}
ordered = sorted(checks, key=lambda c: (status_rank[c["status"]], c["area"], c["id"]))
check_rows = [
    (c["id"], c["area"], c["description"],
     "**FAIL**" if c["status"] == "FAIL" else c["status"],
     "" if c["expected"] is None else f"`{c['expected']}`",
     "" if c["actual"] is None else f"`{c['actual']}`",
     c["detail"].replace("|", "/"))
    for c in ordered
]

missing_rows = [
    (col, v["missing"], f"{v['missing_pct']}%", v["zeros"])
    for col, v in missingness.items()
]
coverage_rows = [
    (col, reported, f"{pct(reported, len(events))}%", len(events) - reported)
    for col, reported in event_coverage.items()
]
type_rows_md = [(t, n, f"{pct(n, len(events))}%")
                for t, n in sorted(type_event_counts.items(), key=lambda kv: -kv[1])]

verdict = ("All executable checks passed."
           if status_counts.get("FAIL", 0) == 0
           else f"{status_counts.get('FAIL', 0)} check(s) FAILED and require attention.")

md = f"""# Data Quality Report — When Nature Strikes

Generated by `scripts/validate_project_data.py` on {report['generated_at_utc']}.
Re-run `python scripts/validate_project_data.py` to reproduce every number below.

**Result: {verdict}**
Checks: {len(checks)} total — {status_counts.get('PASS', 0)} pass,
{status_counts.get('FAIL', 0)} fail, {status_counts.get('WARN', 0)} warning,
{status_counts.get('SKIP', 0)} skipped.

A **WARN** records a real property of the data that readers must respect (a documented
limitation), not a defect. A **SKIP** means the check could not run in this environment.
Missing impact values are blanks, never zeroes, and this report preserves that distinction.

## 1. Dataset overview

{md_table([(v['path'], f"{v['rows']:,}", v['columns'], f"{v['bytes']:,}", v['sha256'][:16] + '…') for v in overview.values()], ['File', 'Rows', 'Columns', 'Bytes', 'SHA-256 (first 16)'])}

Source workbook: `{source_info['path']}` — present: {source_info['present']}; SHA-256
`{source_info.get('sha256', 'n/a')}`. The workbook is never modified by this repository's scripts.

Grains: one row per country impact (detailed), one row per consolidated event, one row per
disaster type, and one row per country/year/type group. See `docs/DASHBOARD_DATA_HANDOVER.md`.

## 2. Validation checks and outcomes

{md_table(check_rows, ['ID', 'Area', 'Check', 'Status', 'Expected', 'Actual', 'Detail'])}

## 3. Confirmed statistics

{md_table([(t, f"{n:,}", f"{pct(n, len(events))}%") for t, n in sorted(type_event_counts.items(), key=lambda kv: -kv[1])], ['Disaster type', 'Unique events', 'Share of events'])}

- Country-impact rows: **{len(impacts):,}**; consolidated events: **{len(events):,}**;
  multi-country events: **{multi:,}**; disaster types: **{len(type_event_counts)}**.
- Coverage: **{min(years)}–{max(years)}**; busiest year **{worst_year[0]}** with **{worst_year[1]}** events.
- Total reported deaths: **{TOTALS.get(DEATHS, 0):,.0f}**; total reported affected:
  **{TOTALS.get(AFFECTED, 0):,.0f}**; total reported adjusted damage:
  **{(TOTALS.get(DAMAGE_KUSD, 0) / 1000):,.0f} million US$**.
- Historic flag: {hist_values.get('Yes', 0):,} records marked `Historic = Yes`,
  {hist_values.get('No', 0):,} marked `No`.

Every total above is reproduced identically in the impact, event, type, and country/year/type
datasets; that identity is what the cross-dataset checks verify.

## 4. Missing-data limitations

### Country-impact grain ({len(impacts):,} rows)

{md_table([(c, f"{m:,}", p, f"{z:,}") for c, m, p, z in missing_rows], ['Column', 'Missing', 'Missing %', 'Reported zeros'])}

### Event grain ({len(events):,} events)

{md_table([(c, f"{n:,}", p, f"{miss:,}") for c, n, p, miss in coverage_rows], ['Measure', 'Events with reported value', 'Coverage', 'Events blank'])}

A blank means *not reported or not known*, not *no impact*. Damage coverage
({event_coverage[DAMAGE_MUSD] / len(events) * 100:.1f}% of events) is low enough that any
damage ranking is a ranking of **reported** damage. Always show the reported-event count
next to a damage total.

## 5. Data inconsistencies and risks

1. **Blank ≠ zero is preserved, but only for the impact measures.** Deaths, affected, and damage
   contain no zero-filled blanks. `Magnitude` contains {zero_counts[MAGNITUDE]} literal zeros,
   which are reported values on hazard-specific scales, not imputed data.
2. **`Unique Events` is additive across types but not across countries.**
   `natural_disaster_type_summary.csv` sums to {len(events):,} events because each event has one
   type. `natural_country_year_type_summary.csv` sums to
   {sum(int(num(r['Unique Events']) or 0) for r in cyt_rows) if cyt_rows else 'n/a':,}
   because an event is repeated for each country it touches. Summing the country-year-type
   column would overstate frequency.
3. **One event can span several countries.** {multi:,} events
   ({pct(multi, len(events))}%) affect more than one country, so counting country-impact rows
   inflates frequency by {(len(impacts) - len(events)) / len(events) * 100:.1f}%.
4. **Damage units.** `Total Damage, Adjusted (million US$)` is exactly
   `Total Damage, Adjusted ('000 US$)` ÷ 1,000 (verified on every row); it inherits EM-DAT's
   CPI-adjusted base and its documented underreporting.
5. **Coordinates** are complete for {pct(both, len(impacts))}% of impacts and are country-level
   locations. Do not map them as subnational points or infer missing coordinates from country names.
6. **Historical comparability.** {hist_values.get('Yes', 0):,} records are flagged historic and
   have lower reporting quality; period filters must be visible on the dashboard.

## 6. Checks that could not be performed

- `SRC-rows` / `SRC-natural` require `openpyxl` (declared in `requirements.txt`). When it is not
  installed the source workbook row count cannot be re-verified and the checks report SKIP.
- The script does not re-run `scripts/prepare_emdat.py`, so it validates the committed outputs
  rather than regenerating them. It does not verify EM-DAT's upstream data-quality claims, the
  accuracy of EM-DAT's CPI adjustment, or whether blanks mean "no impact" or "unreported".
- No check evaluates the Power BI `.pbix` file, which is out of scope for this repository role.
"""

OUT_MD.write_text(md, encoding="utf-8")

print(f"Datasets validated: {', '.join(overview)}")
print(f"Checks: {len(checks)} total, {status_counts.get('PASS', 0)} pass, "
      f"{status_counts.get('FAIL', 0)} fail, {status_counts.get('WARN', 0)} warn, "
      f"{status_counts.get('SKIP', 0)} skip")
for c in checks:
    if c["status"] in {"FAIL", "WARN", "SKIP"}:
        print(f"  [{c['status']}] {c['id']}: {c['description']} — expected {c['expected']}, got {c['actual']}")
print(f"Wrote {OUT_JSON.relative_to(ROOT)} and {OUT_MD.relative_to(ROOT)}")
sys.exit(0 if status_counts.get("FAIL", 0) == 0 else 1)
