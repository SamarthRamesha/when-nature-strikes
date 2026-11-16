"""Interactive profiles, explanations and saved research cohorts."""
import json

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.metrics import ID, METRICS, OUT, SHORT, TYPE, YEAR, summarize

TEAL = "#087f80"
DIM = OUT / "dimensionality_reduction"
XAI = OUT / "xai"
METHODS = ("PCA", "t-SNE", "UMAP")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def chart(fig, key):
    fig.update_layout(margin=dict(l=15, r=15, t=24, b=10), paper_bgcolor="white",
                      font=dict(color="#182942"), legend_title_text="")
    st.plotly_chart(fig, width="stretch", key=key, config={"displaylogo": False})


def cohort(label):
    st.caption(f"Saved EM-DAT analysis • {label}. Use the controls on this page to explore this fixed research cohort.")


def story(events, impacts, synthetic):
    st.subheader("Follow the evidence")
    topics = ("Occurrence", "Accumulated burden", "Typical severity", "Time", "Geography", "Limitations", "Conclusion")
    step = st.segmented_control("Story step", topics, default=topics[0], key="story_step")
    if step is None:
        step = topics[0]
    metric = st.selectbox("Story impact metric", tuple(METRICS), format_func=lambda key: SHORT[key])
    unit = METRICS[metric]
    table = summarize(events, TYPE).query("metric == @metric")
    first = table.sort_values("events", ascending=False).iloc[0]
    if step in ("Occurrence", "Accumulated burden", "Typical severity"):
        stat = {"Occurrence": "events", "Accumulated burden": "total",
                "Typical severity": st.radio("Typical event", ("mean", "median"), horizontal=True)
                if step == "Typical severity" else "mean"}[step]
        ranking = table.dropna(subset=[stat]).sort_values(stat)
        if ranking.empty:
            st.info("The selected scope contains no reported values for this metric.")
            return
        top = ranking.iloc[-1]
        columns = ["events", "reported", "coverage"]
        hover = {name: ":.1%" if name == "coverage" else True for name in columns if name != stat}
        chart(px.bar(ranking, x=stat, y=TYPE, orientation="h", hover_data=hover, color_discrete_sequence=[TEAL],
                     labels={stat: "Distinct events" if stat == "events" else f"{stat.title()} ({unit})"}),
              "story_ranking")
        if stat == "events":
            st.write(f"{top[TYPE]} leads with {top.events:,} distinct events in the selected scope.")
        else:
            st.write(f"{top[TYPE]} leads this {stat} with {top[stat]:,.2f} {unit}. "
                     f"{top.reported:,} of its {top.events:,} events report this impact ({top.coverage:.1%}).")
    elif step == "Time":
        annual = summarize(events, YEAR).query("metric == @metric")
        chart(px.line(annual, x=YEAR, y="events", markers=True, hover_data=["reported", "coverage"],
                     labels={"events": "Distinct events"}, color_discrete_sequence=[TEAL]), "story_time")
        st.write("Compare complete years and check reporting coverage before interpreting a trend.")
    elif step == "Geography":
        region = summarize(impacts, "Region").query("metric == @metric").dropna(subset=["total"])
        chart(px.bar(region.sort_values("total"), x="total", y="Region", orientation="h",
                     hover_data={"reported": True, "coverage": ":.1%"}, color_discrete_sequence=[TEAL],
                     labels={"total": f"Total ({unit})"}), "story_region")
        st.write("These totals describe recorded contributions by affected region. Open Geography to inspect country polygons.")
    elif step == "Limitations":
        all_rows = summarize(events.assign(scope="Selected scope"), "scope")
        st.dataframe(all_rows[["metric", "events", "reported", "coverage"]], hide_index=True,
                     column_config={"coverage": st.column_config.NumberColumn(format="percent")})
        st.write("An unreported value remains unknown. Historical monitoring coverage differs, and the 2026 source year is partial.")
    else:
        candidates = table.dropna(subset=["total"])
        st.write(f"{first[TYPE]} leads recorded frequency in this selection. Totals describe accumulated reported loss, "
                 "while mean and median summarize reporting events. Compare the leaders across metrics and periods.")
        if not candidates.empty:
            leaders = {stat.title(): candidates.loc[candidates[stat].idxmax(), TYPE] for stat in ("total", "mean", "median")}
            st.dataframe(pd.DataFrame(list(leaders.items()), columns=["Summary", "Leading hazard"]), hide_index=True)
        if synthetic:
            st.caption("This is a demonstration with invented rows. Open the research report for the EM-DAT findings.")


def ml():
    info = read_json(OUT / "model_metrics.json")
    cohort("single-country events with mortality reported")
    st.subheader("Retrospective high-mortality ranking")
    models = info["test"]
    chosen = st.selectbox("Classifier", tuple(models), index=list(models).index(info["selected"]))
    stats = models[chosen]
    row = st.columns(4)
    for col, key, label in zip(row, ("average_precision", "roc_auc", "macro_f1", "brier"),
                               ("Average precision", "ROC AUC", "Macro F1", "Brier score")):
        col.metric(label, f"{stats[key]:.3f}")
    st.caption(f"Threshold selected in 2018–2021. Held out 2022–2025: {info['splits']['test']['events']:,} events. "
               f"Positive target: at least {info['threshold_deaths']} reported deaths.")
    matrix = stats["confusion"]
    chart(px.imshow(matrix, text_auto=True, x=["Below 100", "100 or more"], y=["Below 100", "100 or more"],
                    labels={"x": "Predicted class", "y": "Observed class", "color": "Events"},
                    color_continuous_scale="Teal", height=390), "ml_confusion")
    st.dataframe(pd.DataFrame({key: stats["by_class"][key] for key in ("0", "1")}).T,
                 width="stretch")
    st.write("Hazard type, region and month are the only inputs. The time split limits look-ahead. "
             "Event reporting and the single-country eligibility rule restrict generalization.")


def xai():
    info = read_json(XAI / "summary.json")
    cohort(f"{info['held_out_events']} held-out events; local scenarios use invented inputs")
    st.subheader("Explainable AI")
    view = st.radio("Explanation view", ("Global importance", "Local scenarios", "Month PDP and ICE"),
                    horizontal=True, key="xai_view")
    if view == "Global importance":
        cols = st.columns(2)
        pfi = pd.read_csv(XAI / "permutation_importance.csv").sort_values("mean_ap_drop")
        with cols[0]:
            st.markdown("#### Held-out permutation")
            chart(px.bar(pfi, x="mean_ap_drop", y="feature", error_x="sd_ap_drop", orientation="h",
                         labels={"mean_ap_drop": "Average precision drop", "feature": ""},
                         color_discrete_sequence=[TEAL]), "pfi")
        with cols[1]:
            st.markdown("#### Grouped SHAP")
            st.image(str(OUT / "figures/shap_global.png"), width="stretch")
        with st.expander("SHAP beeswarm and hazard comparison"):
            st.image(str(OUT / "figures/shap_beeswarm.png"))
            st.image(str(OUT / "figures/shap_hazard.png"))
        st.write("Permutation asks how much a field improves ranking when its meaning is intact. "
                 "SHAP describes how much that field moves scores. The scales differ, and correlated predictors can share credit.")
    elif view == "Local scenarios":
        case = st.selectbox("Illustrative profile", tuple(info["scenarios"]))
        selection = info["scenarios"][case]
        st.metric("Model score for at least 100 deaths", f"{selection['prediction']:.1%}")
        st.caption("Invented metadata combination. The model was fitted on the authorized training cohort.")
        left, right = st.columns(2)
        with left:
            st.image(str(XAI / selection["shap_image"]), width="stretch")
        with right:
            frame = pd.DataFrame(selection["lime"]["conditions"], columns=["Condition", "Weight"])
            chart(px.bar(frame, x="Weight", y="Condition", orientation="h", color_discrete_sequence=[TEAL],
                         labels={"Weight": "Local probability-scale coefficient"}), "lime_case")
            st.caption(f"Weighted surrogate R² {selection['lime']['weighted_r2']:.3f}. "
                       "Perturbations may combine sparse or unusual categories.")
    else:
        data = pd.read_csv(XAI / "pdp_ice.csv")
        targets = st.multiselect("Show scenario ICE curves", ["Scenario 1", "Scenario 2", "Scenario 3"],
                                 default=["Scenario 1"])
        labels = {"month": "Calendar month category", "value": "Predicted probability"}
        fig = px.line(data, x="month", y=["held_out_mean", *targets], markers=True, labels=labels)
        fig.add_trace(go.Scatter(x=[*data.month, *data.month[::-1]],
            y=[*data.held_out_q90, *data.held_out_q10[::-1]], fill="toself", name="Held-out 10th–90th percentile",
            fillcolor="rgba(8,127,128,.15)", line=dict(color="rgba(0,0,0,0)"), hoverinfo="skip"))
        fig.update_xaxes(dtick=1)
        chart(fig, "pdp")
        st.write("Month is categorical. Each line replaces that category and holds all other fields fixed. "
                 "The variations summarize model sensitivity and may represent rare combinations. They do not identify causes.")


def projection(method, dimensions, grouping, filters=True):
    cells = pd.read_csv(DIM / "projection_cells.csv")
    buckets = cells[(cells.method == method) & (cells.dimensions == dimensions) & (cells.grouping == grouping)].copy()
    if filters:
        categories = sorted(buckets.group.unique())
        chosen = st.multiselect("Visible hazard groups", categories, key="projection_hazards")
        if chosen:
            buckets = buckets[buckets.group.isin(chosen)]
    labels = {"axis1": f"{method} 1", "axis2": f"{method} 2", "axis3": f"{method} 3",
              "events": "Events in cell", "group": grouping.title()}
    settings = dict(x="axis1", y="axis2", color="group", size="events", labels=labels, height=490)
    fig = px.scatter_3d(buckets, z="axis3", **settings) if dimensions == 3 else px.scatter(buckets, **settings)
    chart(fig, f"{method}_{grouping}_{dimensions}")
    st.caption(f"{buckets.events.sum():,} events represented by visible aggregate cells. Cells with fewer than five events are omitted.")


def dimensionality():
    info = read_json(OUT / "profile_summary.json")
    cohort(f"{info['complete_events']:,} fully reporting events, 2000–2025")
    st.subheader("Compare impact projections")
    method = st.selectbox("Projection method", METHODS)
    dimensions = st.radio("PCA dimensions", (2, 3), horizontal=True) if method == "PCA" else 2
    projection(method, dimensions, "hazard")
    if method == "PCA":
        st.metric("Variance explained by the first two components", f"{sum(info['explained_variance_ratio'][:2]):.1%}")
        st.image(str(OUT / "figures/pca_variance.png"), width="stretch")
    else:
        diagnostics = info["embedding_diagnostics"][method]
        st.metric("15-neighbor trustworthiness", f"{diagnostics['trustworthiness_15']:.3f}")
        st.write("Neighborhood plots emphasize local similarity. Separation and distances across groups depend on settings.")
    st.caption("Local reproduction writes event-level coordinates to results/dimensionality_reduction/embeddings_local.csv.")


def clustering():
    info = read_json(OUT / "profile_summary.json")
    cohort(f"{info['complete_events']:,} fully reporting events, 2000–2025")
    st.subheader("Cluster structure and anomalies")
    mode = st.radio("Analysis", ("K-means", "DBSCAN", "Isolation Forest"), horizontal=True)
    table = pd.read_csv(OUT / "cluster_evaluation.csv")
    if mode == "Isolation Forest":
        st.metric("Flagged profiles", info["anomaly_flags"])
        st.dataframe(pd.read_csv(DIM / "anomaly_summary.csv"), hide_index=True)
        local = DIM / "embeddings_local.csv"
        if local.is_file() and st.checkbox("Show examples from authorized local data"):
            data = pd.read_csv(local)
            st.dataframe(data.loc[data.anomaly_flag, [ID, TYPE, YEAR, "cluster", *METRICS, "anomaly_score"]]
                         .nlargest(8, "anomaly_score"), hide_index=True)
        st.caption("Flags prioritize records for examination. They can reflect extreme impacts or reporting peculiarities.")
    else:
        st.dataframe(table[table.method.eq(mode)], hide_index=True)
        if mode == "K-means":
            projection("PCA", 2, "cluster", filters=False)
            st.dataframe(pd.read_csv(OUT / "cluster_profiles.csv"), hide_index=True)
        else:
            st.write("DBSCAN returned one density-connected group across the tested radii. Noise counts vary with radius.")


def quality():
    info = read_json(OUT / "provenance.json")
    st.subheader("Data quality and methodology")
    cohort("23 October 2026 authorized workbook")
    cols = st.columns(3)
    cols[0].metric("Source workbook rows", f"{info['source_rows']:,}")
    cols[1].metric("Natural country impacts", f"{info['natural_impacts']:,}")
    cols[2].metric("Distinct natural events", f"{info['natural_events']:,}")
    labels = {"Impact": list(info["missing"]), "Missing country-impact rows": list(info["missing"].values())}
    frame = pd.DataFrame(labels)
    frame["Missing share"] = frame["Missing country-impact rows"] / info["natural_impacts"]
    st.dataframe(frame, hide_index=True, column_config={"Missing share": st.column_config.NumberColumn(format="percent")})
    st.caption("71 automated checks. 69 passed and two warnings describe explicit magnitude zeroes and non-additive country event counts.")
    with st.expander("From country records to analytical cohorts"):
        st.write("The prep script groups country impacts by Event ID while preserving reporting counts and explicit zeros. "
                 "The mortality cohort uses reported single-country events. The profile cohort uses fully reporting 2000–2025 events. "
                 "The country map joins contemporary Natural Earth ISO codes and retains unmatched entries in tables.")
        st.code(info["source_sha256"], language=None)
    st.markdown("[EM-DAT documentation](https://doc.emdat.be/) · [Project methodology](https://github.com/SamarthRamesha/when-nature-strikes/blob/project/complete-final-submission/docs/METHODOLOGY.md)")
