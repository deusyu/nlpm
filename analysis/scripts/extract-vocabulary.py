#!/usr/bin/env python3
"""Extract candidate vocabulary terms from NL programming artifacts.

Walks a repository and emits frequency tables for verbs and nouns by
literary source (filenames, frontmatter descriptions, headings). Output
feeds a project's `skills/<plugin>/vocabulary/` registry — see the
human-readable `vocabulary/SKILL.md` for definitions and the
`registry.yaml` sidecar for the machine-readable canonical/deprecated
map. A term has *literary warrant* (P6 of
analysis/vocabulary-design-principles.md) when this script finds it;
re-run to refresh.

Stdlib-only. Usage:

  # Default: run on NLPM itself, write to analysis/vocabulary-extract/
  python3 analysis/scripts/extract-vocabulary.py

  # Run on another repo with NLPM-shaped layout (commands/, agents/, skills/)
  python3 analysis/scripts/extract-vocabulary.py --root /path/to/other-repo

  # Run on any repo with a custom scope config (JSON)
  python3 analysis/scripts/extract-vocabulary.py \\
      --root /path/to/other-repo \\
      --scopes /path/to/scopes.json \\
      --out /path/to/other-repo/analysis/vocab-extract/

Scope config (JSON) — same shape as the built-in defaults below:

  {
    "scopes": {
      "commands":   { "scope": "internal", "glob": "commands/*.md",
                      "role": "verb-filename" },
      "agents":     { "scope": "internal", "glob": "agents/*.md",
                      "role": "noun-filename" },
      "skills":     { "scope": "internal", "glob": "skills/*/SKILL.md",
                      "role": "skill-dirname" },
      "auditor":    { "scope": "auditor",  "glob": ".github/workflows/*.yml",
                      "role": "verb-filename" }
    }
  }

Roles control which extraction pass runs on the matched files:
  * "verb-filename"  — split filename → candidate verbs
  * "noun-filename"  — split filename → role-nouns
  * "skill-dirname"  — use parent-dir name as concept-noun
  * "headings"       — extract capitalized phrases from H1–H4 headings
  * "description"    — first verb after frontmatter `description:`
  * "verb-or-noun"   — split filename, classify each token by VERB_SEEDS
                       membership (heuristic; used for auditor scripts)

A scope entry without an explicit "role" defaults to "headings+description"
(both passes run, conservative).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Built-in defaults (NLPM-shaped layout)
# ---------------------------------------------------------------------------

REPO_ROOT_DEFAULT = Path(__file__).resolve().parents[2]

DEFAULT_SCOPES: dict[str, dict[str, str]] = {
    "commands":           {"scope": "internal", "glob": "commands/*.md",
                           "role": "verb-filename"},
    "agents":             {"scope": "internal", "glob": "agents/*.md",
                           "role": "noun-filename"},
    "skills":             {"scope": "internal", "glob": "skills/*/*/SKILL.md",
                           "role": "skill-dirname"},
    "rules-body":         {"scope": "internal", "glob": "skills/*/rules/SKILL.md",
                           "role": "headings"},
    "auditor-workflows":  {"scope": "auditor", "glob": ".github/workflows/auditor-*.yml",
                           "role": "verb-filename"},
    "auditor-scripts":    {"scope": "auditor", "glob": "auditor/scripts/*.py",
                           "role": "verb-or-noun"},
    "auditor-scripts-sh": {"scope": "auditor", "glob": "auditor/scripts/*.sh",
                           "role": "verb-or-noun"},
    "analysis":           {"scope": "internal", "glob": "analysis/*.md",
                           "role": "headings"},
    "docs":               {"scope": "internal", "glob": "docs/*.md",
                           "role": "headings"},
}

STOPWORDS = {
    "the","a","an","and","or","but","if","of","in","on","at","to","for",
    "with","from","by","as","is","are","was","were","be","been","being",
    "have","has","had","do","does","did","this","that","these","those",
    "it","its","they","them","their","what","which","who","when","where",
    "why","how","all","any","each","every","some","no","not","yes","you",
    "your","we","our","i","me","my","he","she","his","her","him","us",
    "one","two","three","four","five","first","second","third","last",
    "next","more","most","less","least","than","then","so","out","up",
    "down","over","under","via","per","into","onto","about","after",
    "before","between","during","while","since","until","though","even",
    "still","just","only","also","well","very","much","many","few","such",
    "same","other","another","own","new","old","yaml","json","md","ts",
    "py","sh","true","false","null","yml","github","com","https","http",
}

VERB_SEEDS = {
    "use","write","create","make","build","add","remove","delete","fix",
    "patch","update","refresh","load","save","store","fetch","get","set",
    "list","find","search","scan","check","validate","verify","test",
    "audit","review","score","rank","classify","discover","explore",
    "track","log","emit","report","summarize","extract","parse","render",
    "convert","transform","rationalize","canonicalize","consolidate",
    "merge","split","promote","demote","approve","reject","label","tag",
    "name","rename","declare","document","describe","define","specify",
    "configure","init","initialize","bootstrap","install","uninstall",
    "enable","disable","open","close","start","stop","run","trigger",
    "fire","skip","include","exclude","match","fail","pass","succeed",
    "produce","consume","gate","infer","claim","assert","ensure","require",
    "expect","prevent","block","allow","permit","deny","follow","drive",
    "pull","push","fork","branch","commit","rebase","release","publish",
    "ship","deploy","select","pick","choose","decide","judge","weigh",
    "compare","contrast","differ","align","diverge","drift","diff",
    "triage","resolve","reopen","stale","expire","walk","apply",
    "enforce","cite","propose","detect","backfill","prepare",
    "synthesize","repair","three-way",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        return "", text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return "", text
    return parts[1], parts[2]


def yaml_field(yaml_text: str, key: str) -> str | None:
    m = re.search(rf"^{re.escape(key)}:\s*(.+)$", yaml_text, re.M)
    if not m:
        return None
    val = m.group(1).strip().strip('"').strip("'")
    return val or None


def file_stem_tokens(path: Path) -> list[str]:
    stem = path.stem
    if stem == "SKILL":
        stem = path.parent.name
    # Drop auditor- prefix in workflow file names so the verb is the lead token
    if stem.startswith("auditor-"):
        stem = stem[len("auditor-"):]
    return [t for t in re.split(r"[-_]", stem) if t]


def headings(text: str) -> list[str]:
    return re.findall(r"^#{1,4}\s+(.+?)\s*$", text, re.M)


def heading_terms(line: str) -> list[str]:
    return re.findall(r"\b[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]+){0,3}\b", line)


def load_scopes(scope_arg: str | None) -> dict[str, dict[str, str]]:
    if not scope_arg:
        return DEFAULT_SCOPES
    data = json.loads(Path(scope_arg).read_text(encoding="utf-8"))
    if "scopes" not in data or not isinstance(data["scopes"], dict):
        raise SystemExit(f"scopes file {scope_arg}: missing top-level 'scopes' object")
    for label, entry in data["scopes"].items():
        if "scope" not in entry or "glob" not in entry:
            raise SystemExit(f"scopes file {scope_arg}: entry '{label}' missing 'scope' or 'glob'")
    return data["scopes"]


# ---------------------------------------------------------------------------
# Extraction passes
# ---------------------------------------------------------------------------

def extract_one(
    path: Path,
    rel: Path,
    label: str,
    entry: dict[str, str],
    verbs: dict[str, Counter],
    nouns: dict[str, Counter],
    scope_of: dict[str, set[str]],
    examples: dict[tuple[str, str], list[str]],
) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return

    yaml_text, body = split_frontmatter(text)
    scope = entry.get("scope", "internal")
    role = entry.get("role", "headings")

    if role == "verb-filename":
        for tok in file_stem_tokens(path):
            if tok in STOPWORDS or len(tok) < 2:
                continue
            verbs[f"{label}:filename"][tok] += 1
            scope_of[tok].add(scope)
            if len(examples[("verb", tok)]) < 3:
                examples[("verb", tok)].append(str(rel))

    elif role == "noun-filename":
        for tok in file_stem_tokens(path):
            if tok in STOPWORDS or len(tok) < 2:
                continue
            nouns[f"{label}:filename"][tok] += 1
            scope_of[tok].add(scope)
            if len(examples[("noun", tok)]) < 3:
                examples[("noun", tok)].append(str(rel))

    elif role == "skill-dirname":
        for tok in file_stem_tokens(path):
            if tok in STOPWORDS or len(tok) < 2:
                continue
            nouns[f"{label}:dirname"][tok] += 1
            scope_of[tok].add(scope)
            if len(examples[("noun", tok)]) < 3:
                examples[("noun", tok)].append(str(rel))

    elif role == "verb-or-noun":
        for tok in file_stem_tokens(path):
            if tok in STOPWORDS or len(tok) < 2:
                continue
            if tok in VERB_SEEDS:
                verbs[f"{label}:filename"][tok] += 1
                scope_of[tok].add(scope)
                if len(examples[("verb", tok)]) < 3:
                    examples[("verb", tok)].append(str(rel))
            else:
                nouns[f"{label}:filename"][tok] += 1
                if len(examples[("noun", tok)]) < 3:
                    examples[("noun", tok)].append(str(rel))

    # description-pass and headings-pass run additionally for all roles
    # except verb-filename/noun-filename/skill-dirname where we already
    # captured the high-signal filename term; for those, still run
    # description so frontmatter triggers count.
    desc = yaml_field(yaml_text, "description")
    if desc:
        m = re.match(r"['\"]?(?:Use\s+(?:when|for|this)\s+)?([A-Za-z]+)", desc)
        if m:
            first = m.group(1).lower()
            if first in VERB_SEEDS:
                verbs[f"{label}:description"][first] += 1
                scope_of[first].add(scope)

    if role in ("headings", "verb-or-noun") or role.endswith("filename") or role == "skill-dirname":
        for h in headings(body):
            for term in heading_terms(h):
                if term.lower() in STOPWORDS:
                    continue
                nouns[f"{label}:heading"][term] += 1


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--root", default=str(REPO_ROOT_DEFAULT),
        help="Repository root to scan (default: NLPM's own root)",
    )
    parser.add_argument(
        "--scopes", default=None,
        help="Path to JSON file overriding the built-in scope config",
    )
    parser.add_argument(
        "--out", default=None,
        help="Output directory (default: <root>/analysis/vocabulary-extract/)",
    )
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"error: --root {root} is not a directory", file=sys.stderr)
        return 2
    out_dir = Path(args.out).resolve() if args.out else (root / "analysis" / "vocabulary-extract")
    scopes = load_scopes(args.scopes)

    verbs: dict[str, Counter] = defaultdict(Counter)
    nouns: dict[str, Counter] = defaultdict(Counter)
    examples: dict[tuple[str, str], list[str]] = defaultdict(list)
    scope_of: dict[str, set[str]] = defaultdict(set)

    files_seen = 0
    for label, entry in scopes.items():
        for path in sorted(root.glob(entry["glob"])):
            if not path.is_file():
                continue
            try:
                rel = path.relative_to(root)
            except ValueError:
                rel = path
            extract_one(path, rel, label, entry, verbs, nouns, scope_of, examples)
            files_seen += 1

    all_verbs: Counter = Counter()
    for c in verbs.values():
        all_verbs.update(c)
    all_nouns: Counter = Counter()
    for c in nouns.values():
        all_nouns.update(c)

    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "verbs.json").write_text(json.dumps({
        "root": str(root),
        "by_source": {k: dict(v) for k, v in verbs.items()},
        "scope": {k: sorted(s) for k, s in scope_of.items() if k in all_verbs},
        "totals": dict(all_verbs.most_common()),
    }, indent=2) + "\n")

    (out_dir / "nouns.json").write_text(json.dumps({
        "root": str(root),
        "by_source": {k: dict(v) for k, v in nouns.items()},
        "scope": {k: sorted(s) for k, s in scope_of.items() if k in all_nouns},
        "totals": dict(all_nouns.most_common()),
    }, indent=2) + "\n")

    md = [
        "# Vocabulary Extraction",
        "",
        f"Root: `{root}`",
        f"Files scanned: {files_seen}",
        "Auto-generated by `analysis/scripts/extract-vocabulary.py`. Do not hand-edit.",
        "Re-run to refresh literary warrant (P6 of vocabulary-design-principles).",
        "",
        "## Verbs with literary warrant",
        "",
        "Sources: command filenames, workflow filenames, script filenames,",
        "frontmatter `description:` openers. Filename warrant is highest signal —",
        "those are verbs the codebase already operationalizes.",
        "",
        "| Verb | Total | Scopes | Sources |",
        "|------|-------|--------|---------|",
    ]
    for verb, total in all_verbs.most_common(50):
        srcs = sorted(s for s, c in verbs.items() if verb in c)
        scopes_str = ",".join(sorted(scope_of[verb]))
        md.append(f"| `{verb}` | {total} | {scopes_str} | {', '.join(srcs)} |")

    md += [
        "",
        "## Nouns with literary warrant",
        "",
        "Sources: agent filenames (role-nouns), skill directory names",
        "(concept-nouns), headings across artifacts.",
        "",
        "| Noun | Total | Scopes | Sources |",
        "|------|-------|--------|---------|",
    ]
    for noun, total in all_nouns.most_common(50):
        srcs = sorted(s for s, c in nouns.items() if noun in c)
        scopes_str = ",".join(sorted(scope_of[noun]))
        md.append(f"| `{noun}` | {total} | {scopes_str} | {', '.join(srcs)} |")

    md.append("")
    (out_dir / "summary.md").write_text("\n".join(md))

    print(f"Files scanned: {files_seen}")
    print(f"Verbs: {len(all_verbs)} unique, {sum(all_verbs.values())} occurrences")
    print(f"Nouns: {len(all_nouns)} unique, {sum(all_nouns.values())} occurrences")
    print(f"Wrote {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
