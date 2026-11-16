"""Explanations of the verified chronological mortality classifier."""
import json
from importlib.metadata import version

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.metrics import average_precision_score

from .metrics import ID, OUT
from .metrics import load_data
from .model import FEATURES, SEED, candidates, cohorts
from .statistics import INK, TEAL

DEST = OUT / "xai"
PROBES = {
    "Flood in Southern Asia scenario": ["Flood", "Asia", "7"],
    "Earthquake in the Americas scenario": ["Earthquake", "Americas", "2"],
    "Storm in Oceania scenario": ["Storm", "Oceania", "12"],
}


def predicted(model, frame):
    return model.predict_proba(pd.DataFrame(frame, columns=FEATURES))


def explore_month(model, frame, months):
    return np.column_stack([predicted(model, frame.assign(**{"Start Month": month}))[:, 1]
                            for month in months])


def lime_cases(model, training, probes):
    from lime.lime_tabular import LimeTabularExplainer

    levels = {i: sorted(training[feature].unique()) for i, feature in enumerate(FEATURES)}
    encoded = np.column_stack([pd.Categorical(training[feature], categories=levels[i]).codes
                               for i, feature in enumerate(FEATURES)])

    def classify(matrix):
        return predicted(model, {feature: np.asarray(levels[i])[matrix[:, i].astype(int)]
                                 for i, feature in enumerate(FEATURES)})

    output = {}
    for label, row in probes.iterrows():
        if any(row[feature] not in levels[i] for i, feature in enumerate(FEATURES)):
            raise ValueError(f"Unsupported scenario: {label}")
        indices = [levels[i].index(row[feature]) for i, feature in enumerate(FEATURES)]
        explainer = LimeTabularExplainer(encoded, mode="classification", feature_names=FEATURES,
            categorical_features=list(levels), categorical_names=levels, feature_selection="none",
            class_names=["Under 100", "100 or more"], discretize_continuous=False, random_state=SEED)
        local = explainer.explain_instance(np.asarray(indices), classify, labels=(1,),
                                           num_features=len(FEATURES), num_samples=5000)
        output[label] = {"conditions": local.as_list(label=1), "weighted_r2": float(local.score),
                         "surrogate_prediction": float(local.local_pred[0]),
                         "surrogate_intercept": float(local.intercept[1])}
    return output


def shap_cases(model, training, probes):
    import shap

    encoder, estimator = [step[1] for step in model.steps]
    background = encoder.transform(training.sample(n=256, random_state=SEED))
    design = encoder.transform(probes)
    if hasattr(estimator, "decision_function"):
        raw = shap.LinearExplainer(estimator, shap.maskers.Independent(background, max_samples=256))(design)
        target, units = estimator.decision_function(design), "log odds"
    else:
        raw = shap.TreeExplainer(estimator, background, feature_perturbation="interventional",
                                 model_output="probability")(design)[:, :, 1]
        target, units = model.predict_proba(probes)[:, 1], "probability"
    np.testing.assert_allclose(raw.base_values + raw.values.sum(axis=1), target, rtol=0, atol=1e-6)
    names = encoder.get_feature_names_out(FEATURES)
    grouped = np.column_stack([raw.values[:, [i for i, n in enumerate(names) if n.startswith(f"{feature}_")]].sum(axis=1)
                               for feature in FEATURES])
    for index, label in enumerate(probes.index):
        compact = shap.Explanation(values=grouped[index], base_values=raw.base_values[index],
                                   data=None, feature_names=FEATURES)
        shap.plots.waterfall(compact, show=False)
        plt.gcf().suptitle(f"Illustrative scenario {index + 1} · {units}", fontsize=14)
        save(plt.gcf(), f"shap_scenario_{index + 1}")
    return units, {label: {"baseline": float(raw.base_values[i]), "explanation_total": float(target[i]),
                          "grouped": dict(zip(FEATURES, grouped[i].tolist()))}
                   for i, label in enumerate(probes.index)}


def save(fig, name):
    fig.text(.99, -.025, "EM-DAT-derived model · CRED / UCLouvain, www.emdat.be", ha="right", fontsize=8)
    fig.savefig(DEST / f"{name}.png", dpi=155, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def run():
    DEST.mkdir(parents=True, exist_ok=True)
    recorded = json.loads((OUT / "model_metrics.json").read_text())
    selected = recorded["selected"]
    train, _, test = cohorts(*load_data()).values()
    train_x, test_x = train[FEATURES], test[FEATURES]
    model = candidates()[selected].fit(train_x, train.high_mortality)
    scores = predicted(model, test_x)[:, 1]
    ap = average_precision_score(test.high_mortality, scores)
    np.testing.assert_allclose(ap, recorded["test"][selected]["average_precision"], atol=1e-8, rtol=0)
    threshold = recorded["validation"][selected]["threshold"]
    pd.DataFrame({ID: test[ID], "observed_high_mortality": test.high_mortality, "probability": scores,
                  "decision": scores >= threshold}).to_csv(DEST / "predictions_local.csv", index=False)

    importance = permutation_importance(model, test_x, test.high_mortality,
                                        scoring="average_precision", n_repeats=40, random_state=SEED, n_jobs=1)
    pfi = pd.DataFrame({"feature": FEATURES, "mean_ap_drop": importance.importances_mean,
                        "sd_ap_drop": importance.importances_std}).sort_values("mean_ap_drop", ascending=False)
    pfi.to_csv(DEST / "permutation_importance.csv", index=False)
    fig, ax = plt.subplots(figsize=(8.2, 3.5), layout="constrained")
    ax.barh(pfi.feature[::-1], pfi.mean_ap_drop[::-1], xerr=pfi.sd_ap_drop[::-1], color=TEAL)
    ax.axvline(0, color=INK, lw=.8)
    ax.set(title=f"Change in held-out average precision after permuting one field (n = {len(test):,})",
           xlabel="Average precision drop ± 1 repeat standard deviation")
    save(fig, "permutation_importance")

    probes = pd.DataFrame.from_dict(PROBES, orient="index", columns=FEATURES)
    lime = lime_cases(model, train_x, probes)
    units, shap = shap_cases(model, train_x, probes)
    scenarios = {}
    fig, axes = plt.subplots(1, len(probes), figsize=(12, 3.7), layout="constrained")
    for i, ((label, row), ax) in enumerate(zip(probes.iterrows(), axes), start=1):
        info = lime[label]
        names, values = zip(*info["conditions"])
        ax.barh([name.split("=")[0] for name in names], values,
                color=[TEAL if weight >= 0 else "#ad4829" for weight in values])
        ax.axvline(0, color=INK, lw=.8)
        ax.set(title=f"Scenario {i} · weighted R² {info['weighted_r2']:.2f}", xlabel="LIME weight on probability scale")
        scenarios[label] = {"inputs": row.to_dict(), "prediction": float(predicted(model, row.to_frame().T)[0, 1]),
                            "lime": info, "shap": shap[label], "shap_image": f"shap_scenario_{i}.png"}
    save(fig, "lime_local")

    months = [str(x) for x in range(1, 13)]
    real_ice = explore_month(model, test_x, months)
    synthetic_ice = explore_month(model, probes, months)
    pd.DataFrame(real_ice, columns=months).assign(**{ID: test[ID].to_numpy()}).to_csv(
        DEST / "ice_local.csv", index=False)
    pdp = pd.DataFrame({"month": list(map(int, months)), "held_out_mean": real_ice.mean(axis=0),
                        "held_out_q10": np.quantile(real_ice, .1, axis=0),
                        "held_out_q90": np.quantile(real_ice, .9, axis=0)})
    for i, profile in enumerate(synthetic_ice, start=1):
        pdp[f"Scenario {i}"] = profile
    pdp.to_csv(DEST / "pdp_ice.csv", index=False)
    fig, ax = plt.subplots(figsize=(9, 4.3), layout="constrained")
    ax.fill_between(pdp.month, pdp.held_out_q10, pdp.held_out_q90, color=TEAL, alpha=.16, label="Held-out 10th–90th percentile")
    ax.plot(pdp.month, pdp.held_out_mean, color=TEAL, lw=3, label="Held-out partial dependence")
    for i in range(1, len(probes) + 1):
        ax.plot(pdp.month, pdp[f"Scenario {i}"], linestyle="--", label=f"Synthetic ICE {i}")
    ax.set(title="Replacing start month while holding other inputs fixed",
           xlabel="Calendar month category", ylabel="Predicted probability", xticks=range(1, 13))
    ax.legend(frameon=False, ncols=2, fontsize=8)
    save(fig, "pdp_ice")

    shap_global = json.loads((OUT / "shap_summary.json").read_text())["mean_absolute_group_shap"]
    payload = {"model": selected, "seed": SEED, "train_events": len(train), "held_out_events": len(test),
               "held_out_average_precision": ap, "permutation_repeats": 40, "lime_samples": 5000,
               "shap_units": units, "shap_global": shap_global, "scenarios": scenarios,
               "versions": {name: version(name) for name in ("lime", "shap", "scikit-learn")}}
    (DEST / "summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    run()
