# Six Principles for Minimal, Viable, Comprehensive Vocabulary Design

> **Source.** Copied from `eou-foundry/dev-docs/04-vocabulary-principles.md`, where they were derived from first principles and battle-tested against four established frameworks: OntoClean (Guarino & Welty), Domain-Driven Design (Evans), ISO 25964 / ANSI-NISO Z39.19 warrant theory, and BPMN / Event Storming (Brandolini). This file is the operationalized form for NLPM.
>
> Applies to: the `skills/nlpm/vocabulary/` registry, command and agent names, rule wording in `skills/nlpm/rules/`, the verb taxonomy across `/nlpm:score` / `/nlpm:check` / `/nlpm:scan` / `/nlpm:vocab-drift`, and any project-level extension via `.claude/nlpm.local.md`.

---

## The Six Principles

### P1 — One term per distinct identity, at uniform granularity, within a declared scope

Two terms merge when they share the same identity criterion, operate at the same level of specificity, and live within the same scope. A term legitimately meaning different things across scopes is not a violation — it is a boundary that must be named. Never apply the merge test globally across undeclared scope boundaries.

**Scope-timing rule:** scope must be declared *before* a vocabulary decision enters review. A scope boundary declared after the fact to resolve a collision is a retroactive exemption, not a valid scope, and is treated as a P1 violation.

**Sibling-granularity rule:** sibling terms in the vocabulary must be at comparable levels of specificity. A vocabulary that mixes crisp acts (`diagnose`) with vague phases (`process`) at the same level fails this principle even if each term individually passes the merge test.

### P2 — Nouns are rigid artifacts; verbs are state-changing acts

A noun belongs in the inventory when it is *rigid* — it remains the same kind of thing regardless of what state it is in — and has a testable criterion for identity across time.

A state of an artifact is not a noun. `candidate`, `pending-approval`, `active` are field values on artifacts, not standalone nouns. The artifact they modify is the noun.

A verb belongs when it either changes the authority-state of a named artifact or produces a new rigid artifact that governance can act on independently. Sub-steps that serve a named verb without changing anything a stakeholder needs to react to separately are not top-level verbs.

### P3 — A verb is top-level only if it gates or produces

A verb earns its place when it either:

(a) changes what the executor is permitted to do next, or
(b) produces a named artifact that governance can act on independently.

A **governed artifact** is any artifact with a declared schema, a file path, and an owner. This includes advisory artifacts — recommendations, no-change records, audit reports — not only active state-changers. An act that produces only ephemeral output or internal prose does not qualify.

An act that evaluates and recommends but does not meet either condition above is a sub-step, not a top-level verb.

**Pipeline-membership override:** when an act is a required named step in a declared governance pipeline, P5 naming pressure overrides the gates-or-produces test. The act is named regardless of whether it independently satisfies (a) or (b). For cross-scope pipeline steps, the naming obligation belongs to the scope that *produces* the step's output artifact, not the scope that consumes it.

### P4 — The vocabulary is closed under its own operations, within scope

Every verb applies to at least one noun. Every noun is the target of at least one verb. A term that never appears in a verb+noun combination within its scope has no structural role and is a deletion candidate. Evaluate closure per declared scope, not globally.

A closure gap — a noun with no producing verb, or a verb whose artifacts are only described in prose — is evidence of an unnamed act.

**Cross-scope nouns:** a noun produced in one scope and consumed in another is a *cross-scope noun*, not a closure gap. It must be formally designated as such, naming the producing scope explicitly. A bare "application-domain" without naming the scope is not a valid designation — it is a deferment that must be recorded and revisited.

### P5 — Comprehensive means no unnamed judgment

The vocabulary is comprehensive when every significant decision point has a name that forces the practitioner to surface what they are actually deciding.

If practitioners routinely describe an act as "we just checked" or "it felt right," or if documentation describes a step without assigning it a verb from the canonical set, the vocabulary has a gap.

### P6 — A term requires warrant before it enters

A term earns inclusion through at least one of:

- **Literary warrant** — it appears in actual domain artifacts (specs, rules, schemas).
- **User warrant** — practitioners reach for it unprompted when describing their work.
- **Structural warrant** — the vocabulary hierarchy requires it for coherence. **Must cite a specific P4 closure requirement or P1 hierarchy coherence requirement.** Self-referential structural warrant ("the hierarchy needs this term") is not valid without naming which other term's relationship breaks without it.
- **Domain warrant** — the operational domain requires the distinction to prevent a specific failure.

Intuition alone is not warrant. Absence of warrant is grounds for exclusion or demotion to a sub-step or field value.

---

## Conflict resolution: precedence order

When two or more principles point in different directions, apply them in this order:

```
P2 > P3 > P1 > P4 > P5 > P6
```

- **P2 first** — artifact integrity and the noun/verb distinction are non-negotiable. If a candidate term fails the rigid-artifact or state-changing-act test, no other principle can reinstate it.
- **P3 second** — gatekeeping purity. A verb that neither gates nor produces (by P3's definition, including the pipeline-membership override) does not enter regardless of naming pressure from P5.
- **P1 third** — scope discipline and merge decisions. After identity and gatekeeping are settled, resolve collisions by scope.
- **P4 fourth** — closure. Use P4 to identify gaps after the vocabulary is otherwise stable; do not use it to force terms into the vocabulary before P2 and P3 have been satisfied.
- **P5 fifth** — comprehensiveness. Naming pressure from P5 can trigger addition only after P2–P4 have been evaluated. P5 overrides P3 only via the pipeline-membership override, not generally.
- **P6 last** — warrant is an entry check, not a veto over terms that satisfy P2–P5. A term that satisfies all five structural principles enters; P6 then confirms it has evidence. **If warrant is absent, the term is deferred, not permanently rejected.**

---

## Application status

These principles were applied to NLPM itself in this order. Each entry references the principle(s) that drove the change.

**Foundational pass (P1/P2/P3/P5/P6):**

1. **Two scopes declared** (P1) — internal (NLPM commands, agents, skills) vs auditor (`.github/workflows/auditor-*.yml`, `auditor/`). Documented in `skills/nlpm/vocabulary/SKILL.md`. Declared before any merge/collision decisions, satisfying the scope-timing rule.
2. **Literary warrant extracted** (P6) — `analysis/scripts/extract-vocabulary.py` walks the repo and emits frequency tables at `analysis/vocabulary-extract/`. Re-run after artifact changes to refresh warrant.
3. **Evaluation-cluster bright-line table built** (P1/P5) — `score`, `check`, `test`, `scan`, `audit`, `review` differentiated by output type and judgment requirement. Lives in the vocabulary skill.
4. **Agent names classified as role-nouns, not verbs** (P2/P3) — `scanner`, `scorer`, `checker`, etc. paired alongside their parent verbs in the registry's role-noun table.
5. **Speculative additions held pending warrant** (P6) — `triage`, `rationalize`, internal-scope `audit`, internal-scope `review`. See "Deferred vs rejected" below — the precedence-order refinement reclassified these from "rejected" to "deferred" for the ones that pass P2–P5.

**R51 wiring pass:**

6. **R51 written and made opt-in** — vocabulary discipline is an available audit methodology, not mandatory. Default disabled. Projects opt in via `rule_overrides.R51.enabled: true` + `vocabulary_skill: <path>` in `.claude/nlpm.local.md`. The `enabled` override type was added to `nlpm:conventions` §13.
7. **Machine-readable sidecar** — `skills/nlpm/vocabulary/registry.yaml` exports canonical/deprecated pairs for tooling. SKILL.md remains the human-readable canonical source.
8. **Checker and scorer agents** acknowledge R51 via `skills: [..., nlpm:vocabulary]` and per-step instructions that read the local config before applying any vocabulary checks.
9. **Per-rule warrant tags on R01–R51** appended to the rules SKILL.md, with a retirement-test table.
10. **Auditor workflow filename convention** declared as a sanctioned split (`auditor-<verb>` for state-changers, `auditor-<output-noun>` for artifact-producers). `auditor-batch-processor` flagged as the one outlier.
11. **NLPM self-opts-in** via `.claude/nlpm.local.md` — the plugin dogfoods R51 at strict/90.

**Cross-repo adoption pass:**

12. **Extractor parameterized** — `--root`, `--scopes`, `--out` arguments. Any repo can produce its own warrant tables.
13. **`/nlpm:vocab-init` command** — bootstraps a vocabulary skill in any target project: detects layout, runs the extractor, seeds canonical noun/verb tables from top extracted terms, writes the R51 opt-in stub.
14. **`/nlpm:vocab-drift` command + `vocab-drift-scanner` agent** — registry-free drift detection. Advisory only.
15. **Adopter documentation** — `docs/for-authors.md` gained the "Vocabulary discipline (R51, opt-in)" section.

**Auditor pipeline integration pass:**

16. **Auditor `vocab-drift` workflow** — runs in parallel with `auditor-audit` on `audit-ready`; writes to `auditor/vocab-advisories.jsonl` (separate from `findings.jsonl`, structurally preventing PRs).
17. **Vocab fingerprint helper** — `auditor/scripts/compute-vocab-fingerprint.sh`.
18. **Scanner JSONL output mode** documented in `agents/vocab-drift-scanner.md`.
19. **Schema entries** in `auditor/SCHEMAS.md` — `vocab_advisory` record format, `VOCAB-*` rule_id namespace, lifecycle events.
20. **Premature-corpus skip** — `<5 NL artifacts` short-circuits with `scan_skipped_premature` event.
21. **Cross-scope homonym suppression** — workflow reads the target's `cross_scope_homonyms.verbs` if a registry exists.

**Refined-principles sync pass (this turn):**

22. **Principles synced from eou-foundry** — added scope-timing rule, sibling-granularity rule (both P1), governed-artifact definition + pipeline-membership override (P3), cross-scope-noun designation rule (P4), structural-warrant-must-cite requirement (P6), and the P2>P3>P1>P4>P5>P6 precedence order.
23. **Re-audit findings recorded** — see "Findings against the refined principles" below.

---

## Findings against the refined principles

| ID | Principle | Severity | Finding |
|----|-----------|----------|---------|
| N-01 | P6 | High | R51's warrant tag in `skills/nlpm/rules/SKILL.md` is `structural` but the citation ("Vocabulary drift across artifacts; rule is opt-in by design") is self-referential. The refined P6 requires citing a specific P4 closure or P1 coherence requirement. **Fix:** retag as `domain` warrant — the operational domain (multi-author NL plugins) has the specific failure of vocabulary drift across artifacts (observed empirically in early audits and prior conversations). Cite the failure mode, not the rule's existence. |
| N-02 | P6 / precedence | Moderate | `skills/nlpm/vocabulary/registry.yaml` lists `triage`, `rationalize`, internal `audit`, internal `review` under `rejected_pending_warrant`. Under the refined precedence (P6 last, no veto), terms that pass P2–P5 should be **deferred**, not rejected. Some of these pass P2–P5 (`triage`, internal `review` as a sanctioned cross-scope homonym); some still fail P1 (`internal audit` is P1-blocked by `score`+`check`). **Fix:** split into two lists: `deferred_pending_warrant` (P2–P5 pass, P6 absent) and `rejected_by_higher_principle` (one or more of P2–P5 fail). |
| N-03 | P1 sibling-granularity | Low | The auditor-scope verb table includes `report` next to specific verbs (`classify`, `refine`, `cite`). `report` is broader than its siblings. Either re-cast as a sub-step of more specific verbs (`summarize-day`, `aggregate-findings`) or accept the granularity mismatch and document why. **Fix:** keep `report` for now and note the granularity asymmetry inline in the table; the workflow filename convention already absorbs this (noun-named workflows produce reports — the verb is implicit). |
| N-04 | P4 cross-scope | Clean | `finding` is produced and consumed within auditor scope; no internal/auditor cross-scope nouns identified. `vocab_advisory` is produced and consumed within auditor scope. Verified clean. |
| N-05 | P1 scope-timing | Clean | Both NLPM scopes (internal, auditor) were declared in the foundational pass before any merge decisions. No retroactive exemptions detected. |
| N-06 | P3 pipeline-membership | Possible gap | The auditor pipeline has named steps (`discover` → `audit` + `vocab-drift` → `contribute` → `track`) but no formal "pipeline declaration" artifact tying them together. Each step is a verb satisfying (a) or (b) on its own, so the override isn't strictly needed. Documenting the pipeline as a governed artifact (e.g., a YAML file or section in `auditor/README.md`) would make P3 pipeline-membership applicable if a non-gating, non-producing step is ever needed. **Status:** not a current violation; flag for future. |

Severities: High requires action; Moderate is worth doing; Low is documentation only.

---

## Deferred vs rejected

Under the refined P6, terms that satisfy P2–P5 enter the registry as **deferred** with a pending-warrant marker. Only terms that fail P2, P3, P1, or P4 are **rejected**. Distinguishing the two clarifies what evidence would unblock each term.

**Deferred (P2–P5 satisfied; awaiting warrant):**

- `triage` — verb, applies to `finding`, gates downstream contribute consideration. Awaits user warrant (practitioner reaches for the term in real NLPM operation).
- `internal review` — verb, sanctioned cross-scope homonym with auditor `review`, produces a comment trail. Awaits user warrant.
- `rationalize` — verb, applies to extracted-term frequencies, produces a curated registry. Awaits user warrant (practitioner names the curation act explicitly during vocab work).

**Rejected by higher principle (no entry):**

- `internal audit` — fails P1. The internal scope already has `score`+`check` covering quantitative+structural evaluation. Adding `audit` here would violate P1's merge test (two terms, one identity criterion, same scope).
- `lint`, `validate` (internal-scope synonyms of `check`) — fail P1.
- `analyze`, `grade`, `rate` (internal-scope synonyms of `score`) — fail P1.

The `registry.yaml` `rejected_pending_warrant` block should be split into `deferred_pending_warrant` (the first list) and `rejected_by_higher_principle` (the second list).

---

## Maintenance

When eou-foundry's `dev-docs/04-vocabulary-principles.md` changes:

1. Diff upstream against this file.
2. Bring over structural changes (new sub-rules, new principles, precedence shifts).
3. Skip EOU-specific application material (self-audit findings, EOU vocabulary tables).
4. Re-audit NLPM's vocabulary work for any new requirements introduced by the change.
