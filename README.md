# yamanasehi-sekkei-web

山梨一正建築設計事務所 WEBサイトリニューアル プロジェクトリポジトリ

---

## プロジェクト構成

| フォルダ/ファイル | 内容 |
|-----------------|------|
| `ga4_analysis/` | GA4データ分析・Web改善提案生成ツール（Python） |
| `doco-connect-lp/` | doco-connect コミュニティLPページ（HTML） |
| `yamanashi_sekkei_website_project.md` | WEBリニューアル戦略資料 |
| `yamanashi_sekkei_interview_source.md` | 代表インタビュー記録（NotebookLMソース） |

---

## GA4分析ツール

工務店・建築設計事務所のGA4データを分析し、Web改善仮説を自動生成するPythonスクリプト。

### セットアップ

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r ga4_analysis/requirements.txt
```

### 実行

```bash
python ga4_analysis/scripts/analyze_ga4.py
```

`ga4_analysis/data/raw/` にGA4エクスポートCSVを配置してから実行する。

### 出力

`ga4_analysis/data/processed/` に分析済みCSVが生成される。最重要ファイルは `06_HP改善仮説.csv`。

---

## WEBリニューアル戦略資料

山梨一正建築設計事務所のWEBサイトリニューアルに向けた戦略・コンセプト・インタビュー設計資料。NotebookLMのソースとして利用。

- **[戦略資料](yamanashi_sekkei_website_project.md)** — サイトコンセプト・ページ構成・ターゲット像
- **[インタビュー記録](yamanashi_sekkei_interview_source.md)** — 対話形式のWHY言語化記録

---

## 注意事項

- `ga4_analysis/data/raw/` のCSVはGitにコミットしない（クライアントデータを含む）
