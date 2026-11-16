# Academic submission package

| Deliverable | Open |
| --- | --- |
| Research report | [PDF](final_report.pdf) · [Editable Word document](final_report.docx) |
| Presentation | [PDF](final_presentation.pdf) · [Editable PowerPoint](final_presentation.pptx) |
| Presenter materials | [Presenter script](presenter_script.md) · [Dashboard demonstration](dashboard_demo_guide.md) · [Viva questions](viva_questions.md) |
| Charts and evidence | [Final figures](../results/figures/) · [Validation](../docs/VALIDATION_REPORT.md) |
| Interactive dashboard | [Local browser setup](../docs/DASHBOARD_GUIDE.md) · [Power BI handover](../dashboard/powerbi/README.md) |
| Review | [Contributions and academic review](../docs/TEAM_CONTRIBUTIONS.md) · [Completion matrix](COMPLETION_MATRIX.csv) |

The report and deck are submission copies for team and faculty review.
Both dashboards support a synthetic demo and locally rebuilt authorized data.
[Deliverables manifest](DELIVERABLES_MANIFEST.md)

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
