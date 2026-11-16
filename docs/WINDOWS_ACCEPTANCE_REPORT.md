# Windows handover verification

This update continues the original submission on the same draft PR. The
pre-handover baseline is `2dcc847` and the local backup ref is
`backup/pre-windows-handover-2026-11-16`. The six existing notebooks, primary
analysis and original Git history were preserved. The prior data and model
verification is recorded in [VALIDATION_REPORT.md](VALIDATION_REPORT.md).

| Verification | Method and evidence |
| --- | --- |
| Snapshot and analytical outputs | The authorized run verifies the input fingerprint, the four output hashes, baseline validation and EDA before running statistics, models, XAI, profiles and geography. New outputs retain the original 834-event held-out cohort and 1,821-event profile cohort. |
| XAI and projection artifacts | 40 held-out raw-feature permutations, three probability-scale LIME scenarios with fidelity scores, individual grouped SHAP, a categorical month PDP and ICE, and coarsened 2D or 3D projection cells. Per-event data are local. |
| Browser application | Actual Chromium ran the expanded ten views in authorized and invented modes, exercised guided findings, model and XAI controls, 3D PCA, t-SNE, UMAP, anomaly selection and the map. [Authorized screenshots](../submission/evidence/streamlit/) |
| Native report authoring | Microsoft Power BI authoring CLI 0.5.0 reported zero errors and zero warnings. Microsoft's Power Query parser accepted 13 generated expressions across the two data modes. Independent source tests verify all visual bindings, slicer groups and synthetic denominators. [Authoring receipt](../submission/evidence/powerbi_author_cli.json) |
| Native report runtime | The local Windows VM reaches a password-protected sign-in screen. Desktop open, refresh, interactive rendering, save and reopen require a signed-in Windows session. The archive supplies the built five-page PBIP and a Windows script that points it at the authorized CSVs. [Desktop checks](../WINDOWS_HANDOVER/POWERBI_ACCEPTANCE_CHECKLIST.md) |
| Windows automation | The [Windows workflow](https://github.com/SamarthRamesha/when-nature-strikes/actions/workflows/windows-handover.yml) runs credential-free Python setup and PowerShell scripts on a hosted Windows x64 runner. This scope does not launch Power BI Desktop or use the authorized workbook. |
| Office and distribution | LibreOffice exported the editable report and presentation to PDF. Packaging uses the committed tree, a restricted-input gate and a separate extraction that verifies each hash, the regression suite and both document packages. |

Windows scripts operate on a local short path such as `C:\WNS`. The native
geographic visual relies on Azure Maps and current Desktop settings. Check
the accompanying ranking tables and ISO exclusions independently. The
licensed data dependency for full replication is the same export documented
in [data provenance](DATA_LICENSE.md).
