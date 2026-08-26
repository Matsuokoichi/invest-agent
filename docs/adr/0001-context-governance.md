# ADR-0001: Context Governance as a Versioned Contract

Status: Accepted

Date: 2026-08-25

## Context

The repository contains product specifications, runtime behavior, evaluation policy, local coding instructions, and hidden evaluation expectations. As implementation grows, relying on contributors to remember authority and visibility boundaries creates duplication, stale guidance, and evaluation leakage risk.

## Decision

Adopt `context/MANIFEST.toml` as the machine-readable index of scopes, canonical documents, and dependency boundaries. Keep governance principles in `context/POLICY.md`, semantic review criteria in `context/REVIEW_RUBRIC.md`, and enforce objective rules with `context-audit` in pull requests.

Nested `AGENTS.md` files contain local deltas only. Evaluation privacy is treated separately from context relevance: runtime process isolation remains mandatory before executing the real Agent adapter.

## Consequences

- Context resolution and objective drift checks become reproducible.
- Canonical document and instruction changes are reviewable as code.
- The manifest adds maintenance cost and must change with durable scope changes.
- Semantic contradiction and staleness still require human or Agent review.
- The audit cannot claim security isolation until the process filesystem boundary is implemented.
