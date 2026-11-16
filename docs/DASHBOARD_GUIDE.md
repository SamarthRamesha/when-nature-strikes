# Dashboard guide

Launch from the repository root after rebuilding the data.

```sh
python -m streamlit run dashboard/app.py --server.port 8765
```

The sidebar filters by canonical event year, primary hazard, affected region
and ISO country. All four views use these controls. With geographic filters,
impacts are summed from the selected country rows and events are counted
once within the selection. Event loss summaries report observed event
contributions. Country and regional impact coverage uses country-impact rows.

| View | Interaction and interpretation |
| --- | --- |
| Overview | Compare distinct-event frequency and reported losses. Use the metric selector to see rankings with denominators. |
| Frequency vs impact | Choose one of three impact variables and total, mean or median. Hover on a hazard for counts and coverage. A single report can dominate a sparse hazard's ranking. |
| Trends | Explore annual composition and impact, with decade and era summaries. The partial 2026 warning applies whenever 2026 is selected. |
| Geography | Choose count or a loss metric. Zoom and hover on ISO-matched country polygons. Compare ranked countries and regions or inspect unmatched entries. |

Natural Earth 1:110m Admin 0 country polygons use `ISO_A3_EH`. Historical codes
and small territories without matching polygons remain in tables. The app maps
countries, so source event coordinates are unnecessary. Regional counts can
repeat cross-region events and should not be summed to obtain world counts.
See [Power BI sources and acceptance checks](../dashboard/powerbi/README.md).

## Browser checks and screenshots

With the dashboard running locally, use:

```sh
python -m playwright install chromium --only-shell
python tests/browser_acceptance.py --screenshots results/figures
```

The test checks the full and flood-only event count, all four views, the
summary-mode control, filter state and map canvas. Screenshot files record
the real browser app. Keep the dashboard reachable only by the permitted
audience for the workbook.
