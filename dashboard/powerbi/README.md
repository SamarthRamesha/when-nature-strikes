# Power BI authoring package

The full four-table data package is produced locally by `python scripts/prepare_emdat.py`.
Use a Windows installation of Power BI Desktop to build and refresh a PBIX. This
directory contains source queries, measures and a visual specification.

1. Create a Text parameter named `DataFolder` pointing to the absolute path of
   `data/processed`. Create blank queries `FactImpacts` and `DimEvent`, paste the
   respective M files into Advanced Editor, and load both.
2. Relate `DimEvent[Event ID]` (one) to `FactImpacts[Event ID]` (many), with a
   single filter direction from DimEvent. Use start year, reporting era and hazard
   from DimEvent. Use ISO, country and region from FactImpacts so the geography
   narrows contributions before event-level measure calculations. Keep the
   country-year summary out of this relationship model.
3. Add each DAX block as a separate measure, format coverage as a percentage,
   and import the theme. Assign ISO as Country/Region data category and inspect
   each plotted code against the Natural Earth coverage table. Keep historical
   and unmatched ISO entries in the ranking table.
4. Synchronize year, hazard, region and country slicers across all four pages.
   Use filter interactions for selections and preserve the selected scope in
   drill-through. Keep the 2026 and pre-2000 reporting caveats on every page.

| Page | Layout and bindings |
| --- | --- |
| Overview | Distinct events and three impact cards with event coverage. Horizontal hazard bars and a ranking matrix by hazard. |
| Frequency vs impact | Scatter with event-count X, selected impact measure Y, hazard detail, and reporting count and coverage tooltips. Include the totals, means and medians for all three metrics. |
| Trends | Annual stacked hazard counts, annual loss line, decade and reporting-era summaries. Show reporting denominators beside impact trends. |
| Geography | ISO-keyed filled map, country rankings, and a comparison grouped by region. Use country-record coverage for impact values. |

Acceptance checks at full scope include 15,727 distinct events, 18,060 country
impacts, 5,814 flood events and 33.4% reporting for adjusted damage on the event
denominator. Multi-country events count once across selected countries, and
unknown impact remains blank. Validate filter interactions, maps, refresh and
blank behavior in Desktop before publishing a PBIX. Keep any PBIX containing
imported EM-DAT records within the permitted audience.
