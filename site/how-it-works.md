---
title: How it works
outline: [2, 3]
---

# How NLPM works

Two pipelines, one rulebook. The **local pipeline** is what a plugin author runs in their own repository; the **auditor pipeline** is what NLPM runs continuously against public Claude Code plugins on GitHub.

## Local pipeline (run in your repo)

```mermaid
flowchart TD
  ls[/nlpm:ls/] --> score[/nlpm:score/]
  ls --> check[/nlpm:check/]
  score --> report[/nlpm:report/]
  check --> report
  vocab[/nlpm:vocab-init/] -.optional.-> drift[/nlpm:vocab-drift/]
  drift -.advisory.-> report
  fix[/nlpm:fix/] -.repair.-> score
  report --> html[(HTML report)]

  classDef step fill:#d5e0ff,stroke:#2b5fff,color:#1d2433
  classDef out fill:#fff,stroke:#2a8a3d,color:#2a8a3d
  class ls,score,check,vocab,drift,fix,report step
  class html out
```

Every step writes a JSON snapshot under `.claude/nlpm-history.json` so `/nlpm:trend` and `/nlpm:report` can chart progress over time.[^1]

## Auditor pipeline (NLPM's own self-evolution loop)

```mermaid
flowchart TD
  Discover[discover] --> Audit[audit + security scan]
  Audit --> Drift[vocab-drift advisory]
  Audit --> Contribute[contribute PRs]
  Drift -.no PR.-> Reports[per-repo reports]
  Contribute --> Track[track]
  Track -->|merged + re-audit| CaseStudy[case study]
  Track -->|clean| Exemplar[exemplar]
  Exemplar --> CiteExemplars[cite-exemplars PR]
  CiteExemplars -->|human-gated| Refine[refine rules PR]
  Refine -.feeds back.-> Discover

  classDef gated fill:#fffbf0,stroke:#c47c00,color:#1d2433
  classDef auto fill:#d5e0ff,stroke:#2b5fff,color:#1d2433
  classDef adv fill:#f6f7fa,stroke:#888,color:#666
  class Discover,Audit,Contribute,Track,CaseStudy,Exemplar auto
  class CiteExemplars,Refine gated
  class Drift,Reports adv
```

Everything before *refine rules* is automated observation. Only `auditor-refine-rules` mutates NLPM's own rulebook, and only by opening a PR for a human reviewer.[^2]

## Findings flow

```mermaid
sequenceDiagram
    participant Repo as External repo
    participant Audit as auditor-audit
    participant Findings as findings.jsonl
    participant Contribute as auditor-contribute
    participant Maintainer as Repo maintainer
    Audit->>Repo: clone target
    Audit->>Findings: write per-finding records
    Note over Findings: confidence: high<br/>required for PR
    Contribute->>Findings: read confidence: high
    Contribute->>Maintainer: open PR per finding (≤3 first contact)
    Maintainer->>Contribute: merge / close / comment
    Contribute->>Findings: track outcome (finding_outcome event)
```

## Two scopes, one boundary

NLPM operates in two declared scopes[^3]. The boundary is intentional: same verb name can mean different things across scopes, and that's a documented homonym, not a collision.

| Scope | What it operates on | Where it lives |
|-------|---------------------|----------------|
| **internal** | NLPM's own behavior — scoring, checking, fixing your local repo | `commands/`, `agents/`, `skills/`, hooks |
| **auditor** | External repos at scale | `.github/workflows/auditor-*.yml`, `auditor/` |

Cross-scope homonyms (`scan`, `test`, `discover`) mean the same thing in both scopes. Scope-bound verbs (`audit`, `contribute`, `track`) only make sense in the auditor scope. The [vocabulary reference](/reference/vocabulary) lists every term.

---

[^1]: Snapshots accumulate; `/nlpm:trend` reads them all to surface regressions over time. If you don't want history, delete `.claude/nlpm-history.json` between runs.

[^2]: This is by design — autonomous rule changes would create feedback loops between the auditor and its own rulebook. The human-gate is the cycle-breaker.

[^3]: The two-scope boundary is principle **P1** of the [vocabulary design principles](/reference/principles#P1). Cross-scope homonyms are *sanctioned* boundaries (declared explicitly in `registry.yaml`); accidental homonyms are flagged as drift by R51.
