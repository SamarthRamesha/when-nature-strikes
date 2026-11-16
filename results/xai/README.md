# Fitted model explanations

Run `python -m src.model` and `python -m src.xai` after rebuilding the authorized data. The XAI module refits the selected model using the training era and checks the held-out average precision against the saved evaluation.

- `summary.json` records model provenance, scores, SHAP and local LIME fidelity.
- `permutation_importance.csv` reports forty held-out repetitions per feature.
- `pdp_ice.csv` stores the held-out month curve, quantiles and three invented scenario curves.
- `shap_scenario_*.png` and `lime_local.png` illustrate invented metadata.
- `predictions_local.csv` and `ice_local.csv` are generated locally and stay within the permitted audience.

[Methodology and interpretation](../../docs/XAI_COMPARISON.md)
