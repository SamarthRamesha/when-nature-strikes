# When Nature Strikes deliverables

Begin with `WINDOWS_HANDOVER/START_HERE.md` in the extracted folder. Use
`submission/COMPLETION_MATRIX.csv` and `submission/evidence/` for observed
validation and runtime boundaries. Git commit and file-level hashes are in
`PACKAGED_COMMIT.txt` and `SHA256SUMS.txt` at the archive root.
The [Windows x64 acceptance run](https://github.com/SamarthRamesha/when-nature-strikes/actions/runs/43898487037)
passed setup, tests and synthetic Chromium. The native Desktop step is pending.

| Deliverable | Path | How to use |
| --- | --- | --- |
| Windows scripts and documentation | `WINDOWS_HANDOVER/` | Run the installation and tests in PowerShell. Use the synthetic route without credentials. |
| Desktop checkpoint | `NEXT_SESSION.md` | Resume Power BI Desktop acceptance from the packaged native project. |
| Data prep, model and statistics source | `src/`, `scripts/`, `analysis/` and `requirements.txt` | Supply the authorized workbook, then use the rebuild script. |
| Data provenance, quality and statistics | `results/provenance.json`, `docs/DATA_DICTIONARY.md`, `docs/DATA_QUALITY_REPORT.md` and `results/` | Read the source fingerprint, aggregation definitions, cautions and performance metrics. |
| Dashboard, guided findings and geography | `dashboard/app.py`, `dashboard/analysis_views.py`, `dashboard/world.geojson` | Use `RUN_STREAMLIT.ps1` or `RUN_STREAMLIT.ps1 -Synthetic`. Actual browser captures are in `submission/evidence/streamlit/`. |
| Native Power BI source | `submission/powerbi/demo/When_Nature_Strikes.pbip` and adjacent directories | Open in current Desktop, refresh and test. Use the Windows authorized project generator to make the report use your CSVs, then save as PBIX. |
| Native PBIX | Local Windows save target `submission/powerbi/When_Nature_Strikes.pbix` | Desktop open, refresh, Save As and reopen are pending direct Windows sign-in. Check `NEXT_SESSION.md` for the resume command. |
| Classifier and explanation results | `results/model_metrics.json` and `results/xai/` | Compare the held-out classifier, grouped SHAP, permutation, LIME and PDP/ICE. |
| Dimensionality reduction and clustering | `results/dimensionality_reduction/`, `results/profile_summary.json` and `results/cluster_evaluation.csv` | Explore coarsened PCA, t-SNE and UMAP and read diagnostics. Authorized rebuild adds exact local event embeddings. |
| Report and presentation | `submission/final_report.docx`, `submission/final_report.pdf`, `submission/final_presentation.pptx` and `submission/final_presentation.pdf` | Open the PDFs directly or edit the Office files. Speaker notes are in the PPTX. |
| Presenter support and academic record | `submission/presenter_script.md`, `submission/dashboard_demo_guide.md`, `submission/viva_questions.md` and `docs/TEAM_CONTRIBUTIONS.md` | Use during the walkthrough and attribution review. |
| Build tests and evidence | `tests/`, `submission/evidence/` and `docs/WINDOWS_ACCEPTANCE_REPORT.md` | Check the Windows CI receipt, synthetic browser run and authorized rebuild evidence. Use the authorized switch for licensed-data checks. |

The authorized 23 October 2026 EM-DAT workbook must be obtained independently.
Prepared row-level data, per-event predictions, ICE and embeddings, detailed
individual geography matches, cached models and refreshed real-data PBIX
are local artifacts. The package supplies clearly labeled invented fixtures
plus aggregate real research results. Synthetic totals exercise controls and
carry no research interpretation.
