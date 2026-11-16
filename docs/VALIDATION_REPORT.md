# Validation and acceptance

## Data and research

| Check | Observed result |
| --- | --- |
| Authorized input | Workbook SHA-256 matches the exact 23 October 2026 snapshot. A clean macOS rebuild matched all four prepared CSV hashes. [Provenance](../results/provenance.json) |
| Preparation and original EDA | 27,962 source rows, 18,060 natural country impacts and 15,727 events. Baseline validation returned 69 passes and two documented warnings, with zero failures or skips. All 89 EDA comparisons matched. The six original notebooks executed in an isolated rebuild. [Data quality](DATA_QUALITY_REPORT.md) · [EDA validation](EDA_VALIDATION_REPORT.md) |
| Classifier and XAI | The later test cohort contains 834 events and 97 positives. Logistic regression reached test AP 0.288. SHAP reconstructed model margins within 8.9 × 10⁻¹⁶. The rebuild matched saved model metrics, SHAP, 40 held-out permutations, three invented LIME scenarios and month PDP/ICE results. [Saved XAI results](../results/xai/README.md) |
| Profiles and geography | The authorized rebuild matched the saved PCA, t-SNE, UMAP, cluster and anomaly summaries, including projection cells for the 1,821-event profile cohort. Natural Earth polygons covered 17,269 of 18,060 impact records. [Projections and clusters](../results/dimensionality_reduction/README.md) · [Map coverage](../results/map_summary.json) |

The two data warnings concern 13 explicit zero magnitudes and non-additive
country-year-type event counts. The `Historic` flag conflicts across impacts
in three events, so the analysis uses year to split reporting eras. Treat 2026
as partial and compare reported losses alongside coverage.

## Dashboards and academic artifacts

| Check | Observed result |
| --- | --- |
| Streamlit | Chromium exercised all ten views in authorized and synthetic modes. Checks include year, region, country and hazard filters, seven story steps, model and XAI selectors, 3D PCA, t-SNE, UMAP, anomaly selection and the map. [Browser screenshots](../submission/evidence/streamlit/) |
| Power BI project files | Microsoft Power BI report-authoring CLI 0.5.0 returned zero errors and two deprecation warnings for the team’s Bing map and filled map in each input mode. Microsoft's Power Query parser accepted all 13 expressions. Source tests verify 54 retained visual IDs, shared bindings, Top N filters, interactions and synchronized slicers. [Authoring receipt](../submission/evidence/powerbi_author_cli.json) |
| Office files | LibreOffice rendered 14 report pages and 18 slides. The submission check verifies both PDFs, both editable packages, speaker notes and shared headline figures. [Academic submission](../submission/README.md) |
| Windows checkout | Hosted Windows x64 verified PowerShell 5.1 installation, PBIP path discovery, 18 regressions, Office checks, ten synthetic Chromium views and the Streamlit launcher. Desktop and the authorized Windows pipeline are separate acceptance steps. [Verified Windows run for the independent ZIP](https://github.com/SamarthRamesha/when-nature-strikes/actions/runs/43900273955) · [Current Windows workflow](https://github.com/SamarthRamesha/when-nature-strikes/actions/workflows/windows-handover.yml) |
| Independent ZIP | The existing archive at `7590255` passed 303 file hash checks, 18 regressions, Office checks and the ten-view synthetic Chromium suite after extraction. [Package manifest](../submission/DELIVERABLES_MANIFEST.md) |

## Repository handover

The integration branch restored the original EDA output filenames and data
handover alongside the later analyses and academic artifacts. Both source PBIX
fact tables matched the baseline for all fields used here. Historical CSVs and
the original source files are preserved locally. [Recovery and integration](RECOVERY_AND_POWER_BI.md)

The credential-free CI checks include the public-tree path policy. It rejects
known detailed EM-DAT output paths, workbooks, PBIX files and caches. Keep the
source and detailed derivatives local. [Public data and historical exposure](DATA_LICENSE.md)

## Pending human acceptance

Power BI Desktop refresh, slicers, cross-filtering, Bing map rendering, PBIX
save and reopen are pending. A source validation pass establishes the PBIP
structure and syntax. Desktop acceptance requires observing the report in the
application. [Desktop checklist](../WINDOWS_HANDOVER/POWERBI_ACCEPTANCE_CHECKLIST.md)

The team and faculty review the academic format, contribution record and AI
disclosure. [Contribution record](TEAM_CONTRIBUTIONS.md)
