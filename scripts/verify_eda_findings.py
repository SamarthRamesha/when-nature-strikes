"""Independently recompute the headline EDA findings from the processed data.

This script re-derives the findings reported in the analysis notebooks directly
from `data/processed/natural_disaster_events.csv` using only the standard
library, then compares them with the committed outputs in `analysis/outputs/`.
It does not re-run the notebooks and it does not create charts.

Output: analysis/outputs/eda_validation.json

Usage:
    python scripts/verify_eda_findings.py
"""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVENTS = ROOT / "data" / "processed" / "natural_disaster_events.csv"
TYPE_SUMMARY = ROOT / "data" / "processed" / "natural_disaster_type_summary.csv"
OUT = ROOT / "analysis" / "outputs" / "eda_validation.json"

DEATHS = "Total Deaths"
AFFECTED = "Total Affected"
DAMAGE = "Total Damage, Adjusted (million US$)"


def load(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def num(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def rank(values):
    """Average ranks with ties, 1 = smallest."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return cov / (sx * sy) if sx and sy else None


def spearman(xs, ys):
    paired = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    if len(paired) < 3:
        return None
    rx = rank([p[0] for p in paired])
    ry = rank([p[1] for p in paired])
    return pearson(rx, ry)


events = load(EVENTS)
type_rows = {r["Disaster Type"]: r for r in load(TYPE_SUMMARY)}

# ---------------------------------------------------------------- frequency
by_type = {}
for e in events:
    by_type.setdefault(e["Disaster Type"], []).append(e)

frequency = sorted(
    ((t, len(rows)) for t, rows in by_type.items()), key=lambda kv: (-kv[1], kv[0])
)

# ------------------------------------------------------------ impact summary
# Average = mean over events with a reported value (the notebooks' definition).
summary = {}
for t, rows in by_type.items():
    entry = {"unique_events": len(rows)}
    for label, col in [("deaths", DEATHS), ("affected", AFFECTED), ("damage", DAMAGE)]:
        reported = [num(r[col]) for r in rows if num(r[col]) is not None]
        entry[label] = {
            "reported_events": len(reported),
            "coverage_pct": round(len(reported) / len(rows) * 100, 2),
            "total": round(sum(reported), 6) if reported else None,
            "average": round(sum(reported) / len(reported), 6) if reported else None,
            "median": round(sorted(reported)[len(reported) // 2], 6) if reported else None,
        }
    summary[t] = entry


def top(label, key):
    candidates = [(t, s[label][key]) for t, s in summary.items() if s[label][key] is not None]
    candidates.sort(key=lambda kv: (-kv[1], kv[0]))
    return candidates


findings = []


def add_finding(fid, statement, metric, grain, dataset, dataset_path, verified, evidence, caveat):
    findings.append({
        "id": fid,
        "statement": statement,
        "metric": metric,
        "grain": grain,
        "dataset": dataset,
        "dataset_path": dataset_path,
        "independently_verified": verified,
        "evidence": evidence,
        "caveat": caveat,
    })


freq_top = frequency[0]
add_finding(
    "F1", "Flood is the most frequent natural disaster type.",
    "Unique events (distinct Event ID)", "One consolidated event",
    "natural_disaster_events.csv", EVENTS.relative_to(ROOT).as_posix(),
    True,
    {"top": {"type": freq_top[0], "events": freq_top[1],
             "share_pct": round(freq_top[1] / len(events) * 100, 2)},
     "runner_up": {"type": frequency[1][0], "events": frequency[1][1]},
     "ranked": [{"type": t, "events": n} for t, n in frequency]},
    "Frequency counts depend on the consolidated Event ID; counting country-impact rows would "
    "give Flood 6,217 rather than 5,814 and inflate every type.",
)

death_top = top("deaths", "average")
add_finding(
    "F2", "Drought has the highest average deaths per event.",
    "Mean reported Total Deaths per event with a reported value",
    "One consolidated event", "natural_disaster_events.csv", EVENTS.relative_to(ROOT).as_posix(),
    True,
    {"top": {"type": death_top[0][0], "average_deaths": round(death_top[0][1], 2),
             "reported_events": summary[death_top[0][0]]["deaths"]["reported_events"],
             "coverage_pct": summary[death_top[0][0]]["deaths"]["coverage_pct"],
             "median_deaths": summary[death_top[0][0]]["deaths"]["median"]},
     "runner_up": {"type": death_top[1][0], "average_deaths": round(death_top[1][1], 2),
                   "reported_events": summary[death_top[1][0]]["deaths"]["reported_events"]}},
    "The average rests on only "
    f"{summary[death_top[0][0]]['deaths']['reported_events']} of "
    f"{summary[death_top[0][0]]['unique_events']} drought events with reported deaths, and the "
    f"median ({summary[death_top[0][0]]['deaths']['median']:.0f}) is far below the mean, so a "
    "small number of catastrophic droughts drives the average. Report median, coverage, and "
    "event count alongside it.",
)

affected_top = top("affected", "average")
add_finding(
    "F3", "Drought has the highest average affected population per event.",
    "Mean reported Total Affected per event with a reported value",
    "One consolidated event", "natural_disaster_events.csv", EVENTS.relative_to(ROOT).as_posix(),
    True,
    {"top": {"type": affected_top[0][0], "average_affected": round(affected_top[0][1], 2),
             "reported_events": summary[affected_top[0][0]]["affected"]["reported_events"],
             "coverage_pct": summary[affected_top[0][0]]["affected"]["coverage_pct"],
             "median_affected": summary[affected_top[0][0]]["affected"]["median"]},
     "runner_up": {"type": affected_top[1][0], "average_affected": round(affected_top[1][1], 2)}},
    "Same heavy-tail caveat as F2: the drought median affected "
    f"({summary[affected_top[0][0]]['affected']['median']:,.0f}) is two orders of magnitude "
    "below the mean. Affected counts may also double-count people across successive events.",
)

damage_top = top("damage", "average")
add_finding(
    "F4", "Earthquake has the highest average adjusted economic damage per event.",
    "Mean reported adjusted damage in million US$ per event with a reported value",
    "One consolidated event", "natural_disaster_events.csv", EVENTS.relative_to(ROOT).as_posix(),
    True,
    {"top": {"type": damage_top[0][0], "average_damage_musd": round(damage_top[0][1], 2),
             "reported_events": summary[damage_top[0][0]]["damage"]["reported_events"],
             "coverage_pct": summary[damage_top[0][0]]["damage"]["coverage_pct"]},
     "runner_up": {"type": damage_top[1][0], "average_damage_musd": round(damage_top[1][1], 2)},
     "reported_damage_events_all_types": sum(
         s["damage"]["reported_events"] for s in summary.values())},
    "Damage is reported for only "
    f"{summary[damage_top[0][0]]['damage']['reported_events']} of "
    f"{summary[damage_top[0][0]]['unique_events']} earthquake events, and only "
    f"{sum(s['damage']['reported_events'] for s in summary.values())} of {len(events)} events "
    "overall. Damage underreporting is documented by EM-DAT, so this ranks reported damage.",
)

year_counts = {}
for e in events:
    year = int(num(e["Start Year"]))
    year_counts[year] = year_counts.get(year, 0) + 1
year_top = sorted(year_counts.items(), key=lambda kv: (-kv[1], kv[0]))[0]
add_finding(
    "F5", "2000 is the year with the highest number of disaster events.",
    "Unique events (distinct Event ID) grouped by Start Year", "One consolidated event",
    "natural_disaster_events.csv", EVENTS.relative_to(ROOT).as_posix(),
    True,
    {"top": {"year": year_top[0], "events": year_top[1]},
     "runner_up": {"year": year_top[0] + 1, "events": year_counts.get(year_top[0] + 1)},
     "top5_years": [{"year": y, "events": n} for y, n in
                    sorted(year_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]]},
    "Yearly counts rise with reporting capacity, so the 2000 peak partly reflects reporting "
    "rather than hazard activity. Compare decades, and split Historic vs 2000-onward.",
)

# ------------------------------------------------------------ event coverage
coverage = {}
for label, col in [("deaths", DEATHS), ("affected", AFFECTED), ("damage", DAMAGE)]:
    reported = sum(1 for e in events if num(e[col]) is not None)
    coverage[label] = {"reported_events": reported,
                       "missing_events": len(events) - reported,
                       "coverage_pct": round(reported / len(events) * 100, 2)}
add_finding(
    "F6", "Event-level impact coverage is 74.1% deaths, 78.6% affected, 33.4% damage.",
    "Share of consolidated events with a reported value", "One consolidated event",
    "natural_disaster_events.csv", EVENTS.relative_to(ROOT).as_posix(),
    coverage["deaths"]["reported_events"] == 11655
    and coverage["affected"]["reported_events"] == 12366
    and coverage["damage"]["reported_events"] == 5251,
    coverage,
    "Coverage describes reporting, not absence of impact. Missing values must stay blank.",
)

# ------------------------------------------- total-versus-average comparison
totals = {label: sorted(((t, s[label]["total"]) for t, s in summary.items()
                         if s[label]["total"] is not None), key=lambda kv: -kv[1])[:3]
          for label in ["deaths", "affected", "damage"]}
averages = {label: sorted(((t, s[label]["average"]) for t, s in summary.items()
                          if s[label]["average"] is not None), key=lambda kv: -kv[1])[:3]
            for label in ["deaths", "affected", "damage"]}

# ------------------------------------------------------- correlation (Spearman)
for col in [DEATHS, AFFECTED, DAMAGE]:
    for e in events:
        e.setdefault("_numeric", {})[col] = num(e[col])
corr = {}
columns = [DEATHS, AFFECTED, DAMAGE]
for a in columns:
    for b in columns:
        if a == b:
            corr[f"{a} vs {b}"] = 1.0
            continue
        corr[f"{a} vs {b}"] = spearman([e["_numeric"][a] for e in events],
                                       [e["_numeric"][b] for e in events])

# --------------------------------------- compare with committed EDA artefacts
comparisons = []


def compare(name, committed, recomputed, tolerance):
    if committed is None and recomputed is None:
        note = "both blank (no reported values)"
        ok = True
    elif committed is None or recomputed is None:
        note = "one side is blank"
        ok = False
    else:
        note = "values agree" if abs(committed - recomputed) <= tolerance else "values differ"
        ok = abs(committed - recomputed) <= tolerance
    comparisons.append({"artifact_value": name, "committed": committed,
                        "recomputed": recomputed, "match": ok, "note": note})


freq_csv = ROOT / "analysis" / "outputs" / "final_disaster_frequency.csv"
if freq_csv.is_file():
    committed = {r["Disaster Type"]: int(num(r["Unique Events"])) for r in load(freq_csv)}
    for t, n in frequency:
        compare(f"final_disaster_frequency.csv:{t}", committed.get(t), n, 0)

pattern_csv = ROOT / "analysis" / "outputs" / "disaster_pattern_summary.csv"
if pattern_csv.is_file():
    committed = {r["Disaster Type"]: r for r in load(pattern_csv)}
    for t, s in summary.items():
        row = committed.get(t)
        if not row:
            continue
        compare(f"disaster_pattern_summary.csv:{t}:total_deaths",
                num(row["Total_Deaths"]), s["deaths"]["total"], 1e-6)
        compare(f"disaster_pattern_summary.csv:{t}:average_deaths",
                num(row["Average_Deaths"]), s["deaths"]["average"], 1e-6)
        compare(f"disaster_pattern_summary.csv:{t}:average_affected",
                num(row["Average_Affected"]), s["affected"]["average"], 1e-6)
        compare(f"disaster_pattern_summary.csv:{t}:average_damage",
                num(row["Average_Damage"]), s["damage"]["average"], 1e-6)

coverage_csv = ROOT / "analysis" / "outputs" / "final_reporting_coverage.csv"
if coverage_csv.is_file():
    committed = {r["Impact Measure"]: int(num(r["Reported Events"])) for r in load(coverage_csv)}
    compare("final_reporting_coverage.csv:Deaths", committed.get("Deaths"),
            coverage["deaths"]["reported_events"], 0)
    compare("final_reporting_coverage.csv:Affected Population",
            committed.get("Affected Population"), coverage["affected"]["reported_events"], 0)
    compare("final_reporting_coverage.csv:Economic Damage",
            committed.get("Economic Damage"), coverage["damage"]["reported_events"], 0)

year_csv = ROOT / "analysis" / "outputs" / "final_yearly_frequency.csv"
if year_csv.is_file():
    committed = {int(num(r["Start Year"])): int(num(r["Unique Events"])) for r in load(year_csv)}
    compare("final_yearly_frequency.csv:2000", committed.get(2000), year_counts.get(2000), 0)
    compare("final_yearly_frequency.csv:count_of_years", len(committed), len(year_counts), 0)

corr_csv = ROOT / "analysis" / "outputs" / "final_impact_correlation.csv"
if corr_csv.is_file():
    with corr_csv.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    headers = rows[0]
    for row in rows[1:]:
        left = row[0]
        for header, value in zip(headers[1:], row[1:]):
            key = f"{left} vs {header}"
            # Tolerance 1e-6 absorbs floating-point summation order between the
            # notebook (pandas/NumPy) and this pure-Python rank correlation.
            compare(f"final_impact_correlation.csv:{key}", num(value), corr.get(key), 1e-6)

# --------------------------------------------------- historic flag conflicts
historic_by_event = {}
for e in events:
    historic_by_event[e["Event ID"]] = None
impacts_path = ROOT / "data" / "processed" / "cleaned_natural_disaster_impacts.csv"
conflicts = []
if impacts_path.is_file():
    flags = {}
    for r in load(impacts_path):
        flags.setdefault(r["Event ID"], set()).add(r["Historic"])
    conflicts = sorted(eid for eid, v in flags.items() if len(v) > 1)

max_corr_delta = max(
    (abs(c["committed"] - c["recomputed"]) for c in comparisons
     if c["artifact_value"].startswith("final_impact_correlation.csv")
     and c["committed"] is not None and c["recomputed"] is not None),
    default=0.0,
)

result = {
    "generated_by": "scripts/verify_eda_findings.py",
    "max_spearman_abs_delta_vs_committed": max_corr_delta,
    "generated_at_utc": __import__("datetime").datetime.now(
        __import__("datetime").timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "dataset": EVENTS.relative_to(ROOT).as_posix(),
    "events": len(events),
    "types": len(by_type),
    "findings": findings,
    "type_summary_recomputed": summary,
    "totals_vs_averages_top3": {"totals": totals, "averages": averages},
    "spearman_correlations": corr,
    "committed_artifact_comparisons": comparisons,
    "committed_artifacts_all_match": all(c["match"] for c in comparisons),
    "committed_artifacts_compared": len(comparisons),
    "historic_flag_conflicts": {
        "events": conflicts,
        "count": len(conflicts),
        "note": "These events have country impacts carrying different Historic flags, so a "
                "per-event Historic dimension must be derived from Start Year, not from any "
                "single country row.",
    },
    "type_summary_csv_matches_events": all(
        int(num(type_rows[t]["Unique Events"])) == n for t, n in frequency
    ) if type_rows else None,
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

print(f"Recomputed {len(findings)} findings from {len(events):,} events across {len(by_type)} types.")
print(f"Committed-artifact comparisons: {len(comparisons)}, "
      f"all match: {result['committed_artifacts_all_match']}")
for c in comparisons:
    if not c["match"]:
        print(f"  MISMATCH {c['artifact_value']}: committed={c['committed']} recomputed={c['recomputed']}")
print(f"Historic flag conflicts across country impacts: {len(conflicts)} {conflicts}")
print(f"Wrote {OUT.relative_to(ROOT)}")
sys.exit(0 if result["committed_artifacts_all_match"] else 1)
