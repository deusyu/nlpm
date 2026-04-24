# Re-Audit: shanraisshan/claude-code-best-practice

**Date**: 2026-04-24  |  **Before**: `unknown` (88/100)  |  **After**: `13cbf08` (87/100)

## Summary

| Outcome | Count |
|---------|------:|
| fixed — upstream, not via our PR | 27 |
| newly introduced (regressions) | 57 |

## Original findings — verification

| # | File | Line | Rule | Pattern | Outcome | PR |
|---|------|------|------|---------|---------|----|
| 1 | `agent-teams/.claude/commands/time-orchestrator.md` | — | BUG-missing-frontmatter | `missing-description` | fixed — upstream, not via our PR |  |
| 2 | `.claude/agents/development-workflows-research-agent.md` | — | CC-name-collision | `name-collision` | fixed — upstream, not via our PR |  |
| 3 | `.claude/agents/workflows/development-workflows-research-agent.md` | — | CC-name-collision | `name-collision` | fixed — upstream, not via our PR |  |
| 4 | `.claude/agents/time-agent.md` | — | BUG-unclassified | `both-declare-name-time-agent-with-differ` | fixed — upstream, not via our PR |  |
| 5 | `agent-teams/.claude/agents/time-agent.md` | — | BUG-unclassified | `both-declare-name-time-agent-with-differ` | fixed — upstream, not via our PR |  |
| 6 | `.mcp.json` | — | SEC-unknown | `npx-y-playwright-mcp-no-version-pin` | fixed — upstream, not via our PR |  |
| 7 | `.mcp.json` | — | SEC-unknown | `npx-y-deepwiki-mcp-unknown-package-no-pi` | fixed — upstream, not via our PR |  |
| 8 | `.claude/hooks/scripts/hooks.py` | — | SEC-unknown | `subprocess-popen-resolves-audio-player-f` | fixed — upstream, not via our PR |  |
| 9 | `.claude/hooks/scripts/hooks.py` | — | SEC-unknown | `hook-log-may-persist-sensitive-tool-inpu` | fixed — upstream, not via our PR |  |
| 10 | `All 20 agents` | — | R09 | `no-examples` | fixed — upstream, not via our PR |  |
| 11 | `.claude/agents/development-workflows-research-agent.md` | — | BUG-read-only-write | `write-edit-on-readonly` | fixed — upstream, not via our PR |  |
| 12 | `.claude/agents/weather-agent.md` | — | UNCLASSIFIED | `body-says-not-to-write-files-or-create-o` | fixed — upstream, not via our PR |  |
| 13 | `.claude/agents/time-agent.md` | — | UNCLASSIFIED | `single-purpose-time-agent-runs-one-bash` | fixed — upstream, not via our PR |  |
| 14 | `workflows/best-practice/*-agent.md` | — | UNCLASSIFIED | `all-five-workflow-research-agents-declar` | fixed — upstream, not via our PR |  |
| 15 | `.claude/agents/presentation-vibe-coding.md` | — | BUG-unused-tool | `unused-tools` | fixed — upstream, not via our PR |  |
| 16 | `.claude/agents/presentation-learning-journey.md` | — | BUG-unused-tool | `unused-tools` | fixed — upstream, not via our PR |  |
| 17 | `agent-teams/.claude/commands/time-orchestrator.md` | — | BUG-undeclared-tool | `missing-allowed-tools` | fixed — upstream, not via our PR |  |
| 18 | `All 8 standalone commands` | — | BUG-undeclared-tool | `missing-allowed-tools` | fixed — upstream, not via our PR |  |
| 19 | `development-workflows/rpi/.claude/commands/rpi/plan.md` | — | R01 | `vague-quantifiers` | fixed — upstream, not via our PR |  |
| 20 | `development-workflows/rpi/.claude/commands/rpi/research.md` | — | R01 | `vague-quantifiers` | fixed — upstream, not via our PR |  |
| 21 | `development-workflows/rpi/.claude/commands/rpi/implement.md` | — | R01 | `vague-quantifiers` | fixed — upstream, not via our PR |  |
| 22 | `development-workflows/rpi/.claude/agents/requirement-parser.md` | — | R01 | `vague-quantifiers` | fixed — upstream, not via our PR |  |
| 23 | `development-workflows/rpi/.claude/agents/technical-cto-advisor.md` | — | R01 | `vague-quantifiers` | fixed — upstream, not via our PR |  |
| 24 | `development-workflows/rpi/.claude/agents/constitutional-validator.md` | — | R01 | `vague-quantifiers` | fixed — upstream, not via our PR |  |
| 25 | `development-workflows/rpi/.claude/agents/documentation-analyst-writer.md` | — | R01 | `vague-quantifiers` | fixed — upstream, not via our PR |  |
| 26 | `development-workflows/rpi/.claude/agents/*.md` | — | UNCLASSIFIED | `no-allowedtools-in-frontmatter-tools-ava` | fixed — upstream, not via our PR |  |
| 27 | `Repo-wide agents` | — | UNCLASSIFIED | `inconsistent-frontmatter-format-root-sco` | fixed — upstream, not via our PR |  |

## Findings introduced since audit

These findings appear in the re-audit but were not in the original audit. They may be true regressions (new commits introduced them) or artifacts of scoring drift.

| # | File | Line | Rule | Pattern | Description |
|---|------|------|------|---------|-------------|
| 1 | `.claude/agents/development-workflows-research-agent.md` | — | BUG-undeclared-tool | `write-edit-on-read-only-agent` | Agent declares Write and Edit in allowedTools but body states 'Do NOT modify any local files' — read-only contract contradicts tool grants |
| 2 | `.claude/agents/weather-agent.md` | — | BUG-undeclared-tool | `write-edit-on-read-only-agent` | Agent declares Write and Edit in allowedTools but body states 'not to write files or create outputs' — read-only intent contradicts tool grants |
| 3 | `.claude/agents/time-agent.md` | — | BUG-undeclared-tool | `write-edit-on-read-only-agent` | Root-scope time-agent declares Write and Edit in allowedTools but only runs a bash date command and returns a formatted string — no file writes possible or intended |
| 4 | `.claude/agents/workflows/best-practice/workflow-claude-subagents-agent.md` | — | BUG-undeclared-tool | `write-edit-on-read-only-agent` | Agent declares Write and Edit in allowedTools but body states 'Do NOT modify any files' — read-only research intent contradicts tool grants |
| 5 | `.claude/agents/workflows/best-practice/workflow-claude-skills-agent.md` | — | BUG-undeclared-tool | `write-edit-on-read-only-agent` | Agent declares Write and Edit in allowedTools but body states 'Do NOT modify any files' |
| 6 | `.claude/agents/workflows/best-practice/workflow-concepts-agent.md` | — | BUG-undeclared-tool | `write-edit-on-read-only-agent` | Agent declares Write and Edit in allowedTools but body states 'Do NOT take any actions or modify files' |
| 7 | `.claude/agents/workflows/best-practice/workflow-claude-settings-agent.md` | — | BUG-undeclared-tool | `write-edit-on-read-only-agent` | Agent declares Write and Edit in allowedTools but body states 'Do NOT modify any files' |
| 8 | `.claude/agents/workflows/best-practice/workflow-claude-commands-agent.md` | — | BUG-undeclared-tool | `write-edit-on-read-only-agent` | Agent declares Write and Edit in allowedTools but body states 'Do NOT modify any files' |
| 9 | `.claude/skills/presentation/presentation-structure/SKILL.md` | 7 | CC-broken-relative-path | `stale-file-path` | Skill references 'presentation/index.html' as the target file but that path does not exist; actual path is presentation/vibe-coding-to-agentic-engineering/index.html |
| 10 | `.claude/skills/presentation/presentation-styling/SKILL.md` | 8 | CC-broken-relative-path | `stale-file-path` | Skill references 'presentation/index.html' as the target file but that path does not exist; actual path is presentation/vibe-coding-to-agentic-engineering/index.html |
| 11 | `.claude/agents/development-workflows-research-agent.md` | — | R05 | `missing-examples` | Agent has zero example blocks showing sample input prompts and expected outputs |
| 12 | `.claude/agents/presentation-vibe-coding.md` | — | R05 | `missing-examples` | Agent has zero example blocks despite a complex multi-step workflow |
| 13 | `.claude/agents/presentation-vibe-coding.md` | 13 | R08 | `unused-tool-declared` | NotebookEdit declared in allowedTools but the agent only edits HTML/CSS files; Jupyter notebook editing is out of scope |
| 14 | `.claude/agents/presentation-learning-journey.md` | — | R05 | `missing-examples` | Agent has zero example blocks |
| 15 | `.claude/agents/presentation-learning-journey.md` | 13 | R08 | `unused-tool-declared` | NotebookEdit declared in allowedTools but agent only edits HTML presentations |
| 16 | `.claude/agents/weather-agent.md` | — | R05 | `missing-examples` | Agent has zero example blocks |
| 17 | `.claude/agents/time-agent.md` | — | R05 | `missing-examples` | Agent has zero example blocks |
| 18 | `.claude/agents/workflows/best-practice/workflow-claude-subagents-agent.md` | — | R05 | `missing-examples` | Agent has zero example blocks despite multi-phase research workflow |
| 19 | `.claude/agents/workflows/best-practice/workflow-claude-skills-agent.md` | — | R05 | `missing-examples` | Agent has zero example blocks |
| 20 | `.claude/agents/workflows/best-practice/workflow-concepts-agent.md` | — | R05 | `missing-examples` | Agent has zero example blocks despite an extensive 8-section analysis workflow |
| 21 | `.claude/agents/workflows/best-practice/workflow-claude-settings-agent.md` | — | R05 | `missing-examples` | Agent has zero example blocks |
| 22 | `.claude/agents/workflows/best-practice/workflow-claude-commands-agent.md` | — | R05 | `missing-examples` | Agent has zero example blocks |
| 23 | `development-workflows/rpi/.claude/agents/ux-designer.md` | — | R05 | `missing-examples` | Agent has zero example blocks; the deliverable description is minimal |
| 24 | `development-workflows/rpi/.claude/agents/technical-cto-advisor.md` | — | R05 | `missing-examples` | Agent has zero example blocks despite a five-step decision framework |
| 25 | `development-workflows/rpi/.claude/agents/technical-cto-advisor.md` | — | R15 | `vague-quantifier` | Six vague quantifier instances: 'appropriate' x4, 'properly' x1, 'relevant' x1 |
| 26 | `development-workflows/rpi/.claude/agents/documentation-analyst-writer.md` | — | R05 | `missing-examples` | Agent has zero example blocks |
| 27 | `development-workflows/rpi/.claude/agents/product-manager.md` | — | R05 | `missing-examples` | Agent has zero example blocks |
| 28 | `development-workflows/rpi/.claude/agents/senior-software-engineer.md` | — | R05 | `missing-examples` | Agent has zero example blocks |
| 29 | `development-workflows/rpi/.claude/agents/code-reviewer.md` | — | R05 | `missing-examples` | Agent has zero example blocks |
| 30 | `development-workflows/rpi/.claude/agents/constitutional-validator.md` | — | R05 | `missing-examples` | Agent has zero example blocks despite an extensive five-dimension validation framework |
| 31 | `development-workflows/rpi/.claude/agents/constitutional-validator.md` | — | R15 | `vague-quantifier` | Three vague quantifier instances: 'appropriate' x2, 'relevant' x1 |
| 32 | `agent-teams/.claude/agents/time-agent.md` | — | R05 | `missing-examples` | Agent has zero example blocks |
| 33 | `.claude/skills/time-skill/SKILL.md` | — | R05 | `missing-examples` | Skill has zero inline example blocks |
| 34 | `.claude/skills/weather-fetcher/SKILL.md` | — | R05 | `missing-examples` | Skill has zero inline example blocks |
| 35 | `.claude/skills/weather-svg-creator/SKILL.md` | — | R05 | `missing-inline-example` | Examples are deferred to reference.md and examples.md; no inline example in the SKILL.md body |
| 36 | `agent-teams/.claude/skills/time-svg-creator/SKILL.md` | — | R05 | `missing-inline-example` | Examples are deferred to reference.md and examples.md; no inline example in the SKILL.md body |
| 37 | `.claude/commands/time-command.md` | — | R12 | `missing-allowed-tools` | Command runs a Bash date command but declares no allowed-tools in frontmatter |
| 38 | `.claude/commands/workflows/development-workflows.md` | — | R12 | `missing-allowed-tools` | Command launches agents, reads/writes files, and runs Bash but declares no allowed-tools |
| 39 | `.claude/commands/workflows/development-workflows.md` | — | R15 | `vague-quantifier-appropriate` | One vague quantifier: 'appropriate row' in table update instructions |
| 40 | `.claude/commands/workflows/best-practice/workflow-claude-settings.md` | — | R12 | `missing-allowed-tools` | Command orchestrates agents, reads changelog, updates badge and runs Bash but declares no allowed-tools |
| 41 | `.claude/commands/workflows/best-practice/workflow-claude-skills.md` | — | R12 | `missing-allowed-tools` | Command missing allowed-tools declaration |
| 42 | `.claude/commands/workflows/best-practice/workflow-claude-commands.md` | — | R12 | `missing-allowed-tools` | Command missing allowed-tools declaration |
| 43 | `.claude/commands/workflows/best-practice/workflow-claude-subagents.md` | — | R12 | `missing-allowed-tools` | Command missing allowed-tools declaration |
| 44 | `.claude/commands/workflows/best-practice/workflow-concepts.md` | — | R12 | `missing-allowed-tools` | Command missing allowed-tools declaration |
| 45 | `agent-teams/.claude/commands/time-orchestrator.md` | — | R12 | `missing-allowed-tools` | Command uses Agent and Skill tools but declares no allowed-tools |
| 46 | `development-workflows/rpi/.claude/commands/rpi/plan.md` | — | R12 | `missing-allowed-tools` | Command orchestrates multiple agents and reads/writes files but declares no allowed-tools |
| 47 | `development-workflows/rpi/.claude/commands/rpi/plan.md` | — | R25 | `missing-empty-input-guard` | Command requires a feature slug in $ARGUMENTS but has no explicit empty-input stop at the top of the file — the 'MUST parse' instruction appears in Phase 0, not as a guard before Phase 0 executes |
| 48 | `development-workflows/rpi/.claude/commands/rpi/plan.md` | — | R15 | `vague-quantifier` | Two vague quantifier instances: 'appropriate code areas', 'relevant project guidelines' |
| 49 | `development-workflows/rpi/.claude/commands/rpi/research.md` | — | R12 | `missing-allowed-tools` | Command missing allowed-tools declaration |
| 50 | `development-workflows/rpi/.claude/commands/rpi/research.md` | — | R25 | `missing-empty-input-guard` | Command requires a feature slug in $ARGUMENTS but has no guard at top of file for empty input |
| 51 | `development-workflows/rpi/.claude/commands/rpi/implement.md` | — | R12 | `missing-allowed-tools` | Command missing allowed-tools declaration |
| 52 | `development-workflows/rpi/.claude/commands/rpi/implement.md` | — | R25 | `missing-empty-input-guard` | Command requires a feature slug in $ARGUMENTS but has no guard at top of file for empty input |
| 53 | `development-workflows/rpi/.claude/commands/rpi/implement.md` | — | R15 | `vague-quantifier` | Four vague quantifier instances: 'appropriate agent' x1, 'appropriate error handling' x1, 'relevant existing code' x1, 'properly follow' x1 |
| 54 | `CLAUDE.md` | — | CC-stale-count | `stale-hook-event-count` | CLAUDE.md lists 15 hook events configured in settings.json; .claude/hooks/config/hooks-config.json exposes disable flags for 27+ event types including WorktreeCreate, WorktreeRemove, InstructionsLoaded, PostCompact, Elicitation, ElicitationResult, StopFailure, CwdChanged, FileChanged, TaskCreated, PermissionDenied — the listed count is stale |
| 55 | `.claude/skills/weather-svg-creator/SKILL.md` | — | CC-orphan-component | `unverified-sub-references` | SKILL.md references sibling files reference.md and examples.md; these were not audited and may not exist or may have drifted from the skill description |
| 56 | `agent-teams/.claude/skills/time-svg-creator/SKILL.md` | — | CC-orphan-component | `unverified-sub-references` | SKILL.md references sibling files reference.md and examples.md that were not audited |
| 57 | `.claude/skills/agent-browser/SKILL.md` | — | CC-orphan-component | `unverified-sub-references` | SKILL.md references six files under references/ (commands.md, snapshot-refs.md, session-management.md, authentication.md, video-recording.md, proxy-support.md) and three template files under templates/ — these were not audited |

