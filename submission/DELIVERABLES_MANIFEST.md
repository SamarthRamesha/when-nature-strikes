# When Nature Strikes deliverables

The repository is the project source and handover. The integration archive
supersedes the pre-integration Windows ZIP from `7590255`. Each archive records
its own revision and file hashes in `PACKAGED_COMMIT.txt` and `SHA256SUMS.txt`.
[Repository entry point](../README.md)

| Deliverable | Repository location |
| --- | --- |
| Windows setup, launch and tests | [Windows quick start](../WINDOWS_HANDOVER/START_HERE.md) · [Authorized workflow](../WINDOWS_HANDOVER/README_WINDOWS.md) |
| Data preparation, models and statistics | [`scripts/`](../scripts/) · [`src/`](../src/) · [Dependencies](../requirements.txt) · [Data dictionary](../docs/DATA_DICTIONARY.md) |
| Original EDA and aggregate results | [Six notebooks and aggregate outputs](../analysis/) · [32 EDA figures](../visualizations/) · [Research results](../results/) · [Input provenance](../results/provenance.json) |
| Exact baseline inventory and team Power BI source evidence | [Recovery and model reconciliation](../docs/RECOVERY_AND_POWER_BI.md) · [Inventory and hashes](evidence/recovery_baseline.json) |
| Streamlit views, filters, geography and story | [Dashboard guide](../docs/DASHBOARD_GUIDE.md) · [Application](../dashboard/app.py) · [Additional views](../dashboard/analysis_views.py) · [Browser evidence](evidence/streamlit/) |
| Five-page native Power BI project | [Synthetic PBIP](powerbi/demo/When_Nature_Strikes.pbip) with adjacent report and model directories · [Power Query, DAX, fixtures and theme](../dashboard/powerbi/) · [Authoring receipt](evidence/powerbi_author_cli.json) |
| Power BI Desktop acceptance and PBIX save | [Desktop checklist](../WINDOWS_HANDOVER/POWERBI_ACCEPTANCE_CHECKLIST.md) · [Pending acceptance record](../NEXT_SESSION.md) |
| Classifier and explanations | [Model metrics](../results/model_metrics.json) · [SHAP, LIME, permutation and PDP/ICE](../results/xai/) |
| Projections, clustering and anomalies | [PCA, t-SNE and UMAP cells](../results/dimensionality_reduction/) · [Profiles](../results/profile_summary.json) · [Cluster evaluation](../results/cluster_evaluation.csv) |
| Report, slides, notes, demo and viva | [Academic submission index](README.md) |
| Attribution and acceptance | [Team contributions](../docs/TEAM_CONTRIBUTIONS.md) · [Completion matrix](COMPLETION_MATRIX.csv) · [Validation report](../docs/VALIDATION_REPORT.md) · [Data terms](../docs/DATA_LICENSE.md) |

The authorized workbook, detailed derivatives and real-data PBIX stay local.
The demo uses invented data alongside labeled aggregate research results.
