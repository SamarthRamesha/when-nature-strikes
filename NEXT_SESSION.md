# Pending Power BI Desktop acceptance

Continue on `project/restore-and-integrate-powerbi`. The original Power BI
files and exact baseline are in the local `work/powerbi-integration` workspace.
The integrated report source and verification are recorded in the repository.
[Integration and recovery](docs/RECOVERY_AND_POWER_BI.md)

On this Mac, open **UTM → Windows**, dismiss the lock screen, and sign in
through Windows. A Windows laptop with Power BI Desktop can perform the same
acceptance from the extracted handover. Install the project dependencies, then
run the authorized preparation and open the integrated project.

```powershell
.\WINDOWS_HANDOVER\RUN_PIPELINE.ps1 -Workbook 'C:\Data\authorized-export.xlsx' -PrepareOnly
.\WINDOWS_HANDOVER\OPEN_POWERBI.ps1 -Authorized
```

Use `OPEN_POWERBI.ps1` without `-Authorized` to exercise the included synthetic
fixture first. In Desktop, refresh, follow the [acceptance checklist](WINDOWS_HANDOVER/POWERBI_ACCEPTANCE_CHECKLIST.md),
and save the authorized copy as `submission\powerbi\When_Nature_Strikes.pbix`.
Close and reopen it, change a filter, and record the Desktop version, mode,
observations and SHA-256. Keep the real-data PBIX local.

```powershell
Get-FileHash -Algorithm SHA256 .\submission\powerbi\When_Nature_Strikes.pbix
```

Record the observed results in the [completion matrix](submission/COMPLETION_MATRIX.csv)
and [validation report](docs/VALIDATION_REPORT.md). Draft PR #3 retains the
prior handover and links to the integration review.
