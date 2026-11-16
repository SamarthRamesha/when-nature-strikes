# Academic submission package

| Deliverable | Open |
| --- | --- |
| Research report | [PDF](final_report.pdf) · [Editable Word document](final_report.docx) |
| Presentation | [PDF](final_presentation.pdf) · [Editable PowerPoint](final_presentation.pptx) |
| Presenter materials | [Presenter script](presenter_script.md) · [Dashboard demonstration](dashboard_demo_guide.md) · [Viva questions](viva_questions.md) |
| Charts and evidence | [Final figures](../results/figures/) · [Validation](../docs/VALIDATION_REPORT.md) |
| Interactive dashboard | [Local browser setup](../docs/DASHBOARD_GUIDE.md) · [Power BI handover](../dashboard/powerbi/README.md) |
| Review | [Contributions](../docs/TEAM_CONTRIBUTIONS.md) · [Submission checklist](../docs/FINAL_SUBMISSION_CHECKLIST.md) |

The report and deck are technical submission drafts for team and faculty review.
The browser app uses the locally rebuilt EM-DAT tables. The Power BI handover
contains authoring sources for a Windows build.

## Rebuild editable and PDF artifacts

After running the analytical pipeline and capturing the dashboard screenshots
as described in the dashboard guide, use the repository root:

```sh
python scripts/build_report.py
node scripts/build_presentation.mjs
soffice --headless --convert-to pdf --outdir submission \
  submission/final_report.docx submission/final_presentation.pptx
python scripts/check_submission.py
```

The deck builder uses the Codex workspace bundle of `@oai/artifact-tool`.
Use Node 22+ with that package resolvable, or set `ARTIFACT_TOOL_ENTRY` to
its absolute JavaScript entry path. LibreOffice exports the PDFs. A renderer
can produce slightly different pagination if the Aptos font is unavailable.
