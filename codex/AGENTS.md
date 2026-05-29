# nlpm — checker-backed workflows for Codex CLI

This Codex plugin ships two surfaces:

- **Checker-backed workflow skills** that run `bin/nlpm-check`, read JSON findings, and produce repair plans.
- **Reference skills** for the 50 Rules of Natural Language Programming, the 100-point scoring rubric, per-tool conventions (Claude Code / Codex CLI / Antigravity), anti-patterns, vocabulary discipline, and authoring guides.

The Codex package does not claim `/nlpm:*` slash-command parity. Codex users should use the workflow skills and the standalone checker. Claude Code remains the richer slash-command orchestration surface because its `/nlpm:*` commands dispatch specialist agents.

## Deterministic Checks

Use these skills when the user wants executable NLPM feedback in Codex:

| Skill | What it does |
|-------|--------------|
| `$nlpm-check` | Runs `bin/nlpm-check <path> --profile auto --format json` and explains deterministic findings |
| `$nlpm-score` | Runs the checker first, then clearly labels any rubric-based Codex review as judgment-only |
| `$nlpm-fix-plan` | Turns checker JSON findings into an ordered mechanical repair plan |

If `bin/nlpm-check` is not present in the target repo, use an installed `nlpm-check` on `PATH` with the same arguments.

## Reference Skills

Load these when the user needs NLPM's rulebook, conventions, or writing guidance:

| Skill | What it teaches |
|-------|-----------------|
| `$nlpm-rules` | The 50 Rules of Natural Language Programming (R01-R51) |
| `$nlpm-scoring` | 100-point penalty rubric per artifact type |
| `$nlpm-conventions` | Universal floor: SKILL.md open spec, AGENTS.md, naming |
| `$nlpm-conventions-claude` | Claude Code overlay: `.claude/` paths, plugin.json, hook events |
| `$nlpm-conventions-codex` | Codex CLI overlay: `.codex/config.toml`, `.codex-plugin/`, `.agents/skills/` |
| `$nlpm-conventions-antigravity` | Antigravity + Gemini CLI overlay |
| `$nlpm-patterns` | NL programming patterns + anti-patterns |
| `$nlpm-vocabulary` | Controlled-vocabulary discipline (R51) |
| `$nlpm-testing` | NL-TDD spec format |
| `$nlpm-security` | Security pattern database for executable artifacts |
| `$nlpm-orchestration` | Multi-agent workflow patterns (Claude-lineage; informational on Codex) |
| `$nlpm-writing-skills` ... `$nlpm-writing-prompts` | Authoring guides per artifact type |

## Boundaries

- Do not reimplement deterministic checks in prose; run `bin/nlpm-check`.
- Do not claim Codex can run `/nlpm:score`, `/nlpm:check`, or `/nlpm:fix`.
- Keep binary findings separate from LLM-judged quality review.

Source and full Claude Code plugin: <https://github.com/xiaolai/nlpm>
