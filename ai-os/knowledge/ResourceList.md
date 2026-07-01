# Resource Ingestion List

このファイルは、AI OS の「最強の文脈」を構築するために取り込むべき外部リソースのリストである。

## 1. Core Frameworks & Principles (High Priority)
- [x] [Ankh.md](https://github.com/Abruptive/Ankh.md) - 構造化文書プロトコル (Framework extracted)
- [x] [design.md](https://github.com/google-labs-code/design.md) - Google式設計ドキュメント (Framework extracted)
- [x] [vibeyard](https://github.com/elirantutia/vibeyard) - Vibe-based 開発 (Synthesis completed)
- [x] [SocratiCode](https://github.com/giancarloerra/SocratiCode) - ソクラテス式コーディング (Synthesis completed)
- [x] [How to write paper (Matsuo-lab)](https://ymatsuo.com/information/how-to-write-paper-en/) - 論文執筆原則 (Principle extracted)
- [x] [plur](https://github.com/plur-ai/plur) - エージェントフレームワーク (Synthesis completed)
- [x] [hermes-paperclip-adapter](https://github.com/NousResearch/hermes-paperclip-adapter) - 長期記憶/アダプター (Synthesis completed)

## 2. Skills & Tools
- [ ] [hermeshub](https://github.com/amanning3390/hermeshub) - Hermes スキルハブ
- [ ] [hermes-skill-marketplace](https://github.com/Lethe044/hermes-skill-marketplace) - スキルマーケットプレイス
- [ ] [Hermes-Agent-Wizard](https://github.com/GUNAASHRINM/Hermes-Agent-Wizard) - エージェント生成ウィザード
- [ ] [hermes-skill-factory](https://github.com/Romanescu11/hermes-skill-factory) - スキル工場
- [ ] [awesome-codex-skills](https://github.com/ComposioHQ/awesome-codex-skills) - Codex スキル集
- [ ] [ppt-master](https://github.com/hugohe3/ppt-master) - PPT生成
- [ ] [GitNexus](https://github.com/abhigyanpatwari/GitNexus) - コードベース索引
- [ ] [review-codecommit](https://github.com/watany-dev/review-codecommit) - CodeCommit レビュー

## 3. Knowledge & Research
- [x] [MIT Open Access Books](https://direct.mit.edu/books/search-results?sort=Date+-+Newest+First&f_ContentType=Book&fl_SiteID=5&access_openaccess=true&page=1) (Curated bookshelf created: MIT_OpenAccess_Bookshelf.md)
- [x] [Vibe-Trading](https://github.com/HKUDS/Vibe-Trading) - 自然言語から戦略構築・バックテスト (Integrated)
- [x] [QuantDinger](https://github.com/brokermr810/QuantDinger) - セルフホスト型量化OS (Integrated)
- [x] [engineer-vocabulary-list](https://github.com/mercari/engineer-vocabulary-list) - メルカリ エンジニア用語集
- [x] [dexter-jp](https://github.com/edinetdb/dexter-jp) - 日本のEDINET/金融データ解析ツール (Integrated)
- [x] [timesfm](https://github.com/google-research/timesfm) - Google 時系列予測モデル (Framework extracted)
- [x] [FinceptTerminal](https://github.com/Fincept-Corporation/FinceptTerminal) - Bloomberg級金融ターミナル、37 AIエージェント、100+データコネクタ (Integrated)
- [x] [daily_stock_analysis](https://github.com/ZhuLinsen/daily_stock_analysis) - LLM駆動A/H/米株毎日分析・自動配信パイプライン (Integrated)
- [x] [last30days-skill](https://github.com/mvanhorn/last30days-skill) - 30日間トレンド・コミュニティコンセンサス並列リサーチスキル (Integrated)
- [x] [scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) - 135の科学・金融・データ分析スキル集 (Integrated)
- [x] [public-apis](https://github.com/public-apis/public-apis) - 500以上の公開APIカタログ（金融・暗号資産・FX・経済データ） (Integrated)
- [x] [Beyond Code Reasoning: A Specification-Anchored Audit Framework for Expert-Augmented Security Verification](https://arxiv.org/abs/2604.26495) (Framework extracted: speca.md)
- [ ] [Hermes-Wiki](https://github.com/cclank/Hermes-Wiki)

## 4. Tactical (X Threads & Others)
- [x] [AnatoliKopadze - Hermes 活用](https://x.com/AnatoliKopadze/status/2050225292585607440) (Synthesis completed)
- [x] [AYi_AInotes - AIノート術](https://x.com/AYi_AInotes/status/2050201752868131075) (Synthesis completed)
- [ ] [milesdeutscher - クリプト/AI](https://x.com/milesdeutscher/status/2049618781841031551)
- [x] [S0N_IA_ - エージェント思考](https://x.com/S0N_IA_/status/2050260648857120841) (Synthesis completed)
- [x] [aiscwork - AIワークフロー](https://x.com/aiscwork/status/2050143291933426103) (Synthesis completed)

## Ingestion Strategy
1. **Scrape**: `web_fetch` または `requests` でコンテンツ取得
2. **Summarize**: 各リソースの要約、主要原則、適用場面を抽出
3. **Convert**: `ai-os/knowledge/` のフォーマット（principles/playbooks/frameworks）に変換
4. **Index**: `obsidian-vault/` に保存し、`knowledge-pipeline` で埋め込み
