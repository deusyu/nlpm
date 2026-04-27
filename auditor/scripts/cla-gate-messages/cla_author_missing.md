## Contribute step skipped — CLA author identity not configured

`GOOGLE_CLA_SIGNED=true` is set, but `CONTRIBUTE_AUTHOR_EMAIL` and/or `CONTRIBUTE_AUTHOR_NAME` are missing. Without those, claude-code-action commits under its default bot identity (`claude[bot]@users.noreply.github.com`), which is not covered by any CLA — the `cla/google` check would fail on every PR.

**To unblock**:

1. Set repository variables in this repo's Actions settings:
   - `CONTRIBUTE_AUTHOR_EMAIL=<the email registered with your signed CLA>`
   - `CONTRIBUTE_AUTHOR_NAME=<full name to use as commit author>`
2. Re-add the `contribute-approved` label on this issue.

Both fields must be populated and the email must match the one used when signing the CLA at <https://cla.developers.google.com/about>.
