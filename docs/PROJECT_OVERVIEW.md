# Project Overview — When Nature Strikes

A single reference for **what this project is, why it exists, how it was built and what it
deliberately does not claim**. It is the document to read when you have the repository but not the
conversation. It does not replace the data-level detail in `DATA_HANDOVER.md`,
`DATA_DICTIONARY.md` and `DASHBOARD_DATA_HANDOVER.md`; it orients you before you open them.

| | |
|---|---|
| **Title** | When Nature Strikes: A Visualization Approach to Determine the Impact of Natural Disasters |
| **Research question** | Are the most frequent natural disasters also the most destructive? |
| **Domain** | Data visualization / exploratory data analysis of disaster impact |
| **Data** | EM-DAT public custom-request export, CRED / UCLouvain, table version 2026-10-23, file dated 31 October 2026 |
| **Deliverable** | One integrated, interactive Power BI dashboard with four pages, plus the analytical report and presentation |
| **Repository** | https://github.com/SamarthRamesha/when-nature-strikes |
| **Phase status (11 Nov 2026)** | Data phase complete and verified; dashboard, geospatial page and submission assembly pending with their owners |

---

## 1. Problem statement

Disaster discourse tends to rank hazards by how often they occur. Policy attention, however, follows
destruction: deaths, people affected, economic loss. Those two rankings are not the same, and the
difference matters — a type that occurs rarely can dominate casualties while the most frequent type
dominates total damage.

Making that comparison responsibly requires three things that a naive chart gets wrong:

1. **The right grain.** EM-DAT's public table stores one row per *country impact*, not per event.
   Counting rows inflates frequency by 14.8% (18,060 rows vs 15,727 events) because 1,067 events span
   more than one country.
2. **Honest denominators.** Impact fields are frequently unreported. Adjusted damage is missing for
   67.6% of country impacts; a "zero damage" bar would be a factual claim the data cannot support.
   Averages must be per *reported* event, with coverage shown beside them.
3. **Comparable measures.** `Magnitude` is recorded on five different scales (km², kph, moment
   magnitude, °C, vaccinated people) and cannot be compared across hazard types; mortality and damage
   are separate constructs that must not be collapsed into one "destructiveness" number without
   saying which one is being ranked.

The project's contribution is a defensible answer to the research question, delivered as an
interactive dashboard that always shows how much of the data is actually reported.

## 2. Objectives

| # | Objective | Where it is evidenced |
|---|---|---|
| O1 | Build reproducible, validated datasets at four grains from the raw EM-DAT export | `scripts/prepare_emdat.py`, `data/processed/`, `docs/DATA_DICTIONARY.md` |
| O2 | Verify the data before anyone analyses it | `scripts/validate_project_data.py` (71 checks), `docs/DATA_QUALITY_REPORT.md` |
| O3 | Quantify frequency versus destructiveness with stated denominators | `docs/EDA_VALIDATION_REPORT.md`, `scripts/verify_eda_findings.py` |
| O4 | Specify and build one integrated four-page Power BI dashboard | `docs/DASHBOARD_DATA_HANDOVER.md` (specification); **build pending** |
| O5 | Make every limitation visible in the report and on the dashboard | `docs/DATA_HANDOVER.md`, `README.md` §Academic limitations |
| O6 | Hand the project over so a new owner can continue without prior conversations | `docs/TEAM_HANDOVER.md`, `docs/AI_AGENT_HANDOVER_PROTOCOL.md`, `docs/NEXT_SESSION_PROMPT.md` |

## 3. Approved scope

From the approval presentation (summarised, identifiers removed, in `PROJECT_APPROVAL_SUMMARY.md`):

- **Title and question** as stated above.
- **Dataset:** EM-DAT, the International Disaster Database.
- **Scope:** historical natural disasters, including earthquakes, floods, cyclones/storms, wildfires,
  droughts and other natural hazard types.
- **Dimensions named:** disaster type, location, magnitude/severity, deaths and affected population,
  economic damage.
- **Visualization direction:** exploratory comparison of frequency against destructiveness, with an
  interactive dashboard.
- **Unit coverage written in the deck:** Unit 1 and Unit 3.

**Open discrepancy.** The current team allocation describes a **Unit 2** geospatial component, while
the deck names Unit 1 + Unit 3. No teacher feedback document was supplied to resolve this. It is
recorded in `DATA_HANDOVER.md` §Requirement provenance and remains a team decision before final
submission.

## 4. Data and provenance

| Item | Value |
|---|---|
| Source | EM-DAT, CRED / UCLouvain — public custom-request table |
| Version | 2026-10-23; request file created 31 October 2026 |
| Records in export | 27,962 |
| Natural-hazard country impacts | **18,060** (the processed population) |
| Technological impacts excluded | 9,902 (filtered out, not reclassified) |
| Period | 1900–2026 (2026 partial: 153 events) |
| Coverage | 230 countries, 17 subregions, 5 regions, 15 disaster types, 6 subgroups |
| Integrity | Workbook retained unmodified; SHA-256 recorded in `analysis/outputs/data_quality_report.json` |

Grain model built on that export:

```text
18,060 country impacts  ──(group by Event ID)──▶  15,727 events  ──(by type)──▶  15 type rows
        │
        └──(group by ISO × Start Year × Type)──▶  11,157 country-year-type rows
```

## 5. Method

1. **Extract** — read the workbook (`EM-DAT Data` sheet) with `openpyxl`, preserving every column.
2. **Filter** — keep `Disaster Group = Natural`; the 9,902 technological records are excluded and that
   exclusion is stated rather than hidden.
3. **Derive** — six fields only, each deterministic: `Event ID`, `Start Date`, `End Date`, `Decade`,
   `Has Coordinates`, `Total Damage, Adjusted (million US$)` (a unit conversion from EM-DAT's
   CPI-adjusted thousands). No value is imputed, capped or zero-filled.
4. **Consolidate** — sum reported values per `Event ID` for the event file, keeping a per-measure count
   of contributing country impacts so coverage is always recoverable. A measure stays blank when all
   its inputs are blank.
5. **Aggregate** — type-level and country-year-type summaries, with distinct-`Event ID` frequency and
   reported-value counters.
6. **Validate** — 71 executable checks over schemas, uniqueness, reconciliation, missingness, unit
   conversion and every statistic quoted in the documentation.
7. **Analyse (EDA)** — frequency, impact, temporal and pattern analysis in six notebooks by
   Shashank S K, producing 15 tables and 32 charts.
8. **Verify** — the headline findings recomputed independently: 89/89 committed values reproduce.
9. **Specify** — the Power BI model, measures and page structure handed to the dashboard team.

Every step above is reproducible from a clean clone with the commands in `README.md` §Reproduce the
project.

## 6. Deliverables map

| Deliverable | Owner | State |
|---|---|---|
| Reproducible preprocessing pipeline | Samarth | Complete, byte-identical rebuild verified |
| Four processed datasets | Samarth | Complete |
| Data dictionary (all 132 columns) | Samarth | Complete |
| Data-quality validation (71 checks) | Samarth | Complete, exit 0 |
| EDA notebooks, 15 tables, 32 charts | Shashank | Delivered |
| Findings verification (F1–F7) | Samarth | Complete, 89/89 values |
| Power BI data handover specification | Samarth | Complete |
| Integration and ownership documentation | Samarth | Complete |
| Main analytical dashboard (pages 1–3) | Shreya Patil | **Not started** |
| Geospatial page (page 4) in the same file | Shreya S Mattimadu | **Waiting** on the `.pbix` |
| Integrated dashboard QA | Team | **Blocked** — no `.pbix` |
| Final report, presentation, contribution record | Shashank (narrative), team (assembly) | **Pending** |

## 7. Limitations

State these wherever the results appear.

1. **Missing data is systemic.** Deaths missing 27.8%, total affected 25.8%, adjusted damage 67.6%,
   magnitude 68.8% at country-impact grain. All totals are *reported* totals.
2. **Economic loss is under-reported**, especially where insurance penetration is low; damage rankings
   partly measure reporting capacity.
3. **Geography is country-level.** Coordinates exist for 15.8% of impacts and are country points;
   GADM identifiers do not support subnational allocation.
4. **Historical quality.** Pre-2000 records (7,137 impacts, `Historic = Yes`) reflect weaker reporting;
   three events carry conflicting flags, so the period must be derived from `Start Year < 2000`.
5. **2026 is partial** (153 events as at 31 October 2026).
6. **Dates are incomplete** — 3,612 impacts and 3,185 events have no complete start date; `Start Year`
   is the only complete temporal key.
7. **Magnitude is incomparable** across types; 13 rows report a literal 0 and 133 a negative value.
8. **Impacts are not deduplicated across events** — the same population can be affected repeatedly, so
   summed totals are reported impact, not unique people.
9. **No inferential statistics.** The Spearman correlations are event-level, pairwise-complete and
   untested for significance; they describe association in the reported data, not causation.

## 8. Licensing, ethics and academic integrity

- EM-DAT is the **only** data source. Cite EM-DAT (CRED / UCLouvain), version 2026-10-23, in every
  output, and follow EM-DAT's current terms of use.
- The workbook and the four derived CSVs are **restricted project materials**: do not publish,
  redistribute, upload or commit them to public services. The repository itself is private to the
  project team.
- Charts, aggregated findings and documentation are the team's work and may be used in the academic
  submission with attribution.
- Record who did what. The team contribution record in `FINAL_SUBMISSION_CHECKLIST.md` is an academic
  requirement, not a formality.
- The approval deck contained names and student identifiers; it is **not** in the repository, and
  `PROJECT_APPROVAL_SUMMARY.md` is the identifier-free substitute.

## 9. Glossary

| Term | Meaning here |
|---|---|
| **Country-impact record** | One disaster event's impact in one country (18,060 rows). |
| **Event** | One underlying disaster after merging its country impacts on `Event ID` (15,727). |
| **Multi-country event** | An event with impacts in more than one country (1,067, 6.8%). |
| **Coverage / reporting coverage** | Events (or records) that report a given measure ÷ the total events (or records) in scope. |
| **Reported impact** | A total of the values actually present. Never "all impact". |
| **Historic** | EM-DAT flag for pre-2000 records; equivalent to `Start Year < 2000` here, apart from three conflicting events. |
| **Unique Events** | `DISTINCTCOUNT(Event ID)`. Additive only in the type summary. |
| **Grain** | What one row represents. Mixing grains inside one visual is the most common error this project guards against. |

## 10. Where to go next

- Continue the work: `TEAM_HANDOVER.md` (ownership and ordered tasks) and
  `AI_AGENT_HANDOVER_PROTOCOL.md` (rules for the next agent).
- Build the dashboard: `DASHBOARD_DATA_HANDOVER.md`.
- Understand or defend a number: `DATA_DICTIONARY.md`, `DATA_QUALITY_REPORT.md`,
  `EDA_VALIDATION_REPORT.md`.
- Check academic completeness: `FINAL_SUBMISSION_CHECKLIST.md`.
