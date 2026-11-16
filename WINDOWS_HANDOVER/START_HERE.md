# Start here on Windows

Extract to a short local path such as `C:\WNS`. Open PowerShell in the extracted project root.

1. Install 64-bit [Python 3.11](https://www.python.org/downloads/) and current [Power BI Desktop](https://learn.microsoft.com/power-bi/fundamentals/desktop-get-the-desktop).
2. Run these commands. Browser testing downloads Chromium once.

   ```powershell
   .\WINDOWS_HANDOVER\INSTALL_WINDOWS.ps1 -Browser
   .\WINDOWS_HANDOVER\RUN_TESTS.ps1 -Browser
   .\WINDOWS_HANDOVER\RUN_STREAMLIT.ps1 -Synthetic
   ```

3. Open [localhost port 8765](http://127.0.0.1:8765). The first five views use invented rows in synthetic mode. The other views show saved, labeled research cohorts.
4. In a second PowerShell window run `.\WINDOWS_HANDOVER\OPEN_POWERBI.ps1`. In Desktop refresh and use the [synthetic acceptance targets](POWERBI_ACCEPTANCE_CHECKLIST.md).
5. Open the [report](../submission/final_report.pdf), [slides](../submission/final_presentation.pdf) and [demo script](../submission/dashboard_demo_guide.md).

To reproduce the research instead, independently obtain the authorized export and follow [README_WINDOWS.md](README_WINDOWS.md).
