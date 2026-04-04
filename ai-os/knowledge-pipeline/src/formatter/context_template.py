"""CONTEXT.md生成用プロンプトテンプレート"""
from datetime import datetime


WORK_SYSTEM_PROMPT = """あなたはデータサイエンスの実務プロジェクト支援AIです。
提供された参考ドキュメントをもとに、Claude Codeが実装を開始するための
CONTEXTドキュメントを生成してください。

## 出力規則
- 日本語で出力する
- ドキュメントに情報がない項目は「（参考ドキュメントに該当情報なし）」と記載する
- 推測や補完は明示してから行う
- frontmatterは出力しない
"""

COMP_SYSTEM_PROMPT = """あなたはKaggle/SIGNATEのデータサイエンスコンペ支援AIです。
提供された参考ドキュメントをもとに、Claude Codeが実装を開始するための
CONTEXTドキュメントを生成してください。

## 出力規則
- 日本語で出力する
- ドキュメントに情報がない項目は「（参考ドキュメントに該当情報なし）」と記載する
- 推測や補完は明示してから行う
- frontmatterは出力しない
"""


def _format_docs(docs: list[dict]) -> str:
    """retriever.query() の結果をプロンプト埋め込み用文字列に変換"""
    parts = []
    for d in docs:
        parts.append(
            f"--- [{d.get('rank', '?')}] {d.get('title', d.get('filename', '不明'))} ---\n"
            f"URL: {d.get('url', '')}\n\n"
            f"{d.get('content', '')}"
        )
    return "\n\n".join(parts)


def build_work_prompt(query: str, docs: list[dict]) -> str:
    date_str = datetime.now().strftime("%Y-%m-%d")
    docs_text = _format_docs(docs)
    filenames = [d.get("filename", "不明") for d in docs]

    return f"""プロジェクト: {query}

参考ドキュメント:
{docs_text}

---

以下のフォーマットで出力してください：

# CONTEXT: {query}
生成日: {date_str}

## プロジェクト概要
（クエリから推定される目的・スコープ）

## 関連先行事例・論文
（ドキュメントから抽出）

## 技術的アプローチ候補
（ドキュメントから抽出）

## 業界トレンド・市場データ
（ドキュメントから抽出）

## 実装上の注意点・落とし穴
（ドキュメントから抽出）

## 参考ノート一覧
{chr(10).join(f"- {f}" for f in filenames)}
"""


def build_comp_prompt(query: str, docs: list[dict]) -> str:
    date_str = datetime.now().strftime("%Y-%m-%d")
    docs_text = _format_docs(docs)
    filenames = [d.get("filename", "不明") for d in docs]

    return f"""コンペ・タスク: {query}

参考ドキュメント:
{docs_text}

---

以下のフォーマットで出力してください：

# CONTEXT: {query}
生成日: {date_str}

## タスク定義と類似コンペ
（ドキュメントから抽出）

## 有効だった手法・モデル
（ドキュメントから抽出）

## 特徴量エンジニアリングのアイデア
（ドキュメントから抽出）

## アンサンブル・後処理の知見
（ドキュメントから抽出）

## やってはいけないこと・落とし穴
（ドキュメントから抽出）

## 参考ノート一覧
{chr(10).join(f"- {f}" for f in filenames)}
"""


PROMPTS = {
    "work": (WORK_SYSTEM_PROMPT, build_work_prompt),
    "comp": (COMP_SYSTEM_PROMPT, build_comp_prompt),
}
