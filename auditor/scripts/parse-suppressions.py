#!/usr/bin/env python3
"""Parse rule_overrides from an NLPM config markdown file.

Reads YAML frontmatter from the file given as argv[1].
Prints one JSON object per rule override, one per line.
Exits silently (no output) if the file has no overrides or no frontmatter.
"""

import json
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit(0)


def main() -> int:
    if len(sys.argv) < 2:
        return 0

    try:
        with open(sys.argv[1]) as f:
            content = f.read()
    except OSError:
        return 0

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return 0

    try:
        frontmatter = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return 0

    if not isinstance(frontmatter, dict):
        return 0

    overrides = frontmatter.get("rule_overrides") or {}
    if not isinstance(overrides, dict):
        return 0

    for rule, val in overrides.items():
        print(json.dumps({"rule_id": str(rule), "override": val}))

    return 0


if __name__ == "__main__":
    sys.exit(main())
