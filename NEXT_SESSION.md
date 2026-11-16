# Pending Power BI Desktop acceptance

Use the packaged synthetic `.pbip` from the same checkout or the verified ZIP.
Run the following command from the project root on a signed-in Windows machine
with Power BI Desktop.

```powershell
.\WINDOWS_HANDOVER\OPEN_POWERBI.ps1
```

Refresh, exercise all five pages, then save as
`submission\powerbi\When_Nature_Strikes.pbix`. Reopen the saved file and
record the Desktop version, data mode, SHA-256 and observed results. The
[Desktop acceptance checklist](WINDOWS_HANDOVER/POWERBI_ACCEPTANCE_CHECKLIST.md)
provides the expected values and interactions. For authorized Desktop testing,
obtain the matching workbook independently and keep the imported PBIX local.
[Authorized rebuild](WINDOWS_HANDOVER/README_WINDOWS.md)

Record observed results in the [completion matrix](submission/COMPLETION_MATRIX.csv)
and [validation report](docs/VALIDATION_REPORT.md). The current draft review is
[PR #3](https://github.com/SamarthRamesha/when-nature-strikes/pull/3).
