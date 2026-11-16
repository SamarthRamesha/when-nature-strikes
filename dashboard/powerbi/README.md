# Native Power BI project

Open the [synthetic Power BI project](../../submission/powerbi/demo/When_Nature_Strikes.pbip)
in current Power BI Desktop. It embeds 12 invented events and 13 impact rows
for immediate control testing. To point a new project at your authorized local CSVs:

```sh
python scripts/build_powerbi.py --output submission/powerbi/local/authorized --processed-data data/processed
```

The five native pages cover overview, frequency vs severity, temporal analysis,
geography and guided findings. The import model includes the original Power Query
queries, null handling, a single-direction event relationship, extended DAX,
synchronized slicers and the project theme. The generator uses Microsoft's
report-authoring CLI scaffold and its authoring definitions were validated by
that CLI. [Desktop build and test steps](../../WINDOWS_HANDOVER/POWERBI_BUILD_AND_TEST.md)
