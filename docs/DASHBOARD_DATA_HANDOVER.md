# Dashboard Data Handover — When Nature Strikes

Practical guide for Shreya Patil (analytical dashboard) and Shreya S Mattimadu (geospatial
component), written by Samarth Ramesha as part of the data/integration role.

Every number and column name below was verified against the committed CSV files by
`scripts/validate_project_data.py` (see `docs/DATA_QUALITY_REPORT.md`) and
`scripts/verify_eda_findings.py` (see `docs/EDA_VALIDATION_REPORT.md`). Nothing here is
inferred from memory. This document complements `docs/DATA_HANDOVER.md` (derivations and
caveats) — read that first if you need the *why*; this one is the *what to build*.

---

## A. Which dataset to use for what

| Visual need | Use this file | Grain of one row | Why |
|---|---|---|---|
| Frequency vs destructiveness by disaster type | `data/processed/natural_disaster_events.csv` | One consolidated event (15,727 rows) | One row per event, so frequency and impact are counted once. This is the required basis for the research question. |
| Compact disaster-type overview / KPI cards | `data/processed/natural_disaster_type_summary.csv` | One disaster type (15 rows) | Pre-aggregated. Fast type-level cards and a ranked bar chart. |
| Country drill-down, event names, dates, GADM fields, coordinates | `data/processed/cleaned_natural_disaster_impacts.csv` | One EM-DAT **country impact** (18,060 rows) | Only this file carries `Country`, `ISO`, `Region`, `Subregion`, `Event Name`, `Location`, `Latitude`, `Longitude`, `Historic`, and the GADM fields. |
| Map + country/year time series | `data/processed/natural_country_year_type_summary.csv` | One **country × start year × disaster type** group (11,157 rows) | Already aggregated per country-year-type; ideal for filled maps, small multiples and country trend lines. |

Do not mix grains inside one visual. In particular, never put a measure from one file next to a
count from another unless the relationship model in section G is in place.

---

## B. Data grain — the single most important thing to get right

| Concept | Definition | Verified count |
|---|---|---|
| **Country-impact record** | One disaster event's impact *in one country*. `DisNo.` is unique; `Event ID` repeats across countries. | 18,060 |
| **Consolidated event** | One underlying disaster event, after merging its country impacts on `Event ID`. | 15,727 |
| **Disaster-type aggregate** | One row per `Disaster Type` with a distinct count of events. | 15 types |
| **Country/year/type aggregate** | One group per `ISO` + `Start Year` + `Disaster Type`. | 11,157 groups |

**Why country-impact rows overcount:** 1,067 events (6.8% of all events) affected more than one
country. Counting rows instead of events inflates total frequency by 14.8% (18,060 vs 15,727) and
changes individual type counts — Flood is 5,814 events but 6,217 country-impact rows.

Rules that follow from the grain:

1. Frequency = **distinct `Event ID`**, never `COUNTROWS()` of the impact table.
2. `Unique Events` in `natural_country_year_type_summary.csv` must **never be summed as a
   project total**. It sums to 18,060 because an event is repeated for every country-year-type
   group it touches. Only the type-summary `Unique Events` column is safely additive (it totals
   15,727, since each event has exactly one type).
3. Impact measures (`Total Deaths`, `Total Affected`, damage) *are* additive across country rows
   — they are country-level amounts that roll up to an event total. They are still **not**
   additive across time if a country is hit twice for the same population; label totals as
   "reported impact", not "unique people".

---

## C. Recommended metrics

Compute these on `natural_disaster_events.csv` unless stated otherwise.

| Metric | Definition | Purpose |
|---|---|---|
| Unique disaster events | Distinct `Event ID` | The frequency axis of the research question. |
| Total deaths | `SUM('Total Deaths')` — blanks ignored | Destructiveness (human, immediate). |
| Total affected | `SUM('Total Affected')` | Destructiveness (human, scale). |
| Adjusted economic damage (million US$) | `SUM('Total Damage, Adjusted (million US$)')` | Destructiveness (economic). |
| Reporting coverage | Reported events ÷ unique events, per measure | Mandatory honesty layer; damage coverage is only 33.4%. |
| Average impact per reported event | Total ÷ **reported** events | Fairer comparison between frequent and rare types. |
| Median impact per reported event | `MEDIAN()` of the measure | Guards against the heavy tails that drive every average. |

Verified totals on the event grain: **32,842,715** reported deaths,
**9,065,006,097** reported affected people, **8,120,533.17** million US$ reported adjusted
damage (≈ US$8.12 trillion). Coverage: deaths **11,655 events (74.1%)**, affected
**12,366 (78.6%)**, damage **5,251 (33.4%)**.

**Never** use `COALESCE`/`IFNULL`/`+0` on an impact column. Missing values are absent
measurements, not zeroes: 67.6% of country-impact rows have no adjusted damage. A total that
silently treats blanks as zero is wrong, and a "0 deaths" bar is a factual claim the data does
not support.

---

## D. Recommended dimensions and filters

| Dimension | Source column(s) | Notes |
|---|---|---|
| Year | `Start Year` (1900–2026) | Integer. 2026 is a partial year (153 events; export dated 31 Oct 2026) — mark it as partial in the subtitle. |
| Decade | `Decade` | Already derived (`floor(year/10)*10`). Verified on every row. |
| Disaster group | `Disaster Group` | Always `Natural` in the processed files. |
| Disaster subgroup | `Disaster Subgroup` | 6 values — Hydrological, Meteorological, Geophysical, Biological, Climatological, Extra-terrestrial (the last has 1 impact row). Verified: each `Disaster Type` maps to exactly one subgroup. |
| Disaster type | `Disaster Type` | 15 values — the approved type-level question. |
| Disaster subtype | `Disaster Subtype` | Drill-down only; sparse. |
| Country | `ISO`, `Country` | 230 ISO codes, 1:1 with country names (verified). |
| Region / Subregion | `Region`, `Subregion` | 5 regions, 17 subregions. Present only in the impact and country/year/type files — **not** in the event file. |
| Historic vs recent | derived: `Start Year < 2000` | Verified equivalent to EM-DAT's `Historic = Yes` (7,137 impact rows; zero disagreements). Prefer deriving it from the year so it works on the event grain too. |

Filters to expose on every page: year range, disaster subgroup/type, region/country, historic
period. `Associated Types` (4,510 rows) is a secondary tag list — it must not be used as a second
classification to count events again.

---

## E. Dashboard structure (one integrated dashboard, four pages)

1. **Disaster Overview** — headline KPI cards (15,727 events, 15 types, 1900–2026, the three
   impact totals and their coverage), a ranked bar of events by type, and a coverage strip.
   States the research question and data source on the page.
2. **Frequency vs Destructiveness** — the answer page. Scatter of unique events (x) against
   average deaths / average affected / average adjusted damage (y, switchable), plus a ranked
   bar of totals with coverage labels. Call out the finding explicitly: frequency ≠ destructive-
   ness. Flood is 37.0% of events; Drought leads average deaths and average affected; Earthquake
   leads average damage; Storm leads *total* damage.
3. **Temporal Analysis** — events per year (line) and per decade (bar), impact totals by decade
   with coverage overlay, and a Historic vs 2000-onward comparison. Note the 2000 peak (489
   events) and that early-century counts reflect reporting capacity.
4. **Geographic Analysis** — filled map of the selected impact measure by country, a country
   leaderboard, and region/subregion comparison. Keep the geospatial drill/zoom work in this
   page as one component of the shared dashboard, not a separate report file.

Each page carries a footer: source (EM-DAT, CRED/UCLouvain, version 2026-10-23), measure
definition, unit, and the relevant missing-data note.

---

## F. Interaction requirements

- **Year-range slider** on the year dimension; default full range 1900–2026, with a one-click
  "2000 onwards" bookmark.
- **Disaster type / subgroup filters** — keep them hierarchical (subgroup filter narrows the type
  list) and synchronised across pages.
- **Country / region filters** — region and subregion must filter the country list; use the same
  country dimension on every page.
- **Cross-filtering between charts** — clicking a bar filters the other visuals on the page;
  clicking the same bar again clears it.
- **Cross-highlighting** where supported (Power BI default for bar/scatter) — do not disable it,
  but do not rely on highlight values being comparable to filtered totals.
- **Consistent filter behaviour** — a single dedicated filter pane or identical slicer layout;
  avoid page-local filters that silently persist.
- **Clear titles, units, and missing-data explanations** — every impact visual states
  "reported" and its unit; every impact visual shows the reported-event count or coverage %.
- **Reset / clear-all** control and a visible "current filters" text box on the answer page.

---

## G. Power BI implementation guidance

### G.1 Load and shape

Load all four CSVs (UTF-8 with BOM). In Power Query:

- Set `Start Year`, `Decade`, `Country Count`, `Country Impact Records`, `Unique Events` and all
  impact columns to **Whole Number / Decimal Number**. Blank cells must stay *null*, not 0 —
  do not use "Replace Values" on empty cells.
- Keep `ISO`, `Country`, `Region`, `Subregion`, `Disaster Type`, `Disaster Subgroup` as text with
  no trimming surprises.
- Add one derived column on the event table for the period flag (used by every page):

```dax
Period = IF ( 'FactEvents'[Start Year] < 2000, "Historic (pre-2000)", "2000 onwards" )
```

### G.2 Recommended model

```text
DimType  (1) ──< FactEvents >── (1) DimYear
                    │
                    └──< BridgeEventCountry >── (1) DimCountry
                                                   │
DimType (1) ──< FactCountryYearType >──────────────┘
                    └── (1) DimYear

FactTypeSummary   (disconnected: already aggregated per type — never relate or filter it)
```

- `DimType`: `Disaster Type`, `Disaster Subgroup` (one row per type; verified 1:1).
- `DimCountry`: `ISO`, `Country`, `Region`, `Subregion` (230 rows; verified 1:1).
- `DimYear`: `Start Year`, `Decade` (1900–2026). Build this from distinct `Start Year` rather than
  from `Start Date`: 3,185 events have no complete start date and would be silently dropped by a
  date relationship.
- `BridgeEventCountry`: distinct `Event ID`, `ISO` from the impact file. Relationship
  `FactEvents[Event ID] → Bridge[Event ID]` and `DimCountry[ISO] → Bridge[ISO]`, single-direction
  filters from dimensions to facts. This is what makes region/country slicers filter event-level
  frequency correctly.
- `FactCountryYearType` serves pages 3–4 where a country grain is required. It duplicates event
  impacts by design; use it only with country-grain measures, and never sum its `Unique Events`
  as a project total.

### G.3 Measures (column names verified against the CSVs)

```dax
Unique Events = DISTINCTCOUNT ( 'FactEvents'[Event ID] )

Total Deaths = SUM ( 'FactEvents'[Total Deaths] )
Deaths Reported Events = COUNT ( 'FactEvents'[Total Deaths] )
Death Coverage % = DIVIDE ( [Deaths Reported Events], [Unique Events] )
Average Deaths per Reported Event = DIVIDE ( [Total Deaths], [Deaths Reported Events] )
Median Deaths per Reported Event = MEDIAN ( 'FactEvents'[Total Deaths] )

Total Affected = SUM ( 'FactEvents'[Total Affected] )
Affected Reported Events = COUNT ( 'FactEvents'[Total Affected] )
Affected Coverage % = DIVIDE ( [Affected Reported Events], [Unique Events] )
Average Affected per Reported Event = DIVIDE ( [Total Affected], [Affected Reported Events] )
Median Affected per Reported Event = MEDIAN ( 'FactEvents'[Total Affected] )

Total Adjusted Damage (million US$) = SUM ( 'FactEvents'[Total Damage, Adjusted (million US$)] )
Damage Reported Events = COUNT ( 'FactEvents'[Total Damage, Adjusted (million US$)] )
Damage Coverage % = DIVIDE ( [Damage Reported Events], [Unique Events] )
Average Adjusted Damage per Reported Event =
    DIVIDE ( [Total Adjusted Damage (million US$)], [Damage Reported Events] )
Median Adjusted Damage per Reported Event =
    MEDIAN ( 'FactEvents'[Total Damage, Adjusted (million US$)] )

Multi-Country Events = CALCULATE ( [Unique Events], 'FactEvents'[Country Count] > 1 )
```

Country-grain measures (page 4), only from `FactCountryYearType`:

```dax
Country Impact Records = SUM ( 'FactCountryYearType'[Country Impact Records] )
Country Deaths = SUM ( 'FactCountryYearType'[Total Deaths] )
Country Death Coverage % =
    DIVIDE (
        SUM ( 'FactCountryYearType'[Total Deaths Reported Records] ),
        [Country Impact Records]
    )
Events Impacting Selected Countries = DISTINCTCOUNT ( 'FactEvents'[Event ID] )
```

`Events Impacting Selected Countries` is the honest country-scoped frequency: the country
dimension filters the bridge, which filters `FactEvents`, so an event touching two selected
countries is counted once. Do **not** replace it with `SUM('FactCountryYearType'[Unique Events])`
in a card.

### G.4 Aggregation choices and assumptions

- `Total Deaths` and `Total Affected` are whole-number sums of reported country values; they are
  additive. Damage is a decimal sum in million US$ and is a unit conversion of EM-DAT's
  CPI-adjusted damage — label the base and unit once on the page.
- Averages use **reported events** as the denominator, matching the notebooks and
  `docs/EDA_VALIDATION_REPORT.md`. Using all events as the denominator would change the ranking
  and imply that unreported events had no impact.
- `MEDIAN()` in Power BI ignores blanks automatically; it is the recommended companion to every
  average because Drought's mean deaths (175,140) sit far above its median (200).
- No measure converts blank to zero. If a stakeholder wants a zero-based chart, that requires a
  separate, explicitly named measure and a visible disclaimer.
- Filtering by `Disaster Type` on `DimType` keeps event measures correct because each event has
  exactly one type. Do not add `Associated Types` to the same dimension — it is a multi-value tag.

---

## Role boundaries

This document is data guidance, not dashboard implementation. Shreya Patil owns the `.pbix`
analytical pages; Shreya S Mattimadu owns the geospatial page and its integration into the same
file. Samarth's role stops at prepared data, validation, and this handover. I have not opened,
edited, or regenerated the `.pbix`.
