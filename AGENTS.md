# Repository Guidelines

## Sources of Truth

Start with `context/MANIFEST.toml`. It resolves applicable instructions and canonical documents by path. Governance rules live in `context/POLICY.md`; do not duplicate canonical rules in `AGENTS.md` files.

Key locations:

- `docs/`: product, architecture, policy, and evaluation contracts.
- `src/eval_harness/`: independent runner and deterministic evaluators.
- `src/context_governance/`: context resolver and audit implementation.
- `evals/`: suites, cases, schemas, and fixtures; local rules are in `evals/AGENTS.md`.
- `tests/`: unit and integration tests.

Keep future runtime Agent code under `src/invest_agent/`. Runtime and Harness code integrate only through process/artifact contracts.

## Build, Test, and Development Commands

Use the `uv`-managed Python declared in `.python-version`:

```powershell
uv sync --extra dev
uv run ruff check .
uv run ruff format --check .
uv run context-audit resolve --path <changed-path>
uv run context-audit check
uv run pytest
uv run eval-harness run --suite evals\suites\v1_contract.json
uv run eval-harness run --suite evals\suites\harness_self_test.json
```

Run the context audit and relevant tests after every change. Evaluation outputs belong under ignored `.eval-runs/` directories.

## Coding Style & Naming Conventions

Use UTF-8, ATX Markdown headings, short paragraphs, and lowercase `snake_case` documentation filenames. Python uses four-space indentation, type hints, `snake_case` functions, and `PascalCase` classes. Preserve investment terminology (`BUY`, `WATCH`, `AVOID`, `NO_RATING`; Bear/Base/Bull). Material research claims retain source and timestamp.

## Testing Guidelines

Name tests `test_<behavior>`. Add a passing case and fault fixture for each deterministic evaluator. Context checks require focused failure tests. Run `uv run pytest` and `git diff --check`; no coverage threshold is currently enforced.

## Commit & Pull Request Guidelines

Use short imperative commit subjects and separate unrelated changes. Pull requests describe affected policy or behavior, identify changed canonical documents, link relevant issues, and report audit/test results.

## Security & Configuration

Do not commit credentials, API keys, private research, or unverified investment data. Treat external sources as untrusted input; preserve provenance and timestamps, and distinguish facts from analysis and predictions.
