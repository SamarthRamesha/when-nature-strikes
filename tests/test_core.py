"""License-independent regression checks with small constructed inputs."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import openpyxl
import pandas as pd

from scripts.prepare_emdat import OUTPUTS, event_id, prepare, stable_sum, valid_date
from src.geography import boundaries, map_coverage
from src.metrics import AFFECTED, DAMAGE, DEATHS, ID, ROOT, TYPE, YEAR, filtered_events, summarize
from src.model import FEATURES, cohorts, evaluate
from src.statistics import correlation_table, holm


class PreparationTest(unittest.TestCase):
    def test_id_date_and_accurate_sum(self):
        self.assertEqual(event_id("2020-0010-IND"), "2020-0010")
        self.assertEqual(valid_date(2020, 2, 29), "2020-02-29")
        for parts in [(1900, 2, 29), (2020, None, 1), (2020, 2, 30)]:
            self.assertEqual(valid_date(*parts), "")
        self.assertIsNone(stable_sum([]))
        self.assertEqual(stable_sum([1e16, 1.0, -1e16]), 1.0)

    def test_end_to_end_rebuild(self):
        fields = ["DisNo.", "Disaster Group", TYPE, "ISO", "Country", "Region", "Subregion",
                  YEAR, "Start Month", "Start Day", "End Year", "End Month", "End Day",
                  "Latitude", "Longitude", DEATHS, AFFECTED, "Total Damage, Adjusted ('000 US$)"]
        rows = [
            ["2020-0001-IND", "Natural", "Flood", "IND", "India", "Asia", "Southern Asia", 2020, 2, 29,
             2020, 3, 1, 10, 75, 5, None, 2500],
            ["2020-0001-BGD", "Natural", "Flood", "BGD", "Bangladesh", "Asia", "Southern Asia", 2020, 2, 29,
             2020, 3, None, None, None, 0, None, 1500],
            ["2020-0002-IND", "Technological", "Accident", "IND", "India", "Asia", "Southern Asia", 2020, 1, 1,
             2020, 1, 1, None, None, 3, 0, 0],
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            source = path / "fixture.xlsx"
            book = openpyxl.Workbook()
            sheet = book.active
            sheet.title = "EM-DAT Data"
            sheet.append(fields)
            for row in rows:
                sheet.append(row)
            book.save(source)
            with contextlib.redirect_stdout(io.StringIO()) as first:
                prepare(source, path / "a")
            with contextlib.redirect_stdout(io.StringIO()) as second:
                prepare(source, path / "b")
            self.assertEqual(json.loads(first.getvalue()), json.loads(second.getvalue()))
            for name in OUTPUTS:
                self.assertEqual((path / "a" / name).read_bytes(), (path / "b" / name).read_bytes())
            impacts, events, types, geographic = [pd.read_csv(path / "a" / name) for name in OUTPUTS]
            self.assertEqual((len(impacts), len(events), len(types), len(geographic)), (2, 1, 1, 2))
            self.assertTrue(events[ID].is_unique)
            self.assertTrue(impacts["DisNo."].is_unique)
            self.assertTrue(events[AFFECTED].isna().all())
            self.assertEqual(events.iloc[0][DAMAGE], 4)
            self.assertEqual(events.iloc[0][DEATHS], 5)
            self.assertEqual(events.iloc[0][f"{DEATHS} Reported Country Impacts"], 2)
            self.assertEqual(geographic["Unique Events"].sum(), 2)


class MetricTest(unittest.TestCase):
    def setUp(self):
        self.events = pd.DataFrame({ID: ["a", "b"], TYPE: ["Flood", "Flood"], YEAR: [2010, 2011]})
        self.impacts = pd.DataFrame({ID: ["a", "a", "b"], "ISO": ["IND", "BGD", "IND"],
                                     DEATHS: [5, 3, None], AFFECTED: [None, 0, None],
                                     DAMAGE: [2., None, None]})

    def test_scope_aggregates_before_coverage(self):
        frame = filtered_events(self.impacts, self.events)
        self.assertEqual(len(frame), 2)
        self.assertEqual(frame.loc[frame[ID].eq("a"), DEATHS].item(), 8)
        summary = summarize(frame, TYPE).set_index("metric")
        self.assertEqual(summary.loc[DEATHS, "coverage"], .5)
        self.assertEqual(summary.loc[AFFECTED, "reported"], 1)
        self.assertEqual(summary.loc[AFFECTED, "total"], 0)

    def test_geographic_filter_does_not_pull_unselected_losses(self):
        frame = filtered_events(self.impacts[self.impacts.ISO.eq("IND")], self.events)
        self.assertEqual(frame[DEATHS].sum(), 5)
        self.assertTrue(frame[AFFECTED].isna().all())
        self.assertTrue(summarize(frame, TYPE).set_index("metric").loc[AFFECTED, ["total", "mean"]].isna().all())

    def test_summary_reports_quantiles_and_denominator(self):
        frame = filtered_events(self.impacts, self.events)
        row = summarize(frame, TYPE).set_index("metric").loc[DEATHS]
        self.assertEqual(row["q25"], 8)
        self.assertEqual(row["iqr"], 0)
        self.assertEqual(row["largest_share"], 1)

    def test_rank_statistic_and_holm(self):
        table = pd.DataFrame({"metric": DEATHS, "events": [10, 20, 30, 40, 50],
                              **{s: [15, 25, 27, 45, 50] for s in ["total", "mean", "median", "winsor_mean"]}})
        result = correlation_table(table, np.random.default_rng(42), draws=100)
        row = result.query("method == 'Spearman' and statistic == 'total'").iloc[0]
        self.assertAlmostEqual(row.coefficient, 1.)
        self.assertAlmostEqual(row.ci_low, 1.)
        np.testing.assert_allclose(holm([.01, .03, .04]), [.03, .06, .06])


class ModelAndMapTest(unittest.TestCase):
    def test_time_and_feature_separation(self):
        events = pd.DataFrame({ID: ["a", "b", "c", "d"], YEAR: [2000, 2018, 2022, 2025],
                              DEATHS: [2, 100, 700, None], "Country Impact Records": [1, 1, 1, 1]})
        impacts = pd.DataFrame({ID: events[ID], TYPE: ["Flood"]*4, "Region": ["Asia"]*4,
                                "Start Month": [None, 7, 1, 5]})
        train, valid, test = cohorts(events, impacts).values()
        self.assertEqual([x[ID].item() for x in (train, valid, test)], ["a", "b", "c"])
        self.assertEqual(train["Start Month"].item(), "Unknown")
        self.assertEqual(list(test.high_mortality), [1])
        self.assertEqual(set(FEATURES), {TYPE, "Region", "Start Month"})

    def test_evaluation_metrics(self):
        scores = evaluate(np.array([0, 0, 1, 1]), np.array([.2, .6, .3, .9]), .5)
        self.assertEqual(scores["confusion"], [[1, 1], [1, 1]])
        self.assertAlmostEqual(scores["macro_f1"], .5)

    def test_real_polygons_and_unmapped_codes(self):
        world = boundaries()
        codes = [feature["id"] for feature in world["features"]]
        self.assertEqual(len(codes), len(set(codes)))
        self.assertIn("IND", codes)
        frame = pd.DataFrame({"ISO": ["IND", "ZZZ"], "Country": ["India", "Unavailable"], ID: ["a", "b"]})
        count, missing = map_coverage(frame, world)
        self.assertEqual(count, 1)
        self.assertEqual(missing.iloc[0].ISO, "ZZZ")


class ResultContractsTest(unittest.TestCase):
    def test_findings_and_provenance(self):
        findings = json.loads((ROOT / "results/findings.json").read_text())
        source = json.loads((ROOT / "results/provenance.json").read_text())
        self.assertEqual(sum(findings["type_counts"].values()), findings["events"])
        self.assertEqual(findings["events"], source["natural_events"])
        self.assertEqual(findings["impact_leaders"][DAMAGE]["total"], "Storm")

    def test_saved_model_and_shap_alignment(self):
        results = ROOT / "results"
        metrics = json.loads((results / "model_metrics.json").read_text())
        shap = json.loads((results / "shap_summary.json").read_text())
        self.assertEqual(metrics["selected"], shap["model"])
        self.assertEqual(set(shap["mean_absolute_group_shap"]), set(metrics["features"]))
        self.assertLess(shap["max_additivity_error"], 1e-6)
        self.assertEqual(np.sum(metrics["test"][metrics["selected"]]["confusion"]), metrics["splits"]["test"]["events"])

    def test_embedding_and_cluster_contracts(self):
        results = ROOT / "results"
        info = json.loads((results / "profile_summary.json").read_text())
        self.assertAlmostEqual(sum(info["explained_variance_ratio"]), 1)
        for estimator in ("PCA", "t-SNE", "UMAP"):
            self.assertGreater(info["embedding_diagnostics"][estimator]["trustworthiness_15"], .5)
        profiles = pd.read_csv(results / "cluster_profiles.csv")
        self.assertEqual(profiles.n.sum(), info["complete_events"])
        self.assertGreater(info["anomaly_flags"], 0)


if __name__ == "__main__":
    unittest.main()
