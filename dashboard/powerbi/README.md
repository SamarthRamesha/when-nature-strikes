# Native Power BI project

Open the [synthetic Power BI project](../../submission/powerbi/demo/When_Nature_Strikes.pbip)
in current Power BI Desktop. It embeds 12 invented events and 13 impact rows
for immediate control testing. To point a new project at your authorized local CSVs:

```sh
python scripts/build_powerbi.py --output submission/powerbi/local/authorized --processed-data data/processed
```

The five native pages cover overview, frequency vs severity, temporal analysis,
geography and guided findings. The model uses the Power Query definitions and
DAX measures in this directory. The builder generates pages, synchronized
slicers, the custom theme and a fresh model, using the checked-in project for
shared report metadata and the Fluent base theme. The scaffold came from
Microsoft's authoring CLI. [Microsoft license notice](MICROSOFT_LICENSE.txt)

The PBIP passed Microsoft's file validator. Refresh, render and save/reopen
acceptance remain Windows Desktop steps. [Desktop build and test steps](../../WINDOWS_HANDOVER/POWERBI_BUILD_AND_TEST.md)
