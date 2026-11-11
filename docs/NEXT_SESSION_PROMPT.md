# Next Session Prompt

**Purpose.** Restore full project context in a chat that has never seen this repository, with no
shared memory, on any platform. Copy the block below into the new session as the first message.

**Maintained by:** whoever last worked on the repository. Update it before finishing a session — it is
part of the handover (`docs/AI_AGENT_HANDOVER_PROTOCOL.md` §5).

**Last updated:** 11 November 2026 (Samarth Ramesha, repository finalisation and publishing).

---

## Copy this prompt

```text
You are continuing an existing academic data-visualization project. Work directly in the
repository; do not rebuild finished work.

PROJECT
Title: "When Nature Strikes: A Visualization Approach to Determine the Impact of Natural Disasters".
Research question: are the most frequent natural disasters also the most destructive?
Data: EM-DAT (CRED / UCLouvain) public custom-request export, table version 2026-10-23, file dated
31 October 2026. 27,962 source records; 18,060 natural-hazard country impacts; 15,727 consolidated
events; 15 disaster types; 11,157 country-year-type groups; 1900-2026 (2026 partial).
Repository: https://github.com/SamarthRamesha/when-nature-strikes

MANDATORY FIRST STEPS (in this order)
1. Read README.md.
2. Read docs/TEAM_HANDOVER.md (current ownership, phase ledger, ordered tasks).
3. Read docs/AI_AGENT_HANDOVER_PROTOCOL.md (binding rules, including the handover you must perform
   before you finish).
4. Run: git status && git log --oneline -10 && git branch -a
5. Run the two data checks and confirm they exit 0:
   python scripts/validate_project_data.py     (71 checks: 69 pass, 2 documented warnings, 0 fail)
   python scripts/verify_eda_findings.py       (6 findings; 89/89 committed values reproduce)
6. Verify claims in the documents against the actual files before trusting them.

CURRENT STATE
- Data phase COMPLETE and verified: reproducible pipeline, four processed datasets, data dictionary,
  71-check validation, EDA findings verification (89/89 values), dashboard specification,
  integration documentation.
- Power BI dashboard: NOT STARTED. There is no .pbix in the repository. Do not claim it is complete.
- Geospatial page: BLOCKED until the shared .pbix exists.
- Final report / presentation: pending with the team.

OWNERSHIP (from docs/TEAM_HANDOVER.md - verify it is still current)
- Samarth Ramesha: data inspection, cleaning, preprocessing, consolidation, summaries,
  reproducibility, data dictionary, validation, handover, integration coordination. COMPLETE.
- Shashank S K: EDA, statistical analysis, findings, charts, metric validation. DELIVERED; narrative
  and metric re-validation open with him.
- Shreya Patil: main analytical Power BI dashboard (pages 1-3). NEXT OWNER, ownership pending her
  acknowledgement.
- Shreya S Mattimadu: geospatial component integrated as page 4 of the same dashboard file. Waiting.
If you are not sure who currently owns the work, read docs/TEAM_HANDOVER.md and ask the user.

KEY PATHS
- data/source/EM-DAT Custom Request Oct 31 2026.xlsx   source workbook, restricted, never modify
- data/processed/cleaned_natural_disaster_impacts.csv   18,060 x 53  country-impact grain
- data/processed/natural_disaster_events.csv            15,727 x 35  event grain (use this for frequency)
- data/processed/natural_disaster_type_summary.csv          15 x 19  type grain
- data/processed/natural_country_year_type_summary.csv  11,157 x 25  country x year x type grain
- scripts/prepare_emdat.py            rebuilds the four CSVs (rewrites in place)
- scripts/validate_project_data.py    data-quality validation, writes the reports
- scripts/verify_eda_findings.py      recomputes the headline findings
- analysis/*.ipynb, analysis/outputs/, visualizations/   Shashank's EDA (do not edit casually)
- docs/DASHBOARD_DATA_HANDOVER.md     the Power BI specification (model, DAX, pages, interactions)
- docs/DATA_HANDOVER.md               derivations, units, caveats
- docs/DATA_DICTIONARY.md             every column, unit, origin, fill rate, additivity rules
- docs/EDA_VALIDATION_REPORT.md       the six verified findings with denominators
- docs/FINAL_SUBMISSION_CHECKLIST.md  academic deliverables and their status

SETUP
python -m venv .venv && source .venv/bin/activate     (Windows: .venv\Scripts\activate)
python -m pip install -r requirements.txt             (openpyxl; only needed to rebuild data)
Validation and verification need only the Python standard library.

COMMANDS
python scripts/prepare_emdat.py          # only when the source data changes; must be byte-identical
python scripts/validate_project_data.py  # exit 0 required
python scripts/verify_eda_findings.py    # exit 0 required

ACCEPTANCE NUMBERS (reproduce before building on them)
15,727 events | 18,060 country impacts | 11,157 country-year-type groups | 15 types |
1,067 multi-country events | 32,842,715 reported deaths | 9,065,006,097 reported affected |
8,120,533.174 million US$ reported adjusted damage | coverage 74.1% / 78.6% / 33.4% |
Flood 5,814 events (37.0%) | 2000 busiest year (489) | Spearman rho 0.3496 / 0.2445 / 0.2327

KNOWN LIMITATIONS (must be stated in any output)
Missing is not zero: deaths missing 27.8% of country impacts, total affected 25.8%, adjusted damage
67.6%, magnitude 68.8%. Coordinates exist for 15.8% and are country-level. Pre-2000 records are lower
quality (three events have conflicting Historic flags - derive the period from Start Year < 2000).
2026 is partial (153 events). 3,185 events lack a complete start date. Magnitude is on five
incomparable scales. Impacts are not deduplicated across events. EM-DAT export is restricted: do not
redistribute it or upload it to external services.

NEXT ACTIONS (unless the user directs otherwise)
1. Read the three documents and run the two checks.
2. If the user is the dashboard owner: build one .pbix, load the four CSVs keeping blanks null,
   create DimType / DimCountry / DimYear / BridgeEventCountry, implement the measures in
   docs/DASHBOARD_DATA_HANDOVER.md section G.3, and prove they reproduce the acceptance numbers.
3. Build pages 1-3 (Overview, Frequency vs Destructiveness, Temporal) with one shared filter pane,
   coverage beside every impact measure, and a missing-data disclaimer on every page.
4. Hand the same file to Shreya S Mattimadu for page 4 (geographic), then run the integrated QA in
   docs/INTEGRATION_HANDOVER.md section 9.

RULES
- Never commit, push, merge or delete without the user's explicit authorisation for that action.
- Never claim completion without evidence from executed checks or inspected files.
- Never modify the source workbook, hand-edit the processed CSVs, edit the notebooks, or regenerate
  the charts unless the task requires it.
- Keep distribution of the EM-DAT data inside the project.

BEFORE YOU FINISH (required)
Prepare the handover for the next person even if the user does not ask: update
docs/TEAM_HANDOVER.md (status, evidence, ordered tasks, change log), docs/NEXT_SESSION_PROMPT.md
(this prompt), and README.md section "Current project status" if it materially changed. Then tell the
next agent to repeat this protocol recursively for the person after them.
```

---

## Notes for a human pasting this

- Replace nothing: the prompt is accurate as written for this commit range. If the phase status
  changes, update `docs/TEAM_HANDOVER.md` first, then regenerate this file.
- If the new chat cannot access the repository, give it `docs/PROJECT_OVERVIEW.md` and
  `docs/TEAM_HANDOVER.md` as attachments first — the prompt then still works.
- The prompt deliberately contains no credentials, no personal identifiers and no absolute paths.
