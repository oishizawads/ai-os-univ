# review-exp

## Objective
実験コード・結果・設計の整合性をレビューし、採否判断まで行う。

## When to Use
- 実験実装後
- 学習後
- submission 前
- 改善案を本命候補に上げる前

## Review Scope
以下をセットで見る。
- `.steering/`
- 実験ディレクトリ
- `train.py`
- `inference.py`
- `settings.py`
- `notes.md`
- `result.md`
- `SESSION_NOTES.md`

## Review Axes
1. objective alignment
2. validation quality
3. train / inference parity
4. leakage risk
5. reproducibility
6. config clarity
7. logging / saved artifacts
8. complexity vs gain
9. baselineとの差分説明
10. next-step usefulness

## Output Format

### Summary
-

### Good Points
- 
- 
- 

### Critical Issues
- 
- 
- 

### Medium Issues
- 
- 
- 

### Nice to Have
- 
- 
- 

### Adopt Decision
以下から1つ選ぶ。
- Adopt now
- Fix then adopt
- Keep as reference only
- Discard

### Why
-

### Recommended Next Experiment
1.
2.
3.

## Hard Rules
- スコアだけで褒めない
- validation が怪しい改善は採用しない
- train / inference 不整合は critical 扱い
- baselineとの差分を説明できない実験は保留寄りに扱う