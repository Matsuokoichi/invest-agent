# Evaluation Harness Specification

Harness version: **1.0.0**

Evaluation HarnessはInvestment Research Agentの外部からcaseを実行し、artifactを収集し、V1 Evaluation Protocolに従って採点する独立コンポーネントである。

## 1. Trust boundary

Harnessは次をAgentから信用しない。

- schema_checkedなどの自己申告audit flag
- 計算済みreturn、margin of safety、decision hurdle
- source tier、freshness、citation entailment
- Research loopを実行したという文章上の主張

Harnessがsource snapshot、計算式、policy、traceから独立再検証する。AgentとHarnessはevaluator codeを共有しない。共通利用してよいのはversioned schemaとpolicy constantsだけである。

## 2. Components

~~~text
Case Store
  -> Suite Loader
  -> Run Sandbox
  -> Agent Adapter
  -> Artifact Collector
  -> Evaluator Registry
       -> Deterministic Evaluators
       -> Reference Assertion Evaluators
       -> Citation / Rubric Judge
       -> Human Adjudication Queue
  -> Result Aggregator
  -> Evaluation Report
~~~

## 3. Execution modes

- snapshot：固定source bundleだけを使用。release比較は必ずこのmode
- live：実際のsource connectorを評価。探索・connector監視用でrelease scoreと混ぜない
- replay：保存済みAgent artifactを再採点。evaluator変更の検証用

snapshot modeではAgentの外部network accessを無効化し、基準日後の情報混入を構造的に防ぐ。

## 4. Case layout

~~~text
evals/
├─ suites/
│  └─ v1_release.yaml
├─ cases/
│  └─ <case_id>/
│     ├─ case.json
│     ├─ source_manifest.json
│     ├─ sources/
│     ├─ assertions.json
│     └─ rubric.json
└─ schemas/
   ├─ case.schema.json
   ├─ trace_event.schema.json
   └─ evaluation_result.schema.json
~~~

case.jsonにはcase ID、type、ticker、as-of、horizon、source mode、expected status、適用evaluator、toleranceを持たせる。Reference research caseにはexpected recommendationまたは完成レポートを入れない。

assertions.jsonには次を持たせる。

- required material facts
- accepted values、unit、period、tolerance
- acceptable source IDs
- prohibited future sources
- known conflicts and critical gaps
- contract caseに限るexpected calculation / status / recommendation

Agent adapterへ渡すのはcase inputとsource bundleだけである。assertions.json、rubric.json、prohibited source/claim一覧はHarness内部に保持し、Agentから読み取れない場所へ配置する。

## 5. Agent adapter contract

HarnessからAgentへ1つのrun requestを渡す。

~~~json
{
  "run_id": "run-...",
  "case_id": "aapl-2025-06-30",
  "ticker": "AAPL",
  "as_of_date": "2025-06-30",
  "horizon_months": 24,
  "source_mode": "snapshot",
  "source_bundle_path": "...",
  "output_directory": "..."
}
~~~

Agentはoutput directoryへ次を生成する。

~~~text
report.json
report.md
trace.jsonl
sources.json
calculations.json
run_manifest.json
~~~

run_manifestにはagent version、model、prompt version、code revision、開始・終了時刻、token/cost、statusを含める。秘密情報やchain-of-thoughtはartifactへ保存しない。

## 6. Harness run lifecycle

1. Suiteとcase schemaを検証する
2. 隔離されたrun directoryとsource snapshotを準備する
3. Agent adapterをtimeout付きで実行する
4. stdout、stderr、exit code、artifactを保存する
5. Contract evaluatorを先に実行する
6. Hard gateを順番に実行する
7. Hard gate通過caseだけquality judgeへ送る
8. 判断不能をadjudication queueへ送る
9. case resultとsuite summaryを生成する
10. immutable run IDでartifactを保存する

Agent crash、timeout、artifact欠落はERRORとし、FAILと区別して報告する。ERRORはreleaseをblockする。

## 7. Evaluation result

Harnessはcaseごとに次を出力する。

~~~json
{
  "case_id": "aapl-2025-06-30",
  "run_id": "run-...",
  "verdict": "PASS",
  "hard_gates": {
    "passed": 17,
    "failed": 0,
    "review_required": 0
  },
  "quality": {
    "score": 82.5,
    "dimensions": {}
  },
  "forward_outcome": null,
  "evaluator_results": [],
  "artifact_paths": {},
  "versions": {}
}
~~~

verdictはPASS、FAIL、REVIEW_REQUIRED、ERRORのいずれかとする。suite summaryではhard-gate pass rate、quality score、cost、latencyを別々に表示し、単一の総合点へ統合しない。

## 8. Evaluator behavior

各evaluatorは次を返す。

- evaluator IDとversion
- PASS / FAIL / REVIEW_REQUIRED / NOT_APPLICABLE
- expected、actual、差分
- 対象artifact pathとJSON pointer
- 人間が再現できる短い理由

Judge evaluatorは固定model、固定prompt、固定rubricを使用する。Agent名、過去score、期待recommendationを見せない。Judgeの自由文だけで合否を決めず、構造化結果をschema検証する。

## 9. Harness self-tests

Harnessには既知の欠陥を注入したfixtureを持たせる。

- 基準日後のsource
- 引用と無関係なpassage
- 単位1000倍のfinancial value
- scenario probability合計90%
- 誤ったannualization
- margin of safety未達のBUY
- counter-thesis event欠落
- trace eventが存在するが参照artifactが欠落
- Tier 5のみのmaterial FACT
- supported / partial / unsupported citationのjudge fixture
- unsupported銘柄へのBUY
- report.json欠落とAgent timeout

各fixtureを対応evaluatorが必ず検出することをrelease前に検証する。

## 10. Initial implementation boundary

Harnessの最初のincrementでは、C001、C002、N001、N003、D001とcontract caseだけを実装する。次にsnapshot runnerとP001/P002/P004を追加し、その後citation judge、quality rubric、longitudinal evaluatorを実装する。

Harness本体は `src/eval_harness/`、Agent本体は `src/invest_agent/` に分ける。HarnessはAgent内部moduleをimportせず、processまたはadapter contract経由でだけ呼び出す。共通schemaとpolicy constants以外の実装共有を禁止する。

このincrementは実装済みである。`evals/suites/v1_contract.json`が正常系8件、`evals/suites/harness_self_test.json`が故障注入5件を実行する。現在のadapterは固定fixtureからartifactを生成するため、Agent本体とのprocess adapterおよびsnapshot source bundleは次incrementの対象である。
