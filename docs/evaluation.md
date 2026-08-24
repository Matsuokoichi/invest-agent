# V1 Evaluation

## Release gates

V1は投資成績より先に、リサーチ過程の正確性と再現性を評価する。Golden setは異なる業種・企業状態を含む10銘柄以上とし、各ケースに基準日、期待される主要FACT、許容source、計算結果、重大リスクを持たせる。

| 指標 | 定義 | V1合格基準 |
|---|---|---:|
| Schema validity | 最終JSONのSchema通過率 | 100% |
| Required-section completeness | 必須項目の充足率 | 100% |
| Material-claim citation coverage | 重要主張のうちsourceが付いた割合 | 100% |
| Material-claim citation entailment | sourceが重要主張を実際に支持する割合 | 100% |
| Overall citation entailment | 全引用でsourceが主張を支持する割合 | 95%以上 |
| Tier 1 financial fact coverage | 重要財務FACTをTier 1で裏付けた割合 | 95%以上 |
| Point-in-time correctness | 基準日後の情報を使用しなかった割合 | 100% |
| Numeric accuracy | 再計算と一致する数値の割合 | 100% |
| Hallucination rate | 根拠のない重要FACTの割合 | 0% |
| Counter-thesis completion | 反証探索と再検討を実施した割合 | 100% |
| Decision-policy consistency | 判定が方針の閾値と一致する割合 | 100% |

## Human rubric

各項目を0〜2点で評価する。

- Business economics：売上・コストを経済ドライバーまで分解している
- Forecast causality：Narrativeが数値予測とvaluationへ接続されている
- Competitive analysis：優位性の根拠、持続性、脅威が説明されている
- Valuation appropriateness：企業に適した手法と感応度を使っている
- Variant perception：市場期待と独自見解の差が具体的である
- Risk quality：先行指標とThesis invalidationが検証可能である
- Concision：5つの投資判断上の問いに不要な情報を抑えている

各項目1点以上、合計11/14以上を合格とする。

## Forward evaluation

運用開始後はレポートを基準日時点で凍結し、12・24・36か月で次を測る。

- 価格リターンと配当込みtotal return
- S&P 500に対するexcess return
- BUY / WATCH / AVOID別の結果
- Bear / Base / Bullレンジへの実現値の包含率
- 数値確率を出したレポートのcalibration、Brier score、最大下落率
- Thesis invalidationの検知速度と更新判断

取引コスト、税、ポートフォリオ構築を含まないため、これらは銘柄リサーチ品質の評価であり、運用戦略のバックテストではない。
