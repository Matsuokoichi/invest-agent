# V1 Evaluation Policy

評価はAgent本体から独立したEvaluation Harnessが実行する。詳細なcase、evaluator、合否条件は [V1 Evaluation Protocol](evaluation_protocol.md)、実行契約は [Evaluation Harness Specification](evaluation_harness.md) を正規文書とする。

## Evaluation model

結果を次の3層に分け、単一scoreへ統合しない。

- Hard gates：Schema、point-in-time、source、citation、計算、Research loop、decision policy、安全制約
- Quality score：Business、competition、financials、forecast、valuation、variant perception、risk、clarity
- Forward outcomes：12・24・36か月後のreturn、calibration、Thesis更新

完成レポートや唯一のfair valueを正解として固定しない。Contract caseだけがexpected recommendationを持ち、Reference research caseは検証可能なFACT、利用可能source、必須process、rubricを持つ。

## Release criteria

- Contract cases：8件以上
- Reference research cases：10銘柄以上
- Adversarial cases：6件以上
- Scope cases：4件以上
- Stability subset：3caseを各3回
- 全mandatory hard gateがPASS
- REVIEW_REQUIREDとERRORが0件
- 各research caseが75点以上、suite平均80点以上
- Harness fault-injection testsがすべてPASS

Forward outcomeは初回releaseをblockしない。投資結果が良くても、point-in-time、引用、計算、policy違反を正当化しない。
