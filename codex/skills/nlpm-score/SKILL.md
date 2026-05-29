---
name: nlpm-score
description: Use when a Codex user asks for NLPM scoring; runs the deterministic checker first, then uses NLPM scoring reference skills for clearly labeled judgment-only review.
---

# NLPM Score for Codex

Use this skill when the user asks Codex to score an NL artifact or repo with NLPM.

## Workflow

1. Run the deterministic checker first:

```bash
python3 bin/nlpm-check <path> --profile auto --format json
```

If `bin/nlpm-check` is absent, use `nlpm-check` from `PATH`.

2. Treat checker findings as deterministic:
   - High findings are real structural failures unless the file has changed since the run.
   - Medium findings are advisory unless `--strict` or a release gate is in scope.
3. For quality scoring, load the NLPM reference skills that match the artifact:
   - `nlpm:scoring` for the penalty table.
   - `nlpm:rules` for rule text.
   - `nlpm:conventions` plus the matching tool overlay.
4. Label any LLM-judged score as a Codex review estimate, not as the Claude `/nlpm:score` command result.
5. Recommend Claude Code `/nlpm:score` only when the user needs the full agent-orchestrated scorer, trend updates, or NL-TDD integration.

## Boundaries

- Do not present Codex review estimates as deterministic binary output.
- Do not claim this skill dispatches NLPM scorer agents.
- Do not duplicate checker logic already covered by `bin/nlpm-check`.
