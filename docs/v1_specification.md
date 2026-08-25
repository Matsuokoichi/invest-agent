# Investment Research Agent V1 正規仕様

Status: **Approved for V1 implementation**

Schema version: **1.0.0**

本書をV1の正規仕様とする。詳細ルールは `investment_policy.md`、`agent_behavior.md`、`architecture.md`、`evaluation.md`、`evaluation_protocol.md`、`evaluation_harness.md` に分割する。矛盾がある場合は本書を優先する。

## 1. Mission

市場価格を短期予測するAIではなく、米国上場株について検証可能な投資仮説を構築・反証・更新するFundamental / Long-only Research Agentを作る。

目的は企業紹介ではない。企業の将来cash flowと本源的価値を推定し、現在価格で十分なrisk premiumとmargin of safetyがあるかを判定する。

Agentは最終的に次の5問へ答える。

1. 会社はどのように利益とcash flowを生むか
2. 主要driverにより将来の利益・cash flowはどう変わるか
3. 予測を壊す事象と先行指標は何か
4. 将来cash flowの現在価値はいくらか
5. 現在価格でリスクに見合う期待リターンがあるか

## 2. Scope

- 対象：NYSE / Nasdaq上場の普通株式・ADR
- 投資期間：12〜36か月、default 24か月
- スタイル：Bottom-up fundamental、long-only
- 判定：BUY / WATCH / AVOID。対象外はUNSUPPORTED、監査未完了はINCOMPLETE
- 基準日：point-in-time。基準日後に公開された情報を使用しない
- V1非対応：特殊なvaluation modelを要する銀行、保険、REIT、資源開発企業
- V1除外：technical indicators、day trading、options、portfolio optimization、social sentiment、ML price prediction、autonomous trading、multi-agent debate、大規模macro予測

## 3. Required report contract

### 3.1 Investment Summary

Ticker、company、as-of、current priceとtimestamp、recommendation、investment horizon、基準日時点のintrinsic value range、horizon target range、Base-case return、probability-weighted expected return、annualized return、risk premium、margin of safety、confidence、Core Thesis、Why Now、Primary Riskを最初に示す。

Business QualityとInvestment Attractivenessを別に表示する。良い企業でも高すぎればWATCHまたはAVOIDになり得る。

### 3.2 Business Economics

Products / services、segments、geographies、customers、recurring revenue、cyclicality、capital intensity、cost structure、gross/operating marginを扱う。売上を可能な限り `volume * price`、`customers * usage * price`、`market size * share` などのdriverへ分解する。

### 3.3 Industry and Competition

業界境界、成長率、主要競合、market shareとtrend、参入障壁、switching costs、network effects、scale、brand / IP、supplier/customer power、substitutesを分析する。

Competitive advantageはStrong / Moderate / Weakとし、source、evidence、durability、threatを併記する。根拠のない小数点scoreは禁止する。

### 3.4 Financial Quality and Capital Allocation

原則5年以上のRevenue、operating income、EPS、OCF、CapEx、FCF、margins、ROIC、ROE、cash、debt、interest coverage、debt maturity、share count、SBC、buybacks、dividendsを確認する。

- `FCF = operating cash flow - capital expenditures` を基本とし、別定義は明示する
- `ROIC = NOPAT / average invested capital` を基本とし、NOPATとinvested capitalの調整を開示する
- GAAPとadjusted metricを分ける
- SBCを費用・希薄化の両面から扱う
- M&A、R&D、CapEx、buyback、dividend、debt repaymentの成果を評価する

### 3.5 Management

Execution record、guidance accuracy、capital allocation、insider ownership、compensation incentives、strategic consistency、accounting/governance issuesで評価する。発言ではなく実績とインセンティブを重視する。

### 3.6 Future Drivers and Macro

3〜5個の主要driverに絞り、各driverを次のchainで表す。

```text
Claim -> Economic mechanism -> Financial impact -> Valuation impact
```

Macroは `macro factor -> business driver -> financial impact` を具体化できる場合だけ掲載する。独立したGDP、金利、為替予想の羅列は禁止する。

### 3.7 Valuation

1. Intrinsic valuation：原則FCFF DCF。Revenue、margin、tax、reinvestment、FCF、WACC、terminal assumptions、net debt、diluted sharesを開示し、基準日時点のpresent valueと投資期間末のtarget valueを分ける
2. Relative valuation：自身の過去と適切なpeerをP/E、EV/EBITDA、EV/Sales、FCF yieldなどで比較する
3. Reverse valuation：現在価格が暗示するgrowth、margin、reinvestment、terminal assumptionsを逆算する

DCFとrelative valuationは独立したcross-checkであり、単純平均しない。モデル選択理由、感応度、terminal value比率、モデル間差異を説明する。

### 3.8 Market Expectations and Variant Perception

次を必須とする。

- Market appears to expect
- Our thesis
- Difference
- Evidence supporting our view
- Why the market may be wrong
- 何が既に価格へ織り込まれているか

市場期待は観測不能な推定であり、FACTではなくINFERENCEとして扱う。

### 3.9 Scenarios, Catalysts, and Risks

Bear / Base / Bullを作成し、各シナリオにdriver assumptions、intrinsic value as of、target value at horizon、return、probabilityを持たせる。確率は5%刻みとし、合計100%にする。合理的に確率化できない場合は期待値を出さずWATCHとする。

Catalystは必須ではない。業績・cash flowの複利成長自体を長期的な再評価要因としてよい。

各riskはprobability、impact、evidence、leading indicators、thesis implication、invalidation conditionを持つ。

### 3.10 Conclusion

Recommendation、理由、未解決事項、次回確認項目、判定を変える条件を示す。判定ルールは `investment_policy.md` に従う。

## 4. Evidence contract

重要主張はFACT / ESTIMATE / INFERENCEのいずれかに分類する。sourceにはURL、publisher、title、source tier、published_at、retrieved_at、対象期間、引用箇所を保存する。

- FACT：sourceに直接記載された検証可能な情報
- ESTIMATE：将来予測、intrinsic value、horizon target、scenario probabilityなどのモデル出力
- INFERENCE：複数のFACTから導く解釈、moat、market expectation、variant perception

Tier 1はSEC提出書類、監査済み財務、公式IR・決算資料を中心とする。Tier 5は探索にのみ使い、重要FACTの単独根拠にしない。引用はURLの存在だけでなく、source内容がclaimを支持するか監査する。

## 5. Autonomous research loop

Define -> Understand Business -> Identify Drivers -> Financial Analysis -> Industry Research -> Initial Thesis -> Search Against Thesis -> Forecast -> Valuation -> Reverse Valuation -> Compare Market Expectations -> Risk Analysis -> Recommendation -> Evidence Audit -> Report

`Search Against Thesis` は省略不可。最も強い反証を探し、Thesis、確信度、シナリオ、判定を再検討した履歴を残す。

## 6. Quality and safety gates

- 最新提出書類と重要current reportを基準日時点で確認する
- 数値は決定論的コードで再計算する
- 重要FACTのcitation coverageを100%にする
- FACTと推論を分離する
- missing data、model limitation、conflictを明示する
- すべてのBUYで反証、Bear case、invalidation conditionを必須にする
- personalized advice、position sizing、注文実行を行わない

## 7. V1 completion criteria

V1完成とは、独立したEvaluation Harnessがversioned Reference Evaluation Suiteを実行し、同一snapshotから再現可能なJSON、Markdown、構造化traceを生成して、`evaluation_protocol.md` のrelease条件を満たすことをいう。リターン実績は継続評価項目であり、初回リリースの合否条件にはしない。

## 8. Design basis

- [CFA Institute: Equity Valuation—Concepts and Basic Tools](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/equity-valuation-concepts-basic-tools)
- [CFA Institute: Company Analysis—Past and Present](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/company-analysis-past-and-present)
- [CFA Institute: Industry and Competitive Analysis](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/industry-and-competitive-analysis)
- [CFA Institute: Standard V(A), Diligence and Reasonable Basis](https://www.cfainstitute.org/standards/professionals/code-ethics-standards/standards-of-practice-v-a)
- [Aswath Damodaran: Numbers and Narrative](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/numbers%26narrative.htm)
- [Aswath Damodaran: Introduction to Valuation](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/background/valintro.htm)
- [Oaktree: Thinking About Macro](https://www.oaktreecapital.com/insights/memo/thinking-about-macro)
- [SEC: Search Filings and EDGAR](https://www.sec.gov/search-filings)
