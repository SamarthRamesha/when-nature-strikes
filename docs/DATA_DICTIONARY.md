# Data Dictionary — When Nature Strikes

Column-level reference for the four processed datasets in `data/processed/`. Written by Samarth
Ramesha to close the "data dictionary" part of the data/preparation role.

Every column below is listed once, with its **position in the CSV**, its **origin** (EM-DAT export or
derived by `scripts/prepare_emdat.py`), type, unit/domain, and the observed nonblank count and rate in
the committed file. Counts were computed from the CSVs themselves on 11 November 2026 and are
re-checked by `scripts/validate_project_data.py`. If the workbook changes, the counts change; the
definitions do not.

Read this together with:

- `docs/DATA_HANDOVER.md` — why the derivations exist, caveats, recommended use.
- `docs/DASHBOARD_DATA_HANDOVER.md` — which file for which visual, measures, DAX.
- `docs/DATA_QUALITY_REPORT.md` — the checks that hold these definitions true.

**Missing values.** A blank cell means *not reported* or *not known*. It is never a zero and must never
be filled with zero. Check `M-no-zero-fill` proves that the three main impact measures contain no zeros
at all in the impact file (their minimum reported value is 1).

---

## 1. `cleaned_natural_disaster_impacts.csv` — one EM-DAT country impact per row

18,060 rows × 53 columns. Grain: one disaster event's impact in one country. Uniqueness: `DisNo.`
(18,060 distinct) and (`Event ID`, `ISO`) — no duplicate pairs (checks `I-disno-unique`,
`I-event-country-unique`).

Column positions are the real header order; the sections group them for reading.

### 1.1 Identification and classification — positions 1–7

| # | Column | Origin | Type | Domain / unit | Nonblank | Notes |
|---|---|---|---|---|---|---|
| 1 | `DisNo.` | EM-DAT | text | `<year>-<seq>-<ISO3>`, e.g. `1987-0326-JAM` | 18,060 (100%) | Primary key, unique per row. Basis of the derived `Event ID`. |
| 2 | `Historic` | EM-DAT | text | `Yes` / `No` | 18,060 (100%) | EM-DAT quality flag: `Yes` 7,137 (39.5%), `No` 10,923. Equivalent to `Start Year < 2000` on every row, but three events carry conflicting flags across their own rows — prefer the year (§5.4). |
| 3 | `Classification Key` | EM-DAT | text | 50 codes, e.g. `nat-hyd-flo-riv` | 18,060 (100%) | EM-DAT's hierarchical hazard code, mirroring the group/subgroup/type/subtype chain. Group with the named columns instead. |
| 4 | `Disaster Group` | EM-DAT | text | `Natural` only | 18,060 (100%) | The pipeline filter. 9,902 `Technological` source rows were excluded, not reclassified. |
| 5 | `Disaster Subgroup` | EM-DAT | text | 6 values | 18,060 (100%) | Hydrological 7,093; Meteorological 6,004; Geophysical 1,994; Biological 1,624; Climatological 1,344; Extra-terrestrial 1. Each `Disaster Type` maps to exactly one subgroup (verified). |
| 6 | `Disaster Type` | EM-DAT | text | 15 values | 18,060 (100%) | The approved type-level dimension. Flood 5,814 events … Animal incident 1; see `DATA_QUALITY_REPORT.md` §3. |
| 7 | `Disaster Subtype` | EM-DAT | text | 50 values, e.g. `Riverine flood` | 18,060 (100%) | Drill-down only. |

### 1.2 Event identity and geography — positions 8–15

| # | Column | Origin | Type | Domain / unit | Nonblank | Notes |
|---|---|---|---|---|---|---|
| 8 | `External IDs` | EM-DAT | text | 3,407 distinct, e.g. `GLIDE:EQ-2025-000153` | 4,643 (25.7%) | Cross-database identifiers. Not used for joins here. |
| 9 | `Event Name` | EM-DAT | text | 1,903 distinct | 4,507 (25.0%) | Named events only ("Typhoon 'Nina'"). Display label, never a key. |
| 10 | `ISO` | EM-DAT | text | ISO-3, 230 codes | 18,060 (100%) | Join key for map geometry. Strictly 1:1 with `Country` (verified). |
| 11 | `Country` | EM-DAT | text | 230 values | 18,060 (100%) | Country of this impact. Repeats across an event only when the event spans countries. |
| 12 | `Subregion` | EM-DAT | text | 17 values | 18,060 (100%) | EM-DAT subregion, e.g. `Latin America and the Caribbean`. Hierarchy: region → subregion → country. |
| 13 | `Region` | EM-DAT | text | 5 values: Africa, Americas, Asia, Europe, Oceania | 18,060 (100%) | |
| 14 | `Location` | EM-DAT | text | 14,516 distinct free text | 16,091 (89.1%) | Place description, not a geometry. |
| 15 | `Origin` | EM-DAT | text | 821 distinct | 4,778 (26.5%) | Named storm/weather system origin, where reported. |

`Region`/`Subregion` exist only here and in the country-year-type file — **not** in the event file, so
region slicers must reach events through the country bridge.

### 1.3 Event attributes, response metadata and aid — positions 16–20

| # | Column | Origin | Type | Domain / unit | Nonblank | Notes |
|---|---|---|---|---|---|---|
| 16 | `Associated Types` | EM-DAT | text | 149 distinct, multi-value | 4,510 (25.0%) | Secondary hazard tags ("Slide (land, mud, snow, rock)"). **Never** a second classification to count events. |
| 17 | `OFDA/BHA Response` | EM-DAT | text | `Yes` / `No` | 18,060 (100%) | Whether US OFDA/BHA responded. Response metadata, not impact. |
| 18 | `Appeal` | EM-DAT | text | `Yes` / `No` | 18,060 (100%) | Whether an international appeal was launched. |
| 19 | `Declaration` | EM-DAT | text | `Yes` / `No` | 18,060 (100%) | Whether a state of emergency was declared. |
| 20 | `AID Contribution ('000 US$)` | EM-DAT | number | thousand US$ | 776 (4.3%) | Aid received, not damage. 95.7% blank; range 1–3,518,530. |

### 1.4 Hazard magnitude, coordinates and river basin — positions 21–25

| # | Column | Origin | Type | Domain / unit | Nonblank | Notes |
|---|---|---|---|---|---|---|
| 21 | `Magnitude` | EM-DAT | number | hazard-specific; −57 to 13,025,900 | 5,638 (31.2%) | **Never compare or sum across types.** 13 rows report a literal 0; 133 report a negative value. |
| 22 | `Magnitude Scale` | EM-DAT | text | `Km2` 7,553; `Kph` 5,234; `Moment Magnitude` 1,664; `°C` 769; `Vaccinated` 730 | 15,950 (88.3%) | Unit of `Magnitude` for that row. Present for more rows than `Magnitude` itself, so it is not a proxy for a reported magnitude. |
| 23 | `Latitude` | EM-DAT | number | decimal degrees, −72.64 to 67.93 | 2,847 (15.8%) | Country-level point, not a subnational impact location. Present only as a pair with longitude (0 half-pairs). Do not infer missing coordinates. |
| 24 | `Longitude` | EM-DAT | number | decimal degrees, −178.252 to 179.65 | 2,847 (15.8%) | As above. |
| 25 | `River Basin` | EM-DAT | text | 1,525 distinct, e.g. `Kosi river` | 1,613 (8.9%) | Free-text basin name for hydrological events. 91.1% blank; not used in any analysis. |

### 1.5 Dates — source positions 26–31

Derived date columns sit at positions 49–51 and are documented in §1.8.

| # | Column | Origin | Type | Domain / unit | Nonblank | Notes |
|---|---|---|---|---|---|---|
| 26 | `Start Year` | EM-DAT | integer | 1900–2026 | 18,060 (100%) | The only complete date component. Drives `Decade`, the historic split and all year filtering. |
| 27 | `Start Month` | EM-DAT | integer | 1–12 | 17,689 (98.0%) | Blank = month unknown in the source. |
| 28 | `Start Day` | EM-DAT | integer | 1–31 | 14,448 (80.0%) | Blank = day unknown. |
| 29 | `End Year` | EM-DAT | integer | 1900–2026 | 18,060 (100%) | |
| 30 | `End Month` | EM-DAT | integer | 1–12 | 17,393 (96.3%) | |
| 31 | `End Day` | EM-DAT | integer | 1–31 | 14,554 (80.6%) | |

20.0% of impact rows (3,612) have no complete start date, which is why a date relationship on the
event file silently loses 3,185 events.

### 1.6 Human impact measures — positions 32–36

| # | Column | Origin | Type | Unit | Nonblank | Notes |
|---|---|---|---|---|---|---|
| 32 | `Total Deaths` | EM-DAT | number | persons | 13,031 (72.2%) | 27.8% blank; minimum reported value is 1 (never zero-filled). Total 32,842,715 across all four files. |
| 33 | `No. Injured` | EM-DAT | number | persons | 4,783 (26.5%) | 73.5% blank. Component of `Total Affected`. |
| 34 | `No. Affected` | EM-DAT | number | persons | 10,746 (59.5%) | 40.5% blank. Component of `Total Affected`. |
| 35 | `No. Homeless` | EM-DAT | number | persons | 2,624 (14.5%) | 85.5% blank. Component of `Total Affected`. |
| 36 | `Total Affected` | EM-DAT | number | persons | 13,405 (74.2%) | 25.8% blank. EM-DAT's own sum of injured + affected + homeless; use it rather than re-deriving from the components, whose blanks differ. Total 9,065,006,097. |

### 1.7 Economic measures — positions 37–43

| # | Column | Origin | Type | Unit | Nonblank | Notes |
|---|---|---|---|---|---|---|
| 37 | `Reconstruction Costs ('000 US$)` | EM-DAT | number | thousand US$ | 43 (0.2%) | 99.8% blank — unusable for analysis. |
| 38 | `Reconstruction Costs, Adjusted ('000 US$)` | EM-DAT | number | thousand US$, CPI-adjusted | 42 (0.2%) | As above. |
| 39 | `Insured Damage ('000 US$)` | EM-DAT | number | thousand US$ | 1,144 (6.3%) | Insured share only; EM-DAT documents loss underreporting where insurance is limited. |
| 40 | `Insured Damage, Adjusted ('000 US$)` | EM-DAT | number | thousand US$, CPI-adjusted | 1,141 (6.3%) | As above. |
| 41 | `Total Damage ('000 US$)` | EM-DAT | number | thousand US$, **nominal** | 5,885 (32.6%) | Nominal damage. Never mix with the adjusted column in one chart. |
| 42 | `Total Damage, Adjusted ('000 US$)` | EM-DAT | number | thousand US$ | 5,850 (32.4%) | 67.6% blank. EM-DAT's CPI-adjusted damage; source of the million-US$ column. |
| 43 | `CPI` | EM-DAT | number | index, 2.584225–100 | 17,883 (99.0%) | EM-DAT's price-index factor behind the adjustment. Not an impact measure: do not sum or average it as one. |

`Total Damage, Adjusted (million US$)` is at position 53 (§1.8).

### 1.8 Administrative, audit and derived columns — positions 44–53

| # | Column | Origin | Type | Domain | Nonblank | Notes |
|---|---|---|---|---|---|---|
| 44 | `Admin Units` | EM-DAT | text (JSON) | 6,876 distinct | 8,363 (46.3%) | Admin-unit codes as a JSON array; not a geometry table. |
| 45 | `GADM Admin Units` | EM-DAT | text (JSON) | 6,457 distinct, e.g. `[{"gid_2":"PHL.17.13_1",…}]` | 7,832 (43.4%) | GADM identifiers as JSON. Their presence does not make the impact subnational — EM-DAT records impacts at country level. |
| 46 | `Entry Date` | EM-DAT | text (date) | 2,537 distinct | 18,060 (100%) | When the record entered EM-DAT. Audit only. |
| 47 | `Last Update` | EM-DAT | text (date) | 376 distinct | 18,060 (100%) | Last EM-DAT revision; useful for data vintage (export 31 Oct 2026). |
| 48 | `Event ID` | **derived** | text | 15,727 distinct, e.g. `1987-0326` | 18,060 (100%) | Year-sequence portion of `DisNo.` with the ISO-3 suffix removed. Reconnects one event's country impacts; repeats across countries (1,067 events have more than one row). |
| 49 | `Start Date` | **derived** | text | ISO `YYYY-MM-DD` | 14,448 (80.0%) | Populated only when year, month and day form a valid calendar date; otherwise blank. Partial dates are not imputed. |
| 50 | `End Date` | **derived** | text | ISO `YYYY-MM-DD` | 14,554 (80.6%) | Same rule as `Start Date`. |
| 51 | `Decade` | **derived** | integer | 1900–2020 | 18,060 (100%) | `floor(Start Year / 10) * 10`. Verified on every row. |
| 52 | `Has Coordinates` | **derived** | text | `Yes` 2,847 / `No` 15,213 | 18,060 (100%) | `Yes` only when both latitude and longitude are present. Never inferred from country names. |
| 53 | `Total Damage, Adjusted (million US$)` | **derived** | number | **million US$** | 5,850 (32.4%) | `Total Damage, Adjusted ('000 US$) / 1000`. Unit conversion only — it does not estimate missing damage. Verified row by row (max deviation 0.0). Total 8,120,533.174 million US$ (≈ US$8.12 trillion). |

**Derived columns total: 6** — `Event ID` (48), `Start Date` (49), `End Date` (50), `Decade` (51),
`Has Coordinates` (52), `Total Damage, Adjusted (million US$)` (53). Everything else is an unmodified
EM-DAT public-table field.

---

## 2. `natural_disaster_events.csv` — one consolidated event per row

15,727 rows × 35 columns. Grain: one underlying disaster event, built by grouping the country impacts
on `Event ID`, which is unique here (check `E-unique`).

### 2.1 Carried event attributes — positions 1–15

`Event ID`, `Disaster Group`, `Disaster Subgroup`, `Disaster Type`, `Disaster Subtype`,
`Classification Key`, `Start Year`, `Start Month`, `Start Day`, `Start Date`, `End Year`,
`End Month`, `End Day`, `End Date`, `Decade`.

Taken from the event's first country row. Safe because each event has exactly one type, subtype and
classification (verified: `E-type`), and start dates agree across an event's rows. Date completeness is
lower than at impact grain: `Start Date` is present for 12,542 events (79.7%) and `End Day` for 12,638.

### 2.2 Country roll-up — positions 16–19

| Column | Type | Range | Notes |
|---|---|---|---|
| `Country Count` | integer | 1–35 | Distinct ISO codes in the event; `> 1` for 1,067 events (6.8%). |
| `Countries` | text | 807 distinct | Country names joined with ` \| `, sorted. Display only. |
| `ISO Codes` | text | 807 distinct | ISO-3 codes joined with ` \| `, sorted. Display only — use the bridge table in Power BI, not this string. |
| `Country Impact Records` | integer | 1–35 | Country-impact rows consolidated into this event. Equals `Country Count` here because one row per (event, ISO) is enforced. |

### 2.3 Impact measures and coverage counters — positions 20–35

Each measure is the **sum of the reported country values** for that event, and is blank when every
country impact for it is blank — never 0 (verified: `E-blank-propagation`). Each is paired with a
counter of how many country impacts contributed.

| Measure | Unit | Reported events | Blank | Coverage | Counter range |
|---|---|---|---|---|---|
| `Total Deaths` | persons | 11,655 | 25.9% | 74.1% | `Total Deaths Reported Country Impacts` 0–34 |
| `No. Injured` | persons | 4,559 | 71.0% | 29.0% | `No. Injured Reported Country Impacts` 0–6 |
| `No. Affected` | persons | 9,965 | 36.6% | 63.4% | `No. Affected Reported Country Impacts` 0–9 |
| `No. Homeless` | persons | 2,575 | 83.6% | 16.4% | `No. Homeless Reported Country Impacts` 0–6 |
| `Total Affected` | persons | 12,366 | 21.4% | 78.6% | `Total Affected Reported Country Impacts` 0–9 |
| `Total Damage, Adjusted ('000 US$)` | thousand US$ | 5,251 | 66.6% | 33.4% | `Total Damage, Adjusted ('000 US$) Reported Country Impacts` 0–13 |
| `Total Damage, Adjusted (million US$)` | million US$ | 5,251 | 66.6% | 33.4% | `Total Damage, Adjusted (million US$) Reported Country Impacts` 0–13 |
| `Magnitude` | hazard-specific | 5,129 | 67.4% | 32.6% | `Magnitude Reported Country Impacts` 0–28 |

Summing a counter across all events reproduces the impact-grain reported count for that measure (the
deaths counters sum to the 13,031 impact rows with reported deaths). The counters are the denominator
for every "average per reported event" figure — never `Unique Events`.

`Magnitude` at this grain sums numbers that are not on one scale (−370 to 13,025,900). It exists for
completeness; do not analyse it.

---

## 3. `natural_disaster_type_summary.csv` — one row per disaster type

15 rows × 19 columns.

| Column group | Columns | Notes |
|---|---|---|
| Dimension (1–2) | `Disaster Group`, `Disaster Type` | `Disaster Group` is always `Natural`. |
| Frequency (3) | `Unique Events` | Distinct `Event ID` per type (1–5,814). **Additive**: sums to 15,727 because each event has exactly one type. |
| Measures (4–18, every second column) | `Total Deaths`, `No. Injured`, `No. Affected`, `No. Homeless`, `Total Affected`, `Total Damage, Adjusted ('000 US$)`, `Total Damage, Adjusted (million US$)`, `Magnitude` | Sum of the event-level values for that type. |
| Coverage counters (5–19, every second column) | `<measure> Events with Reported Values` | Events of that type that reported the measure; the average denominator. |

Types with no reported value for a measure have a blank measure, not 0: `Total Deaths` is blank for 2
of 15 types, `No. Injured` for 3, `No. Homeless` for 6, `Magnitude` for 8.

Averages are `measure ÷ <measure> Events with Reported Values`, never `÷ Unique Events`.

---

## 4. `natural_country_year_type_summary.csv` — one row per country × year × type

11,157 rows × 25 columns. Grain verified unique (check `Y-grain`).

| Column group | Columns | Notes |
|---|---|---|
| Dimensions (1–7) | `ISO`, `Country`, `Region`, `Subregion`, `Start Year`, `Decade`, `Disaster Type` | Map and trend dimensions. Region/subregion are available here, unlike the event file. |
| Counts (8–9) | `Country Impact Records` (1–27), `Unique Events` (1–27) | Distinct `Event ID` within the group. |
| Measures (10–23, every second column) | The same eight measures as §3 | Sum of the group's country-impact values. |
| Coverage counters (11–25, every second column) | `<measure> Reported Records` | Country impacts in the group that reported the measure. |

**`Unique Events` here is NOT additive.** It sums to 18,060 because an event repeats for every
country-year-type group it touches (warning `Y-double-count`). Never place it in a project-total card;
only the type-summary `Unique Events` column is additive. Country-grain coverage uses
`Reported Records ÷ Country Impact Records` — see `DASHBOARD_DATA_HANDOVER.md` §G.3.

---

## 5. Cross-file rules

### 5.1 Which columns may be summed

| Safe to sum | Not safe to sum | Reason |
|---|---|---|
| Impact measures in any file (deaths, injured, affected, homeless, total affected, adjusted damage) | `Magnitude` | Hazard-specific scales; 13 zeros and 133 negative values in the impact file. |
| `Unique Events` in the **type** summary | `Unique Events` in the **country-year-type** summary | The latter repeats events per country (sums to 18,060). |
| Coverage counters (count of reporting units) | `Country Impact Records` used as a frequency | It counts country rows (18,060), not events (15,727). |
| `Country Impact Records` when counting rows | `CPI`, `Event ID`, `ISO`, `Decade` and other identifiers/attributes | Not additive quantities. |

### 5.2 Grain arithmetic

- 18,060 country impacts → 15,727 events. The gap is the 1,067 multi-country events; row counting
  inflates frequency by 14.8%.
- 18,060 impacts → 11,157 country-year-type groups (an event repeats per country and year).
- 15,727 events → 15 types, and the type summary's `Unique Events` sums back to 15,727.

### 5.3 Units

| Quantity | Unit | Note |
|---|---|---|
| Deaths, injured, affected, homeless, total affected | persons | Not deduplicated across events — the same people can be counted in successive events. |
| `Total Damage` and all `… ('000 US$)` columns | thousand US$ | Nominal unless the column says `Adjusted`. |
| `Total Damage, Adjusted (million US$)` | million US$ | = adjusted '000 US$ ÷ 1,000. 8,120,533 million ≈ **8.12 trillion** US$. |
| `AID Contribution`, `Reconstruction Costs`, `Insured Damage` | thousand US$ | Separate concepts from `Total Damage`; never add them to it. |
| `Magnitude` | `Km2`, `Kph`, `Moment Magnitude`, `°C`, `Vaccinated` | Per `Magnitude Scale`; incomparable across types. |
| Coordinates | decimal degrees | Country-level point. |
| `CPI` | index | EM-DAT's adjustment factor, not a measure. |

### 5.4 Known data nuances that affect use

1. **Three events have conflicting `Historic` flags** across their own country rows:
   `1988-0424`, `1995-0275`, `1999-9388`. Derive the historic split from `Start Year < 2000`
   (`Historic = Yes` ⟺ `Start Year < 2000` for all 7,137 flagged rows).
2. **2026 is a partial year** — 153 events, export dated 31 October 2026. Any 2026 bar is incomplete by
   construction; mark it or exclude it.
3. **3,185 events (20.3%) have no complete start date.** They must not be dropped by a date
   relationship; build the year dimension from `Start Year`.
4. **13 impact rows report `Magnitude = 0`** and 133 report a negative magnitude — reported values on
   hazard-specific scales, not missing data (warning `M-magnitude-zeros`).
5. **Blanks are concentrated**: adjusted damage is missing for 67.6% of impacts, so every damage
   conclusion is about *reported* damage only.

---

## 6. Reproducing the counts in this dictionary

```bash
python - <<'PY'
import csv
for name in ['cleaned_natural_disaster_impacts','natural_disaster_events',
             'natural_disaster_type_summary','natural_country_year_type_summary']:
    rows = list(csv.DictReader(open(f'data/processed/{name}.csv', encoding='utf-8-sig', newline='')))
    print(f'\n## {name}  n={len(rows)}')
    for i, col in enumerate(rows[0], 1):
        vals = [r[col] for r in rows]
        filled = [v for v in vals if v != '']
        print(f'{i:2d}. {col}: nonblank={len(filled)} blank={len(vals)-len(filled)} '
              f'distinct={len(set(filled))}')
PY
```

Structural guarantees (grain, uniqueness, reconciliation, blank-vs-zero) are covered by
`python scripts/validate_project_data.py`; a passing run means this dictionary still describes the
files.
