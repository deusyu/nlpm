# Universal Core + Codex Adapter Goal Plan

Status: execution plan
Scope: `universal-core + codex-adapter`

## Goal Prompt

Implement NLPM's universal deterministic checker core and a Codex-native adapter without rewriting the rule system or breaking the existing Claude Code plugin surface.

The result should make `bin/nlpm-check` the shared checker core, add profile-aware validation for Claude/Codex/generic NL artifacts, and replace the current Codex "reference knowledge only" posture with checker-backed Codex skill workflows. Do not promise `/nlpm:*` slash-command parity on Codex unless the supported Codex distribution surface can actually provide it.

## Problem

NLPM already has a Codex plugin manifest and a `codex/` skill tree, but the public Codex surface is incomplete:

- `.codex/prompts/` is empty, so Codex CLI users have no `/nlpm-*` slash-command entry.
- `.codex-plugin/plugin.json` currently says interactive linting remains a Claude Code plugin.
- `codex/AGENTS.md` presents the Codex package as reference knowledge, not as executable linting workflows.
- `bin/nlpm-check` currently centers on `.claude-plugin/plugin.json` discovery and explicitly skips the `codex/` subtree when scanning the Claude plugin.

This is not just a documentation gap. The implementation needs a real product boundary for Codex.

## Product Decision

Do not promise Codex `/nlpm:*` parity in the first implementation.

Promise these Codex-native surfaces instead:

- `bin/nlpm-check` as the shared deterministic checker.
- Codex skills that call the checker, interpret reports, and produce repair plans.
- Optional legacy `.codex/prompts/` entries only if they are verified to be a supported, distributable Codex plugin surface.

If `.codex/prompts/` is not a supported project/plugin distribution surface, leave it out of the promise and update documentation accordingly.

## Non-Goals

- Do not rewrite the 50-rule system.
- Do not replace the LLM-judged scorer/checker agents.
- Do not remove or rename existing Claude `/nlpm:*` commands.
- Do not migrate the auditor pipeline in this change.
- Do not make Codex skills duplicate checker logic that belongs in `bin/nlpm-check`.

## Architecture

`bin/nlpm-check` remains the only deterministic checker core.

Adapters call the core:

- Claude Code commands remain the existing interactive orchestration layer.
- Codex skills become the Codex-native workflow layer.
- CI, pre-commit, and generic author workflows call the binary directly.

Configuration is shared but backward-compatible:

- New cross-tool config: `nlpm.config.json`.
- Existing Claude config remains supported: `.claude/nlpm.local.md`.
- CLI `--config` overrides auto-discovery.

## Phase 0: Resolve Codex Entry Boundary

Before adding implementation, audit the current Codex surfaces:

- `.codex-plugin/plugin.json`
- `codex/AGENTS.md`
- `.codex/prompts/`
- `site/` and README references to Codex usage

Decide and document one of two outcomes:

1. Codex prompts are supported and distributable:
   - Add `.codex/prompts/nlpm-check.md`
   - Add `.codex/prompts/nlpm-score.md`
   - Add `.codex/prompts/nlpm-fix-plan.md`
   - Document them as legacy or compatibility entrypoints.

2. Codex prompts are not the right plugin surface:
   - Keep Codex entrypoints as skills plus `bin/nlpm-check`.
   - Do not claim `/nlpm:*` parity.
   - Update manifest and docs so they no longer say Codex is reference-only after the adapter lands.

Acceptance criteria:

- No public file implies Codex has `/nlpm:*` parity unless that entrypoint exists.
- No public file says Codex is "reference knowledge only" after checker-backed skills are added.

## Phase 1: Add Profile-Aware Core CLI

Extend `bin/nlpm-check` with:

- `--profile auto|claude|codex|generic`
- `--config <path>`
- `--format json|md`
- Keep `--json` as a backward-compatible alias for `--format json`.

Default behavior:

- Preserve existing behavior for current users as much as possible.
- Prefer `--profile auto` as the long-term default.
- In `auto`, discover available surfaces and choose the matching validator:
  - `.claude-plugin/plugin.json` -> Claude profile
  - `.codex-plugin/plugin.json` -> Codex profile
  - no tool manifest but `SKILL.md` files -> generic profile

Acceptance criteria:

- Existing `--json` consumers still work.
- Existing Claude plugin checks still produce the same high-confidence findings.
- Missing path and no-manifest error behavior remains scriptable with exit code 2.

## Phase 2: Implement Profile Validators

### Claude Profile

Keep current Claude behavior intact:

- `.claude-plugin/plugin.json`
- `commands/`
- `agents/`
- `skills/`
- `hooks/hooks.json`
- existing manifest-vs-disk and frontmatter checks

Do not make Codex artifacts create Claude findings.

### Codex Profile

Validate Codex plugin and project surfaces:

- `.codex-plugin/plugin.json`
  - required: `name`, `version`, `description`
  - component paths must stay inside the plugin root
  - declared `skills`, `hooks`, `mcpServers`, and `apps` paths must exist when present
- Declared Codex skill directories
  - every `SKILL.md` has `name` and `description`
  - `name` matches parent directory
  - `name` follows the open spec format
- `.agents/skills/<name>/SKILL.md`
  - validate as project-scope Codex skills
- `.codex/config.toml`
  - parseability check if feasible with stdlib
  - flag known deprecated `[features].codex_hooks` if present
- `.codex/hooks.json`
  - validate Codex hook event names using the Codex event table

Do not assume Codex plugin skills must live in exactly one hardcoded directory. Resolve from `.codex-plugin/plugin.json` paths first.

### Generic Profile

Validate the universal floor only:

- `SKILL.md` frontmatter
- `name == parent directory`
- skill name format
- optional AGENTS.md presence/shape checks if already deterministic

Do not require `.claude-plugin/` or `.codex-plugin/`.

Acceptance criteria:

- A Codex-only fixture passes discovery under `--profile codex` without needing `.claude-plugin/plugin.json`.
- A mixed fixture validates Claude and Codex surfaces without cross-profile false positives.
- A generic skill collection can be checked without any plugin manifest.

## Phase 3: Add Shared Config

Add `nlpm.config.json` with this minimal schema:

```json
{
  "artifact_paths": [],
  "enabled_rules": [],
  "score_thresholds": {
    "default": 70
  },
  "tool_profile": "auto"
}
```

Support config discovery in this order:

1. `--config <path>`
2. `nlpm.config.json`
3. `.claude/nlpm.local.md`
4. built-in defaults

Keep the schema small. Do not move all Claude-local options into JSON in this change.

Acceptance criteria:

- `--config` overrides defaults.
- Existing `.claude/nlpm.local.md` still works for Claude workflows.
- A Codex-only repo can configure profile and thresholds without creating `.claude/`.

## Phase 4: Build Codex Adapter Skills

Add checker-backed Codex skills:

- `codex/skills/nlpm-check/SKILL.md`
- `codex/skills/nlpm-score/SKILL.md`
- `codex/skills/nlpm-fix-plan/SKILL.md`

Responsibilities:

- Call `bin/nlpm-check` with the correct profile.
- Prefer `--format json` for structured interpretation.
- Explain high/medium/low findings.
- Produce concrete repair plans.
- Point users to Claude `/nlpm:score` only for judgment-heavy full scoring that the binary does not implement.

Boundaries:

- Skills must not reimplement deterministic checks in prose.
- Skills must not claim to run Claude subagents.
- Skills must clearly distinguish deterministic binary findings from LLM-judged quality review.

Update `.codex-plugin/plugin.json`:

- Change description from "reference knowledge only" to "checker-backed Codex workflows plus reference knowledge."
- Keep honest language that Claude Code still has the richer slash-command orchestration.

Acceptance criteria:

- Codex manifest declares the new skills.
- The new skills are discoverable from the plugin manifest.
- The docs no longer publicly frame Codex support as reference-only.

## Phase 5: Preserve Claude Adapter

Leave existing Claude commands untouched in this implementation:

- `commands/ls.md`
- `commands/score.md`
- `commands/check.md`
- `commands/fix.md`
- `commands/trend.md`
- `commands/test.md`
- `commands/init.md`
- `commands/security-scan.md`

Future migration path:

- `/nlpm:check` can call `bin/nlpm-check --profile claude` for deterministic findings.
- LLM checker/scorer agents continue to handle judgment-required findings.

Acceptance criteria:

- Existing Claude tests and command docs remain valid.
- No current Claude workflow regresses because Codex support was added.

## Phase 6: Fixtures, Tests, and CI

Add fixtures:

- `fixtures/claude`
- `fixtures/codex`
- `fixtures/mixed`
- `fixtures/generic`

Add tests for:

- old `--json` compatibility
- `--format json`
- `--format md`
- `--profile claude`
- `--profile codex`
- `--profile generic`
- `--profile auto`
- `--config` precedence
- Codex manifest path existence
- Codex-only repo with no `.claude-plugin`
- mixed repo without cross-profile false positives

Minimum verification commands:

```bash
python3 -m unittest tests.test_nlpm_check
python3 bin/nlpm-check fixtures/claude --profile claude --format json
python3 bin/nlpm-check fixtures/codex --profile codex --format json
python3 bin/nlpm-check fixtures/mixed --profile auto --format json
python3 bin/nlpm-check fixtures/generic --profile generic --format json
python3 bin/nlpm-check . --profile auto
```

Acceptance criteria:

- All existing tests pass.
- New profile tests pass.
- `python3 bin/nlpm-check . --profile auto` is clean or reports only intentional findings.

## Release Notes Checklist

Before release:

- Bump `.claude-plugin/plugin.json`.
- Bump `.codex-plugin/plugin.json`.
- Update marketplace metadata if plugin skill list changes.
- Update README and site install/use pages.
- Update `docs/for-authors.md`.
- Run the repo's standard self-checks.

## Risks

- Codex prompt entrypoints may not be a supported plugin distribution surface. Treat this as a product-boundary decision, not an implementation detail.
- `--profile auto` can become surprising if a repo contains multiple tool manifests. Prefer explicit profile in CI examples.
- `nlpm.config.json` can fragment configuration if it tries to replace `.claude/nlpm.local.md` too early. Keep it minimal.
- Codex conventions may continue to move. Keep first-pass Codex checks deterministic and conservative.

## Done Definition

The goal is complete when:

- `bin/nlpm-check` supports Claude, Codex, and generic profiles.
- Codex-only artifacts can be validated without a Claude manifest.
- Codex users have checker-backed NLPM skills or verified prompt entrypoints.
- Public docs no longer describe Codex support as only reference knowledge.
- Existing Claude Code plugin behavior is preserved.
- Tests cover all profiles and compatibility paths.
