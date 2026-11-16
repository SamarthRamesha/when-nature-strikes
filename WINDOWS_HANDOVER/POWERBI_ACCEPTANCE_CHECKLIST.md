# Power BI acceptance checklist

Record Windows build, Desktop version, input mode and date. Check each item after observing the result. The [completion matrix](../submission/COMPLETION_MATRIX.csv) records the submission-time status.

| Full-scope metric | Invented demonstration | Authorized snapshot |
| --- | ---: | ---: |
| Distinct events | 12 | 15,727 |
| Country-impact records | 13 | 18,060 |
| Flood events | 6 | 5,814 |
| Reported deaths | 297 | 32,842,715 |
| Reported affected | 5,025 | 9,065,006,097 |
| Adjusted damage, USD millions | 1,762 | 8,120,533.174 |
| Death reporting events | 11 | 11,655 |
| Affected reporting events | 11 | 12,366 |
| Damage reporting events | 10 | 5,251 |
| Damage event coverage | 83.3% | 33.4% |
| Matched country-impact records | 12 | 17,269 |
| Unmatched country-impact records | 1 | 791 |

- [ ] All five tabs open and refresh. The cards match the intended input mode.
- [ ] A hazard or subgroup selection carries from Overview to the comparison, geographic and story pages.
- [ ] The year range and decade slicer update the time series and totals.
- [ ] In synthetic mode Bangladesh contributes two events. Its 1997 event contributes 800 affected and USD 5 million. Its deaths remain unknown. In the full scope the 1997 event still counts once.
- [ ] Switching impact, Total, Mean and Median updates the scatter. A tooltip shows count and coverage.
- [ ] The filled map responds to the selected measure and the bubble map shows adjusted damage by hazard. Synthetic ZZZ appears as unmatched in the country table.
- [ ] The Overview hazard bar highlights the subgroup chart. Selecting a country in either map filters the three original country ranking charts. Clear the selection to restore the rankings.
- [ ] The guided visuals lead from frequency to severity, time, geography and limitations.
- [ ] Save As PBIX, close, reopen and change a filter. Record the path and hash with `Get-FileHash -Algorithm SHA256`.

If Bing maps are unavailable, record map rendering as pending. The Power BI
rankings still give country and region comparisons. The local Streamlit
Geography view renders the bundled Natural Earth polygons.
