---
title: How to install
outline: [2, 3]
---

# How to install

NLPM has three install surfaces — pick whichever fits your environment.

The **slash-command plugin** ships through Claude Code. Inside Claude Code you get eleven `/nlpm:*` commands backed by six specialist agents and the reference skill catalog. The scoring rubric this plugin runs covers all three tools NLPM supports — **Claude Code, Codex CLI, and Antigravity** — via tier-aware overlays in `nlpm:conventions-claude` / `nlpm:conventions-codex` / `nlpm:conventions-antigravity`. See [the multi-tool design doc](https://github.com/xiaolai/nlpm/blob/main/analysis/multi-tool-design-2026-05.md).

The **Codex plugin** ships checker-backed workflow skills plus the reference skill catalog. It does not promise `/nlpm:*` slash-command parity; use `$nlpm-check`, `$nlpm-score`, and `$nlpm-fix-plan` to call `bin/nlpm-check` and interpret findings.

The **standalone binary** (`bin/nlpm-check`) has no Claude Code dependency. Use it in Codex / Antigravity projects, in any project's pre-commit hook, or in CI.

## Plugin install (Claude Code)

Two install paths — both reach the same code:

### Via Anthropic's official community marketplace

Curated; updates lag the maintainer marketplace by up to ~24h.

```bash
claude plugin marketplace add anthropics/claude-plugins-community
claude plugin install nlpm@claude-community --scope project   # or --scope user
```

### Via the xiaolai marketplace

Latest version lands here first.

```bash
claude plugin marketplace add xiaolai/claude-plugin-marketplace

# Project scope (recommended)
claude plugin install nlpm@xiaolai --scope project

# Global (all projects)
claude plugin install nlpm@xiaolai --scope user
```

> **"Plugin not found in marketplace 'xiaolai'"?** Your local marketplace clone is stale. Run `claude plugin marketplace update xiaolai` and retry — `plugin install` does not auto-refresh. (The community marketplace doesn't have this caveat.)

Then in your project:

```bash
/nlpm:ls              # discover NL artifacts
/nlpm:score           # 100-point quality scoring
/nlpm:check           # cross-component consistency
/nlpm:vocab-init      # bootstrap a vocabulary skill (optional)
/nlpm:report          # render a self-contained HTML report
```

## Standalone binary (Codex CLI, Antigravity, any CI, no Claude Code required)

`bin/nlpm-check` is a single-file Python 3.11+ script (stdlib only) that runs the deterministic subset of `/nlpm:check`. It validates Claude, Codex, and generic SKILL.md surfaces via `--profile auto|claude|codex|generic`. Drop it into pre-commit hooks or CI.

```bash
git clone https://github.com/xiaolai/nlpm
./nlpm/bin/nlpm-check /path/to/your/plugin --profile auto
```

Or copy `bin/nlpm-check` into your repo:

```bash
curl -fsSL https://raw.githubusercontent.com/xiaolai/nlpm/main/bin/nlpm-check -o nlpm-check
chmod +x nlpm-check
./nlpm-check .
```

Use `--format json` for CI/badges. The legacy `--json` alias remains supported.

Pre-commit hook and GitHub Actions workflow templates live at:

- `templates/pre-commit-nlpm.sh`
- `templates/workflows/nlpm-check.yml`

## Vocabulary discipline (R51, opt-in)

After installing NLPM in your project, decide whether to enforce a canonical noun/verb registry. If yes:

```bash
/nlpm:vocab-init      # detects layout, runs the extractor, seeds tables
```

This writes `skills/<plugin>/vocabulary/SKILL.md` + `registry.yaml`. Prune the seeded tables, define `deprecated:` synonym lists, then opt into R51 by adding to `.claude/nlpm.local.md`:

```yaml
rule_overrides:
  R51:
    enabled: true
    vocabulary_skill: skills/<plugin>/vocabulary/
```

Now `/nlpm:score` and `/nlpm:check` flag deprecated-synonym occurrences. See [/reference/principles](/reference/principles) for the six principles behind R51.

## Updates

```bash
claude plugin update nlpm@xiaolai
```

## Uninstall

```bash
claude plugin uninstall nlpm@xiaolai
```

## See also

- [/reference/](/reference/) — full framework guide
- [Auditor dashboard](/dashboard.html) — cross-repo audit data
- [GitHub issues](https://github.com/xiaolai/nlpm/issues) — bug reports, feature requests
