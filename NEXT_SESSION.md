# Resume Power BI Desktop acceptance

Continue on `project/complete-final-submission` in the existing
`work/when-nature-strikes` checkout. Keep [draft PR #3](https://github.com/SamarthRamesha/when-nature-strikes/pull/3) open.
The completion matrix and [verification record](docs/WINDOWS_ACCEPTANCE_REPORT.md)
carry the results. The archive identifies its exact source commit in
`PACKAGED_COMMIT.txt`.
The [Windows x64 workflow](https://github.com/SamarthRamesha/when-nature-strikes/actions/runs/43898487037)
passed setup, tests, synthetic browser acceptance and the Streamlit launcher.

The handover includes an authored five-page native PBIP and its import model.
Microsoft's authoring CLI returned zero errors and zero warnings. A clean
authorized rebuild matched the saved model metrics, SHAP and XAI summary,
permutation importance, PDP/ICE, projection cells, and profile and anomaly
summaries. An independent ZIP extraction passed the regression and Office
checks and the synthetic ten-view Chromium suite. The Word report and
PowerPoint deck are preserved in `submission/`.

## Next action in Windows

1. On this Mac, open UTM, select the running Windows VM, dismiss the lock
   screen, and sign in directly through Windows. Alternatively, use a Windows
   PC with current Power BI Desktop and extract the archive to a short local
   path such as `C:\WNS`.
2. In PowerShell at the extracted project root, run:

   ```powershell
   .\WINDOWS_HANDOVER\OPEN_POWERBI.ps1
   ```

3. In Power BI Desktop, select **Refresh** and follow the [acceptance
   checklist](WINDOWS_HANDOVER/POWERBI_ACCEPTANCE_CHECKLIST.md). It covers all
   five tabs, expected counts, slicers, cross-filtering, and the Azure Maps
   visual. Use **File → Save As** to save
   `submission\powerbi\When_Nature_Strikes.pbix`. Close and reopen it, change a
   filter, and record the Desktop version, input mode, results, and SHA-256:

   ```powershell
   Get-FileHash -Algorithm SHA256 .\submission\powerbi\When_Nature_Strikes.pbix
   ```

4. For authorized Desktop acceptance, independently obtain the matching
   EM-DAT workbook. From the extracted root run `INSTALL_WINDOWS.ps1` using
   [Start here](WINDOWS_HANDOVER/START_HERE.md), then:

   ```powershell
   .\WINDOWS_HANDOVER\RUN_PIPELINE.ps1 -Workbook 'C:\Data\authorized-export.xlsx' -PrepareOnly
   .\WINDOWS_HANDOVER\OPEN_POWERBI.ps1 -Authorized
   ```

   Refresh and compare the authorized counts in the checklist. Save that
   PBIX under `submission\powerbi\local\` and keep it with the authorized
   data on the Windows machine.

After Desktop acceptance, update `submission/COMPLETION_MATRIX.csv`, the
manifest, and the verification record with the observed results. Use a new
staging destination when repackaging so the previous archive is preserved.
