# Failed Approaches

Dead ends, kept so they are not repeated blindly. Format: [FAILURE_HANDLING §3](../docs/FAILURE_HANDLING.md#3-failed-approach-entries).
Schema: [`schemas/failed-approach.schema.json`](../schemas/failed-approach.schema.json).

### FAILED-0001 — Writing many files in one multi-heredoc shell command
- **Hypothesis:** generating several Markdown files from one bash command with multiple quoted heredocs is faster than writing them one at a time.
- **Tried:** one command that wrote the ADR index, template and five ADRs (OOS-0001 session, 2026-10-01).
- **Result:** the shell reported `unexpected EOF while looking for matching '`. No files were written.
- **Why it failed:** the Windows bash tool's handling of quoting in long multi-heredoc commands was not reliable for prose containing apostrophes. The exact cause is unconfirmed.
- **Retry when:** never needed. Use the file-writing tool per file, or a short Python script that reads its content from data.
- **Scope:** project · **Capabilities:** devops · **Date:** 2026-10-01
