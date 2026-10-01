# Domain package: software-development

**Status:** draft · **Operational:** yes · **Profile:** [`orchestration/profiles/software-development.json`](../../orchestration/profiles/software-development.json)

Everything here specializes the kernel for building software. It was moved out of the
kernel by [ADR-0006](../../docs/adr/ADR-0006-domain-agnostic-kernel.md).

| File | Contents |
|---|---|
| [domain.json](domain.json) | Manifest, tools and the summary of the workspace binding |
| [capabilities.json](capabilities.json) | 14 software capabilities (architecture, backend, frontend, game_development, database, testing, code_review, security, devops, performance, ux, product_analysis, research, release_engineering) |
| [policy.json](policy.json) | Software class floors (dependency, API, CI, schema, auth, new service, history rewrite, production deploy, release), the protected-branch prohibition, cost calibration and golden examples |
| [verification.json](verification.json) | Gates G-TEST, G-BUILD, G-STATIC, G-RUNTIME, G-VISUAL, G-BENCH, G-MIGRATION, G-SECURITY, evidence types and task types |
| [context_routing.json](context_routing.json) | Capability profiles and the user-context ceiling |
| [GIT_WORKFLOW.md](GIT_WORKFLOW.md) | Workspace binding: kernel `ProjectStore`/`Workspace`/`ChangeSet`/`ArtifactVersion`/`Integration` map to repo, branch+worktree, commits, SHA and reviewed merge |

## Task type → required gates (plus kernel G-SCOPE)

| Task type | Gates |
|---|---|
| bug_fix | G-TEST (incl. regression test), G-REVIEW |
| feature_backend | G-TEST, G-BUILD, G-STATIC, G-REVIEW |
| feature_ui | G-TEST, G-BUILD, G-VISUAL, G-REVIEW |
| refactor | G-TEST (no behaviour change), G-STATIC, G-REVIEW |
| migration | G-MIGRATION, G-TEST, G-REVIEW |
| security_sensitive | G-SECURITY, G-TEST, G-REVIEW |
| performance | G-BENCH, G-TEST |
| documentation, design, spike, outcome_validation | kernel task types (see [VERIFICATION](../../docs/VERIFICATION.md)) |

## Failure-handling bindings

The kernel classes in [FAILURE_HANDLING](../../docs/FAILURE_HANDLING.md) bind here as follows.
*Verification failure* means failed tests. *Workspace contamination* means a dirty working tree.
*Change-set conflict* means merge conflicts.
