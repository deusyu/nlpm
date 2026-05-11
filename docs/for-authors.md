# NLPM for plugin authors

You're building a Claude Code plugin or skill kit. NLPM checks one thing the official validator doesn't: **does your manifest match what's on disk?**

That single check has caught manifest-vs-disk bugs in plugins from authors with 16k-69k stars (see `analysis/ecosystem-gap.md`). The check is mechanical, fast, and runs without Claude Code installed.

## The two surfaces

| Surface | What it does | When to use |
|---|---|---|
| **`bin/nlpm-check`** (standalone Python script) | Deterministic checks — manifest-vs-disk, frontmatter, hook event-name case — exits non-zero on findings | Pre-commit hooks, CI, pre-publish scripts |
| **`/nlpm:check` and `/nlpm:score`** (Claude Code slash commands) | Full 100-point quality scoring with judgment-required findings (vague language, instruction quality, etc.) | Interactive review during development |

Both surfaces share the same rule registry. The binary is the deterministic subset; the slash commands are the full set.

## What the binary catches

High-confidence findings (exit code 1):
- **manifest-disk-diff**: a path declared in `plugin.json` doesn't exist on disk, or a SKILL.md / agent / command exists on disk but isn't reachable from the manifest
- **frontmatter**: missing required `name` (skills, agents) or `description` (commands, skills, agents)
- **skill name parent**: SKILL.md `name:` field doesn't match its parent directory (silently breaks Claude Code's skill loader)
- **skill name format**: SKILL.md `name:` violates the open spec format (`^[a-z][a-z0-9-]{0,63}$`)
- **hook event case**: `pretooluse` instead of `PreToolUse` (the loader is case-sensitive and silently ignores wrong-case events)

Medium-confidence findings (exit code 1 only under `--strict`):
- **hook event-name**: unknown event name not in the documented event list

For full quality scoring (description quality, vague language, instruction clarity, etc.) run `/nlpm:score` inside Claude Code.

## Install the binary

The binary is a single Python 3.11+ file with no external dependencies.

```bash
# Option A — into /usr/local/bin
curl -fsSL -o /usr/local/bin/nlpm-check \
  https://raw.githubusercontent.com/xiaolai/nlpm-for-claude/main/bin/nlpm-check
chmod +x /usr/local/bin/nlpm-check

# Option B — into your repo (commits the script alongside your code)
mkdir -p bin
curl -fsSL -o bin/nlpm-check \
  https://raw.githubusercontent.com/xiaolai/nlpm-for-claude/main/bin/nlpm-check
chmod +x bin/nlpm-check
```

Verify:

```bash
nlpm-check --version
# nlpm-check 0.8.0
```

## Use it in your authoring workflow

### 1. Editing — slash command (in Claude Code)

While in Claude Code, run `/nlpm:check` to surface findings inline. The hook installed by the plugin emits advisory checks as you write SKILL.md / agent / command files.

### 2. Committing — pre-commit hook

Copy the template:

```bash
curl -fsSL -o .git/hooks/pre-commit \
  https://raw.githubusercontent.com/xiaolai/nlpm-for-claude/main/templates/pre-commit-nlpm.sh
chmod +x .git/hooks/pre-commit
```

Now `git commit` blocks if NLPM finds high-confidence issues. Bypass with `git commit --no-verify` (not recommended).

If you use the [`pre-commit`](https://pre-commit.com/) framework, add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: nlpm-check
        name: nlpm-check
        entry: nlpm-check
        language: system
        pass_filenames: false
        files: '(\.claude-plugin/.+\.json|skills/.+/SKILL\.md|agents/.+\.md|commands/.+\.md|hooks/hooks\.json)$'
```

### 3. Pushing — GitHub Actions

Copy the workflow template:

```bash
mkdir -p .github/workflows
curl -fsSL -o .github/workflows/nlpm-check.yml \
  https://raw.githubusercontent.com/xiaolai/nlpm-for-claude/main/templates/workflows/nlpm-check.yml
```

Commit. Every push and PR now runs `nlpm-check`. No secrets required.

### 4. Publishing — release script

Add to your publish script (npm publish, release-please, manual):

```bash
nlpm-check --strict . || {
  echo "nlpm-check found issues. Fix them or run /nlpm:fix in Claude Code."
  exit 1
}
```

`--strict` exits 1 on findings of any confidence (high + medium + low).

## What NLPM does NOT replace

NLPM is **complementary** to the official validators. Run both.

| Tool | What it covers |
|---|---|
| `claude plugin validate` (Anthropic, built-in) | Manifest JSON syntax + deprecation warnings |
| `plugin-validator` (Anthropic agent) | Per-component frontmatter, security checks, MCP configs |
| `skills-ref` (Linux Foundation) | Per-skill frontmatter validity, name conventions |
| **NLPM** | Cross-component consistency (manifest-vs-disk), hook event-name case, frontmatter |

If you can only adopt one validator: pick the one that covers your most likely failure mode. If you've been bitten by "I added a skill but users can't see it" — that's the manifest-vs-disk gap, and NLPM is the only tool that catches it.

## JSON output

For machine consumption:

```bash
nlpm-check --json .
```

```json
{
  "version": "0.8.0",
  "plugin_root": "/path/to/plugin",
  "findings": [
    {
      "confidence": "high",
      "rule": "manifest-disk-diff",
      "path": "skills/foo/SKILL.md",
      "line": 0,
      "message": "SKILL.md exists on disk but not registered by plugin.json `skills`",
      "fix": "Add `skills/foo/` to plugin.json `skills` array"
    }
  ],
  "summary": {"high": 1, "medium": 0, "low": 0}
}
```

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Clean (or `--strict` not set and no high-confidence findings) |
| 1 | One or more high-confidence findings (or any finding under `--strict`) |
| 2 | Error reading the manifest, path not found, etc. |

## Reporting issues

NLPM rules cite primary sources (Anthropic docs, the Agent Skills spec). If a check is wrong, file an issue with the docs URL that contradicts it: <https://github.com/xiaolai/nlpm-for-claude/issues>.

## See also

- `analysis/ecosystem-gap.md` — why this validator exists and what other tools do
- `analysis/scope-expansion-2026-05.md` — the broader plan for author-facing NLPM
- The full slash-command surface — install the plugin: `claude plugin install nlpm@xiaolai --scope project`
