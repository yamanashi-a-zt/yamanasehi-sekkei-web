"""
GA4分析スクリプト｜工務店・住宅会社のWeb集客改善
対象プロパティ：山梨設計
分析期間：2024/05/27 〜 2026/05/26（約2年間）

実行方法：
    python scripts/analyze_ga4.py
"""

import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

# ========================================
# パス設定
# ========================================
# このスクリプトの場所から ga4_analysis/ ルートを特定
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR   = os.path.dirname(SCRIPT_DIR)
RAW_DIR    = os.path.join(BASE_DIR, "data", "raw")
PROC_DIR   = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(PROC_DIR, exist_ok=True)


# ========================================
# ユーティリティ関数
# ========================================

def load_ga4_csv(filename):
    """
    GA4エクスポートCSVを読み込む。
    - 先頭9行はGA4のコメントヘッダー → スキップ
    - 文字コードは UTF-8-BOM → Shift-JIS の順で試みる
    """
    filepath = os.path.join(RAW_DIR, filename)
    for enc in ('utf-8-sig', 'utf-8', 'shift_jis', 'cp932'):
        try:
            df = pd.read_csv(filepath, skiprows=9, encoding=enc)
            df.columns = df.columns.str.strip()   # 列名の余分なスペースを除去
            df = df.dropna(how='all')             # 空行を除去
            return df
        except (UnicodeDecodeError, FileNotFoundError):
            continue
    raise FileNotFoundError(f"ファイルを読み込めませんでした: {filepath}")


def to_pct(val):
    """小数を % 表示文字列に変換（例: 0.0123 → '1.23%'）"""
    try:
        return f"{float(val):.2%}"
    except Exception:
        return "0.00%"


def classify_page(path):
    """URLパスをページ種別に分類する"""
    p = str(path).rstrip('/')
    if p == '':                             return 'トップページ'
    if p == '/':                            return 'トップページ'
    if p.startswith('/works-garelly'):      return '施工事例'
    if p.startswith('/news'):               return 'お知らせ・ブログ'
    if p.startswith('/contact'):            return '問い合わせ'
    if p.startswith('/consultation'):       return '相談申込'
    if p == '/company':                     return '会社概要'
    if p == '/cost':                        return '費用・価格'
    if p == '/plan':                        return 'プラン'
    if p == '/flow':                        return '流れ・プロセス'
    if p == '/policy':                      return 'プライバシーポリシー'
    if p == '/sitemap':                     return 'サイトマップ'
    return 'その他'


def save(df, filename, msg=""):
    """data/processed/ にCSVを保存する"""
    path = os.path.join(PROC_DIR, filename)
    df.to_csv(path, index=False, encoding='utf-8-sig')
    size = os.path.getsize(path)
    print(f"  📄 保存: {filename}  ({size:,} bytes)  {msg}")


# ========================================
# データ読み込み
# ========================================
print("=" * 55)
print("  GA4分析スクリプト 開始")
print("=" * 55)
print(f"\nデータフォルダ: {RAW_DIR}")
print("\n[データ読み込み中...]")

df_traffic = load_ga4_csv("01_traffic_acquisition.csv.csv")
df_landing = load_ga4_csv("02_landing_page.csv.csv")
df_pages   = load_ga4_csv("03_pages.csv.csv")
df_events  = load_ga4_csv("04_events.csv.csv")
df_device  = load_ga4_csv("05_device.csv.csv")

print(f"  ✅ 01_流入経路     : {len(df_traffic)} 行")
print(f"  ✅ 02_ランディング : {len(df_landing)} 行")
print(f"  ✅ 03_ページ       : {len(df_pages)} 行")
print(f"  ✅ 04_イベント     : {len(df_events)} 行")
print(f"  ✅ 05_デバイス     : {len(df_device)} 行")


# ========================================
# 分析1：流入経路（参照元/メディア）別のCV傾向
# ========================================
print("\n\n【分析1】流入経路別コンバージョン傾向")
print("-" * 40)

df_t = df_traffic.copy()
col_src = df_t.columns[0]   # 「セッションの参照元 / メディア」

# 数値型に変換
for col in ['セッション', 'キーイベント', 'エンゲージメント率']:
    df_t[col] = pd.to_numeric(df_t[col], errors='coerce').fillna(0)

# CV率を計算
df_t['CV率_実数'] = df_t.apply(
    lambda r: r['キーイベント'] / r['セッション'] if r['セッション'] > 0 else 0, axis=1
)

# 流入経路を日本語に分類
def classify_channel(src):
    s = str(src).lower()
    if 'direct' in s:                        return 'ダイレクト（直接流入）'
    if 'google' in s and 'organic' in s:     return 'Google自然検索'
    if 'yahoo' in s and 'organic' in s:      return 'Yahoo自然検索'
    if 'bing' in s and 'organic' in s:       return 'Bing検索'
    if 'duckduckgo' in s or 'ask /' in s:    return 'その他検索エンジン'
    if 'googlebusinessprofile' in s:         return 'Googleマイビジネス（地図）'
    if 'docotate' in s:                      return 'ドコタテ（提携サイト）'
    if 'facebook' in s or s.startswith('ig /') or 'instagram' in s: return 'SNS（Meta系）'
    if 'referral' in s:                      return '外部サイトからの参照'
    return 'その他'

df_t['流入経路_分類'] = df_t[col_src].apply(classify_channel)

# 1a: チャンネル別集計（サマリー）
df_ch = df_t.groupby('流入経路_分類').agg(
    訪問数=('セッション', 'sum'),
    問い合わせ完了数=('キーイベント', 'sum')
).reset_index().sort_values('訪問数', ascending=False)

df_ch['問い合わせ率'] = (df_ch['問い合わせ完了数'] / df_ch['訪問数']).apply(to_pct)

def eval_ch(row):
    rate = row['問い合わせ完了数'] / row['訪問数'] if row['訪問数'] > 0 else 0
    cv   = row['問い合わせ完了数']
    if cv == 0:        return '⚠️ 問い合わせゼロ：流入の質を確認'
    if rate >= 0.015:  return '⭐ 非常に優秀：この経路を伸ばす'
    if rate >= 0.008:  return '✅ 良好'
    if rate >= 0.003:  return '△ 平均的'
    return '▼ 改善余地あり'

df_ch['評価'] = df_ch.apply(eval_ch, axis=1)
save(df_ch, "01a_流入経路別CV集計.csv")

# 1b: 参照元ごとの詳細（上位20）
df_t_out = df_t[[col_src, '流入経路_分類', 'セッション', 'キーイベント',
                  'CV率_実数', 'エンゲージメント率']].copy()
df_t_out.columns = ['参照元_メディア', '分類', '訪問数', '問い合わせ完了数', 'CV率', 'ちゃんと見た訪問の割合']
df_t_out['CV率']             = df_t_out['CV率'].apply(to_pct)
df_t_out['ちゃんと見た訪問の割合'] = df_t_out['ちゃんと見た訪問の割合'].apply(to_pct)
df_t_out = df_t_out.sort_values('訪問数', ascending=False).head(30)
save(df_t_out, "01b_流入経路詳細Top30.csv")


# ========================================
# 分析2：ランディングページ別のCV傾向
# ========================================
print("\n【分析2】ランディングページ別コンバージョン傾向")
print("-" * 40)

df_l = df_landing.copy()
col_lp = df_l.columns[0]   # 「ランディング ページ」

df_l[col_lp]      = df_l[col_lp].astype(str).str.rstrip('/')
df_l['キーイベント'] = pd.to_numeric(df_l['キーイベント'], errors='coerce').fillna(0)
df_l['セッション']   = pd.to_numeric(df_l['セッション'],   errors='coerce').fillna(0)
df_l['セッションあたりの平均エンゲージメント時間'] = pd.to_numeric(
    df_l['セッションあたりの平均エンゲージメント時間'], errors='coerce').fillna(0)

df_l['CV率_実数']  = df_l.apply(
    lambda r: r['キーイベント'] / r['セッション'] if r['セッション'] > 0 else 0, axis=1
)
df_l['ページ種別'] = df_l[col_lp].apply(classify_page)

# サンクスページ（CV完了ページ自体）は除外
df_l_ex = df_l[~df_l[col_lp].str.contains('thanks', case=False)].copy()

# 2a: ページ種別サマリー
df_pt = df_l_ex.groupby('ページ種別').agg(
    訪問数=('セッション', 'sum'),
    問い合わせ完了数=('キーイベント', 'sum')
).reset_index().sort_values('訪問数', ascending=False)

df_pt['問い合わせ率']   = (df_pt['問い合わせ完了数'] / df_pt['訪問数']).apply(to_pct)
df_pt['総訪問に占める割合'] = (df_pt['訪問数'] / df_pt['訪問数'].sum()).apply(to_pct)
save(df_pt, "02a_ページ種別CV集計.csv")

# 2b: ランディングページ上位30詳細
df_l_top = df_l_ex.nlargest(30, 'セッション').copy()
df_l_top = df_l_top[[
    col_lp, 'ページ種別', 'セッション', 'キーイベント', 'CV率_実数',
    'セッションあたりの平均エンゲージメント時間'
]]
df_l_top.columns = ['ページURL', 'ページ種別', '訪問数', '問い合わせ完了数',
                    'CV率', '平均滞在時間_分']
df_l_top['CV率'] = df_l_top['CV率'].apply(to_pct)
df_l_top['CV力'] = df_l_top['問い合わせ完了数'].apply(
    lambda x: '🔥 高CV（10件以上）' if x >= 10 else ('✅ CV有' if x >= 1 else '－ CVなし')
)
save(df_l_top, "02b_ランディングページTop30.csv")


# ========================================
# 分析3：ブラウザ／デバイス別のCV傾向
# ========================================
print("\n【分析3】デバイス別コンバージョン傾向")
print("-" * 40)

df_d = df_device.copy()
for col in ['アクティブ ユーザー', 'キーイベント', 'エンゲージメント率']:
    df_d[col] = pd.to_numeric(df_d[col], errors='coerce').fillna(0)

df_d['CV率_実数'] = df_d.apply(
    lambda r: r['キーイベント'] / r['アクティブ ユーザー'] if r['アクティブ ユーザー'] > 0 else 0, axis=1
)

def classify_device(browser):
    b = str(browser)
    if 'Safari (in-app)' in b:  return 'スマホ（アプリ内ブラウザ・iOS）'
    if b == 'Safari':           return 'iPhone / iPad（Safari）'
    if 'Android Webview' in b:  return 'スマホ（Androidアプリ内）'
    if 'Samsung' in b:          return 'Androidスマホ（Samsung）'
    if b == 'Chrome':           return 'PC / Androidスマホ（Chrome）'
    if b == 'Edge':             return 'PCまたはスマホ（Edge）'
    if b == 'Firefox':          return 'PC（Firefox）'
    return 'その他'

df_d['デバイス推定'] = df_d['ブラウザ'].apply(classify_device)

df_dev = df_d[['ブラウザ', 'デバイス推定', 'アクティブ ユーザー',
               'キーイベント', 'CV率_実数', 'エンゲージメント率']].copy()
df_dev.columns = ['ブラウザ', 'デバイス推定', 'ユーザー数', '問い合わせ完了数',
                  'CV率', 'ちゃんと見た割合']
df_dev['CV率']        = df_dev['CV率'].apply(to_pct)
df_dev['ちゃんと見た割合'] = df_dev['ちゃんと見た割合'].apply(to_pct)
df_dev['注意・評価'] = df_dev.apply(lambda r: (
    '🚨 CV0件：フォームのiOS動作確認が急務'
    if r['問い合わせ完了数'] == 0 and r['ユーザー数'] >= 100
    else ('✅ 良好' if r['問い合わせ完了数'] >= 5 else '△')
), axis=1)
df_dev = df_dev.sort_values('ユーザー数', ascending=False)
save(df_dev, "03_デバイス別CV集計.csv")


# ========================================
# 分析4：CVにつながりやすいページ
# ========================================
print("\n【分析4】CVにつながりやすいページ")
print("-" * 40)

df_p = df_pages.copy()
col_pp = df_p.columns[0]   # 「ページパスとスクリーン クラス」

for col in ['表示回数', 'アクティブ ユーザー', 'キーイベント',
            'アクティブ ユーザーあたりの平均エンゲージメント時間']:
    df_p[col] = pd.to_numeric(df_p[col], errors='coerce').fillna(0)

df_p['ページURL']  = df_p[col_pp].astype(str).str.rstrip('/')
df_p['ページ種別'] = df_p['ページURL'].apply(classify_page)

# 4a: キーイベントが発生しているページ（CV直接関与）
df_cv_p = df_p[df_p['キーイベント'] > 0].sort_values('キーイベント', ascending=False).copy()
df_cv_p_out = df_cv_p[[
    'ページURL', 'ページ種別', '表示回数', 'アクティブ ユーザー', 'キーイベント',
    'アクティブ ユーザーあたりの平均エンゲージメント時間'
]].copy()
df_cv_p_out.columns = ['ページURL', 'ページ種別', '表示回数', 'ユーザー数',
                       'CV関連イベント数', '平均滞在時間_分']
df_cv_p_out['役割'] = df_cv_p_out['ページURL'].apply(lambda p: (
    '✅ 問い合わせ完了ページ（ゴール）'  if 'thanks' in p
    else '📌 CV発生ページ'
))
save(df_cv_p_out, "04a_CVに関与したページ.csv")

# 4b: ランディングページとしてCV率が高いページ（CV1件以上・入口として有効）
df_l_cv = df_l_ex[df_l_ex['キーイベント'] >= 1].copy()
df_l_cv = df_l_cv.sort_values('キーイベント', ascending=False)
df_l_cv_out = df_l_cv[[
    col_lp, 'ページ種別', 'セッション', 'キーイベント', 'CV率_実数'
]].copy()
df_l_cv_out.columns = ['ページURL', 'ページ種別', '入口としての訪問数',
                       '問い合わせ完了数', 'CV率']
df_l_cv_out['CV率'] = df_l_cv_out['CV率'].apply(to_pct)
df_l_cv_out['改善ヒント'] = df_l_cv_out['ページ種別'].map({
    'トップページ':  '✅ 入口として機能。さらに導線を強化',
    '問い合わせ':    '🔥 問い合わせ意欲の高いユーザーが直接訪問',
    '会社概要':      '📌 会社を調べてCVへ。信頼コンテンツが効いている',
    '施工事例':      '📌 事例が気に入ってCV。事例の充実が効果的',
}).fillna('📌 CV発生ページ')
save(df_l_cv_out, "04b_CV率の高い入口ページ.csv")


# ========================================
# 分析5：離脱が多い可能性があるページ
# ========================================
print("\n【分析5】離脱が懸念されるページ")
print("-" * 40)

# 条件：
#   ① 表示回数 50回以上（一定数見られているページ）
#   ② キーイベント = 0（CVにつながっていない）
#   ③ 平均滞在時間 0.1分（6秒）未満（ほとんど読まれていない）
#   ④ サンクスページ・プライバシーポリシー・サイトマップは除外
EXCLUDE = ['thanks', '/policy', '/sitemap']
mask_exclude = df_p['ページURL'].apply(
    lambda p: not any(ex in str(p) for ex in EXCLUDE)
)

df_drop = df_p[
    mask_exclude &
    (df_p['表示回数'] >= 50) &
    (df_p['キーイベント'] == 0) &
    (df_p['アクティブ ユーザーあたりの平均エンゲージメント時間'] < 0.1)
].copy().sort_values('表示回数', ascending=False)

df_drop_out = df_drop[[
    'ページURL', 'ページ種別', '表示回数', 'アクティブ ユーザー',
    'アクティブ ユーザーあたりの平均エンゲージメント時間'
]].copy()
df_drop_out.columns = ['ページURL', 'ページ種別', '表示回数', 'ユーザー数', '平均滞在時間_分']

HINT = {
    'トップページ':     '🔴 最重要：多くの人が来るのに離脱。ファーストビューの見直しを',
    '施工事例':         '🟡 事例を見て終わっている。各事例に問い合わせボタンを追加',
    'お知らせ・ブログ':  '🟡 情報収集で離脱。記事内に相談・問い合わせへの誘導を',
    '会社概要':         '🟡 会社を調べて離脱。「まずは相談」ボタンで次の行動を促す',
    '費用・価格':        '🔴 価格確認後に離脱。「詳しくはご相談ください」CTAを追加',
    'プラン':           '🟡 プランを見て終わっている。問い合わせへの橋渡しコンテンツを',
    '流れ・プロセス':    '🟡 検討段階ユーザー。次ステップを明示するCTAを配置',
}
df_drop_out['改善ヒント'] = df_drop_out['ページ種別'].map(HINT).fillna('△ 改善余地あり')
save(df_drop_out, "05_離脱懸念ページ.csv")


# ========================================
# 分析6：HP改善仮説まとめ
# ========================================
print("\n【分析6】HP改善仮説まとめ")
print("-" * 40)

# 主要指標を計算して仮説に埋め込む
total_sessions = int(df_traffic['セッション'].sum())
total_cv       = int(df_traffic['キーイベント'].sum())
cv_rate        = total_cv / total_sessions if total_sessions > 0 else 0

safari_users = int(df_device[df_device['ブラウザ'].str.contains('Safari', case=False)]['アクティブ ユーザー'].sum())
safari_cv    = int(df_device[df_device['ブラウザ'].str.contains('Safari', case=False)]['キーイベント'].sum())

docotate_row = df_traffic[df_traffic[df_traffic.columns[0]].str.contains('docotate', case=False)]
docotate_ses = int(docotate_row['セッション'].sum()) if not docotate_row.empty else 0
docotate_cv  = int(docotate_row['キーイベント'].sum()) if not docotate_row.empty else 0

gmb_row = df_traffic[df_traffic[df_traffic.columns[0]].str.contains('googlebusinessprofile', case=False)]
gmb_ses = int(gmb_row['セッション'].sum()) if not gmb_row.empty else 0
gmb_cv  = int(gmb_row['キーイベント'].sum()) if not gmb_row.empty else 0

top_row = df_landing[df_landing[df_landing.columns[0]].str.rstrip('/') == '/']
top_ses = int(top_row['セッション'].sum()) if not top_row.empty else 0
top_cv  = int(top_row['キーイベント'].sum()) if not top_row.empty else 0

hypotheses = [
    {
        'No': 1,
        '優先度': '🔴 最優先',
        '改善箇所': 'iPhoneでの問い合わせフォームの動作確認',
        '現状の課題':
            f'Safariユーザーが{safari_users:,}人いるにもかかわらず問い合わせ完了数が{safari_cv}件。'
            'フォームがiOSで正常に送信できない技術的バグの可能性が高い。',
        '推奨アクション':
            'iPhoneのSafariで実際にフォームを送信テストする。'
            '送信ボタンの反応・バリデーションエラー・完了ページへの遷移を確認する。',
        '期待効果':
            f'Safariユーザーの1%がCVすれば年間+{int(safari_users * 0.01)}件の問い合わせが期待できる。',
        'データ根拠':
            f'05_device: Safari系ユーザー {safari_users:,}人 / 問い合わせ完了 {safari_cv}件',
    },
    {
        'No': 2,
        '優先度': '🔴 最優先',
        '改善箇所': 'トップページの問い合わせ導線強化',
        '現状の課題':
            f'トップページは{top_ses:,}訪問で最大の入口だが、CV率は{to_pct(top_cv/top_ses if top_ses else 0)}にとどまる。'
            '多くの人が来ても次の行動につながっていない。',
        '推奨アクション':
            '「まずは相談する」「施工事例を見る」などのボタンをファーストビューに配置。'
            '「どんな悩みでも相談できる」という安心感を前面に出す。',
        '期待効果':
            f'CV率が1%になれば、年間の問い合わせ数が{top_cv}件→{int(top_ses * 0.01)}件へ増加。',
        'データ根拠':
            f'02_landing: トップページ {top_ses:,}セッション / 問い合わせ完了 {top_cv}件',
    },
    {
        'No': 3,
        '優先度': '🔴 高',
        '改善箇所': 'ドコタテ経由ユーザーへの専用対応',
        '現状の課題':
            f'ドコタテからの流入は{docotate_ses:,}セッションと2番目に多いが、'
            f'CV率は{to_pct(docotate_cv/docotate_ses if docotate_ses else 0)}と非常に低い。'
            '流入の目的がサイトのコンテンツと合っていない可能性。',
        '推奨アクション':
            'ドコタテ流入ユーザー向けに、工務店の強み・特徴・地域密着を伝える専用ランディングページを作成する。',
        '期待効果':
            f'CV率が0.5%になれば、現在の{docotate_cv}件→{int(docotate_ses * 0.005)}件へ増加。',
        'データ根拠':
            f'01_traffic: docotate {docotate_ses:,}セッション / 問い合わせ完了 {docotate_cv}件',
    },
    {
        'No': 4,
        '優先度': '🟡 中',
        '改善箇所': 'Googleマイビジネス（地図）の強化',
        '現状の課題':
            f'地図経由の流入は{gmb_ses}セッションと少ないが、CV率{to_pct(gmb_cv/gmb_ses if gmb_ses else 0)}は最高効率。'
            'まだまだ伸びしろがある経路。',
        '推奨アクション':
            'Googleビジネスプロフィールに施工事例の写真・Q&A・最新情報を定期投稿。'
            'レビューの返信も丁寧に行い、地図表示での露出を高める。',
        '期待効果':
            f'訪問数が500に増えれば、CV数は{gmb_cv}件→{int(500 * gmb_cv/gmb_ses) if gmb_ses else "−"}件に増加。',
        'データ根拠':
            f'01_traffic: googlebusinessprofile {gmb_ses}セッション / CV率 {to_pct(gmb_cv/gmb_ses if gmb_ses else 0)}',
    },
    {
        'No': 5,
        '優先度': '🟡 中',
        '改善箇所': '施工事例ページからの問い合わせ誘導',
        '現状の課題':
            '施工事例ページは閲覧数が多いが、CV数がほぼゼロ。'
            '事例を見て「いいな」と思っても、次の行動（問い合わせ）への道筋がない。',
        '推奨アクション':
            '各事例ページの末尾に「この事例について相談する」ボタンを追加。'
            '費用目安・こだわりポイントも記載し、問い合わせの背中を押す。',
        '期待効果':
            '施工事例訪問者の0.5%がCVすれば、月数件の追加問い合わせが期待できる。',
        'データ根拠':
            '03_pages: /works-garelly系 → 多数閲覧 / キーイベントほぼ0',
    },
    {
        'No': 6,
        '優先度': '🟡 中',
        '改善箇所': '費用・価格ページのCTA追加',
        '現状の課題':
            '費用ページへの直接流入140件でCV=0件。価格を確認して離脱している。',
        '推奨アクション':
            '「詳しい費用はご相談ください」「無料見積もり実施中」のボタンを追加。'
            '価格帯の目安と「相談するだけでOK」という安心感を伝える。',
        '期待効果':
            '費用ページCV率1%で月1〜2件の追加問い合わせが期待できる。',
        'データ根拠':
            '02_landing: /cost 140セッション / 問い合わせ完了 0件',
    },
    {
        'No': 7,
        '優先度': '🟢 低（要調査）',
        '改善箇所': 'Yahoo検索流入のCV改善',
        '現状の課題':
            '428訪問でCV完全ゼロ。Yahooから来るユーザーに響くコンテンツが不足している可能性。',
        '推奨アクション':
            'Yahoo検索ユーザーが検索しているキーワードとコンテンツの一致を確認。'
            '地域名＋工務店などのキーワードに対応したページを作成する。',
        '期待効果':
            '中期的なCVゼロ脱却。',
        'データ根拠':
            '01_traffic: yahoo/organic 428セッション / 問い合わせ完了 0件',
    },
]

df_hypo = pd.DataFrame(hypotheses)
save(df_hypo, "06_HP改善仮説.csv")


# ========================================
# 完了サマリー
# ========================================
print("\n\n" + "=" * 55)
print("  ✅ 全分析完了！")
print("=" * 55)
print(f"\n出力先: {PROC_DIR}")
print("\n【全体サマリー】")
print(f"  総訪問数         : {total_sessions:,} セッション（2年間合計）")
print(f"  問い合わせ完了数  : {total_cv} 件")
print(f"  全体CV率         : {to_pct(cv_rate)}")
print(f"\n【今すぐ対応すべき課題】")
print(f"  🚨 Safari/iPhone ユーザー（推計{safari_users:,}人）の問い合わせ完了 = {safari_cv}件")
print(f"     → iPhoneでのフォーム送信テストを最優先で実施してください")
print(f"\n出力ファイル一覧:")
for f in sorted(os.listdir(PROC_DIR)):
    if f.endswith('.csv'):
        size = os.path.getsize(os.path.join(PROC_DIR, f))
        print(f"  📄 {f} ({size:,} bytes)")
