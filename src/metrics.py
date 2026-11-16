"""Shared unit, reporting, and event-grain definitions."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
PROCESSED = ROOT / "data" / "processed"
ID = "Event ID"
TYPE = "Disaster Type"
YEAR = "Start Year"
DEATHS = "Total Deaths"
AFFECTED = "Total Affected"
DAMAGE = "Total Damage, Adjusted (million US$)"
METRICS = {DEATHS: "people", AFFECTED: "people", DAMAGE: "million adjusted USD"}
SHORT = {DEATHS: "Deaths", AFFECTED: "Affected", DAMAGE: "Adjusted damage"}


def load_data():
    events = pd.read_csv(PROCESSED / "natural_disaster_events.csv")
    impacts = pd.read_csv(PROCESSED / "cleaned_natural_disaster_impacts.csv",
                          usecols=[ID, TYPE, YEAR, "ISO", "Country", "Region", "Start Month", *METRICS])
    if events[ID].isna().any() or not events[ID].is_unique:
        raise ValueError("The event table must have exactly one row per Event ID.")
    return events, impacts


def filtered_events(impacts, events):
    """Sum selected country contributions and retain the canonical event year."""
    totals = impacts.groupby(ID)[list(METRICS)].sum(min_count=1).reset_index()
    return events[[ID, TYPE, YEAR]].merge(totals, on=ID, validate="one_to_one")


def summarize(frame, by):
    """Summarize each metric with coverage at the supplied grain."""
    groups = frame.groupby(by, observed=True, dropna=False)
    records = []
    for key, group in groups:
        key = key if isinstance(key, tuple) else (key,)
        common = dict(zip([by] if isinstance(by, str) else by, key))
        for metric, unit in METRICS.items():
            values = group[metric].dropna()
            quantiles = values.quantile([.25, .5, .75, .90, .99])
            cap = quantiles[.99]
            total = values.sum(min_count=1)
            records.append({
                **common, "metric": metric, "unit": unit, "events": group[ID].nunique(),
                "records": len(group), "reported": len(values), "coverage": len(values) / len(group),
                "total": total, "mean": values.mean(), "median": quantiles[.5],
                "sd": values.std(), "q25": quantiles[.25], "q75": quantiles[.75],
                "iqr": quantiles[.75] - quantiles[.25], "q90": quantiles[.9], "q99": cap,
                "winsor_mean": values.clip(upper=cap).mean(),
                "largest_share": values.max() / total if pd.notna(total) and total else None,
            })
    return pd.DataFrame.from_records(records,
        columns=([by] if isinstance(by, str) else by) + [
            "metric", "unit", "events", "records", "reported", "coverage", "total",
            "mean", "median", "sd", "q25", "q75", "iqr", "q90", "q99",
            "winsor_mean", "largest_share",
        ])
