"""Separate local event embeddings from public, coarsened projection cells."""

import numpy as np
import pandas as pd

from .metrics import OUT, TYPE

DEST = OUT / "dimensionality_reduction"
METHODS = ("PCA", "t-SNE", "UMAP")


def bins(points, dimensions, divisions, minimum=5):
    """Summarize fixed-width cells. Small cells are suppressed without merging."""
    cuts = [np.linspace(points[key].min() - 1e-7, points[key].max() + 1e-7, divisions + 1)
            for key in dimensions]
    labels = [(edge[1:] + edge[:-1]) / 2 for edge in cuts]
    groups = pd.DataFrame({f"axis{i+1}": labels[i][np.searchsorted(edge[1:-1], points[key])]
                           for i, (key, edge) in enumerate(zip(dimensions, cuts))}, index=points.index)
    groups["hazard"] = points[TYPE].where(points[TYPE].isin(points[TYPE].value_counts().head(5).index), "Other")
    groups["cluster"] = points["cluster"].astype(str)
    result = []
    for field in ("hazard", "cluster"):
        cols = [key for key in groups if key.startswith("axis")] + [field]
        counts = groups.groupby(cols, observed=True).size().rename("events").reset_index()
        result.append(counts[counts.events.ge(minimum)].rename(columns={field: "group"}).assign(grouping=field))
    return pd.concat(result, ignore_index=True)


def publish(full):
    DEST.mkdir(parents=True, exist_ok=True)
    tables = []
    for method in METHODS:
        layers = [2, 3] if method == "PCA" else [2]
        for dimension in layers:
            dimensions = [f"{method} {i+1}" for i in range(dimension)]
            tables.append(bins(full, dimensions, 13 if dimension == 2 else 7)
                          .assign(method=method, dimensions=dimension))
    pd.concat(tables, ignore_index=True).to_csv(DEST / "projection_cells.csv", index=False)
    count = full.groupby("cluster").size().rename("events")
    flagged = full.groupby("cluster")["anomaly_flag"].sum().rename("flagged")
    samples = full.loc[full.anomaly_flag]
    score = samples.groupby("cluster").anomaly_score.agg(["min", "median", "max"])
    count.to_frame().join(flagged).join(score.where(flagged.ge(5), axis=0)).to_csv(DEST / "anomaly_summary.csv")
