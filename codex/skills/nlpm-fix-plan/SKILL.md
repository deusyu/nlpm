---
name: nlpm-fix-plan
description: Use when a Codex user asks how to fix NLPM checker findings; runs bin/nlpm-check JSON and turns deterministic fixes into an ordered repair plan.
---

# NLPM Fix Plan for Codex

Use this skill when the user wants a repair plan for NLPM findings in Codex.

## Workflow

1. Run the checker in JSON mode:

```bash
python3 bin/nlpm-check <path> --profile auto --format json
```

If `bin/nlpm-check` is absent, use `nlpm-check` from `PATH`.

2. Build the fix plan from checker fields only:
   - `path` and `line` identify the edit location.
   - `message` explains the deterministic failure.
   - `fix` is the preferred mechanical repair.
3. Order repairs by confidence and blast radius:
   - Parse errors and manifest path errors first.
   - Missing frontmatter and name-parent mismatches next.
   - Hook event casing next.
   - Medium advisory cleanup last.
4. When the user asks you to execute the plan, edit only the listed files, then rerun the same checker command.
5. If a requested fix needs judgment beyond the deterministic checker output, say so and use `nlpm:scoring` / `nlpm:rules` as reference rather than pretending the binary decided it.

## Boundaries

- Do not invent automatic rewrites for vague language or instruction quality.
- Do not claim Codex can run `/nlpm:fix`; this is a checker-backed repair-plan skill.
- Keep Claude Code slash-command recommendations scoped to workflows that actually require Claude's agents.
