#!/usr/bin/env python3
"""Prepare refinement input for the quarterly rule-refinement run.

Joins rule-health metrics with the raw evidence (maintainer quotes, rule
gaps, downstream suppression reasons) needed to weight refinement
proposals. Writes /tmp/refinement-input.json.

Inputs:
  /tmp/rule-health.json         — produced by auditor/scripts/rule-health.py
  auditor/disagreements.jsonl   — raw dissent events

Output:
  /tmp/refinement-input.json    — {proposals: [...], generated_at: ISO8601}
  Also prints the proposal count to stdout.

Extracted from auditor-refine-rules.yml in v0.8.10 (was a 90-line
inline Python heredoc).
"""

from __future__ import annotations

import json
import os
from collections import defaultdict
from datetime import datetime, timezone


HEALTH_PATH = "/tmp/rule-health.json"
DISAGREEMENTS_PATH = "auditor/disagreements.jsonl"
OUT_PATH = "/tmp/refinement-input.json"


def collect_evidence(path: str) -> tuple[dict, dict, dict]:
    """Walk disagreements.jsonl, group quotes / gaps / suppression-reasons by rule."""
    quotes_by_rule: dict[str, list[dict]] = defaultdict(list)
    gaps_by_rule: dict[str, list[str]] = defaultdict(list)
    reasons_by_rule: dict[str, list[dict]] = defaultdict(list)

    if not os.path.exists(path):
        return quotes_by_rule, gaps_by_rule, reasons_by_rule

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            ev = d.get("event")
            if ev in ("maintainer_rejected", "maintainer_pushback"):
                q = (d.get("quote") or "").strip()
                if q:
                    for rid in d.get("rule_ids", []) or []:
                        quotes_by_rule[rid].append({
                            "quote": q,
                            "dissent_type": d.get("dissent_type"),
                            "pr": d.get("pr"),
                            "confidence": d.get("classifier_confidence"),
                        })
            elif ev == "self_false_positive":
                rid = d.get("rule_id")
                gap = (d.get("rule_gap") or "").strip()
                if rid and gap:
                    gaps_by_rule[rid].append(gap)
            elif ev == "downstream_suppression":
                rid = d.get("rule_id")
                reason = (d.get("reason_given") or "").strip()
                if rid:
                    reasons_by_rule[rid].append({
                        "reason": reason or "(no reason given)",
                        "path": d.get("path"),
                        "type": d.get("suppression_type"),
                    })

    return quotes_by_rule, gaps_by_rule, reasons_by_rule


def main() -> int:
    with open(HEALTH_PATH) as f:
        health = json.load(f)

    quotes_by_rule, gaps_by_rule, reasons_by_rule = collect_evidence(DISAGREEMENTS_PATH)

    metrics = health.get("rule_metrics", {}) or {}
    proposals = []
    for rid, m in metrics.items():
        if m.get("state") not in ("noisy", "disputed"):
            continue
        if m.get("hits", 0) < 3:
            continue
        proposals.append({
            "rule_id": rid,
            "state": m["state"],
            "metrics": {k: v for k, v in m.items() if k != "state"},
            # Cap evidence payload so the prompt stays focused.
            # High-confidence quotes first.
            "maintainer_quotes": sorted(
                quotes_by_rule.get(rid, []),
                key=lambda q: {"high": 0, "medium": 1, "low": 2}.get(q.get("confidence"), 3),
            )[:5],
            "rule_gaps": gaps_by_rule.get(rid, [])[:5],
            "downstream_reasons": reasons_by_rule.get(rid, [])[:5],
        })

    # Order: disputed first (external signal is stronger), then noisy,
    # then by hits descending.
    proposals.sort(key=lambda p: (p["state"] != "disputed", -p["metrics"].get("hits", 0)))

    out = {
        "proposals": proposals,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Prepared {len(proposals)} refinement proposal(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
