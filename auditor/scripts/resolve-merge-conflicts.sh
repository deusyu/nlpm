#!/usr/bin/env bash
# Resolve merge conflicts for auditor-managed files using the right strategy per file.
#
# Called by push-retry loops in auditor-audit.yml, auditor-contribute.yml,
# and auditor-daily-report.yml after `git pull` when a concurrent push has
# created conflicts. Uses :2 (ours = this commit) and :3 (theirs = remote).
#
# Strategies:
#   auditor/registry/repos.json  → jq deep merge (ours wins on overlap, union on additions)
#   auditor/logs/events.jsonl    → line union (concat + dedupe, preserves events from both sides)
#   everything else              → --ours (keep this commit's work; never silently revert to remote)
#
# Why `--ours` as default: the previous `--theirs` default silently dropped
# the current workflow's own data whenever a concurrent push beat it to main.
# Lost pipeline_prs on wshobson/agents #488-#492 is a concrete example.

set -euo pipefail

# Use a per-run temp directory so concurrent resolver runs (multiple
# auditor workflows hitting a push-conflict at the same instant) can't
# stomp on each other's /tmp/reg-*.json or /tmp/log-*.jsonl staging files.
RESOLVE_TMPDIR=$(mktemp -d -t nlpm-resolve.XXXXXX)
trap 'rm -rf "$RESOLVE_TMPDIR"' EXIT

conflicted_paths() {
  git diff --name-only --diff-filter=U 2>/dev/null || true
}

# Registry: 3-way merge preserves remote updates to entries this workflow
# didn't touch. The previous strategy (`jq -s '.[0] * .[1]' theirs ours`)
# was a 2-way recursive merge with ours-wins, which silently reverted
# remote updates whenever this workflow's checkout was stale. Concrete
# symptom: audit commits flipping unrelated entries (e.g.,
# kepano/obsidian-skills) back to status=discovered/score=null on every
# concurrent push. The 3-way merge uses git's BASE (:1) to distinguish
# "current workflow changed this field" from "field is the same as
# checkout-time." Only fields the current workflow actually modified
# come from ours; everything else takes the remote version.
#
# Validate the merged result before writing — a malformed merge would
# silently corrupt the registry on disk (observed 2026-04-28: an
# unguarded merge produced two concatenated top-level objects).
if conflicted_paths | grep -qx "auditor/registry/repos.json"; then
  echo "Resolving auditor/registry/repos.json via 3-way merge"
  git show :1:auditor/registry/repos.json > "$RESOLVE_TMPDIR/reg-base.json"   # merge base
  git show :2:auditor/registry/repos.json > "$RESOLVE_TMPDIR/reg-ours.json"   # our commit
  git show :3:auditor/registry/repos.json > "$RESOLVE_TMPDIR/reg-theirs.json" # remote
  python3 auditor/scripts/three-way-merge-registry.py \
      "$RESOLVE_TMPDIR/reg-base.json" "$RESOLVE_TMPDIR/reg-ours.json" "$RESOLVE_TMPDIR/reg-theirs.json" \
      > "$RESOLVE_TMPDIR/reg.json" \
    || { echo "ERROR: three-way merge failed; refusing to write"; exit 1; }
  REG_TMP="$RESOLVE_TMPDIR/reg.json" bash auditor/scripts/atomic-registry-write.sh
  git add auditor/registry/repos.json
fi

# Append-only logs: union both sides, dedupe identical lines.
#
# Why findings.jsonl was added 2026-05-01: per-audit sidecars contained
# 2,279 finding entries cumulatively, but only 644 (28%) had reached the
# global log. Investigation traced the gap to the same race that
# previously corrupted the registry: two parallel audits both append
# findings, the loser pulls and runs this resolver, the previous
# `--ours` fallback dropped the remote's appended findings entirely.
# Result: rule-health metrics systematically undercounted by ~3-4×,
# every per-rule precision number was wrong, BUG-missing-frontmatter
# and SEC-curl-pipe-sh false-positive ratios were wildly off.
#
# disagreements.jsonl has the same shape and the same race, so it
# joins the union list defensively rather than waiting for a similar
# investigation to surface a similar gap.
for log in auditor/logs/events.jsonl auditor/findings.jsonl auditor/disagreements.jsonl; do
  if conflicted_paths | grep -qx "$log"; then
    echo "Resolving $log via line union"
    git show ":2:$log" > "$RESOLVE_TMPDIR/log-ours.jsonl"
    git show ":3:$log" > "$RESOLVE_TMPDIR/log-theirs.jsonl"
    cat "$RESOLVE_TMPDIR/log-theirs.jsonl" "$RESOLVE_TMPDIR/log-ours.jsonl" | awk '!seen[$0]++' > "$log"
    git add "$log"
  fi
done

# Exemplar gallery: regenerate from disk. The gallery is deterministic
# from the auditor/exemplars/ directory — running build-exemplar-gallery.py
# after the rebase has staged both sides' new exemplar files produces the
# correct union view. Picking --ours here would silently revert exemplar
# entries from concurrent runs (observed during the 2026-05-13 bulk-seed:
# the gallery committed by the last winning push said "Total exemplars: 8"
# while disk had 61 because each parallel run kept its own snapshot).
if conflicted_paths | grep -qx "auditor/exemplars/README.md"; then
  echo "Resolving auditor/exemplars/README.md via regenerate-from-disk"
  # Accept either side's blob temporarily to clear the conflict, then
  # overwrite with the freshly regenerated gallery.
  git checkout --ours auditor/exemplars/README.md
  python3 auditor/scripts/build-exemplar-gallery.py >/dev/null
  git add auditor/exemplars/README.md
fi

# Everything else: prefer ours so the current workflow's work survives
conflicted_paths | while read -r f; do
  [ -z "$f" ] && continue
  echo "Resolving $f via --ours"
  git checkout --ours "$f"
  git add "$f"
done
