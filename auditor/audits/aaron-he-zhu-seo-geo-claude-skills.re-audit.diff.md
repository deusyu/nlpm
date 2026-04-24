# Re-Audit: aaron-he-zhu/seo-geo-claude-skills

**Date**: 2026-04-24  |  **Before**: `unknown` (91/100)  |  **After**: `dc77e77` (95/100)

## Summary

| Outcome | Count |
|---------|------:|
| fixed — upstream, not via our PR | 35 |
| newly introduced (regressions) | 28 |

## Original findings — verification

| # | File | Line | Rule | Pattern | Outcome | PR |
|---|------|------|------|---------|---------|----|
| 1 | `commands/contract-lint.md` | — | BUG-undeclared-tool | `missing-allowed-tools` | fixed — upstream, not via our PR |  |
| 2 | `commands/wiki-lint.md` | — | BUG-missing-steps | `missing-step-ordering` | fixed — upstream, not via our PR |  |
| 3 | `.claude-plugin/plugin.json` | — | CC-version-drift | `version-drift` | fixed — upstream, not via our PR |  |
| 4 | `commands/audit-domain.md` | — | BUG-undeclared-tool | `missing-allowed-tools` | fixed — upstream, not via our PR |  |
| 5 | `commands/keyword-research.md` | — | BUG-undeclared-tool | `missing-allowed-tools` | fixed — upstream, not via our PR |  |
| 6 | `commands/optimize-meta.md` | — | BUG-undeclared-tool | `missing-allowed-tools` | fixed — upstream, not via our PR |  |
| 7 | `commands/p2-review.md` | — | BUG-undeclared-tool | `missing-allowed-tools` | fixed — upstream, not via our PR |  |
| 8 | `commands/report.md` | — | BUG-undeclared-tool | `missing-allowed-tools` | fixed — upstream, not via our PR |  |
| 9 | `commands/setup-alert.md` | — | BUG-undeclared-tool | `missing-allowed-tools` | fixed — upstream, not via our PR |  |
| 10 | `commands/write-content.md` | — | BUG-undeclared-tool | `missing-allowed-tools` | fixed — upstream, not via our PR |  |
| 11 | `SKILL.md` | — | R01 | `vague-quantifiers` | fixed — upstream, not via our PR |  |
| 12 | `commands/audit-domain.md` | — | UNCLASSIFIED | `missing-argument-hint-field` | fixed — upstream, not via our PR |  |
| 13 | `commands/optimize-meta.md` | — | UNCLASSIFIED | `missing-argument-hint-field` | fixed — upstream, not via our PR |  |
| 14 | `commands/wiki-lint.md` | — | UNCLASSIFIED | `missing-argument-hint-field` | fixed — upstream, not via our PR |  |
| 15 | `commands/p2-review.md` | — | UNCLASSIFIED | `missing-argument-hint-field` | fixed — upstream, not via our PR |  |
| 16 | `hooks/hooks.json` | — | UNCLASSIFIED | `stop-hook-auto-appends-critical-veto-ite` | fixed — upstream, not via our PR |  |
| 17 | `commands/geo-drift-check.md` | — | UNCLASSIFIED | `experimental-v9-0-label-in-claude-md-but` | fixed — upstream, not via our PR |  |
| 18 | `CLAUDE.md` | — | BUG-broken-reference | `broken-reference` | fixed — upstream, not via our PR |  |
| 19 | `cross-cutting/content-quality-auditor/SKILL.md` | — | UNCLASSIFIED | `both-auditor-class-skills-carry-the-iden` | fixed — upstream, not via our PR |  |
| 20 | `cross-cutting/domain-authority-auditor/SKILL.md` | — | UNCLASSIFIED | `both-auditor-class-skills-carry-the-iden` | fixed — upstream, not via our PR |  |
| 21 | `SKILL.md` | — | UNCLASSIFIED | `metadata-geo-relevance-values-are-hardco` | fixed — upstream, not via our PR |  |
| 22 | `research/competitor-analysis/SKILL.md` | — | UNCLASSIFIED | `include-a-scraping-legality-note-verify` | fixed — upstream, not via our PR |  |
| 23 | `optimize/internal-linking-optimizer/SKILL.md` | — | UNCLASSIFIED | `include-a-scraping-legality-note-verify` | fixed — upstream, not via our PR |  |
| 24 | `hooks/hooks.json` | — | UNCLASSIFIED | `the-filechanged-hook-matcher-hot-cache-m` | fixed — upstream, not via our PR |  |
| 25 | `commands/report.md` | — | UNCLASSIFIED | `cross-project-mode-is-described-but-the` | fixed — upstream, not via our PR |  |
| 26 | `build/seo-content-writer/SKILL.md` | — | UNCLASSIFIED | `banned-vocabulary-list-crucial-robust-le` | fixed — upstream, not via our PR |  |
| 27 | `monitor/performance-reporter/SKILL.md` | — | UNCLASSIFIED | `11-step-workflow-integrates-core-eeat-an` | fixed — upstream, not via our PR |  |
| 28 | `cross-cutting/memory-management/SKILL.md` | — | UNCLASSIFIED | `gdpr-art-17-deletion-flow-is-documented` | fixed — upstream, not via our PR |  |
| 29 | `All research skills` | — | UNCLASSIFIED | `the-next-best-skill-section-uses-markdow` | fixed — upstream, not via our PR |  |
| 30 | `commands/p2-review.md` | — | UNCLASSIFIED | `tombstone-rule-states-tombstone-review-2` | fixed — upstream, not via our PR |  |
| 31 | `commands/sync-versions.md` | — | UNCLASSIFIED | `step-5-says-to-verify-all-3-cross-agent` | fixed — upstream, not via our PR |  |
| 32 | `optimize/technical-seo-checker/SKILL.md` | — | UNCLASSIFIED | `llm-crawler-handling-section-names-speci` | fixed — upstream, not via our PR |  |
| 33 | `build/schema-markup-generator/SKILL.md` | — | UNCLASSIFIED | `ftc-disclosure-note-for-aggregaterating` | fixed — upstream, not via our PR |  |
| 34 | `SKILL.md` | — | UNCLASSIFIED | `save-results-section-is-identical-across` | fixed — upstream, not via our PR |  |
| 35 | `hooks/hooks.json` | 36 | UNCLASSIFIED | `userpromptsubmit-hook-line-36-fires-on-e` | fixed — upstream, not via our PR |  |

## Findings introduced since audit

These findings appear in the re-audit but were not in the original audit. They may be true regressions (new commits introduced them) or artifacts of scoring drift.

| # | File | Line | Rule | Pattern | Description |
|---|------|------|------|---------|-------------|
| 1 | `hooks/hooks.json` | — | R27 | `invalid-hook-event` | FileChanged is not a recognized hook event per conventions §7; the hot-cache line-count monitoring hook will silently never fire. |
| 2 | `CLAUDE.md` | — | R34 | `missing-test-command` | CLAUDE.md has no section documenting how to run tests or validation checks for the library. |
| 3 | `commands/setup-alert.md` | — | R15 | `missing-empty-input-handling` | Required parameter alert_type has no empty-input handler; invoking /seo:setup-alert with no argument produces undefined behavior. |
| 4 | `commands/setup-alert.md` | — | R17 | `missing-error-paths` | No error guidance for unrecognized alert type or non-numeric threshold value. |
| 5 | `commands/keyword-research.md` | — | R15 | `missing-empty-input-handling` | Required parameter seed has no empty-input handler; invoking /seo:keyword-research with no argument produces undefined behavior. |
| 6 | `commands/keyword-research.md` | — | R17 | `missing-error-paths` | No error handling for bad or empty competitor domain input. |
| 7 | `commands/validate-library.md` | — | R17 | `missing-error-paths` | No error paths for unreadable SKILL.md files or failed shasum comparison. |
| 8 | `commands/report.md` | — | R15 | `missing-empty-input-handling` | Both domain and project parameters are optional with no guidance when neither is supplied. |
| 9 | `commands/report.md` | — | R17 | `missing-error-paths` | No error handling when memory/wiki/<slug>/index.md is missing for a named project. |
| 10 | `commands/write-content.md` | — | R15 | `missing-empty-input-handling` | Required parameters topic and keyword have no empty-input handler. |
| 11 | `commands/write-content.md` | — | R17 | `missing-error-paths` | No error paths documented in the workflow body. |
| 12 | `commands/geo-drift-check.md` | — | R17 | `missing-error-paths` | No error handling for missing memory/geo-feedback/ directory or records with no prior queries. |
| 13 | `commands/check-technical.md` | — | R15 | `missing-empty-input-handling` | Required parameter target has no empty-input handler. |
| 14 | `commands/check-technical.md` | — | R17 | `missing-error-paths` | No error handling for unreachable URL or WebFetch failure. |
| 15 | `commands/generate-schema.md` | — | R15 | `missing-empty-input-handling` | Required parameter schema_type has no empty-input handler. |
| 16 | `commands/generate-schema.md` | — | R17 | `missing-error-paths` | No error handling for unavailable source URL or malformed content input. |
| 17 | `commands/audit-domain.md` | — | R15 | `missing-empty-input-handling` | Required parameter domain has no empty-input handler. |
| 18 | `commands/audit-domain.md` | — | R17 | `missing-error-paths` | No error paths documented in the workflow body. |
| 19 | `commands/audit-page.md` | — | R15 | `missing-empty-input-handling` | Required parameter source has no empty-input handler. |
| 20 | `commands/audit-page.md` | — | R17 | `missing-error-paths` | No error handling for inaccessible URL passed to WebFetch. |
| 21 | `commands/optimize-meta.md` | — | R15 | `missing-empty-input-handling` | Required parameter source has no empty-input handler. |
| 22 | `commands/optimize-meta.md` | — | R17 | `missing-error-paths` | No error paths documented in the workflow body. |
| 23 | `commands/p2-review.md` | — | R14 | `missing-numbered-steps` | Multi-step evaluation procedure is written as a bullet list rather than numbered steps. |
| 24 | `commands/p2-review.md` | — | R17 | `missing-error-paths` | No error handling for missing memory/audits/ directory or no audits found. |
| 25 | `commands/contract-lint.md` | — | R14 | `missing-numbered-steps` | Multi-check workflow is organized as prose subsections rather than numbered steps. |
| 26 | `commands/contract-lint.md` | — | R17 | `missing-error-paths` | No error handling for missing auditor SKILL.md files or absent references/auditor-runbook.md. |
| 27 | `commands/wiki-lint.md` | — | R17 | `missing-error-paths` | No error handling for missing memory/wiki/ directory or empty memory store. |
| 28 | `monitor/alert-manager/SKILL.md` | 145 | R01 | `vague-quantifier-relevant` | Vague quantifier 'relevant' used in 'For each relevant category' without measurable selection criteria. |

