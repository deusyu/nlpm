#!/usr/bin/env python3
"""Three-way merge for auditor/registry/repos.json on push-conflict.

The previous strategy (`jq -s '.[0] * .[1]' theirs ours`) is a recursive
merge with ours-wins on conflict. That is wrong when the current
workflow's checkout is stale: for every entry the workflow did NOT touch,
"ours" carries the OLD value, and the merge silently reverts whatever
update landed on remote since this workflow's checkout. Concrete symptom:
kepano/obsidian-skills oscillating between status=audited (set by audit
commit) and status=discovered (overwritten by every subsequent unrelated
audit/contribute commit's stale view). See the timeline in
`git log --all -- auditor/registry/repos.json`.

The correct strategy is a 3-way merge:
- BASE (`:1`)   — common ancestor at the conflict point
- OURS (`:2`)   — this workflow's view (what we just committed)
- THEIRS (`:3`) — what landed on remote since BASE

For every (repo, field) cell:
- ours != base AND theirs == base  → use ours  (we changed, nobody else did)
- ours == base AND theirs != base  → use theirs (we didn't touch, remote did)
- both differ                      → use ours  (current workflow's intent)
- neither differs                  → either (identical)

Repos that exist in only one side are added (union).
Top-level non-`repos` keys (e.g. metadata) get the same treatment.

Validates the merged JSON before printing — malformed output is rejected
so the conflict-resolution script can exit non-zero rather than corrupt
the registry on disk.

Usage:
    three-way-merge-registry.py BASE OURS THEIRS

Reads three JSON files, prints merged JSON to stdout.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def merge_value(base: Any, ours: Any, theirs: Any) -> Any:
    """Three-way merge of one cell. See module docstring for rules."""
    ours_changed = ours != base
    theirs_changed = theirs != base
    if isinstance(base, dict) and isinstance(ours, dict) and isinstance(theirs, dict):
        return merge_dict(base, ours, theirs)
    if not ours_changed and theirs_changed:
        return theirs
    if ours_changed and not theirs_changed:
        return ours
    return ours


def merge_dict(base: dict, ours: dict, theirs: dict) -> dict:
    keys = set(base) | set(ours) | set(theirs)
    out: dict = {}
    sentinel = object()
    for k in keys:
        b = base.get(k, sentinel)
        o = ours.get(k, sentinel)
        t = theirs.get(k, sentinel)
        if o is sentinel and t is sentinel:
            continue
        if o is sentinel:
            if b is sentinel:
                out[k] = t
            elif t == b:
                continue
            else:
                out[k] = t
            continue
        if t is sentinel:
            if b is sentinel:
                out[k] = o
            elif o == b:
                continue
            else:
                out[k] = o
            continue
        bv = b if b is not sentinel else None
        out[k] = merge_value(bv, o, t)
    return out


def main() -> int:
    if len(sys.argv) != 4:
        print(f"usage: {sys.argv[0]} BASE OURS THEIRS", file=sys.stderr)
        return 2
    paths = [Path(p) for p in sys.argv[1:]]
    docs = []
    for p in paths:
        try:
            docs.append(json.loads(p.read_text()))
        except Exception as e:
            print(f"ERROR: failed to load {p}: {e}", file=sys.stderr)
            return 3
    base, ours, theirs = docs
    if not (isinstance(base, dict) and isinstance(ours, dict) and isinstance(theirs, dict)):
        print("ERROR: all three inputs must be JSON objects", file=sys.stderr)
        return 4
    merged = merge_dict(base, ours, theirs)
    if "repos" not in merged or not isinstance(merged.get("repos"), dict):
        print("ERROR: merged registry has no `repos` map; refusing to write", file=sys.stderr)
        return 5
    json.dump(merged, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
