# NLPM Re-Audit: aaron-he-zhu/seo-geo-claude-skills

**Date**: 2026-04-24  |  **Artifacts**: 38  |  **Strategy**: batched
**NL Score**: 95/100
**Bugs**: 1  |  **Quality Issues**: 27

## NL Score Summary

| File | Type | Score | Top Issue |
|------|------|-------|-----------|
| hooks/hooks.json | Hooks | 85 | Unrecognized `FileChanged` event (R27) |
| commands/audit-domain.md | Command | 85 | No empty-input handling; no error paths |
| commands/audit-page.md | Command | 85 | No empty-input handling; no error paths |
| commands/check-technical.md | Command | 85 | No empty-input handling; no error paths |
| commands/contract-lint.md | Command | 85 | No numbered steps; no error paths |
| commands/generate-schema.md | Command | 85 | No empty-input handling; no error paths |
| commands/keyword-research.md | Command | 85 | No empty-input handling; no error paths |
| commands/optimize-meta.md | Command | 85 | No empty-input handling; no error paths |
| commands/p2-review.md | Command | 85 | No numbered steps; no error paths |
| commands/report.md | Command | 85 | No empty-input handling; no error paths |
| commands/setup-alert.md | Command | 85 | No empty-input handling; no error paths |
| commands/write-content.md | Command | 85 | No empty-input handling; no error paths |
| CLAUDE.md | CLAUDE.md | 95 | No test command (R34) |
| commands/geo-drift-check.md | Command | 95 | No error paths (R17) |
| commands/validate-library.md | Command | 95 | No error paths (R17) |
| commands/wiki-lint.md | Command | 95 | No error paths (R17) |
| monitor/alert-manager/SKILL.md | Skill | 98 | Vague quantifier "relevant" (R01) |
| .claude-plugin/plugin.json | plugin.json | 100 | — |
| build/geo-content-optimizer/SKILL.md | Skill | 100 | — |
| build/meta-tags-optimizer/SKILL.md | Skill | 100 | — |
| build/schema-markup-generator/SKILL.md | Skill | 100 | — |
| build/seo-content-writer/SKILL.md | Skill | 100 | — |
| commands/sync-versions.md | Command | 100 | — |
| cross-cutting/content-quality-auditor/SKILL.md | Skill | 100 | — |
| cross-cutting/domain-authority-auditor/SKILL.md | Skill | 100 | — |
| cross-cutting/entity-optimizer/SKILL.md | Skill | 100 | — |
| cross-cutting/memory-management/SKILL.md | Skill | 100 | — |
| monitor/backlink-analyzer/SKILL.md | Skill | 100 | — |
| monitor/performance-reporter/SKILL.md | Skill | 100 | — |
| monitor/rank-tracker/SKILL.md | Skill | 100 | — |
| optimize/content-refresher/SKILL.md | Skill | 100 | — |
| optimize/internal-linking-optimizer/SKILL.md | Skill | 100 | — |
| optimize/on-page-seo-auditor/SKILL.md | Skill | 100 | — |
| optimize/technical-seo-checker/SKILL.md | Skill | 100 | — |
| research/competitor-analysis/SKILL.md | Skill | 100 | — |
| research/content-gap-analysis/SKILL.md | Skill | 100 | — |
| research/keyword-research/SKILL.md | Skill | 100 | — |
| research/serp-analysis/SKILL.md | Skill | 100 | — |

## Bugs (PR-worthy)

| # | File | Issue | Impact |
|---|------|-------|--------|
| 1 | hooks/hooks.json | `FileChanged` is not a recognized hook event per conventions §7; the hot-cache line-count monitoring hook will silently never fire | Hot-cache overflow warnings are inoperative |

## Quality Issues (informational)

| # | File | Issue | Penalty |
|---|------|-------|---------|
| 1 | CLAUDE.md | No test command documented (R34) | -5 |
| 2 | commands/setup-alert.md | No empty-input handling when required `alert_type` is omitted (R15) | -10 |
| 3 | commands/setup-alert.md | No error paths for unrecognized alert type or bad threshold (R17) | -5 |
| 4 | commands/keyword-research.md | No empty-input handling when required `seed` is omitted (R15) | -10 |
| 5 | commands/keyword-research.md | No error paths for bad data (R17) | -5 |
| 6 | commands/validate-library.md | No error paths for unreadable SKILL.md or failed shasum check (R17) | -5 |
| 7 | commands/report.md | Both `domain` and `project` are optional but no guidance when neither is supplied (R15) | -10 |
| 8 | commands/report.md | No error paths for missing wiki index or unavailable data (R17) | -5 |
| 9 | commands/write-content.md | No empty-input handling when required `topic` or `keyword` is omitted (R15) | -10 |
| 10 | commands/write-content.md | No error paths (R17) | -5 |
| 11 | commands/geo-drift-check.md | No error paths for missing `memory/geo-feedback/` or unresolvable records (R17) | -5 |
| 12 | commands/check-technical.md | No empty-input handling when required `target` is omitted (R15) | -10 |
| 13 | commands/check-technical.md | No error paths for unreachable URL (R17) | -5 |
| 14 | commands/generate-schema.md | No empty-input handling when required `schema_type` is omitted (R15) | -10 |
| 15 | commands/generate-schema.md | No error paths for unavailable source URL (R17) | -5 |
| 16 | commands/audit-domain.md | No empty-input handling when required `domain` is omitted (R15) | -10 |
| 17 | commands/audit-domain.md | No error paths (R17) | -5 |
| 18 | commands/audit-page.md | No empty-input handling when required `source` is omitted (R15) | -10 |
| 19 | commands/audit-page.md | No error paths for inaccessible URL (R17) | -5 |
| 20 | commands/optimize-meta.md | No empty-input handling when required `source` is omitted (R15) | -10 |
| 21 | commands/optimize-meta.md | No error paths (R17) | -5 |
| 22 | commands/p2-review.md | Multi-step evaluation procedure uses bullets, not numbered steps (R14) | -10 |
| 23 | commands/p2-review.md | No error paths for missing `memory/audits/` directory (R17) | -5 |
| 24 | commands/contract-lint.md | Multi-step check sections use prose headers, not numbered steps (R14) | -10 |
| 25 | commands/contract-lint.md | No error paths for missing auditor SKILL.md or Runbook (R17) | -5 |
| 26 | commands/wiki-lint.md | No error paths for missing `memory/wiki/` or empty memory store (R17) | -5 |
| 27 | monitor/alert-manager/SKILL.md | Vague quantifier "relevant" in "For each relevant category" (R01) | -2 |

## Cross-Component

**hooks/hooks.json — `FileChanged` event not recognized**: `FileChanged` does not appear in the valid hook event list in `skills/nlpm/conventions/SKILL.md §7`. The hook body intended to monitor `memory/hot-cache.md` line count will silently never execute. Fix: rename to a supported lifecycle event or remove the stale entry.

**hooks/hooks.json — SessionStart matcher `"startup"` instead of `""`**: The `SessionStart` hook block uses matcher `"startup"` rather than the conventional empty-string (match all). For lifecycle events, the matcher field is evaluated against the tool name, which is undefined at session start. This may silently suppress all five SessionStart prompts. Recommend setting `"matcher": ""`.

No broken partial references, orphaned skills, or component contradictions found. All 15 commands map to documented skills; all 20 skills are listed in plugin.json; hooks reference no external scripts.

## Recommendation

All 20 skills score 98–100 and are production-ready; the single bug (invalid `FileChanged` hook event) should be patched since it silently disables hot-cache overflow warnings, and the 11 commands missing empty-input handlers are a consistent gap that could be closed in one pass by adding a short "if no argument provided" clause to each workflow.
