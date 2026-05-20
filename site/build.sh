#!/usr/bin/env bash
# Build nlpm.com.
#
# 1. pnpm install (Vite needs node_modules early).
# 2. Re-generate the reference Markdown from canonical SKILL.md sources.
# 3. Sync case studies from /case-studies/ into site/case-studies/.
# 4. Copy JSON report sidecars from auditor/reports/*.json into
#    site/.vitepress/theme/data/{dashboard.json,reports/*.json}.
# 5. Generate one site/reports/<slug>.md per JSON sidecar; each mounts
#    <RepoReport> with its JSON data inline.
# 6. Vendor Lucide icons + write CNAME into site/public/ — these are
#    the only things in public/ now. The static dashboard.html and the
#    210 per-repo HTML files used to live here too, but VitePress's
#    Vue pages at /dashboard and /reports/<slug> are the canonical
#    online versions.
# 7. Run `pnpm build` (VitePress).
#
# Output: site/.vitepress/dist/
set -euo pipefail

cd "$(dirname "$0")"/..
ROOT=$(pwd)
SITE="$ROOT/site"
PUBLIC="$SITE/public"
SRC_REPORTS="$ROOT/auditor/reports"

echo "==> Installing site dependencies (pnpm)"
# Run install first so any later step that needs node_modules (icon
# vendoring from lucide-static) sees the tree it expects.
( cd "$SITE" && pnpm install --silent )

echo "==> Regenerating reference Markdown"
python3 "$ROOT/bin/nlpm-build-reference-md" --out "$SITE/reference"

echo "==> Syncing case studies into site/case-studies/"
SRC_CASES="$ROOT/case-studies"
DEST_CASES="$SITE/case-studies"
rm -rf "$DEST_CASES"
mkdir -p "$DEST_CASES"
if [ -d "$SRC_CASES" ]; then
  # Copy articles + cover images. Skip nothing — case-studies/ holds only
  # publishable artifacts.
  cp -R "$SRC_CASES"/. "$DEST_CASES/"
  python3 "$ROOT/bin/nlpm-build-case-studies-index" --out "$DEST_CASES"
else
  echo "(no case-studies/ source — skipping)"
fi

echo "==> Resetting site/public/"
# public/ holds only assets the VitePress build can't generate itself:
# CNAME for GitHub Pages and the vendored Lucide icons. The 210 static
# audit HTMLs that used to live here are gone — their content is now
# served via VitePress at /dashboard and /reports/<slug>.
rm -rf "$PUBLIC"
mkdir -p "$PUBLIC"
echo "nlpm.com" > "$PUBLIC/CNAME"

echo "==> Refreshing NLPM self-audit (with vocabulary data)"
# The NLPM self-audit is special: it consumes its own vocabulary
# registry to populate the noun-verb map. Other audited repos get
# vocabulary: null until we add cross-repo registry extraction.
if [ -f "$ROOT/skills/nlpm/vocabulary/registry.yaml" ]; then
  python3 "$ROOT/bin/nlpm-build-vocab-data" \
    --registry "$ROOT/skills/nlpm/vocabulary/registry.yaml" \
    --out /tmp/nlpm-vocab.json >/dev/null
  python3 "$ROOT/auditor/scripts/render-repo-report.py" \
    --repo xiaolai/nlpm-for-claude \
    --vocab-data /tmp/nlpm-vocab.json >/dev/null 2>&1 || \
    echo "  (NLPM self-audit re-render failed; continuing)"
fi

echo "==> Copying JSON report data into site/.vitepress/theme/data/"
# Files in site/public/ are served at runtime but NOT importable as
# modules. To inline the report data into Vue components at build time
# we copy the JSON sidecars to .vitepress/theme/data/ where Vite's
# standard JSON import resolves them.
DATA_DST="$SITE/.vitepress/theme/data"
mkdir -p "$DATA_DST/reports"
rm -f "$DATA_DST"/*.json "$DATA_DST/reports"/*.json 2>/dev/null || true
[ -f "$SRC_REPORTS/dashboard.json" ] && cp "$SRC_REPORTS/dashboard.json" "$DATA_DST/dashboard.json"
find "$SRC_REPORTS" -maxdepth 1 -name '*.json' -not -name 'dashboard.json' \
  -exec cp {} "$DATA_DST/reports/" \; 2>/dev/null || true
echo "  Dashboard JSON: $([ -f "$DATA_DST/dashboard.json" ] && echo yes || echo no)"
echo "  Per-repo JSONs: $(ls "$DATA_DST/reports" 2>/dev/null | wc -l | tr -d ' ')"

echo "==> Generating per-repo VitePress pages from JSON sidecars"
# One site/reports/<slug>.md per JSON, each importing its sidecar +
# mounting <RepoReport>. Source-of-truth stays in auditor/reports/*.json;
# the markdown files are build-time-generated and gitignored.
mkdir -p "$SITE/reports"
find "$SITE/reports" -maxdepth 1 -name '*.md' -delete 2>/dev/null || true
python3 "$ROOT/bin/nlpm-build-site-report-pages" \
  --data-dir "$DATA_DST/reports" \
  --out-dir "$SITE/reports"

echo "==> Vendoring Lucide icons into site/public/icons/"
# MUST run after the public/ wipe above. Pre-color with the brand blue
# so the icons read in both light and dark modes (SVGs loaded via
# <img src=...> can't inherit `currentColor` from the host page).
ICONS_DST="$PUBLIC/icons"
ICONS_SRC="$SITE/node_modules/lucide-static/icons"
mkdir -p "$ICONS_DST"
for icon in bar-chart-3 compass link-2 globe terminal book-open file-terminal; do
  if [ -f "$ICONS_SRC/${icon}.svg" ]; then
    sed 's|stroke="currentColor"|stroke="#3b82f6"|' "$ICONS_SRC/${icon}.svg" > "$ICONS_DST/${icon}.svg"
  else
    echo "::warning::missing icon ${icon}.svg in lucide-static"
  fi
done

# Favicon + site logo: file-terminal is the brand icon for NLPM (an NL
# artifact linter — "code in a document"). Written from the raw Lucide
# source with a black stroke (not the brand blue used by the in-page
# feature icons) so the favicon reads as a flat black-and-white mark in
# the browser tab and OS bookmark UIs.
if [ -f "$ICONS_SRC/file-terminal.svg" ]; then
  sed 's|stroke="currentColor"|stroke="#000"|' "$ICONS_SRC/file-terminal.svg" > "$PUBLIC/favicon.svg"
else
  echo "::warning::missing file-terminal.svg for favicon"
fi

echo "==> Generating site/privacy.md from PRIVACY.md"
# Single source of truth is the repo-root PRIVACY.md. The site copy is
# build-time-generated (gitignored) with VitePress frontmatter prepended.
# Updating PRIVACY.md is the only edit point — never edit site/privacy.md
# directly (it gets overwritten on every build).
PRIVACY_SRC="$ROOT/PRIVACY.md"
if [ -f "$PRIVACY_SRC" ]; then
  {
    printf -- '---\ntitle: Privacy Policy\naside: false\nfooter: false\n---\n\n'
    cat "$PRIVACY_SRC"
  } > "$SITE/privacy.md"
  echo "  wrote $SITE/privacy.md"
else
  echo "::warning::PRIVACY.md not found at $PRIVACY_SRC"
fi

echo "==> Building VitePress"
cd "$SITE"
pnpm build

# Surface the dist path so callers can deploy from it.
echo ""
echo "Built: $SITE/.vitepress/dist"
# `ls | head` trips pipefail on broken-pipe; show the count instead.
echo "dist entries: $(ls "$SITE/.vitepress/dist" | wc -l | tr -d ' ')"
