#!/usr/bin/env bash
# Pre-commit hook for Claude Code plugin authors.
#
# Runs nlpm-check (the deterministic NLPM validator) against staged changes
# and blocks the commit on high-confidence findings.
#
# Installation:
#   1. Place this file at .git/hooks/pre-commit in your plugin repo
#   2. chmod +x .git/hooks/pre-commit
#   3. Place nlpm-check on PATH, OR set NLPM_CHECK_BIN below to its path
#
# To bypass (not recommended): git commit --no-verify

set -euo pipefail

# Locate nlpm-check
NLPM_CHECK_BIN="${NLPM_CHECK_BIN:-nlpm-check}"
if ! command -v "$NLPM_CHECK_BIN" >/dev/null 2>&1; then
    # Try common locations
    for candidate in \
        "$(git rev-parse --show-toplevel 2>/dev/null)/bin/nlpm-check" \
        "$HOME/.local/bin/nlpm-check" \
        "$HOME/.claude/plugins/cache/xiaolai/nlpm/0.8.0/bin/nlpm-check"
    do
        if [[ -x "$candidate" ]]; then
            NLPM_CHECK_BIN="$candidate"
            break
        fi
    done
fi

if ! command -v "$NLPM_CHECK_BIN" >/dev/null 2>&1 && [[ ! -x "$NLPM_CHECK_BIN" ]]; then
    echo "pre-commit-nlpm: nlpm-check not found on PATH" >&2
    echo "  install: https://github.com/xiaolai/nlpm-for-claude#install-the-binary" >&2
    echo "  or set NLPM_CHECK_BIN=/path/to/nlpm-check" >&2
    exit 1
fi

# Only run if the commit touches plugin artifacts
STAGED=$(git diff --cached --name-only --diff-filter=ACMR)
RELEVANT=0
while IFS= read -r file; do
    case "$file" in
        .claude-plugin/plugin.json|.claude-plugin/marketplace.json) RELEVANT=1 ;;
        skills/*/SKILL.md|.claude/skills/*/SKILL.md) RELEVANT=1 ;;
        agents/*.md|.claude/agents/*.md) RELEVANT=1 ;;
        commands/*.md|.claude/commands/*.md|commands/**/*.md|.claude/commands/**/*.md) RELEVANT=1 ;;
        hooks/hooks.json|.claude/hooks.json) RELEVANT=1 ;;
    esac
done <<< "$STAGED"

if [[ "$RELEVANT" -eq 0 ]]; then
    exit 0
fi

# Run the check against the working tree (not the staged content).
# Authors typically run `git add` after editing, so the working tree
# reflects the commit content. For stricter staged-content validation,
# see `templates/workflows/nlpm-check.yml` which runs in CI.
"$NLPM_CHECK_BIN" .
