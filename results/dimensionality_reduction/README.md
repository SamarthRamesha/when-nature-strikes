# Saved impact projections

`projection_cells.csv` supplies aggregate cells for two- and three-dimensional PCA and two-dimensional t-SNE and UMAP. Cells are split by hazard group or cluster. The displayed position is the cell center and size is count. Cells with fewer than five events are omitted.

Run `python -m src.profiles` against the authorized data to create local `embeddings_local.csv` with exact event coordinates, cluster labels and anomaly scores. The [profile summary](../profile_summary.json) stores settings, variance and neighborhood diagnostics. Inspect [loadings](../pca_components.csv), [cluster evaluation](../cluster_evaluation.csv) and [interpretation](../../docs/DIMENSIONALITY_REDUCTION.md). The public `anomaly_summary.csv` shows counts and score ranges where at least five profiles were flagged.
