# Team Handover — When Nature Strikes

**This is the living handover record.** It states who owns what *now*, what is finished, what is next,
and what the next owner must do before passing the project on again. It is updated at the end of every
work session by whoever worked on the repository — human or AI agent.

Read with: `README.md` (entry point), `docs/AI_AGENT_HANDOVER_PROTOCOL.md` (how to continue and hand
over), `docs/NEXT_SESSION_PROMPT.md` (paste-ready context for a new chat).

**Last updated:** 11 November 2026 · **Updated by:** Samarth Ramesha (repository finalisation and
publishing) · **Branch:** `project/final-handover-and-repository-cleanup`

Status vocabulary — do not blur these:

| Status | Meaning |
|---|---|
| **COMPLETE** | Present in the repository and verified by an executed check in this session. |
| **DELIVERED** | Owned by another teammate, present in the repository, not re-verified here. |
| **IN PROGRESS** | Someone is actively working on it now; the branch or file is named. |
| **NOT STARTED** | Assigned, nothing exists yet. |
| **BLOCKED** | Cannot start or finish without something outside this repository. |
| **EXTERNAL** | Depends on a person, meeting, teacher decision or system outside the repository. |

---

## 1. Current ownership

| Member | Ownership | State |
|---|---|---|
| **Samarth Ramesha** | Data inspection, cleaning, preprocessing, event consolidation, summary datasets, reproducibility, data dictionary, validation, data handover, integration coordination | **COMPLETE** — see `SAMARTH_FINAL_HANDOVER_CHECKLIST.md` |
| **Shashank S K** | EDA, statistical analysis, findings, charts, metric validation | **DELIVERED** (6 notebooks, 15 tables, 32 charts); findings narrative and metric re-validation still open with him |
| **Shreya Patil** | Main analytical Power BI dashboard (pages 1–3) | **NOT STARTED** — next owner |
| **Shreya S Mattimadu** | Geospatial component and its integration into the shared dashboard (page 4) | **BLOCKED** — waits on the shared `.pbix` |
| **Team** | Scope decision (Unit 1 + 3 vs Unit 2), final report and presentation assembly, submission review | **EXTERNAL** |

### Handover to the next owner

**Intended next owner: Shreya Patil.** Ownership is **pending acknowledgement** — this repository
records the intended handover; it does not assume she has accepted it.

### Handover acknowledgement

To be completed by the person taking over. Until it is signed, treat the handover as *offered*, not
*accepted*.

| Field | Value |
|---|---|
| Accepted by (name) | _pending_ |
| Date | _pending_ |
| Starting branch / commit | _pending_ |
| Confirmed they can run `scripts/validate_project_data.py` (exit 0) | _pending_ |
| Confirmed they can run `scripts/verify_eda_findings.py` (exit 0) | _pending_ |
| Notes / conditions | _pending_ |

---

## 2. Phase ledger

| Phase | Owner | State | Evidence |
|---|---|---|---|
| Dataset inspection and cleaning | Samarth | COMPLETE | `scripts/prepare_emdat.py`; 27,962 → 18,060 natural impacts |
| Natural-hazard filtering | Samarth | COMPLETE | `Disaster Group = Natural`; 9,902 technological impacts excluded and documented |
| Event consolidation | Samarth | COMPLETE | 15,727 events; 1,067 multi-country; totals reconcile exactly |
| Processed + summary datasets | Samarth | COMPLETE | Four CSVs in `data/processed/` |
| Reproducible pipeline | Samarth | COMPLETE | Clean-copy rebuild byte-identical for all four CSVs |
| Data dictionary | Samarth | COMPLETE | `docs/DATA_DICTIONARY.md` — 132 columns |
| Data-quality validation | Samarth | COMPLETE | 71 checks, exit 0 |
| EDA and charts | Shashank | DELIVERED | `analysis/*.ipynb`, `analysis/outputs/`, `visualizations/` |
| EDA findings verification | Samarth | COMPLETE | `scripts/verify_eda_findings.py`, 89/89 values |
| Dashboard specification | Samarth | COMPLETE | `docs/DASHBOARD_DATA_HANDOVER.md` |
| Power BI dashboard pages 1–3 | Shreya Patil | NOT STARTED | No `.pbix` in the repository |
| Geospatial page 4 | Shreya S Mattimadu | BLOCKED | Needs the shared `.pbix` |
| Integrated dashboard QA | Team | BLOCKED | Needs a built dashboard |
| Final report / presentation | Shashank (narrative), team (assembly) | EXTERNAL | See `FINAL_SUBMISSION_CHECKLIST.md` |

---

## 3. What Samarth completed (condensed)

| Area | Deliverable |
|---|---|
| Pipeline | `scripts/prepare_emdat.py` — deterministic rebuild of the four CSVs, six derived fields, no imputation |
| Data | `data/processed/*.csv` — 18,060 × 53, 15,727 × 35, 15 × 19, 11,157 × 25 |
| Validation | `scripts/validate_project_data.py` (71 checks) → `analysis/outputs/data_quality_report.json`, `docs/DATA_QUALITY_REPORT.md` |
| Findings verification | `scripts/verify_eda_findings.py` → `analysis/outputs/eda_validation.json`, `docs/EDA_VALIDATION_REPORT.md` |
| Documentation | `DATA_HANDOVER.md`, `DATA_DICTIONARY.md`, `DASHBOARD_DATA_HANDOVER.md`, `INTEGRATION_HANDOVER.md`, `PROJECT_OVERVIEW.md`, this file, the AI protocol, `NEXT_SESSION_PROMPT.md`, `FINAL_SUBMISSION_CHECKLIST.md` |
| Coordination | `INTEGRATION_HANDOVER.md` §6–§9 (sequence, per-owner work, QA checklist) |

Detail and audit evidence: `docs/SAMARTH_COMPLETION_SUMMARY.md`,
`docs/SAMARTH_FINAL_HANDOVER_CHECKLIST.md`.

---

## 4. What Shreya Patil needs to know

### 4.1 Datasets ready to use — no further preparation required

| File | Rows × cols | Grain |
|---|---|---|
| `data/processed/natural_disaster_events.csv` | 15,727 × 35 | one consolidated event |
| `data/processed/cleaned_natural_disaster_impacts.csv` | 18,060 × 53 | one country impact |
| `data/processed/natural_disaster_type_summary.csv` | 15 × 19 | one disaster type |
| `data/processed/natural_country_year_type_summary.csv` | 11,157 × 25 | country × year × type |

Load as **UTF-8 with BOM**; keep blank cells as *null*. No new columns are needed beyond one computed
period flag (`Period = IF(Start Year < 2000, "Historic (pre-2000)", "2000 onwards")`).

### 4.2 Which dataset belongs to which page

| Page | Primary file | Why |
|---|---|---|
| 1. Disaster Overview | `natural_disaster_type_summary.csv` + `natural_disaster_events.csv` | Fast type cards and KPI totals; event file for distinct-event counts |
| 2. Frequency vs Destructiveness | `natural_disaster_events.csv` | One row per event — the only correct basis for frequency |
| 3. Temporal Analysis | `natural_disaster_events.csv` (year/decade), `natural_country_year_type_summary.csv` (country trends) | Event grain for global trends, country grain for maps over time |
| 4. Integrated Geographic Analysis | `natural_country_year_type_summary.csv` (+ `cleaned_natural_disaster_impacts.csv` for drill-through) | Country-grain sums joined on `ISO` |

### 4.3 Metrics that must be calculated at event level

- **Unique events** = `DISTINCTCOUNT('FactEvents'[Event ID])` — the frequency axis.
- **Coverage** = reported events ÷ unique events, per measure (deaths 74.1%, affected 78.6%, damage 33.4%).
- **Average and median impact per reported event** — denominators are reported events, never all events.
- **Multi-country events** = `CALCULATE([Unique Events], FactEvents[Country Count] > 1)`.

### 4.4 Aggregations that cause double-counting

| Trap | Consequence | Correct approach |
|---|---|---|
| `COUNTROWS` on the impact file as "number of disasters" | 18,060 instead of 15,727 (+14.8%) | `DISTINCTCOUNT(Event ID)` |
| Summing `Unique Events` from `natural_country_year_type_summary.csv` | sums to 18,060 because events repeat per country | never use as a project total; use event-grain distinct count |
| Adding nominal and CPI-adjusted damage | meaningless total | use adjusted only, label the unit |
| Adding `Insured Damage` / `AID Contribution` / `Reconstruction Costs` to damage | double counts the same loss | keep as separate measures |
| Comparing `Magnitude` across types | compares km² with kph and °C | never aggregate; show per type and scale |
| Using `Associated Types` as a second classification | counts events twice | display as tags only |
| Treating blank as 0 (`COALESCE`, `+0`) | invents data and flattens coverage | leave null; show coverage |

### 4.5 Missing-data limitations that must be displayed

State on every impact visual: **"Reported values only — missing ≠ zero"**, with the coverage figure
for the selected measure. Concretely: deaths missing for 27.8% of country impacts, total affected
25.8%, adjusted damage 67.6%, magnitude 68.8%; coordinates exist for 15.8% and are country-level;
3,185 events have no complete start date; 2026 is partial (153 events); pre-2000 records are
lower-quality (`Historic = Yes`, 7,137 impacts).

### 4.6 Expected pages (one integrated dashboard, four pages)

1. **Disaster Overview** — KPI cards (15,727 events, 15 types, 1900–2026, three impact totals with
   coverage), ranked bar of events by type, coverage strip, research question and source on the page.
2. **Frequency vs Destructiveness** — the answer page: scatter of events (x) against average
   deaths / affected / damage (y), totals bar with coverage labels, explicit finding callout.
3. **Temporal Analysis** — events per year and per decade, impact totals by decade with coverage,
   historic vs 2000-onward comparison, 2026 marked partial.
4. **Integrated Geographic Analysis** — filled map by country, country leaderboard, region/subregion
   comparison, drill-through to event detail; built **inside the same file** as page 4 by
   Shreya S Mattimadu.

Every page carries a footer: source (EM-DAT, CRED/UCLouvain, 2026-10-23), measure definition, unit and
the relevant missing-data note.

### 4.7 Filters and cross-visual interactions

- Year-range slider (1900–2026, default full range) with a "2000 onwards" bookmark; disaster
  subgroup/type filters kept hierarchical; region/country filters with region → subregion → country.
- One shared filter pane across all four pages; no page-local filters that silently persist.
- Cross-filtering between charts (click a bar to filter the page, click again to clear);
  cross-highlighting left enabled where Power BI supports it.
- A visible clear-all/reset control and a "current filters" text box on the answer page.
- Historic-period filter present on every page (derived from `Start Year`, not from `Historic`).

### 4.8 What Shashank is responsible for validating

- The six verified findings in `docs/EDA_VALIDATION_REPORT.md` against his notebooks — especially the
  **reported-event denominator** for every average and the **total-vs-average** distinction.
- Medians and coverage beside every average claim (Drought: mean 175,139.60 deaths vs median 200).
- The Spearman matrix (0.3496 / 0.2445 / 0.2327) described as event-level, pairwise-complete, without
  significance testing.
- Adjudication of the three events with conflicting `Historic` flags (`1988-0424`, `1995-0275`,
  `1999-9388`).
- The final findings narrative used as dashboard page-2 copy — from verified numbers only.

### 4.9 When Shreya S Mattimadu receives the PBIX

After pages 1–3 are built and the measures reproduce the acceptance numbers in §5, Shreya Patil hands
over **the same file** (never a copy or a second report), together with the confirmed `DimCountry`
definition. Shreya S Mattimadu then adds the geographic page as **page 4 inside that file**, joins map
geometry on `ISO`, verifies zero unmatched rows, keeps the shared filters synchronized, and confirms
cross-filtering in both directions. After that, the file returns to Shreya Patil/the team unchanged in
structure for final QA.

### 4.10 What the final integrated deliverable must contain

- One `.pbix` with four pages, one filter pane, one country dimension, one type dimension, one year
  dimension built from `Start Year`.
- Measures reproducing: 15,727 events · 32,842,715 deaths · 9,065,006,097 affected ·
  8,120,533.17 million US$ damage · coverage 74.1 / 78.6 / 33.4.
- The research question answered explicitly on page 2, with totals **and** averages, medians and
  coverage.
- Missing-data disclaimer and source/version footer on every page.
- A map that joins on `ISO` with zero unmatched countries and does not imply subnational precision.
- The completed QA table in `docs/INTEGRATION_HANDOVER.md` §9, with evidence.

### 4.11 What she must document before handing it to the next owner

- Update **this file**: ownership, phase ledger, what she built, file/branch paths, acceptance numbers
  reproduced, what failed, what is blocked.
- Update `docs/NEXT_SESSION_PROMPT.md` so a fresh chat can resume.
- Update `README.md` §Current project status if the status materially changed (do **not** mark the
  dashboard complete without a real, verified `.pbix`).
- Record the QA evidence in `docs/INTEGRATION_HANDOVER.md` §9 and any new limitations found while
  building.
- Note the next responsible person (Shreya S Mattimadu, then the team for the report).

---

## 5. Acceptance numbers to reproduce

| Metric | Value |
|---|---|
| Country impacts | 18,060 |
| Consolidated events | 15,727 |
| Country × year × type groups | 11,157 |
| Disaster types | 15 |
| Multi-country events | 1,067 (6.8%) |
| Reported deaths total | 32,842,715 (11,655 events, 74.1%) |
| Reported affected total | 9,065,006,097 (12,366 events, 78.6%) |
| Reported adjusted damage | 8,120,533.174 million US$ (5,251 events, 33.4%) |
| Most frequent type | Flood — 5,814 events (37.0%) |
| Busiest year | 2000 — 489 events |
| Highest average deaths | Drought — 175,139.60 per reported event (67/647 events, median 200) |
| Highest average affected | Drought — 6,349,540.46 (477 events, median 900,000) |
| Highest average damage | Earthquake — 2,881.02 million US$ (626 events, 39.8%) |
| Highest total damage | Storm — ≈ 3.49 million million US$ (US$3.49T) |
| Spearman ρ | deaths↔affected 0.3496 · deaths↔damage 0.2445 · affected↔damage 0.2327 |

---

## 6. Ordered task list for the next owner

| # | Task | Status | Done when |
|---|---|---|---|
| 1 | Acknowledge the handover in §Handover acknowledgement | NOT STARTED | Sections filled with name and date |
| 2 | Read README, this file, `DATA_HANDOVER.md` caveats, `DASHBOARD_DATA_HANDOVER.md` | NOT STARTED | — |
| 3 | Reproduce the data checks (`validate`, `verify`, exit 0) | NOT STARTED | Both exit 0; §5 numbers confirmed |
| 4 | Build one `.pbix`; load four CSVs; keep blanks null | NOT STARTED | File exists, row counts match |
| 5 | Model: `DimType`, `DimCountry`, `DimYear`, `BridgeEventCountry` | NOT STARTED | Relationships per `DASHBOARD_DATA_HANDOVER.md` §G.2 |
| 6 | Measures from §G.3 reproduce §5 totals | NOT STARTED | All five acceptance figures match |
| 7 | Page 1 Disaster Overview | NOT STARTED | Cards, ranked bar, coverage strip, source footer |
| 8 | Page 2 Frequency vs Destructiveness | NOT STARTED | Scatter + totals bar + explicit finding |
| 9 | Page 3 Temporal Analysis | NOT STARTED | Year/decade views, historic split, 2026 marked partial |
| 10 | Shared filter pane + interactions on pages 1–3 | NOT STARTED | Cross-filtering works both ways |
| 11 | Hand the same file to Shreya S Mattimadu | NOT STARTED | She confirms receipt in this file |
| 12 | Page 4 geographic analysis integrated | NOT STARTED | Map joins on `ISO`, zero unmatched |
| 13 | Integrated QA against `INTEGRATION_HANDOVER.md` §9 | NOT STARTED | Every row checked with evidence |
| 14 | Update this file, `NEXT_SESSION_PROMPT.md`, README status | NOT STARTED | Next owner can continue without a chat history |

---

## 7. Original allocation vs recommended next actions

Keep these distinct when writing the report; the second list is **guidance**, not a change of team
allocation.

**Original allocation (from the project brief):** Samarth and Shashank — inspection, cleaning,
preparation and analysis; Shreya Patil and Shreya S Mattimadu — dashboard development and the
Unit 2/geospatial component.

**Recommended next actions (technical sequencing suggested by the data phase):** build the model
before the pages; prove the measures against the acceptance numbers before designing visuals; hand the
single `.pbix` to the geospatial owner only after pages 1–3 are stable; run the integrated QA once, at
the end.

Nothing in this repository reassigns anyone's responsibility. If the team wants to change ownership,
record it here explicitly with a date.

---

## 8. Blockers and open decisions

| Item | Owner | Effect |
|---|---|---|
| No `.pbix` in the repository | Shreya Patil | Blocks geospatial page, integrated QA and screenshot review |
| Unit 1 + Unit 3 (deck) vs Unit 2 geospatial (allocation) | Team / teacher | Affects the dashboard's scope statement and the report |
| Report and presentation assembly ownership | Team | Not assigned in any project document; currently Shashank holds the narrative |
| EM-DAT PDF definitions not machine-verifiable | — | Field meanings rest on EM-DAT documentation plus observed fill rates; recorded in `DATA_DICTIONARY.md` |

---

## 9. Change log

| Date | Author | Change |
|---|---|---|
| 31 Oct 2026 | Samarth | Source workbook added; pipeline and four processed CSVs built |
| 5 Nov 2026 | Shashank | EDA notebooks, 15 tables, 32 charts (PR #1) |
| 11 Nov 2026 | Samarth | Validation (71 checks), EDA verification (89/89), data dictionary, dashboard and integration handover, closure audit |
| 11 Nov 2026 | Samarth | Repository finalisation: README rewrite, `.gitignore` hardening, project overview, this handover record, AI agent protocol, next-session prompt, final submission checklist, PR template; published on a feature branch for review |

---

## 10. Rules for updating this file

1. Update it **before** you finish a session, not after.
2. Change only the sections your work touched; never rewrite another owner's record.
3. Every status change needs evidence in the same row or in the linked document — a document claiming
   completion is not evidence (`docs/AI_AGENT_HANDOVER_PROTOCOL.md` §Evidence).
4. Keep the change log append-only.
5. Never record credentials, tokens or personal identifiers here.
6. When ownership changes, name the new owner and the date, and leave the previous owner's history
   intact.
