# NLPM Audit: nexu-io/open-design
**Date**: 2026-05-04  |  **Artifacts**: 63  |  **Strategy**: progressive
**NL Score**: 95/100
**Security**: REVIEW
**Bugs**: 3  |  **Quality Issues**: 28  |  **Security Findings**: 7

## NL Score Summary
| File | Type | Score | Top Issue |
|------|------|-------|-----------|
| CLAUDE.md | skill | 50 | Missing `name` and `description` — just a redirect (`@AGENTS.md`) |
| skills/guizang-ppt/SKILL.md | skill | 85 | `name: magazine-web-ppt` mismatches directory `guizang-ppt` |
| skills/html-ppt-presenter-mode-reveal/SKILL.md | skill | 85 | `name: html-ppt-presenter-mode` mismatches directory name; no output contract |
| skills/editorial-collage/SKILL.md | skill | 90 | Non-standard `inputs:/parameters:` schema; missing `example_prompt` |
| skills/editorial-collage-deck/SKILL.md | skill | 90 | Non-standard schema (`inputs:/parameters:` top-level); no `example_prompt` |
| skills/html-ppt-dir-key-nav-minimal/SKILL.md | skill | 90 | No output contract section; defers entirely to master skill |
| skills/html-ppt-graphify-dark-graph/SKILL.md | skill | 90 | No output contract section |
| skills/html-ppt-hermes-cyber-terminal/SKILL.md | skill | 90 | No output contract section |
| skills/html-ppt-knowledge-arch-blueprint/SKILL.md | skill | 90 | No output contract section |
| skills/html-ppt-obsidian-claude-gradient/SKILL.md | skill | 90 | No output contract section |
| skills/html-ppt-pitch-deck/SKILL.md | skill | 90 | No output contract section |
| skills/html-ppt-product-launch/SKILL.md | skill | 90 | No output contract section |
| skills/html-ppt-taste-brutalist/SKILL.md | skill | 90 | No `triggers`, no `od:` block, no output contract |
| skills/html-ppt-taste-editorial/SKILL.md | skill | 90 | No `triggers`, no `od:` block, no output contract |
| skills/html-ppt-tech-sharing/SKILL.md | skill | 90 | No output contract section |
| skills/html-ppt-testing-safety-alert/SKILL.md | skill | 90 | No output contract section |
| skills/html-ppt-weekly-report/SKILL.md | skill | 90 | No output contract section |
| skills/html-ppt-xhs-pastel-card/SKILL.md | skill | 90 | No output contract section |
| skills/html-ppt-xhs-post/SKILL.md | skill | 90 | No output contract section |
| skills/html-ppt-xhs-white-editorial/SKILL.md | skill | 90 | No output contract section |
| skills/html-ppt-course-module/SKILL.md | skill | 90 | No output contract section |
| skills/pptx-html-fidelity-audit/SKILL.md | skill | 90 | `od: mode: utility` with minimal metadata; output only partially specified |
| skills/replit-deck/SKILL.md | skill | 90 | No `example_prompt`; output contract not in observed content |
| skills/simple-deck/SKILL.md | skill | 90 | No `example_prompt`; output contract not confirmed in read window |
| skills/web-prototype-taste-brutalist/SKILL.md | skill | 90 | No `triggers`, no `od:` block, no output contract |
| skills/web-prototype-taste-editorial/SKILL.md | skill | 90 | No `triggers`, no `od:` block, no output contract |
| skills/web-prototype-taste-soft/SKILL.md | skill | 90 | No `triggers`, no `od:` block, no output contract |
| skills/critique/SKILL.md | skill | 95 | Excellent structure; minor: example_prompt in body rather than frontmatter |
| skills/html-ppt/SKILL.md | skill | 95 | Master skill, comprehensive; `example_prompt` in frontmatter ✓ |
| skills/hyperframes/SKILL.md | skill | 95 | Comprehensive; complex OD-integration path well-documented |
| skills/hatch-pet/SKILL.md | skill | 98 | Vague quantifier: "choose a short **appropriate** name" |
| skills/tweaks/SKILL.md | skill | 98 | Vague quantifier: "keep only the knobs you decided are **relevant** to this artifact" |
| docs/examples/saas-landing-skill/SKILL.md | skill | 100 | Reference example; complete and canonical |
| skills/audio-jingle/SKILL.md | skill | 100 | — |
| skills/blog-post/SKILL.md | skill | 100 | — |
| skills/dashboard/SKILL.md | skill | 100 | — |
| skills/dating-web/SKILL.md | skill | 100 | — |
| skills/design-brief/SKILL.md | skill | 100 | — |
| skills/digital-eguide/SKILL.md | skill | 100 | — |
| skills/docs-page/SKILL.md | skill | 100 | — |
| skills/email-marketing/SKILL.md | skill | 100 | — |
| skills/eng-runbook/SKILL.md | skill | 100 | — |
| skills/finance-report/SKILL.md | skill | 100 | — |
| skills/gamified-app/SKILL.md | skill | 100 | — |
| skills/hr-onboarding/SKILL.md | skill | 100 | — |
| skills/image-poster/SKILL.md | skill | 100 | — |
| skills/invoice/SKILL.md | skill | 100 | — |
| skills/kanban-board/SKILL.md | skill | 100 | — |
| skills/magazine-poster/SKILL.md | skill | 100 | — |
| skills/meeting-notes/SKILL.md | skill | 100 | — |
| skills/mobile-app/SKILL.md | skill | 100 | — |
| skills/mobile-onboarding/SKILL.md | skill | 100 | — |
| skills/motion-frames/SKILL.md | skill | 100 | — |
| skills/pm-spec/SKILL.md | skill | 100 | — |
| skills/pricing-page/SKILL.md | skill | 100 | — |
| skills/saas-landing/SKILL.md | skill | 100 | — |
| skills/social-carousel/SKILL.md | skill | 100 | — |
| skills/sprite-animation/SKILL.md | skill | 100 | — |
| skills/team-okrs/SKILL.md | skill | 100 | — |
| skills/video-shortform/SKILL.md | skill | 100 | — |
| skills/web-prototype/SKILL.md | skill | 100 | — |
| skills/weekly-update/SKILL.md | skill | 100 | — |
| skills/wireframe-sketch/SKILL.md | skill | 100 | — |

## Security Scan
| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 2 (1 false positive) |
| Medium | 2 |
| Low | 3 |

### Execution Surface Inventory
| Surface | Files |
|---------|-------|
| Hooks | 0 |
| Scripts | 14 files in `scripts/` (`*.mjs`, `*.ts`, `*.json`) |
| MCP configs | 0 (no `.mcp.json`) |
| Package manifests | `package.json` (has `postinstall` script) |

### Security Findings
| # | Severity | File | Line | Pattern | Description |
|---|----------|------|------|---------|-------------|
| 1 | HIGH | scripts/sync-hyperframes-skill.mjs | 60 | SEC-npx-remote-exec | `npx -y skills add heygen-com/hyperframes` downloads and executes a third-party npm package at runtime with auto-confirmation (`-y`). No pinned version; depends on npm registry integrity. |
| 2 | HIGH (fp) | package.json | 13 | SEC-postinstall-script | `postinstall` script runs `node ./scripts/postinstall.mjs` on every `npm/pnpm install`. Internally audited: only invokes `pnpm build` for workspace packages; no network calls or credential access. **False positive** — standard monorepo build automation. |
| 3 | MEDIUM | scripts/sync-community-pets.ts | null | SEC-external-binary-fetch | Downloads binary spritesheet files from `https://j20.nz/hatchery/api/pets.json` and associated URLs. Validates magic bytes (webp/png/gif) before writing. External domain not under repo owner's control. |
| 4 | MEDIUM | scripts/bake-community-pets.ts | null | SEC-external-api-fetch | Fetches pet data from `https://ihzwckyzfcuktrljwpha.supabase.co/functions/v1/petshare`. Validates binary format before writing. Supabase project ID is hardcoded; if project is compromised, malicious data could be injected. |
| 5 | LOW | scripts/import-prompt-templates.mjs | null | SEC-network-fetch | Fetches markdown from two raw.githubusercontent.com paths (YouMind-OpenLab repos) and writes parsed JSON. Trusts GitHub CDN integrity. |
| 6 | LOW | scripts/sync-litellm-models.ts | null | SEC-network-fetch | Fetches `model_prices_and_context_window.json` from BerriAI/litellm raw GitHub. Writes to `apps/web/src/state/litellm-models.json`. GitHub CDN dependency; no pinning. |
| 7 | LOW | scripts/sync-hyperframes-skill.mjs | null | SEC-env-var-write-path | Respects `OD_KEEP_HF_SYNC_TMP` env var to skip temp-dir cleanup; temp directory under `os.tmpdir()` is predictable. Combined with finding #1, could expose intermediate skill content. |

## Bugs (PR-worthy)
| # | File | Issue | Impact |
|---|------|-------|--------|
| 1 | skills/html-ppt-presenter-mode-reveal/SKILL.md | `name: html-ppt-presenter-mode` mismatches directory `html-ppt-presenter-mode-reveal`; skill registered as wrong name | Gallery links using directory path will fail to resolve skill by name; users invoking `html-ppt-presenter-mode-reveal` won't match |
| 2 | skills/guizang-ppt/SKILL.md | `name: magazine-web-ppt` mismatches directory `guizang-ppt`; directory and registered name are inconsistent | Plugin install and direct invocation by directory path diverge from trigger registration |
| 3 | CLAUDE.md | File is `@AGENTS.md` — a bare redirect with no YAML frontmatter, no `name`, no `description` | Cannot be registered as a skill; confuses discovery tooling that scans for SKILL.md-style documents |

## Security Fixes (PR-worthy, Medium/Low only)
| # | File | Issue | Suggested Fix |
|---|------|-------|---------------|
| 1 | scripts/sync-community-pets.ts | Binary downloads from `j20.nz` (external, unversioned) with no checksum verification beyond magic-byte sniff | Add SHA-256 checksum verification against a manifest signed by the pet author; or move asset hosting to repo-controlled CDN |
| 2 | scripts/bake-community-pets.ts | Hardcoded Supabase project ID in source; if project is transferred or compromised, fetched data changes silently | Store the Supabase URL in a config file or env var; add a content-hash check on the response |
| 3 | scripts/import-prompt-templates.mjs | Fetches raw markdown from GitHub CDN at unpinned HEAD | Pin to a specific commit SHA in the URL instead of `main` to prevent silent upstream changes |
| 4 | scripts/sync-litellm-models.ts | Fetches JSON from BerriAI/litellm at unpinned HEAD | Pin to tagged release URL |

## Quality Issues (informational)
| # | File | Issue | Penalty |
|---|------|-------|---------|
| 1 | CLAUDE.md | Redirect file (`@AGENTS.md`) — no skill content, no frontmatter | -50 (missing name −25, missing description −25) |
| 2 | skills/html-ppt-taste-editorial/SKILL.md | No `triggers`, no `od:` block, no output contract section | -10 |
| 3 | skills/html-ppt-taste-brutalist/SKILL.md | No `triggers`, no `od:` block, no output contract section | -10 |
| 4 | skills/web-prototype-taste-brutalist/SKILL.md | No `triggers`, no `od:` block, no output contract section | -10 |
| 5 | skills/web-prototype-taste-editorial/SKILL.md | No `triggers`, no `od:` block, no output contract section | -10 |
| 6 | skills/web-prototype-taste-soft/SKILL.md | No `triggers`, no `od:` block, no output contract section | -10 |
| 7–21 | 15× html-ppt subskills (dir-key-nav-minimal, xhs-post, knowledge-arch-blueprint, tech-sharing, product-launch, graphify-dark-graph, obsidian-claude-gradient, xhs-white-editorial, pitch-deck, testing-safety-alert, course-module, weekly-report, xhs-pastel-card, hermes-cyber-terminal, presenter-mode-reveal) | No output contract section; authoring defers entirely to master skill | -10 each |
| 22 | skills/editorial-collage/SKILL.md | Non-standard top-level `inputs:/parameters:` schema; missing `example_prompt` | -10 |
| 23 | skills/editorial-collage-deck/SKILL.md | Non-standard top-level `inputs:/parameters:` schema structure | -10 |
| 24 | skills/pptx-html-fidelity-audit/SKILL.md | `od: mode: utility` only; minimal metadata; output contract not in primary file section | -10 |
| 25 | skills/replit-deck/SKILL.md | No `example_prompt`; output contract not confirmed in read window (234-line file) | -10 |
| 26 | skills/simple-deck/SKILL.md | No `example_prompt`; output contract not confirmed in read window | -10 |
| 27 | skills/hatch-pet/SKILL.md | Vague quantifier: "choose a short **appropriate** name" — "appropriate" is underspecified | -2 |
| 28 | skills/tweaks/SKILL.md | Vague quantifier: "keep only the knobs you decided are **relevant** to this artifact" — "relevant" is underspecified | -2 |

## Cross-Component

**Duplicate skill content:** `docs/examples/saas-landing-skill/SKILL.md` and `skills/saas-landing/SKILL.md` are near-identical. The production version correctly adds `craft: requires: [typography, color, anti-ai-slop]`. The example version omits `craft:` and includes a "For skill authors reading this" section that belongs only in docs. These are intentionally separate (reference vs. production) but risk diverging silently.

**Name/directory mismatches (2):** `skills/html-ppt-presenter-mode-reveal/SKILL.md` (name: `html-ppt-presenter-mode`) and `skills/guizang-ppt/SKILL.md` (name: `magazine-web-ppt`). If the Skills registry resolves by `name` field, these will be reachable by the wrong identifier and invisible by directory name. See Bugs #1 and #2.

**Taste skills lack triggers/od:** Five style-reference skills (`html-ppt-taste-editorial`, `html-ppt-taste-brutalist`, `web-prototype-taste-brutalist`, `web-prototype-taste-editorial`, `web-prototype-taste-soft`) define visual constraints without `triggers` or `od:` blocks. They function as reference documents loaded by other skills rather than standalone invokeables, but this is never stated explicitly in the files.

**`editorial-collage-deck` references `../editorial-collage/styles.css` at compile time:** The deck composer reads the sister skill's stylesheet. If `editorial-collage` is moved or renamed, the deck skill's compose step silently breaks with no skill-level indication. Verified: `schema.ts` files exist in both directories.

**`sync-hyperframes-skill.mjs` vendors a third-party skill at runtime:** This script is designed to pull `heygen-com/hyperframes` from npm on demand. The vendored `skills/hyperframes/SKILL.md` is the result of a previous sync. If the npm package diverges from the vendored copy, users get inconsistent skill behavior depending on whether they run the sync script.

## Recommendation
REVIEW — Submit NL fix PRs for Bugs #1–#3 (name mismatches and CLAUDE.md). Flag finding #1 (`npx -y` runtime execution in `sync-hyperframes-skill.mjs`) privately or in a dedicated security issue before any contribution that touches the scripts directory. Medium/Low security fixes (findings #3–#7) are safe to include in regular PRs.
