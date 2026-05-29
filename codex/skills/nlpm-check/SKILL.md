---
name: nlpm-check
description: Use when a Codex user asks to check NLPM-supported artifacts deterministically; runs bin/nlpm-check and interprets manifest, frontmatter, config, and hook findings.
---

# NLPM Check for Codex

Use this skill when the user asks Codex to check, validate, lint, or audit NL artifacts with NLPM's deterministic checker.

## Workflow

1. Locate the target path. Default to the current repo root when the user does not provide one.
2. Prefer the repo-local binary when present:

```bash
python3 bin/nlpm-check <path> --profile auto --format json
```

If the repo-local binary is not present, use an installed `nlpm-check` on `PATH` with the same arguments.

3. Read the JSON findings. Group them by `confidence`:
   - `high`: blocking deterministic bug; report first.
   - `medium`: advisory unless the user asked for strict release gating.
   - `low`: informational.
4. Explain the concrete file/path, rule, message, and fix from the checker output. Do not invent additional deterministic findings in prose.
5. If the user asks for full 100-point quality scoring, state that Codex can use the reference skills for review, but the richer `/nlpm:score` agent orchestration remains the Claude Code surface.

## Boundaries

- Do not reimplement checker logic inside this skill.
- Do not claim Codex has `/nlpm:*` slash-command parity.
- Keep deterministic `bin/nlpm-check` findings separate from any LLM-judged writing-quality observations.
