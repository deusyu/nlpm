#!/usr/bin/env python3
"""Fetch every cited doc URL, hash the body, diff against the stored hash.

Reads:
  auditor/docs-citations.json    — URL → metadata (`_meta` keys ignored)
  auditor/docs-hashes.json       — URL → {hash, last_seen} (created on first run)

Writes:
  auditor/docs-hashes.json       — updated atomically (rewritten with new
                                   hashes for every URL we successfully fetch)
  /tmp/changed-urls.txt          — one URL per line; URLs whose hash differs
                                   from the stored hash (drift candidates)

Prints to stdout a JSON summary:
  {"changed": N, "bootstrapped": N, "unchanged": N, "fetch_failed": N}

The caller (auditor-docs-diff.yml) reads the JSON and propagates the counts
to GITHUB_OUTPUT and GITHUB_STEP_SUMMARY.

Extracted from auditor-docs-diff.yml in v0.8.10 — the previous inline
shell version mixed two languages and a jq update loop.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


CITATIONS_PATH = Path("auditor/docs-citations.json")
HASHES_PATH = Path("auditor/docs-hashes.json")
CHANGED_FILE = Path("/tmp/changed-urls.txt")
USER_AGENT = "nlpm-docs-diff/1.0 (+https://github.com/xiaolai/nlpm)"
FETCH_TIMEOUT = 30


def load_json(path: Path, default):
    try:
        with path.open() as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return default


def save_atomic(path: Path, data: dict) -> None:
    """Atomic write via same-directory tempfile + rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def fetch(url: str) -> str | None:
    """Fetch URL body. Returns None on any failure (timeout, HTTP error, etc.)."""
    req = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=FETCH_TIMEOUT) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except (URLError, HTTPError, TimeoutError, ConnectionError, ValueError):
        return None


def main() -> int:
    citations = load_json(CITATIONS_PATH, {})
    hashes = load_json(HASHES_PATH, {})
    urls = [k for k in citations if not k.startswith("_")]

    if not urls:
        print(json.dumps({"changed": 0, "bootstrapped": 0, "unchanged": 0, "fetch_failed": 0}))
        return 0

    CHANGED_FILE.write_text("")  # truncate

    changed = 0
    bootstrapped = 0
    unchanged = 0
    fetch_failed = 0
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for url in urls:
        body = fetch(url)
        if body is None:
            print(f"WARN: failed to fetch {url} — skipping", file=sys.stderr)
            fetch_failed += 1
            continue

        new_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
        stored = hashes.get(url) or {}
        old_hash = stored.get("hash") if isinstance(stored, dict) else None

        if not old_hash:
            print(f"BOOTSTRAP: {url} -> {new_hash}")
            bootstrapped += 1
        elif old_hash != new_hash:
            print(f"CHANGED: {url}")
            print(f"  old: {old_hash}")
            print(f"  new: {new_hash}")
            with CHANGED_FILE.open("a") as f:
                f.write(url + "\n")
            changed += 1
        else:
            unchanged += 1

        hashes[url] = {"hash": new_hash, "last_seen": now_iso}

    save_atomic(HASHES_PATH, hashes)

    summary = {
        "changed": changed,
        "bootstrapped": bootstrapped,
        "unchanged": unchanged,
        "fetch_failed": fetch_failed,
    }
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
