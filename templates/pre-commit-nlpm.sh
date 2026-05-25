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
    # Try common locations (sorted descending lexically so newest cache version wins)
    REPO_BIN="$(git rev-parse --show-toplevel 2>/dev/null)/bin/nlpm-check"
    LATEST_CACHE_BIN=""
    if [[ -d "$HOME/.claude/plugins/cache/xiaolai/nlpm" ]]; then
        # Pick newest installed version. Use Python (which the binary
        # already requires) for portable semver comparison — `sort -V`
        # is GNU-coreutils-specific and not on BSD/macOS by default.
        LATEST_VERSION=$(python3 - <<'PY' 2>/dev/null
import os, re
base = os.path.expanduser("~/.claude/plugins/cache/xiaolai/nlpm")
try:
    versions = [d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))]
except OSError:
    raise SystemExit
def key(v):
    return tuple(int(p) if p.isdigit() else 0 for p in re.split(r"[.\-]", v))
versions.sort(key=key)
if versions:
    print(versions[-1])
PY
)
        if [[ -n "$LATEST_VERSION" ]]; then
            LATEST_CACHE_BIN="$HOME/.claude/plugins/cache/xiaolai/nlpm/$LATEST_VERSION/bin/nlpm-check"
        fi
    fi
    for candidate in "$REPO_BIN" "$HOME/.local/bin/nlpm-check" "$LATEST_CACHE_BIN"; do
        if [[ -n "$candidate" && -x "$candidate" ]]; then
            NLPM_CHECK_BIN="$candidate"
            break
        fi
    done
fi

if ! command -v "$NLPM_CHECK_BIN" >/dev/null 2>&1 && [[ ! -x "$NLPM_CHECK_BIN" ]]; then
    echo "pre-commit-nlpm: nlpm-check not found on PATH" >&2
    echo "  install: https://github.com/xiaolai/nlpm#install-the-binary" >&2
    echo "  or set NLPM_CHECK_BIN=/path/to/nlpm-check" >&2
    exit 1
fi

# Only run if the commit touches plugin artifacts.
# Bash case-pattern `*` matches across slashes, so the patterns below
# also cover nested layouts (e.g. multi-plugin monorepos with
# plugins/<sub>/agents/foo.md). nlpm-check itself walks the tree and
# auto-detects multi-plugin layouts (v0.8.5+).
STAGED=$(git diff --cached --name-only --diff-filter=ACMR)
RELEVANT=0
while IFS= read -r file; do
    case "$file" in
        *.claude-plugin/plugin.json|*.claude-plugin/marketplace.json) RELEVANT=1 ;;
        *skills/*SKILL.md) RELEVANT=1 ;;
        *agents/*.md) RELEVANT=1 ;;
        *commands/*.md) RELEVANT=1 ;;
        *hooks/hooks.json|*hooks.json|*.mcp.json) RELEVANT=1 ;;
    esac
done <<< "$STAGED"

if [[ "$RELEVANT" -eq 0 ]]; then
    exit 0
fi

# Run the check against a snapshot of the staged content (the exact
# bytes that would land in the commit), not the working tree. The
# working tree can include unstaged edits that mask staged regressions.
STAGE_DIR=$(mktemp -d)
trap 'rm -rf "$STAGE_DIR"' EXIT
git checkout-index --prefix="$STAGE_DIR/" -a 2>/dev/null || {
    # Fall back to working-tree check if checkout-index fails (older git,
    # detached scenarios, etc.). Document the fallback.
    echo "pre-commit-nlpm: warning — could not snapshot index, checking working tree" >&2
    "$NLPM_CHECK_BIN" .
    exit $?
}
"$NLPM_CHECK_BIN" "$STAGE_DIR"
