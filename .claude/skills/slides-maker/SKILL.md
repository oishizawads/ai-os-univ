---
name: slides-maker
description: 日本語のプレゼン資料やPowerPoint/PPTXの作成・改善を行う。slides、presentation、deck、McKinsey style、BCG style などの依頼で使う。
---

# Slides Maker

## Mission
日本語のコンサル調スライドを、内容整理からPPTX化まで一貫して進める。

## Read Only What You Need
必読:
```text
Read /mnt/skills/public/pptx/SKILL.md
Read /mnt/skills/public/pptx/pptxgenjs.md
```

デザイン指定や既存テンプレートに合わせる必要がある場合だけ読む:
```text
Read slides-maker/references/design-system.md
```

## Workflow
1. 依頼から目的、対象読者、意思決定、必要スライド数を確定する。
2. 先にストーリーを作る。各スライドは `title / key message / evidence / visual` を1行ずつでよい。
3. 作るべき図解を決める。2x2、比較表、フロー、タイムライン、箇条書きのどれかに寄せる。
4. その後でPPTXを実装する。本文より余白と整列を優先する。
5. 最後に全スライドの一貫性を確認する。

## Recommended Deck Shape
- 基本構成は `title / executive summary / context / analysis / recommendation` とする。
- 分析スライドは 2 から 4 枚を目安にする。
- 各スライドタイトルはトピック名ではなく、結論や示唆を言い切る。

## Default Rules
- 1スライド1メッセージ。情報過多にしない。
- 文章ではなく見出しと要点で伝える。
- 装飾より可読性を優先する。
- 指定がなければ白背景のコンサル調にする。
- 数字、比較、結論を優先して置く。
- 各コンテンツスライドに visual を最低1つ置く。箇条書きだけで終わらせない。
- タイトル下に細い区切り線を置き、全スライドで整列基準を揃える。
- 日本語では全角の `。` `、` を使い、英数字は読みやすさを優先して混在させる。

## When Using Design Reference
`references/design-system.md` を読んだ場合だけ、その色・タイポ・余白ルールに従う。

## Visual Choice
- 比較は比較表か2x2を優先する。
- 変化や因果はフローかタイムラインを優先する。
- 数値訴求はチャートを優先する。
- 視覚化に無理がある場合だけ箇条書きを使う。

## Output
- まずスライド構成案
- 次に各スライドの内容要約
- 必要ならPPTX生成コード
- 最後にQA結果

## QA
- 見出しが action title になっているか
- 見出しだけ読んでも流れが通るか
- 各スライドに主張が1つあるか
- テキストのはみ出し、重なり、詰め込みがないか
- 整列、余白、色、フォントが揃っているか
- 図解が本文よりわかりやすいか
