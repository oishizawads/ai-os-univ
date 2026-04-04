# VALIDATION_RULES.md

- CV不安定な案は本命にしない
- seed違いで崩れる案は保留
- OOF分析なしの改善案は信用しない
- public LBだけ良い案は採用しない
- 前処理変更時は baseline と差分比較する
- train / inference 不整合は即修正対象
- mean だけでなく std も評価する