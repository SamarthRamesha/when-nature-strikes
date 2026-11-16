# SHAP explainability

The final logistic model uses LinearExplainer with an independent masker and
256 training records as background. The explanation sample uses 450 held-out
events with seed 661. Contributions use log-odds. Summing the encoded feature
contributions plus the expected value reconstructs the fitted margin within
(8.9 × 10⁻¹⁶) on the held-out sample.

Grouped mean absolute contributions were 0.415 for hazard, 0.346 for region and
0.182 for start month. The hazard group contribution is positive on average for
epidemics and earthquakes in the sample. Signed directions differ across hazard
groups. Month's unknown category can reflect data reporting. The background
distribution and dependent dummy encodings affect attribution. The fitted
linear model has no explicit interaction terms.

The [global bar](../results/figures/shap_global.png), [beeswarm](../results/figures/shap_beeswarm.png),
[local waterfall](../results/figures/shap_local.png), [hazard dependence](../results/figures/shap_hazard.png)
and [source summary](../results/shap_summary.json) describe the classifier's
behavior conditional on training and the labeled cohort.
