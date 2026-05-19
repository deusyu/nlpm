#!/usr/bin/env python3
"""Render the daily auditor report from cached stats.

Inputs (all optional; missing files become empty dicts/lists):
  /tmp/report/registry-stats.json    — pipeline stage counts
  /tmp/report/issue-counts.json      — open issues by label
  /tmp/report/recent-activity.json   — today's notable events
  /tmp/report/feedback-summary.json  — rule-health + PR scorecard

Output:
  auditor/reports/<YYYY-MM-DD>.md

Extracted from auditor-daily-report.yml in v0.8.10 — the previous
inline-Python-heredoc was 178 lines and untestable. As a script it's
runnable directly, can be invoked manually with synthesized fixtures,
and stops tripping shellcheck-in-actionlint with parser confusion.
"""

import json
from datetime import datetime
from pathlib import Path


def load(path: str, default):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return default


def main() -> int:
    date = datetime.utcnow().strftime('%Y-%m-%d')

    reg = load('/tmp/report/registry-stats.json', {})
    issues = load('/tmp/report/issue-counts.json', {})
    activity = load('/tmp/report/recent-activity.json', [])
    fb = load('/tmp/report/feedback-summary.json', {})

    L = [f"# Daily Report: {date}\n"]

    # Pipeline
    L.append("## Pipeline\n")
    L.append("| Stage | Count |")
    L.append("|-------|-------|")
    by_s = reg.get('by_status') or {}
    for s in ['discovered', 'audited', 'contributed', 'tracked', 'complete']:
        L.append(f"| {s} | {by_s.get(s, 0)} |")
    L.append(f"| **total** | **{reg.get('total', 0)}** |\n")

    # Open issues
    open_issues = {k: v for k, v in issues.items() if v > 0}
    if open_issues:
        L.append("## Awaiting Action\n")
        L.append("| Label | Count |")
        L.append("|-------|-------|")
        for label, count in sorted(open_issues.items()):
            L.append(f"| `{label}` | {count} |")
        L.append("")

    # PR outcomes
    L.append("## PR Scorecard\n")
    L.append("| | Count |")
    L.append("|--------|-------|")
    L.append(f"| Submitted | {fb.get('prs_total', 0)} |")
    L.append(f"| Merged | {fb.get('prs_merged', 0)} |")
    L.append(f"| Applied separately | {fb.get('prs_applied_separately', 0)} |")
    L.append(f"| Rejected | {fb.get('prs_rejected', 0)} |")
    L.append(f"| Pending | {fb.get('prs_pending', 0)} |")
    L.append(
        f"| **Acceptance rate** (merged+applied / resolved) | "
        f"**{fb.get('acceptance_rate', 'N/A')}** |"
    )
    L.append(f"| Merge-only rate (merged / resolved) | {fb.get('merge_only_rate', 'N/A')} |\n")

    # Rule adoption — the rare, best outcome
    adopted = fb.get('rule_adopted_repos', [])
    if adopted:
        L.append("## Rule Adoption\n")
        L.append(
            "*Repos where the maintainer went beyond merging our PRs — "
            "added systemic checks, backfilled siblings, or credited NLPM "
            "in their CHANGELOG.*\n"
        )
        for r in adopted:
            L.append(f"- {r}")
        L.append("")

    # Rule health distribution (SCHEMAS §Learning) — the pulse of the rubric
    states = fb.get('state_counts', {}) or {}
    dormant_n = fb.get('dormant_count', 0)
    if any(states.values()) or dormant_n > 0:
        L.append("## Rule Health\n")
        L.append("| State | Count | Meaning |")
        L.append("|-------|-------|---------|")
        L.append(f"| healthy | {states.get('healthy', 0)} | keeping as-is |")
        L.append(
            f"| noisy | {states.get('noisy', 0)} | high false-positive or low merge precision |"
        )
        L.append(
            f"| disputed | {states.get('disputed', 0)} | maintainer pushback or downstream suppression |"
        )
        L.append(f"| dormant | {dormant_n} | catalog rules with zero hits |")
        L.append("")

    # Top rules with their health state inline.
    # `Drift` is the count of findings whose rule_id was misapplied per the
    # v0.8.16 validate-rule-ids check (wrong artifact type or no semantic
    # overlap with the rule's title). `Validated` is hits minus drift — the
    # honest count of real applications. The 2026-05-13 sweep found R22
    # had 127 hits but only 30 validated (97 drift); raw hits alone would
    # have misled "noisy rule" triage forever. Drift columns surface this.
    top = fb.get('top_rules', [])
    metrics = fb.get('rule_metrics', {}) or {}
    if top:
        L.append("## Rule Frequency\n")
        L.append("*Rules that fire most. `Drift` = scorer misapplied the rule_id; `Validated` = hits − drift, the count to actually trust.*\n")
        L.append("| Rule | Hits | Drift | Validated | Merged | Self-FP | Rejected | Downstream | State |")
        L.append("|------|------|-------|-----------|--------|---------|----------|------------|-------|")
        for rule, hits in top:
            m = metrics.get(rule, {})
            drift = m.get('drift_hits', 0)
            validated = m.get('validated_hits', hits)
            L.append(
                f"| {rule} | {hits} | {drift} | {validated} | "
                f"{m.get('merged', 0)} | {m.get('self_fp', 0)} | "
                f"{m.get('maintainer_rejected', 0)} | {m.get('downstream_suppressions', 0)} | "
                f"{m.get('state', '?')} |"
            )
        L.append("")

    # Noisy rules — candidates for refinement. Sort by validated_hits so
    # drift-inflated raw counts don't push truly-noisy rules out of view.
    noisy = [(rid, m) for rid, m in metrics.items() if m.get('state') == 'noisy']
    if noisy:
        L.append("## Noisy Rules — candidates for refinement\n")
        L.append("*High false-positive rate, or PRs not landing. Validated = hits − drift.*\n")
        L.append("| Rule | Validated | Hits | Drift | Self-FP | Merged/Contributed |")
        L.append("|------|-----------|------|-------|---------|---------------------|")
        for rid, m in sorted(noisy, key=lambda kv: -kv[1].get('validated_hits', kv[1].get('hits', 0))):
            L.append(
                f"| {rid} | {m.get('validated_hits', m['hits'])} | {m['hits']} | "
                f"{m.get('drift_hits', 0)} | {m['self_fp']} | {m['merged']}/{m['contributed']} |"
            )
        L.append("")

    # Disputed rules — external disagreement
    disputed = [(rid, m) for rid, m in metrics.items() if m.get('state') == 'disputed']
    if disputed:
        L.append("## Disputed Rules — external disagreement\n")
        L.append("*Maintainer pushback or downstream suppressions above threshold.*\n")
        L.append("| Rule | Hits | Maintainer-rejected | Downstream suppressions | Top dissent |")
        L.append("|------|------|--------------------|-------------------------|-------------|")
        for rid, m in sorted(disputed, key=lambda kv: -kv[1]['hits']):
            dt = sorted(m.get('dissent_types', {}).items(), key=lambda kv: -kv[1])
            top_dissent = dt[0][0] if dt else "—"
            L.append(
                f"| {rid} | {m['hits']} | {m['maintainer_rejected']} | "
                f"{m['downstream_suppressions']} | {top_dissent} |"
            )
        L.append("")

    # Unclassified rule_ids — namespace drift signal
    unclassified = fb.get('unclassified_ids', []) or []
    if unclassified:
        L.append("## Non-catalog rule IDs seen\n")
        L.append(
            "*SEC-*, BUG-*, CC-* and UNCLASSIFIED findings. Recurring patterns "
            "may deserve a named catalog entry.*\n"
        )
        for rid in unclassified[:20]:
            m = metrics.get(rid, {})
            L.append(f"- `{rid}` — {m.get('hits', 0)} hits ({m.get('state', '?')})")
        if len(unclassified) > 20:
            L.append(f"- … and {len(unclassified) - 20} more")
        L.append("")

    # Activity
    if activity:
        L.append("## Today\n")
        for item in activity[:10]:
            state = item.get('state', '?')
            title = item.get('title', '?')
            L.append(f"- [{state}] {title}")
        L.append("")

    # Self-evolution
    L.append("## Self-Evolution Signals\n")
    L.append("*What should feed back into NLPM itself.*\n")

    if top and len(top) >= 1:
        L.append(
            f"- **Hottest rule**: {top[0][0]} ({top[0][1]} hits) — "
            "earning its keep, or crying wolf?"
        )
    noisy_n = states.get('noisy', 0)
    disputed_n = states.get('disputed', 0)
    if noisy_n > 0:
        L.append(
            f"- **{noisy_n} noisy rule(s)**: refinement candidates — "
            "reduce the false-positive rate or narrow the trigger"
        )
    if disputed_n > 0:
        L.append(
            f"- **{disputed_n} disputed rule(s)**: external disagreement above "
            "threshold — revisit the principle, not just the phrasing"
        )
    if dormant_n > 0 and dormant_n >= 10:
        L.append(
            f"- **{dormant_n} dormant rule(s)**: catalog rules never fired — re-scope or delete"
        )
    rejected_n = fb.get('prs_rejected', 0)
    total_n = fb.get('prs_total', 0)
    if total_n > 0 and rejected_n > 0:
        L.append(
            f"- **Rejection rate {rejected_n}/{total_n}**: "
            "every 'no' is a rule that needs rethinking"
        )
    merged_n = fb.get('prs_merged', 0)
    applied_n = fb.get('prs_applied_separately', 0)
    if merged_n > 0:
        L.append(f"- **{merged_n} merged**: these rules found real bugs — protect them")
    if applied_n > 0:
        L.append(
            f"- **{applied_n} applied separately**: PR closed but fix shipped in a "
            "later release — maintainer took the advice, just not the diff"
        )
    adopted_n = len(fb.get('rule_adopted_repos', []))
    if adopted_n > 0:
        L.append(
            f"- **{adopted_n} rule-adopted**: maintainers went beyond the PR "
            "(systemic hardening, sibling-file backfill, CHANGELOG credit) — "
            "the best possible outcome; study what worked"
        )
    if not top and rejected_n == 0 and merged_n == 0:
        L.append("- Pipeline needs more data — run discover.yml to start")
    L.append("")

    out_path = Path(f'auditor/reports/{date}.md')
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text('\n'.join(L))
    print(f"Report: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
