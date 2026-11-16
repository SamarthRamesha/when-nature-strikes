# Integration Handover — When Nature Strikes

Written by Samarth Ramesha at the end of the data/preparation phase. This document is the
coordination map for the **single integrated Power BI dashboard**; it does not replace
`docs/DATA_HANDOVER.md` (derivations, caveats) or `docs/DASHBOARD_DATA_HANDOVER.md` (build
guidance, DAX).

Status convention used below: **Done** = present in the repository and verified this run;
**Blocked** = cannot proceed without something outside this repository; **Open** = outstanding for
a named teammate.

---

## 1. What Samarth has completed

| Area | Deliverable | Status |
|---|---|---|
| Dataset inspection and cleaning | `scripts/prepare_emdat.py` reads the EM-DAT workbook, filters `Disaster Group = Natural`, derives `Event ID`, dates, `Decade`, `Has Coordinates`, and damage in million US$ | Done (unmodified this run) |
| Processed datasets | Four CSVs in `data/processed/` | Done (unmodified this run) |
| Data documentation | `docs/DATA_HANDOVER.md`, `data/processed/README.md`, `data/source/README.md` | Done (unmodified this run) |
| Data quality validation | `scripts/validate_project_data.py`, `analysis/outputs/data_quality_report.json`, `docs/DATA_QUALITY_REPORT.md` | **Done this run** — 71 checks, 69 pass, 2 warn, 0 fail |
| EDA verification | `scripts/verify_eda_findings.py`, `analysis/outputs/eda_validation.json`, `docs/EDA_VALIDATION_REPORT.md` | **Done this run** — 6 findings verified, 89/89 committed values reproduced |
| Dashboard data handover | `docs/DASHBOARD_DATA_HANDOVER.md` | **Done this run** |
| Integration handover | this file | **Done this run** |
| Final summary | `docs/SAMARTH_COMPLETION_SUMMARY.md` | **Done this run** |
| Power BI `.pbix` | not touched | Out of Samarth's scope; owned by the dashboard team |

---

## 2. Exact assets available to the dashboard team

Data (`data/processed/`, all UTF-8 with BOM, never regenerate without reason):

| File | Rows | Grain |
|---|---|---|
| `cleaned_natural_disaster_impacts.csv` | 18,060 | One country impact |
| `natural_disaster_events.csv` | 15,727 | One consolidated event |
| `natural_disaster_type_summary.csv` | 15 | One disaster type |
| `natural_country_year_type_summary.csv` | 11,157 | One country × year × type |

Documentation: `docs/DATA_HANDOVER.md` (source, derivations, caveats, units),
`docs/DATA_DICTIONARY.md` (every column, unit, origin and fill rate),
`docs/DASHBOARD_DATA_HANDOVER.md` (dataset choice, grain, metrics, model, DAX),
`docs/DATA_QUALITY_REPORT.md` (validation evidence), `docs/EDA_VALIDATION_REPORT.md`
(verified findings), `docs/PROJECT_APPROVAL_SUMMARY.md` (approved scope).

Reference outputs: `analysis/outputs/*.csv` (tables the notebooks export) and
the 32 charts under `visualizations/` (frequency, impacts, trends, patterns and final, Shashank's work).

---

## 3. Which dataset each visual should use

| Visual | File | Measure |
|---|---|---|
| KPI cards: total events / types / period | `natural_disaster_events.csv` | `DISTINCTCOUNT('Event ID')` |
| Ranked frequency bar by type | `natural_disaster_events.csv` or `natural_disaster_type_summary.csv` | Unique events |
| Frequency vs average impact scatter | `natural_disaster_events.csv` | Unique events × average per reported event |
| Total impact by type (with coverage) | `natural_disaster_type_summary.csv` | Sums + reported-value counts |
| Impact coverage strip | `natural_disaster_events.csv` | Reported events ÷ unique events |
| Yearly / decadal trend | `natural_disaster_events.csv` | Unique events by `Start Year` / `Decade` |
| Historical vs recent comparison | `natural_disaster_events.csv` | Derived `Start Year < 2000` flag |
| Filled map by country | `natural_country_year_type_summary.csv` | Country-grain reported sums (join on `ISO`) |
| Country leaderboard / region bars | `natural_country_year_type_summary.csv` | Country-grain sums + coverage |
| Country drill to event detail | `cleaned_natural_disaster_impacts.csv` | Event name, dates, location, GADM fields |

---

## 4. Known data limitations to state in the dashboard

1. Missing ≠ zero. Deaths missing in 27.8% of country impacts, affected 25.8%, adjusted damage
   67.6%, magnitude 68.8%; at event grain damage is missing for 66.6% of events.
2. Adjusted damage is in **million US$** (converted from EM-DAT's '000 US$). It is CPI-adjusted by
   EM-DAT; the base year is EM-DAT's, not recomputed here.
3. Coordinates exist for 15.8% of impacts and are **country-level**; do not plot them as
   subnational points and do not infer missing coordinates.
4. 1,067 events (6.8%) span multiple countries: count events, not country rows.
5. `Unique Events` in the country/year/type file sums to 18,060 and must not be used as a project
   total.
6. Magnitude is on hazard-specific scales (Km2, Kph, Moment Magnitude, °C, Vaccinated) — never
   compare across types. 13 impact rows report a literal magnitude of 0.
7. Pre-2000 records are historic and lower quality (7,137 impact rows / 6,710 events).
8. 2026 is a partial year (153 events; export dated 31 Oct 2026).
9. Data is country-level; district/admin-1 claims are not supported even where GADM fields exist.

---

## 5. Required dashboard filters and interactions

Mandatory on every page: year-range slider (1900–2026), disaster subgroup/type filter,
region/country filter, historic-period filter, coverage display next to every impact measure.

Required interactions: cross-filtering between charts, cross-highlighting where supported,
consistent filter pane across pages, clear reset control, titles with units, and a visible
missing-data statement. Full detail and DAX are in `docs/DASHBOARD_DATA_HANDOVER.md`, sections D–G.

---

## 6. Expected handover sequence: Shreya Patil → Shreya S Mattimadu

1. **Shreya Patil** builds the shared `.pbix`: loads all four CSVs, creates `DimType`,
   `DimCountry`, `DimYear`, `BridgeEventCountry`, the relationships in
   `DASHBOARD_DATA_HANDOVER.md` §G.2, and the core measures from §G.3.
2. Shreya Patil completes pages 1 (Overview), 2 (Frequency vs Destructiveness) and
   3 (Temporal) and confirms the measures reproduce the verified totals: 15,727 events,
   32,842,715 deaths, 9,065,006,097 affected, 8,120,533.17 million US$ damage, coverage
   74.1% / 78.6% / 33.4%.
3. Shreya Patil then hands the **same file** to Shreya S Mattimadu, together with the confirmed
   `DimCountry` definition (join map geometry on `ISO`) so both use one country dimension.
4. **Shreya S Mattimadu** adds the geographic page (map, country leaderboard, region/subregion
   comparison) inside that file, reusing the shared country dimension and date/type filters, and
   places it as page 4 of the integrated dashboard.
5. Both confirm cross-filtering in both directions (map → charts, charts → map) and that no page
   keeps a private, unsynchronised filter.
6. Do not create a second `.pbix` for geospatial work; the deliverable is one integrated
   dashboard.

---

## 7. What Shashank should validate

- Re-check the six findings in `docs/EDA_VALIDATION_REPORT.md` against his notebooks, especially
  the **reported-event denominator** for every average and the **total-vs-average** distinction
  (Drought leads averages and total deaths; Storm leads total damage while Earthquake leads average
  damage; Flood leads total affected).
- Confirm the median and coverage values that accompany each average, since they carry the
  heavy-tail caveat.
- Confirm the Spearman matrix (0.3496 / 0.2445 / 0.2327) and state in the report that only
  event-level pairwise-complete correlations were computed, with no significance testing.
- Confirm that no notebook output contradicts `analysis/outputs/eda_validation.json`; the current
  state is 89/89 committed values reproduced.
- Decide whether the 3 events with conflicting `Historic` flags should be excluded from any
  historic split (they are listed in the EDA report).

---

## 8. What remains outstanding, by owner

| Owner | Remaining work |
|---|---|
| **Samarth** | Nothing outstanding in the repository. Optional: install `openpyxl` (already in `requirements.txt`) so the source-workbook checks run instead of skipping. |
| **Shashank** | Validation listed in §7; final written findings narrative for the report/deck. |
| **Shreya Patil** | Build and integrate dashboard pages 1–3; enforce the measures/filters in §5; embed the limitations text from §4. |
| **Shreya S Mattimadu** | Build page 4 geospatial component inside the shared `.pbix`; join geometry on `ISO`; respect the country-level limitation. |
| **Team** | Resolve the unit/scope discrepancy recorded in `docs/DATA_HANDOVER.md` (approval deck says Unit 1 + Unit 3; the current allocation describes Unit 2 geospatial). No teacher feedback document was available to resolve it. |

---

## 9. Final integration and QA checklist

Repository/data (done this run unless noted):

- [x] All four processed CSVs exist, are readable, and match documented row counts.
- [x] Schemas contain every required column.
- [x] `Event ID` unique in the event file; `DisNo.` unique in the impact file.
- [x] Event/type/country-year-type totals reconcile exactly with country-impact totals.
- [x] Missing values preserved as blanks; no zero-filled impact columns.
- [x] Damage unit conversion verified row by row.
- [x] Documented statistics and headline findings independently reproduced.
- [x] Source workbook unmodified (SHA-256 recorded in `data_quality_report.json`).
- [ ] `.pbix` exists and opens (dashboard team).
- [ ] Measures reproduce the verified totals in Power BI (dashboard team).
- [ ] All four pages present in one file with shared filters (dashboard team).
- [ ] Map joins on `ISO` without unmatched rows (geospatial owner).
- [ ] Missing-data disclaimer visible on every impact page (dashboard team).
- [ ] Final screenshot/review pass before submission (team).

## 10. Reproduce the verification

```bash
python -m pip install -r requirements.txt
python scripts/validate_project_data.py      # exit 0 = no failed check
python scripts/verify_eda_findings.py        # exit 0 = committed findings reproduce
```

Both scripts are read-only with respect to the datasets: they write only their own JSON/Markdown
reports.
