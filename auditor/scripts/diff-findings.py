#!/usr/bin/env python3
"""Diff a re-audit's findings against the original audit's findings.

Invoked by `auditor-case-study.yml` after a post-merge re-score of a target
repo. Produces three outputs:

1. `finding_verified` events — one per original finding, outcome ∈
   {persists_identically, persists_line_shifted, fixed_and_merged,
    fixed_applied_separately, fixed_upstream_not_merged}.
2. `finding_introduced` events — one per re-audit finding that has no
   counterpart in the original audit.
3. A human-readable diff report at `<auditor/audits/<slug>.re-audit.diff.md>`
   that the case-study writer prompt consumes.

Design notes:

- The fingerprint formula (SCHEMAS.md §fingerprint) includes `line`, so line
  shifts change the fingerprint. This script does BOTH a strict match (same
  fingerprint → `persists_identically`) and a loose match (same
  repo+file+rule_id+pattern, any line → `persists_line_shifted`) so
  maintainer edits that merely rewrap or reorder code don't look like fixes.
- PR outcomes are joined through the `nlpm-metadata` block parsed by
  `auditor-track.yml` into `registry/repos.json[repo].prs[].fingerprints[]`.
  A finding's outcome is `fixed_and_merged` if any merged PR carried its
  fingerprint, `fixed_applied_separately` if any closed-unmerged PR carried
  it (maintainer applied the fix their own way), else
  `fixed_upstream_not_merged` (maintainer fixed it independently of our PRs).
- Re-audit findings are NOT appended to the global `auditor/findings.jsonl`.
  Double-counting the same rule against the same repo would inflate
  per-rule reach in `rule-health.py`. The sidecar and events are sufficient.

Usage:

    diff-findings.py \\
        --repo owner/name \\
        --original-sidecar auditor/audits/owner-name.findings.jsonl \\
        --reaudit-sidecar auditor/audits/owner-name.re-audit.findings.jsonl \\
        --registry auditor/registry/repos.json \\
        --commit-sha-before <sha> \\
        --commit-sha-after <sha> \\
        --events-out auditor/logs/events.jsonl \\
        --diff-report-out auditor/audits/owner-name.re-audit.diff.md \\
        --summary-out /tmp/re-audit-summary.json

All inputs are read-only; outputs are appended (events) or overwritten
(diff report, summary).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Fingerprint — must match auditor/scripts/compute-fingerprint.sh exactly.
# If this drifts from the shell implementation, every downstream metric
# silently breaks. Kept in sync by an explicit cross-reference in SCHEMAS.md
# §fingerprint and by _run_self_tests() below.
#
# Two shell behaviours Python must match:
#   1. jq emits its output with a trailing "\n" that shasum folds into the
#      digest — the spec payload is `<fields...>\n`, not `<fields...>`.
#   2. jq's string interpolation `"\(.x // "")"` returns `""` ONLY when
#      `.x` is null or missing. For a number, it emits the JSON scalar
#      ("0", "42"); for a boolean, it emits lowercase "true"/"false".
#      Python's `finding.get("x") or ""` collapses `0`, `False`, and `""`
#      all to `""` — which diverges for any malformed sidecar row whose
#      field is numeric or boolean.
# See SCHEMAS.md §fingerprint for the canonical description.
# ---------------------------------------------------------------------------

def _coerce_pr_number(value: object) -> int | None:
    """Normalize a PR number to `int | None` for event emission.

    The registry currently stores `pr.number` as a JSON integer (track.yml
    uses `jq --argjson`, preserving types from `gh pr view`). But nothing
    across the pipeline enforces that invariant — a legacy record, a
    hand-edit, or a future tool using `jq --arg` could leak a string.
    `finding_verified` events carry `pr_number` in their data payload; if
    it sometimes lands as `42` and sometimes as `"42"`, every consumer
    joining on that field has to branch on type.

    Boundary normalization. Accepts:
      - int → returned as-is
      - str (decimal, optionally prefixed with `#`) → parsed to int
      - anything else (None, bool, float, list, dict, junk string) → None

    Bool is rejected even though `isinstance(True, int)` is true in Python:
    a boolean PR number is always bad data.
    """
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        stripped = value.strip().lstrip("#")
        if stripped.isdigit():
            return int(stripped)
        return None
    return None


def _jq_stringify(value: object, if_falsy: str = "") -> str:
    """Mirror `\\(.field // default)` jq semantics in Python.

    Critical subtlety: jq's alternative operator `//` defaults on both
    `null` AND `false`. Every other value (including `0`, `""`, `[]`,
    `{}`) is truthy for `//`. So this helper returns `if_falsy` for both
    `None` and `False`, and passes through everything else via JSON-scalar
    stringification. Missing this distinction previously let a finding
    with `pattern: false` produce divergent Python vs shell fingerprints.

    Covered by a self-test case in `_run_self_tests` — adding new
    edge cases there is the failure-first way to extend this."""
    if value is None or value is False:
        return if_falsy
    if value is True:
        return "true"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        # jq renders 1.0 as "1" but 1.5 as "1.5" — match it.
        return str(int(value)) if value.is_integer() else repr(value)
    if isinstance(value, str):
        return value
    return str(value)


def compute_fingerprint(repo: str, finding: dict) -> str:
    file_ = _jq_stringify(finding.get("file"), "")
    rule_id = _jq_stringify(finding.get("rule_id"), "")
    pattern = _jq_stringify(finding.get("pattern"), "")
    line_str = _jq_stringify(finding.get("line"), "null")
    # Trailing "\n" matches jq's output mode, which the shell helper pipes
    # into shasum. Removing it would silently invalidate every fingerprint
    # emitted by audit.yml and contribute.yml.
    payload = f"{repo}|{file_}|{rule_id}|{pattern}|{line_str}\n"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def loose_key(repo: str, finding: dict) -> tuple[str, str, str, str]:
    """Fingerprint minus the line number — matches findings across line shifts."""
    return (
        repo,
        finding.get("file") or "",
        finding.get("rule_id") or "",
        finding.get("pattern") or "",
    )


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_jsonl(path: Path) -> tuple[list[dict], int]:
    """Tolerant reader — missing file → ([], 0); malformed lines are dropped
    with a warning. Returns (records, malformed_count) so the caller can
    surface low-confidence runs in the summary. Silent-drop is the right
    posture (matches audit.yml's aggregation tolerance), but a non-zero
    count is worth flagging upstream — it means a re-audit ran with
    incomplete data and the `fixed` tally may under-count."""
    if not path.exists():
        return [], 0
    records: list[dict] = []
    malformed = 0
    with path.open() as fh:
        for i, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                print(f"WARN {path}:{i} malformed JSON: {exc}", file=sys.stderr)
                malformed += 1
    return records, malformed


def load_registry_pr_outcomes(registry_path: Path, repo: str) -> dict[str, dict]:
    """Return {fingerprint: pr_record} for every PR filed against this repo.

    When two PRs carry the same fingerprint (rare — manual reopen + re-submit),
    the merged/applied one wins over the rejected/open one."""
    try:
        with registry_path.open() as fh:
            registry = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {}

    repo_entry = registry.get("repos", {}).get(repo, {})
    prs = repo_entry.get("prs", []) or []

    # Precedence for outcome resolution: merged > applied_separately > open > rejected.
    # Ensures that a reopened-and-merged PR beats a prior rejected sibling.
    precedence = {"merged": 0, "applied_separately": 1, "open": 2, "rejected": 3}
    by_fp: dict[str, dict] = {}
    for pr in prs:
        outcome = pr.get("outcome") or ""
        rank = precedence.get(outcome, 99)
        for fp in pr.get("fingerprints", []) or []:
            existing = by_fp.get(fp)
            if existing is None or rank < precedence.get(existing.get("outcome") or "", 99):
                by_fp[fp] = pr
    return by_fp


# ---------------------------------------------------------------------------
# Outcome classification
# ---------------------------------------------------------------------------

OUTCOME_FIXED_AND_MERGED = "fixed_and_merged"
OUTCOME_FIXED_APPLIED = "fixed_applied_separately"
OUTCOME_FIXED_UPSTREAM = "fixed_upstream_not_merged"
OUTCOME_PERSISTS_IDENTICALLY = "persists_identically"
OUTCOME_PERSISTS_SHIFTED = "persists_line_shifted"


def classify_original(
    finding: dict,
    fingerprint: str,
    strict_counts: Counter,
    loose_counts: Counter,
    pr_by_fp: dict[str, dict],
    repo: str,
) -> tuple[str, dict | None]:
    """Given an original finding, decide its post-merge outcome.

    Mutates `strict_counts` / `loose_counts` by decrementing on a match —
    this enforces 1:1 pairing between original findings and re-audit
    findings. Without that, two originals sharing `(file, rule_id,
    pattern, null_line)` (common for file-level findings) would both
    match a single re-audit finding and both be marked as persisting,
    under-reporting the fixed count. The caller iterates originals in
    input order, so the pairing is deterministic by source position.

    Returns (outcome, matching_pr_record_or_None)."""
    if strict_counts[fingerprint] > 0:
        strict_counts[fingerprint] -= 1
        # Consume the same match from the loose counter so introduced
        # detection downstream doesn't double-count this re-audit row.
        loose_counts[loose_key(repo, finding)] -= 1
        return OUTCOME_PERSISTS_IDENTICALLY, None

    lk = loose_key(repo, finding)
    if loose_counts[lk] > 0:
        loose_counts[lk] -= 1
        return OUTCOME_PERSISTS_SHIFTED, None

    # The finding is gone from the re-audit — it was fixed. Attribute.
    pr = pr_by_fp.get(fingerprint)
    if pr is not None:
        outcome = pr.get("outcome") or ""
        if outcome == "merged":
            return OUTCOME_FIXED_AND_MERGED, pr
        if outcome == "applied_separately":
            return OUTCOME_FIXED_APPLIED, pr
        # An open or rejected PR carried this fingerprint but the finding is
        # gone. Most likely: the maintainer fixed it in a parallel commit.
        return OUTCOME_FIXED_UPSTREAM, pr

    # No PR ever carried this fingerprint — maintainer found and fixed it
    # independently of our contribution.
    return OUTCOME_FIXED_UPSTREAM, None


# ---------------------------------------------------------------------------
# Event emission
# ---------------------------------------------------------------------------

def emit_event(
    events_path: Path,
    event: str,
    workflow: str,
    data: dict,
    run_id: str,
    run_number: int,
) -> None:
    """Append a single event record to events.jsonl in the canonical shape
    (`timestamp`, `workflow`, `event`, `run_id`, `run_number`, `data`).

    Matches `auditor/scripts/log-event.sh` so consumers don't have to branch
    on emitter identity."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "workflow": workflow,
        "event": event,
        "run_id": run_id,
        "run_number": run_number,
        "data": data,
    }
    events_path.parent.mkdir(parents=True, exist_ok=True)
    with events_path.open("a") as fh:
        fh.write(json.dumps(record, separators=(",", ":")) + "\n")


# ---------------------------------------------------------------------------
# Diff report rendering
# ---------------------------------------------------------------------------

OUTCOME_LABEL = {
    OUTCOME_PERSISTS_IDENTICALLY: "persists (identical)",
    OUTCOME_PERSISTS_SHIFTED: "persists (line shifted)",
    OUTCOME_FIXED_AND_MERGED: "fixed — our PR merged",
    OUTCOME_FIXED_APPLIED: "fixed — applied separately",
    OUTCOME_FIXED_UPSTREAM: "fixed — upstream, not via our PR",
}


def render_diff_report(
    repo: str,
    commit_sha_before: str,
    commit_sha_after: str,
    date_iso: str,
    original_score: int | None,
    reaudit_score: int | None,
    verified_rows: list[dict],
    introduced_rows: list[dict],
) -> str:
    """Emit the markdown the writer prompt splices into the case study.

    The shape mirrors the manual Re-Audit section from the mirror-test case
    study (2026-04-24-mirror-test.md) so article tone stays consistent."""

    def fmt_score(s: int | None) -> str:
        return f"{s}/100" if s is not None else "—"

    out: list[str] = []
    out.append(f"# Re-Audit: {repo}")
    out.append("")
    out.append(
        f"**Date**: {date_iso}  |  **Before**: `{commit_sha_before[:7]}` "
        f"({fmt_score(original_score)})  |  **After**: `{commit_sha_after[:7]}` "
        f"({fmt_score(reaudit_score)})"
    )
    out.append("")

    # Summary table: count of each outcome.
    outcome_counts = Counter(row["outcome"] for row in verified_rows)
    out.append("## Summary")
    out.append("")
    out.append("| Outcome | Count |")
    out.append("|---------|------:|")
    for outcome in (
        OUTCOME_FIXED_AND_MERGED,
        OUTCOME_FIXED_APPLIED,
        OUTCOME_FIXED_UPSTREAM,
        OUTCOME_PERSISTS_SHIFTED,
        OUTCOME_PERSISTS_IDENTICALLY,
    ):
        n = outcome_counts.get(outcome, 0)
        if n:
            out.append(f"| {OUTCOME_LABEL[outcome]} | {n} |")
    if introduced_rows:
        out.append(f"| newly introduced (regressions) | {len(introduced_rows)} |")
    out.append("")

    # Per-finding table — what every original finding's fate was.
    if verified_rows:
        out.append("## Original findings — verification")
        out.append("")
        out.append("| # | File | Line | Rule | Pattern | Outcome | PR |")
        out.append("|---|------|------|------|---------|---------|----|")
        for i, row in enumerate(verified_rows, 1):
            pr_cell = ""
            if row.get("pr_number"):
                pr_cell = f"#{row['pr_number']}"
            line_cell = str(row["line"]) if row.get("line") is not None else "—"
            out.append(
                f"| {i} | `{row['file']}` | {line_cell} | {row['rule_id']} | "
                f"`{row['pattern']}` | {OUTCOME_LABEL[row['outcome']]} | {pr_cell} |"
            )
        out.append("")

    # Introduced findings — may be regressions the maintainer shipped, or
    # drift that was already latent but now meets the rubric's threshold.
    if introduced_rows:
        out.append("## Findings introduced since audit")
        out.append("")
        out.append(
            "These findings appear in the re-audit but were not in the "
            "original audit. They may be true regressions (new commits "
            "introduced them) or artifacts of scoring drift."
        )
        out.append("")
        out.append("| # | File | Line | Rule | Pattern | Description |")
        out.append("|---|------|------|------|---------|-------------|")
        for i, row in enumerate(introduced_rows, 1):
            line_cell = str(row["line"]) if row.get("line") is not None else "—"
            out.append(
                f"| {i} | `{row['file']}` | {line_cell} | {row['rule_id']} | "
                f"`{row['pattern']}` | {row['description']} |"
            )
        out.append("")

    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--original-sidecar", required=True, type=Path)
    parser.add_argument("--reaudit-sidecar", required=True, type=Path)
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--commit-sha-before", required=True)
    parser.add_argument("--commit-sha-after", required=True)
    parser.add_argument("--events-out", required=True, type=Path)
    parser.add_argument("--diff-report-out", required=True, type=Path)
    parser.add_argument("--summary-out", required=True, type=Path)
    parser.add_argument("--date-iso", default=None,
                        help="Override the date in the diff report header")
    parser.add_argument("--original-score", type=int, default=None)
    parser.add_argument("--reaudit-score", type=int, default=None)
    parser.add_argument("--run-id", default=os.environ.get("GITHUB_RUN_ID", "local"))
    parser.add_argument("--run-number", type=int,
                        default=int(os.environ.get("GITHUB_RUN_NUMBER", "0")))
    args = parser.parse_args()

    repo = args.repo
    date_iso = args.date_iso or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    original, original_malformed = load_jsonl(args.original_sidecar)
    reaudit, reaudit_malformed = load_jsonl(args.reaudit_sidecar)

    # Fingerprint both sides. We compute in-process rather than calling the
    # shell helper so the script stays a single invocation.
    for f in original:
        f["_fp"] = compute_fingerprint(repo, f)
    for f in reaudit:
        f["_fp"] = compute_fingerprint(repo, f)

    # Counters, not sets — we need multiplicity so pairing stays 1:1
    # between original and re-audit findings. classify_original decrements
    # on match.
    strict_counts = Counter(f["_fp"] for f in reaudit)
    loose_counts = Counter(loose_key(repo, f) for f in reaudit)

    pr_by_fp = load_registry_pr_outcomes(args.registry, repo)

    verified_rows: list[dict] = []
    for f in original:
        outcome, pr = classify_original(
            f, f["_fp"], strict_counts, loose_counts, pr_by_fp, repo
        )
        row = {
            "fingerprint": f["_fp"],
            "rule_id": f.get("rule_id") or "UNCLASSIFIED",
            "file": f.get("file") or "",
            "line": f.get("line"),
            "pattern": f.get("pattern") or "",
            "description": f.get("description") or "",
            "outcome": outcome,
            # Always int|None — any registry-shape drift is flattened here.
            # See _coerce_pr_number for the accepted input forms.
            "pr_number": _coerce_pr_number(pr.get("number")) if pr else None,
        }
        verified_rows.append(row)

        # Emit finding_verified event. Preserves the original fingerprint so
        # rule-health.py can join without re-deriving.
        emit_event(
            args.events_out,
            event="finding_verified",
            workflow="case-study",
            data={
                "repo": repo,
                "fingerprint": f["_fp"],
                "rule_id": row["rule_id"],
                "file": row["file"],
                "pattern": row["pattern"],
                "outcome": outcome,
                "commit_sha_before": args.commit_sha_before,
                "commit_sha_after": args.commit_sha_after,
                "pr_number": row["pr_number"],
            },
            run_id=args.run_id,
            run_number=args.run_number,
        )

    # Introduced findings: re-audit rows that had no pairing partner on
    # the original side. classify_original decremented `loose_counts` by
    # one per matched original, so the remaining positive counts are
    # exactly the un-paired re-audit rows. We iterate re-audit in source
    # order and consume from the counter to preserve that pairing.
    introduced_rows: list[dict] = []
    for f in reaudit:
        lk = loose_key(repo, f)
        if loose_counts[lk] <= 0:
            continue
        loose_counts[lk] -= 1
        row = {
            "fingerprint": f["_fp"],
            "rule_id": f.get("rule_id") or "UNCLASSIFIED",
            "file": f.get("file") or "",
            "line": f.get("line"),
            "pattern": f.get("pattern") or "",
            "description": f.get("description") or "",
            "severity": f.get("severity") or "info",
        }
        introduced_rows.append(row)
        emit_event(
            args.events_out,
            event="finding_introduced",
            workflow="case-study",
            data={
                "repo": repo,
                "fingerprint": f["_fp"],
                "rule_id": row["rule_id"],
                "file": row["file"],
                "pattern": row["pattern"],
                "severity": row["severity"],
                "commit_sha": args.commit_sha_after,
            },
            run_id=args.run_id,
            run_number=args.run_number,
        )

    report = render_diff_report(
        repo=repo,
        commit_sha_before=args.commit_sha_before,
        commit_sha_after=args.commit_sha_after,
        date_iso=date_iso,
        original_score=args.original_score,
        reaudit_score=args.reaudit_score,
        verified_rows=verified_rows,
        introduced_rows=introduced_rows,
    )
    args.diff_report_out.parent.mkdir(parents=True, exist_ok=True)
    args.diff_report_out.write_text(report)

    outcome_counts = Counter(row["outcome"] for row in verified_rows)
    summary = {
        "repo": repo,
        "date": date_iso,
        "original_score": args.original_score,
        "reaudit_score": args.reaudit_score,
        "commit_sha_before": args.commit_sha_before,
        "commit_sha_after": args.commit_sha_after,
        "original_findings_count": len(original),
        "reaudit_findings_count": len(reaudit),
        "original_malformed_count": original_malformed,
        "reaudit_malformed_count": reaudit_malformed,
        "verified": {k: outcome_counts.get(k, 0) for k in OUTCOME_LABEL},
        "introduced_count": len(introduced_rows),
        "fixed_total": sum(
            outcome_counts.get(k, 0) for k in (
                OUTCOME_FIXED_AND_MERGED,
                OUTCOME_FIXED_APPLIED,
                OUTCOME_FIXED_UPSTREAM,
            )
        ),
        "persists_total": sum(
            outcome_counts.get(k, 0) for k in (
                OUTCOME_PERSISTS_IDENTICALLY,
                OUTCOME_PERSISTS_SHIFTED,
            )
        ),
    }
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    args.summary_out.write_text(json.dumps(summary, indent=2))

    # Also echo to stdout so the workflow can capture and use as an output.
    print(json.dumps(summary))
    return 0


# ---------------------------------------------------------------------------
# Self-tests — invoked with `--self-test`. Kept in the same file so CI can
# gate on a single invocation and so drift from compute-fingerprint.sh shows
# up the moment either implementation changes.
# ---------------------------------------------------------------------------

def _run_self_tests() -> int:
    import subprocess

    script_dir = Path(__file__).resolve().parent
    shell_helper = script_dir / "compute-fingerprint.sh"
    repo = "demo/repo"

    # Every case the shell might feed us. Keep this set exhaustive —
    # gaps here are exactly where fingerprint drift hides.
    cases: list[tuple[str, dict]] = [
        ("typical string fields", {
            "file": "agents/foo.md",
            "rule_id": "BUG-missing-frontmatter",
            "pattern": "missing-name",
            "line": 1,
        }),
        ("null line (file-level finding)", {
            "file": "agents/foo.md",
            "rule_id": "CC-orphan-component",
            "pattern": "orphan",
            "line": None,
        }),
        ("missing line key (legacy sidecar)", {
            "file": "agents/foo.md",
            "rule_id": "CC-orphan-component",
            "pattern": "orphan",
        }),
        ("empty string fields", {
            "file": "",
            "rule_id": "",
            "pattern": "",
            "line": 0,
        }),
        ("numeric rule_id (malformed Claude output)", {
            "file": "agents/foo.md",
            "rule_id": 1,
            "pattern": "missing-name",
            "line": 5,
        }),
        ("boolean false in pattern (malformed Claude output)", {
            "file": "agents/foo.md",
            "rule_id": "R01",
            "pattern": False,
            "line": 5,
        }),
        ("boolean true in pattern (malformed Claude output)", {
            "file": "agents/foo.md",
            "rule_id": "R01",
            "pattern": True,
            "line": 5,
        }),
        ("line as string (jq permits either shape)", {
            "file": "agents/foo.md",
            "rule_id": "R01",
            "pattern": "x",
            "line": "42",
        }),
        ("path with spaces and special characters", {
            "file": "agents/foo bar/baz's file.md",
            "rule_id": "R01",
            "pattern": "vague-|-pipe-in-pattern",
            "line": 1,
        }),
        ("unicode file name", {
            "file": "agents/テスト.md",
            "rule_id": "R01",
            "pattern": "unicode",
            "line": 1,
        }),
    ]

    fails = 0
    for label, finding in cases:
        py_fp = compute_fingerprint(repo, finding)
        shell_cmd = (
            f'source "{shell_helper}" && '
            f'printf "%s" {json.dumps(json.dumps(finding))} | compute_fingerprint "{repo}"'
        )
        result = subprocess.run(
            ["bash", "-c", shell_cmd],
            capture_output=True, text=True, check=True,
        )
        sh_fp = result.stdout.strip()
        if py_fp != sh_fp:
            print(
                f"FAIL [{label}]: Python fingerprint != shell fingerprint\n"
                f"  input:  {finding}\n"
                f"  python: {py_fp}\n"
                f"  shell:  {sh_fp}",
                file=sys.stderr,
            )
            fails += 1

    if fails:
        print(f"\n{fails} fingerprint mismatch(es) — fingerprint contract broken.",
              file=sys.stderr)
        return 1

    # PR-number coercion cases — the event's pr_number must always be
    # int|None regardless of registry shape drift. Add new shapes here
    # as they appear in the wild.
    coerce_cases: list[tuple[object, int | None]] = [
        (42, 42),                 # canonical: jq-preserved integer
        ("42", 42),               # legacy/hand-edit: string of digits
        ("#42", 42),              # defensive: human-readable prefix
        ("  42  ", 42),           # defensive: whitespace
        (None, None),             # missing
        ("", None),               # empty string
        ("forty-two", None),      # non-numeric junk
        (True, None),             # bool sneaking through as int subclass
        (False, None),
        (3.14, None),             # float — not a PR number
        ([42], None),             # list — bad data
        ({"n": 42}, None),        # dict — bad data
    ]
    coerce_fails = 0
    for value, expected in coerce_cases:
        got = _coerce_pr_number(value)
        if got != expected:
            print(
                f"FAIL [pr_number coerce]: input={value!r} expected={expected!r} got={got!r}",
                file=sys.stderr,
            )
            coerce_fails += 1
    if coerce_fails:
        print(f"\n{coerce_fails} pr_number coercion mismatch(es).", file=sys.stderr)
        return 1

    print(
        f"diff-findings.py self-tests: OK "
        f"({len(cases)} fingerprint cases, {len(coerce_cases)} pr_number cases)"
    )
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        sys.exit(_run_self_tests())
    sys.exit(main())
