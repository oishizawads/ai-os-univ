# eda

## Objective
EDAを「何となく眺める作業」ではなく、仮説形成とモデリング前のリスク確認に変える。

## When to Use
- 新しいデータを初めて触る時
- ベースライン前
- スコアが不安定な時
- OOFや予測が壊れている時
- 特徴量追加の前

## Standard EDA Flow

### Phase 1: Schema Check
- shape
- columns
- dtypes
- missing
- duplicates
- target availability
- id columns
- date/time columns
- categorical / numerical split

### Phase 2: Distribution Check
- target distribution
- major feature distributions
- skew / outliers
- train-test drift suspicion
- segment differences

### Phase 3: Leakage / Validation Check
- target-like columns
- post-event columns
- split mismatch risk
- grouped samples
- time leakage risk
- preprocessing fit/transform mismatch risk

### Phase 4: Failure Analysis Setup
- what should be checked in OOF
- what segments may fail
- what plots are needed before harder modeling

## Output Format

### EDA Objective
-

### Priority Checks
1.
2.
3.

### Observations
- 
- 
- 

### Leakage / Validation Suspicion
- 
- 
- 

### What to Visualize Next
- 
- 
- 

### What to Check Before Modeling Harder
- 
- 
- 

### Immediate Next Action
1つだけ書く。

## Hard Rules
- ただ「分布を見ました」で終わらない
- 可視化の目的を書く
- 競技なら CV / leakage に必ず触れる
- 業務なら粒度・定義・利用可能性に必ず触れる