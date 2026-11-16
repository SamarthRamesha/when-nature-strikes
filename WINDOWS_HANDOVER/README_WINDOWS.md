# Windows handover

Use [START_HERE.md](START_HERE.md) to preview the package. The Python pins target 64-bit CPython 3.11. On Windows ARM, check the current Power BI Desktop requirements and Python wheel availability. The Windows automated job uses x64.

## Obtain and verify the workbook

Request the authorized custom export version **2026-10-23**, delivered 31 October 2026, from the [EM-DAT portal](https://public.emdat.be/). It has a sheet named `EM-DAT Data`. Verify the file with `Get-FileHash -LiteralPath 'C:\path\authorized-export.xlsx' -Algorithm SHA256`. The full fingerprint is in [provenance.json](../results/provenance.json) and starts with `6767b6125b3ad35a`. Another export will produce other results. [Data terms](../docs/DATA_LICENSE.md)

## Run the authorized pipeline

```powershell
.\WINDOWS_HANDOVER\INSTALL_WINDOWS.ps1 -Browser
.\WINDOWS_HANDOVER\RUN_PIPELINE.ps1 -Workbook 'C:\path\authorized-export.xlsx'
.\WINDOWS_HANDOVER\RUN_TESTS.ps1 -Authorized -Browser
.\WINDOWS_HANDOVER\RUN_STREAMLIT.ps1
```

The rebuild checks the locked source fingerprint, copies it to the expected local name if needed, rebuilds and verifies four CSVs, runs both validators, and reproduces statistics, model evaluation, XAI, embeddings, clustering and geography. Use `-PrepareOnly` for preparation and both data validators. An existing different workbook stays in place and raises an error.

Open [localhost port 8765](http://127.0.0.1:8765). Stop the server from PowerShell with Ctrl+C. The four CSVs, fitted model, row-level predictions, event-level ICE, projections and geographic matches remain in your local copy.

Run `.\WINDOWS_HANDOVER\OPEN_POWERBI.ps1 -Authorized` in a second window to generate the native report project against your prepared CSVs. Follow the [Desktop guide](POWERBI_BUILD_AND_TEST.md) to refresh and save. See [troubleshooting](TROUBLESHOOTING.md).
