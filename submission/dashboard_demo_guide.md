# Dashboard demonstration

## Setup

Place an authorized workbook in `data/source`, install the pinned dependencies,
and run `python scripts/prepare_emdat.py`. Launch
`python -m streamlit run dashboard/app.py --server.port 8765` from the root and
open `http://127.0.0.1:8765`. Leave filters clear at the start.

## Two minute tour

1. **Overview.** Confirm 15,727 distinct events and show 74.1%, 78.6% and 33.4%
   reporting for deaths, affected population and adjusted damage. Hover on the
   flood bar and show 5,814 events.
2. **Frequency vs impact.** Choose adjusted damage. Toggle **Total** to
   **Mean** and then **Median**. Full-snapshot leaders are storm, earthquake and
   drought respectively. Point to the reporting count and units for each.
3. **Trends.** Narrow the year range to 2000–2025. Compare year and decade
   counts and show the impact reporting denominator. Return to the full range
   and point out the partial-2026 message.
4. **Geography.** Choose adjusted damage or event frequency and hover over a
   country. Show the ranking and unmapped tabs. Choose India and Flood in the
   sidebar, then return to Overview and confirm that the filters persist and
   the displayed totals change.

If the live demo cannot run, use the real screenshots in the presentation
and the [static country map](../results/figures/geography.png). Present the
browser application and [Power BI sources](../dashboard/powerbi/README.md)
by their actual formats.
