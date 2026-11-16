# Native Power BI project

Open the [synthetic Power BI project](../../submission/powerbi/demo/When_Nature_Strikes.pbip)
in current Power BI Desktop. It embeds 12 invented events and 13 impact rows
for immediate control testing. To point a new project at your authorized local CSVs:

```sh
python scripts/build_powerbi.py --output submission/powerbi/local/authorized --processed-data data/processed
```

The five native pages incorporate the two team reports and the Guided Findings
page. The model uses the Power Query definitions and DAX measures in this
directory. The builder rebinds the 54 source visuals from `team_visuals.json`
to the shared model, adds synchronized controls and uses the checked-in report
metadata and theme. [Model reconciliation](../../docs/RECOVERY_AND_POWER_BI.md)
· [Microsoft license notice](MICROSOFT_LICENSE.txt)

The PBIP passed Microsoft's file validator with zero errors and two legacy
map warnings. Refresh, rendering and save/reopen remain Windows Desktop
steps. [Desktop build and test steps](../../WINDOWS_HANDOVER/POWERBI_BUILD_AND_TEST.md)
