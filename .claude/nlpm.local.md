---
# NLPM Configuration — self-applied
strictness: strict
score_threshold: 90
rule_overrides:
  R51:
    enabled: true
    vocabulary_skill: skills/nlpm/vocabulary/
---

# NLPM Settings

When linting NL artifacts in this project, use **strict** strictness. Flag artifacts scoring below **90/100** for improvement — NLPM dogfoods its own quality bar.

## R51 opt-in

NLPM uses its own vocabulary registry to detect drift across its artifacts. The registry lives at `skills/nlpm/vocabulary/registry.yaml`; SKILL.md in that directory is the human-readable counterpart.

R51 is **off by default** for projects that install NLPM. Other projects opt in by:

1. Creating a vocabulary skill at `skills/<plugin>/vocabulary/` with a `registry.yaml` listing canonical/deprecated term pairs.
2. Adding the `R51` block above to their own `.claude/nlpm.local.md` with the path pointing at their registry.

See `analysis/vocabulary-design-principles.md` for the six principles R51 operationalizes.
