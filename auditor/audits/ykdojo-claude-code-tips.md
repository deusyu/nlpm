# NLPM Audit: ykdojo/claude-code-tips
**Date**: 2026-04-17  |  **Artifacts**: 9  |  **Strategy**: single
**NL Score**: 94/100
**Security**: REVIEW
**Bugs**: 1  |  **Quality Issues**: 8  |  **Security Findings**: 5

## NL Score Summary
| File | Type | Score | Top Issue |
|------|------|-------|-----------|
| `.claude/commands/upgrade-patches.md` | Command | 70 | Missing `name` frontmatter (-25), no allowed-tools (-5) |
| `skills/reddit-fetch/SKILL.md` | Skill | 86 | No output format section (-10), vague quantifiers (-4) |
| `skills/gha/SKILL.md` | Skill | 98 | "relevant error messages" vague quantifier (-2) |
| `skills/review-claudemd/SKILL.md` | Skill | 98 | "seems outdated or unnecessary" vague (-2) |
| `CLAUDE.md` | Project instructions | 98 | "etc." vague quantifier (-2) |
| `.claude-plugin/plugin.json` | Plugin manifest | 100 | — |
| `skills/clone/SKILL.md` | Skill | 100 | — |
| `skills/half-clone/SKILL.md` | Skill | 100 | — |
| `skills/handoff/SKILL.md` | Skill | 100 | — |

## Security Scan
| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 1 |
| Medium | 3 |
| Low | 1 |

### Execution Surface Inventory
| Surface | Files |
|---------|-------|
| Hooks | 0 (check-context.sh and context-bar.sh are hook-ready scripts, not installed hooks) |
| Scripts | 8 (`scripts/check-context.sh`, `scripts/clone-conversation.sh`, `scripts/color-preview.sh`, `scripts/context-bar.sh`, `scripts/half-clone-conversation.sh`, `scripts/setup.sh`, `scripts/test-half-clone.sh`, `scripts/generate-toc.js`) |
| MCP configs | 0 |
| Package manifests | 0 (no package.json / requirements.txt) |

### Security Findings
| # | Severity | File | Line | Pattern | Description |
|---|----------|------|------|---------|-------------|
| 1 | HIGH | scripts/setup.sh | 139 | sudo usage | `sudo npm install -g cc-safe` runs npm with root privileges as a fallback with no explicit user warning before sudo elevation |
| 2 | MEDIUM | scripts/setup.sh | 158 | Network download of executable | Downloads `context-bar.sh` from `raw.githubusercontent.com/…/main` (unpinned branch, no checksum) then `chmod +x` and installs as a Claude status-line hook |
| 3 | MEDIUM | scripts/setup.sh | 137 | Runtime package install | `npm install -g cc-safe` with no version pin or `--ignore-scripts` flag; postinstall scripts run as the current user |
| 4 | MEDIUM | scripts/setup.sh | 247 | File write outside repo | Appends aliases and a shell function to `~/.zshrc` / `~/.bashrc` without creating a backup |
| 5 | LOW | scripts/setup.sh | 9 | Unpinned upstream reference | `REPO_URL` targets the `main` branch; any future commit to the upstream repo is immediately picked up by fresh installs |

## Bugs (PR-worthy)
| # | File | Issue | Impact |
|---|------|-------|--------|
| 1 | `.claude/commands/upgrade-patches.md` | Missing `name` field in frontmatter (only `description` present) | Command may not register correctly under plugin discovery; `-25` score penalty |

## Security Fixes (PR-worthy, Medium/Low only)
| # | File | Issue | Suggested Fix |
|---|------|-------|---------------|
| 1 | scripts/setup.sh | MEDIUM (line 158): Downloads shell script from `main` branch with no integrity check | Pin `REPO_URL` to a specific git tag or commit SHA; verify SHA-256 after download before `chmod +x` |
| 2 | scripts/setup.sh | MEDIUM (line 137): `npm install -g cc-safe` unpinned with no `--ignore-scripts` | Pin to a specific version (e.g., `cc-safe@X.Y.Z`) and add `--ignore-scripts` to suppress postinstall execution |
| 3 | scripts/setup.sh | MEDIUM (line 247): Modifies shell config without backup | Create a timestamped backup (`cp "$SHELL_RC" "${SHELL_RC}.bak.$(date +%s)"`) before appending |
| 4 | scripts/setup.sh | LOW (line 9): `REPO_URL` pinned to `main` | Use a versioned tag URL (e.g., `.../refs/tags/v0.25.1/…`) instead of `main` |

*Finding #1 (HIGH — sudo) requires private disclosure, not a public PR.*

## Quality Issues (informational)
| # | File | Issue | Penalty |
|---|------|-------|---------|
| 1 | `.claude/commands/upgrade-patches.md` | No `allowed-tools` declared | -5 |
| 2 | `.claude/commands/upgrade-patches.md` | Hardcoded absolute path `/Users/yk/Desktop/projects/safeclaw` — non-portable, breaks for any other user | informational |
| 3 | `skills/reddit-fetch/SKILL.md` | No output format section; skill teaches fetching but does not specify what the invoking agent should return to the user | -10 |
| 4 | `skills/reddit-fetch/SKILL.md` | "adjust as needed" — vague quantifier in sleep comment | -2 |
| 5 | `skills/reddit-fetch/SKILL.md` | "complex searches" — vague quantifier | -2 |
| 6 | `skills/gha/SKILL.md` | "relevant error messages or file names" — vague quantifier in step 5 | -2 |
| 7 | `skills/review-claudemd/SKILL.md` | "seems outdated or unnecessary" — vague phrasing in analysis prompt template | -2 |
| 8 | `CLAUDE.md` | "etc." in "skills, plugin.json, etc." — vague enumeration | -2 |

## Cross-Component
- **References resolve**: `skills/clone/SKILL.md` → `scripts/clone-conversation.sh` ✓; `skills/half-clone/SKILL.md` → `scripts/half-clone-conversation.sh` + `--preview` flag ✓; `CLAUDE.md` → `scripts/generate-toc.js` ✓
- **marketplace.json**: `CLAUDE.md` instructs bumping `.claude-plugin/marketplace.json` alongside `plugin.json` on every plugin release, but `marketplace.json` was not present in the scanned artifact list — confirm it exists and is kept in sync.
- **upgrade-patches.md path**: The command hardcodes `/Users/yk/Desktop/projects/safeclaw` as the container host path. This is developer-specific and will silently fail for any other user. The command should either document this prerequisite in a `prerequisites:` frontmatter field or parametrize the path.
- **No circular references or contradictions detected** across the 9 scored artifacts.

## Recommendation
REVIEW — submit NL fix PRs (missing `name` frontmatter on `upgrade-patches.md`, output format on `reddit-fetch`, vague quantifier cleanups), and submit security fix PRs for the three MEDIUM findings and the one LOW finding. File a **private security report** for the HIGH finding (unconditional `sudo` escalation in `setup.sh:139`) rather than a public PR.
