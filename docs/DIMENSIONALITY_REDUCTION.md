# Dimensionality reduction

PCA, t-SNE and UMAP use the same 1,821 of 8,864 recent events with all three
losses observed for every participating country. The input is standardized
log1p of deaths, affected population and adjusted damage. This complete-case
representation emphasizes hazards with routine reporting. Metadata and IDs
do not enter the feature matrix. Hazard colors are added after fitting.

PCA explains 55.3%, 29.5% and 15.2% across three components. Positive PC1
coefficients indicate a common impact axis. PC2 emphasizes damage relative
to human impact. [Scree and components](../results/figures/pca_variance.png)
show these coefficients alongside cumulative variance.

The t-SNE fit uses PCA initialization, perplexity 30 and 850 iterations.
Its sensitivity run uses perplexity 50 and a different seed. UMAP uses
Euclidean metric, 25 neighbors and minimum distance 0.15. Its sensitivity run
uses 45 neighbors and minimum distance 0.35 with a different seed. For 15
neighbors, trustworthiness is 0.928 for PCA, 0.995 for t-SNE and 0.978 for
UMAP. Mean overlap of 15-neighbor sets under the sensitivity settings is
0.797 for t-SNE and 0.610 for UMAP. Each alternative changes parameters and
seed together, so the difference does not isolate either effect. PCA uses a
deterministic fit on this matrix. Nonlinear plot distances and gaps require
careful interpretation. See the [three projections](../results/figures/impact_embeddings.png)
and [diagnostics](../results/profile_summary.json).
