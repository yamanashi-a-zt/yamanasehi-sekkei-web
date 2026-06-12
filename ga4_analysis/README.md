# GA4分析プロジェクト｜工務店・住宅会社のWeb集客改善

## このプロジェクトの目的

GA4（Googleアナリティクス4）から出力したデータをもとに、

- **問い合わせしたユーザーはどんな行動をしていたか**
- **問い合わせしなかったユーザーとの違いは何か**
- **HP・広告・導線のどこを改善すべきか**

を分析し、工務店の経営者や広報担当者にわかりやすいレポートとして届けます。

---

## フォルダ構成

```
ga4_analysis/
│
├── data/
│   ├── raw/              ← GA4からエクスポートしたCSVをここに置く（触らない）
│   └── processed/        ← スクリプトが自動生成する前処理済みデータ
│
├── notebooks/            ← 分析作業のJupyter Notebook
├── scripts/              ← 再利用できるPythonスクリプト
├── reports/              ← 出力されたレポート（HTML / Excel）
├── docs/                 ← 分析計画・仕様書
│
├── requirements.txt      ← 必要なPythonパッケージ一覧
└── README.md             ← このファイル
```

---

## セットアップ手順

### 1. Python環境の準備

```bash
# 仮想環境を作成（推奨）
python -m venv venv
venv\Scripts\activate  # Windows

# パッケージをインストール
pip install -r requirements.txt
```

### 2. GA4からCSVをエクスポートする

`data/raw/` フォルダに以下のCSVを置いてください。
（エクスポート方法は `docs/analysis_plan.md` に記載）

| ファイル名（推奨）              | 内容                       |
|-------------------------------|--------------------------|
| `user_overview.csv`           | ユーザー行動サマリー         |
| `cv_segment.csv`              | CV済みユーザーデータ         |
| `page_performance.csv`        | ページ別閲覧データ           |
| `traffic_source.csv`          | 流入経路データ              |
| `landing_page.csv`            | ランディングページデータ      |
| `device_region.csv`           | デバイス・地域データ         |
| `events.csv`                  | イベントデータ              |
| `funnel.csv`                  | ファネル分析データ           |

### 3. 分析を実行する

```bash
# Jupyter Notebookを起動
jupyter notebook
```

`notebooks/` フォルダのノートブックを番号順に実行してください。

---

## 分析の流れ

```
① CSVをdata/raw/に置く
       ↓
② 01_data_check.ipynb でデータ確認・クレンジング
       ↓
③ 02_cv_behavior.ipynb でCV済みユーザーの行動を分析
       ↓
④ 03_comparison.ipynb でCV有/無ユーザーを比較
       ↓
⑤ 04_traffic_source.ipynb で流入経路を分析
       ↓
⑥ 05_page_analysis.ipynb でページ別パフォーマンスを分析
       ↓
⑦ reports/ にレポートが自動出力される
```

---

## 出力されるレポート

- **summary_report.html** — エグゼクティブサマリー（経営者向け）
- **detail_report.xlsx** — 詳細データ表（社内共有用）
- **action_sheet.xlsx** — 改善アクションの優先度一覧

---

## 注意事項

- `data/raw/` に入れたCSVは**絶対に上書き・削除しない**こと
- 個人情報が含まれる場合はGitにコミットしないこと（`.gitignore`で管理推奨）
