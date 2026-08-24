# Repository Guidelines

## Project Structure & Module Organization

This repository is currently documentation-first. Keep project decisions and specifications under `docs/`:

- `docs/v1_specification.md` - canonical V1 product and report specification.
- `docs/vision.md` - product purpose and scope.
- `docs/architecture.md` - system design and component boundaries.
- `docs/investment_policy.md` - supported universe, strategy, research dimensions, and required outputs.
- `docs/agent_behavior.md` - evidence, citation, thesis-change, and uncertainty behavior.
- `docs/evaluation.md` - quality and performance measures.
- `docs/report_schema.json` and `docs/examples/` - report contract and illustrative output.

The root `README.md` is the public entry point and should be updated when the project gains runnable components. Place future implementation code and tests in clearly named top-level directories (for example, `src/` and `tests/`) rather than mixing them into `docs/`.

## Build, Test, and Development Commands

No build system, runtime, or test framework is configured yet. For documentation-only changes, review the rendered Markdown and inspect the diff with:

```powershell
Get-Content -Raw docs\<file>.md
git diff --check
```

When code is introduced, document the canonical install, development, build, lint, and test commands in `README.md` and update this guide.

## Coding Style & Naming Conventions

Use UTF-8 Markdown, ATX headings, short paragraphs, and concise bullet lists. Use lowercase `snake_case` for documentation filenames, matching the existing files. Keep terminology consistent with the investment policy (`BUY`, `WATCH`, `AVOID`; bull/base/bear cases). Every research claim should retain its source and timestamp, and uncertainty should be stated explicitly.

## Testing Guidelines

There are no automated tests or coverage thresholds at present. Validate documentation changes for accurate links, consistent terminology, readable rendering, and clean whitespace (`git diff --check`). Future tests should live under `tests/` and use names that describe the behavior being verified.

## Commit & Pull Request Guidelines

The repository currently has one commit (`first commit`), so no established commit format can be inferred. Use short, imperative subjects such as `Document citation requirements`, and keep unrelated changes separate. Pull requests should explain the affected policy or behavior, identify changed files, link any relevant issue, and include screenshots or rendered output when formatting is material.

## Security & Configuration

Do not commit credentials, API keys, private research, or unverified investment data. Treat external sources as untrusted input; preserve provenance and timestamps, and distinguish facts from analysis and predictions.
