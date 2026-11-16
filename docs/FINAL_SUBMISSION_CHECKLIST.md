# Final Submission Checklist — When Nature Strikes

Academic deliverables for the final submission, with their real state as of **11 November 2026**.
Nothing here is marked complete because a document says so: each **COMPLETE** row names evidence that
exists in this repository.

**This checklist does not claim the project is finished.** The dashboard, the geospatial page, the
report, the presentation and the literature review are still open.

Status vocabulary: **COMPLETE** (in the repository, verified) · **PARTIAL** (part exists) ·
**PENDING** (assigned, nothing yet) · **BLOCKED** (waits on another artefact) · **EXTERNAL** (waits on
a person, meeting or teacher decision) · **NOT IN REPOSITORY** (no source material supplied).

---

## 1. Deliverables

| # | Deliverable | Status | Owner | Evidence in this repository | What is still needed |
|---|---|---|---|---|---|
| 1 | Approved project scope | **COMPLETE (with caveat)** | Samarth | `docs/PROJECT_APPROVAL_SUMMARY.md` — title, question, dataset, scope, dimensions; approval deck excluded because it carries names and student IDs | Team to confirm the Unit 1 + Unit 3 vs Unit 2 discrepancy (row 14) |
| 2 | Literature review | **NOT IN REPOSITORY** | Shashank / team | No literature-review document or reference list exists in the repository; no source material was supplied | Compile the review and its reference list; add it as a document under `docs/` (not yet created) or as a section of the report |
| 3 | Dataset and source documentation | **COMPLETE** | Samarth | `data/source/README.md` (provenance, version, 27,962 records), `docs/DATA_HANDOVER.md` (source, filter, derivations), `docs/DATA_DICTIONARY.md` (132 columns), `docs/EM_DAT_Documentation.pdf`, SHA-256 in `analysis/outputs/data_quality_report.json` | — |
| 4 | Reproducible preprocessing | **COMPLETE** | Samarth | `scripts/prepare_emdat.py` + `requirements.txt`; clean-copy rebuild reproduces all four CSVs byte for byte | — |
| 5 | Data dictionary | **COMPLETE** | Samarth | `docs/DATA_DICTIONARY.md` — every column of the four files with origin, type, unit, fill rate, additivity matrix, unit table, caveats | — |
| 6 | EDA and findings | **COMPLETE** (analysis) / **PENDING** (narrative) | Shashank | Six notebooks, 15 tables in `analysis/outputs/`, 32 charts in `visualizations/`, `docs/EDA_VALIDATION_REPORT.md` (F1–F7, 89/89 values verified) | Final written findings narrative in report form |
| 7 | Interactive Power BI dashboard | **PENDING** | Shreya Patil | Specification only: `docs/DASHBOARD_DATA_HANDOVER.md` (model, measures, pages, interactions). **No `.pbix` exists.** | Build one file with pages 1–3, measures reproducing the acceptance numbers, shared filters, disclaimers |
| 8 | Geographic analysis | **BLOCKED** | Shreya S Mattimadu | Page-4 specification in `DASHBOARD_DATA_HANDOVER.md` §E; country-grain data ready (`natural_country_year_type_summary.csv`, `ISO` join) | The shared `.pbix`, then the page inside it |
| 9 | Validation and testing evidence | **COMPLETE** (data) / **PENDING** (dashboard) | Samarth / team | 71-check validation (exit 0), 89/89 findings values, closure audit in `docs/SAMARTH_FINAL_HANDOVER_CHECKLIST.md`; QA table in `docs/INTEGRATION_HANDOVER.md` §9 | Dashboard QA rows once a `.pbix` exists |
| 10 | Final written report | **PENDING** | Shashank (narrative) / team (assembly) | Verified numbers ready in `docs/EDA_VALIDATION_REPORT.md`; limitations ready in `README.md` / `docs/PROJECT_OVERVIEW.md` §7 | Write and assemble the report; embed the limitation statements verbatim |
| 11 | Final presentation | **PENDING** | Team | Approval deck only (not in repository); 8 final charts in `visualizations/final/` | Build the final deck from verified figures |
| 12 | Team contribution record | **PENDING** | Team | Change history in `docs/TEAM_HANDOVER.md` §9; per-owner records in `docs/SAMARTH_COMPLETION_SUMMARY.md` §7–10 and `docs/INTEGRATION_HANDOVER.md` §8 | Fill the contribution table in §3 below and submit it |
| 13 | References and licensing | **PARTIAL** | Team | EM-DAT citation, version 2026-10-23, and terms-of-use statement in `README.md` and `docs/PROJECT_OVERVIEW.md` §8; EM-DAT documentation PDF in `docs/` | Academic reference list (sources cited in the report), plus any cited literature |
| 14 | Unit/scope confirmation | **EXTERNAL** | Team / teacher | Discrepancy recorded in `docs/DATA_HANDOVER.md` §Requirement provenance and `docs/PROJECT_OVERVIEW.md` §3 | Teacher or team lead decision on Unit 1 + 3 vs Unit 2 |

---

## 2. Submission gates

The submission is ready only when **all** of these are true. Current state in the right column.

| Gate | Required | Now |
|---|---|---|
| Data reproducible from the repository | Rebuild matches committed CSVs | ✅ byte-identical |
| Data validated | Validation script exits 0 | ✅ 71 checks, 0 fail |
| Findings verified | Committed EDA values reproduce | ✅ 89/89 |
| Every column documented | Dictionary covers all four files | ✅ 132 columns |
| Dashboard exists and is verified | `.pbix` in the repository, four pages, measures match | ❌ no `.pbix` |
| Geospatial page integrated | Page 4 inside the same file | ❌ blocked |
| Cross-filtering validated | Both directions, all pages | ❌ blocked |
| Limitations stated in report **and** dashboard | Missing-data disclaimer on every impact page | ⚠️ documented, not yet on a dashboard |
| Scope question resolved | Unit 1 + 3 vs Unit 2 agreed | ❌ external |
| Report written | Final document | ❌ pending |
| Presentation built | Final deck | ❌ pending |
| Contribution record submitted | Table in §3 completed | ❌ pending |
| Data used within EM-DAT terms | No public redistribution of export or CSVs | ✅ repository is project-private |

---

## 3. Team contribution record (to be completed)

Fill this in for submission. It is a template only — no entries are pre-filled with claims about who
did what beyond what the repository itself records.

| Member | Contribution | Artefacts | Approx. share |
|---|---|---|---|
| Samarth Ramesha | Data inspection, cleaning, preprocessing, consolidation, summaries, reproducibility, dictionary, validation, handover | `scripts/*.py`, `data/processed/`, `docs/DATA_*`, `docs/*HANDOVER*`, README | |
| Shashank S K | EDA, statistical analysis, findings, charts, metric validation | `analysis/*.ipynb`, `analysis/outputs/`, `visualizations/`, findings narrative | |
| Shreya Patil | Analytical Power BI dashboard (pages 1–3), integration | `.pbix` (when built) | |
| Shreya S Mattimadu | Geospatial component (page 4) and integration | `.pbix` page 4 | |

---

## 4. External dependencies (cannot be completed inside this repository)

| Dependency | Blocks | Who can unblock |
|---|---|---|
| Teacher / team decision on Unit 1 + Unit 3 vs Unit 2 | Scope statement in the report and dashboard framing | Team lead or teacher |
| A built `.pbix` from Shreya Patil | Geospatial page, integrated QA, screenshots, report figures | Shreya Patil |
| Literature-review source material | Deliverable 2 | Team |
| Submitted report and deck | Deliverables 10–11 | Team |
| Teacher feedback document (if it exists) | Confirmation that the data preparation matches expectations | Team |

---

## 5. Final review pass (before submission)

```text
[ ] Dashboard opens from a clean machine and refreshes against the four CSVs
[ ] Measures reproduce: 15,727 events, 32,842,715 deaths, 9,065,006,097 affected,
    8,120,533.17 million US$ damage, coverage 74.1 / 78.6 / 33.4
[ ] Four pages present in ONE file, one filter pane, cross-filtering both ways
[ ] Map joins on ISO with zero unmatched countries
[ ] "Reported values only — missing ≠ zero" visible on every impact visual
[ ] 2026 marked as partial on every time axis
[ ] Source and version footer on every page (EM-DAT, CRED/UCLouvain, 2026-10-23)
[ ] Report states: missing data, coverage, country-level geography, historic quality,
    partial 2026, magnitude incomparability, no significance testing
[ ] Reference list complete and consistent with the report body
[ ] Contribution record completed and agreed by all four members
[ ] No raw EM-DAT export or derived CSV published outside the project
[ ] Screenshots captured for the report appendix
[ ] docs/TEAM_HANDOVER.md updated for whoever holds the project after submission
```

---

## 6. Honest summary

The **data and analysis foundation is submission-grade and verified**: reproducible, validated,
documented column by column, with findings independently recomputed. The **dashboard — the project's
main deliverable — does not exist yet**, the geospatial page depends on it, and the report,
presentation, literature review and contribution record are not in the repository. The team should not
represent the project as complete until the gates in §2 are green.
