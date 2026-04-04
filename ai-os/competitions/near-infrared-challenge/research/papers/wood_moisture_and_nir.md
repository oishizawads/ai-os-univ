# Wood Moisture And NIR

## Scope

木材や木質バイオマスの含水率を NIR で予測する研究をまとめる。

## Key Sources

### 1. Estimation of moisture in wood chips by near infrared spectroscopy

- URL: https://revistas.ubiobio.cl/index.php/MCT/article/view/4076
- Accessed: 2026-04-02
- Relevance: 木材含水率そのものを NIR で推定する近い題材

What seems useful here:

- 木材 moisture 推定では PLS 系が自然なベースライン
- 今回の課題でも PLS を捨てる必要はなく、前処理と波長選択の質が重要

### 2. NIR Measurement of Moisture Content in Wood under Unstable Temperature Conditions

- URL: https://opg.optica.org/jnirs/abstract.cfm?origin=search&uri=jnirs-8-3-183
- Accessed: 2026-04-02
- Relevance: 木材 moisture に対する NIR の基礎的知見

What seems useful here:

- 水に関係する吸収帯の挙動が重要
- 条件差でスペクトルが動くため、一般化を落としやすい

### 3. Near-infrared spectroscopy for moisture content prediction in soil-mixed woody biomass

- URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC12902024/
- Accessed: 2026-04-02
- Relevance: 木質バイオマス moisture 予測における比較的新しい前処理知見

What seems useful here:

- `SNV + Savitzky-Golay` と `PLSR` の組み合わせが有望
- 今回の `SNV`, `SG微分`, `SNV+SG微分` の方向性は論文側とも整合的

## Interpretation For This Project

- 木材 moisture 予測では `PLS/PLSR` は依然として本命
- 強い候補は `SNV`, `SG微分`, `SNV+SG微分`
- 前処理だけでなく、モデルや波長選択との組み合わせを見るべき

## Candidate Experiments

- `SNV + SG微分 + PLS` を波長選択ありで再試行
- 水の吸収帯を重視した区間選択 PLS
- species ごとに壊れる fold を調べ、どの前処理が安定するか比較
