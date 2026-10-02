# Failed Approaches

Dead ends, kept so they are not repeated blindly. Format: [FAILURE_HANDLING §3](../docs/FAILURE_HANDLING.md#3-failed-approach-entries).
Schema: [`schemas/failed-approach.schema.json`](../schemas/failed-approach.schema.json).

### FAILED-0001 — Writing many files in one multi-heredoc shell command
- **Hypothesis:** generating several Markdown files from one bash command with multiple quoted heredocs is faster than writing them one at a time.
- **Tried:** one command that wrote the ADR index, template and five ADRs (OOS-0001 session, 2026-10-01).
- **Result:** the shell reported `unexpected EOF while looking for matching '`. No files were written.
- **Why it failed:** the Windows bash tool's handling of quoting in long multi-heredoc commands was not reliable for prose containing apostrophes. The exact cause is unconfirmed.
- **Retry when:** never needed. Use the file-writing tool per file, or a short Python script that reads its content from data.
- **Recurred:** 2026-10-01, OOS-0001 addendum. A heredoc Python script failed the same way. This entry had
  not been consulted before acting. The narrowed cause is apostrophes inside heredoc bodies, even with a
  quoted delimiter. The working pattern is to write the script with the file tool, then run it.
- **Recurred again:** 2026-10-02, OOS-0003. Heredoc-embedded Python turned an escaped newline into a real newline
  in a generated test file (syntax error), and a Windows path literal into a unicode-escape error. Rule: never generate
  source files through heredocs. Write them with the file tool.
- **Scope:** project · **Capabilities:** devops · **Date:** 2026-10-01

### FAILED-0002 — Measuring orphan survival with `subprocess.run(capture_output=True)`
- **Hypothesis:** running the crashing child via `subprocess.run(..., capture_output=True)` returns as soon as the child dies.
- **Tried:** OOS-0002 E4, first run.
- **Result:** the call blocked ~60 s, until the orphaned grandchild (which had inherited the pipe) exited. The "no orphans" reading was an artifact.
- **Why it failed:** inherited pipe handles keep the read end open, so EOF arrives only when the last holder exits.
- **Retry when:** never for this purpose. Use DEVNULL stdio and wait on process exit.
- **Scope:** project · **Capabilities:** testing, backend · **Date:** 2026-10-01
