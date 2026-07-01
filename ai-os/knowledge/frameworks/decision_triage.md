---
title: "意思決定トリアージ（何をやる/何を捨てる）"
type: framework
domain: general
tags: [decision, prioritization, opportunity-cost, overload]
created: 2026-06-18
source:
  title: "Two-way door (Bezos 2015 Letter) / Hell yes or no (Sivers) / Satisficing (Simon 1956) / WSJF (SAFe)"
  author: "Jeff Bezos, Derek Sivers, Herbert Simon, SAFe"
---

## 原則
過密化は「何をやるか」でなく「**何を捨てるか・どれだけ悩むか**」の設計ミスで起きる。決定ごとに"重さ"を変える。

## 判断基準（順に当てる）
1. **可逆性で悩む量を決める（Two-way door / Bezos）**: 元に戻せる決定(Type2)は即決・任せる。戻せない決定(Type1=公開/契約/破壊的変更)だけ慎重に。**全決定を同じ重さで悩むのが最大の生産性損失**。
2. **オファーは"絶対Yes"だけYes（Hell yes or no / Sivers）**: "たぶんYes"は全部No。案件打診・新技術・協業の機会費用フィルタ。
3. **最適でなく十分で止める（Satisficing / Simon）**: 決定前に「この決定の"十分条件"は何か」を先に書く。満たす最初の解で確定＝完璧主義によるスコープ肥大を防ぐ。
4. **並行タスクは定量順位（WSJF / SAFe）**: (価値+時間切迫+リスク低減) ÷ ジョブサイズ。「なんとなく重要」を「遅らせたら何を失うか」に変換。複数クライアント並行時。

## 手順
- 新タスク/打診が来たら: 可逆か？ → 絶対Yesか？ → 十分条件は？ の順で30秒トリアージ。
- 週次で WSJF を再計算しキューを並べ替える。

## 失敗例
- 可逆な技術選定を会議で長時間議論（Type2をType1扱い）。
- "面白そう"で受けて過密化（Hell-yesでないものをYes）。
- 「最適なツール」を比較し続けて着手が遅れる（十分条件を決めてない）。

関連: [[META_MAP]] ③決める層 / 認知バイアス「過密スケジュール化」への直接対策。
