# When Nature Strikes

**A Visualization Approach to Determine the Impact of Natural Disasters**

Are the most frequent natural disasters also the most destructive? In the
23 October 2026 EM-DAT export, floods led recorded frequency (5,814 of 15,727
events) and total reported affected population. Storms led total adjusted
damage and earthquakes led mean adjusted damage among reporting events.
The ranking depends on the impact measure, reporting coverage and time period.

| Explore | Where to start |
| --- | --- |
| Report and presentation | [Research report](submission/final_report.pdf), [presentation](submission/final_presentation.pdf), [editable files and presenter materials](submission/README.md) |
| Dashboards | [Ten-view Streamlit dashboard](docs/DASHBOARD_GUIDE.md), [five-page Power BI project](submission/powerbi/demo/When_Nature_Strikes.pbip), [Power BI authoring source](dashboard/powerbi/README.md) |
| Research | [Methodology](docs/METHODOLOGY.md), [EDA notebooks](analysis/), [statistical analysis](docs/STATISTICAL_ANALYSIS.md), [model evaluation](docs/ML_METHODOLOGY.md), [XAI](docs/XAI_COMPARISON.md), [projections](docs/DIMENSIONALITY_REDUCTION.md), [clustering and anomalies](docs/CLUSTERING_ANALYSIS.md) |
| Reproduce and verify | [Windows setup](WINDOWS_HANDOVER/START_HERE.md), [data dictionary](docs/DATA_DICTIONARY.md), [validation record](docs/VALIDATION_REPORT.md), [completion matrix](submission/COMPLETION_MATRIX.csv) |
| Review the handover | [Deliverables manifest](submission/DELIVERABLES_MANIFEST.md), [team contributions](docs/TEAM_CONTRIBUTIONS.md), [draft PR #3](https://github.com/SamarthRamesha/when-nature-strikes/pull/3) |

![Streamlit guided findings with the impact selector and hazard chart](submission/evidence/streamlit/05-story.png)

## Reproduce

Use `project/restore-and-integrate-powerbi` for the current handover. The Windows
setup uses Python 3.11 and the included synthetic fixtures for a credential-free
demo. The full pipeline and research dashboard use the matching authorized
workbook. [Authorized Windows workflow](WINDOWS_HANDOVER/README_WINDOWS.md)

On macOS or Linux, install `requirements.txt` in a Python 3.11 environment,
then run `python scripts/reproduce_windows.py --workbook /path/to/export.xlsx`
from the repository root. This command checks the input fingerprint, rebuilds
all four tables and reruns validation and analysis. To exercise the demo
without the workbook, install Playwright and run `python scripts/test_browser_local.py`
after provisioning Chromium. [Dashboard and browser checks](docs/DASHBOARD_GUIDE.md)

The native project integrates both team reports with one EM-DAT model and a
Guided Findings page. Microsoft validation found zero errors and two legacy
map warnings. Desktop refresh, interactions and PBIX save/reopen are pending.
[Recovery and integration](docs/RECOVERY_AND_POWER_BI.md) · [Desktop checklist](WINDOWS_HANDOVER/POWERBI_ACCEPTANCE_CHECKLIST.md)

## Data and attribution

EM-DAT data, 2026, CRED / UCLouvain, Brussels, Belgium. The release branch
contains synthetic fixtures, Natural Earth boundaries and published aggregate
research results. Keep the authorized workbook, detailed tables, per-event
results and imported real-data PBIX local. See the terms and the separate
record of exposure on the default branch and in history. [Data provenance and licensing](docs/DATA_LICENSE.md)
