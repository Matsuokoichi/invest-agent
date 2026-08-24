# V1 投資方針

## 投資思想

- Fundamental / Long-only
- 企業の本源的価値と市場価格の乖離を探す
- 「良い企業か」ではなく「現在価格で、リスクに見合う期待リターンがあるか」を判断する
- 銘柄単体のリサーチであり、個人向け助言、ポートフォリオ適合性評価、注文執行は行わない

## 対象と期間

- 対象：NYSEまたはNasdaqに上場する普通株式・ADR
- 投資期間：12〜36か月（未指定時は24か月）
- DCF明示予測期間：原則5年。安定化に時間を要する場合は最大10年
- 除外：ETF、投資信託、オプション、レバレッジ商品、OTC、上場前企業、買収前SPAC
- 銀行、保険、REIT、資源開発企業など通常のFCFF DCFが不適切な企業は、V1では `UNSUPPORTED` とする

## リターンの定義

各Bear / Base / Bullシナリオについて、基準日時点の本源的価値と、投資期間末の希薄化後target valueを分けて推定する。

```text
scenario_total_return = (target_value_at_horizon + dividends - current_price) / current_price
expected_total_return = sum(scenario_probability * scenario_total_return)
expected_annualized_return = (1 + expected_total_return)^(12 / horizon_months) - 1
risk_premium = expected_annualized_return - matched_maturity_us_treasury_yield
margin_of_safety = (base_intrinsic_value_as_of - current_price) / base_intrinsic_value_as_of
decision_hurdle = max(10%, treasury_yield + 5%)
```

- シナリオ確率は5%刻み、合計100%とし、推定であることを明示する
- 確率を合理的に置けない場合、`expected_return` は `null`、判定は `WATCH`
- Base-case returnと確率加重Expected returnを混同しない
- 株価日時、通貨、配当、希薄化、税引前であることを明記する
- 5%の上乗せ幅と10%の下限はV1運用パラメータであり、評価結果から再校正する

## 判定基準

### BUY

以下をすべて満たす場合に限る。

- 確信度がMediumまたはHigh
- 確率加重年率期待リターンが `decision_hurdle` 以上
- 基準日時点のBase intrinsic valueに対するmargin of safetyが15%以上
- Bearケース、主要リスク、反証を明示済み
- 重大な証拠不足、会計・ガバナンス懸念、Thesis invalidationがない

### WATCH

- 企業品質は調査継続に値するが、価格、安全余地、確信度のいずれかがBUY基準未達
- データ不足・陳腐化、評価モデル不一致、合理的なシナリオ確率を置けない
- 何が変わればBUYまたはAVOIDになるかを必ず示す

### AVOID

- 確率加重期待リターンが0以下、またはMedium/High confidenceで基準日時点のBase intrinsic valueが現在価格以下
- Thesisが反証された、重大な会計・ガバナンス問題がある、または下方非対称性が大きい
- 「情報不足」はAVOIDではなくWATCHとする

## 確信度

- High：主要仮定が複数の最新一次情報で支持され、評価法間の乖離と感応度を説明できる
- Medium：合理的根拠はあるが、重要仮定または評価レンジに不確実性が残る
- Low：証拠が不足・矛盾・陳腐化している、または未検証仮定への依存が大きい

## 必須分析

Business economics、Industry and competition、Financial quality、Capital allocation、Management、Future drivers、Valuation、Reverse valuation、Variant perception、Catalysts、Risks、Bear/Base/Bull、Thesis invalidationを扱う。詳細は [V1正規仕様](v1_specification.md) に従う。
