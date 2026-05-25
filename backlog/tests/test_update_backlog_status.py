"""Tests for ``update_backlog_status`` (run from repo: ``python3 -m unittest discover -s old/backlog/tests``)."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Extension layout: backlog/scripts/python/update_backlog_status.py
_EXT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_EXT_ROOT / "scripts" / "python"))

import update_backlog_status as ubs  # noqa: E402


class FindBacklogFileTests(unittest.TestCase):
    def test_none_when_no_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(ubs.find_backlog_file("*-backlog.md", [tmp]))

    def test_single_match_returns_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "alpha-backlog.md"
            p.write_text("# x\n", encoding="utf-8")
            found = ubs.find_backlog_file("*-backlog.md", [tmp])
            self.assertTrue(os.path.samefile(found, p))

    def test_multiple_matches_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "a-backlog.md").write_text("# a\n", encoding="utf-8")
            (Path(tmp) / "b-backlog.md").write_text("# b\n", encoding="utf-8")
            with self.assertRaises(ubs.AmbiguousBacklogError) as ctx:
                ubs.find_backlog_file("*-backlog.md", [tmp])
            self.assertIn("Multiple backlog files", str(ctx.exception))

    def test_skips_empty_root_uses_next(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            p = Path(second) / "only-backlog.md"
            p.write_text("# x\n", encoding="utf-8")
            found = ubs.find_backlog_file("*-backlog.md", [first, second])
            self.assertTrue(os.path.samefile(found, p))


class AggregateStatusTests(unittest.TestCase):
    def setUp(self):
        self.feature_catalog = [
            {"id": "Backlog", "display": "x", "aggregate": "initial"},
            {"id": "Specified", "display": "x", "aggregate": "in_progress"},
            {"id": "Implemented", "display": "x", "aggregate": "final_done"},
            {"id": "Cancelled", "display": "x", "aggregate": "final_cancelled"},
            {"id": "Blocked", "display": "x", "aggregate": "blocked"},
        ]
        self.parent_catalog = [
            {"id": "Backlog", "display": "x", "aggregate": "initial"},
            {"id": "In progress", "display": "x", "aggregate": "in_progress"},
            {"id": "Done", "display": "x", "aggregate": "final_done"},
            {"id": "Cancelled", "display": "x", "aggregate": "final_cancelled"},
            {"id": "Blocked", "display": "x", "aggregate": "blocked"},
        ]

    def test_all_done_mixed_cancelled(self):
        s = ubs.get_aggregate_status(
            ["Implemented", "Cancelled"],
            self.feature_catalog,
            self.parent_catalog,
        )
        self.assertEqual(s, "Done")

    def test_in_progress_when_active(self):
        s = ubs.get_aggregate_status(
            ["Backlog", "Specified"],
            self.feature_catalog,
            self.parent_catalog,
        )
        self.assertEqual(s, "In progress")

    def test_all_blocked(self):
        s = ubs.get_aggregate_status(
            ["Blocked", "Blocked"],
            self.feature_catalog,
            self.parent_catalog,
        )
        self.assertEqual(s, "Blocked")


class LoadConfigMergeTests(unittest.TestCase):
    def test_load_installed_config_returns_valid_cfg(self):
        cfg_path = _EXT_ROOT / "backlog-config.yml"
        if not cfg_path.is_file():
            self.skipTest("backlog-config.yml not present")
        cfg, used = ubs.load_config(str(cfg_path))
        self.assertIsNotNone(cfg)
        self.assertTrue(cfg["feature_statuses"])
        self.assertTrue(cfg["parent_statuses"])
        self.assertTrue(cfg["priorities"])
        self.assertTrue(cfg["events"])
        self.assertEqual(Path(used).resolve(), cfg_path.resolve())

    def test_partial_user_yaml_merges_template(self):
        with tempfile.NamedTemporaryFile(
            "w", suffix=".yml", delete=False, encoding="utf-8"
        ) as f:
            f.write("levels:\n  milestones: false\n")
            tmp_path = f.name
        try:
            cfg, _ = ubs.load_config(tmp_path)
            self.assertIsNotNone(cfg)
            self.assertFalse(cfg["levels"]["milestones"])
            self.assertTrue(cfg["levels"]["epics"])
            ids = [x["id"] for x in cfg["feature_statuses"]]
            self.assertIn("Analyzed", ids)
        finally:
            Path(tmp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
