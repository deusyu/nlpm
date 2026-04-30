# NLPM Audit: shinpr/claude-code-workflows
**Date**: 2026-04-30  |  **Artifacts**: 51  |  **Strategy**: full
**NL Score**: 86/100
**Security**: CLEAR
**Bugs**: 0  |  **Quality Issues**: 6  |  **Security Findings**: 0

## NL Score Summary
| File | Type | Score | Top Issue |
|------|------|-------|-----------|
| agents/technical-designer.md | agent | 60 | "appropriate" used 10+ times throughout (cap -20); no model; no examples |
| agents/technical-designer-frontend.md | agent | 60 | "appropriate" used 10+ times throughout (cap -20); no model; no examples; checklist/process mismatch |
| agents/work-planner.md | agent | 69 | No model; no examples; output is a file but no template shown (-5 partial) |
| agents/prd-creator.md | agent | 69 | No model; no examples; output is a file but no template shown (-5 partial) |
| agents/codebase-analyzer.md | agent | 70 | 5 vague quantifiers (relevant×2, appropriate×3, -10); no model; no examples |
| agents/ui-spec-designer.md | agent | 71 | No model; no examples; output is a spec file but no template shown (-5 partial) |
| agents/document-reviewer.md | agent | 72 | No model; no examples; 4 vague quantifiers (-8) |
| agents/investigator.md | agent | 74 | No model; no examples; 3 vague quantifiers (-6) |
| agents/scope-discoverer.md | agent | 74 | No model; no examples; 3 vague quantifiers (-6) |
| agents/solver.md | agent | 74 | No model; no examples; 3 vague quantifiers (-6) |
| agents/task-decomposer.md | agent | 74 | No model; no examples; 3 vague quantifiers (-6) |
| agents/task-executor.md | agent | 74 | No model; no examples; 3 vague quantifiers (-6) |
| agents/code-reviewer.md | agent | 76 | No model; no examples; 2 vague quantifiers (-4) |
| agents/code-verifier.md | agent | 76 | No model; no examples; 2 vague quantifiers (-4) |
| agents/quality-fixer.md | agent | 76 | No model; no examples; 2 vague quantifiers (-4) |
| agents/quality-fixer-frontend.md | agent | 76 | No model; no examples; 2 vague quantifiers (-4) |
| agents/requirement-analyzer.md | agent | 76 | No model; no examples; 2 vague quantifiers (-4) |
| agents/rule-advisor.md | agent | 76 | No model; no examples; 2 vague quantifiers (-4) |
| agents/security-reviewer.md | agent | 76 | No model; no examples; 2 vague quantifiers (-4) |
| agents/task-executor-frontend.md | agent | 76 | No model; no examples; 2 vague quantifiers (-4) |
| agents/verifier.md | agent | 76 | No model; no examples; 2 vague quantifiers (-4) |
| agents/integration-test-reviewer.md | agent | 78 | No model; no examples; 1 vague quantifier (-2) |
| agents/acceptance-test-generator.md | agent | 89 | No model; has output format examples (no -15); 3 vague quantifiers (-6) |
| agents/design-sync.md | agent | 91 | No model; has 5 concrete conflict-detection examples (no -15); 2 vague quantifiers (-4) |
| skills/ai-development-guide/SKILL.md | skill | 95 | Minor vague language (2-3 instances) |
| skills/documentation-criteria/SKILL.md | skill | 95 | Minor vague language (2-3 instances) |
| skills/frontend-ai-guide/SKILL.md | skill | 95 | Minor vague language (2-3 instances) |
| skills/recipe-front-review/SKILL.md | skill | 95 | Minor vague language (2-3 instances) |
| skills/recipe-fullstack-implement/SKILL.md | skill | 95 | Minor vague language (2-3 instances) |
| skills/subagents-orchestration-guide/SKILL.md | skill | 95 | Minor vague language (2-3 instances) |
| skills/coding-principles/SKILL.md | skill | 96 | Minor vague language (2 instances) |
| skills/recipe-add-integration-tests/SKILL.md | skill | 96 | Minor vague language (2 instances) |
| skills/recipe-design/SKILL.md | skill | 96 | Minor vague language (2 instances) |
| skills/recipe-diagnose/SKILL.md | skill | 96 | Minor vague language (2 instances) |
| skills/recipe-front-design/SKILL.md | skill | 96 | Minor vague language (2 instances) |
| skills/recipe-front-plan/SKILL.md | skill | 96 | Minor vague language (2 instances) |
| skills/recipe-fullstack-build/SKILL.md | skill | 96 | Minor vague language (2 instances) |
| skills/recipe-implement/SKILL.md | skill | 96 | Minor vague language (2 instances) |
| skills/recipe-plan/SKILL.md | skill | 96 | Minor vague language (2 instances) |
| skills/recipe-review/SKILL.md | skill | 96 | Minor vague language (2 instances) |
| skills/recipe-reverse-engineer/SKILL.md | skill | 96 | Minor vague language (2 instances) |
| skills/recipe-task/SKILL.md | skill | 96 | Minor vague language (2 instances) |
| skills/recipe-update-doc/SKILL.md | skill | 96 | Minor vague language (2 instances) |
| skills/typescript-rules/SKILL.md | skill | 96 | Minor vague language (2 instances) |
| skills/implementation-approach/SKILL.md | skill | 97 | Minor vague language (1 instance) |
| skills/integration-e2e-testing/SKILL.md | skill | 97 | Minor vague language (1 instance) |
| skills/recipe-build/SKILL.md | skill | 97 | Minor vague language (1 instance) |
| skills/recipe-front-build/SKILL.md | skill | 97 | Cross-reference to `dev-workflows-frontend:task-decomposer` — no frontend variant exists |
| skills/task-analyzer/SKILL.md | skill | 97 | Minor vague language (1 instance) |
| skills/test-implement/SKILL.md | skill | 97 | Minor vague language (1 instance) |
| skills/testing-principles/SKILL.md | skill | 97 | Minor vague language (1 instance) |

**Agent average**: 74.3/100 (24 files)  |  **Skill average**: 96.1/100 (27 files)  |  **Overall**: 86/100

## Security Scan
| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 0 |
| Medium | 0 |
| Low | 0 |

### Execution Surface Inventory
| Surface | Files |
|---------|-------|
| Hooks | 0 |
| Scripts | 0 |
| MCP configs | 0 |
| Package manifests | 0 |

The repository contains only `agents/`, `skills/`, `CONTRIBUTING.md`, `LICENSE`, and `README.md`. No executable surfaces exist; no hooks.json, no shell scripts, no MCP server configuration files, and no package.json or requirements.txt were found.

### Security Findings
No security findings.

## Bugs (PR-worthy)
No confirmed bugs. The `agents/requirement-analyzer.md` body references TaskCreate in its process description but the frontmatter `tools:` list does not include it; this is flagged as a cross-component concern below rather than a confirmed bug because the reference is advisory ("may use TaskCreate") rather than an unconditional call.

## Security Fixes (PR-worthy, Medium/Low only)
No security fixes required.

## Quality Issues (informational)
| # | Files | Issue | Penalty |
|---|-------|-------|---------|
| 1 | all 24 agents | **Missing model declaration** — no `model:` field in any agent's frontmatter. Claude Code defaults to the ambient context model rather than the tier appropriate for each agent's task complexity (haiku for mechanical agents like codebase-analyzer; sonnet for reasoning-heavy agents like technical-designer). | -5 per agent |
| 2 | 22 of 24 agents (all except design-sync and acceptance-test-generator) | **No example blocks** — zero worked invocation scenarios across 22 agents, making it impossible for callers to verify correct usage or for the framework to ground expected input/output shapes. `design-sync.md` (5 detection examples) and `acceptance-test-generator.md` (output format examples) are the only exceptions. | -15 per agent |
| 3 | agents/technical-designer.md | **Vague quantifiers at cap** — "appropriate" appears 10+ times (e.g., "appropriate abstractions", "appropriate level of detail", "appropriate design patterns") with no measurable thresholds. Other vague terms (comprehensive, sufficient, proper) appear throughout. Cap penalty reached. | -20 |
| 4 | agents/technical-designer-frontend.md | **Vague quantifiers at cap** — same pattern as technical-designer.md; "appropriate" used 10+ times throughout the file. Also affected by the checklist/process mismatch noted in Cross-Component. | -20 |
| 5 | agents/codebase-analyzer.md | **Elevated vague quantifier density** — 5 instances (relevant×2, appropriate×3) without measurable criteria. | -10 |
| 6 | 17 agents scoring 74–78 (solver, task-executor, scope-discoverer, task-decomposer, investigator, security-reviewer, rule-advisor, quality-fixer, task-executor-frontend, verifier, quality-fixer-frontend, code-reviewer, code-verifier, requirement-analyzer, document-reviewer, integration-test-reviewer, and others) | **Minor scattered vague quantifiers** — 1–4 instances per file of "appropriate", "relevant", "comprehensive", "sufficient", etc. without measurable thresholds. Contributes -2 to -8 per file on top of the systematic -15/-5 penalties. | -2 to -8 per agent |

## Cross-Component
| # | Source File | Referenced Artifact | Issue |
|---|-------------|---------------------|-------|
| 1 | skills/recipe-front-build/SKILL.md | `dev-workflows-frontend:task-decomposer` | The skill dispatches work using the namespace-qualified agent name `dev-workflows-frontend:task-decomposer`, but only `agents/task-decomposer.md` exists — there is no `-frontend` variant registered under that namespace. If the plugin manifest follows the file structure, this call will fail to route. |
| 2 | agents/technical-designer-frontend.md | Internal process sections | The verification checklist includes "Standards identification gate completed (required)" as a mandatory step, but the Mandatory Process section does not describe the Standards Identification Gate. The parent `technical-designer.md` describes the gate at length (lines 31–51 of that file). The frontend variant inherited the checklist item without porting the process description, leaving callers with an undocumented requirement. |
| 3 | agents/requirement-analyzer.md | TaskCreate tool | The process description references TaskCreate as part of the workflow but the `tools:` frontmatter does not list it. If the agent attempts to call TaskCreate at runtime, Claude Code will either refuse the call or require an unexpected permission grant. |

## Recommendation
CLEAR — no confirmed bugs, no security findings. The plugin is structurally sound and the skills layer is high quality. Submit targeted quality PRs to raise the agent layer above 80.

**Highest-ROI PR** (two agents, +40 cumulative points): Add measurable criteria to `technical-designer.md` and `technical-designer-frontend.md`, replacing unconstrained uses of "appropriate", "comprehensive", "sufficient", and "proper" with concrete thresholds (e.g., "describe the tradeoffs between at least two design alternatives" instead of "use appropriate design patterns"). This alone moves both files from 60 to 80 and raises the repo average from 86 to 87.6.

**Systematic PR** (22 agents, +15 per agent): Add a `## Examples` section to each agent with at least one concrete invocation scenario. Priority order: technical-designer, work-planner, prd-creator (complex agents with the most to gain), then the remaining 19. This would raise the repo-wide NL Score from 86 to approximately 91.

**Model tier PR** (24 agents, +5 per agent): Add `model: haiku` to mechanical/routing agents (codebase-analyzer, scope-discoverer, task-decomposer, design-sync, quality-fixer, quality-fixer-frontend) and `model: sonnet` to reasoning-heavy agents (technical-designer, work-planner, prd-creator, verifier, investigator, requirement-analyzer). This is a low-effort change with no correctness risk.

**Cross-component fixes** (3 items): (1) Add or alias `task-decomposer-frontend` in the frontend namespace or update `recipe-front-build` to use the existing `dev-workflows:task-decomposer`; (2) add the Standards Identification Gate description to `technical-designer-frontend.md`'s Mandatory Process section; (3) add `TaskCreate` to `requirement-analyzer.md`'s `tools:` list.
