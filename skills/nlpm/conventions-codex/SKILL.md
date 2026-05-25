---
name: conventions-codex
description: "Use when scoring or writing Codex CLI artifacts — covers .codex/config.toml schema, .codex-plugin/plugin.json, .agents/skills/ layout, Codex hook events, AGENTS.md hierarchy, marketplace.json, and the agents/openai.yaml sidecar."
version: 0.1.0
---

# Codex CLI Conventions

Tool-specific overlay for OpenAI Codex CLI artifacts. Loaded by the scorer and checker when an artifact is classified as **Tier 2-Codex** (per `agents/scorer.md` step 3). The universal floor lives in `nlpm:conventions`; this overlay adds Codex-specific schemas on top.

**Primary authoritative sources:**
- <https://developers.openai.com/codex>
- <https://developers.openai.com/codex/skills>
- <https://developers.openai.com/codex/guides/agents-md>
- <https://developers.openai.com/codex/config-reference>
- <https://developers.openai.com/codex/hooks>
- <https://developers.openai.com/codex/plugins>
- <https://github.com/openai/codex>

---

## 1. File system layout

Codex separates the **cross-tool surface** (`.agents/`) from the **Codex-private surface** (`.codex/`). The Claude Code mental model of "everything under one tool directory" does not transfer.

| Artifact | Project scope | User scope |
|---|---|---|
| Skills | `.agents/skills/<name>/SKILL.md` | `~/.agents/skills/` |
| Plugin manifest | `<plugin-root>/.codex-plugin/plugin.json` | — |
| Marketplace | `.agents/plugins/marketplace.json` | `~/.agents/plugins/marketplace.json` |
| AGENTS.md | Git root → CWD (concatenated; closer overrides earlier) | `~/.codex/AGENTS.md`, `~/.codex/AGENTS.override.md` |
| Config | `.codex/config.toml` (trust-gated) | `~/.codex/config.toml` |
| Hooks | `.codex/hooks.json` OR inline `[hooks]` in `config.toml` | `~/.codex/hooks.json` |
| Slash commands (deprecated) | — (not project-shareable) | `~/.codex/prompts/<name>.md` |
| MCP servers | `[mcp_servers.<id>]` table inside `config.toml` | same |
| Skill sidecar (Codex-specific) | `<skill>/agents/openai.yaml` next to `SKILL.md` | — |

**Trust gate:** Project hooks load only when `.codex/` is trusted. Trust is enforced via `/hooks` and `allow_managed_hooks_only` in `requirements.toml`.

---

## 2. SKILL.md (Tier 1, open spec — `name`, `description` required only)

Codex reads SKILL.md from `.agents/skills/`, not `.codex/skills/`. The required frontmatter is the agentskills.io baseline — `name` and `description` — same as every other tool.

**Codex-specific extras live in a SIDECAR `agents/openai.yaml`**, not in SKILL.md frontmatter. Treat the sidecar as additive metadata, not a deviation from the open spec.

**Sidecar fields:**
```yaml
# <skill>/agents/openai.yaml
interface:
  display_name: "My Skill"
  default_prompt: "Use this skill when..."
  icon_small: "icon-16.png"
  brand_color: "#FF6B00"
policy:
  allow_implicit_invocation: true
dependencies:
  tools:
    - bash
    - jq
```

Duplicate-name skills across scopes are NOT merged — both appear in selectors, repo-level wins for local workflows.

---

## 3. `.codex-plugin/plugin.json` (plugin manifest)

```json
{
  "name": "my-codex-plugin",
  "version": "1.0.0",
  "description": "Short summary",
  "skills": ["./skills/foo"],
  "mcpServers": ["./mcp/bar.toml"],
  "apps": ["./apps/baz.app.json"],
  "hooks": ["./hooks.json"],
  "interface": {
    "displayName": "My Plugin",
    "longDescription": "Detailed description for installer UI"
  }
}
```

**Required fields:** `name` (kebab-case), `version` (semver), `description`.
**Optional component paths** (all relative `./` paths only): `skills`, `mcpServers`, `apps`, `hooks`.
**Optional UI block:** `interface.{displayName, longDescription, defaultPrompt, …}`.

---

## 4. `.agents/plugins/marketplace.json` (marketplace manifest)

Three marketplace tiers exist in Codex:

- **Official Curated** — OpenAI-managed; self-serve publishing "coming soon" as of May 2026.
- **Repository** — `<repo-root>/.agents/plugins/marketplace.json` aggregates plugins shipped from that repo.
- **Personal** — `~/.agents/plugins/marketplace.json`.

Schema:

```json
{
  "name": "xiaolai",
  "interface": {
    "displayName": "xiaolai Marketplace"
  },
  "plugins": [
    {
      "name": "nlpm",
      "source": {
        "source": "github",
        "repo": "xiaolai/nlpm"
      },
      "policy": {
        "installation": "auto",
        "authentication": "none"
      },
      "category": "developer-tools",
      "interface": {
        "displayName": "nlpm"
      }
    }
  ]
}
```

Per-plugin `source` types: `"github"`, `"git"`, `"local"`.

---

## 5. `.codex/config.toml`

TOML — NOT JSON. Top-level sections nlpm cares about:

- `[features]` — feature flags. **Breaking change ~2026-04 (CLI 0.129+):** `[features].codex_hooks` was renamed to `[features].hooks`. Old key emits a deprecation warning. Flag config files that still use `codex_hooks`.
- `[mcp_servers.<id>]` — MCP server registrations. Fields: `command`, `args`, `cwd`, `url`, `enabled`, `enabled_tools`, `disabled_tools`, `env`, `startup_timeout_sec`.
- `[hooks.<event>]` — inline hook registrations (alternative to `.codex/hooks.json`).
- `[agents.<name>]` — subagent definitions (Codex multi-agent feature).
- `[profiles.*]` — named permission/model profiles.
- `[permissions.*]` — permission policy.

**No `.mcp.json` at repo root.** Codex does NOT read Claude's `.mcp.json` — MCP servers live inside `config.toml`. A bridge from `.mcp.json` → `.codex/config.toml` is a common port pattern (see `cc-suite:bridge-mcp` skill).

---

## 6. Hook events (Codex CLI)

Codex hooks mostly mirror Claude Code's event names — easier than the Antigravity divergence.

| Event | In Claude? | In Antigravity? | Notes |
|---|---|---|---|
| `SessionStart` | yes | yes | — |
| `UserPromptSubmit` | yes | — | — |
| `PreToolUse` | yes | — (different model) | — |
| `PostToolUse` | yes | — | — |
| `PermissionRequest` | yes | — | — |
| `PreCompact` | yes | — (uses `PreCompress`) | — |
| `PostCompact` | — | — | **Codex-only** (Claude has no PostCompact) |
| `SubagentStart` | — | — | **Codex-only** (added 2026-05-21 in 0.133.0) |
| `SubagentStop` | yes | — | — |
| `Stop` | yes | — | — |

**Absent in Codex (but present in Claude):** `Notification`, `SessionEnd`, `FileChanged`, `StopFailure`.

**Hook I/O contract:** Same JSON-on-stdin / JSON-on-stdout shape as Claude. Stdin: `session_id`, `cwd`, `hook_event_name`, `tool_name`, `tool_input`, etc. Stdout: `continue`, `systemMessage`, `stopReason`, `permissionDecision`. Exit codes: `0` = ok, `2` = block (stderr = reason), other = warning.

---

## 7. AGENTS.md (Codex's canonical memory file)

Codex reads `AGENTS.md` before every turn. Hierarchical: global `AGENTS.override.md` → global `AGENTS.md` → project AGENTS.md files (root-down, closer overrides earlier) → CWD AGENTS.md.

**Default cap:** 32 KiB per file (`project_doc_max_bytes` in config.toml).
**Fallback filenames:** Configurable via `project_doc_fallback_filenames` — this is the official hook for AGENTS.md / CLAUDE.md / GEMINI.md interop (set the array to include all three to make Codex read whichever exists).

**Body conventions** (not enforced, but common):
- `## Working agreements` — high-level decisions
- `## Repository expectations` — invariants
- `@file.md` imports are NOT supported (unlike Gemini's GEMINI.md hierarchy) — use file concatenation instead.

The nlpm pattern of `CLAUDE.md` → one line `@AGENTS.md` does NOT work for Codex (no @-import). Codex authors should put content directly in AGENTS.md and configure Claude Code's CLAUDE.md to import it instead.

---

## 8. Slash commands (deprecated)

Codex's old slash-command format (`~/.codex/prompts/<name>.md`) is **deprecated in favor of skills**. nlpm should NOT penalize their presence (legacy users still maintain them) but should emit an advisory recommending migration to `.agents/skills/`.

Placeholders if scoring legacy prompts: `$1..$9`, `$ARGUMENTS`, `$FILE`, `$TICKET_ID`, `$$`.

---

## 9. Recent breaking / material changes (last 6 months)

| Date | Version | Change |
|---|---|---|
| 2026-03-26 | — | Plugin marketplace **launched**. New artifact class. |
| ~2026-04 | 0.129.0 | `[features].codex_hooks` renamed to `[features].hooks` (deprecation warning) |
| 2026-05-18 | 0.131.0 | Plugin hooks enabled by default; legacy shell tools + built-in MCPs removed; `codex doctor` added |
| 2026-05-21 | 0.133.0 | Goals enabled by default; `SubagentStart` event observable by hooks |

Repos relying on the removed built-in MCPs will silently regress under 0.131+. nlpm should flag MCP configs that name MCPs no longer shipped natively.

---

## 10. Scope and uncertainty

This skill covers Codex CLI conventions. It does NOT cover:
- Universal SKILL.md spec → `nlpm:conventions`
- Penalty tables → `nlpm:scoring`
- Cross-component validation → invoked by `agents/checker.md`

**Uncertainties flagged (verify before scoring with confidence):**
- `child_agents_md` feature flag semantics — referenced in `agents_md.md` but not fully documented at developers.openai.com.
- `.app.json` schema for plugin `apps` field — referenced but no canonical doc found.
- Exact merge boundary between `~/.codex/AGENTS.md` and project AGENTS.md — docs say "global first, closer overrides" but the layer split is implied, not stated.
- OpenAI's contributor licensing policy for PRs into `openai/codex`-ecosystem repos — research needed before the auditor pipeline (PR-C) scales Codex contributions.
