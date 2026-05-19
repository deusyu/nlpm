#!/bin/bash
# Compute fingerprint for a vocab-advisory record.
#
# Vocab advisories cluster terms, not single file:line findings, so the
# fingerprint formula differs from compute-fingerprint.sh: it joins the
# repo, the sorted term set, and the disposition.
#
# Formula: sha256("<repo>|VOCAB|<sorted-csv-terms>|<disposition>\n")
# - empty string for missing disposition
# - terms are joined with "," (commas), no spaces
# - the trailing newline is part of the contract (jq's default output adds \n;
#   shasum folds it into the digest). Python reimplementations MUST include it.
#
# The fingerprint is stable across re-runs of the scanner as long as the
# cluster's term set is unchanged. Adding or removing a term from a cluster
# changes the fingerprint — that is intentional: a different cluster is a
# different advisory.
#
# Usage:
#   source auditor/scripts/compute-vocab-fingerprint.sh
#   FP=$(printf '%s' "$advisory_json" | compute_vocab_fingerprint "<repo>")
#
# Callers:
#   - auditor-vocab-drift.yml aggregate step

compute_vocab_fingerprint() {
  local repo="$1"
  (
    set -o pipefail
    jq -r --arg repo "$repo" \
      '"\($repo)|VOCAB|\([.terms[]] | sort | join(","))|\(.disposition // "")"' \
      | shasum -a 256 | awk '{print "sha256:" $1}'
  )
}
