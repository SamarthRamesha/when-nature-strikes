"""Complete-case impact profiles and exploratory structure diagnostics."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.manifold import TSNE, trustworthiness
from sklearn.metrics import adjusted_rand_score, calinski_harabasz_score, davies_bouldin_score, silhouette_score
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits
from umap import UMAP

from .metrics import ID, METRICS, OUT, SHORT, TYPE, YEAR, load_data
from .statistics import INK, TEAL, save
from .projection_output import DEST, publish

SEED = 661
METHODS = ["PCA", "t-SNE", "UMAP"]


def impact_matrix(events):
    recent = events.loc[events[YEAR].between(2000, 2025)].copy()
    full = pd.DataFrame({metric: recent[f"{metric} Reported Country Impacts"].eq(
        recent["Country Impact Records"]) for metric in METRICS})
    complete = recent.loc[full.all(axis=1) & recent[list(METRICS)].notna().all(axis=1)].copy()
    matrix = complete[list(METRICS)].to_numpy()
    if (matrix < 0).any():
        raise ValueError("Negative impacts cannot enter the log1p representation.")
    return recent, complete, StandardScaler().fit_transform(np.log1p(matrix))


def neighbors(projection, count=15):
    return NearestNeighbors(n_neighbors=count).fit(projection).kneighbors(return_distance=False)


def overlap(a, b):
    return float(np.mean([len(set(x) & set(y)) / len(x) for x, y in zip(a, b)]))


def cluster(x, rng):
    rows = []
    fits = {}
    for k in range(2, 9):
        model = KMeans(n_clusters=k, n_init=20, random_state=SEED).fit(x)
        labels = model.labels_
        stability = []
        for iteration in range(12):
            sample = rng.choice(len(x), int(.8 * len(x)), replace=False)
            replica = KMeans(n_clusters=k, n_init=10, random_state=SEED + iteration).fit(x[sample])
            stability.append(adjusted_rand_score(labels, replica.predict(x)))
        rows.append({"method": "K-means", "k": k, "silhouette": silhouette_score(x, labels),
                     "davies_bouldin": davies_bouldin_score(x, labels),
                     "calinski_harabasz": calinski_harabasz_score(x, labels),
                     "median_subsample_ari": float(np.median(stability)),
                     "smallest_cluster": int(np.bincount(labels).min()), "noise": 0})
        fits[k] = labels
    k_ref = max(rows, key=lambda result: result["silhouette"])["k"]
    distances = NearestNeighbors(n_neighbors=12).fit(x).kneighbors()[0][:, -1]
    for percentile in (.70, .85, .95):
        epsilon = max(float(np.quantile(distances, percentile)), 1e-6)
        labels = DBSCAN(eps=epsilon, min_samples=12).fit_predict(x)
        valid = labels >= 0
        groups = np.unique(labels[valid])
        eligible = len(groups) >= 2
        rows.append({"method": "DBSCAN", "k": len(groups), "epsilon": epsilon,
                     "smallest_cluster": int(np.bincount(labels[valid]).min()) if len(groups) else 0,
                     "silhouette": silhouette_score(x[valid], labels[valid]) if eligible else None,
                     "davies_bouldin": davies_bouldin_score(x[valid], labels[valid]) if eligible else None,
                     "calinski_harabasz": calinski_harabasz_score(x[valid], labels[valid]) if eligible else None,
                     "noise": int((~valid).sum())})
    return k_ref, fits[k_ref], rows


def run():
    (OUT / "figures").mkdir(parents=True, exist_ok=True)
    events, _ = load_data()
    recent, full, x = impact_matrix(events)
    rng = np.random.default_rng(SEED)
    pca = PCA().fit(x)
    pca_projection = pca.transform(x)
    coordinates = [pca_projection[:, :2]]
    alternatives = [coordinates[0]]
    for perplexity, seed in [(30, SEED), (50, SEED + 1)]:
        target = coordinates if perplexity == 30 else alternatives
        target.append(TSNE(perplexity=perplexity, init="pca", learning_rate="auto",
                           max_iter=850, random_state=seed, n_jobs=1).fit_transform(x))
    for n_neighbors, min_dist, seed in [(25, .15, SEED), (45, .35, SEED + 1)]:
        target = coordinates if n_neighbors == 25 else alternatives
        target.append(UMAP(n_neighbors=n_neighbors, min_dist=min_dist, metric="euclidean",
                           random_state=seed, n_jobs=1, compatibility_layout=True).fit_transform(x))
    quality = {name: dict(trustworthiness_15=trustworthiness(x, xy, n_neighbors=15),
                          sensitivity_neighbor_overlap_15=overlap(neighbors(xy), neighbors(alt)))
               for name, xy, alt in zip(METHODS, coordinates, alternatives)}
    k, labels, evaluation = cluster(x, rng)
    anomalies = IsolationForest(n_estimators=180, random_state=SEED, n_jobs=1).fit(x)
    score = -anomalies.score_samples(x)
    full["cluster"] = labels + 1
    full["anomaly_score"] = score
    full["anomaly_flag"] = score >= np.quantile(score, .99)
    for name, xy in zip(METHODS, coordinates):
        full[f"{name} 1"], full[f"{name} 2"] = xy.T
    full["PCA 3"] = pca_projection[:, 2]
    publish(full)
    output_fields = [ID, TYPE, YEAR, *METRICS, "cluster", "anomaly_score", "anomaly_flag"]
    full[output_fields + [f"{name} {dim}" for name in METHODS for dim in (1, 2)] + ["PCA 3"]].to_csv(
        DEST / "embeddings_local.csv", index=False)
    profile = full.groupby("cluster")[list(METRICS)].median().join(full.groupby("cluster").size().rename("n"))
    profile.to_csv(OUT / "cluster_profiles.csv")
    eval_frame = pd.DataFrame(evaluation)
    eval_frame.to_csv(OUT / "cluster_evaluation.csv", index=False)
    loadings = pd.DataFrame(pca.components_.T, index=list(METRICS), columns=["PC1", "PC2", "PC3"])
    loadings.to_csv(OUT / "pca_components.csv")
    payload = {"seed": SEED, "recent_events": len(recent), "complete_events": len(full),
               "eligible_hazards": int(full[TYPE].nunique()), "hazard_coverage": (
                   full[TYPE].value_counts() / recent[TYPE].value_counts()).fillna(0).to_dict(),
               "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
               "embedding_diagnostics": quality,
               "settings": {"t-SNE": [30, 50], "UMAP": [[25, .15], [45, .35]], "neighbors_scored": 15},
               "reproduction": {"features": list(METRICS), "transformation": "standardize log1p losses",
                                "t_sne_max_iterations": 850, "t_sne_init": "pca", "umap_metric": "euclidean",
                                "umap_legacy_compatibility": True, "years": [2000, 2025],
                                "complete_country_reporting_required": True,
                                "scales": dict(zip(METRICS, x.std(axis=0).tolist()))},
               "kmeans_reference_k": k, "cluster_metrics": evaluation[k-2],
               "anomaly_flags": int(full.anomaly_flag.sum())}
    (OUT / "profile_summary.json").write_text(json.dumps(payload, indent=2) + "\n")

    groups = full[TYPE].where(full[TYPE].isin(full[TYPE].value_counts().head(5).index), "Other")
    colors = ["#087f80", "#ad4829", "#594a91", "#497ca5", "#9b761f", "#929baa"]
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.6), layout="constrained")
    for ax, name, xy in zip(axes, METHODS, coordinates):
        for hazard, color in zip(sorted(groups.unique()), colors):
            take = groups.eq(hazard).to_numpy()
            ax.scatter(xy[take, 0], xy[take, 1], s=9, alpha=.42, label=hazard,
                       color=color, linewidths=0)
        ax.set(title=f"{name} | T₁₅ = {quality[name]['trustworthiness_15']:.3f}",
               xlabel=f"{name} dimension 1", ylabel=f"{name} dimension 2")
    handles, labels_legend = axes[-1].get_legend_handles_labels()
    fig.legend(handles, labels_legend, loc="outside lower center", ncol=len(handles), frameon=False)
    fig.suptitle(f"Impact profiles of {len(full):,} fully reporting events, 2000–2025", fontsize=16, color=INK)
    save(fig, "impact_embeddings")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), layout="constrained")
    ratios = pca.explained_variance_ratio_
    axes[0].bar([1, 2, 3], ratios, color=TEAL)
    axes[0].plot([1, 2, 3], np.cumsum(ratios), "o-", color=INK, label="Cumulative share")
    axes[0].set(title="PCA scree and cumulative variance", xlabel="Principal component",
                ylabel="Explained variance fraction", xticks=[1, 2, 3], ylim=(0, 1.07))
    axes[0].legend(frameon=False)
    loadings.rename(index=SHORT).plot.barh(ax=axes[1], color=[TEAL, "#ad4829", INK])
    axes[1].set(title="Component coefficients", xlabel="Eigenvector coefficient")
    save(fig, "pca_variance")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), layout="constrained")
    for label in sorted(full.cluster.unique()):
        mask = full.cluster.eq(label)
        axes[0].scatter(coordinates[0][mask, 0], coordinates[0][mask, 1],
                        c=colors[(label-1) % len(colors)], label=f"{label} ({mask.sum()})", s=9, alpha=.5)
    axes[0].legend(title="Cluster (n)", frameon=False)
    flag = full.anomaly_flag
    axes[1].scatter(*coordinates[0].T, s=7, alpha=.23, color=TEAL)
    axes[1].scatter(*coordinates[0][flag].T, s=23, color="#ad4829", label=f"Flagged ({flag.sum()})")
    axes[1].legend(frameon=False)
    for ax, title in zip(axes, (f"K-means reference partition, k = {k}", "Isolation Forest top 1% score")):
        ax.set(title=title, xlabel="PC1", ylabel="PC2")
    save(fig, "clusters_and_anomalies")


if __name__ == "__main__":
    with threadpool_limits(limits=1):
        run()
