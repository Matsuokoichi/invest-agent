# V1 Architecture

## 方針

V1は単一のオーケストレーターが明示的なResearch loopを実行する。Multi-agent debateは採用しない。LLMは検索計画、文章理解、仮説形成、説明に使い、財務計算、バリュエーション、スキーマ検証は決定論的コードで行う。

## Components

```text
CLI / API
  -> Research Orchestrator
     -> Source Connectors (SEC, IR, market/macro data)
     -> Evidence Store (documents, passages, timestamps, claim links)
     -> Financial Normalizer (periods, units, GAAP, shares)
     -> Analysis Engine (drivers, forecasts, risks, counter-evidence)
     -> Valuation Engine (DCF, relative, reverse DCF, sensitivity)
     -> Decision Engine (policy thresholds)
     -> Evidence Auditor (citations, freshness, contradictions)
     -> Report Renderer (validated JSON -> Markdown)
```

## Core records

- `SourceRecord`：URL、source tier、publisher、published_at、retrieved_at、as-of availability、document hash
- `ClaimRecord`：FACT / ESTIMATE / INFERENCE、本文、source IDs、reasoning、confidence
- `FinancialSeries`：metric、period、value、unit、GAAP/adjusted、source、restatement status
- `ThesisVersion`：version、created_at、claims、counter-evidence、change reason、invalidation conditions
- `ValuationRun`：model、inputs、outputs、sensitivities、code version
- `ResearchReport`：`docs/report_schema.json` に準拠する最終成果物

## Processing gates

1. Scope gate：対象銘柄・評価モデルをV1が扱えるか
2. Freshness gate：基準日時点の最新10-K/10-Q/20-Fと、その後の重要8-K/6-Kを確認したか
3. Evidence gate：重要FACTに根拠があり、FACTと推論が分離されているか
4. Model gate：単位、期間、希薄化、FCF、discount rate、terminal valueを検証したか
5. Counter-thesis gate：反証探索を実施したか
6. Decision gate：投資方針の判定条件と一致するか
7. Schema gate：JSON Schemaを通過するか

いずれかの重大gateが失敗した場合はレポートを `INCOMPLETE` とし、BUYを禁止する。

## Storage and reproducibility

- 原文、抽出箇所、計算入力、モデル版、prompt版、生成日時を保存する
- 同じsnapshotとcode versionから同じ数値結果を再現できるようにする
- レポート更新は新しいThesisVersionを作り、過去版を保持する
- 市場データ・ニュースの利用規約と再配布制約を記録する

## V1 interface

```text
invest analyze <TICKER> [--as-of YYYY-MM-DD] [--horizon 12|24|36]
```

出力は検証済みJSON、Markdownレポート、評価結果、使用source一覧とする。
