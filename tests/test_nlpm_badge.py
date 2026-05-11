"""Tests for bin/nlpm-badge.

Run from the plugin root with:
    python3 -m unittest tests.test_nlpm_badge
"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
NLPM_BADGE_PATH = REPO_ROOT / "bin" / "nlpm-badge"

loader = SourceFileLoader("nlpm_badge", str(NLPM_BADGE_PATH))
spec = importlib.util.spec_from_loader("nlpm_badge", loader)
assert spec is not None
nlpm_badge = importlib.util.module_from_spec(spec)
sys.modules["nlpm_badge"] = nlpm_badge
loader.exec_module(nlpm_badge)


SHIELDS_ALLOWED_FIELDS = {
    "schemaVersion", "label", "message", "color", "labelColor",
    "isError", "namedLogo", "logoSvg", "logoColor", "style", "cacheSeconds",
}


class TestBuildBadge(unittest.TestCase):

    def test_clean_state(self):
        badge = nlpm_badge.build_badge({
            "version": "0.8.2",
            "findings": [],
            "summary": {"high": 0, "medium": 0, "low": 0},
        })
        self.assertEqual(badge["schemaVersion"], 1)
        self.assertEqual(badge["label"], "nlpm")
        self.assertEqual(badge["color"], "success")
        self.assertEqual(badge["isError"], False)
        self.assertIn("0 issues", badge["message"])
        self.assertIn("v0.8.2", badge["message"])

    def test_advisory_state_only_medium_low(self):
        badge = nlpm_badge.build_badge({
            "version": "0.8.2",
            "findings": [
                {"confidence": "medium", "rule": "hook/event-name"},
                {"confidence": "low", "rule": "vague"},
                {"confidence": "low", "rule": "vague"},
            ],
            "summary": {"high": 0, "medium": 1, "low": 2},
        })
        self.assertEqual(badge["color"], "important")
        self.assertEqual(badge["isError"], False)
        self.assertIn("3 advisory", badge["message"])

    def test_failing_state_single_high(self):
        badge = nlpm_badge.build_badge({
            "version": "0.8.2",
            "findings": [{"confidence": "high", "rule": "manifest-disk-diff"}],
            "summary": {"high": 1, "medium": 0, "low": 0},
        })
        self.assertEqual(badge["color"], "critical")
        self.assertEqual(badge["isError"], True)
        self.assertEqual(badge["message"], "1 high issue")

    def test_failing_state_multiple_high(self):
        badge = nlpm_badge.build_badge({
            "version": "0.8.2",
            "findings": [
                {"confidence": "high", "rule": "manifest-disk-diff"},
                {"confidence": "high", "rule": "skill/frontmatter"},
            ],
            "summary": {"high": 2, "medium": 0, "low": 0},
        })
        self.assertEqual(badge["color"], "critical")
        self.assertEqual(badge["message"], "2 high issues")

    def test_badge_emits_only_shields_allowed_fields(self):
        """Regression: shields.io rejects unknown fields with 'invalid properties: X'.

        Was caused 2026-05-11 by the original badge schema including an
        'extras' object — shields rendered the badge text as "invalid
        properties: extras" rather than the intended payload.
        """
        for inputs in [
            {"version": "0.8.2", "findings": [], "summary": {"high": 0, "medium": 0, "low": 0}},
            {"version": "0.8.2", "findings": [{"confidence": "high", "rule": "manifest-disk-diff"}], "summary": {"high": 1, "medium": 0, "low": 0}},
            {"version": "0.8.2", "findings": [{"confidence": "medium", "rule": "x"}], "summary": {"high": 0, "medium": 1, "low": 0}},
        ]:
            badge = nlpm_badge.build_badge(inputs)
            unknown = set(badge.keys()) - SHIELDS_ALLOWED_FIELDS
            self.assertEqual(
                unknown, set(),
                f"badge contains shields-incompatible fields: {unknown}",
            )


class TestBuildAttestation(unittest.TestCase):

    def test_attestation_includes_check_metadata(self):
        att = nlpm_badge.build_attestation({
            "version": "0.8.5",
            "findings": [],
            "summary": {"high": 0, "medium": 0, "low": 0},
        })
        self.assertIn("checked_at", att)
        self.assertEqual(att["nlpm_version"], "0.8.5")
        self.assertEqual(att["findings"], {"high": 0, "medium": 0, "low": 0})
        self.assertTrue(att["manifest_disk_consistent"])

    def test_attestation_flags_manifest_inconsistency(self):
        att = nlpm_badge.build_attestation({
            "version": "0.8.5",
            "findings": [{"confidence": "high", "rule": "manifest-disk-diff"}],
            "summary": {"high": 1, "medium": 0, "low": 0},
        })
        self.assertFalse(att["manifest_disk_consistent"])


class TestMain(unittest.TestCase):

    def run_main(self, stdin_text):
        saved_in, saved_out, saved_err = sys.stdin, sys.stdout, sys.stderr
        sys.stdin = io.StringIO(stdin_text)
        sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
        try:
            code = nlpm_badge.main([])
            return code, sys.stdout.getvalue(), sys.stderr.getvalue()
        finally:
            sys.stdin, sys.stdout, sys.stderr = saved_in, saved_out, saved_err

    def run_main_with_args(self, stdin_text, args):
        saved_in, saved_out, saved_err = sys.stdin, sys.stdout, sys.stderr
        sys.stdin = io.StringIO(stdin_text)
        sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
        try:
            code = nlpm_badge.main(args)
            return code, sys.stdout.getvalue(), sys.stderr.getvalue()
        finally:
            sys.stdin, sys.stdout, sys.stderr = saved_in, saved_out, saved_err

    def test_main_passes_through_clean(self):
        payload = json.dumps({
            "version": "0.8.2",
            "findings": [],
            "summary": {"high": 0, "medium": 0, "low": 0},
        })
        code, out, _err = self.run_main(payload)
        self.assertEqual(code, 0)
        parsed = json.loads(out)
        self.assertEqual(parsed["color"], "success")
        # Regression: only shields-allowed fields in default output
        unknown = set(parsed.keys()) - SHIELDS_ALLOWED_FIELDS
        self.assertEqual(unknown, set())

    def test_main_attestation_flag_emits_metadata(self):
        payload = json.dumps({
            "version": "0.8.4",
            "findings": [],
            "summary": {"high": 0, "medium": 0, "low": 0},
        })
        code, out, _err = self.run_main_with_args(payload, ["--attestation"])
        self.assertEqual(code, 0)
        parsed = json.loads(out)
        self.assertIn("checked_at", parsed)
        self.assertEqual(parsed["nlpm_version"], "0.8.4")

    def test_main_rejects_empty_stdin(self):
        code, _out, err = self.run_main("")
        self.assertEqual(code, 2)
        self.assertIn("stdin was empty", err)

    def test_main_rejects_invalid_json(self):
        code, _out, err = self.run_main("not json")
        self.assertEqual(code, 2)
        self.assertIn("failed to parse", err)

    def test_output_is_shields_endpoint_format(self):
        """Shields.io endpoint badge requires schemaVersion=1 and message+label."""
        payload = json.dumps({
            "version": "0.8.2",
            "findings": [],
            "summary": {"high": 0, "medium": 0, "low": 0},
        })
        _code, out, _err = self.run_main(payload)
        parsed = json.loads(out)
        self.assertEqual(parsed["schemaVersion"], 1)
        self.assertIn("label", parsed)
        self.assertIn("message", parsed)
        self.assertIn("color", parsed)


if __name__ == "__main__":
    unittest.main()
