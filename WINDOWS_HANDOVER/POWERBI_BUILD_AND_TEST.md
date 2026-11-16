# Open refresh and save the native Power BI report

The five-page native report uses the enhanced PBIR format. Keep the `.pbip` entry, `.Report` directory and `.SemanticModel` directory together. [Microsoft documentation](https://learn.microsoft.com/power-bi/developer/projects/projects-report)

1. Install the latest [Power BI Desktop](https://learn.microsoft.com/power-bi/fundamentals/desktop-get-the-desktop). If your release exposes **File > Options and settings > Options > Preview features > Power BI Project (.pbip) save option**, enable it and restart Desktop.
2. Run `.\WINDOWS_HANDOVER\OPEN_POWERBI.ps1` for the self-contained synthetic project. For authorized analysis, first prepare the workbook, then run `.\WINDOWS_HANDOVER\OPEN_POWERBI.ps1 -Authorized`. If the file association is missing, use **File > Open** and select the printed path.
3. Select **Home > Refresh**. The demo has two embedded invented tables. The authorized project reads the two freshly prepared CSVs via the `DataFolder` parameter. If the authorized copy moves, regenerate the project or use **Transform data > Edit parameters > DataFolder** before refreshing.
4. In **Model view**, verify `DimEvent[Event ID]` (one) filters `FactImpacts[Event ID]` (many) in one direction. The three selector tables are disconnected. Hazard and year come from DimEvent. Geographic scope narrows FactImpacts before data are summarized. Empty loss cells are null and reported numeric zeros count.
5. Check the native marker visual on **Geographic analysis**. Azure Maps needs compatible Desktop settings and network access. Placement uses contemporary allowlisted ISO codes. Unmapped rows stay in the tables. [Azure Maps prerequisites](https://learn.microsoft.com/azure/azure-maps/power-bi-visual-get-started)
6. Run the [acceptance checklist](POWERBI_ACCEPTANCE_CHECKLIST.md). Select **File > Save As > Power BI Desktop file (.pbix)**. For authorized use, save to `submission\powerbi\When_Nature_Strikes.pbix` in the local copy. Use a distinct filename for the synthetic PBIX. Close and reopen what you saved, then test the filters. The real-data PBIX contains imported EM-DAT records.

## Visual and interaction checks

| Tab | Already authored | What to test |
| --- | --- | --- |
| Disaster overview | Five count/loss cards, hazard bars, a hazard ranking with all three reporting coverages | Check cards against the expected totals. Choose a hazard or geography and observe related visuals. |
| Frequency vs destructiveness | Hazard scatter with distinct events on X and chosen severity on Y. Table of total, mean, median and denominator | Change impact and summary selectors. Hover a hazard and check report count and coverage. |
| Temporal analysis | Annual stacked hazard frequency, death and affected trend with separate scales, adjusted damage line, era/decade table | Narrow years and decades. Check a damage tooltip and the visible partial-2026 warning. |
| Geographic analysis | Native Azure Maps by matched ISO, metric-driven marker size, coverage cards, country and region rankings | Toggle count and impact measures, then inspect a marker. Use country and region filters. Unmatched entries remain in the ranking. |
| Guided findings | Ordered frequency, total and mean charts, time series and regional comparison with a concluding explanation | Follow the indicated visual sequence. Change the shared impact selector and compare leaders. |

Use **View > Sync slicers** to inspect linked year, hazard, region, country and decade slicers. The impact metric syncs between comparison and guided pages. Use **Edit interactions** to inspect cross-filter behavior. The deployment gate is an actual Desktop refresh, Save As and reopen.

The generator reads [FactImpacts.m](../dashboard/powerbi/FactImpacts.m), [DimEvent.m](../dashboard/powerbi/DimEvent.m), [Measures.dax](../dashboard/powerbi/Measures.dax) and [theme.json](../dashboard/powerbi/theme.json) and registers the layouts. It preserves saved projects by requiring a new output directory. The [validation receipt](../submission/evidence/powerbi_author_cli.json) records authoring checks separately from Desktop acceptance.
