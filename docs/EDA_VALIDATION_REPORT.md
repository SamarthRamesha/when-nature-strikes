# EDA Validation Report — When Nature Strikes

Written by Samarth Ramesha (data/integration role) to verify the findings produced by Shashank
S K's analysis notebooks before they are used in the integrated dashboard.

## How this was verified

- **Independent recomputation.** `scripts/verify_eda_findings.py` re-derives findings **F1–F6**
  directly from `data/processed/natural_disaster_events.csv` using only the Python standard
  library (no pandas, no notebooks). It writes `analysis/outputs/eda_validation.json`.
- **Artefact comparison.** The same script compares its values with **89** values committed in
  `analysis/outputs/final_disaster_frequency.csv`, `disaster_pattern_summary.csv`,
  `final_reporting_coverage.csv`, `final_yearly_frequency.csv` and
  `final_impact_correlation.csv`. **All 89 match.**
- **Notebooks were not re-executed.** They are preserved untouched. Their stored outputs were used
  only to locate the claimed findings, and every claim below was re-derived from the data instead.
  The Spearman correlations agree with the committed matrix to within 6.0e-8 (floating-point
  summation order).
- **Commands:** `python scripts/validate_project_data.py` and
  `python scripts/verify_eda_findings.py`. Both exit 0.

**Denominator convention.** "Average" below always means the mean over **events that reported that
measure**, which is the notebooks' definition and the only defensible one. Averages over all
events would require pretending unreported impacts were zero.

---

## 1. Verified findings

### F1 — Flood is the most frequent natural disaster type ✅ Verified

| Item | Value |
|---|---|
| Metric | Distinct `Event ID` per `Disaster Type` |
| Dataset / grain | `natural_disaster_events.csv` — one consolidated event |
| Result | Flood **5,814 events** (36.97% of 15,727) |
| Runner-up | Storm 4,026 (25.6%), Earthquake 1,573, Epidemic 1,447 |
| Denominator | 15,727 consolidated events, 15 types |

Caveats: this is a count of *consolidated* events, not source rows. Counting country impacts
instead would give Flood 6,217 and inflate every type by up to 14.8%. The count also rises with
reporting capacity over time, so "most frequent" describes the compiled record, not a physical
hazard rate.

### F2 — Drought has the highest average deaths per event ✅ Verified

| Item | Value |
|---|---|
| Metric | Mean reported `Total Deaths` per event with a reported value |
| Dataset / grain | `natural_disaster_events.csv` — one consolidated event |
| Result | Drought **175,139.60** average deaths |
| Denominator | **67** drought events with reported deaths (10.4% coverage) |
| Runner-up | Epidemic 7,747.34 (1,243 reported events) |
| Median (drought) | **200** deaths |

Caveats: the ranking rests on **67 of 647** drought events, and the median (200) is three orders
of magnitude below the mean. A handful of catastrophic droughts drives this result. Report the
median, the reported-event count, and coverage on the same visual. By **total** deaths Drought also
leads (11.73M vs Epidemic 9.63M and Flood 7.03M), so this finding is robust to total-vs-average —
but not to the choice of statistic, so the caveat must be visible.

### F3 — Drought has the highest average affected population per event ✅ Verified

| Item | Value |
|---|---|
| Metric | Mean reported `Total Affected` per event with a reported value |
| Dataset / grain | `natural_disaster_events.csv` — one consolidated event |
| Result | Drought **6,349,540.46** average affected |
| Denominator | **477** drought events with reported affected (73.7% coverage) |
| Runner-up | Flood 805,689.88 |
| Median (drought) | 900,000 |

Caveats: same heavy-tail shape (median ≈ 14% of the mean). By **total** affected, Flood leads
(4.11B) ahead of Drought (3.03B) and Storm (1.43B) — so the "most destructive" answer depends on
whether the question asks per event or in aggregate. Affected counts can also double-count people
across successive events and are not deduplicated by person.

### F4 — Earthquake has the highest average adjusted economic damage per event ✅ Verified

| Item | Value |
|---|---|
| Metric | Mean reported `Total Damage, Adjusted (million US$)` per event with a reported value |
| Dataset / grain | `natural_disaster_events.csv` — one consolidated event |
| Result | Earthquake **2,881.02** million US$ average |
| Denominator | **626** earthquake events with reported damage (39.8% coverage) |
| Runner-up | Extreme temperature 2,391.10; Drought 2,228.70; Storm 1,667.40 |

Caveats: damage is reported for only **5,251 of 15,727 events (33.4%)** overall, and EM-DAT
documents economic-loss underreporting, especially outside insured markets. By **total** adjusted
damage, **Storm** leads (3.49M million US$ ≈ US$3.49 trillion) ahead of Flood (1.91T) and
Earthquake (1.80T). Earthquake leading the average while Storm leads the total is the clearest
illustration of the total-versus-average distinction in this project.

### F5 — 2000 is the year with the highest number of events ✅ Verified

| Item | Value |
|---|---|
| Metric | Distinct `Event ID` per `Start Year` |
| Dataset / grain | `natural_disaster_events.csv` — one consolidated event |
| Result | **2000: 489 events** |
| Next | 2002: 478; 2001: 413; 2006: 388; 1999: 382 |

Caveats: yearly counts track reporting capacity as much as hazard occurrence, and 2000 sits inside
a 1990s–2000s reporting expansion. The 2020s are truncated by the export (2026 is a partial year:
153 events). Prefer decade-level comparisons plus a visible Historic/2000-onward split.

### F6 — Event-level impact coverage ✅ Verified

| Measure | Reported events | Coverage | Missing |
|---|---|---|---|
| Deaths | 11,655 | 74.11% | 4,072 |
| Affected population | 12,366 | 78.63% | 3,361 |
| Adjusted economic damage | 5,251 | 33.39% | 10,476 |

Denominator: 15,727 consolidated events. These match
`analysis/outputs/final_reporting_coverage.csv` and `impact_reporting_coverage.csv` exactly.
Coverage describes reporting, not absence of impact.

### F7 — Spearman correlations between impacts ✅ Verified (via artefact comparison)

| Pair (event grain, pairwise-complete) | ρ |
|---|---|
| Deaths vs Affected | 0.34961 |
| Deaths vs Adjusted damage | 0.24451 |
| Affected vs Adjusted damage | 0.23265 |

F7 is not one of the six recomputed findings: the script recomputes the Spearman matrix and
verifies it against `analysis/outputs/final_impact_correlation.csv` inside the artefact
comparison (values reproduce to within 6e-8, floating-point summation order). Interpretation:
weak positive relationships only. Deaths, affected population and economic damage are largely
independent dimensions of destructiveness, which supports treating "destructiveness" as three
separate measures rather than one score.

---

## 2. Total versus average — why both belong on the dashboard

| Measure | Highest **total** | Highest **average per reported event** |
|---|---|---|
| Deaths | Drought 11.73M | Drought 175,140 (median 200) |
| Affected | Flood 4.11B | Drought 6.35M |
| Adjusted damage (million US$) | Storm 3.49M (≈US$3.49T) | Earthquake 2,881 |

A type can be frequent without being the most destructive *per event*, and a type can lead the
average without leading the total. The dashboard should show both, each with its coverage.

## 3. Answer to the research question (as supported by the data)

**No — frequency does not imply destructiveness.** Flood is the most frequent type (5,814 events,
37.0%) but ranks first on only one impact measure (total affected) and is not the leader on average
deaths, average affected or average damage. Drought and Earthquake — 4.1% and 10.0% of events
respectively — dominate average human and economic destructiveness. The weak rank correlations
(ρ = 0.23–0.35) confirm that frequency and impact are distinct dimensions.

This answer is conditional on reported data: damage coverage of 33.4% means economic
destructiveness is the least certain part of the conclusion.

---

## 4. What could not be verified

- **Notebook cell-level re-execution.** The notebooks retain stored outputs (10/11, 9/12, 22/25,
  22/26, 12/15 and 12/13 executed cells across the six notebooks) but were not re-run, to avoid
  regenerating charts and outputs. Findings were verified by independent recomputation instead.
- **Chart contents.** The 32 PNGs in `visualizations/` were not re-rendered or inspected
  pixel-by-pixel; the underlying tables they plot were verified.
- **Statistical significance.** No confidence intervals or hypothesis tests were recomputed;
  the reported correlations have no significance testing in the committed outputs.
- **Causal and normalisation claims.** No exposure, population or GDP normalisation exists in the
  data, so "destructiveness" cannot be adjusted for exposed population or wealth here.
- **Upstream EM-DAT quality.** Whether a blank means "no impact" or "unreported impact" is not
  determinable from the export; the reports treat blanks as unknown.

## 5. Data nuance found during validation

Three events — `1988-0424`, `1995-0275`, `1999-9388` — carry **different `Historic` flags across
their own country impacts**, so a per-event Historic attribute must be derived from `Start Year`
(verified equivalent: `Historic = Yes` ⟺ `Start Year < 2000` for all 7,137 flagged rows), not read
from a single country row. This affects no headline finding and is recorded so the dashboard team
does not build the filter from the wrong column.
