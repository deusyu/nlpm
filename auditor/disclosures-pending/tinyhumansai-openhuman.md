<!--
Auto-prepared disclosure body for tinyhumansai/openhuman.
The audit workflow's GITHUB_TOKEN cannot file issues on third-party
repos, so this body sits here pending manual filing:

  gh issue create --repo tinyhumansai/openhuman \
    --title 'Security findings in executable artifacts' \
    --body-file auditor/disclosures-pending/tinyhumansai-openhuman.md

After filing, record the URL with:
  jq '.repos["tinyhumansai/openhuman"] += {disclosure_url: "<URL>", disclosure_filed_at: "<ISO8601>", disclosure_filed_by: "manual"}' \
    auditor/registry/repos.json > /tmp/r.json && mv /tmp/r.json auditor/registry/repos.json
-->

## Security Findings in Executable Artifacts

While auditing NL programming artifacts in this repository, our scanner detected potential security issues in executable files.

### Findings

| # | Severity | File | Line | Pattern | Description |
|---|----------|------|------|---------|-------------|
| 1 | CRITICAL | scripts/install.sh | 4,58 | SEC-curl-pipe-sh | Script is designed to be executed via `curl -fsSL URL \| bash` (documented as primary install method). No verification of script integrity before execution; only downloaded binary artifacts are SHA-256 checked after the fact. |
| 2 | HIGH | scripts/build-macos-signed.sh | 52–53 | SEC-new-function-eval | `eval "$(jq -r '...\"export \(.key)=\"\(.value)\"\"' ci-secrets.json)"` — JSON key names are not shell-escaped. A tampered ci-secrets.json with a key containing shell metacharacters (`;`, `$()`, backticks) would execute arbitrary code. Values lack `@sh` quoting too. |

### About This Report

These findings come from [NLPM](https://github.com/xiaolai/nlpm-for-claude)'s security scanner, which checks executable surfaces (hooks, scripts, MCP configs, dependencies) against known-dangerous patterns.

We may be wrong — false positives happen. If any finding is intentional or already mitigated, please close this issue. If a finding is genuine and you'd like a fix PR, let us know.

Full audit report: https://github.com/xiaolai/nlpm-for-claude/blob/main/auditor/audits/tinyhumansai-openhuman.md
