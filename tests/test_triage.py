"""Tests for the triage tool.

Standard library only, so there is nothing to install:

    python3 -m unittest discover -s tests

pytest also collects these if you have it.
"""

from __future__ import annotations

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import triage  # noqa: E402


class TestNormalize(unittest.TestCase):
    def test_known_category_passes_through(self):
        out = triage.normalize({"category": "lint", "action": "Fix the lint errors."})
        self.assertEqual(out["category"], "lint")

    def test_unknown_category_falls_back_to_infra(self):
        out = triage.normalize({"category": "not_a_real_category"})
        self.assertEqual(out["category"], "infra")

    def test_confidence_is_always_high(self):
        for category in triage.CATEGORIES:
            with self.subTest(category=category):
                out = triage.normalize({"category": category})
                self.assertEqual(out["confidence"], "high")

    def test_missing_action_gets_a_default(self):
        out = triage.normalize({"category": "flaky"})
        self.assertEqual(out["action"], triage.DEFAULT_ACTIONS["flaky"])

    def test_every_category_has_a_default_action(self):
        for category in triage.CATEGORIES:
            with self.subTest(category=category):
                self.assertIn(category, triage.DEFAULT_ACTIONS)


if __name__ == "__main__":
    unittest.main()
