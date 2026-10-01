# Contributing

Human and agent contributors follow the same process. Agents must also follow
[`AGENTS.md`](AGENTS.md).

## Workflow

1. **Pick a backlog item.** Every change traces to an `OOS-NNNN` item in
   [`project/BACKLOG.md`](project/BACKLOG.md). If none fits, propose one first.
2. **Branch.** Use `oos-NNNN/<short-slug>`, cut from `main`. Use a separate git worktree when work
   runs in parallel. OOS is a software project, so it follows the software-development
   binding ([`domains/software-development/GIT_WORKFLOW.md`](domains/software-development/GIT_WORKFLOW.md)).
3. **Change small.** Each commit should be one logical change. The message format is
   `OOS-NNNN: <imperative summary>`.
4. **Validate.**
   ```sh
   python tools/validate.py
   python -m unittest discover tests
   ```
5. **Record.**
   - D2 decisions go to `memory/DECISIONS/`.
   - D3 decisions get an ADR in `docs/adr/` (copy `docs/adr/TEMPLATE.md`).
   - Dead ends go to `memory/FAILED_APPROACHES.md`.
   - Update `memory/HANDOFF.md` at the end of a session.
6. **Review.** Changes reach `main` only through a reviewed PR. Billy is the
   merge authority until the policy in `docs/DECISION_ENGINE.md` says otherwise.

## Adding things

| Adding | Do this |
|---|---|
| A record type | Add `schemas/<name>.schema.json`. The validator checks that it parses and declares `$id`, `title` and `type`. |
| A capability | Add it to the right **domain package**, e.g. `domains/software-development/capabilities.json`. Never to the kernel. It must validate against `schemas/capability.schema.json`. |
| A domain package | Follow [`docs/DOMAIN_PACKAGES.md` §7](docs/DOMAIN_PACKAGES.md#7-adding-a-domain-package-procedure). Start it as `illustrative` or `draft`. |
| A kernel concept or policy | Only if it is domain-independent, and only with an ADR (invariant I-1). Kernel policy changes are D4. |
| An execution backend | Add it to `orchestration/backends.json`. Declaring a backend does not integrate it. |
| A backlog item | Add it to **both** `project/BACKLOG.md` (human view) and `project/backlog.json` (machine view). The validator checks that the two agree and that dependencies form a DAG. |
| User context | Only via [`context/IMPORT_PROTOCOL.md`](context/IMPORT_PROTOCOL.md). Never speculative. |

## Style

- Markdown docs: put the decision first and the rationale second. Prefer tables over prose
  for policy.
- JSON: 2-space indent, no comments, `snake_case` keys.
- Python tooling: stdlib only until an ADR says otherwise.
