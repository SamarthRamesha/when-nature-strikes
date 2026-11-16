# Statistical analysis

[Hazard estimates](../results/impact_by_type.csv) cover all recorded years
(1900–2026) and the 2000–2025 sensitivity window. The full series includes
partial 2026 for archival description. The file records sample size and reported
coverage next to each total, mean, median, standard deviation, interquartile
range, 90th and 99th percentile, and 99th-percentile-capped mean.
[Complete-country sensitivity](../results/complete_country_sensitivity.csv)
uses only events in which every participating country reports a given metric.

Frequency and the total of reported losses have a built-in relationship through
the number of reporting events. For deaths, affected population and adjusted
damage, the full-window Spearman coefficients with totals were 0.81, 0.89 and
0.70 across 13, 14 and 13 available hazard categories. Corresponding
median coefficients were −0.29, 0.15 and 0.05. Spearman tests are exploratory,
using 9,999 two-sided Monte Carlo permutations under an exchangeable-hazard null,
with Holm correction for nine tests per window. Pearson and Kendall
coefficients serve as sensitivity estimates. The Spearman 95% percentile
intervals use 2,000 hazard-pair bootstrap draws and exclude degenerate
replicates. Category resampling illustrates sensitivity to category composition.
The finite, related set of hazards and reporting patterns constrain inference.

[Distribution tests](../results/distribution_tests.csv) apply Kruskal–Wallis to
reported event losses across hazards with at least 20 reports, with Holm
correction over three metrics per window. Full-window epsilon-squared estimates
were 0.061 for deaths, 0.156 for affected counts and 0.030 for damage. The test
concerns rank distributions. Unequal shapes preclude reading it as a test of
isolated median shifts. Standard p-values also assume independent events, and
historical or regional dependence can weaken that assumption. A stored zero
p-value is numeric underflow, not a probability of zero.

The full-window median mortality leader, fog, has one reporting event. Among
types with 20 or more reports, drought leads with a median of 200 deaths, based
on 67 of 647 recorded droughts. Earthquakes replace droughts as the mean and
total mortality leaders in 2000–2025. Capping extreme losses changes the
full-window mean adjusted damage leader from earthquake to extreme temperature,
and the recent leader from earthquake to drought. Compare these sensitivity
checks before interpreting any ranking as stable.

At the exploratory 0.05 familywise threshold, the full-window total
associations meet the cutoff for deaths (adjusted p = 0.0104) and affected
population (0.0009). Adjusted damage total has p = 0.0749 in the full record
and p = 0.0018 in 2000–2025. No mean or median comparison meets that threshold
in either window. See the [coefficient and interval table](../results/correlations.csv).
