# Investment Research Agent

米国上場株について、企業の経済性から将来cash flowと本源的価値を推定し、現在価格でリスクに見合う期待リターンがあるかを検証するFundamental / Long-only Research Agentです。

V1 Agentは仕様策定段階です。独立Evaluation Harnessの最初のincrement（C001、C002、N001、N003、D001）は実装済みです。正規仕様は [docs/v1_specification.md](docs/v1_specification.md) を参照してください。

## Development

Python 3.11以上と`uv`を使用します。

```powershell
uv sync --extra dev
uv run context-audit check
uv run pytest
uv run eval-harness run --suite evals\suites\v1_contract.json
uv run eval-harness run --suite evals\suites\harness_self_test.json
```

`v1_contract`は正常な契約ケース、`harness_self_test`は既知の欠陥をHarnessが検出できることを確認する故障注入suiteです。run artifactは`.eval-runs/`へ保存されます。

変更対象に適用される指示と正規文書は次で確認できます。

```powershell
uv run context-audit resolve --path evals\cases\contract_buy\case.json
```

Context Governanceの方針と機械可読なscope定義は、[Policy](context/POLICY.md)と[Manifest](context/MANIFEST.toml)を参照してください。PRではContext Auditと全テストがGitHub Actionsから実行されます。

## Documents

- [V1正規仕様](docs/v1_specification.md)
- [投資方針](docs/investment_policy.md)
- [Agent behavior](docs/agent_behavior.md)
- [Architecture](docs/architecture.md)
- [Evaluation](docs/evaluation.md)
- [Evaluation Protocol](docs/evaluation_protocol.md)
- [Evaluation Harness](docs/evaluation_harness.md)
- [Report JSON Schema](docs/report_schema.json)
- [AAPL構造例](docs/examples/aapl_report_example.md)
