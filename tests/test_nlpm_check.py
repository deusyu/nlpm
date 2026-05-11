"""Tests for bin/nlpm-check.

Run from the plugin root with:
    python3 -m unittest tests.test_nlpm_check
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path


# Load the bin/nlpm-check script as a module so we can call its main()
# directly. The lack of .py extension means we have to use a loader
# explicitly.
REPO_ROOT = Path(__file__).resolve().parent.parent
NLPM_CHECK_PATH = REPO_ROOT / "bin" / "nlpm-check"

loader = SourceFileLoader("nlpm_check", str(NLPM_CHECK_PATH))
spec = importlib.util.spec_from_loader("nlpm_check", loader)
assert spec is not None
nlpm_check = importlib.util.module_from_spec(spec)
# Register in sys.modules BEFORE exec so that @dataclass (Python 3.14+)
# can resolve the module via cls.__module__ during type inspection.
sys.modules["nlpm_check"] = nlpm_check
loader.exec_module(nlpm_check)


def make_plugin(root: Path, manifest: dict | None, files: dict[str, str]) -> None:
    """Write a manifest + file tree under root."""
    if manifest is not None:
        (root / ".claude-plugin").mkdir(parents=True, exist_ok=True)
        (root / ".claude-plugin" / "plugin.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
    for rel, content in files.items():
        full = root / rel
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")


SKILL_VALID = """---
name: {name}
description: a skill
---
body
"""


class TestNlpmCheck(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self._stdout_buffer = []
        self._stderr_buffer = []

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_check(self, *args: str) -> tuple[int, str, str]:
        """Run nlpm_check.main() with stdout/stderr captured."""
        import io
        saved_out, saved_err = sys.stdout, sys.stderr
        out_buf, err_buf = io.StringIO(), io.StringIO()
        sys.stdout, sys.stderr = out_buf, err_buf
        try:
            code = nlpm_check.main([str(self.tmp), *args])
        finally:
            sys.stdout, sys.stderr = saved_out, saved_err
        return code, out_buf.getvalue(), err_buf.getvalue()

    # ----- happy path -----

    def test_clean_plugin_passes(self) -> None:
        make_plugin(self.tmp, {"name": "ok", "skills": "skills/"}, {
            "skills/ok/SKILL.md": SKILL_VALID.format(name="ok"),
        })
        code, out, _err = self.run_check()
        self.assertEqual(code, 0, out)
        self.assertIn("clean", out)

    def test_no_manifest_returns_2(self) -> None:
        # Empty directory; no .claude-plugin/plugin.json.
        code, _out, err = self.run_check()
        self.assertEqual(code, 2)
        self.assertIn("no .claude-plugin", err)

    # ----- manifest-disk-diff (the bug class) -----

    def test_unregistered_skill_with_explicit_array(self) -> None:
        """The mattpocock pattern: SKILL.md on disk, missing from manifest array."""
        make_plugin(self.tmp, {"name": "p", "skills": ["skills/registered"]}, {
            "skills/registered/SKILL.md": SKILL_VALID.format(name="registered"),
            "skills/missed/SKILL.md": SKILL_VALID.format(name="missed"),
        })
        code, out, _ = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("skills/missed/SKILL.md", out)
        self.assertIn("not registered", out)

    def test_skill_outside_canonical_paths_no_manifest_field(self) -> None:
        """SKILL.md in a non-canonical location with no `skills` field declared."""
        make_plugin(self.tmp, {"name": "p"}, {
            "extras/foo/SKILL.md": SKILL_VALID.format(name="foo"),
        })
        code, out, _ = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("extras/foo/SKILL.md", out)
        self.assertIn("outside canonical", out)

    def test_skill_at_canonical_path_no_manifest_field_passes(self) -> None:
        """No `skills` declaration + SKILL.md in canonical `skills/` → no finding."""
        make_plugin(self.tmp, {"name": "p"}, {
            "skills/foo/SKILL.md": SKILL_VALID.format(name="foo"),
        })
        code, _out, _ = self.run_check()
        self.assertEqual(code, 0)

    def test_manifest_path_does_not_exist(self) -> None:
        make_plugin(self.tmp, {"name": "p", "skills": ["skills/ghost"]}, {})
        code, out, _ = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("doesn't exist on disk", out)

    def test_unregistered_agent(self) -> None:
        make_plugin(self.tmp, {"name": "p", "agents": ["agents/registered.md"]}, {
            "agents/registered.md": "---\nname: registered\ndescription: ok\n---\nbody",
            "agents/missed.md": "---\nname: missed\ndescription: ok\n---\nbody",
        })
        code, out, _ = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("agents/missed.md", out)

    # ----- frontmatter checks -----

    def test_skill_missing_name(self) -> None:
        make_plugin(self.tmp, {"name": "p", "skills": "skills/"}, {
            "skills/foo/SKILL.md": "---\ndescription: only desc\n---\nbody\n",
        })
        code, out, _ = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("missing required `name`", out)

    def test_skill_name_parent_mismatch(self) -> None:
        make_plugin(self.tmp, {"name": "p", "skills": "skills/"}, {
            "skills/foo/SKILL.md": SKILL_VALID.format(name="bar"),
        })
        code, out, _ = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("does not match parent directory", out)

    def test_skill_name_format_invalid(self) -> None:
        make_plugin(self.tmp, {"name": "p", "skills": "skills/"}, {
            "skills/Foo/SKILL.md": SKILL_VALID.format(name="Foo"),
        })
        code, out, _ = self.run_check()
        self.assertEqual(code, 1)
        # name=Foo matches parent dir Foo but violates spec (uppercase)
        self.assertIn("violates spec", out)

    def test_skill_missing_frontmatter_entirely(self) -> None:
        make_plugin(self.tmp, {"name": "p", "skills": "skills/"}, {
            "skills/foo/SKILL.md": "no frontmatter here, just body\n",
        })
        code, out, _ = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("missing YAML frontmatter", out)

    def test_command_missing_description(self) -> None:
        make_plugin(self.tmp, {"name": "p", "commands": "commands/"}, {
            "commands/foo.md": "---\nname: foo\n---\nbody",
        })
        code, out, _ = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("missing required `description`", out)

    def test_command_with_only_description_passes(self) -> None:
        """`name:` is explicitly optional for commands."""
        make_plugin(self.tmp, {"name": "p", "commands": "commands/"}, {
            "commands/foo.md": "---\ndescription: a command\n---\nbody",
        })
        code, _out, _ = self.run_check()
        self.assertEqual(code, 0)

    # ----- hook checks -----

    def test_hook_event_wrong_case(self) -> None:
        make_plugin(self.tmp, {"name": "p"}, {
            "hooks/hooks.json": json.dumps({
                "hooks": {
                    "pretooluse": [
                        {"matcher": "", "hooks": [{"type": "command", "command": "echo"}]}
                    ]
                }
            }),
        })
        code, out, _ = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("wrong case", out)
        self.assertIn("PreToolUse", out)

    def test_hook_valid_event_passes(self) -> None:
        make_plugin(self.tmp, {"name": "p"}, {
            "hooks/hooks.json": json.dumps({
                "hooks": {
                    "PreToolUse": [
                        {"matcher": "", "hooks": [{"type": "command", "command": "echo"}]}
                    ]
                }
            }),
        })
        code, _out, _ = self.run_check()
        self.assertEqual(code, 0)

    # ----- strict mode -----

    def test_strict_mode_fails_on_medium(self) -> None:
        # Unknown hook event is medium, not high. Default mode passes;
        # strict mode fails.
        make_plugin(self.tmp, {"name": "p"}, {
            "hooks/hooks.json": json.dumps({
                "hooks": {
                    "TotallyMadeUpEvent": [
                        {"matcher": "", "hooks": [{"type": "command", "command": "echo"}]}
                    ]
                }
            }),
        })
        code_default, _, _ = self.run_check()
        self.assertEqual(code_default, 0, "default mode should not fail on medium")
        code_strict, _, _ = self.run_check("--strict")
        self.assertEqual(code_strict, 1, "strict mode should fail on medium")

    # ----- JSON output -----

    def test_json_output_is_valid_json(self) -> None:
        make_plugin(self.tmp, {"name": "p", "skills": ["skills/ghost"]}, {})
        code, out, _ = self.run_check("--json")
        self.assertEqual(code, 1)
        parsed = json.loads(out)
        self.assertEqual(parsed["summary"]["high"], 1)
        self.assertEqual(parsed["version"], nlpm_check.VERSION)

    # ----- plugin root discovery -----

    def test_finds_plugin_root_from_subdir(self) -> None:
        make_plugin(self.tmp, {"name": "p", "skills": "skills/"}, {
            "skills/foo/SKILL.md": SKILL_VALID.format(name="foo"),
        })
        # Run check pointed at a subdirectory; it should walk up.
        subdir = self.tmp / "skills" / "foo"
        import io
        saved_out, saved_err = sys.stdout, sys.stderr
        out_buf, err_buf = io.StringIO(), io.StringIO()
        sys.stdout, sys.stderr = out_buf, err_buf
        try:
            code = nlpm_check.main([str(subdir)])
        finally:
            sys.stdout, sys.stderr = saved_out, saved_err
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
