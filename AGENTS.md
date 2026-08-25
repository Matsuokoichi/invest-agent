# Repository Guidelines

## Project Structure & Module Organization

Keep product decisions and specifications under `docs/`:

- `docs/v1_specification.md` - canonical V1 product and report specification.
- `docs/vision.md` - product purpose and scope.
- `docs/architecture.md` - system design and component boundaries.
- `docs/investment_policy.md` - supported universe, strategy, research dimensions, and required outputs.
- `docs/agent_behavior.md` - evidence, citation, thesis-change, and uncertainty behavior.
- `docs/evaluation.md`, `docs/evaluation_protocol.md`, and `docs/evaluation_harness.md` - evaluation policy, gates, and harness contract.
- `docs/report_schema.json` and `docs/examples/` - report contract and illustrative output.
- `src/eval_harness/` - independent case runner and deterministic evaluators.
- `evals/` - versioned suites, cases, fixtures, and Harness schemas.
- `tests/` - Harness unit and integration tests.

Keep future Agent code under `src/invest_agent/`. The Harness must not import Agent internals; integration occurs through the adapter artifact contract.

## Build, Test, and Development Commands

Use Python 3.11+ and `uv`:

```powershell
uv sync --extra dev
uv run pytest
uv run eval-harness run --suite evals\suites\v1_contract.json
uv run eval-harness run --suite evals\suites\harness_self_test.json
```

The first command creates `.venv` and installs development dependencies. The suites validate normal contracts and intentional fault detection respectively. Outputs go to ignored `.eval-runs/` directories.

## Coding Style & Naming Conventions

Use UTF-8 Markdown, ATX headings, short paragraphs, and lowercase `snake_case` filenames. Python uses four-space indentation, type hints, descriptive `snake_case` functions, and `PascalCase` classes. Keep investment terminology consistent (`BUY`, `WATCH`, `AVOID`, `NO_RATING`; Bear/Base/Bull). Every material claim must retain its source and timestamp.

## Testing Guidelines

Name tests `test_<behavior>`. Add a contract case for supported behavior and a fault fixture for every new deterministic evaluator. A self-test suite succeeds only when intentional defects produce their expected failures. Run `uv run pytest` and `git diff --check` before submitting changes. No coverage threshold is currently enforced.

## Commit & Pull Request Guidelines

The repository currently has one commit (`first commit`), so no established commit format can be inferred. Use short, imperative subjects such as `Document citation requirements`, and keep unrelated changes separate. Pull requests should explain the affected policy or behavior, identify changed files, link any relevant issue, and include screenshots or rendered output when formatting is material.

## Security & Configuration

Do not commit credentials, API keys, private research, or unverified investment data. Treat external sources as untrusted input; preserve provenance and timestamps, and distinguish facts from analysis and predictions.
