# Literature review

## Synthesis

EM-DAT provides a broad, standardized record of disasters that meet its capture
criteria [1]. Its rows describe disaster impacts in a country. Cross-border
events therefore require consolidation before global frequency is measured.
Country views answer a different question about where an impact was recorded
[1, 4]. The project keeps primary types mutually exclusive and uses the country
ISO field to join contemporary boundaries. Associated hazards and historical
entities require additional event and geographic linkage [4, 5].

Jones et al. show that missing loss fields vary with observable factors such as
hazard, country income and year [2]. Gall et al. identify biases in disaster loss
databases by time, hazard, threshold, accounting, geography and systemic
coverage [3]. This evidence motivates recent-period and full-country-reporting
sensitivity analyses, a reporting denominator for every impact measure, and
attention to rare categories and catastrophic historical events. The effects of
unobserved missing losses remain unidentified.

A common reporting problem is to use one ranking as a proxy for several distinct
questions. A type may generate a high accumulated burden from many occurrences,
and it may have a lower median recorded loss than less common types. This
project pairs nine precisely defined rankings with consistent coverage and
adds chronological mortality classification for a narrow eligible cohort.
Precision-recall evaluation addresses the imbalance in reported high-mortality
events [6]. SHAP describes how hazard, region and month influence fitted scores
[7]. PCA summarizes variation in three measured impacts, and t-SNE and UMAP
compare local neighborhood structure [8–10]. Density-based clustering and
isolation scores probe structure and unusual profiles [11, 12]. These methods
address different questions, and all are conditional on the eligible records.

The dashboard aligns visualization and interaction with those distinct tasks
[13]. It exposes the reporting denominator next to each value, keeps geographic
slicers consistent, and preserves unmapped entries in tables. The gap addressed
is practical. Published data-quality and method studies inform a single
reproducible workflow where students can inspect how frequency, severity,
geography, and reporting jointly change an answer.

## Source matrix

| Ref. | Source | Research objective and method | Finding and limitation | Use here |
| --- | --- | --- | --- | --- |
| [1] | D. Delforge et al., “EM-DAT: the Emergency Events Database,” *International Journal of Disaster Risk Reduction*, 124, 105509, 2025. [DOI](https://doi.org/10.1016/j.ijdrr.2025.105509) | Technical review of coverage, collection, classification and access. | Global coverage with heterogeneous loss reporting and changes in recording practice. | Data provenance, event grain, caution on trends. |
| [2] | R. L. Jones, D. Guha-Sapir and S. Tubeuf, “Human and economic impacts of natural disasters: can we trust the global data?” *Scientific Data*, 9, 572, 2022. [DOI](https://doi.org/10.1038/s41597-022-01667-x) | Missingness diagnosis in 1990–2020 EM-DAT records using logistic regression. | Missingness associates with time, type and country income group. Observed covariates cannot explain all missingness. | Coverage labels and selection caveats. |
| [3] | M. Gall, K. A. Borden and S. L. Cutter, “When Do Losses Count? Six Fallacies of Natural Hazards Loss Data,” *Bulletin of the American Meteorological Society*, 90(6), 799–810, 2009. [DOI](https://doi.org/10.1175/2008BAMS2721.1) | Comparative assessment of loss database biases. | Six bias classes can distort comparisons. Context and definitions differ across datasets. | Historical and economic reporting sensitivity. |
| [4] | W. S. Jäger, M. C. de Ruiter, T. Tiggeloven and P. J. Ward, “What can we learn about multi-hazard impacts from global disaster records?” *Natural Hazards and Earth System Sciences*, 25, 2751–2769, 2025. [DOI](https://doi.org/10.5194/nhess-25-2751-2025) | Compare reported losses for single- and multi-hazard event configurations. | Data limitations constrain inference about impact amplification. | Keep associated hazard tags separate from primary counts. |
| [5] | E. L. Rosvold and H. Buhaug, “GDIS, a global dataset of geocoded disaster locations,” *Scientific Data*, 8, 61, 2021. [DOI](https://doi.org/10.1038/s41597-021-00846-6) | Geocode EM-DAT place names into administrative areas. | Spatial enrichment is possible for a subset of records using independent matching and checks. | Country-level interpretation for this project, which uses no GDIS linkage. |
| [6] | T. Saito and M. Rehmsmeier, “The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets,” *PLOS ONE*, 10(3), e0118432, 2015. [DOI](https://doi.org/10.1371/journal.pone.0118432) | Compare ROC and PR under changing class imbalance. | PR makes errors on the rare positive class visible. Prevalence affects PR. | Average precision selection and prior baseline. |
| [7] | S. M. Lundberg and S.-I. Lee, “A Unified Approach to Interpreting Model Predictions,” *NeurIPS*, 2017. [Proceedings](https://proceedings.neurips.cc/paper_files/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html) | Define additive feature attributions based on Shapley values. | Scores depend on the explained model and reference distribution. | Training-background, held-out explanations. |
| [8] | I. T. Jolliffe and J. Cadima, “Principal component analysis: a review and recent developments,” *Philosophical Transactions of the Royal Society A*, 374, 20150202, 2016. [DOI](https://doi.org/10.1098/rsta.2015.0202) | Review linear dimension reduction and variants. | PCA captures directions of maximum variance. Feature scales affect components. | Standardized log-impact PCA, loadings and scree. |
| [9] | L. van der Maaten and G. Hinton, “Visualizing Data using t-SNE,” *Journal of Machine Learning Research*, 9, 2579–2605, 2008. [Article](https://jmlr.org/papers/v9/vandermaaten08a.html) | Compare neighborhood visualizations using an affinity-matching objective. | Local neighborhoods can be retained. Far-apart distances are hard to interpret. | Two perplexity settings and neighborhood overlap. |
| [10] | L. McInnes, J. Healy and J. Melville, “UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction,” arXiv, 2018. [Preprint](https://arxiv.org/abs/1802.03426) | Construct low-dimensional representations using neighborhood graphs. | Choice of neighborhood and minimum distance changes the embedding. | Report parameter sensitivity alongside trustworthiness. |
| [11] | M. Ester, H.-P. Kriegel, J. Sander and X. Xu, “A Density-Based Algorithm for Discovering Clusters in Large Spatial Databases with Noise,” *KDD*, 1996. [Proceedings](https://cdn.aaai.org/KDD/1996/KDD96-037.pdf) | Identify density-connected clusters while retaining noise points. | Can discover irregular shapes. Density thresholds influence grouping. | Comparison against K-means and sensitivity to epsilon. |
| [12] | F. T. Liu, K. M. Ting and Z.-H. Zhou, “Isolation Forest,” *IEEE ICDM*, 2008. [DOI](https://doi.org/10.1109/ICDM.2008.17) | Detect anomalies through randomized partitioning. | Isolated observations often have shorter paths. Flag thresholds depend on the task. | Descriptive review of the top one percent of scores. |
| [13] | T. Munzner, “A Nested Model for Visualization Design and Validation,” *IEEE TVCG*, 15(6), 921–928, 2009. [Author publication page](https://www.cs.ubc.ca/labs/imager/tr/2009/NestedModel/) | Relate domain tasks, abstractions, encodings and implementation to distinct forms of validation. | Errors in task definition affect downstream choices. | Separate audit of grain, interactions and map rendering. |
| [14] | CRED / UCLouvain, “EM-DAT Public Table,” *EM-DAT Documentation*. [Reference](https://doc.emdat.be/docs/data-structure-and-content/emdat-public-table/) | Document the public-table structure, types and field semantics. | Country records describe reported impacts, and metric definitions constrain comparisons. | Damage units, impact scope and data dictionary. |
| [15] | Natural Earth, “Admin 0 Countries,” 1:110m cultural vector dataset. [Dataset](https://www.naturalearthdata.com/downloads/110m-cultural-vectors/110m-admin-0-countries/) | Provide generalized contemporary political boundaries. | Simplification omits some small territories and boundaries do not represent historical geography. | ISO-keyed polygons with an unmatched-record table. |
| [16] | S. Holm, “A Simple Sequentially Rejective Multiple Test Procedure,” *Scandinavian Journal of Statistics*, 6(2), 65–70, 1979. [Article](https://www.jstor.org/stable/4615733) | Derive a sequential adjustment for familywise error. | Controls familywise error when input tests are valid. | Nine planned Spearman comparisons per window and three omnibus impact tests per window. |
