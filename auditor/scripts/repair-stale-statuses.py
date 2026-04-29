#!/usr/bin/env python3
"""Repair statuses corrupted by the pre-fix `resolve-merge-conflicts.sh`
2-way merge race (see three-way-merge-registry.py for root cause).

Reads `auditor/registry/repos.json` and looks for two corruption patterns:

1. status=discovered but commit_sha_at_audit is set
   → audit completed; status was reverted by a concurrent push.
   → repair: set status=audited, score=<from report>.

2. status in {discovered, audited} but pipeline_prs is non-empty
   → contribute completed; status was reverted by a concurrent push.
   → repair: set status=contributed.

Recovers `score` from the per-repo audit report (`auditor/audits/<slug>.md`)
by parsing the `**NL Score**: N/100` line. If the report cannot be parsed,
leaves score unchanged.

Does not touch `tracked` or `complete` — those are downstream of contribute
and the track workflow owns those transitions. Does not write `prs[]`
(the human-curated PR list) — only `pipeline_prs` is auto-managed.

Run with --dry-run to see what would change without writing.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REGISTRY = Path("auditor/registry/repos.json")
AUDITS_DIR = Path("auditor/audits")
SCORE_RE = re.compile(r"\*\*NL Score\*\*:\s*(\d+)\s*/\s*100")


def slug_to_audit_path(slug: str) -> Path:
    return AUDITS_DIR / f"{slug.replace('/', '-')}.md"


def read_score(slug: str) -> int | None:
    path = slug_to_audit_path(slug)
    if not path.exists():
        return None
    for line in path.read_text(errors="replace").splitlines():
        m = SCORE_RE.search(line)
        if m:
            return int(m.group(1))
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data = json.loads(REGISTRY.read_text())
    repos = data["repos"]

    promoted_to_audited = 0
    promoted_to_contributed = 0
    score_recovered = 0

    for slug, r in repos.items():
        status = r.get("status")
        sha = r.get("commit_sha_at_audit")
        prs = r.get("pipeline_prs") or []

        if status == "discovered" and sha:
            r["status"] = "audited"
            promoted_to_audited += 1
            print(f"  audited  ← discovered  {slug}")

        if r.get("score") in (None, 0):
            score = read_score(slug)
            if score is not None:
                r["score"] = score
                score_recovered += 1
                print(f"    score recovered: {score}/100  {slug}")

        if prs and r.get("status") in ("discovered", "audited"):
            r["status"] = "contributed"
            promoted_to_contributed += 1
            print(f"  contributed  ← {status}  {slug} ({len(prs)} pipeline PRs)")

    print()
    print(f"Promoted to audited:    {promoted_to_audited}")
    print(f"Promoted to contributed: {promoted_to_contributed}")
    print(f"Scores recovered:        {score_recovered}")

    if args.dry_run:
        print("\n[dry-run] no changes written")
        return 0

    REGISTRY.write_text(json.dumps(data, indent=2) + "\n")
    print(f"\nWrote {REGISTRY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
