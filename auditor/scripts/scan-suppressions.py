#!/usr/bin/env python3
"""Scan GitHub for committed NLPM configs that suppress rules.

Searches for `.claude/nlpm.local.md` and `.claude/nlpm.md` files
containing `rule_overrides`, fetches each, parses the YAML frontmatter,
and emits one `downstream_suppression` event per override to
`auditor/disagreements.jsonl`.

Skips:
- The host repo (self-references)
- (repo, sha, path) tuples already in disagreements.jsonl (dedupe)
- Files with no frontmatter or no rule_overrides

Prints a JSON summary on stdout:
  {"candidates": N, "emitted": N, "skipped_self": N,
   "skipped_dup": N, "skipped_no_overrides": N, "search_ok": bool}

Extracted from auditor-suppressions.yml in v0.8.10 — the previous
inline 110-line bash block mixed gh-api shell calls with jq + sha256sum
+ python heredoc invocations of parse-suppressions.py.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


DISAGREEMENTS = Path("auditor/disagreements.jsonl")
PARSE_SUPPRESSIONS = Path("auditor/scripts/parse-suppressions.py")
TMP_CONFIG = Path("/tmp/nlpm-config.md")
SELF_REPO = os.environ.get("GITHUB_REPOSITORY", "")
RATE_DELAY_SECONDS = 0.5


def gh_search_paginated(query: str) -> tuple[bool, list[dict]]:
    """Return (success, items). On failure, items is partial/empty."""
    try:
        proc = subprocess.run(
            ["gh", "api", "--paginate", f"/search/code?q={query}",
             "--jq", ".items[]?"],
            capture_output=True, text=True, check=True,
        )
        items = []
        for line in proc.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return True, items
    except subprocess.CalledProcessError as e:
        print(f"WARN: gh api search failed: {e.stderr[:200]}", file=sys.stderr)
        return False, []


def gh_fetch_file(repo: str, path: str) -> str | None:
    """Return decoded file content, or None on failure."""
    try:
        proc = subprocess.run(
            ["gh", "api", f"/repos/{repo}/contents/{path}", "--jq", ".content"],
            capture_output=True, text=True, check=True,
        )
        b64 = proc.stdout.strip().replace("\n", "")
        if not b64:
            return None
        return base64.b64decode(b64).decode("utf-8", errors="replace")
    except (subprocess.CalledProcessError, ValueError):
        return None


def parse_overrides(content: str) -> list[dict]:
    """Invoke the existing parse-suppressions.py on `content`."""
    TMP_CONFIG.write_text(content)
    try:
        proc = subprocess.run(
            ["python3", str(PARSE_SUPPRESSIONS), str(TMP_CONFIG)],
            capture_output=True, text=True, check=False,
        )
        records = []
        for line in proc.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return records
    finally:
        try:
            TMP_CONFIG.unlink()
        except OSError:
            pass


def suppression_type(override) -> str:
    if override is False:
        return "suppress"
    if isinstance(override, dict):
        if "max_penalty" in override:
            return "max_penalty"
        if "threshold" in override:
            return "threshold_adjustment"
    return "rule_override"


def fingerprint(parts: list[str]) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def already_seen(file_fp: str) -> bool:
    if not DISAGREEMENTS.exists():
        return False
    needle = f'"file_fingerprint":"sha256:{file_fp}"'
    with DISAGREEMENTS.open() as f:
        for line in f:
            if needle in line:
                return True
    return False


def main() -> int:
    DISAGREEMENTS.parent.mkdir(parents=True, exist_ok=True)
    DISAGREEMENTS.touch()

    queries = [
        "filename:nlpm.local.md+rule_overrides",
        "filename:nlpm.md+rule_overrides",
    ]
    items: list[dict] = []
    search_ok = True
    for q in queries:
        ok, found = gh_search_paginated(q)
        if not ok:
            search_ok = False
        items.extend(found)

    total = len(items)
    print(f"Candidate files: {total}", file=sys.stderr)

    counters = {"emitted": 0, "skipped_self": 0, "skipped_dup": 0, "skipped_no_overrides": 0}

    with DISAGREEMENTS.open("a") as out_fh:
        for item in items:
            repo = (item.get("repository") or {}).get("full_name", "")
            file_path = item.get("path", "")
            sha = item.get("sha", "")
            if not (repo and file_path and sha):
                continue

            if repo == SELF_REPO:
                counters["skipped_self"] += 1
                continue

            file_fp = fingerprint([repo, sha, file_path])
            if already_seen(file_fp):
                counters["skipped_dup"] += 1
                continue

            content = gh_fetch_file(repo, file_path)
            if not content:
                continue

            overrides = parse_overrides(content)
            if not overrides:
                counters["skipped_no_overrides"] += 1
                continue

            ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            for rec in overrides:
                rule_id = rec.get("rule_id", "")
                if not rule_id:
                    continue
                val = rec.get("override")
                stype = suppression_type(val)
                rule_fp = "sha256:" + fingerprint([repo, sha, rule_id])
                event = {
                    "event": "downstream_suppression",
                    "timestamp": ts,
                    "repo": repo,
                    "commit_sha": sha,
                    "rule_id": rule_id,
                    "suppression_type": stype,
                    "fingerprint": rule_fp,
                    "file_fingerprint": "sha256:" + file_fp,
                    "path": file_path,
                    "override_value": val,
                    "reason_given": "",
                }
                out_fh.write(json.dumps(event, ensure_ascii=False) + "\n")
                counters["emitted"] += 1

            time.sleep(RATE_DELAY_SECONDS)

    summary = {"candidates": total, **counters, "search_ok": search_ok}
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
