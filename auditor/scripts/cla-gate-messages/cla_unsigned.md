## Contribute step skipped — CLA required

Owner `${OWNER}` requires a signed Contributor License Agreement (CLA) before any external PR can be reviewed. The contributor identity used by this pipeline has not signed the CLA.

**To unblock**:

1. Sign the individual CLA at <https://cla.developers.google.com/about> using the GitHub identity that authors PRs.
2. Set repository variables in this repo's Actions settings:
   - `GOOGLE_CLA_SIGNED=true`
   - `CONTRIBUTE_AUTHOR_EMAIL=<the email registered with the CLA>`
   - `CONTRIBUTE_AUTHOR_NAME=<full name to use as commit author>`
3. Re-add the `contribute-approved` label on this issue (or workflow_dispatch this workflow with this issue number).

Audit data has been captured for rule-health analysis; no PRs will be opened until the CLA is in place.
