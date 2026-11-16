# Windows handover verification

This update continues the original submission on the same draft PR. The
pre-handover baseline is `2dcc847` and the local backup ref is
`backup/pre-windows-handover-2026-11-16`. The six existing notebooks, primary
analysis and original Git history were preserved. The prior data and model
verification is recorded in [VALIDATION_REPORT.md](VALIDATION_REPORT.md).

| Verification | Method and evidence |
| --- | --- |
| Snapshot and analytical outputs | A clean authorized run verified the input fingerprint and all four output hashes. Baseline validation returned 69 passes and two documented warnings. EDA matched all 89 comparisons. The rebuilt findings, model metrics, SHAP, XAI, profile, cluster, projection, anomaly and map summaries or tables matched the committed outputs byte for byte. The held-out cohort contains 834 events and the profile cohort contains 1,821 events. |
| XAI and projection artifacts | 40 held-out raw-feature permutations, three probability-scale LIME scenarios with fidelity scores, individual grouped SHAP, a categorical month PDP and ICE, and coarsened 2D or 3D projection cells. Per-event data are local. |
| Browser application | Actual Chromium ran the expanded ten views in authorized and invented modes, exercised guided findings, model and XAI controls, 3D PCA, t-SNE, UMAP, anomaly selection and the map. [Authorized screenshots](../submission/evidence/streamlit/) |
| Native report authoring | Microsoft Power BI authoring CLI 0.5.0 reported zero errors and zero warnings. Microsoft's Power Query parser accepted 13 generated expressions across the two data modes. Independent source tests verify all visual bindings, slicer groups and synthetic denominators. [Authoring receipt](../submission/evidence/powerbi_author_cli.json) |
| Native report runtime | The local Windows VM reaches a password-protected sign-in screen. Desktop open, refresh, interactive rendering, save and reopen require a signed-in Windows session. The archive supplies the built five-page PBIP and a Windows script that points it at the authorized CSVs. [Desktop checks](../WINDOWS_HANDOVER/POWERBI_ACCEPTANCE_CHECKLIST.md) |
| Windows automation | The [Windows x64 run on `c353d71`](https://github.com/SamarthRamesha/when-nature-strikes/actions/runs/43898487037) passed Windows PowerShell 5.1 setup, PBIP path discovery, 18 regressions, Office package checks, ten synthetic Chromium views and a health check of the PowerShell Streamlit launcher. Both Power BI Desktop and the authorized workbook remain outside this automation. |
| Office and distribution | LibreOffice exported the 14-page report and 18-slide presentation to PDF. The independently extracted ZIP passed the per-file SHA-256 checks, all 18 regressions, both Office package checks and the ten-view synthetic Chromium suite. |

Windows scripts operate on a local short path such as `C:\WNS`. The native
geographic visual relies on Azure Maps and current Desktop settings. Check
the accompanying ranking tables and ISO exclusions independently. The
licensed data dependency for full replication is the same export documented
in [data provenance](DATA_LICENSE.md).

The [first Windows run](https://github.com/SamarthRamesha/when-nature-strikes/actions/runs/43897195817)
failed while reading the UTF-8 GeoJSON with Windows code page 1252. The
rerun used explicit UTF-8 for that file and the packaged Markdown checks.
The [Linux project checks](https://github.com/SamarthRamesha/when-nature-strikes/actions/runs/43898486888)
also passed on the fix.

The [draft PR's Windows run](https://github.com/SamarthRamesha/when-nature-strikes/actions/runs/43899271292)
passed after the evidence update. A duplicate push run logged a successful
Uvicorn start but its HTTP probe timed out and its PowerShell job treated the
native stderr log as an error. The launcher check now makes a direct loopback
request with curl and captures stdout and stderr separately. Current results
are listed in the [Windows handover workflow](https://github.com/SamarthRamesha/when-nature-strikes/actions/workflows/windows-handover.yml).
