"""Descriptive tables and sensitivity tests at explicit analysis grains."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from .metrics import ID, TYPE, YEAR, METRICS, SHORT, OUT, load_data, summarize

SEED = 661
WINDOWS = ("1900–2026", "2000–2025")
METHODS = {"Pearson": stats.pearsonr, "Spearman": stats.spearmanr, "Kendall": stats.kendalltau}
ESTIMANDS = ("total", "mean", "median", "winsor_mean")
INK, TEAL, RUST = "#182942", "#087f80", "#ad4829"


def holm(p_values):
    values = np.asarray(p_values)
    order = np.argsort(values)
    adjusted = np.empty(len(values))
    adjusted[order] = np.minimum(1, np.maximum.accumulate(values[order] * np.arange(len(values), 0, -1)))
    return adjusted


def spearman_permutation_p(x, y, rho, rng, draws=9999):
    """Approximate a two-sided exchangeable-hazard null, using average ranks for ties."""
    x_rank, y_rank = stats.rankdata(x), stats.rankdata(y)
    x_rank -= x_rank.mean()
    y_rank -= y_rank.mean()
    permutations = rng.random((draws, len(y_rank))).argsort(axis=1)
    null = (y_rank[permutations] @ x_rank) / (np.linalg.norm(x_rank) * np.linalg.norm(y_rank))
    return (1 + np.count_nonzero(abs(null) >= abs(rho) - 1e-12)) / (draws + 1)


def correlation_table(summary, rng, draws=2000):
    rows = []
    for metric, table in summary.groupby("metric", sort=False):
        for estimand in ESTIMANDS:
            paired = table.dropna(subset=[estimand])
            x, y = paired["events"].to_numpy(), paired[estimand].to_numpy()
            if len(x) < 3 or np.unique(x).size < 2 or np.unique(y).size < 2:
                continue
            indexes = rng.integers(0, len(x), size=(draws, len(x)))
            for name, test in METHODS.items():
                result = test(x, y)
                samples = [test(x[i], y[i]).statistic for i in indexes
                           if np.unique(x[i]).size > 1 and np.unique(y[i]).size > 1] if name == "Spearman" else []
                lo, hi = np.quantile(samples, [.025, .975]) if samples else (None, None)
                p = (spearman_permutation_p(x, y, result.statistic, rng)
                     if name == "Spearman" else result.pvalue)
                rows.append(dict(metric=metric, statistic=estimand, method=name, types=len(x),
                                 coefficient=result.statistic, p_raw=p, ci_low=lo, ci_high=hi))
    result = pd.DataFrame(rows)
    result["p_holm"] = None
    primary_family = result["method"].eq("Spearman") & result["statistic"].ne("winsor_mean")
    result.loc[primary_family, "p_holm"] = holm(result.loc[primary_family, "p_raw"])
    return result


def distribution_tests(events):
    rows = []
    for metric in METRICS:
        samples = [g[metric].dropna().to_numpy() for _, g in events.groupby(TYPE)]
        samples = [sample for sample in samples if len(sample) >= 20]
        result = stats.kruskal(*samples)
        n = sum(map(len, samples))
        k = len(samples)
        rows.append(dict(metric=metric, types=k, reported_events=n, h=result.statistic,
                         p_raw=result.pvalue, epsilon_sq=max(0, (result.statistic-k+1)/(n-k))))
    frame = pd.DataFrame(rows)
    frame["p_holm"] = holm(frame["p_raw"])
    return frame


def save(fig, name):
    fig.text(.99, -.035, "EM-DAT data, 2026 · www.emdat.be", ha="right", fontsize=8, color=INK)
    fig.savefig(OUT / "figures" / f"{name}.png", dpi=165, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)


def figures(events, summary, correlations):
    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False,
                         "axes.spines.right": False, "text.color": INK, "axes.labelcolor": INK})
    fig, axes = plt.subplots(3, 3, figsize=(13, 10), layout="constrained")
    for row, metric in enumerate(METRICS):
        table = summary[summary.metric.eq(metric)]
        for col, stat in enumerate(("total", "mean", "median")):
            ax = axes[row, col]
            eligible = table.dropna(subset=[stat])
            ax.scatter(eligible.events, eligible[stat], s=25 + 85*eligible.coverage, color=TEAL, alpha=.6)
            leader = eligible.loc[eligible[stat].idxmax()]
            frequent = eligible.loc[eligible.events.idxmax()]
            for label, point in {point[TYPE]: point for point in (leader, frequent)}.items():
                at_left = point.events < 3
                ax.annotate(label, (point.events, point[stat]),
                            xytext=(4 if at_left else -3, -13), textcoords="offset points",
                            ha="left" if at_left else "right", fontsize=8)
            ax.set(xscale="log", yscale="symlog", title=f"{SHORT[metric]} · {stat}",
                   xlabel="Recorded events" if row == 2 else "", ylabel=METRICS[metric],
                   ylim=(-.03, 1.8 * eligible[stat].max()))
    fig.suptitle("Frequency and reported impact, 1900–2026", fontsize=17, x=.01, ha="left")
    fig.supxlabel("One point per hazard type. Point size scales with reporting coverage. EM-DAT, 2026 partial.", fontsize=9)
    save(fig, "frequency_vs_impact")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4), layout="constrained")
    annual = summarize(events, YEAR)
    counts = annual.drop_duplicates(YEAR).sort_values(YEAR)
    axes[0].plot(counts[YEAR].iloc[:-1], counts.events.iloc[:-1], color=TEAL)
    axes[0].scatter(counts[YEAR].iloc[-1], counts.events.iloc[-1], facecolors="none", edgecolors=RUST)
    axes[0].set(title="Annual recorded frequency", xlabel="Start year", ylabel="Distinct events")
    for metric, table in annual.groupby("metric", sort=False):
        axes[1].plot(table[YEAR], table.coverage.rolling(5, min_periods=1).mean(), label=SHORT[metric])
    axes[1].set(title="Mean annual reporting coverage (5-year window)", xlabel="Start year",
                ylabel="Share of events", ylim=(0, 1))
    axes[1].legend(frameon=False)
    fig.supxlabel("Source: EM-DAT. Open marker denotes partial 2026. Historical reporting differs.", fontsize=9)
    save(fig, "annual_trends")

    table = correlations[(correlations.method == "Spearman") & correlations.statistic.ne("winsor_mean")].reset_index()
    fig, ax = plt.subplots(figsize=(8.5, 5.8), layout="constrained")
    for i, item in table.iterrows():
        ax.plot([item.ci_low, item.ci_high], [i, i], color=TEAL, lw=2)
        ax.scatter(item.coefficient, i, color=INK, zorder=2)
    ax.set(yticks=range(len(table)), yticklabels=[f"{SHORT[m]} · {s}" for m, s in zip(table.metric, table.statistic)],
           xlim=(-1.05, 1.05), title="Frequency and impact rank associations",
           xlabel="Spearman ρ and 95% hazard-category bootstrap interval")
    ax.axvline(0, color="#888888", lw=1)
    ax.invert_yaxis()
    save(fig, "spearman_intervals")


def run():
    (OUT / "figures").mkdir(parents=True, exist_ok=True)
    events, impacts = load_data()
    recent = events[events[YEAR].between(2000, 2025)]
    type_tables, corr_tables, test_tables = [], [], []
    rng = np.random.default_rng(SEED)
    for window, subset in zip(WINDOWS, [events, recent]):
        summary = summarize(subset, TYPE)
        type_tables.append(summary.assign(window=window))
        corr_tables.append(correlation_table(summary, rng).assign(window=window))
        test_tables.append(distribution_tests(subset).assign(window=window))
    for filename, tables in [("impact_by_type", type_tables), ("correlations", corr_tables),
                             ("distribution_tests", test_tables)]:
        pd.concat(tables).to_csv(OUT / f"{filename}.csv", index=False)
    for filename, frame, columns in [
        ("annual", events, YEAR), ("decadal", events, "Decade"),
        ("type_by_year", events, [YEAR, TYPE]),
        ("period", events.assign(period=np.select([events[YEAR] < 2000, events[YEAR] < 2026],
                                                  ["1900–1999", "2000–2025"], "2026 partial")), "period"),
        ("country", impacts, ["ISO", "Country"]), ("country_by_year", impacts, ["ISO", "Country", YEAR]),
        ("region", impacts, "Region"),
    ]:
        summarize(frame, columns).to_csv(OUT / f"{filename}.csv", index=False)
    complete = events.copy()
    for metric in METRICS:
        complete[metric] = complete[metric].where(
            complete[f"{metric} Reported Country Impacts"].eq(complete["Country Impact Records"]))
    summarize(complete, TYPE).to_csv(OUT / "complete_country_sensitivity.csv", index=False)
    overall = summarize(events.assign(scope="all events"), "scope")
    overall.to_csv(OUT / "overall.csv", index=False)
    leaders = {}
    for metric, group in type_tables[0].groupby("metric"):
        leaders[metric] = {stat: group.loc[group[stat].idxmax(), TYPE] for stat in ESTIMANDS}
    evidence = {"events": len(events), "impacts": len(impacts),
                "type_counts": events[TYPE].value_counts().to_dict(),
                "busiest_year": int(events[YEAR].value_counts().idxmax()),
                "coverage": dict(zip(overall.metric, overall.coverage)),
                "impact_leaders": leaders}
    (OUT / "findings.json").write_text(json.dumps(evidence, indent=2) + "\n")
    figures(events, type_tables[0], corr_tables[0])


if __name__ == "__main__":
    run()
