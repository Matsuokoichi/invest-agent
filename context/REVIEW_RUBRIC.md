# Context Review Rubric

Use this rubric when a pull request changes governed context and before large context refactors. Deterministic audit results are evidence, not a substitute for judgment.

## Review dimensions

| Dimension | Review question |
|---|---|
| Boundary | Can runtime code or prompts see evaluation-private information? |
| Hierarchy | Does each rule live at the narrowest natural scope? |
| Duplication | Is one durable rule repeated instead of linked to its authority? |
| Contradiction | Do instructions, code, schemas, and canonical documents disagree? |
| Staleness | Do paths, commands, interfaces, and implementation claims still exist? |
| Discoverability | Does `context-audit resolve` return enough context for the changed path? |
| Relevance | Does the resolved set omit unrelated documents and rubrics? |
| Authority | Is the source of truth for each topic explicit and unique? |
| Durability | Are temporary status and run-specific details kept out of durable docs? |
| Executability | Can an important objective rule become a deterministic check? |
| Security | Is sensitive separation physically enforced rather than instruction-only? |

## Review procedure

1. Read `POLICY.md` and `MANIFEST.toml`.
2. Run `uv run context-audit check`.
3. Inspect every `AGENTS.md`, changed canonical document, relevant module boundary, and audit warning.
4. Resolve context for representative changed paths.
5. Fix safe duplication, broken references, stale paths, and enforceable omissions.
6. Do not change product behavior or architectural decisions silently.
7. Run the audit and tests again.

## Required review output

Report:

- findings, with severity and affected paths;
- changes made;
- unresolved architectural or security questions;
- checks newly automated;
- commands run and their results.

Automated reviewers may propose changes on a branch, but must not write directly to the default branch. Human approval remains required for canonical policy, architecture, security boundaries, and rubric changes.
