"""Chronological retrospective classification of reported high mortality."""
import hashlib
import json
from importlib.metadata import version

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, average_precision_score, brier_score_loss,
                             classification_report, confusion_matrix, f1_score,
                             precision_recall_curve, roc_auc_score)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder

from .metrics import DEATHS, ID, OUT, PROCESSED, TYPE, YEAR, load_data
from .statistics import INK, TEAL, save

SEED = 661
FEATURES = [TYPE, "Region", "Start Month"]
THRESHOLD = 100
SPLITS = {"train": (2000, 2017), "validation": (2018, 2021), "test": (2022, 2025)}


def cohorts(events, impacts):
    eligible = events.loc[events["Country Impact Records"].eq(1), [ID, YEAR, DEATHS]]
    meta = impacts[[ID, *FEATURES]].drop_duplicates(ID)
    cohort = eligible.merge(meta, on=ID, validate="one_to_one").dropna(subset=[DEATHS])
    cohort["Start Month"] = cohort["Start Month"].astype("Int64").astype("string")
    cohort[FEATURES] = cohort[FEATURES].fillna("Unknown").astype(str)
    cohort["high_mortality"] = cohort[DEATHS].ge(THRESHOLD).astype(int)
    return {name: cohort[cohort[YEAR].between(*bounds)].copy() for name, bounds in SPLITS.items()}


def candidates():
    estimators = {
        "Prior baseline": DummyClassifier(strategy="prior"),
        "Logistic regression": LogisticRegression(C=1, max_iter=1000, random_state=SEED),
        "Random forest": RandomForestClassifier(n_estimators=240, max_depth=7, min_samples_leaf=18,
                                                n_jobs=1, random_state=SEED),
    }
    return {name: make_pipeline(OneHotEncoder(handle_unknown="ignore", sparse_output=False), estimator)
            for name, estimator in estimators.items()}


def operating_point(y, scores):
    precision, recall, thresholds = precision_recall_curve(y, scores)
    harmonic = 2 * precision[:-1] * recall[:-1] / np.maximum(precision[:-1] + recall[:-1], 1e-15)
    return float(thresholds[np.argmax(harmonic)])


def evaluate(y, scores, threshold):
    predicted = scores >= threshold
    return {"average_precision": average_precision_score(y, scores), "roc_auc": roc_auc_score(y, scores),
            "brier": brier_score_loss(y, scores), "accuracy": accuracy_score(y, predicted),
            "macro_f1": f1_score(y, predicted, average="macro"), "confusion": confusion_matrix(y, predicted).tolist(),
            "by_class": classification_report(y, predicted, output_dict=True, zero_division=0)}


def heldout_intervals(y, scores):
    rng = np.random.default_rng(SEED)
    groups = [np.flatnonzero(y == label) for label in (0, 1)]
    draws = []
    for _ in range(800):
        idx = np.concatenate([rng.choice(group, len(group), replace=True) for group in groups])
        draws.append((average_precision_score(y[idx], scores[idx]), roc_auc_score(y[idx], scores[idx])))
    return dict(zip(["average_precision", "roc_auc"], np.quantile(draws, [.025, .975], axis=0).T.tolist()))


def explain(name, model, train, test):
    import shap

    encoder, estimator = model.steps[0][1], model.steps[1][1]
    names = encoder.get_feature_names_out(FEATURES).tolist()
    sample = test.sample(n=min(450, len(test)), random_state=SEED).copy()
    background = encoder.transform(train.sample(n=min(256, len(train)), random_state=SEED)[FEATURES])
    design = encoder.transform(sample[FEATURES])
    if name == "Random forest":
        raw = shap.TreeExplainer(estimator, background, feature_perturbation="interventional",
                                 model_output="probability")(design)[:, :, 1]
        expected = model.predict_proba(sample[FEATURES])[:, 1]
        units = "probability"
    else:
        raw = shap.LinearExplainer(estimator, shap.maskers.Independent(background, max_samples=256))(design)
        expected = estimator.decision_function(design)
        units = "log-odds"
    np.testing.assert_allclose(raw.base_values + raw.values.sum(axis=1), expected, atol=1e-6, rtol=0)
    explained = shap.Explanation(values=raw.values, base_values=raw.base_values,
                                 data=design, feature_names=names)
    shap.plots.beeswarm(explained, max_display=11, show=False, plot_size=(9.6, 5.2))
    save(plt.gcf(), "shap_beeswarm")
    grouped = np.column_stack([raw.values[:, [i for i, n in enumerate(names)
                                               if n.startswith(f"{feature}_")]].sum(axis=1)
                               for feature in FEATURES])
    global_importance = pd.Series(abs(grouped).mean(axis=0), index=FEATURES).sort_values()
    fig, ax = plt.subplots(figsize=(8, 3.7), layout="constrained")
    ax.barh(global_importance.index, global_importance.values, color=TEAL)
    ax.set(title=f"Global SHAP importance ({len(sample)} held-out events)",
           xlabel=f"Mean absolute grouped contribution ({units})")
    save(fig, "shap_global")
    scores = model.predict_proba(sample[FEATURES])[:, 1]
    idx = int(np.argmax(scores))
    shap.plots.waterfall(explained[idx], max_display=9, show=False)
    save(plt.gcf(), "shap_local")
    per_hazard = pd.DataFrame(grouped, columns=FEATURES).assign(hazard=sample[TYPE].to_numpy())
    counts = per_hazard.groupby("hazard").size()
    keep = counts[counts >= 12].sort_index().index
    fig, ax = plt.subplots(figsize=(9, 4.7), layout="constrained")
    ax.boxplot([per_hazard.loc[per_hazard.hazard.eq(h), TYPE] for h in keep],
               tick_labels=[f"{h} ({counts[h]})" for h in keep], orientation="horizontal", showfliers=False)
    ax.axvline(0, color="#808080")
    ax.set(title="Hazard group contributions on held-out records", xlabel=f"Grouped SHAP ({units})")
    save(fig, "shap_hazard")
    return {"model": name, "events": len(sample), "output_units": units,
            "max_additivity_error": float(np.max(abs(raw.base_values + raw.values.sum(axis=1) - expected))),
            "mean_absolute_group_shap": global_importance.to_dict(),
            "local_example": {"probability": float(scores[idx]),
                              "base_value": float(raw.base_values[idx]),
                              "grouped_contributions": dict(zip(FEATURES, grouped[idx].tolist()))},
            "hazard_mean_signed_shap": per_hazard.groupby("hazard")[FEATURES].mean().loc[keep].to_dict("index")}


def run():
    (OUT / "figures").mkdir(parents=True, exist_ok=True)
    events, impacts = load_data()
    train, val, test = cohorts(events, impacts).values()
    models = candidates()
    valid = {}
    for name, model in models.items():
        model.fit(train[FEATURES], train.high_mortality)
        scores = model.predict_proba(val[FEATURES])[:, 1]
        valid[name] = {"average_precision": average_precision_score(val.high_mortality, scores),
                       "threshold": operating_point(val.high_mortality, scores)}
    selected = max(("Logistic regression", "Random forest"), key=lambda name: valid[name]["average_precision"])
    y = test.high_mortality.to_numpy()
    performance, test_scores = {}, {}
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), layout="constrained")
    for name, model in models.items():
        scores = model.predict_proba(test[FEATURES])[:, 1]
        test_scores[name] = scores
        performance[name] = evaluate(y, scores, valid[name]["threshold"])
        precision, recall, _ = precision_recall_curve(y, scores)
        axes[0].step(recall, precision, where="post", label=f"{name} ({performance[name]['average_precision']:.3f})")
        if name != "Prior baseline":
            observed, predicted = calibration_curve(y, scores, n_bins=6, strategy="quantile")
            axes[1].plot(predicted, observed, "o-", label=name)
    axes[0].set(title="Held-out precision and recall", xlabel="Recall", ylabel="Precision")
    axes[1].plot([0, .4], [0, .4], linestyle=":", color=INK)
    axes[1].set(title="Held-out calibration", xlabel="Mean predicted probability", ylabel="Observed positive fraction")
    for ax in axes:
        ax.legend(frameon=False, fontsize=8)
    fig.supxlabel(f"2022–2025 | n = {len(test):,} | {int(y.sum())} events with at least {THRESHOLD} reported deaths", fontsize=9)
    save(fig, "model_evaluation")
    with (PROCESSED / "natural_disaster_events.csv").open("rb") as event_csv:
        event_digest = hashlib.file_digest(event_csv, "sha256").hexdigest()
    payload = {
        "seed": SEED, "threshold_deaths": THRESHOLD, "features": FEATURES, "selected": selected,
        "splits": {name: dict(years=years, events=len(frame), positives=int(frame.high_mortality.sum()))
                   for (name, years), frame in zip(SPLITS.items(), (train, val, test))},
        "validation": valid, "test": performance, "selected_test_ci": heldout_intervals(y, test_scores[selected]),
        "source_event_csv_sha256": event_digest,
        "versions": {package: version(package) for package in ["scikit-learn", "numpy", "pandas", "shap"]},
    }
    joblib.dump(models[selected], OUT / "mortality_model.joblib")
    (OUT / "model_metrics.json").write_text(json.dumps(payload, indent=2) + "\n")
    info = explain(selected, models[selected], train, test)
    (OUT / "shap_summary.json").write_text(json.dumps(info, indent=2) + "\n")


if __name__ == "__main__":
    run()
