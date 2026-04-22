#!/usr/bin/env python3
"""Compute per-rule health metrics from the structured auditor logs.

Runs SCHEMAS §Learning query over the three append-only logs and
classifies every rule_id as healthy, noisy, dormant, or disputed.

Inputs (paths are relative to the repo root):
    auditor/findings.jsonl          — one record per finding
    auditor/logs/events.jsonl       — finding_outcome events (filtered)
    auditor/disagreements.jsonl     — self_fp, maintainer_rejected, pr_comments_snapshot, downstream_suppression
    auditor/registry/repos.json     — rule-adopted repos, total repos audited

Output (argv[1] or stdout): a JSON blob with
    summary.*            — PR scorecard numbers (drop-in replacement for the old feedback-summary.json)
    rule_metrics[rid]    — hits, contributed, merged, closed_unmerged, open, self_fp,
                           maintainer_rejected, downstream_suppressions, dissent_types, state
    dormant_rules[]      — R* rules in the catalog with zero hits
    unclassified_ids[]   — non-catalog rule_ids seen in findings (SEC-*, BUG-*, CC-*)
    metadata.*           — totals, updated_at

All reads are tolerant: missing files produce zeros, malformed JSONL
lines are skipped with a warning to stderr.
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

FINDINGS_PATH = Path("auditor/findings.jsonl")
EVENTS_PATH = Path("auditor/logs/events.jsonl")
DISAGREEMENTS_PATH = Path("auditor/disagreements.jsonl")
REGISTRY_PATH = Path("auditor/registry/repos.json")
RULES_CATALOG = Path("skills/nlpm/rules/SKILL.md")


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records = []
    with path.open() as fh:
        for i, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                print(f"WARN {path}:{i} malformed JSON: {exc}", file=sys.stderr)
    return records


def load_catalog_rules() -> set[str]:
    if not RULES_CATALOG.exists():
        return set()
    text = RULES_CATALOG.read_text()
    return set(re.findall(r"\bR\d{2}\b", text))


def classify_rule(metrics: dict) -> str:
    hits = metrics["hits"]
    contributed = metrics["contributed"]
    self_fp = metrics["self_fp"]
    maintainer_rejected = metrics["maintainer_rejected"]
    downstream = metrics["downstream_suppressions"]
    merged = metrics["merged"]

    # Disputed first — downstream suppressions and maintainer rejection outrank
    # self-precision, since those represent external dissent the auditor
    # can't resolve alone.
    if downstream >= 2:
        return "disputed"
    if contributed >= 3 and maintainer_rejected / contributed > 0.3:
        return "disputed"

    # Noisy: high false-positive rate (self-known or externally inferred).
    if hits >= 3 and self_fp / hits > 0.2:
        return "noisy"
    if contributed >= 3 and merged / contributed < 0.5:
        return "noisy"

    return "healthy"


def main() -> int:
    findings = load_jsonl(FINDINGS_PATH)
    events = load_jsonl(EVENTS_PATH)
    disagreements = load_jsonl(DISAGREEMENTS_PATH)

    try:
        with REGISTRY_PATH.open() as fh:
            registry = json.load(fh)
    except (OSError, json.JSONDecodeError):
        registry = {"repos": {}}

    # Index finding_outcome events by fingerprint. When a fingerprint appears
    # multiple times (e.g., open → merged), the LAST entry wins. events.jsonl
    # is append-only and chronologically ordered, so a simple final-write loop
    # gives the latest state.
    outcome_by_fp: dict[str, str] = {}
    for e in events:
        if e.get("event") != "finding_outcome":
            continue
        data = e.get("data", {})
        state = data.get("pr_state")
        if not state:
            continue
        for fp in data.get("fingerprints", []) or []:
            outcome_by_fp[fp] = state

    self_fp_fps = {
        d.get("fingerprint")
        for d in disagreements
        if d.get("event") == "self_false_positive" and d.get("fingerprint")
    }

    rejected_by_fp: dict[str, list[dict]] = defaultdict(list)
    for d in disagreements:
        if d.get("event") not in ("maintainer_rejected", "maintainer_pushback"):
            continue
        for fp in d.get("fingerprints", []) or []:
            rejected_by_fp[fp].append(d)

    suppressions_by_rule: dict[str, list[dict]] = defaultdict(list)
    for d in disagreements:
        if d.get("event") != "downstream_suppression":
            continue
        rid = d.get("rule_id")
        if rid:
            suppressions_by_rule[rid].append(d)

    findings_by_rule: dict[str, list[dict]] = defaultdict(list)
    for f in findings:
        rid = f.get("rule_id")
        if rid:
            findings_by_rule[rid].append(f)

    rule_metrics: dict[str, dict] = {}
    for rid, fs in findings_by_rule.items():
        unique_fps = {f["fingerprint"] for f in fs if f.get("fingerprint")}
        contributed = sum(1 for fp in unique_fps if fp in outcome_by_fp)
        merged = sum(1 for fp in unique_fps if outcome_by_fp.get(fp) == "merged")
        closed_unmerged = sum(
            1 for fp in unique_fps if outcome_by_fp.get(fp) == "closed_unmerged"
        )
        open_count = sum(1 for fp in unique_fps if outcome_by_fp.get(fp) == "open")
        self_fp = len(unique_fps & self_fp_fps)
        maintainer_rejected = sum(1 for fp in unique_fps if fp in rejected_by_fp)

        dissent_types: Counter[str] = Counter()
        for fp in unique_fps:
            for d in rejected_by_fp.get(fp, []):
                dt = d.get("dissent_type")
                if dt:
                    dissent_types[dt] += 1

        metrics = {
            "hits": len(fs),
            "unique_fingerprints": len(unique_fps),
            "contributed": contributed,
            "merged": merged,
            "closed_unmerged": closed_unmerged,
            "open": open_count,
            "self_fp": self_fp,
            "maintainer_rejected": maintainer_rejected,
            "downstream_suppressions": len(suppressions_by_rule.get(rid, [])),
            "dissent_types": dict(dissent_types),
        }
        metrics["state"] = classify_rule(metrics)
        rule_metrics[rid] = metrics

    # Dormant: catalog R* rules with zero findings. SEC/BUG/CC namespaces are
    # dynamic — no authoritative inventory — so dormant detection is catalog-only.
    catalog = load_catalog_rules()
    dormant_rules = sorted(catalog - set(rule_metrics.keys()))

    # Non-catalog rule_ids that appeared in findings — useful for spotting
    # new SEC-* patterns or UNCLASSIFIED drift.
    unclassified_ids = sorted(set(rule_metrics.keys()) - catalog)

    # PR scorecard from the registry (drop-in for the old summary).
    all_prs = []
    for _, v in registry.get("repos", {}).items():
        all_prs.extend(v.get("prs", []) or [])

    merged_prs = [p for p in all_prs if p.get("outcome") == "merged"]
    applied_prs = [p for p in all_prs if p.get("outcome") == "applied_separately"]
    rejected_prs = [p for p in all_prs if p.get("outcome") == "rejected"]
    open_prs = [p for p in all_prs if p.get("outcome") == "open"]
    accepted = len(merged_prs) + len(applied_prs)
    resolved = accepted + len(rejected_prs)

    rule_adopted = [
        k for k, v in registry.get("repos", {}).items() if v.get("rule_adopted") is True
    ]

    # Top rules for the report's Rule Frequency table — ordered by hits.
    top_rules = sorted(
        rule_metrics.items(), key=lambda kv: -kv[1]["hits"]
    )[:10]

    summary = {
        "prs_total": len(all_prs),
        "prs_merged": len(merged_prs),
        "prs_applied_separately": len(applied_prs),
        "prs_rejected": len(rejected_prs),
        "prs_pending": len(open_prs),
        "acceptance_rate": f"{accepted / resolved * 100:.0f}%" if resolved else "N/A",
        "merge_only_rate": f"{len(merged_prs) / resolved * 100:.0f}%" if resolved else "N/A",
        "rule_adopted_repos": rule_adopted,
        "top_rules": [(rid, m["hits"]) for rid, m in top_rules],
        "rule_metrics": rule_metrics,
        "dormant_rules": dormant_rules,
        "unclassified_ids": unclassified_ids,
        "state_counts": dict(
            Counter(m["state"] for m in rule_metrics.values())
        ),
        "dormant_count": len(dormant_rules),
    }

    # Mirror into auditor/feedback/log.json so the legacy shape continues
    # to carry the fields older tooling might read. Only the fields that
    # the old pipeline wrote are kept here.
    feedback_path = Path("auditor/feedback/log.json")
    if feedback_path.exists():
        try:
            with feedback_path.open() as fh:
                feedback = json.load(fh)
        except (OSError, json.JSONDecodeError):
            feedback = {"metadata": {}, "rule_stats": {}}
    else:
        feedback = {"metadata": {}, "rule_stats": {}}

    feedback.setdefault("metadata", {}).update({
        "total_prs_submitted": len(all_prs),
        "total_prs_merged": len(merged_prs),
        "total_prs_applied_separately": len(applied_prs),
        "total_prs_rejected": len(rejected_prs),
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    })
    feedback.setdefault("rule_stats", {})
    for rid, m in rule_metrics.items():
        feedback["rule_stats"].setdefault(
            rid, {"total_hits": 0, "led_to_merged_pr": 0, "led_to_rejected_pr": 0}
        )
        feedback["rule_stats"][rid].update({
            "total_hits": m["hits"],
            "led_to_merged_pr": m["merged"],
            "led_to_rejected_pr": m["closed_unmerged"],
            "self_false_positive": m["self_fp"],
            "maintainer_rejected": m["maintainer_rejected"],
            "downstream_suppressions": m["downstream_suppressions"],
            "state": m["state"],
        })
    with feedback_path.open("w") as fh:
        json.dump(feedback, fh, indent=2)

    out = json.dumps(summary, indent=2)
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(out)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
