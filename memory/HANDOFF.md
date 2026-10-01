# Handoff

- **Session:** OOS-0001 Foundation + addendum (domain-specialized orchestration) · 2026-10-01 · founding architect (Claude Code, claude-opus-5-5)
- **Branch:** `oos-0001/foundation` (local, **not pushed**). `main` has no commits.

## Done this session

1. **Foundation (first commit set).** Vision, architecture and every subsystem model; ADR-0001 to
   ADR-0005; context placeholders and the import protocol; memory; machine-readable policy;
   schemas; milestones, OKRs and backlog; validator and tests.
2. **Addendum: domain-specialized orchestration (ADR-0006).**
   - The audit found software, git and repo assumptions in the "kernel". These were moved to
     `domains/software-development/`: capabilities, software class floors, gates, task types,
     routing profiles, and the git workflow as the workspace binding.
   - New kernel: `orchestration/kernel/` (generic floors, a **PROHIBITED** tier, tighten-only
     composition rules, evidence base types, kernel gates, the relevance pipeline).
   - New: `orchestration/profiles/software-development.json`, `domains/finance/` (an **illustrative**
     sketch, non-operational, with no thresholds), `docs/DOMAIN_PACKAGES.md` (contract, composition,
     the FinanceOS example, Orchestrator Factory direction).
   - Neutralized kernel schemas: `artifact_version`, `built_at_version`, `implementing_changes`,
     `resource_scope`, `isolated_workspace`. The project claim became `claim.schema.json` with an `owner` field.
   - Backends: added `claude-agent-sdk` and `claude-api` (declared only) and the latency and reliability routing factors.
   - Validator: tighten-only composition, profiles, kernel purity (vocabulary + project names),
     anchors. New `tools/mutation_check.py`.
   - Backlog: OOS-0018 (domain loader, M1), OOS-0019 (factory, M5), OOS-0020 (second domain, M5),
     M5 "Domain specialization", M6 "Sustained autonomy". New OQ-007.

## Verified (2026-10-01, Windows, Python 3.10.6)

- `python tools/validate.py`: **13/13 checks passed**
- `python -m unittest discover tests`: **31 tests OK**
- `python tools/mutation_check.py`: **20/20 planted defects caught**, including the original
  `commit_sha` kernel contamination, a domain loosening a kernel floor, a profile loading the
  illustrative finance package, and a broken anchor.
- The new anchor check found and fixed one real broken link (ADR-0002 to the renumbered architecture section).

## Not verified / not done (by design)

- No runtime component exists. No backend integration, no domain loader, no factory.
- The purity check covers kernel *JSON and schemas* only. Kernel prose and future code need review (AGENTS.md §3a).
- FinanceOS and Demon Codex were not read or modified.
- G-REVIEW and G-HUMAN for OOS-0001 are pending Billy's review.

## Next step

1. Billy reviews the branch and answers OQ-001, OQ-003, OQ-004 and OQ-005 (`memory/OPEN_QUESTIONS.md`).
   OQ-007 can wait until after the pilot.
2. Billy decides whether to push and how to create `main` (see OQ-003 on merge authority).
3. Then OOS-0002 (runtime, language and execution-mode spike). **Do not start it before OOS-0001 is accepted.**
