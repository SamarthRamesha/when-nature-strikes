# When Nature Strikes — Data Preparation Handover

Prepared 31 October 2026 for the dashboard and geospatial team.

## Files in this handover

| File | Grain | Use |
|---|---|---|
| `cleaned_natural_disaster_impacts.csv` | One EM-DAT country impact per row (18,060 rows) | Detailed source fields for filters and drill-down; includes all 47 source fields plus six derived fields. |
| `natural_disaster_events.csv` | One underlying natural disaster event per row (15,727 rows) | Event frequency and event-level summaries; country impacts have been consolidated here. |
| `natural_disaster_type_summary.csv` | One row per natural disaster type (15 types) | Quick overview of unique event counts and summed reported impacts by type. |
| `natural_country_year_type_summary.csv` | One row per country, start year, and disaster type (11,157 rows) | Country maps and time-series views; includes unique event count and impact sums. |

CSV files use UTF-8 with BOM for spreadsheet compatibility. Blank source values remain blank. Numeric source measures remain numeric. Source field names are retained as exported by EM-DAT.

## Scope and sources

The primary project reference is *When Nature Strikes*, the supplied approval presentation. It proposes EM-DAT and asks whether the most frequent natural disaster types are also the most destructive. This preparation therefore filters the event-impact export to `Disaster Group = Natural`. The original file also contains 9,902 technological disaster impacts; those are excluded from the four prepared files, not reclassified as natural hazards.

Dataset source metadata: EM-DAT, CRED / UCLouvain; public custom request table; version 2026-10-23; request file created 31 October 2026. The accompanying EM-DAT documentation describes each public-table row as a disaster impact in a country, and documents the fields and limitations below. See the [EM-DAT public table documentation](https://doc.emdat.be/docs/data-structure-and-content/emdat-public-table/) and the supplied PDF, *Data Structure and Content Description | EM-DAT Documentation*.

## Processing and derived fields

- Kept the 18,060 rows labelled `Natural`, preserving every original column and original nonblank value. No impact values were imputed, capped, or removed.
- Added `Event ID` by taking the year-sequence portion of `DisNo.` and dropping its final country suffix. EM-DAT appends ISO-3 to `DisNo.` in the public table; this key reconnects country impact rows for the same event.
- Added `Start Date` and `End Date` only when year, month, and day form a valid complete calendar date. Partial dates stay blank in the derived date field; the original component fields remain available.
- Added `Decade` from `Start Year` (for example, 1998 maps to 1990).
- Added `Has Coordinates = Yes` only where both latitude and longitude are present. Coordinates were not inferred from country names.
- Added `Total Damage, Adjusted (million US$)` by dividing EM-DAT's inflation-adjusted `Total Damage, Adjusted ('000 US$)` by 1,000. The original adjusted and unadjusted damage columns remain unchanged. This conversion changes units only; it does not estimate missing losses.
- Built event-level measures by summing available country-impact values for all rows sharing `Event ID`. `Country Impact Records` and per-measure reported-impact counts make the source coverage visible. A summary measure is blank when all country impacts for that measure are blank.
- Built type-level `Unique Events` as a distinct count of `Event ID`, not a count of country-impact rows. Impact totals sum reported country-impact values. The country-year-type file likewise counts unique event IDs within each group and separately reports the number of impact records.

## Data profile and caveats

- 27,962 rows in the source export; 18,060 natural country impacts; 15,727 underlying natural event IDs; 1,067 of those natural events affect more than one country.
- Natural records span 1900–2026 and cover 15 types. The most frequent by unique event count are Flood (5,814), Storm (4,026), Earthquake (1,573), and Epidemic (1,447).
- Among the 18,060 natural impact records, `Total Deaths` is blank for 5,029 (27.8%), `Total Affected` for 4,655 (25.8%), adjusted total damage for 12,210 (67.6%), and magnitude for 12,422 (68.8%). These blanks can mean no impact or unknown/unreported impact; they are not zeroes.
- Both coordinates are available for 2,847 natural impacts (15.8%). Country ISO-3, country, region, and subregion are much more complete for broad mapping. The source documentation says impact measures are recorded at country level; do not allocate them to admin-1/admin-2 areas just because a GADM unit is present.
- Historical records before 2000 are explicitly flagged `Historic = Yes` and should be treated as lower-quality per EM-DAT documentation. Consider a post-2000 view or a visible historical-period filter.
- Magnitude and `Magnitude Scale` are hazard-specific. Do not compare raw magnitude numbers across different disaster types as though they shared one scale. An epidemic magnitude may, for example, count vaccinated people, while flood magnitude is area and storm magnitude is wind speed.
- EM-DAT documents underreporting of economic loss, especially where insurance and reinsurance reporting is limited. A type with more recorded damage is not necessarily the type with the greatest true loss.
- Frequency and destructiveness require separate measures. Recommended dashboard measures: `Unique Events`; sum of `Total Deaths`; sum of `Total Affected`; and sum of adjusted damage in million US$. Show the corresponding reported-value count or coverage alongside impact totals. Avoid treating a blank impact as zero or comparing aggregate totals without noting record coverage.

## Handover recommendations

1. Use `natural_disaster_events.csv` for a one-row-per-event frequency-vs-impact comparison. Use `natural_disaster_type_summary.csv` for a compact type overview.
2. Use `cleaned_natural_disaster_impacts.csv` when users need country-level filtering, associated types, dates, event names, or the exported GADM Admin Units field.
3. Use `natural_country_year_type_summary.csv` for country-level maps and annual trends. Join map geometries with `ISO`; historical ISO extensions documented by EM-DAT may need a join table.
4. For map coloring, use country-level reported sums and clearly label the measure. A country map of total deaths or damage shows country-level impacts, not subnational distribution.
5. Keep `Total Damage, Adjusted (million US$)` separate from unadjusted damage. Make the selected amount and unit explicit in labels/tooltips.
6. For event type, use `Disaster Type` for the approved type-level question and expose subgroup/subtype for drill-down. Use `Associated Types` as additional tags, not as a second event classification to count again.

## Requirement provenance and differences

### Explicit teacher instructions

No teacher approval, feedback, or correction document was included among the supplied project files. No teacher-specific directions are inferred here. If such feedback exists elsewhere, compare it against this handover before treating this preparation as final to the teacher's direction.

### Team allocation

The task prompt states that Samarth Ramesha and Shashank S K own dataset inspection and preparation, and Shreya Patil and Shreya S Mattimadu own dashboard development and Unit 2/geospatial work. No allocation screenshot was identified among the supplied project materials, so that allocation is recorded as the user's prompt, not independently verified from a screenshot. This handover prepares data for the dashboard team and does not build the dashboard.

### Difference requiring team/teacher confirmation

The approval PPT describes Unit 1 and Unit 3 coverage and an interactive Power BI dashboard. The allocation supplied in the task prompt assigns dashboard development and the geospatial component to Unit 2. These descriptions differ on the unit/geospatial scope. No teacher feedback was available to resolve the difference. Keep this discrepancy visible and confirm which unit coverage is expected before final submission. The approved research question and natural-hazard dataset remain aligned across the available materials.

### Technical recommendations (not teacher instructions)

The grain-aware event key, missing-value handling, unit conversion, event/impact aggregations, coverage counts, and dashboard suggestions in this handover are technical choices made to support the approved question and the supplied EM-DAT definitions. They are not attributed to the teacher or team agreement.
