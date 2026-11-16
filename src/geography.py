"""Resolve country polygons by ISO without assigning locations to unmatched records."""
import json

import pandas as pd

from .metrics import ID, ROOT


def boundaries():
    raw = json.loads((ROOT / "dashboard" / "world.geojson").read_text())
    features = []
    for item in raw["features"]:
        props = item["properties"]
        iso = props["ISO_A3_EH"]
        if iso != "-99":
            features.append({"type": "Feature", "id": iso, "properties": {},
                             "geometry": item["geometry"]})
    return {"type": "FeatureCollection", "features": features}


def map_coverage(impacts, world):
    ids = {feature["id"] for feature in world["features"]}
    matched = impacts["ISO"].isin(ids)
    excluded = (impacts.loc[~matched].groupby(["ISO", "Country"], dropna=False)[ID]
                .size().rename("records").reset_index())
    return int(matched.sum()), excluded


def static_map():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    from matplotlib.colors import LogNorm

    from .metrics import OUT, load_data
    from .statistics import save

    _, impacts = load_data()
    world = boundaries()
    covered, excluded = map_coverage(impacts, world)
    counts = impacts.groupby("ISO")[ID].nunique()
    fig, ax = plt.subplots(figsize=(12, 6), layout="constrained")
    cmap, norm = plt.get_cmap("YlGnBu"), LogNorm(vmin=1, vmax=counts.max())
    parts, colors = [], []
    for country in world["features"]:
        if country["id"] == "ATA":
            continue
        geometry = country["geometry"]
        polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
        value = counts.get(country["id"])
        for polygon in polygons:
            parts.append(polygon[0])
            colors.append(cmap(norm(value)) if pd.notna(value) else "#ecf0f3")
    ax.add_collection(PolyCollection(parts, facecolor=colors, edgecolor="#707f8d", linewidth=.2))
    ax.set(xlim=(-180, 180), ylim=(-59, 84), aspect="equal")
    ax.axis("off")
    ax.set_title("Recorded disaster events by affected country", loc="left", fontsize=16)
    fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, shrink=.65,
                 label="Distinct events within country (log scale)")
    fig.supxlabel(f"EM-DAT, 1900–2026 (partial). {covered:,}/{len(impacts):,} country-impact rows map by ISO. Boundaries: Natural Earth.", fontsize=9)
    save(fig, "geography")
    excluded.to_csv(OUT / "map_unmatched.csv", index=False)
    (OUT / "map_summary.json").write_text(json.dumps({"matched_records": covered, "total_records": len(impacts),
        "matched_country_codes": len(set(counts.index) - set(excluded.ISO)),
        "unmatched_country_codes": len(excluded), "top": counts.nlargest(6).to_dict()}, indent=2) + "\n")


if __name__ == "__main__":
    static_map()
