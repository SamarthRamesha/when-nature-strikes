# Mortality model

The target indicates at least 100 **reported** deaths in an EM-DAT single-country
event. The threshold defines a reproducible retrospective contrast. Labels use
known deaths only. Hazard, affected region and start month are available from
event metadata. The design excludes year, IDs, losses, response fields, country
count and magnitude. Geography and calendar features may reflect reporting
differences as well as risk. There is no operational forecasting claim.

One row per Event ID enters exactly one time partition: training 2000–2017
(4,131 events, 431 positives), validation 2018–2021 (855, 63) and test 2022–2025
(834, 97). One-hot encoding is fitted only on training. Start month unknowns use
a category, and new categories transform to zeros. The prior baseline captures
prevalence. Logistic regression and random forest address a tabular task with
modest feature count. The process uses no oversampling and leaves probabilities
on their fitted prevalence scale. Validation AP chooses the final model and
positive F1 chooses each operating threshold.

Logistic regression led validation AP (0.268 vs 0.253) and test AP (0.288 vs
0.258 forest and 0.116 prior). The 95% class-stratified event bootstrap interval
for logistic AP is 0.222–0.370. Held-out ROC AUC is 0.709, Brier score 0.096,
accuracy 0.845 and macro F1 0.629. On the selected threshold, positive precision
is 0.340 and recall is 0.351. There were 671 true negatives, 66 false positives,
63 false negatives and 34 true positives. A lower threshold trades off precision
and recall. These test results apply to eligible reported events and reflect
distribution shift across time.

[Saved evidence](../results/model_metrics.json) records all metrics, validation
thresholds, per-class results and library versions. Rebuild the local fitted
model with `python -m src.model`.
