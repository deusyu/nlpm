# NLPM Audit: jordanrendric/claude-video-vision
**Date**: 2026-04-06  |  **Artifacts**: 5  |  **Strategy**: single
**NL Score**: 78/100
**Security**: CLEAR
**Bugs**: 4  |  **Quality Issues**: 8  |  **Security Findings**: 2

## NL Score Summary
| File | Type | Score | Top Issue |
|------|------|-------|-----------|
| commands/setup-video-vision.md | command | 66 | Missing `name` in frontmatter (-25) |
| commands/watch-video.md | command | 58 | Missing `name` in frontmatter + no empty-input handling (-35) |
| .claude-plugin/plugin.json | manifest | 85 | Missing `commands`/`agents` registration + version drift (-15) |
| agents/frame-describer.md | agent | 85 | No example blocks (-15) |
| skills/video-perception/SKILL.md | skill | 94 | Vague quantifiers x3 (-6) |

**Weighted average**: (66 + 58 + 85 + 85 + 94) / 5 = **78/100**

### Score Breakdown

**commands/setup-video-vision.md — 66**
| Penalty | Points |
|---------|--------|
| Missing `name` in frontmatter | -25 |
| No `allowed-tools` declaration (calls video_configure, video_setup, video_watch) | -5 |
| Vague: "brief summary" (line 124) | -2 |
| Vague: "keep it concise" (line 131) | -2 |

**commands/watch-video.md — 58**
| Penalty | Points |
|---------|--------|
| Missing `name` in frontmatter | -25 |
| No `allowed-tools` declaration (calls video_info, video_analyze, video_watch, video_detail, video_setup) | -5 |
| No empty input handling (video path required but no fallback if absent) | -10 |
| Vague: "comprehensive summary" (line 36) | -2 |

**agents/frame-describer.md — 85**
| Penalty | Points |
|---------|--------|
| No example blocks (zero examples) | -15 |

**skills/video-perception/SKILL.md — 94**
| Penalty | Points |
|---------|--------|
| Vague: "relevant" (line 4, line 29) | -2 |
| Vague: "smart" (line 48) | -2 |
| Vague: "brief moments" (line 55) | -2 |

**plugin.json — 85**
| Penalty | Points |
|---------|--------|
| Missing `commands` and `agents` explicit registration fields | -10 |
| Version drift: plugin.json `1.2.0` vs mcp-server/package.json `1.3.1` | -5 |

## Security Scan
| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 0 |
| Medium | 1 |
| Low | 1 |

### Execution Surface Inventory
| Surface | Files |
|---------|-------|
| Hooks | 0 |
| Scripts | 0 |
| MCP configs | `.mcp.json` |
| Package manifests | `mcp-server/package.json` |

### Security Findings
| # | Severity | File | Line | Pattern | Description |
|---|----------|------|------|---------|-------------|
| 1 | Medium | .mcp.json | 4 | SEC-unpinned-remote | `npx -y claude-video-vision@latest` auto-installs and executes the latest npm publish without version pinning; a supply-chain compromise or unreviewed version bump runs immediately on all users |
| 2 | Low | mcp-server/package.json | 27–43 | SEC-unpinned-semver | Four runtime dependencies (`@modelcontextprotocol/sdk`, `zod`, `@google/genai`, `openai`) pinned with `^` semver ranges; downstream builds may silently pick up minor-version changes containing bugs or vulnerabilities |

## Bugs (PR-worthy)
| # | File | Issue | Impact |
|---|------|-------|--------|
| 1 | commands/setup-video-vision.md | Missing `name` field in YAML frontmatter | Command may fail to register in Claude Code; `/setup-video-vision` slash command unavailable |
| 2 | commands/watch-video.md | Missing `name` field in YAML frontmatter | Command may fail to register in Claude Code; `/watch-video` slash command unavailable |
| 3 | commands/setup-video-vision.md | No `allowed-tools` declaration; calls `video_configure`, `video_setup`, `video_watch` without declaring them | Tools may be denied at runtime if the project enforces explicit tool allowlists |
| 4 | commands/watch-video.md | No `allowed-tools` declaration; calls `video_info`, `video_analyze`, `video_watch`, `video_detail`, `video_setup` without declaring them | Same tool-denial risk; also makes auditing and security review harder |

## Security Fixes (PR-worthy, Medium/Low only)
| # | File | Issue | Suggested Fix |
|---|------|-------|---------------|
| 1 | .mcp.json | `@latest` tag causes auto-execution of unreviewed npm versions | Pin to a specific version: `"claude-video-vision@1.3.1"` and update manually after reviewing changelogs |
| 2 | mcp-server/package.json | `^` semver ranges on four runtime deps | Lock to exact versions (`=1.x.y`) in production builds or commit a lockfile; review and update intentionally |

## Quality Issues (informational)
| # | File | Issue | Penalty |
|---|------|-------|---------|
| 1 | agents/frame-describer.md | No example blocks — agent has zero input/output examples | -15 |
| 2 | commands/watch-video.md | No empty-input handling — command requires a video path but gives no instruction for what to do when invoked with no argument | -10 |
| 3 | commands/setup-video-vision.md | Vague: "brief summary" (line 124) — undefined brevity standard | -2 |
| 4 | commands/setup-video-vision.md | Vague: "keep it concise" (line 131) — undefined conciseness standard | -2 |
| 5 | commands/watch-video.md | Vague: "comprehensive summary" (line 36) — undefined comprehensiveness standard | -2 |
| 6 | skills/video-perception/SKILL.md | Vague: "relevant" (lines 4, 29) — which filters are relevant is unspecified; the filter table partially mitigates this | -2 |
| 7 | skills/video-perception/SKILL.md | Vague: "smart" (line 48) — "smart extraction decisions" is undefined; the workflow steps partially mitigate | -2 |
| 8 | skills/video-perception/SKILL.md | Vague: "brief moments" (line 55) — unquantified duration | -2 |

### Additional Quality Notes (no penalty applied)
- `agents/frame-describer.md` declares `tools: Read`. The agent is described as receiving frames as images in the prompt, which does not require `Read`. If the MCP server never passes frame file paths, this tool is unused. Recommend confirming with the implementation and removing if unneeded.

## Cross-Component
| # | Issue |
|---|-------|
| 1 | **Version drift**: `.claude-plugin/plugin.json` declares `"version": "1.2.0"` but `mcp-server/package.json` declares `"version": "1.3.1"`. The manifest version appears stale by one minor bump. |
| 2 | **Missing `commands` field in plugin.json**: The manifest does not declare the two commands (`setup-video-vision`, `watch-video`). If Claude Code requires explicit registration rather than directory auto-discovery, both commands are invisible to the plugin loader. |
| 3 | **Missing `agents` field in plugin.json**: The manifest does not declare `frame-describer`. Same auto-discovery uncertainty as above. |

The skill file (`skills/video-perception/SKILL.md`) correctly matches the MCP tool names (`video_analyze`, `video_watch`, `video_detail`, `video_info`, `video_configure`, `video_setup`) used in the two commands. No broken references between skill and commands.

The `frame-describer` agent is referenced conceptually in `setup-video-vision.md` (Step 3 frame mode section) and in the skill (as the "descriptions" mode sub-agent) but is not wired via any `agents:` or `sub_agents:` field in the calling artifacts. This is consistent with how Claude Code dispatches sub-agents via prompt, so it is not a broken reference — but it does mean the agent is undiscoverable via `plugin.json`.

## Recommendation

CLEAR — submit PRs for all bugs and medium/low security fixes.

Priority order:
1. **Bug #1 and #2** (add `name` to both command frontmatters) — highest impact; these are likely blocking slash command registration.
2. **Bug #3 and #4** (add `allowed-tools` to both commands) — fixes tool-access transparency and satisfies strict allowlist enforcement.
3. **Security Fix #1** (.mcp.json version pinning) — low friction, meaningful supply-chain risk reduction.
4. **Quality #1** (add examples to frame-describer) — improves agent reliability and testability.
5. **Cross-component #1** (sync plugin.json version to 1.3.1) — trivial one-liner.
6. Remaining quality and security-low items can be batched into a single follow-up PR.
