# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## リポジトリ概要

地域密着工務店・建築設計事務所向けのマーケティング支援ツール群。以下の3プロジェクトが同居している。

| フォルダ/ファイル | 内容 |
|-----------------|------|
| `ga4_analysis/` | GA4データを分析してWeb改善提案を生成するPythonプロジェクト |
| `doco-connect-lp/` | ドコタテ会員向けコミュニティ「doco-connect」のランディングページ（HTML単一ファイル） |
| `yamanashi_sekkei_*.md` | 山梨一正建築設計事務所WEBリニューアルの戦略資料（NotebookLMソース用） |

---

## GA4分析プロジェクト（`ga4_analysis/`）

### セットアップ

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r ga4_analysis/requirements.txt
```

### 分析実行

```bash
python ga4_analysis/scripts/analyze_ga4.py
```

実行前に `ga4_analysis/data/raw/` に以下のCSVを配置すること：

| ファイル名 | GA4エクスポート元 |
|-----------|----------------|
| `01_traffic_acquisition.csv.csv` | 集客 > トラフィック獲得 |
| `02_landing_page.csv.csv` | 探索 > ランディングページ |
| `03_pages.csv.csv` | エンゲージメント > ページとスクリーン |
| `04_events.csv.csv` | エンゲージメント > イベント |
| `05_device.csv.csv` | ユーザー属性 > 技術詳細 |

**注意:** GA4エクスポートCSVは先頭9行にコメントヘッダーが入る。`load_ga4_csv()` が自動スキップする。

### 出力

`ga4_analysis/data/processed/` に以下のCSVが生成される：

- `01a_流入経路別CV集計.csv` / `01b_流入経路詳細Top30.csv`
- `02a_ページ種別CV集計.csv` / `02b_ランディングページTop30.csv`
- `03_デバイス別CV集計.csv`
- `04a_CVに関与したページ.csv` / `04b_CV率の高い入口ページ.csv`
- `05_離脱懸念ページ.csv`
- `06_HP改善仮説.csv` ← 経営者向け提案資料のベースになる最重要ファイル

### アーキテクチャ

```
data/raw/（GA4 CSV）
    ↓ load_ga4_csv()  ← 文字コード自動判定（utf-8-sig → shift_jis）
analyze_ga4.py
    ├── classify_channel()  ← 参照元を日本語チャネルに分類
    ├── classify_page()     ← URLパスをページ種別に分類
    ├── to_pct()            ← 小数を%文字列に変換
    └── save()              ← data/processed/ に保存
data/processed/（分析済みCSV）
```

`classify_page()` は現在 `yamanashi-sekkei.jp` のURL構造に対応している。別クライアントのサイトに転用する際はURLパターンを書き換える。

---

## doco-connect LP（`doco-connect-lp/index.html`）

CSS・JS・コンテンツがすべて `index.html` 1ファイルに完結している。外部依存はGoogle Fonts（Noto Sans JP / Noto Serif JP）のみ。ブラウザで直接開いて確認できる。

---

## 共通事項

- `data/raw/` のCSVはGitにコミットしない（個人情報・クライアントデータを含む可能性）
- 分析スクリプトは山梨設計のGA4プロパティを対象として開発されたが、`classify_page()` と `classify_channel()` を修正すれば他クライアントに転用可能
