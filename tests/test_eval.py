"""Tests for deterministic evaluation/reporting helpers."""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import eval as evaluation  # noqa: E402
import triage  # noqa: E402


class TestStatistics(unittest.TestCase):
    def test_wilson_interval_shows_uncertainty_for_nine_of_ten(self):
        low, high = evaluation.wilson_interval(9, 10)
        self.assertGreater(low, 0.59)
        self.assertLess(low, 0.60)
        self.assertGreater(high, 0.98)
        self.assertLess(high, 0.99)

    def test_nearest_rank_p95_of_ten_samples_is_max(self):
        self.assertEqual(evaluation.nearest_rank_percentile(list(range(1, 11)), 0.95), 10)


class TestEvaluate(unittest.TestCase):
    def test_classifier_errors_are_distinct_from_wrong_predictions(self):
        labels = {"good.log": "lint", "wrong.log": "lint", "error.log": "lint"}

        with tempfile.TemporaryDirectory() as tmp:
            logs_dir = pathlib.Path(tmp)
            for name in labels:
                (logs_dir / name).write_text(name)

            def classifier(text: str) -> dict[str, str]:
                if text == "error.log":
                    raise triage.TriageError("provider down")
                if text == "wrong.log":
                    return {"category": "infra", "confidence": "high", "action": "x"}
                return {"category": "lint", "confidence": "high", "action": "x"}

            results = evaluation.evaluate(labels, logs_dir=logs_dir, classifier=classifier)

        by_name = {result.name: result for result in results}
        self.assertTrue(by_name["good.log"].matched)
        self.assertFalse(by_name["wrong.log"].matched)
        self.assertIsNone(by_name["wrong.log"].error)
        self.assertIsNone(by_name["error.log"].predicted)
        self.assertEqual(by_name["error.log"].error, "provider down")

    def test_invalid_utf8_log_bytes_are_replaced_before_classification(self):
        labels = {"invalid.log": "infra"}

        with tempfile.TemporaryDirectory() as tmp:
            logs_dir = pathlib.Path(tmp)
            (logs_dir / "invalid.log").write_bytes(b"failure\xff\xfeerror")
            observed_logs = []

            def classifier(log_text: str) -> dict[str, str]:
                observed_logs.append(log_text)
                return {
                    "category": "infra",
                    "confidence": "high",
                    "action": "Check infrastructure.",
                }

            results = evaluation.evaluate(
                labels,
                logs_dir=logs_dir,
                classifier=classifier,
            )

        self.assertEqual(observed_logs, ["failure\ufffd\ufffderror"])
        self.assertTrue(results[0].matched)


if __name__ == "__main__":
    unittest.main()
