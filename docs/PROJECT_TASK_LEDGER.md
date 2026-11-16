# Project task ledger

| Task | Status | Evidence |
| --- | --- | --- |
| Git and licensing audit | TESTED | PROJECT_AUDIT.md, DATA_LICENSE.md, original refs preserved |
| Data preparation, documentation and reproducibility | TESTED | All four CSV checksums identical across two rebuilds, DATA_DICTIONARY.md |
| Source and baseline validation | TESTED | 69 pass, 2 warnings, 0 fail and 0 skip |
| Original notebooks and EDA | TESTED | Six executed notebooks and 89/89 artifact comparisons |
| Advanced EDA and statistical analysis | TESTED | Coverage, two eras, correlations, bootstrap, omnibus tests and reproducible figures |
| Supervised models | TESTED | Prior, logistic and random forest with a later test cohort |
| SHAP | TESTED | Global, beeswarm, local and hazard plots, with checked additivity |
| PCA, t-SNE and UMAP | TESTED | Projection, variance, loadings and neighborhood evaluation |
| Clustering and anomaly detection | TESTED | K-means and DBSCAN diagnostics, Isolation Forest, local assignments |
| Browser dashboard and geography | TESTED | Four-page Playwright acceptance and ISO matching |
| Power BI authoring package | IMPLEMENTED | M, DAX, theme, page layouts and acceptance targets |
| Native Power BI file and Desktop verification | BLOCKED | Requires Windows Power BI Desktop. The browser alternative is ready. |
| Literature review and contribution record | IMPLEMENTED | Source matrix and historical commit evidence |
| Research report, slides and presenter material | TESTED | DOCX, PPTX, two PDFs and verification |
| Lightweight CI | IMPLEMENTED | .github/workflows/checks.yml |
| Institutional review and acceptance | NEEDS HUMAN REVIEW | FINAL_SUBMISSION_CHECKLIST.md |
