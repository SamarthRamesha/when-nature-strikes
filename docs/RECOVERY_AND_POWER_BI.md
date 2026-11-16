# Recovery and Power BI integration

The original baseline is `9b48a5043cda4238ad53c4d66e18cc0c19d1c870`. The
integration branch starts from `66179d9`, preserving the tested academic
handover and its history. The baseline, `main`, the final-submission branch and
draft PR #3 remain intact. [Original draft PR](https://github.com/SamarthRamesha/when-nature-strikes/pull/3)

## What was recovered

The full baseline tree was recovered byte for byte into a local recovery copy.
It includes the source workbook, four CSVs, six original notebooks with their
saved outputs, 17 EDA outputs, 32 EDA charts, original preparation and
validation scripts, the data dictionary and the handover notes. The public
branch restores the three original EDA CSV names and data handover and retains
the six executable notebooks with source-row displays cleared. The 32 original
charts are byte-identical to the baseline. [Exact recovery inventory and hashes](../submission/evidence/recovery_baseline.json)

| Local file | Rows | Original-script rerun versus the baseline |
| --- | ---: | --- |
| EM-DAT workbook | 27,962 | Exact source SHA-256 |
| `cleaned_natural_disaster_impacts.csv` | 18,060 | Byte-identical |
| `natural_disaster_events.csv` | 15,727 | 27 floating-point representations differ, maximum absolute delta `1.46e-11` |
| `natural_disaster_type_summary.csv` | 15 | 7 floating-point representations differ, maximum absolute delta `1.19e-7` |
| `natural_country_year_type_summary.csv` | 11,157 | 119 floating-point representations differ, maximum absolute delta `1.16e-10` |

The maintained deterministic pipeline matched all four pinned hashes in
[provenance](../results/provenance.json). The original and maintained validators
returned 69 passes and two data warnings, and all 89 EDA comparisons matched.
The maintained full run reproduced the saved findings, model metrics, SHAP,
LIME summary, permutation, PDP/ICE, PCA, t-SNE, UMAP, clustering, anomaly and
geography outputs. Exact embeddings, per-event predictions and ICE stay local.
The existing ten Streamlit views and the final report, presentation, speaker
notes, presenter script, viva material, literature and demo guide are retained.
[Data access](DATA_LICENSE.md) · [Final validation](VALIDATION_REPORT.md)

## Supplied Power BI sources

| File | Read-only inspection |
| --- | --- |
| `When_Nature_Strikes_dashboard.pbix` | Shreya Patil’s three analytical pages contain 43 visuals. The fourth page is empty. Four CSV-backed tables and four relationships are present, with three active and one inactive. Report queries used implicit counts, sums and averages. |
| `nature_strike_geospatial.pbix` | Shreya S Mattimadu’s page contains 11 visuals. The bubble and filled maps, three Top 10 country charts, three impact cards and three slicers came from this page. Its one 53-column fact table has five measure records, including a duplicate draft of the distinct count, and no model relationships. |
| `nature_strike_geospatial.pbip` | References `nature_strike_geospatial.Report`. That directory was absent from the ZIP and repository. The actual page was recovered from the geospatial PBIX’s enhanced report definitions. |
| `When_Nature_Strikes_dashboard.pbit` | Three analytical pages and their four-table model schema. Used to verify table and relationship metadata. It also contains template navigation buttons. The integrated project uses native tabs. |

Both imported PBIX impact tables had 18,060 rows and 15,727 unique event IDs.
A read-only PBIXRay comparison keyed on `DisNo.` matched the baseline IDs,
country, ISO, region, year, hazard and subgroup, loss values and missingness
for the bindings used here. The source PBIXs contain imported EM-DAT records.
All four originals remain byte-for-byte separate from the distributable
project. [Source hashes and visual counts](../submission/evidence/recovery_baseline.json)
· [Microsoft enhanced report format](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report)

## One authoritative model

The two portable imports are `FactImpacts` at country-impact grain and
`DimEvent` at consolidated event grain. One active one-to-many relationship
filters impacts from the unique `DimEvent[Event ID]`. Country, region and ISO
filter the fact table. Canonical year, decade, hazard and subgroup filter the
event dimension. The original type and country-year-type CSVs remain available
in the local rebuild. The integrated visuals use the two detailed grains and
measures, so the original summary-table paths and auto-date tables are
unnecessary in the integrated model. Three disconnected tables provide the
impact, summary and map selectors.

The actual 54 donor visuals keep their page or visual IDs. The generator
rebinds projections, sorts, tooltips, Top N filters and the choropleth color
rule to the shared model. It clears saved geography slicer selections that
would otherwise start in 1925 or on Flood. Original count-of-event-ID
aggregations become distinct event measures. Original country record counts
remain record counts. Mean and median losses use reporting events within the
selected geography, with blanks carried through. Shreya S Mattimadu’s impact
sum and distinct count logic is implemented by the corresponding shared
measures. Her 10 explicit page interactions are retained and the map
selections also filter the country ranking charts. The Overview hazard bar
cross-highlights the subgroup chart. Guided Findings, coverage tables and
selectable severity continue the later analytical additions.

The bubble map retains damage by country and hazard. The filled map uses a
selector for frequency, deaths, affected or adjusted damage. Both bind
allowlisted ISO3 values and retain unmatched records in the tables. Their
Bing service and security settings need a Desktop check. The integrated
report contains the team’s two map types and does not use Azure Maps, which
can depend on a tenant setting and sign-in. Use the country and region
rankings for in-report geographic testing and Streamlit’s locally bundled
Natural Earth choropleth when online map tiles are unavailable. [Bing maps in Power BI](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-filled-maps-choropleths)
· [Azure Maps tenant settings](https://learn.microsoft.com/en-us/azure/azure-maps/power-bi-visual-manage-access)

Both generated projects passed the Power BI authoring checks with zero
errors and two documented legacy-map deprecation warnings. The 13 Power
Query expressions also parsed. Interactive rendering, refresh, interactions,
PBIX save and reopen await a signed-in Windows Desktop session. [Desktop acceptance checklist](../WINDOWS_HANDOVER/POWERBI_ACCEPTANCE_CHECKLIST.md)
