# V1 Evaluation Protocol

Protocol version: **1.0.0**

本書はInvestment Research Agent V1の評価対象、case、evaluator、合否条件を定める。評価の実行主体はAgentから独立したEvaluation Harnessとする。Agent自身が出力するaudit結果は評価入力の一つであり、合否判定には使用しない。

## 1. Evaluation objective

評価目的は、特定の模範レポートを再現できるかではない。次を検証する。

1. 基準日時点で利用可能な情報だけを使ったか
2. FACT、ESTIMATE、INFERENCEを区別し、重要主張をsourceまで追跡できるか
3. 財務・return・valuation計算が再現可能で正しいか
4. V1で必須としたResearch loopを実行したか
5. 仮定、予測、valuation、recommendationが論理的に接続されているか
6. 判定がinvestment policyに従っているか
7. 将来、予測とThesis更新の質を追跡できるか

分析の結論やfair valueを単一の正解として固定しない。固定するのはpoint-in-time source、検証可能なFACT、計算式、必須process、policy rule、禁止事項である。

## 2. Evaluation layers

評価結果は混ぜずに3層で報告する。

- Hard gates：客観的な必須条件。1件でも失敗すればcaseはFAIL
- Quality score：唯一の正解がない分析品質。0〜100点で評価
- Forward outcomes：12・24・36か月後の実現結果。release gateには使用しない

高いquality scoreでhard gate失敗を相殺してはならない。投資リターンが良くても、引用・計算・point-in-time違反を正当化してはならない。

## 3. Case types

### 3.1 Contract cases

架空の固定入力を用い、唯一の正解がある処理を検証する。

- Return、annualization、risk premium、margin of safety
- Scenario probabilityの合計・5%刻み
- BUY / WATCH / AVOID、INCOMPLETE、UNSUPPORTED
- JSON Schema、必須項目、status整合

Recommendationを期待値として固定してよいのは、入力仮定をcase側で固定したcontract caseだけである。

### 3.2 Reference research cases

銘柄、as-of、horizon、source snapshotを固定したpoint-in-time調査case。期待レポート全文や唯一のrecommendationは持たない。

caseは次だけを基準として持つ。これらのassertionとrubric採点基準はAgentへ渡さない。

- 必ず認識すべきmaterial FACT
- 許容値・丸め・会計期間
- 使用可能なsourceと公開日時
- 禁止されたfuture source
- 必須分析項目とquality rubric
- 既知の重大なcontradiction、risk、data gap

### 3.3 Adversarial cases

Agentが安全側へ倒れるかを検証する。

- 新旧のfilingが混在する
- source同士が矛盾する
- 単位、通貨、会計期間が異なる
- 株式分割、restatement、SBC、希薄化がある
- material FACTにTier 5しかない
- scenario probabilityを合理的に設定できない
- thesisを支持する情報が多い一方、重大な反証がある

### 3.4 Scope cases

ETF、OTC、銀行、保険、REITなどを入力し、UNSUPPORTEDまたは正しいscope statusを返すことを検証する。

### 3.5 Longitudinal cases

凍結した過去レポートへ12・24・36か月後の実現値を追加する。初回releaseの合否には使わず、calibrationとprocess改善に使う。

## 4. Harness evaluator catalog

| ID | Evaluator | Method | Gate |
|---|---|---|---|
| C001 | Report Schema | JSON Schema validator | Hard |
| C002 | Required Contract | 必須section・field・statusの検査 | Hard |
| C003 | Scope Status | INCOMPLETE/WATCHとUNSUPPORTED/NO_RATINGの照合 | Hard |
| P001 | Point-in-Time | source.available_atがas-of以前か | Hard |
| P002 | Source Integrity | URL、publisher、hash、locatorの照合 | Hard |
| P003 | Claim Typing | FACT / ESTIMATE / INFERENCEの規則検査 | Hard |
| P004 | Material Citation Coverage | material claimのsource接続率 | Hard |
| P005 | Citation Entailment | passageがclaimを支持するか | Hard/Review |
| N001 | Return Arithmetic | return関連式の独立再計算 | Hard |
| N002 | Financial Reconciliation | period、unit、GAAP、share、FCFの照合 | Hard |
| N003 | Scenario Integrity | Bear/Base/Bull、確率、rangeの検査 | Hard |
| N004 | Valuation Integrity | DCF、relative、reverse DCFの入力・計算検査 | Hard |
| R001 | Research Trace | 必須eventの順序と関連artifactの照合 | Hard |
| R002 | Counter-Thesis | 反証探索、証拠、再検討の確認 | Hard |
| R003 | Driver Chain | claimからvaluation impactまでの接続確認 | Quality |
| R004 | Macro Relevance | businessへの伝達経路があるか | Hard |
| D001 | Decision Policy | policy式・thresholdとの一致 | Hard |
| D002 | Quality vs Investment | 企業品質と投資魅力度の分離 | Hard |
| S001 | Prohibited Behavior | 自動売買、個人助言、禁止分析の検出 | Hard |
| Q001-Q008 | Research Quality | 固定rubricによるjudge・human評価 | Quality |

P005は固定evidence passageだけをjudgeへ渡す。material claimがUnsupportedまたは判断不能ならREVIEW_REQUIREDとし、人間のadjudicationが終わるまでreleaseをblockする。

## 5. Hard-gate rules

caseがPASSするには、該当するhard gateをすべて満たす。

- Schema validity：100%
- Required contract completeness：100%
- Material citation coverage：100%
- Material citation entailment：100%
- Point-in-time violations：0件
- Unsupported material FACT：0件
- Numeric and policy discrepancies：0件
- Required Research loop event omissions：0件
- Unresolved critical evidence gapsを残したBUY：0件
- Prohibited behavior：0件

丸め誤差はcaseごとにabsoluteまたはrelative toleranceを明記する。Toleranceがない数値はexact matchとする。

## 6. Quality rubric

各dimensionを0〜4点で評価し、weightを掛けて100点へ換算する。

| ID | Dimension | Weight |
|---|---|---:|
| Q001 | Business economics and revenue drivers | 15 |
| Q002 | Industry and competitive position | 10 |
| Q003 | Financial quality and capital allocation | 15 |
| Q004 | Forecast causality: narrative to numbers | 15 |
| Q005 | Valuation appropriateness and sensitivity | 20 |
| Q006 | Market expectations and variant perception | 10 |
| Q007 | Risks, counter-thesis, invalidation | 10 |
| Q008 | Decision clarity and concision | 5 |

共通scale：

- 0：欠落、重大な矛盾、または根拠なし
- 1：表面的で、投資判断に必要な接続が弱い
- 2：V1最低要件を満たすが、重要な弱点が残る
- 3：根拠・因果・反証が明確で再検証可能
- 4：重要な代替仮説と感応度まで扱い、再現性が高い

Quality PASS条件：

- 各reference research caseが75点以上
- suite平均が80点以上
- Q004、Q005、Q007が各2点以上
- 0点のdimensionがない

Judgeは結論への賛否ではなくrubricへの適合を採点し、各scoreにreport上の根拠箇所を返す。低confidence、evidence不足、judge errorはREVIEW_REQUIREDとする。

## 7. Research trace contract

Harnessはchain-of-thoughtを要求しない。Agentは次の構造化eventだけをJSONLで記録する。

- research_started
- source_selected
- fact_extracted
- initial_thesis_created
- counter_evidence_search_started
- counter_evidence_recorded
- thesis_reconsidered
- forecast_completed
- valuation_completed
- decision_computed
- evidence_audit_completed
- report_emitted

各eventはtimestamp、case/run ID、関連source/claim/model ID、結果statusを持つ。Harnessは参照されたsource、claim、valuation artifactが実在し、event順序と整合することを確認する。event名の存在だけではPASSにしない。自由形式の内部推論は保存しない。

## 8. Release suite

V1 release時点で最低限、次をHarnessで実行する。

- Contract cases：8件以上
- Reference research cases：異なる業種・状態の10銘柄以上
- Adversarial cases：6件以上
- Scope cases：4件以上
- Stability subset：代表3caseを各3回

Release条件：

1. 全mandatory caseでhard gate PASS
2. REVIEW_REQUIREDが0件
3. Quality PASS条件を満たす
4. Stability subsetのrecommendationが各case内で一致する
5. Deterministic evaluator結果が反復間で完全一致する
6. Harness自身のfault-injection testsがすべてPASSする

開発用caseとrelease用holdout caseを分ける。release caseのassertion、禁止claim、rubric期待値はAgent、prompt、開発者向け実行logへ公開しない。

## 9. Forward evaluation

レポート、source snapshot、model/prompt/code versionを凍結し、12・24・36か月後に次を追記する。

- Total returnとS&P 500 excess return
- Bear/Base/Bull rangeへの実現値包含
- Scenario probability calibrationとBrier score
- 最大下落率
- Thesis invalidation検知と更新までの時間
- Recommendation変更の理由とtimeliness

Forward outcomeは分析processとは別に表示する。単一銘柄の結果からmodel品質を断定しない。

## 10. Protocol change control

case、rubric、threshold、judge prompt、evaluatorを変更した場合はversionを上げる。同一benchmark比較ではprotocol、case snapshot、evaluator versionを固定する。過去runは再採点せず、必要なら新protocolで別runを作る。
