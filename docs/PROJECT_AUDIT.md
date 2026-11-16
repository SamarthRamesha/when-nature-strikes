# Project audit

## Git baseline

The initial local checkout was clean at `9b48a5043cda4238ad53c4d66e18cc0c19d1c870`.
The GitHub connector verified public visibility and `main` as the default branch.
The backup ref `backup/pre-takeover-2026-11-16` points to that baseline. The
implementation branch is `project/complete-final-submission`.

| Remote branch | Verified tip | Unique commits relative to main |
| --- | --- | --- |
| main | `9b48a5043cda4238ad53c4d66e18cc0c19d1c870` | Baseline |
| eda-analysis | `5809b49ba04102ad237d9bb1a08db8b59323fa60` | 0. Merged in PR #1 |
| project/final-handover-and-repository-cleanup | `26405d057dfd9293419f63fe531b2940ba6c398c` | 0. Merged in PR #2 |

Both requested three-dot diffs are empty in the main-to-topic direction because
both topic tips are ancestors of main. The EDA commit added six notebooks,
aggregate outputs and charts. The handover commit added formal validation,
metric definitions, a data dictionary and dashboard specification. Samarth Ramesha
is the recorded author of the data-preparation and handover commits. SSK1703 is
the recorded author of the EDA commit. The connector and `git ls-remote` found
no later licensing correction or additional branch at the start of this session.

## Assets examined and retained

- Source workbook and four processed CSVs. The independently held workbook had
  the same SHA-256 as the baseline blob. All eight documented counts matched.
- `prepare_emdat.py` builds country impacts, consolidated events, hazard summaries
  and country-year-type summaries. The initial Python 3.11 rebuild differed in
  153 floating-point strings across three summaries. Counts and substantive
  metrics matched. The revised pipeline uses deterministic summation.
- Six EDA notebooks, their saved tables, and the original PNG collection.
  Notebook source cells remain available. Saved outputs were cleared because
  some displayed source event rows.
- The baseline contained the EM-DAT field-reference PDF, the sanitized approval
  summary, dashboard model instructions, JSON check results and Markdown guides.
  The original approval deck was excluded by the prior team because it contained
  student identifiers. No final report, final deck, test suite, workflow, PBIX,
  executable dashboard, trained model, SHAP, PCA, t-SNE, UMAP or clustering was
  present. The audited checkout had no pre-existing ignored artifacts.
- `validate_project_data.py` returned 69 pass, two warnings and zero failures
  or skips. `verify_eda_findings.py` reproduced 89 of 89 saved comparisons.

## Risks and implementation choices

The prior private-repository wording contradicted GitHub and the commit history.
Current-tree data removal retains the original Git objects and the independently
held workbook. See [provenance and terms](DATA_LICENSE.md). The retained source
analysis distinguishes repeated country impacts from events. Historic flags
conflict in three events and are unsuitable as a temporal classifier feature.
Legacy magnitude totals are kept for schema compatibility and excluded from
new analyses. Coverage differs markedly by hazard and era. The historic 2026
endpoint is partial, and the harm variables describe reported data.

Keep the established data scripts and add shared metric definitions, statistical
sensitivity checks and a chronological event-level model. Use the same filtered
metrics in the browser dashboard, report and classroom demonstration. Provide
Power BI sources and a model specification for Windows authoring. Keep row-level
and licensed inputs outside the public working tree.
