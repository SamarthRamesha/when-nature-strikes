# When Nature Strikes

**A Visualization Approach to Determine the Impact of Natural Disasters**

An interactive data-visualization project built on [EM-DAT](https://www.emdat.be/) that asks one
question: **are the most frequent natural disasters also the most destructive?** This repository
holds the cleaned datasets, the reproducible preparation and validation pipeline, the exploratory
analysis and charts, the analytical findings, and the data handover specification for a single
integrated Power BI dashboard.

> **Project state:** the data phase is complete and verified. The Power BI dashboard and the
> geospatial page are **not built yet** — no `.pbix` exists in this repository. Current next owner:
> **Shreya Patil** (handover pending her acknowledgement). See
> [Current project status](#current-project-status) and [docs/TEAM_HANDOVER.md](docs/TEAM_HANDOVER.md).

---

## Contents

1. [Project overview](#project-overview)
2. [Current project status](#current-project-status)
3. [Team and ownership](#team-and-ownership)
4. [Repository structure](#repository-structure)
5. [Dataset guide](#dataset-guide)
6. [Reproduce the project](#reproduce-the-project)
7. [Documentation index](#documentation-index)
8. [Handover and continuity](#handover-and-continuity)
9. [Academic limitations and data licensing](#academic-limitations-and-data-licensing)
10. [Next steps for the next owner](#next-steps-for-the-next-owner)

---

## Project overview

**Research question.** Are the most frequent natural disaster types also the most destructive?

**Problem statement.** Disaster policy debate is usually driven by how *often* a hazard occurs, while
damage, casualties and displacement follow how *destructive* it is. These two rankings do not
coincide, and a chart that silently treats unreported damage as zero will make the gap look smaller
than it is. The project therefore compares frequency with destructiveness at the correct grain — one
row per disaster event, not per country impact — and shows how much of each measure is actually
reported.

**Objectives.**

1. Produce reproducible, validated EM-DAT datasets at country-impact, event, type and
   country-year-type grain.
2. Quantify frequency versus destructiveness for 15 natural hazard types, and report the reporting
   coverage behind every impact claim.
3. Deliver one integrated Power BI dashboard with four pages: Disaster Overview, Frequency vs
   Destructiveness, Temporal Analysis, and Integrated Geographic Analysis.
4. Document every column, unit, aggregation rule and missing-data limitation so the numbers can be
   defended in an academic submission.
5. Keep the work reproducible and hand it over so the next owner can continue without the previous
   developer's chat history.

**Dataset.** EM-DAT — the International Disaster Database, CRED / UCLouvain — public custom-request
export, table version **2026-10-23**, request file dated 31 October 2026. The export holds **27,962**
records, of which **18,060** are natural-hazard country impacts. The other 9,902 technological
impacts are excluded from the processed files, not reclassified.

**Scope.** Natural hazards only, 1900–2026 (2026 is partial), country-level impacts worldwide, impact
measures as reported by EM-DAT (deaths, injured, affected, homeless, total affected, CPI-adjusted
damage). The unit is one disaster event's impact in one country.

**Limitations in one paragraph.** Impact fields are frequently unreported (adjusted damage is missing
for 67.6% of country impacts), coverage varies by hazard type and by decade, economic loss is
under-reported where insurance penetration is low, `Magnitude` is on five incomparable scales, the
data is country-level even where GADM identifiers exist, and 2026 is an incomplete year. Missing
means *unknown*, never zero. Full detail: [docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md) and
[docs/DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md) §5.

---

## Current project status

Status as of **11 November 2026**. "Complete" means present in the repository **and** verified by an
executed check — not merely described in a document.

### Completed

| Deliverable | Evidence |
|---|---|
| Dataset inspection and cleaning | `scripts/prepare_emdat.py`; 27,962 source rows → 18,060 natural country impacts, every source value preserved |
| Natural-disaster filtering | `Disaster Group = Natural`; 9,902 technological impacts documented as excluded |
| Event consolidation | `Event ID` derivation; 15,727 events, including 1,067 multi-country events |
| Processed datasets | Four CSVs in `data/processed/`, 18,060 × 53 / 15,727 × 35 / 15 × 19 / 11,157 × 25 |
| Summary datasets | Type-level and country-year-type aggregates that reconcile exactly with the impact totals |
| Reproducible preprocessing pipeline | Rebuild from a clean copy reproduces all four CSVs **byte for byte** |
| Data dictionary | `docs/DATA_DICTIONARY.md` — all 132 columns across the four files, with origin, unit and fill rate |
| Data quality validation | `scripts/validate_project_data.py` — 71 checks, exit 0 |
| EDA verification | `scripts/verify_eda_findings.py` — 6 findings recomputed, 89/89 committed values reproduced |
| Analytical findings documentation | `docs/EDA_VALIDATION_REPORT.md` plus six notebooks and 32 charts |
| Power BI data handover specification | `docs/DASHBOARD_DATA_HANDOVER.md` — dataset choice, model, DAX, pages, interactions |
| Integration and ownership documentation | `docs/INTEGRATION_HANDOVER.md`, `docs/TEAM_HANDOVER.md`, `docs/FINAL_SUBMISSION_CHECKLIST.md` |

### Pending

| Deliverable | Owner | Blocker |
|---|---|---|
| Main Power BI analytical dashboard (pages 1–3) | Shreya Patil | Not started; specification is ready |
| Geospatial dashboard integration (page 4) | Shreya S Mattimadu | Waits on the shared `.pbix` from Shreya Patil |
| Cross-filtering and cross-highlighting validation | Shreya Patil → Shreya S Mattimadu | Needs the built pages |
| Final integrated dashboard QA | Team (data checks by Samarth) | Needs a `.pbix` in the repository |
| Final project findings and submission integration | Shashank (narrative), team (report/deck) | Waits on dashboard pages and the scope question below |

**No Power BI dashboard is claimed as complete.** There is no `.pbix` file in this repository. The
dashboard pages, their measures and their interactions are specified in
[docs/DASHBOARD_DATA_HANDOVER.md](docs/DASHBOARD_DATA_HANDOVER.md); building them is the next
owner's work.

**Open question for the team.** The approval deck describes Unit 1 + Unit 3 coverage, while the
current allocation describes a Unit 2 geospatial component. No teacher feedback document was supplied
to resolve the difference; it is recorded in
[docs/DATA_HANDOVER.md](docs/DATA_HANDOVER.md#requirement-provenance-and-differences) and must be
confirmed before final submission.

---

## Team and ownership

| Member | Responsibility | State |
|---|---|---|
| **Samarth Ramesha** | Dataset inspection, cleaning, preprocessing, event consolidation, summary datasets, reproducibility, data dictionary, validation, data handover, integration coordination | **Complete** (verified — see [docs/SAMARTH_FINAL_HANDOVER_CHECKLIST.md](docs/SAMARTH_FINAL_HANDOVER_CHECKLIST.md)) |
| **Shashank S K** | EDA, statistical analysis, findings, charts, metric validation | **Delivered**; findings verification and the final narrative remain open with him |
| **Shreya Patil** | Main analytical Power BI dashboard | **Next owner — not started** |
| **Shreya S Mattimadu** | Geospatial component and its integration into the shared Power BI dashboard | **Waiting** on the shared `.pbix` |

**Current next owner: Shreya Patil.** She takes over the analytical dashboard and coordinates the
subsequent geospatial integration with Shreya S Mattimadu.

Ownership is **pending acknowledgement** — this repository records the intended handover, it does not
assume she has accepted it. She (or whoever takes the role) should record acceptance in
[docs/TEAM_HANDOVER.md](docs/TEAM_HANDOVER.md#handover-acknowledgement).

There must be **one** shared Power BI dashboard. The analytical pages and the geospatial page are
pages 1–4 of the same file, not separate reports.

---

## Repository structure

```text
when-nature-strikes/
├── README.md                        This file — start here
├── requirements.txt                 Python dependency for the preprocessing script (openpyxl)
├── .gitignore                       Ignores caches, environments, Office lock files, secrets
├── .github/
│   └── pull_request_template.md     PR checklist, including handover obligations
│
├── data/
│   ├── source/                      EM-DAT custom-request workbook (unmodified, restricted)
│   │   ├── EM-DAT Custom Request Oct 31 2026.xlsx
│   │   └── README.md                Provenance note
│   └── processed/                   Four generated CSVs + provenance note
│       ├── cleaned_natural_disaster_impacts.csv        18,060 × 53   country-impact grain
│       ├── natural_disaster_events.csv                 15,727 × 35   event grain
│       ├── natural_disaster_type_summary.csv               15 × 19   type grain
│       ├── natural_country_year_type_summary.csv       11,157 × 25   country × year × type
│       └── README.md
│
├── scripts/
│   ├── prepare_emdat.py             Rebuilds the four CSVs from the workbook
│   ├── validate_project_data.py     Data-quality validation (71 checks) + reports
│   └── verify_eda_findings.py       Recomputes the headline EDA findings (89/89 values)
│
├── analysis/
│   ├── 00_data_overview.ipynb       EDA notebooks — Shashank's work
│   ├── 01_disaster_frequency.ipynb
│   ├── 02_disaster_impact.ipynb
│   ├── 03_temporal_trends.ipynb
│   ├── 04_pattern_analysis.ipynb
│   ├── 05_visualizations_and_findings.ipynb
│   └── outputs/                     15 CSV tables exported by the notebooks
│                                     + data_quality_report.json, eda_validation.json
│
├── visualizations/                  32 PNG charts produced by the notebooks
│   ├── frequency/  (2)              Frequency and cumulative frequency
│   ├── impacts/    (10)             Impact totals, averages, coverage, frequency-vs-impact
│   ├── trends/     (7)              Yearly/decadal trends, historical vs recent
│   ├── patterns/   (5)              Averages by type, correlation heatmap
│   └── final/      (8)              Final chart set for the report and presentation
│
└── docs/                            All project documentation — see the index below
    ├── PROJECT_OVERVIEW.md
    ├── DATA_HANDOVER.md
    ├── DATA_DICTIONARY.md
    ├── DATA_QUALITY_REPORT.md             (generated)
    ├── DASHBOARD_DATA_HANDOVER.md
    ├── EDA_VALIDATION_REPORT.md
    ├── INTEGRATION_HANDOVER.md
    ├── SAMARTH_COMPLETION_SUMMARY.md
    ├── SAMARTH_FINAL_HANDOVER_CHECKLIST.md
    ├── TEAM_HANDOVER.md                   ← living handover record
    ├── AI_AGENT_HANDOVER_PROTOCOL.md      ← rules for the next AI agent
    ├── NEXT_SESSION_PROMPT.md             ← paste-ready prompt for a new chat
    ├── FINAL_SUBMISSION_CHECKLIST.md
    ├── PROJECT_APPROVAL_SUMMARY.md
    └── EM_DAT_Documentation.pdf           EM-DAT public-table field documentation
```

**Why the notebooks sit directly in `analysis/` rather than a `notebooks/` subdirectory:** notebooks 01–05 locate
the repository root with `Path.cwd()` plus a single parent fallback, and notebook 00 reads
`../data/processed/...`. At `analysis/` both work when Jupyter is started from the repository root or
from `analysis/`; one directory deeper they break. The layout is kept as the notebooks were written
so that no executed notebook is edited. The output tables still live in `analysis/outputs/`.

**Intentional duplicates:** `visualizations/` holds overlapping figures (for example
`impacts/08_frequency_vs_average_deaths.png` and `patterns/05_frequency_vs_average_deaths.png`) because
each notebook section exported its own chart set; `analysis/outputs/` likewise keeps both working
tables (`decadal_disaster_frequency.csv`) and final tables (`final_decadal_frequency.csv`). Both are
kept deliberately: the validation script verifies the committed values, and the final set feeds the
report.

---

## Dataset guide

### Which file to use

| Need | File | Grain of one row |
|---|---|---|
| Frequency vs destructiveness by type (the research question) | `natural_disaster_events.csv` | One consolidated disaster event (15,727 rows) |
| Fast type-level cards and ranked bars | `natural_disaster_type_summary.csv` | One disaster type (15 rows) |
| Country drill-down, event names, dates, coordinates, GADM fields | `cleaned_natural_disaster_impacts.csv` | One EM-DAT **country impact** (18,060 rows) |
| Filled maps, country and regional trends | `natural_country_year_type_summary.csv` | One country × start year × type group (11,157 rows) |

### Grain and identifiers

| Concept | Definition | Verified count |
|---|---|---|
| Country-impact record | One event's impact in one country. `DisNo.` is unique; `Event ID` repeats across countries. | 18,060 |
| Consolidated event | One underlying event after merging country impacts on `Event ID`. | 15,727 |
| Disaster type | The approved type-level dimension. | 15 types |
| Country × year × type group | One group per `ISO` + `Start Year` + `Disaster Type`. | 11,157 |

- **`DisNo.`** — EM-DAT identifier, `<year>-<sequence>-<ISO3>`; unique per country impact.
- **`Event ID`** — derived: `DisNo.` without the ISO-3 suffix. This is what reconnects an event's
  country impacts and is the key for event-level frequency.
- **`ISO`** — ISO-3 country code, strictly 1:1 with `Country` (230 codes), the join key for map
  geometry.

### Derived fields (six, all in the impact file)

`Event ID`, `Start Date`, `End Date` (populated only for complete valid dates), `Decade`
(`floor(year/10)*10`), `Has Coordinates` (`Yes` only when both latitude and longitude exist), and
`Total Damage, Adjusted (million US$)` (EM-DAT's CPI-adjusted `'000 US$` ÷ 1,000 — a unit conversion
only, never an estimate of missing loss).

### Units

| Quantity | Unit |
|---|---|
| Deaths, injured, affected, homeless, total affected | persons (reported, not deduplicated across events) |
| `Total Damage ('000 US$)` | thousand US$, **nominal** |
| `Total Damage, Adjusted ('000 US$)` | thousand US$, EM-DAT CPI-adjusted |
| `Total Damage, Adjusted (million US$)` | million US$ (≈ US$8.12 trillion in total) |
| `AID Contribution`, `Reconstruction Costs`, `Insured Damage` | thousand US$ (separate concepts — never added to damage) |
| `Magnitude` | `Km2`, `Kph`, `Moment Magnitude`, `°C` or `Vaccinated`, per `Magnitude Scale` |
| `CPI` | index, not a measure |

### Missing data

A blank cell means **unknown or unreported**. It is never zero and must never be filled, coalesced or
plotted as a zero bar. At country-impact grain: deaths missing 27.8%, total affected 25.8%, adjusted
damage 67.6%, magnitude 68.8%; coordinates exist for 15.8%. At event grain, adjusted damage is
reported for only 5,251 of 15,727 events (33.4%). Every impact visual must show its coverage.

### Multi-country events and aggregation rules

1,067 events (6.8%) affect more than one country. Counting `Country` rows instead of events inflates
frequency by **14.8%** (18,060 vs 15,727) and changes per-type counts.

- **Frequency is `DISTINCTCOUNT(Event ID)`** — never `COUNTROWS` of the impact table.
- **`Unique Events` is additive only in the type summary** (it totals 15,727). In the
  country-year-type summary it repeats events per country and sums to 18,060 — never use it as a
  project total.
- **Impact measures are additive** across country rows (a country-level amount rolls up to an event
  total) but they are *reported impact*, not unique people, and must not be described as deduplicated.
- **Averages use reported events as the denominator**, not all events; median accompanies every mean.

Full rules, the additivity matrix and the Power BI model: [docs/DASHBOARD_DATA_HANDOVER.md](docs/DASHBOARD_DATA_HANDOVER.md) §B, §G.

---

## Reproduce the project

Requires **Python 3.10+**. The validation and verification scripts need only the standard library;
`openpyxl` (in `requirements.txt`) is needed to rebuild the CSVs and to enable the two
source-workbook checks.

```bash
# 1. Environment
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt

# 2. Rebuild the processed datasets from the source workbook
python scripts/prepare_emdat.py
#    Prints a QA JSON summary. Overwrites the four CSVs in data/processed/ in place;
#    only re-run when the source data changes.

# 3. Validate the datasets (writes analysis/outputs/data_quality_report.json + docs/DATA_QUALITY_REPORT.md)
python scripts/validate_project_data.py

# 4. Verify the EDA findings (writes analysis/outputs/eda_validation.json)
python scripts/verify_eda_findings.py
```

**Expected results on the committed data**

| Command | Exit | Output |
|---|---|---|
| `scripts/prepare_emdat.py` | 0 | 27,962 source rows → 18,060 impacts, 15,727 events, 15 types, 11,157 groups; output byte-identical to the committed CSVs |
| `scripts/validate_project_data.py` | 0 | 71 checks: 69 pass, 2 documented warnings, 0 fail (without `openpyxl`: 67 pass, 2 warn, 2 skip) |
| `scripts/verify_eda_findings.py` | 0 | 6 findings recomputed; 89/89 committed artefact values reproduced |

The two warnings are properties of the data, not defects: 13 impact rows report `Magnitude = 0`, and
`Unique Events` in the country-year-type file sums to 18,060 because events repeat per country.

**Notebooks** (optional; they regenerate the charts): start Jupyter from the repository root, then
open any file in `analysis/`. They require pandas, matplotlib and seaborn. Re-running them rewrites
the PNGs in `visualizations/` and the CSVs in `analysis/outputs/` — the committed values are the ones
the verification script checks.

Accepted numbers to reproduce: 15,727 events · 18,060 country impacts · 11,157 country-year-type
groups · 15 types · 1,067 multi-country events · 32,842,715 reported deaths · 9,065,006,097 reported
affected · 8,120,533.174 million US$ reported adjusted damage · coverage 74.1% / 78.6% / 33.4% ·
Flood 5,814 events (37.0%) · 2000 busiest year (489 events) · Spearman ρ 0.3496 / 0.2445 / 0.2327.

---

## Documentation index

| Document | Read it for |
|---|---|
| [docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md) | Scope, objectives, method, deliverables map, limitations, licensing |
| [docs/TEAM_HANDOVER.md](docs/TEAM_HANDOVER.md) | **Living handover record** — who owns what now, per-owner state, ordered tasks, acknowledgement |
| [docs/AI_AGENT_HANDOVER_PROTOCOL.md](docs/AI_AGENT_HANDOVER_PROTOCOL.md) | Mandatory workflow for any AI agent continuing this project |
| [docs/NEXT_SESSION_PROMPT.md](docs/NEXT_SESSION_PROMPT.md) | Paste-ready prompt that restores context in a fresh chat |
| [docs/DATA_HANDOVER.md](docs/DATA_HANDOVER.md) | Source, derivations, caveats, recommended use (the "why" of the data) |
| [docs/DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md) | Every column of the four files: origin, type, unit, fill rate, additivity |
| [docs/DASHBOARD_DATA_HANDOVER.md](docs/DASHBOARD_DATA_HANDOVER.md) | What to build in Power BI: dataset choice, grain, metrics, model, DAX, pages, interactions |
| [docs/DATA_QUALITY_REPORT.md](docs/DATA_QUALITY_REPORT.md) | Generated validation evidence (71 checks) |
| [docs/EDA_VALIDATION_REPORT.md](docs/EDA_VALIDATION_REPORT.md) | The six verified findings, with denominators and caveats |
| [docs/INTEGRATION_HANDOVER.md](docs/INTEGRATION_HANDOVER.md) | Ownership, handover sequence, QA checklist per owner |
| [docs/FINAL_SUBMISSION_CHECKLIST.md](docs/FINAL_SUBMISSION_CHECKLIST.md) | Academic deliverables: complete, pending, externally dependent |
| [docs/SAMARTH_COMPLETION_SUMMARY.md](docs/SAMARTH_COMPLETION_SUMMARY.md) | What the data phase delivered, and its outstanding items |
| [docs/SAMARTH_FINAL_HANDOVER_CHECKLIST.md](docs/SAMARTH_FINAL_HANDOVER_CHECKLIST.md) | Closure audit of the data phase, responsibility by responsibility |
| [docs/PROJECT_APPROVAL_SUMMARY.md](docs/PROJECT_APPROVAL_SUMMARY.md) | Approved project scope (identifier-free summary of the approval deck) |
| [docs/EM_DAT_Documentation.pdf](docs/EM_DAT_Documentation.pdf) | EM-DAT's own public-table field documentation |

---

## Handover and continuity

This project is designed to survive a change of owner, of machine and of chatbot. **If you are an AI
agent or a new teammate, read these three in this order before changing anything:**

1. [README.md](README.md) (this file)
2. [docs/TEAM_HANDOVER.md](docs/TEAM_HANDOVER.md) — current ownership and next actions
3. [docs/AI_AGENT_HANDOVER_PROTOCOL.md](docs/AI_AGENT_HANDOVER_PROTOCOL.md) — how to continue and how
   to hand over again

Then inspect the Git branch and working tree, read the files themselves rather than trusting
completion claims, and continue from the existing implementation. The protocol requires every agent to
update `docs/TEAM_HANDOVER.md`, `docs/NEXT_SESSION_PROMPT.md` and this README's status before
finishing its own work — so continuity does not depend on any chatbot's memory.

Safety rules that apply to everyone: never commit, push, merge or delete without the current user's
explicit authorisation; never claim a task is complete without evidence; never expose credentials;
never silently discard uncommitted changes; preserve attribution and academic integrity.

---

## Academic limitations and data licensing

**Limitations to state in the report and on the dashboard.**

- **Missing impact data.** Deaths are unreported for 27.8% of country impacts, total affected for
  25.8%, adjusted damage for 67.6%. Totals describe *reported* impact only; missing is not zero.
- **Incomplete geographic coverage.** Coordinates exist for 15.8% of impacts and are country-level.
  GADM identifiers do not make the data subnational. Country and region are the only defensible
  geographic units.
- **Historical reporting quality.** Pre-2000 records (7,137 impacts, flagged `Historic = Yes`) reflect
  lower reporting capacity; early-century counts are not comparable to modern surveillance. Three
  events (`1988-0424`, `1995-0275`, `1999-9388`) carry conflicting `Historic` flags, so derive the
  period from `Start Year < 2000`.
- **Partial 2026 coverage.** The export is dated 31 October 2026; 2026 holds 153 events and is
  incomplete by construction.
- **Date coverage.** 3,612 country impacts (20.0%) and 3,185 events lack a complete start date; build
  year dimensions from `Start Year`, never from a date relationship.
- **Economic loss under-reporting.** EM-DAT documents under-reporting where insurance and reinsurance
  data are limited; adjusted damage is CPI-adjusted by EM-DAT (their base year, not recomputed here).
- **Magnitude is not comparable across types** (five different scales) and **impact measures are not
  deduplicated across events** — the same people may appear in successive disasters.

**Licensing and terms of use.** The source workbook is an EM-DAT public custom-request export from
CRED / UCLouvain, version 2026-10-23, included unmodified for reproducibility (its SHA-256 is recorded
in `analysis/outputs/data_quality_report.json`). Cite EM-DAT as the data source in every output and
follow EM-DAT's current terms of use. **The workbook and its derivatives are restricted project
materials:** keep them inside this repository and the project team, do not publish or redistribute the
raw export or the derived CSVs, and do not upload them to external services. Charts and aggregated
findings may be used in the academic submission with attribution.

---

## Next steps for the next owner

Ordered for **Shreya Patil** (analytical dashboard), then **Shreya S Mattimadu** (geospatial page).
The same list, with acceptance criteria, is in [docs/TEAM_HANDOVER.md](docs/TEAM_HANDOVER.md).

1. **Acknowledge the handover** by filling in the acknowledgement section of
   `docs/TEAM_HANDOVER.md` (name, date, branch or commit you start from).
2. **Read** this README, `docs/TEAM_HANDOVER.md`, `docs/DATA_HANDOVER.md` §Data profile and caveats,
   then `docs/DASHBOARD_DATA_HANDOVER.md` in full.
3. **Reproduce the data** — run the two validation scripts and confirm exit 0 and the acceptance
   numbers listed above. Do not regenerate the CSVs unless the source workbook changes.
4. **Build one `.pbix`** and load all four CSVs; keep blanks as null (never replace empty cells with
   0). Add the `Period` column and the `DimType` / `DimCountry` / `DimYear` / `BridgeEventCountry`
   model from `docs/DASHBOARD_DATA_HANDOVER.md` §G.
5. **Implement the measures** from §G.3 and prove they reproduce: 15,727 events, 32,842,715 deaths,
   9,065,006,097 affected, 8,120,533.17 million US$ damage, coverage 74.1 / 78.6 / 33.4.
6. **Build pages 1–3** (Disaster Overview, Frequency vs Destructiveness, Temporal Analysis) with one
   shared filter pane, the coverage display beside every impact measure, and the missing-data
   disclaimer on every page.
7. **Hand the same file** — never a copy — to Shreya S Mattimadu, together with the confirmed
   `DimCountry` definition, for the geographic page as page 4.
8. **Validate the integrated dashboard:** four pages in one file, cross-filtering both ways, map
   joined on `ISO` with zero unmatched rows, measures unchanged after integration. Record the evidence
   in `docs/INTEGRATION_HANDOVER.md` §9.
9. **Before finishing, update** `docs/TEAM_HANDOVER.md`, `docs/NEXT_SESSION_PROMPT.md` and this
   README's status section, so the next person inherits the same clarity.
10. **Agree the open scope question** (Unit 1 + Unit 3 vs Unit 2) and the report/presentation ownership
    with the team, and record the answer in `docs/DATA_HANDOVER.md`.

**Definition of done for the dashboard phase:** a single `.pbix` committed to the repository (or
stored where the team agrees, with the path recorded), four functioning pages, measures reproducing the
accepted totals, filters and disclaimers in place, geospatial page integrated, and the QA table in
`docs/INTEGRATION_HANDOVER.md` §9 fully checked with evidence.

**Do not:** regenerate or hand-edit the processed CSVs, zero-fill impact columns, sum the
country-year-type `Unique Events` as a total, create a second dashboard file, describe reported impact
as unique people, or redistribute the EM-DAT export.

---

*Data source: EM-DAT, CRED / UCLouvain, public custom request, version 2026-10-23. Project: When
Nature Strikes — A Visualization Approach to Determine the Impact of Natural Disasters.*
