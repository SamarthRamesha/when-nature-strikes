# Viva preparation

**Why EM-DAT?** It provides a consistent global source for recorded disaster
occurrence and impacts. Its inclusion thresholds and reporting biases define
the population we can study. Historical coverage and missing losses limit
comparison.

**Why consolidate events?** A cross-border disaster can occupy several source
rows. Counting each Event ID once measures global recorded frequency, while
country-impact records support separate loss contributions and maps.

**Why preserve blanks?** An unknown impact may be large or small. Filling
with zero would increase the reporting count and mechanically lower averages.
An explicit numeric zero remains observed. An all-unknown group stays unknown.

**How do frequency and destructiveness differ?** Frequency counts events.
A reported total combines reporting counts and severity. Mean and median
describe per-report severity. Flood leads total affected, storm leads total
adjusted damage, and earthquake leads mean adjusted damage.

**Why can averages mislead?** Rare large observations can dominate a mean,
and sparse hazard classes may have few reporting events. The fog median is
based on one event. Compare the reporting count, median, quantiles and
winsorized mean before treating a rank as stable.

**Why use two time windows?** The full window describes the archive. The
2000–2025 window reduces historical inconsistency and excludes incomplete
2026. A ranking that reverses across these windows depends on period selection.

**How were significance claims controlled?** The exploratory Spearman family
uses Holm-adjusted p-values and category bootstrap intervals. A separate
Kruskal–Wallis family assesses rank distributions by hazard. Reporting
selection, related hazards and event dependence limit generalization.

**How did you address leakage?** Select one row per eligible Event ID, split
in chronological order, fit the encoder on training, tune the model and
decision threshold on validation, and reserve 2022–2025 for testing. No
impact or response field enters the predictors.

**Why average precision?** The positive class is infrequent. Average
precision summarizes precision and recall over thresholds and can be compared
with the prior baseline. Also inspect AUC, Brier score, per-class metrics and
the confusion matrix. Recall at our chosen cutoff was about 35%.

**Why SHAP?** It splits fitted log-odds into additive contributions relative
to training reference records. The hazard group contributed most on average.
Feature dependence and missingness influence the explanations, and the
explanations describe model behavior.

**Why PCA, t-SNE and UMAP?** PCA summarizes variance in linear components.
t-SNE and UMAP emphasize neighborhoods and are more sensitive to settings.
Comparing all three shows which aspects of the observed profile are stable.
The sample comprises complete recent reports, so it is selective.

**Why test two clustering methods?** K-means gives a reproducible partition
of standardized impact profiles. DBSCAN probes density-connected groups
without prespecifying their count. The results support a broad gradient with
some unusually isolated observations.

**Why these dashboard metrics?** Count, total, mean and median represent
different decisions. Reporting coverage exposes the denominator. Geography
uses country records and distinguishes mapped and unmatched codes.

**Does a high country count mean high individual risk?** The count is an
absolute recorded event count within a country. A relative-risk analysis
needs an exposure denominator and a definition of the population at risk.

**What remains for institutional acceptance?** Confirm individual contributions,
AI disclosure, report format and evaluator acceptance of the Streamlit format.
A native PBIX requires Windows Power BI authoring if the institution requests it.
