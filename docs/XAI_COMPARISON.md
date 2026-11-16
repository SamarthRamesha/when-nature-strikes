# XAI comparison

The selected classifier ranks retrospective high mortality on eligible single-country events with known deaths. The target indicates at least 100 reported deaths. The explanation code refits using the disjoint training era, then verifies average precision on the 834-event held-out set.

| Method | Question and result |
| --- | --- |
| Grouped SHAP | How much does each input change fitted log-odds relative to the training background? Hazard led, followed by region and month. Grouped contributions reconstruct the fitted score. |
| Held-out permutation | What changes after breaking the association with one original input? Across 40 permutations, hazard reduced average precision by 0.158 on average. Region reduced it by 0.013, and month by −0.002. Region and month changes were small relative to permutation variability. |
| LIME | How well does a local linear surrogate explain each scenario? Weighted R² for three invented profiles was 0.174, 0.094 and 0.197. The low fidelity limits interpretation of those weights. |
| PDP and ICE | What happens to predicted probabilities when we replace the month category? The saved curves show the held-out mean and 10th–90th percentile range plus individual invented profiles. Authorized reproduction exports actual individual curves locally. |

SHAP log-odds, LIME probability coefficients and changes in ranking accuracy have different meanings. Categorical perturbations avoid fractional dummy states and can still produce uncommon combinations. Month plots place discrete categories in calendar order. The explanation methods address fitted behavior and associations.

[Results and reproduction](../results/xai/) · [LIME paper](https://doi.org/10.1145/2939672.2939778) · [SHAP paper](https://proceedings.neurips.cc/paper_files/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html) · [Partial dependence and ICE implementation](https://scikit-learn.org/stable/modules/generated/sklearn.inspection.partial_dependence.html)
