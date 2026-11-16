"""Regression checks for newly packaged analytical results and Power BI bindings."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import pandas as pd

from scripts.build_powerbi import DEMO, FACT, SOURCE, build, measures
from scripts.reproduce_windows import REFERENCE, rebuild
from src.metrics import AFFECTED, DAMAGE, DEATHS, ID, OUT, filtered_events, summarize


def read(file):
    return json.loads(file.read_text(encoding="utf-8"))


class PowerBiTest(unittest.TestCase):
    def test_rebuild_matches_packaged_native_project(self):
        with tempfile.TemporaryDirectory() as staging:
            output = Path(staging) / "Power BI source"
            self.assertTrue(build(output).is_file())
            pack = {p.relative_to(DEMO): hashlib.sha256(p.read_bytes()).digest()
                    for p in DEMO.rglob("*") if p.is_file() and ".pbi" not in p.parts}
            new = {p.relative_to(output): hashlib.sha256(p.read_bytes()).digest()
                   for p in output.rglob("*") if p.is_file()}
            self.assertEqual(pack, new)
            with self.assertRaises(FileExistsError):
                build(output)

    def test_bindings_measures_and_slicer_sync(self):
        model = read(DEMO / "When_Nature_Strikes.SemanticModel/model.bim")["model"]
        table = {x["name"]: x for x in model["tables"]}
        expressions = {m["name"]: m["expression"] for m in table[FACT]["measures"]}
        self.assertEqual(expressions["Distinct events"], "DISTINCTCOUNT(FactImpacts[Event ID])")
        self.assertEqual(table[FACT]["measures"], measures())
        self.assertEqual(model["relationships"][0]["crossFilteringBehavior"], "oneDirection")
        self.assertIn("Table.ReplaceValue", " ".join(table[FACT]["partitions"][0]["source"]["expression"]))
        self.assertIn("NOT ISBLANK", expressions["Deaths median per reporting event"])
        self.assertIn("Text.ToBinary", " ".join(table[FACT]["partitions"][0]["source"]["expression"]))
        pages = DEMO / "When_Nature_Strikes.Report/definition/pages"
        page_shapes = [list((pages / page / "visuals").glob("*/visual.json"))
                       for page in read(pages / "pages.json")["pageOrder"]]
        self.assertEqual(len(page_shapes), 5)
        for page in page_shapes:
            anchor = set()
            for path in page:
                item = read(path)
                view = item["visual"]
                pos = item["position"]
                self.assertLessEqual(pos["x"] + pos["width"], 1440)
                self.assertLessEqual(pos["y"] + pos["height"], 900)
                if "syncGroup" in view:
                    anchor.add(view["syncGroup"]["groupName"])
                for values in view.get("query", {}).get("queryState", {}).values():
                    for bind in values["projections"]:
                        kind, value = next(iter(bind["field"].items()))
                        entity = value["Expression"]["SourceRef"]["Entity"]
                        names = {m["name"] for m in table[entity]["measures" if kind == "Measure" else "columns"]}
                        self.assertIn(value["Property"], names)
                if view["visualType"] == "azureMap":
                    self.assertIn("Mapped", str(item["filterConfig"]))
                    self.assertEqual(view["query"]["queryState"]["Size"]["projections"][0]["nativeQueryRef"],
                                     "Selected map value")
            self.assertTrue({"Startyear", "Hazard", "Region", "Country", "Decade"}.issubset(anchor))

    def test_fixture_denominators_and_filtered_country_contribution(self):
        impacts = pd.read_csv(SOURCE / "synthetic_impacts.csv")
        events = pd.read_csv(SOURCE / "synthetic_events.csv")
        self.assertEqual((len(impacts), len(events)), (13, 12))
        combined = filtered_events(impacts, events)
        metrics = summarize(combined.assign(scope=1), "scope").set_index("metric")
        for name, amount, reports in [(DEATHS, 297, 11), (AFFECTED, 5025, 11), (DAMAGE, 1762, 10)]:
            self.assertEqual(metrics.loc[name, "total"], amount)
            self.assertEqual(metrics.loc[name, "reported"], reports)
        cropped = filtered_events(impacts.loc[impacts.ISO.eq("BGD")], events)
        self.assertEqual(len(cropped), 2)
        self.assertTrue(pd.isna(cropped.loc[cropped[ID].eq("SYN-001"), DEATHS].item()))
        self.assertEqual(cropped.loc[cropped[ID].eq("SYN-001"), AFFECTED].item(), 800)


class AnalyticContractTest(unittest.TestCase):
    def test_xai_saved_results_match_actual_model(self):
        folder = OUT / "xai"
        summary = read(folder / "summary.json")
        original = read(OUT / "model_metrics.json")
        selected = original["selected"]
        self.assertEqual(summary["model"], selected)
        self.assertEqual(summary["held_out_events"], original["splits"]["test"]["events"])
        self.assertAlmostEqual(summary["held_out_average_precision"], original["test"][selected]["average_precision"])
        for scenario in summary["scenarios"].values():
            shap = scenario["shap"]
            self.assertAlmostEqual(shap["baseline"] + sum(shap["grouped"].values()), shap["explanation_total"])
            self.assertTrue(0 <= scenario["prediction"] <= 1)
            self.assertTrue(-1 <= scenario["lime"]["weighted_r2"] <= 1)
            self.assertTrue((folder / scenario["shap_image"]).is_file())
        importance = pd.read_csv(folder / "permutation_importance.csv")
        self.assertEqual(importance.iloc[0].feature, "Disaster Type")
        self.assertEqual(list(pd.read_csv(folder / "pdp_ice.csv").month), list(range(1, 13)))

    def test_projection_coordinates_are_aggregates(self):
        cells = pd.read_csv(OUT / "dimensionality_reduction/projection_cells.csv")
        info = read(OUT / "profile_summary.json")
        self.assertNotIn(ID, cells.columns)
        self.assertNotIn(DEATHS, cells.columns)
        self.assertGreaterEqual(cells.events.min(), 5)
        self.assertEqual(set(cells.method), {"PCA", "t-SNE", "UMAP"})
        self.assertTrue(cells.query("dimensions == 3").axis3.notna().all())
        self.assertTrue(cells.groupby(["method", "dimensions", "grouping"]).events.sum().le(info["complete_events"]).all())
        anomalies = pd.read_csv(OUT / "dimensionality_reduction/anomaly_summary.csv")
        self.assertEqual(anomalies.flagged.sum(), info["anomaly_flags"])

    def test_wrong_workbook_is_rejected_before_preparation(self):
        with tempfile.TemporaryDirectory() as folder:
            invalid = Path(folder) / "wrong.xlsx"
            invalid.write_text("an incorrect source")
            with self.assertRaisesRegex(ValueError, "SHA-256 differs"):
                rebuild(invalid, True)
        self.assertEqual(len(read(REFERENCE)["output_sha256"]), 4)


if __name__ == "__main__":
    unittest.main()
