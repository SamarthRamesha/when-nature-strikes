"""Four interactive views sharing one set of filters and impact definitions."""
import os
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.geography import boundaries, map_coverage
from dashboard.analysis_views import clustering, dimensionality, ml, quality, story, xai
from src.metrics import ROOT, ID, TYPE, YEAR, METRICS, SHORT, filtered_events, load_data, summarize

NAVIGATION = ("Overview", "Frequency vs impact", "Trends", "Geography", "Guided findings",
              "Machine learning", "Explainable AI", "Dimensionality reduction", "Clustering and anomalies",
              "Data quality and methodology")
SAVED_VIEWS = dict(zip(NAVIGATION[5:], (ml, xai, dimensionality, clustering, quality)))
TEAL = "#087f80"
STATS = {"Total": "total", "Mean": "mean", "Median": "median"}
PICKABLE = {f"{SHORT[m]} ({unit})": m for m, unit in METRICS.items()}


@st.cache_data
def data(synthetic):
    if synthetic:
        root = ROOT / "dashboard/powerbi"
        events = pd.read_csv(root / "synthetic_events.csv")
        impacts = pd.read_csv(root / "synthetic_impacts.csv").merge(events[[ID, TYPE, YEAR]], on=ID, validate="many_to_one")
    else:
        events, impacts = load_data()
    impacts = impacts.drop(columns=YEAR).merge(events[[ID, YEAR]], on=ID, validate="many_to_one")
    return events, impacts, boundaries()


def draw(fig, key):
    fig.update_layout(margin=dict(l=12, r=12, t=20, b=12), paper_bgcolor="white",
                      font=dict(color="#182942"), legend_title_text="")
    st.plotly_chart(fig, width="stretch", key=key, config={"displaylogo": False})


def metric_picker(key):
    return PICKABLE[st.selectbox("Impact metric", tuple(PICKABLE), key=key)]


def event_table(frame, by, metric):
    return summarize(frame, by).query("metric == @metric").copy()


def show_table(frame, columns):
    table = frame[columns].rename(columns={"events": "Distinct events", "records": "Records",
        "reported": "Reporting count", "coverage": "Coverage (%)", "total": "Total",
        "mean": "Mean", "median": "Median"})
    if "Coverage (%)" in table:
        table = table.assign(**{"Coverage (%)": (table["Coverage (%)"] * 100).round(1)})
    st.dataframe(table, hide_index=True, width="stretch")


def overview(frame):
    overall = summarize(frame.assign(scope="all"), "scope")
    cards = st.columns(4)
    cards[0].metric("Distinct events", f"{len(frame):,}")
    for card, row in zip(cards[1:], overall.itertuples()):
        card.metric(f"{SHORT[row.metric]} ({row.unit})", f"{row.total:,.1f}" if pd.notna(row.total) else "Unknown")
        card.caption(f"{row.reported:,} / {len(frame):,} reporting ({row.coverage:.1%})")
    st.subheader("Recorded events by hazard")
    counts = frame[TYPE].value_counts().sort_values().rename("Events").reset_index()
    draw(px.bar(counts, x="Events", y=TYPE, orientation="h", color_discrete_sequence=[TEAL]), "hazards")
    metric = metric_picker("overview_metric")
    show_table(event_table(frame, TYPE, metric).sort_values("total", ascending=False),
               [TYPE, "events", "reported", "coverage", "total", "mean", "median"])


def frequency(frame):
    st.subheader("How does the ranking change with the impact measure?")
    metric = metric_picker("relationship_metric")
    stat = STATS[st.radio("Impact summary", tuple(STATS), horizontal=True)]
    table = event_table(frame, TYPE, metric)
    valid = table[table[stat].notna()].copy()
    if not valid.empty:
        valid["Reporting coverage"] = valid.coverage.map("{:.1%}".format)
        draw(px.scatter(valid, x="events", y=stat, color="coverage", size="events", size_max=28,
                        hover_name=TYPE, log_x=True, color_continuous_scale="Teal",
                        hover_data={"reported": True, "Reporting coverage": True, "coverage": False},
                        labels={"events": "Distinct events (log scale)", "coverage": "Reporting share",
                                stat: f"{stat.title()} ({METRICS[metric]})"}), "relationship")
        leader = valid.sort_values([stat, TYPE], ascending=[False, True]).iloc[0]
        st.write(f"{leader[TYPE]} leads this reported {stat}, based on {leader.reported:,} of "
                 f"{leader.events:,} recorded events.")
    st.caption("Totals combine frequency with reported losses. Per-event averages and medians use reporting events. Sparse reporting can change rankings.")
    show_table(table.sort_values(stat, ascending=False),
               [TYPE, "events", "reported", "coverage", "total", "mean", "median"])


def trends(frame):
    metric = metric_picker("trend_metric")
    frequency = frame.groupby([YEAR, TYPE], observed=True)[ID].nunique().rename("Events").reset_index()
    st.subheader("Annual recorded frequency by hazard")
    draw(px.bar(frequency, x=YEAR, y="Events", color=TYPE, height=440), "annual_by_hazard")
    st.subheader(f"Annual reported {SHORT[metric].lower()}")
    annual = event_table(frame, YEAR, metric)
    draw(px.line(annual, x=YEAR, y="total", markers=True, hover_data=["events", "reported", "coverage"],
                 labels={"total": METRICS[metric]}, color_discrete_sequence=[TEAL]), "annual_impact")
    st.subheader("Decades and reporting eras")
    periods = frame.assign(Decade=(frame[YEAR] // 10) * 10,
                           Era=frame[YEAR].map(lambda y: "1900–1999" if y < 2000 else "2000–2025" if y < 2026 else "2026 partial"))
    for grouping in ("Decade", "Era"):
        show_table(event_table(periods, grouping, metric),
                   [grouping, "events", "reported", "coverage", "total"])


def geography(frame, world):
    st.subheader("Recorded impacts by affected country")
    choice = st.selectbox("Map measure", ("Distinct events", *PICKABLE))
    metric = PICKABLE.get(choice, next(iter(METRICS)))
    table = event_table(frame, ["ISO", "Country"], metric)
    value = "events" if choice == "Distinct events" else "total"
    matched, missing = map_coverage(frame, world)
    st.caption(f"{matched:,} of {len(frame):,} country-impact records map by ISO. Totals are unnormalized.")
    table["Reporting coverage"] = table.coverage.map("{:.1%}".format)
    fig = px.choropleth_map(table.dropna(subset=[value]), geojson=world, locations="ISO", color=value,
                            hover_name="Country", hover_data=["reported", "records", "Reporting coverage"],
                            labels={value: choice}, color_continuous_scale="Teal", map_style="white-bg",
                            zoom=1.0, center={"lat": 17, "lon": 0}, height=480)
    draw(fig, "country_map")
    tabs = st.tabs(["Country rankings", "Regional comparison", "Unmapped records"])
    with tabs[0]:
        show_table(table.sort_values(value, ascending=False),
                   ["ISO", "Country", "events", "records", "total", "reported", "coverage"])
    with tabs[1]:
        regions = event_table(frame, "Region", metric)
        show_table(regions.sort_values(value, ascending=False),
                   ["Region", "events", "records", "total", "reported", "coverage"])
        st.caption("Regional events are distinct within each region. Reporting coverage uses country-impact records.")
    with tabs[2]:
        st.dataframe(missing, hide_index=True, width="stretch")


def main():
    st.set_page_config(page_title="When Nature Strikes", layout="wide")
    st.title("When Nature Strikes")
    selected = st.sidebar.radio("Page", NAVIGATION)
    synthetic = os.environ.get("WNS_DATA_MODE") == "synthetic"
    st.caption("[EM-DAT data](https://www.emdat.be/) · CRED / UCLouvain · 23 October 2026 export")
    if synthetic and selected not in SAVED_VIEWS:
        st.warning("SYNTHETIC DEMONSTRATION · Invented records for testing controls. Saved research cohorts are separate views.")
    try:
        events, impacts, world = data(synthetic)
    except FileNotFoundError:
        if selected in SAVED_VIEWS:
            SAVED_VIEWS[selected]()
        else:
            st.error("Run python scripts/prepare_emdat.py, or launch with WNS_DATA_MODE=synthetic to use invented demonstration rows.")
        return
    st.sidebar.caption("Filters apply to overview, comparisons, trends, geography and guided findings.")
    lo, hi = int(events[YEAR].min()), int(events[YEAR].max())
    years = st.sidebar.slider("Event start years", lo, hi, (lo, hi))
    hazards = st.sidebar.multiselect("Hazard types", sorted(events[TYPE].unique()))
    regions = st.sidebar.multiselect("Affected regions", sorted(impacts.Region.dropna().unique()))
    options = impacts if not regions else impacts[impacts.Region.isin(regions)]
    country_names = (options[["ISO", "Country"]].drop_duplicates().dropna().set_index("ISO").Country.to_dict())
    countries = st.sidebar.multiselect("Affected countries", sorted(country_names),
                                       format_func=lambda iso: f"{country_names[iso]} ({iso})")
    take = impacts[YEAR].between(*years)
    if hazards:
        take &= impacts[TYPE].isin(hazards)
    if regions:
        take &= impacts.Region.isin(regions)
    if countries:
        take &= impacts.ISO.isin(countries)
    if selected in SAVED_VIEWS:
        SAVED_VIEWS[selected]()
        return
    scope = impacts.loc[take]
    if years[1] == 2026 and not synthetic:
        st.info("2026 is partial. Pre-2000 event counts reflect historical reporting limitations.")
    st.caption("Geographic filters restrict losses to the selected countries. Multi-country events count once in the selected scope.")
    if scope.empty:
        st.warning("No records match these filters.")
        return
    if selected == "Geography":
        geography(scope, world)
    elif selected == "Guided findings":
        story(filtered_events(scope, events), scope, synthetic)
    else:
        {"Overview": overview, "Frequency vs impact": frequency, "Trends": trends}[selected](
            filtered_events(scope, events))


if __name__ == "__main__":
    main()
