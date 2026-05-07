# NLPM Re-Audit: kubesphere/kubesphere

**Date**: 2026-05-07  |  **Artifacts**: 26  |  **Strategy**: batched
**NL Score**: 99.8/100
**Bugs**: 0  |  **Quality Issues**: 7

## NL Score Summary

| File | Type | Score | Top Issue |
|------|------|-------|-----------|
| skills/kubesphere-volcano/SKILL.md | skill | 96 | Vague quantifier "appropriate" (×2) |
| skills/kubesphere-devops-pipeline/SKILL.md | skill | 98 | Vague quantifier "appropriate" |
| skills/frontend-forge-fi-operations/SKILL.md | skill | 100 | — |
| skills/frontend-integration-yaml/SKILL.md | skill | 100 | — |
| skills/kubesphere-cluster-management/SKILL.md | skill | 100 | — |
| skills/kubesphere-core/SKILL.md | skill | 100 | — |
| skills/kubesphere-devops-argocd/SKILL.md | skill | 100 | — |
| skills/kubesphere-devops-credentials/SKILL.md | skill | 100 | Broken Markdown table (informational) |
| skills/kubesphere-devops-jenkins/SKILL.md | skill | 100 | — |
| skills/kubesphere-devops-overview/SKILL.md | skill | 100 | Duplicate table rows (informational) |
| skills/kubesphere-devops-tenant/SKILL.md | skill | 100 | Orphaned shell flag in code block (informational) |
| skills/kubesphere-extension-management/SKILL.md | skill | 100 | — |
| skills/kubesphere-fluid/SKILL.md | skill | 100 | — |
| skills/kubesphere-multi-tenant-management/SKILL.md | skill | 100 | — |
| skills/kubesphere-network-extension-operations/SKILL.md | skill | 100 | — |
| skills/kubesphere-openkruise/SKILL.md | skill | 100 | — |
| skills/nodegroup/SKILL.md | skill | 100 | — |
| skills/opensearch/SKILL.md | skill | 100 | — |
| skills/vector/SKILL.md | skill | 100 | — |
| skills/whizard-auditing/SKILL.md | skill | 100 | — |
| skills/whizard-events/SKILL.md | skill | 100 | — |
| skills/whizard-logging/SKILL.md | skill | 100 | — |
| skills/whizard-notification/SKILL.md | skill | 100 | — |
| skills/whizard-telemetry/SKILL.md | skill | 100 | — |
| skills/whizard-telemetry-ruler/SKILL.md | skill | 100 | — |
| skills/wiztelemetry-tracing/SKILL.md | skill | 100 | — |

## Bugs (PR-worthy)

| # | File | Issue | Confidence | Evidence | Impact |
|---|------|-------|------------|----------|--------|

No high-confidence bugs found.

## Quality Issues (informational)

| # | File | Issue | Penalty |
|---|------|-------|---------|
| 1 | skills/kubesphere-volcano/SKILL.md | Vague quantifier "appropriate" in "Use **appropriate** queue" (line 712) — leaves queue selection criteria undefined | -2 |
| 2 | skills/kubesphere-volcano/SKILL.md | Vague quantifier "appropriate" in "Apply the template with **appropriate** modifications based on user requirements" (line ~792) — provides no actionable guidance on which fields to change | -2 |
| 3 | skills/kubesphere-devops-pipeline/SKILL.md | Vague quantifier "appropriate" in Common Mistakes table: "Use `kubernetes { yaml ... }` agent with **appropriate** container image" (line 1247) — does not specify selection criteria | -2 |
| 4 | skills/kubesphere-devops-credentials/SKILL.md | Blank line at line 544 splits the Common Mistakes Markdown table into two fragments; the second fragment (lines 545–549) renders as plain text, not a table | 0 |
| 5 | skills/kubesphere-devops-overview/SKILL.md | Architecture table contains a duplicate separator row and four repeated data rows at lines 277–281 (copy-paste artifact; devops-jenkins/devops-apiserver/devops-controller/Jenkins Agent rows appear twice) | 0 |
| 6 | skills/kubesphere-devops-pipeline/SKILL.md | Orphan Common Mistakes table at lines 1276–1282 appears inside the Debugging Steps subsection without a heading or context; it duplicates a subset of the earlier Common Mistakes table | 0 |
| 7 | skills/kubesphere-devops-tenant/SKILL.md | Orphaned shell flag at line 253: `  -H "Authorization: Bearer ${API_TOKEN}" | jq '.items[].metadata.name'` appears as a standalone line after the preceding curl command completes; not a valid shell command and likely a copy-paste artifact | 0 |

## Cross-Component

`skills/kubesphere-devops-tenant/SKILL.md` (lines 50 and ~1266) references sibling skills via relative paths `../../core/kubesphere-core/SKILL.md` and `../kubesphere-devops-overview/SKILL.md`. These paths imply that the skill lives in a subdirectory (e.g., `skills/devops/kubesphere-devops-tenant/`), but the actual layout has it at `skills/kubesphere-devops-tenant/`. If the flat layout is canonical, these relative paths would resolve outside the repository root and become unreachable. Not verified at high confidence during this pass.

`skills/frontend-forge-fi-operations/SKILL.md` and `skills/kubesphere-network-extension-operations/SKILL.md` reference local `references/` subdirectories (`references/lifecycle.md`, `references/extension-management.md`, `references/inspection.md` and `references/api_doc.md`, `references/values.yaml`, etc.). Existence of these files in the respective skill directories was not confirmed during this pass.

## Recommendation

The collection is in excellent condition — 99.8/100 weighted average, all 26 SKILL.md files carry valid `name` and `description` frontmatter with names matching their parent directories, and no high-confidence bugs were found. Three minor uses of the vague quantifier "appropriate" in two files account for all scoring deductions; replacing those phrases with concrete criteria would push the collection to a clean 100.
