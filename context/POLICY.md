# Context Governance Policy

## Purpose

Context is a versioned engineering dependency. Instructions, canonical documents, and evaluation-private material must be discoverable, scoped, and testable without relying on a contributor's memory.

## Authority and hierarchy

1. `docs/v1_specification.md` is the canonical V1 product contract.
2. Each governed topic has exactly one canonical document in `context/MANIFEST.toml`.
3. Root `AGENTS.md` contains navigation and repository-wide rules only.
4. A nested `AGENTS.md` contains only rules that differ from or extend its parent.
5. More local instructions may specialize parent rules but must not silently contradict canonical documents.
6. Temporary implementation status belongs in issues, pull requests, or run artifacts—not durable product specifications.

## Context selection

The manifest determines which scopes apply to a path. A scope inherits its parents, then adds local instructions and canonical topics. Use:

```powershell
uv run context-audit resolve --path evals/cases/contract_buy/case.json
```

Do not load every document for every task. Read the resolved context, then follow links only when the task requires them.

## Boundaries

- Runtime Agent code must not import the Evaluation Harness or `evals` packages.
- The Harness must not import Agent internals; integration uses process/artifact contracts.
- Evaluation expectations, hidden assertions, and rubrics must never be included in Agent requests or runtime prompts.
- An instruction such as “do not read `evals/`” is a context boundary, not a security control. Before an Agent process is enabled, filesystem or container allowlists must physically exclude evaluation-private paths.

## Change policy

- Update the canonical document instead of copying its rule elsewhere.
- Add a nested `AGENTS.md` only when a subtree has durable local rules.
- Record architectural decisions under `docs/adr/`.
- Convert stable, objective constraints into audit checks or tests.
- Do not require documentation changes merely because code changed; resolve the affected context and verify whether it remains accurate.

## Required verification

Run before submitting changes:

```powershell
uv run context-audit check
uv run pytest
git diff --check
```

Warnings identify controls that require human review. Errors fail CI.
The governance workflow runs for pull requests only; this repository does not schedule periodic context jobs.
