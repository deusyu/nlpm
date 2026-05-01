#!/usr/bin/env python3
"""Backfill missing entries in `auditor/findings.jsonl` from per-audit sidecars.

Recovers from the append-only log race fixed in v0.7.20: parallel audits
both wrote per-audit sidecars (`auditor/audits/<slug>.findings.jsonl`)
correctly, but only one workflow's append to the global findings.jsonl
survived per push round. The previous resolve-merge-conflicts.sh used
`--ours` for everything except events.jsonl, so the loser's findings
were silently dropped.

This script walks every per-audit sidecar, computes the canonical
fingerprint per `compute-fingerprint.sh`, and appends any missing
entries to the global log. Idempotent — entries that match an existing
fingerprint are skipped, so re-running is safe.

Sidecar slug → repo mapping:
- Try `auditor/registry/repos.json` for an authoritative reverse lookup.
- Fall back to splitting at every dash and matching against registry keys.
- Skip sidecars that can't be mapped (rare; flagged in the report).

The provenance fields (`audit_run_id`, `commit_sha`) are best-effort:
- `commit_sha`: from the registry's `commit_sha_at_audit` if present.
- `audit_run_id`: synthesized as `backfill-2026-05-01` so the entries
  are distinguishable from real audit-run records.

Run with --dry-run to preview without writing.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REGISTRY = Path("auditor/registry/repos.json")
GLOBAL = Path("auditor/findings.jsonl")
AUDITS_DIR = Path("auditor/audits")


def fingerprint(repo: str, finding: dict) -> str:
    """Replicate the exact bash compute-fingerprint.sh formula."""
    payload = (
        f"{repo}|"
        f"{finding.get('file') or ''}|"
        f"{finding.get('rule_id') or ''}|"
        f"{finding.get('pattern') or ''}|"
        f"{finding.get('line') if finding.get('line') is not None else 'null'}\n"
    )
    return f"sha256:{hashlib.sha256(payload.encode()).hexdigest()}"


def slug_to_repo(slug: str, registry_repos: dict) -> str | None:
    """Map a sidecar slug (e.g. 'agent-sh-agnix') to a repo (e.g. 'agent-sh/agnix')."""
    direct = slug.replace("-", "/", 1)
    if direct in registry_repos:
        return direct
    parts = slug.split("-")
    for i in range(1, len(parts)):
        candidate = "/".join(["-".join(parts[:i]), "-".join(parts[i:])])
        if candidate in registry_repos:
            return candidate
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    registry = json.loads(REGISTRY.read_text())
    registry_repos = registry.get("repos", {})

    existing_fps = set()
    if GLOBAL.exists():
        for line in GLOBAL.read_text().splitlines():
            if not line.strip():
                continue
            try:
                f = json.loads(line)
                fp = f.get("fingerprint")
                if fp:
                    existing_fps.add(fp)
            except Exception:
                continue

    print(f"Global findings.jsonl: {len(existing_fps)} existing fingerprints")

    sidecars = sorted(
        p
        for p in glob.glob("auditor/audits/*.findings.jsonl")
        if not p.endswith(".re-audit.findings.jsonl")
    )
    print(f"Per-audit sidecars: {len(sidecars)}")

    backfill_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    appended = 0
    skipped_existing = 0
    skipped_unmapped = 0
    invalid_lines = 0
    new_lines: list[str] = []

    for sidecar_path in sidecars:
        slug = Path(sidecar_path).stem.replace(".findings", "")
        repo = slug_to_repo(slug, registry_repos)
        if not repo:
            entries = sum(1 for line in Path(sidecar_path).read_text().splitlines() if line.strip())
            skipped_unmapped += entries
            print(f"  unmapped slug: {slug}  ({entries} entries skipped)")
            continue

        commit_sha = registry_repos.get(repo, {}).get(
            "commit_sha_at_audit", "unknown"
        )
        audit_run_id = f"backfill-{backfill_ts[:10]}"

        for line in Path(sidecar_path).read_text().splitlines():
            if not line.strip():
                continue
            try:
                f = json.loads(line)
            except Exception:
                invalid_lines += 1
                continue

            fp = fingerprint(repo, f)
            if fp in existing_fps:
                skipped_existing += 1
                continue

            enriched = {
                "event": "finding",
                "timestamp": backfill_ts,
                "audit_run_id": audit_run_id,
                "repo": repo,
                "commit_sha": commit_sha,
                "fingerprint": fp,
                **f,
            }
            new_lines.append(json.dumps(enriched))
            existing_fps.add(fp)
            appended += 1

    print()
    print(f"To append:        {appended}")
    print(f"Skipped existing: {skipped_existing}")
    print(f"Skipped unmapped: {skipped_unmapped}")
    print(f"Invalid lines:    {invalid_lines}")

    if args.dry_run:
        print("\n[dry-run] no changes written")
        return 0

    if appended:
        with GLOBAL.open("a") as fh:
            for line in new_lines:
                fh.write(line + "\n")
        print(f"\nAppended {appended} lines to {GLOBAL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
