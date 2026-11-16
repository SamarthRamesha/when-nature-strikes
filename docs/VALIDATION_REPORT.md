# Validation and acceptance

## Data and analysis

| Check | Observed result |
| --- | --- |
| Source workbook identity | SHA-256 matches the independently held export and the original Git blob. |
| Clean rebuild and repeat | 27,962 source rows → 18,060 country impacts → 15,727 events. All four regenerated CSV checksums matched the separate rebuild. |
| Baseline validator | 71 total, 69 pass, 2 warnings, 0 fail and 0 skip. See [data quality report](DATA_QUALITY_REPORT.md). |
| Independent EDA verification | 89 of 89 comparisons passed. See [EDA verification](../analysis/outputs/eda_validation.json). |
| Original notebooks | The overview input path and the missing frequency calculation were repaired. All six notebooks were executed in an isolated notebook build. |
| New analytics | Statistics, classifier, SHAP, PCA, t-SNE, UMAP, K-means, DBSCAN, Isolation Forest and the country map executed against the verified snapshot. |
| Classifier checks | Disjoint time partitions, 834 held-out events, 97 positives. SHAP reconstructed held-out margins within 8.9 × 10⁻¹⁶. |
| Geographic inputs | 169 current geometry joins covered 17,269 of 18,060 source impact rows. Remaining ISO codes appear in tables. |
| Core unit suite | 12 tests passed. These include a fixture workbook rebuild and coverage, date, aggregation, split, map and result checks. |

The validator flags 13 explicit zero magnitudes and the inflated count from
summing country-year-type event counts. The historic flag disagrees across
country impacts of three events and is excluded from the modeling design.
The source has 3,612 incomplete start month/day records and zero invalid
complete start dates. Missing losses, partial 2026 and historical reporting
differences remain data limitations. The headless local environment reported
font cache and physical-CPU detection warnings during some runs. The analytics
and PDF exports completed.

## Dashboard and submission

- Chromium exercised all four pages, a shared flood filter, the total/median
  control, map canvas and unmatched-country table. The repository captures
  actual screenshots from that run.
- LibreOffice rendered 13 report pages and 16 slides. Page/slide boundaries,
  legibility, figures, pagination and citations were reviewed. The PPTX
  integrity check found 16 slides, one native chart and zero package errors.
- `scripts/check_submission.py` checks the two PDFs, edited document packages,
  speaker note parts and the shared headline metrics without source data.
- GitHub Actions runs the credential-free unit and submission checks. Native
  Microsoft Office rendering, Power BI authoring, Power BI refresh and DAX
  execution require the corresponding applications. No PBIX was created.

## Human review

The team and faculty need to confirm academic format, contributions, AI
disclosure and submission acceptance. A Windows Power BI authoring session is
needed if the evaluator requires a native PBIX. See the
[submission checklist](FINAL_SUBMISSION_CHECKLIST.md).
