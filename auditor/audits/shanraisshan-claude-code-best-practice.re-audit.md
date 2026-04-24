# NLPM Re-Audit: shanraisshan/claude-code-best-practice

**Date**: 2026-04-24  |  **Artifacts**: 43  |  **Strategy**: batched
**NL Score**: 87/100
**Bugs**: 10  |  **Quality Issues**: 40

## NL Score Summary

| File | Type | Score | Top Issue |
|------|------|-------|-----------|
| `.claude/agents/weather-agent.md` | agent | 72 | Write/Edit on read-only agent; no examples |
| `.claude/agents/time-agent.md` | agent | 72 | Write/Edit on read-only agent; no examples |
| `.claude/agents/workflows/best-practice/workflow-claude-subagents-agent.md` | agent | 72 | Write/Edit on read-only agent; no examples |
| `.claude/agents/workflows/best-practice/workflow-claude-skills-agent.md` | agent | 72 | Write/Edit on read-only agent; no examples |
| `.claude/agents/workflows/best-practice/workflow-concepts-agent.md` | agent | 72 | Write/Edit on read-only agent; no examples |
| `.claude/agents/workflows/best-practice/workflow-claude-settings-agent.md` | agent | 72 | Write/Edit on read-only agent; no examples |
| `.claude/agents/workflows/best-practice/workflow-claude-commands-agent.md` | agent | 72 | Write/Edit on read-only agent; no examples |
| `.claude/agents/development-workflows-research-agent.md` | agent | 75 | Write/Edit on read-only agent; no examples |
| `development-workflows/rpi/.claude/commands/rpi/implement.md` | command | 77 | No allowed-tools; no empty-input guard; vague terms |
| `development-workflows/rpi/.claude/agents/technical-cto-advisor.md` | agent | 77 | Vague quantifiers (5+); no examples |
| `development-workflows/rpi/.claude/agents/constitutional-validator.md` | agent | 79 | Vague quantifiers (3+); no examples |
| `development-workflows/rpi/.claude/commands/rpi/plan.md` | command | 81 | No allowed-tools; no empty-input guard |
| `development-workflows/rpi/.claude/commands/rpi/research.md` | command | 81 | No allowed-tools; no empty-input guard |
| `.claude/agents/presentation-vibe-coding.md` | agent | 82 | No examples; NotebookEdit unused |
| `.claude/agents/presentation-learning-journey.md` | agent | 82 | No examples; NotebookEdit unused |
| `development-workflows/rpi/.claude/agents/ux-designer.md` | agent | 85 | No examples |
| `development-workflows/rpi/.claude/agents/documentation-analyst-writer.md` | agent | 85 | No examples |
| `development-workflows/rpi/.claude/agents/product-manager.md` | agent | 85 | No examples |
| `development-workflows/rpi/.claude/agents/senior-software-engineer.md` | agent | 85 | No examples |
| `development-workflows/rpi/.claude/agents/code-reviewer.md` | agent | 85 | No examples |
| `agent-teams/.claude/agents/time-agent.md` | agent | 85 | No examples |
| `.claude/skills/time-skill/SKILL.md` | skill | 85 | No examples |
| `.claude/skills/weather-fetcher/SKILL.md` | skill | 85 | No examples |
| `.claude/hooks/config/hooks-config.json` | hook-cfg | 90 | — |
| `.codex/hooks/config/hooks-config.json` | hook-cfg | 90 | — |
| `CLAUDE.md` | project-instruction | 92 | Hook-event count (15 listed) may be stale vs hooks-config.json |
| `.claude/commands/workflows/development-workflows.md` | command | 93 | No allowed-tools; minor vague term |
| `.claude/commands/time-command.md` | command | 95 | No allowed-tools |
| `.claude/commands/workflows/best-practice/workflow-claude-settings.md` | command | 95 | No allowed-tools |
| `.claude/commands/workflows/best-practice/workflow-claude-skills.md` | command | 95 | No allowed-tools |
| `.claude/commands/workflows/best-practice/workflow-claude-commands.md` | command | 95 | No allowed-tools |
| `.claude/commands/workflows/best-practice/workflow-claude-subagents.md` | command | 95 | No allowed-tools |
| `.claude/commands/workflows/best-practice/workflow-concepts.md` | command | 95 | No allowed-tools |
| `agent-teams/.claude/commands/time-orchestrator.md` | command | 95 | No allowed-tools |
| `.claude/skills/weather-svg-creator/SKILL.md` | skill | 95 | Examples only via external reference.md |
| `agent-teams/.claude/skills/time-svg-creator/SKILL.md` | skill | 95 | Examples only via external reference.md |
| `.claude/commands/weather-orchestrator.md` | command | 100 | — |
| `development-workflows/rpi/.claude/agents/requirement-parser.md` | agent | 100 | — |
| `.claude/skills/agent-browser/SKILL.md` | skill | 100 | — |
| `.claude/skills/presentation/vibe-to-agentic-framework/SKILL.md` | skill | 100 | — |
| `.claude/skills/presentation/presentation-styling/SKILL.md` | skill | 100 | — |
| `.claude/skills/presentation/presentation-structure/SKILL.md` | skill | 100 | — |
| `agent-teams/.claude/skills/time-fetcher/SKILL.md` | skill | 100 | — |

## Bugs (PR-worthy)

| # | File | Issue | Impact |
|---|------|-------|--------|
| 1 | `.claude/agents/development-workflows-research-agent.md` | Declares `Write` and `Edit` in `allowedTools` but body explicitly states "Do NOT modify any local files" — read-only intent contradicts tool grants | Agent can write local files despite read-only contract; unexpected side effects if agent is confused |
| 2 | `.claude/agents/weather-agent.md` | Declares `Write` and `Edit` in `allowedTools` but body states "not to write files or create outputs" | Same as above — grants unnecessary file-write capability |
| 3 | `.claude/agents/time-agent.md` | Declares `Write` and `Edit` in `allowedTools`; agent only reads system clock and returns formatted string | Unnecessary write capability on a trivially read-only agent |
| 4 | `.claude/agents/workflows/best-practice/workflow-claude-subagents-agent.md` | Declares `Write`/`Edit` despite "Do NOT modify any files" in body | Contradicts stated read-only contract |
| 5 | `.claude/agents/workflows/best-practice/workflow-claude-skills-agent.md` | Same as #4 | Same |
| 6 | `.claude/agents/workflows/best-practice/workflow-concepts-agent.md` | Same as #4 | Same |
| 7 | `.claude/agents/workflows/best-practice/workflow-claude-settings-agent.md` | Same as #4 | Same |
| 8 | `.claude/agents/workflows/best-practice/workflow-claude-commands-agent.md` | Same as #4 | Same |
| 9 | `.claude/skills/presentation/presentation-structure/SKILL.md` | References `presentation/index.html` as the target file; actual path is `presentation/vibe-coding-to-agentic-engineering/index.html` | Agent loading this skill sees a stale path; may attempt to read/edit the wrong file |
| 10 | `.claude/skills/presentation/presentation-styling/SKILL.md` | References `presentation/index.html` in styling patterns; same stale path | Same impact as #9 |

## Quality Issues (informational)

| # | File | Issue | Penalty |
|---|------|-------|---------|
| 1 | `.claude/agents/development-workflows-research-agent.md` | No example blocks | -15 |
| 2 | `.claude/agents/presentation-vibe-coding.md` | No example blocks; `NotebookEdit` declared but unused for HTML editing | -15, -3 |
| 3 | `.claude/agents/presentation-learning-journey.md` | No example blocks; `NotebookEdit` declared but unused | -15, -3 |
| 4 | `.claude/agents/weather-agent.md` | No example blocks | -15 |
| 5 | `.claude/agents/time-agent.md` | No example blocks | -15 |
| 6 | `.claude/agents/workflows/best-practice/workflow-claude-subagents-agent.md` | No example blocks | -15 |
| 7 | `.claude/agents/workflows/best-practice/workflow-claude-skills-agent.md` | No example blocks | -15 |
| 8 | `.claude/agents/workflows/best-practice/workflow-concepts-agent.md` | No example blocks | -15 |
| 9 | `.claude/agents/workflows/best-practice/workflow-claude-settings-agent.md` | No example blocks | -15 |
| 10 | `.claude/agents/workflows/best-practice/workflow-claude-commands-agent.md` | No example blocks | -15 |
| 11 | `development-workflows/rpi/.claude/agents/ux-designer.md` | No example blocks | -15 |
| 12 | `development-workflows/rpi/.claude/agents/technical-cto-advisor.md` | No example blocks; vague quantifiers: "appropriate" (×4), "properly" (×1), "relevant" (×1) | -15, -12 |
| 13 | `development-workflows/rpi/.claude/agents/documentation-analyst-writer.md` | No example blocks | -15 |
| 14 | `development-workflows/rpi/.claude/agents/product-manager.md` | No example blocks | -15 |
| 15 | `development-workflows/rpi/.claude/agents/senior-software-engineer.md` | No example blocks | -15 |
| 16 | `development-workflows/rpi/.claude/agents/code-reviewer.md` | No example blocks | -15 |
| 17 | `development-workflows/rpi/.claude/agents/constitutional-validator.md` | No example blocks; vague quantifiers: "appropriate" (×2), "relevant" (×1) | -15, -6 |
| 18 | `agent-teams/.claude/agents/time-agent.md` | No example blocks | -15 |
| 19 | `.claude/skills/time-skill/SKILL.md` | No example blocks | -15 |
| 20 | `.claude/skills/weather-fetcher/SKILL.md` | No example blocks | -15 |
| 21 | `.claude/skills/weather-svg-creator/SKILL.md` | Examples deferred to `reference.md`/`examples.md` only; no inline example | -5 |
| 22 | `agent-teams/.claude/skills/time-svg-creator/SKILL.md` | Examples deferred to `reference.md`/`examples.md` only; no inline example | -5 |
| 23 | `.claude/commands/time-command.md` | Missing `allowed-tools` frontmatter | -5 |
| 24 | `.claude/commands/workflows/development-workflows.md` | Missing `allowed-tools`; vague quantifier "appropriate" (×1) | -5, -2 |
| 25 | `.claude/commands/workflows/best-practice/workflow-claude-settings.md` | Missing `allowed-tools` | -5 |
| 26 | `.claude/commands/workflows/best-practice/workflow-claude-skills.md` | Missing `allowed-tools` | -5 |
| 27 | `.claude/commands/workflows/best-practice/workflow-claude-commands.md` | Missing `allowed-tools` | -5 |
| 28 | `.claude/commands/workflows/best-practice/workflow-claude-subagents.md` | Missing `allowed-tools` | -5 |
| 29 | `.claude/commands/workflows/best-practice/workflow-concepts.md` | Missing `allowed-tools` | -5 |
| 30 | `agent-teams/.claude/commands/time-orchestrator.md` | Missing `allowed-tools` (uses Agent and Skill tools) | -5 |
| 31 | `development-workflows/rpi/.claude/commands/rpi/plan.md` | Missing `allowed-tools`; no empty `$ARGUMENTS` guard (no "stop if slug missing" at top); vague: "appropriate" (×1), "relevant" (×1) | -5, -10, -4 |
| 32 | `development-workflows/rpi/.claude/commands/rpi/research.md` | Missing `allowed-tools`; no empty `$ARGUMENTS` guard | -5, -10 |
| 33 | `development-workflows/rpi/.claude/commands/rpi/implement.md` | Missing `allowed-tools`; no empty `$ARGUMENTS` guard; vague: "appropriate" (×2), "relevant" (×1), "properly" (×1) | -5, -10, -8 |

## Cross-Component

1. **Stale file path in presentation skills**: Both `.claude/skills/presentation/presentation-structure/SKILL.md` and `.claude/skills/presentation/presentation-styling/SKILL.md` reference `presentation/index.html`. This path was valid before the presentation was moved; actual paths are `presentation/vibe-coding-to-agentic-engineering/index.html` and `presentation/2026-04-25-gdg-kolachi-cli-claude-code-gemini/index.html`. Agents loading these skills will navigate to a nonexistent file.

2. **Hook-event count drift**: `CLAUDE.md` lists 15 hook events configured in `.claude/settings.json`. The `.claude/hooks/config/hooks-config.json` exposes disable flags for 27+ event types (including `WorktreeCreate`, `WorktreeRemove`, `InstructionsLoaded`, `PostCompact`, `Elicitation`, `ElicitationResult`, `StopFailure`, `CwdChanged`, `FileChanged`, `TaskCreated`, `PermissionDenied` and others not listed in CLAUDE.md). The presentation-vibe-coding agent's Learnings section also canonizes "16 hook events" as the count; both numbers appear stale.

3. **Unverified skill sub-references**: `weather-svg-creator/SKILL.md` and `time-svg-creator/SKILL.md` both refer to sibling files `reference.md` and `examples.md`. `agent-browser/SKILL.md` refers to six files under `references/` and three under `templates/`. These were not audited; broken sub-references would silently degrade those skills at runtime.

4. **Read-only contract propagated inconsistently**: The five `workflow-*-agent.md` files all enforce "Do NOT modify any files" in their bodies yet inherit `Write`/`Edit` from the shared allowedTools template. The corresponding `workflow-*.md` commands correctly describe the workflow as read-then-report but do not override the agents' tool grants.

## Recommendation

The repo demonstrates excellent command orchestration patterns and exemplary skill composition (weather, time, agent-browser, presentation skills all score 100), but the broad copy-paste `allowedTools` template creates a systematic mismatch between declared tool grants and agent intent across eight read-only agents — the single highest-impact fix is stripping `Write`/`Edit` from those eight agent definitions. Addressing the two stale presentation-skill paths and adding at minimum one example block per agent would push the overall score above 92.
