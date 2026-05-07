# Re-Audit: kubesphere/kubesphere

**Date**: 2026-05-07  |  **Before**: `1681475` (89/100)  |  **After**: `00d94f4` (—)

## Summary

| Outcome | Count |
|---------|------:|
| fixed — our PR merged | 5 |
| fixed — upstream, not via our PR | 13 |
| newly introduced (regressions) | 10 |

## Original findings — verification

| # | File | Line | Rule | Pattern | Outcome | PR |
|---|------|------|------|---------|---------|----|
| 1 | `skills/kubesphere-devops-credentials/SKILL.md` | 111 | BUG-incorrect-api-example | `wrong-credential-type` | fixed — our PR merged | #6632 |
| 2 | `skills/kubesphere-fluid/SKILL.md` | 410 | BUG-yaml-syntax-error | `unclosed-string-literal` | fixed — our PR merged | #6633 |
| 3 | `skills/whizard-logging/SKILL.md` | 106 | BUG-incorrect-step-reference | `wrong-step-reference` | fixed — our PR merged | #6634 |
| 4 | `skills/kubesphere-devops-pipeline/SKILL.md` | 323 | BUG-broken-markdown | `unclosed-bold-marker` | fixed — our PR merged | #6635 |
| 5 | `skills/kubesphere-devops-overview/SKILL.md` | 92 | BUG-duplicate-section | `duplicate-content-block` | fixed — our PR merged | #6636 |
| 6 | `config/ks-core/charts/ks-crds/scripts/post-delete.sh` | 33 | SEC-xargs-shell-injection | `xargs-sh-c-interpolation` | fixed — upstream, not via our PR |  |
| 7 | `skills/whizard-telemetry/scripts/generate-config.sh` | 354 | SEC-plaintext-credential-output | `credential-echoed-to-stdout` | fixed — upstream, not via our PR |  |
| 8 | `skills/kubesphere-core/scripts/ks_api.py` | 28 | SEC-insecure-token-storage | `token-file-no-chmod` | fixed — upstream, not via our PR |  |
| 9 | `skills/kubesphere-multi-tenant-management/scripts/ks_api.py` | 28 | SEC-insecure-token-storage | `token-file-no-chmod` | fixed — upstream, not via our PR |  |
| 10 | `skills/kubesphere-devops-tenant/SKILL.md` | 130 | SEC-hardcoded-credential | `hardcoded-password-in-docs` | fixed — upstream, not via our PR |  |
| 11 | `skills/kubesphere-devops-argocd/SKILL.md` | 640 | R25 | `duplicate-content` | fixed — upstream, not via our PR |  |
| 12 | `skills/kubesphere-devops-pipeline/SKILL.md` | 1277 | R25 | `duplicate-content` | fixed — upstream, not via our PR |  |
| 13 | `skills/kubesphere-devops-overview/SKILL.md` | — | R25 | `duplicate-heading` | fixed — upstream, not via our PR |  |
| 14 | `skills/kubesphere-devops-tenant/SKILL.md` | 247 | R25 | `duplicate-header-in-example` | fixed — upstream, not via our PR |  |
| 15 | `skills/kubesphere-devops-tenant/SKILL.md` | 130 | R15 | `hardcoded-credential-in-docs` | fixed — upstream, not via our PR |  |
| 16 | `skills/kubesphere-volcano/SKILL.md` | 713 | R05 | `vague-quantifier` | fixed — upstream, not via our PR |  |
| 17 | `skills/kubesphere-multi-tenant-management/scripts/ks_api.py` | — | CC-duplicate-file | `verbatim-duplicate-script` | fixed — upstream, not via our PR |  |
| 18 | `skills/whizard-telemetry/SKILL.md` | — | CC-undocumented-dependency | `implicit-cross-extension-dependency` | fixed — upstream, not via our PR |  |

## Findings introduced since audit

These findings appear in the re-audit but were not in the original audit. They may be true regressions (new commits introduced them) or artifacts of scoring drift.

| # | File | Line | Rule | Pattern | Description |
|---|------|------|------|---------|-------------|
| 1 | `skills/kubesphere-volcano/SKILL.md` | 712 | R03 | `vague-quantifier-appropriate` | Vague quantifier 'appropriate' in 'Use appropriate queue' leaves queue selection criteria undefined |
| 2 | `skills/kubesphere-volcano/SKILL.md` | 792 | R03 | `vague-quantifier-appropriate` | Vague quantifier 'appropriate' in template application instruction provides no guidance on which fields to modify |
| 3 | `skills/kubesphere-devops-pipeline/SKILL.md` | 1247 | R03 | `vague-quantifier-appropriate` | Vague quantifier 'appropriate' in Common Mistakes table does not specify how to select the container image |
| 4 | `skills/kubesphere-devops-credentials/SKILL.md` | 544 | UNCLASSIFIED | `broken-markdown-table` | Blank line inside Common Mistakes table splits it into two fragments; second fragment renders as plain text, not a table |
| 5 | `skills/kubesphere-devops-overview/SKILL.md` | 277 | UNCLASSIFIED | `content-duplication` | Architecture table contains a duplicate separator row and four repeated data rows (copy-paste artifact) |
| 6 | `skills/kubesphere-devops-pipeline/SKILL.md` | 1276 | UNCLASSIFIED | `orphan-table` | Orphaned Common Mistakes table at lines 1276–1282 appears inside Debugging Steps without heading or context; duplicates earlier table |
| 7 | `skills/kubesphere-devops-tenant/SKILL.md` | 253 | UNCLASSIFIED | `malformed-code-block` | Orphaned shell flag at line 253 appears as a standalone line after the preceding curl command completes; likely a copy-paste artifact |
| 8 | `skills/kubesphere-devops-tenant/SKILL.md` | 50 | CC-broken-relative-path | `broken-relative-path` | References sibling skills via relative paths '../../core/kubesphere-core/SKILL.md' and '../kubesphere-devops-overview/SKILL.md'; flat layout at skills/kubesphere-devops-tenant/ would resolve these outside the repository root |
| 9 | `skills/frontend-forge-fi-operations/SKILL.md` | — | CC-broken-relative-path | `unverified-local-reference` | References local references/ subdirectory files (references/lifecycle.md, references/extension-management.md, references/inspection.md); existence of these files not confirmed |
| 10 | `skills/kubesphere-network-extension-operations/SKILL.md` | — | CC-broken-relative-path | `unverified-local-reference` | References local references/ subdirectory files (references/api_doc.md, references/values.yaml, etc.); existence of these files not confirmed |

