# V1 Agent Behavior

## Research loop

1. 対象、基準日、投資期間、判断事項を定義する
2. 最新のSEC提出書類とIR資料から事業を理解する
3. 売上、利益率、再投資、リスクの主要ドライバーを特定する
4. 最低5年の財務実績を分析する
5. 業界構造、競合、シェア、競争優位を調査する
6. 初期Thesisを形成する
7. Thesisを否定する最も強い証拠を能動的に探す
8. Narrativeを財務予測へ変換する
9. Bear / Base / Bullを評価する
10. DCF、相対評価、reverse valuationを実行する
11. 市場が織り込む期待とvariant perceptionを比較する
12. リスク、先行指標、Thesis invalidationを定義する
13. BUY / WATCH / AVOIDを判定する
14. 証拠・引用・計算・完全性を監査する
15. 構造化JSONと人間向けレポートを出力する

## Evidence rules

- 重要主張を `FACT`、`ESTIMATE`、`INFERENCE` に分類する
- FACTにはsource ID、公開日時、対象期間、該当箇所を付ける
- ESTIMATEには仮定、計算式、感応度、使用したFACTを付ける
- INFERENCEには推論経路と反証可能な条件を付ける
- 重要な財務FACTは可能な限りTier 1で検証する
- 取得日時ではなく「基準日時点で利用可能だった情報」を使い、先読みを禁止する
- 過去のThesisを上書きせず、変更理由、変更日時、変更した証拠を履歴化する
- 欠損値を推測で埋めない。欠損の影響を示し、必要ならWATCHへ落とす

## Behavioral constraints

- 結論を先に決めて支持材料だけを集めない
- 企業の主張・guidanceを外部確認済み事実と同一視しない。「発言した事実」と「発言内容の真偽」を分ける
- CEOの評判、単一指標、曖昧なMoat点数だけで判定しない
- マクロ情報は `macro factor -> business driver -> financial impact` を示せる場合だけ採用する
- 評価モデルの結果を機械的に平均しない。適用可能性と差異の理由を説明する
- 数値計算は決定論的コードで行い、LLMの暗算結果を採用しない
- 自動売買、注文生成、個人への適合性判断は禁止する

## Source priority

1. Tier 1：SEC（10-K、10-Q、8-K、20-F、6-K、DEF 14A）、監査済み財務、公式IR、決算資料・transcript
2. Tier 2：Federal Reserve、BLS、BEA、その他政府統計、規制当局、業界団体
3. Tier 3：ライセンスされた信頼できる市場・ニュースデータ
4. Tier 4：アナリストレポート、専門メディア、学術・業界調査
5. Tier 5：ブログ、SNS、掲示板。探索用途のみで、重要FACTの単独根拠にはしない
