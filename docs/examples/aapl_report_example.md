# AAPL Investment Research Report（構造例）

> 本文の価格、財務数値、仮定、source URLは仕様確認用の架空データであり、実際のAAPL分析や投資助言ではない。

## 1. Investment Summary

| 項目 | 値 |
|---|---|
| Ticker / Company | AAPL / Apple Inc. |
| As of | 2026-08-24 |
| Current Price | $200.00（架空、2026-08-24T20:00:00Z） |
| Recommendation | WATCH |
| Investment Horizon | 24か月 |
| Intrinsic Value As Of | Bear $145 / Base $230 / Bull $285 |
| Horizon Target Range | Bear $155 / Base $240 / Bull $300 |
| Base-case Total Return | +21.0%（累積配当込み） |
| Expected Total Return | +17.9%（確率加重） |
| Expected Annualized Return | +8.6% |
| Risk Premium | +4.6pt（架空の2年Treasury 4.0%比） |
| Margin of Safety | 13.0%（基準日時点のBase intrinsic value比） |
| Decision Hurdle | 10.0%年率 |
| Confidence | Medium |
| Business Quality | Strong |
| Investment Attractiveness | Watchlist |

Core Thesis:

- Appleのエコシステムと顧客switching costは継続収益と高いcash generationを支える。[C1: INFERENCE]
- Servicesとinstalled baseの成長がhardware成熟化を部分的に補う。[C2: ESTIMATE]
- 企業品質は高いが、確率加重年率期待リターン8.6%はBUY hurdle 10.0%を下回る。

Why now：最新決算後にServices成長とvaluation expectationsを再評価する局面。

Primary Risk：hardware需要の停滞と規制により、Services成長・marginの前提が同時に崩れること。

## 2. Business

Appleはdevice販売と、installed baseへ提供するServicesから収益を得る。主要driverは device units * ASP と active devices * paid service penetration * ARPU に分解する。hardwareはtransactional、Servicesは相対的にrecurringで、製品mixがgross marginを左右する。[C3: INFERENCE]

## 3. Industry & Competition

Competitive advantage：Strong

- Source：brand、integrated hardware/software、switching costs、developer ecosystem
- Evidence：継続率、installed base、Services利用、segment marginの一次資料を確認する
- Durability：5年以上継続する可能性があるが、永久ではない
- Threat：規制によるplatform economicsの変化、競合AI ecosystem、端末更新周期の長期化

## 4. Financial Analysis

最低5年についてRevenue、gross/operating margin、EPS、OCF、CapEx、FCF、ROIC、cash/debt、diluted share count、SBC、buybackを比較する。この例では数値を省略するが、実レポートではGAAP値、計算式、source IDを各系列に付ける。

- FCF：Operating Cash Flow - CapEx
- ROIC：NOPAT / Average Invested Capital
- 株主1株当たり分析ではbuybackによるshare減少とSBCによる希薄化を両方反映する

## 5. Future Drivers

| Driver | Economic mechanism | Financial impact | Valuation impact |
|---|---|---|---|
| Services growth | Installed base * penetration * ARPU | Revenue CAGRとmargin上昇 | FCF増加 |
| Device replacement | Units * ASP | Product revenueとmix | Base/Bearの差 |
| AI monetization | Adoption * monetization | R&D負担後の増分利益 | Growth duration |

Macro要因は、為替が海外売上のtranslationと需要へ与える影響など、会社への伝達経路を推定できる場合だけ反映する。

## 6. Management

評価対象はguidance accuracy、製品実行、R&D/M&A、buyback価格、報酬と株主利益の整合、governanceである。経営者の知名度や発言だけでは評価しない。

## 7. Valuation

### DCF

基準日時点のBase intrinsic valueは架空の$230、24か月後のBase target valueは$240。Revenue、operating margin、tax、reinvestment、WACC、terminal growth、net cash、diluted sharesを明示し、WACCとterminal growthの感応度を付ける。

### Relative valuation

自身の過去と適切なpeerをP/E、EV/EBITDA、FCF yieldで比較する。基準日時点に換算した架空のcross-check rangeは$225〜$250。DCFと単純平均せず、差の原因を説明する。

### Reverse valuation

架空の現在価格$200を正当化する成長率・marginを逆算し、市場がServices成長と高marginの継続をどこまで織り込んでいるかを示す。

## 8. Market Expectations

- Market appears to expect：Servicesが二桁成長し、全社marginが維持される
- Our view：方向性には同意するが、成長率とregulatory riskへの価格上の余裕は小さい
- Difference：市場より低いServices成長と広いdownside rangeを置く
- Why market may be wrong：直近の高成長を長期へ外挿し、規制の経済的影響を過小評価している可能性

これは市場参加者の直接観測ではなく、reverse valuationからのINFERENCEである。

## 9. Counter-Thesis

最も強い反証は、Services成長、installed base monetization、share reductionが想定以上に続き、現在価格でも十分な複利リターンを生む可能性である。この反証を受け、AVOIDではなくWATCHとし、次回決算でdriverを再評価する。

## 10. Scenarios

| Scenario | Probability | Intrinsic Value As Of | Horizon Target | Dividends | Total Return | Annualized |
|---|---:|---:|---:|---:|---:|---:|
| Bear | 25% | $145 | $155 | $2 | -21.5% | -11.4% |
| Base | 50% | $230 | $240 | $2 | +21.0% | +10.0% |
| Bull | 25% | $285 | $300 | $2 | +51.0% | +22.9% |

~~~text
expected_total_return
= 0.25 * (-21.5%) + 0.50 * 21.0% + 0.25 * 51.0%
= 17.875%

expected_annualized_return
= (1 + 0.17875)^(12 / 24) - 1
= 8.6%
~~~

## 11. Catalysts

- 次回決算でのServices growthとmargin
- AI機能の利用・収益化指標
- 規制判断
- 明確な短期catalystがなくても、FCF per shareの複利成長を監視する

## 12. Risks

| Risk | Probability | Impact | Leading Indicator | Thesis Invalidation |
|---|---|---|---|---|
| Services規制 | Medium | High | 手数料率、規制判断、segment margin | Base margin前提を継続的に下回る |
| Device需要低下 | Medium | High | Units、replacement cycle、channel inventory | Revenue driverが2期連続でBaseを下回る |
| AI収益化失敗 | Medium | Medium | Adoption、R&D、ARPU | 投資増加に対し増分FCFが確認できない |

## 13. Conclusion

WATCH。基準日時点のBase intrinsic valueに対するmargin of safetyは13.0%、確率加重年率期待リターンは8.6%であり、いずれもBUY基準未達である。

BUYへの変更条件：価格低下、Services/AI driverの上方確認、またはdownside縮小により期待年率がhurdleを超える。

AVOIDへの変更条件：基準日時点のBase intrinsic valueが現在価格以下になる、重大なgovernance問題、または主要Thesis invalidationが成立する。

## Sources

| ID | Tier | Source | Published | Locator |
|---|---:|---|---|---|
| S1 | 1 | https://example.com/aapl-10-k | 架空 | Business / Financial Statements |
| S2 | 1 | https://example.com/aapl-earnings | 架空 | Earnings release |

実レポートでは各material FACTをclaim ID経由でsourceの該当箇所へ接続する。
