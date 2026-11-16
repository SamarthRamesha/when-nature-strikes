# Agent handover protocol

1. Verify branch and status with `git status --short --branch` and
   `git log -5 --oneline`. The preserved starting point is
   `backup/pre-takeover-2026-11-16` (original main `9b48a50`).
2. Read [the audit](PROJECT_AUDIT.md), [task ledger](PROJECT_TASK_LEDGER.md) and
   [validation report](VALIDATION_REPORT.md). Verify any claims before updating.
3. Reproduce with the README and a provider-authorized workbook. Keep source
   and row-level results local. Preserve history and do not merge main without
   the owner’s explicit authorization.
4. Distinguish passes, warnings, failures and checks that could not run. Record
   the newest branch tip, test evidence, pending approvals and next commands in
   [the team handover](TEAM_HANDOVER.md) and [continuation prompt](NEXT_SESSION_PROMPT.md).
