# When Nature Strikes

Data preparation for the Visualization of Data project **When Nature Strikes: A Visualization Approach to Determine the Impact of Natural Disasters**.

The project question is whether the most frequent natural disaster types are also the most destructive. This repository contains the EM-DAT source export, processed natural-disaster data at both country-impact and event grain, dashboard-ready summaries, the EM-DAT documentation, and a reproducible preparation script.

## Repository layout

```text
data/
  source/       Original EM-DAT custom-request workbook
  processed/    Clean natural-disaster impacts and dashboard summaries
docs/
  DATA_HANDOVER.md
  PROJECT_APPROVAL_SUMMARY.md
  EM_DAT_Documentation.pdf
scripts/
  prepare_emdat.py
```

The original approval deck is not included because it contains team names and student ID numbers. `docs/PROJECT_APPROVAL_SUMMARY.md` records the approved project direction without those identifiers. Teacher feedback and team-allocation screenshots were not among the supplied project materials.

## Data files

- `cleaned_natural_disaster_impacts.csv`: one natural disaster impact per country.
- `natural_disaster_events.csv`: one row per underlying event, aggregating the event's country impacts.
- `natural_disaster_type_summary.csv`: unique event counts and reported impacts by type.
- `natural_country_year_type_summary.csv`: country, year, and type aggregates for map and trend views.

Read `docs/DATA_HANDOVER.md` before using the data. It explains derivations, event grain, missing values, reporting coverage, measurement units, known limitations, and dashboard integration suggestions.

## Rebuild processed data

Requires Python 3.10+ and `openpyxl`:

```bash
python -m pip install -r requirements.txt
python scripts/prepare_emdat.py
```

The script reads the workbook in `data/source/` and rewrites the four CSV files in `data/processed/`.

## Provenance

The source workbook is an EM-DAT public custom-request export from CRED / UCLouvain, version 2026-10-23. The included documentation PDF defines the public-table fields and limitations. Cite EM-DAT as the data source in project outputs and follow EM-DAT's current terms of use.
