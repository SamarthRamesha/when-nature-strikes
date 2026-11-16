# Troubleshooting on Windows

| Symptom | Check |
| --- | --- |
| PowerShell execution is blocked | Read the scripts before executing. For files marked as downloaded, use your organization's approved procedure, or unblock the trusted ZIP in Explorer Properties and extract again. |
| Python 3.11 is absent | Install 64-bit Python 3.11 from python.org and reopen PowerShell. The installer tries `python` and the `py` launcher. |
| Workbook checksum differs | Request the exact 23 October 2026 export. Use the labeled synthetic demonstration if it is unavailable. |
| App asks for CSVs | Rebuild with `RUN_PIPELINE.ps1 -PrepareOnly` or start `RUN_STREAMLIT.ps1 -Synthetic`. |
| Local port is in use | Use `RUN_STREAMLIT.ps1 -Port 8766` and open the printed address. |
| Chromium is missing | Run `INSTALL_WINDOWS.ps1 -Browser`. The network must permit Playwright's browser download. |
| PBIP opens in another app | Open it from Desktop **File > Open**. Update Desktop if it rejects the PBIR format. |
| Power BI refresh can't find data | Rebuild and generate an authorized PBIP, or update `DataFolder` when moving the project. |
| No Azure Maps layer appears | Check Desktop security and organizational permissions for Azure Maps. Confirm internet access and compare against the country table. |
| Country counts add to more than the world count | A single event can affect several countries. Read distinct counts at the current grain and reported losses alongside their denominators. |
