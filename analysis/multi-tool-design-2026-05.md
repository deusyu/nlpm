# Multi-Tool Design — nlpm Beyond Claude Code

**Status:** design proposal, 2026-05-25
**Context:** repo rename `nlpm-for-claude` → `nlpm`; expand audit surface to Claude Code + Codex CLI + Antigravity (which absorbs Gemini CLI on 2026-06-18).

This document records the six decisions taken to expand nlpm beyond Claude Code, the research that informed them, and the staged execution plan.

---

## Six decisions

### 1. Sub-skill split — split `nlpm:conventions` into four skills

```
skills/nlpm/
  conventions/SKILL.md              # universal: SKILL.md open spec, AGENTS.md, vague-quantifier R01, R51 vocab
  conventions-claude/SKILL.md       # Claude Code overlay: .claude/* paths, plugin.json, CLAUDE.md, hook events, LSP, monitors
  conventions-codex/SKILL.md        # Codex CLI overlay: .codex/* + .agents/* paths, config.toml, hook events, marketplace
  conventions-antigravity/SKILL.md  # Antigravity overlay: .gemini/* (legacy), .agent/* (new), gemini-extension.json, GEMINI.md
```

The scorer's Tier 1.5 already separates open-spec corpora from Claude-overlay corpora. Tier 2 expands to Tier 2-Claude / Tier 2-Codex / Tier 2-Antigravity, each loading its own overlay on top of the universal floor. Tier 1.5 loads only the universal skill.

**Rejected alternative:** keep one fat `nlpm:conventions` skill with per-tool subsections. Cleaner to maintain but every audit loads every tool's knowledge — a Tier-1.5 audit of `google/skills` would pay for ~3× the tokens it needs. Sub-skill split makes the retrieval surface match the audit shape.

### 2. Repo rename — `nlpm` (no org change, no namespace prefix)

`github.com/xiaolai/nlpm-for-claude` → `github.com/xiaolai/nlpm`. Plugin name in `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` stays `nlpm`. Marketplace entries in both Claude and Codex marketplaces update to point to the new repo URL.

**Rejected alternatives:**
- `nlpm-multi` / `nlpm-multitool`: redundant after the rename — multi-tool support becomes the default state, not a distinguishing feature.
- Move under a new org: `nlpm` doesn't have collisions worth working around; the personal-account path is fine.

### 3. Antigravity scope — staged adoption

Antigravity 2.0 launched at Google I/O 2026 (2026-05-19), six days before this document. The directory layout is still in flux (two authoritative research passes disagreed on `<workspace>/.agent/skills/` singular vs `.agents/skills/` plural). Hook and plugin specs reference "not yet 1:1 parity" with Gemini CLI without enumerating gaps.

Auditing against an unsettled spec produces wrong findings — same anti-pattern as the prior `BUG-broken-reference` low-landing-rate suppression case (`rule-health.py`).

**Staged plan:**
- **Phase A (PR-A, now):** Tier 2-Antigravity detection — repo-shape classifier recognizes `.gemini/`, `.agent/`, `gemini-extension.json`, `GEMINI.md`. Score the universal floor (SKILL.md open spec + AGENTS.md if present). Do NOT score Antigravity-specific hook/plugin artifacts yet.
- **Phase B (PR-B+, after Antigravity 2.1 or equivalent stabilization):** Add Antigravity-specific penalty tables. Trigger: official Antigravity directory-layout spec published, OR Antigravity overtakes Gemini CLI in real-world repo count (whichever comes first).

This preserves the discover→audit→learn loop on Antigravity repos without filing PRs against unstable conventions.

### 4. Hook events — per-tool tables, no translation

The three event vocabularies are not 1:1-mappable:

| Position | Claude Code | Codex CLI | Antigravity (Gemini lineage) |
|---|---|---|---|
| Session boundary | `SessionStart`, `SessionEnd` | `SessionStart` (no end) | `SessionStart`, `SessionEnd` |
| User input | `UserPromptSubmit` | `UserPromptSubmit` | — |
| Pre-tool | `PreToolUse` | `PreToolUse` | `BeforeTool`, `BeforeToolSelection` (split) |
| Post-tool | `PostToolUse` | `PostToolUse` | `AfterTool` |
| Model | — | — | `BeforeModel`, `AfterModel` |
| Agent boundary | — | `SubagentStart`, `SubagentStop` | `BeforeAgent`, `AfterAgent` |
| Compaction | `PreCompact` | `PreCompact`, `PostCompact` | `PreCompress` |
| Permission | `PermissionRequest` | `PermissionRequest` | — |
| Stop | `Stop`, `StopFailure`, `SubagentStop` | `Stop`, `SubagentStop` | — |
| Notification | `Notification`, `FileChanged` | — | `Notification` |

Gemini/Antigravity's `BeforeModel` vs `BeforeToolSelection` distinction has no analog in Claude or Codex — both happen during a Claude/Codex `PreToolUse`. Forcing a universal taxonomy would either collapse the distinction (losing audit precision) or invent shim events that don't exist (false complexity).

**Decision:** `nlpm:scoring` ships three Hooks penalty tables, one per tool, plus a small "shared event names" reference for the events that do appear in multiple tools. No universal-event-name layer.

**Rejected alternative:** Build a `nlpm:hooks` universal taxonomy with canonical buckets (`pre_tool`, `post_tool`, `session_start`, etc.). Would enable cross-tool rules like "every plugin should define at least one `pre_tool` hook" — but those rules don't survive the lifecycle-model divergence and would produce noise.

### 5. AGENTS.md as canonical universal memory

- **Codex CLI:** reads `AGENTS.md` natively; default 32 KiB cap; hierarchical (root → cwd, closer overrides earlier); `~/.codex/AGENTS.override.md` for personal overlays.
- **Antigravity (Gemini lineage):** reads `GEMINI.md` natively; `context.fileName` setting accepts an array — set to `["AGENTS.md", "GEMINI.md"]` to read both. Hierarchical + `@file.md` imports.
- **Claude Code:** reads `CLAUDE.md` natively; supports `@AGENTS.md` import syntax (this is how nlpm itself already works — `CLAUDE.md` is one line: `@AGENTS.md`).

AGENTS.md is the only one of the three that all three tools can be made to read with no per-tool fork. Promoting it as the canonical universal memory file:

- nlpm's own conventions skill recommends `AGENTS.md` as the primary instructions file.
- `CLAUDE.md` and `GEMINI.md` become `@AGENTS.md` import shims when the project targets multiple tools.
- The auditor (PR-C) recognizes any of the three but prefers `AGENTS.md` presence as the marker of a tool-agnostic project.

**Rejected alternative:** Treat all three as equal canonical paths and let projects pick. Produces ecosystem fragmentation where Claude-only projects use CLAUDE.md, Codex-only projects use AGENTS.md, multi-tool projects use whatever the author favored. AGENTS.md as canonical gives a default that costs Claude Code authors nothing (one-line shim) and costs Codex authors nothing (it's already native).

### 6. Gemini CLI → Antigravity — one overlay, label legacy paths inside

Gemini CLI sunsets 2026-06-18 (24 days from this doc). Both reports confirmed: artifact shapes survive the transition. Differences are CLI name, directory naming, and the "extensions" → "Antigravity plugins" rename.

**Decision:** one `nlpm:conventions-antigravity` skill that documents both:

- **Legacy (until 2026-06-18 sunset):** `.gemini/`, `gemini-extension.json`, `GEMINI.md`, `gemini extensions install`, `~/.gemini/skills/`
- **New:** `<workspace>/.agent/skills/` (Antigravity-specific singular) AND `.agents/skills/` (cross-tool alias, also used by Codex), `~/.gemini/antigravity/skills/` (transitional global path), `npx skills add` (cross-tool installer)

The skill's scope note explicitly flags the transition window and the directory-layout uncertainty. PR-B will update once Antigravity publishes a stable directory spec.

**Rejected alternative:** Two overlays (`conventions-gemini` + `conventions-antigravity`) until 2026-06-18, then delete the Gemini one. Adds maintenance burden for a 24-day window; the two would be ~80% identical anyway.

---

## Staged execution plan

### PR-A (this PR) — Foundation

- **NEW:** `analysis/multi-tool-design-2026-05.md` (this document)
- **MODIFIED:** `agents/scorer.md` — extend Tier 2 into Tier 2-Claude / Tier 2-Codex / Tier 2-Antigravity (detection rules; overlay loading is forward-referenced to PR-B's sub-skills)
- **MODIFIED:** `skills/nlpm/scoring/SKILL.md` — Scope Note cross-references this design doc; flags PR-B's coming changes

Scope discipline: PR-A makes no content move. Existing audits continue to score Claude-shaped repos identically. The new Tier 2-X classifiers detect their respective ecosystems but fall back to the universal floor when their overlay skill doesn't exist yet — equivalent to Tier 1.5 behavior until PR-B.

### PR-B — Content migration + scoring tables

- **NEW:** `skills/nlpm/conventions-claude/SKILL.md` (move Claude-specific content out of `conventions/SKILL.md`)
- **NEW:** `skills/nlpm/conventions-codex/SKILL.md` (write from Codex research report)
- **NEW:** `skills/nlpm/conventions-antigravity/SKILL.md` (write from Antigravity + Gemini research reports; flag uncertainty)
- **MODIFIED:** `skills/nlpm/conventions/SKILL.md` — slim down to universal floor (SKILL.md open spec, AGENTS.md conventions, vocabulary registry, vague-quantifier list)
- **MODIFIED:** `skills/nlpm/scoring/SKILL.md` — split Hooks table into three per-tool tables; add new artifact-type rows for `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `gemini-extension.json`, `agents/openai.yaml` sidecar, LSP, Monitors, and new Claude SKILL.md fields (`context`, `agent`, `paths`, `hooks`, etc.)
- **MODIFIED:** `agents/scorer.md` — Tier 2-X each loads its matching overlay; remove the "forward-reference to overlay not-yet-existing" stub from PR-A
- **MODIFIED:** `agents/checker.md` — cross-component references need to recognize Codex's `.agents/plugins/marketplace.json` and Antigravity's extension manifests
- **MODIFIED:** `bin/nlpm-check` — universal-floor validators only (the deterministic core); per-tool validators stay LLM-judged in scorer

### PR-C — Auditor pipeline + repo rename

- **MODIFIED:** `auditor-discover.yml` — three parallel `gh search repos` queries: Claude-shaped, Codex-shaped, Antigravity-shaped. Single registry, `repo_type` field added.
- **MODIFIED:** `auditor/scripts/vendor_default_filter.py` — add OpenAI-CLA check (Codex contributions need their own contributor agreement — research before merging).
- **MODIFIED:** `agents/security-scanner.md` — recognize Codex MCP TOML format and Antigravity hook events as executable surfaces.
- **MODIFIED:** `auditor/exemplars/` — exemplar frontmatter gains a `tool:` field (claude / codex / antigravity / open-spec). `build-exemplar-gallery.py` adds a per-tool view.
- **NEW:** Per-tool rule-health metrics in `auditor/scripts/rule-health.py` — track precision per (rule, tool) instead of per rule.
- **MODIFIED:** `.claude-plugin/plugin.json` + `.codex-plugin/plugin.json` — bump major version; update `name` if needed.
- **MODIFIED:** central marketplace (`xiaolai/claude-plugin-marketplace`) — update `nlpm` entry to new repo URL in both `.claude-plugin/marketplace.json` and `.agents/plugins/marketplace.json`.
- **MODIFIED:** README files, site (`site/index.md`, `site/install.md`), `bin/nlpm-build-reference-md` output paths.
- **External:** GitHub repo rename (preserves stars, issues, PRs via auto-redirect); update remote references in local clones.

### What stays Claude-Code-specific permanently

A few nlpm artifacts are slash-command surfaces that only run inside Claude Code:

- `commands/*.md` — `/nlpm:*` slash commands. These are Claude Code commands; the equivalent Codex/Antigravity surface uses skills.
- `hooks/hooks.json` — Claude Code hook config.
- The `auditor/` GitHub Actions workflows — they invoke `claude-code-action`. Codex has its own action surface; Antigravity has the SDK + Managed Agents.

These remain Claude-only artifacts of the nlpm plugin itself; the rules nlpm enforces become multi-tool, but the delivery vehicle for the slash commands is still a Claude Code plugin. The `bin/nlpm-check` standalone binary (already pure Python stdlib) covers the cross-tool author surface for users not running Claude Code.

---

## Open uncertainties

These need verification before PR-B lands:

1. **Antigravity directory layout** — `.agent/skills/` (Antigravity report) vs `.agents/skills/` (Gemini report cross-tool alias). Resolution: probably both are true (Antigravity-specific singular + cross-tool plural alias) but the codelab is the only authoritative source and it pre-dates Antigravity 2.0 by months.
2. **`npx skills` verb** — `add` (Antigravity codelab) vs `install` (Cloud Next announcement). Both terms appear; repo page says `add`. PR-B should cite `add` and note `install` as a legacy term.
3. **Codex OpenAI CLA policy** — does contributing to `openai/codex`-adjacent repos require a signed CLA the way Google orgs do? The contribute pipeline's policy gates need to know before PR-C scales discovery to Codex-shaped repos.
4. **Antigravity `child_agents_md` feature flag** — referenced in Codex's `agents_md.md` but semantics not fully documented. Codex-side concern, not Antigravity, but the AGENTS.md hierarchy story interacts.
5. **Claude Code `.lsp.json` and `monitors/monitors.json`** — schemas not researched in this round. PR-B adds nlpm:scoring rows for both but the schemas need their own pass.

These are recorded here so the next research turn knows where to dig.

---

## Post-merge status (2026-05-26)

What actually shipped vs. what was deferred, after PR-A through the Codex layout landed.

### Shipped

- **PR-A / PR-B / PR-C**: foundation, conventions split, v1.0.0 + rename. All merged.
- **Doc-staleness sweep** (PRs #279/#280/#281): top-level docs, authoring skills, rulebook labels caught up to multi-tool.
- **Codex layout** (PR #282): `.codex-plugin/plugin.json` + `codex/` tree of **17 reference-knowledge skills**. Reference-only by design — nlpm's command→agent `Task()` orchestration has no in-skill Codex equivalent, so the 23 command/agent skills the bootstrap generated were pruned. Added to the central Codex marketplace.
- **Gemini AGENTS.md wiring**: verified the `@`-import shim works; shipped `.gemini/settings.json` with `context.fileName: ["AGENTS.md"]` as the robust path. nlpm dogfoods it.
- **OpenAI CLA / policy guard**: `vendor_default_filter.py` now hard-denies `openai/codex` + `openai/codex-action` (repo-specific). See research findings below.

### Codex contribution policy (researched 2026-05-26)

- **`openai/codex` auto-closes unsolicited external PRs** (14-day stale auto-close via `close-stale-contributor-prs.yml`). This is the dominant blocker — bigger than the CLA. nlpm's PRs are unsolicited by definition, so the vendor filter denies these repos at discovery.
- **CLA**: `openai/codex` + `openai/codex-action` require a signed CLA. Status check is named **`cla`** (exact match `^cla$` — narrower than Google's `^cla(/|$)`). Comment-based signing (a human posts "I have read the CLA Document…"), NOT commit-author-based like Google. Allowlist: `codex, dependabot, github-actions[bot]` — `claude[bot]` is NOT allowlisted.
- **Not org-wide**: only the Codex repos have a CLA. `openai/openai-python` etc. have none, and aren't NL-artifact repos anyway. The guard is repo-specific, not owner-wide.
- **Third-party Codex repos**: no CLA, normal contribution. Treat like any other target.
- **For the track workflow** (when Codex contribution eventually scales): detect CLA-block via a `statusCheckRollup` check named exactly `cla` with conclusion FAILURE — the OpenAI analog of the existing `cla/google` detection.

### Deferred as premature (NOT built — would operate on an empty corpus)

The remaining "PR-D" auditor-pipeline items build machinery for a multi-tool *audit corpus that does not exist yet*. Codex CLI plugins are ~2 months old (launched 2026-03-26); Antigravity is days old (2026-05-19). Building these now yields near-empty results and speculative complexity:

- **`auditor-discover.yml` Codex/Antigravity queries + `repo_type` field** — `gh search` for `.codex-plugin/plugin.json` / `.agents/skills/` repos with 500+ stars returns ~nothing today. Build when the corpus reaches a threshold (e.g., ≥10 discoverable Codex-shaped repos).
- **Per-`(rule, tool)` metrics in `rule-health.py`** — every audit to date is Claude-shaped, so per-tool precision is all-Claude. No-op until non-Claude audits land (which requires discovery first).
- **Exemplar `tool:` frontmatter field + per-tool gallery** — all 65 exemplars are Claude. The field would be uniformly `claude` until Codex/Antigravity repos get audited and exemplar-published.

Trigger to build: when discovery surfaces a non-trivial count of Codex- or Antigravity-shaped repos. Until then, the multi-tool *rubric* is ready (it scores any tool's artifacts on demand); the multi-tool *auditing pipeline* waits for its corpus.
