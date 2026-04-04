"""レポート・Marpスライド生成テンプレート"""

REPORT_SYSTEM_PROMPT = """あなたはデータサイエンス・機械学習分野の技術レポート作成者です。
提供された知識ベースの内容をもとに、包括的な技術レポートを作成してください。

## 出力規則
- 日本語で記述する
- frontmatterは出力しない
- 深い洞察・比較・批評を含める
- 実務・研究への具体的な示唆を出す
- 知識ベースにない情報は「（知識ベース外の補足）」と明示する
- 関連概念は [[概念名]] 形式でリンクする
"""


def _format_docs(docs: list[dict]) -> str:
    parts = []
    for d in docs:
        parts.append(
            f"### [{d.get('rank', '?')}] {d.get('title', d.get('filename', 'Unknown'))}\n"
            f"URL: {d.get('url', '')}\n\n"
            f"{d.get('content', '')}"
        )
    return "\n\n---\n\n".join(parts)


def build_report_prompt(query: str, docs: list[dict]) -> str:
    docs_text = _format_docs(docs)
    return f"""以下の知識ベースの内容をもとに、「{query}」についての包括的な技術レポートを作成してください。

## 知識ベース（{len(docs)}件）

{docs_text}

---

以下の構造で出力してください：

# {query}

## エグゼクティブサマリー
（このレポートの核心を3〜5文で述べる）

## 背景・問題設定
（なぜこのトピックが重要か、どんな課題を解決するか）

## 主要手法・アプローチの比較
（知識ベース内の手法を表形式または箇条書きで比較）

## 技術的詳細
（アルゴリズム・実装・数式・コードなど）

## 実務での活用方法
（具体的なユースケース・注意点・ベストプラクティス）

## 今後の展望・未解決課題
（オープンプロブレム・研究の方向性）

## 関連概念マップ
（このトピックに関連する [[概念名]] を列挙）

## 参考文献
{chr(10).join(f"- [{d.get('title', d.get('filename', ''))}]({d.get('url', '')})" for d in docs)}
"""


MARP_SYSTEM_PROMPT = """あなたはMarkdownスライド（Marp形式）の作成者です。
提供された知識ベースの内容をもとに、発表用スライドを作成してください。

## Marp記法
- スライド区切り: `---`
- frontmatter: `marp: true` を先頭に含める
- 各スライドは1トピック
- 箇条書きは3〜5点まで
- コードブロックは ``` で囲む
"""


def build_marp_prompt(query: str, docs: list[dict]) -> str:
    docs_text = "\n\n---\n\n".join(
        f"### {d.get('title', d.get('filename', 'Unknown'))}\n{d.get('content', '')[:800]}"
        for d in docs
    )
    return f"""以下の知識ベースの内容をもとに、「{query}」についてのMarpスライドを作成してください。

## 知識ベース（{len(docs)}件）

{docs_text}

---

以下のMarp形式で出力してください（10〜15枚程度）:

```
---
marp: true
theme: default
paginate: true
---

# {query}
<!-- タイトルスライド -->

---

## アジェンダ
...

---
...
```

スライドは以下を含めてください：
1. タイトル
2. アジェンダ
3. 背景・問題設定
4. 主要手法（複数スライド）
5. 比較・評価
6. 実務への示唆
7. まとめ
"""
