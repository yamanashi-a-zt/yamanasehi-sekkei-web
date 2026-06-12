# Pythonセットアップ手順｜GA4分析プロジェクト

このドキュメントでは、分析スクリプトを実行するためのPython環境を
Windows PCに構築する手順を説明します。

---

## ステップ1：Pythonのインストール

1. 以下のURLにアクセスしてPythonをダウンロードする
   https://www.python.org/downloads/

2. 「Download Python 3.x.x」ボタンをクリック

3. インストーラーを起動し、**必ず以下にチェックを入れる**
   ```
   ☑ Add Python to PATH   ← これを忘れると動かない
   ```

4. 「Install Now」をクリックしてインストール完了

5. コマンドプロンプトで確認
   ```
   python --version
   ```
   → `Python 3.xx.x` と表示されればOK

---

## ステップ2：必要なパッケージのインストール

コマンドプロンプト（またはPowerShell）で以下を実行：

```bash
# ga4_analysis フォルダに移動
cd "C:\Users\hp\Desktop\claude code\ga4_analysis"

# パッケージを一括インストール
pip install -r requirements.txt
```

インストールされるパッケージ：
| パッケージ   | 用途                         |
|-------------|------------------------------|
| pandas      | データ集計・CSVの読み書き      |
| numpy       | 数値計算                      |
| matplotlib  | グラフ作成                    |
| seaborn     | グラフのスタイル               |
| plotly      | インタラクティブグラフ（任意）  |
| openpyxl    | Excelファイル出力              |
| jinja2      | HTMLレポート生成               |
| jupyter     | Notebookの実行                |

---

## ステップ3：分析スクリプトの実行

```bash
# ga4_analysis フォルダに移動（まだしていない場合）
cd "C:\Users\hp\Desktop\claude code\ga4_analysis"

# 分析スクリプトを実行
python scripts/analyze_ga4.py
```

**実行後に出力されるファイル（data/processed/ フォルダ）：**

| ファイル名 | 内容 |
|-----------|------|
| 01a_流入経路別CV集計.csv | チャンネル別の問い合わせ数・率 |
| 01b_流入経路詳細Top30.csv | 参照元ごとの詳細 |
| 02a_ページ種別CV集計.csv | ページ種別ごとの集計 |
| 02b_ランディングページTop30.csv | 入口ページ上位30のCV状況 |
| 03_デバイス別CV集計.csv | ブラウザ・デバイス別CV |
| 04a_CVに関与したページ.csv | CV発生ページ一覧 |
| 04b_CV率の高い入口ページ.csv | CV率の高い入口ページ |
| 05_離脱懸念ページ.csv | 改善が必要なページ |
| 06_HP改善仮説.csv | 優先度付き改善アクション一覧 |

---

## トラブルシューティング

### `python` が認識されない場合
→ Pythonインストール時に「Add Python to PATH」のチェックを忘れた可能性。
　 Pythonを再インストールしてチェックを入れ直す。

### `pip install` でエラーが出る場合
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 文字化けが起きる場合
→ スクリプトは utf-8-sig / utf-8 / shift_jis の順で自動試行します。
　 それでも文字化けする場合は、GA4からのCSV出力時のエンコードを確認してください。

### `pandas` が見つからないと出る場合
```bash
pip install pandas
```
