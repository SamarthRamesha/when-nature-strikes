# Clustering and anomalies

The clustering input is the standardized three-variable log-impact space used
for the embedding, before projection. K-means searched two to eight groups.
The maximum silhouette was 0.327 at k = 2. Davies–Bouldin was 1.171,
Calinski–Harabasz was 1,039, and median adjusted Rand agreement after 12
80% subsamples was 0.991. Agreement measures stability of this model under
subsampling. The moderate silhouette and sensitivity of density clusters show
limited evidence of sharply separated subgroups.

| Cluster | Events | Median deaths | Median affected | Median adjusted damage, USD millions |
| --- | ---: | ---: | ---: | ---: |
| 1 | 681 | 62 | 350,000 | 460.201 |
| 2 | 1,140 | 6 | 4,029 | 68.646 |

DBSCAN, with minimum samples 12 and three epsilons based on distance
quantiles, found one connected group plus 239, 91 or 18 noise records. Scores
that require two clusters are blank for those runs. Isolation Forest flags
19 records near the top 1% of anomaly scores for review. An outlying profile
can reflect a real catastrophe or recording characteristics.

[Evaluation](../results/cluster_evaluation.csv) and [plots](../results/figures/clusters_and_anomalies.png)
are public aggregates. Local reproduction writes event assignments and
anomaly scores to ignored `results/dimensionality_reduction/embeddings_local.csv`.
