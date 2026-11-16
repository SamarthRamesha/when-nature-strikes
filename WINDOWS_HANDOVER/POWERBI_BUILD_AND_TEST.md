# Open, refresh and save the integrated report

Use Power BI Desktop with enhanced PBIR support. Keep the `.pbip`, `.Report`
and `.SemanticModel` together. [Microsoft project documentation](https://learn.microsoft.com/power-bi/developer/projects/projects-report)

For the academic analysis, run the checksum-gated workbook preparation,
then open the authorized project. This generates a fresh project with the
local Windows `DataFolder` parameter.

```powershell
.\WINDOWS_HANDOVER\RUN_PIPELINE.ps1 -Workbook 'C:\Data\authorized-export.xlsx' -PrepareOnly
.\WINDOWS_HANDOVER\OPEN_POWERBI.ps1 -Authorized
```

`OPEN_POWERBI.ps1` without a switch opens the same five-page project with
12 invented events for interface testing. It labels all five pages as
synthetic. If the authorized copy moves, update `DataFolder` or regenerate it.
[Authorized workbook and setup](README_WINDOWS.md)

| Tab | What to verify in Desktop |
| --- | --- |
| Disaster Overview | Confirm distinct events, country records, impacts and reporting coverage. Select a hazard bar and check the subgroup highlight. |
| Frequency vs Destructiveness | Change the metric and total, mean or median controls. Check the scatter tooltip against the reporting denominator. |
| Temporal Analysis | Narrow year and decade controls. Compare annual losses and the partial-2026 label. |
| Geographic Analysis | Exercise Shreya S Mattimadu’s bubble and filled maps, country rankings and region table. Map selections should filter the original rankings. Check unmatched ISO codes. |
| Guided Findings | Follow frequency, total severity, typical severity, time and geography. Change the shared impact selector. |

Use **View → Sync slicers** to verify year, hazard, subgroup, country, region
and decade. Model view should show one relationship from `DimEvent[Event ID]`
to `FactImpacts[Event ID]`. Country filters scope the contributing records.

The two original maps use Bing, which requires allowed map visuals and service
access. This project uses the original Bing visuals and no Azure Maps tenant
connection. If the maps are unavailable, test the country and region rankings
and use the local Streamlit Geography view for the map. [Microsoft map requirements](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-filled-maps-choropleths)

In Desktop, refresh and complete the [acceptance checklist](POWERBI_ACCEPTANCE_CHECKLIST.md).
Save the authorized report as `submission\powerbi\When_Nature_Strikes.pbix`,
close and reopen it, and record the Desktop version and file hash. Keep the
imported EM-DAT PBIX local. [Model reconciliation](../docs/RECOVERY_AND_POWER_BI.md)
