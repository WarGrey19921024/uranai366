"""MBTI切り替えキット（Obsidian に置いた本文17本）に、広告と「ほかの占いへの案内」を足す（2026-10-28 本人OK）。
使い方：python mbti_kit_add.py <bodiesフォルダ> <出力フォルダ>
- 電話占いの箱：タイプページは「2027年の人間関係」（<type>-relation）の後ろ、トップは相性（mbti-compat）の後ろ
- 商品の箱：タイプページは「ラッキーポイント」（<type>-lucky）の前、トップは「よくある質問」（mbti-faq）の前
- 案内：本文の最後（構造化データの前）に「あわせて読みたい」
- 本文の頭に、アイキャッチを隠すCSS・共通CSS（fh-b27.css）・広告のCSS
既に入っていたら入れない（2回実行しても同じ）。
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import aff_extra as AX  # noqa: E402
from build_hub import WP_ASSET, ASSET_VER  # noqa: E402

TYPES = ["intj", "intp", "entj", "entp", "infj", "infp", "enfj", "enfp", "istj", "isfj", "estj", "esfj", "istp", "isfp", "estp", "esfp"]
# 2027年のテーマ（キットの README）に合わせた商品（検索語, 表示名, ひとこと, アイコン）
GOODS = {
    "intj": [("ホワイトボード 卓上", "卓上のホワイトボード", "頭の中の設計図を人に見せる年に。考えを書き出して共有する道具を。", "stationery"), ("ガントチャート ノート", "計画を見える形にするノート", "任せる仕事と自分の仕事を分けて書くと、委ねやすくなります。", "stationery")],
    "intp": [("アイデアノート", "アイデアノート", "考えを仕上げて発表する年。思いつきを形に残すノートを。", "stationery"), ("ポモドーロ タイマー", "集中用のタイマー", "締め切りまでに仕上げる力を、時間を区切る習慣で支えて。", "calendar")],
    "entj": [("手帳 2027", "2027年の手帳", "育てる人と長く走る計画を、1年分の見通しで。", "stationery"), ("ヨガマット", "ヨガマット", "持久力の年。忙しい日でも体を伸ばす時間を。", "health")],
    "entp": [("付箋 大容量", "付箋のセット", "選んで深掘りする年。アイデアを並べて、残すものを選ぶのに。", "stationery"), ("ブックスタンド", "ブックスタンド", "一つのテーマを深く読み込むときの相棒に。", "book")],
    "infj": [("ノイズキャンセリング イヤーマフ", "静けさを守るイヤーマフ", "境界線と自分の時間の年。ひとりの時間を守る道具を。", "kokoro"), ("アロマディフューザー", "アロマディフューザー", "人と会った日の夜に、気持ちを切り替える香りを。", "aroma")],
    "infp": [("スケッチブック", "スケッチブック", "表現と小さな発信の年。気持ちを形にする一冊を。", "stationery"), ("万年筆 初心者", "書きやすい万年筆", "思いを言葉にする時間を、少し特別なものに。", "stationery")],
    "enfj": [("入浴剤 ギフト", "入浴剤の詰め合わせ", "受け取る年。人のために動いたあとは、自分を労わる時間を。", "beauty"), ("ハーブティー セット", "ハーブティーのセット", "頼る勇気を持つ年に、ほっと一息つける一杯を。", "tea")],
    "enfp": [("習慣化 手帳", "習慣を記録する手帳", "習慣と根を張る年。続けたことを毎日ひとこと残して。", "stationery"), ("観葉植物 小さめ", "小さな観葉植物", "根を張って育つ姿を、毎日そばで見られるように。", "plant")],
    "istj": [("工具セット 家庭用", "家庭用の工具セット", "改良と小さな試行の年。身の回りを少しずつ直す道具を。", "hobby"), ("方眼ノート", "方眼ノート", "試したことと結果を記録すると、次の改良が見えてきます。", "stationery")],
    "isfj": [("交換日記 ノート", "気持ちを書くノート", "自分の希望を伝える年。言いたいことを先に書いて整理を。", "stationery"), ("レターセット", "レターセット", "直接言いにくいことは、手紙にして伝えるのもひとつの方法。", "stationery")],
    "estj": [("会議 タイマー", "話し合い用のタイマー", "対話の年。相手が話す時間をしっかり取る道具に。", "calendar"), ("ボードゲーム 協力型", "協力型のボードゲーム", "柔らかな統率の練習に。勝ち負けでなく、みんなで解く遊びを。", "hobby")],
    "esfj": [("アロマキャンドル", "アロマキャンドル", "自分を満たす時間の年。ひとりでくつろぐ夜のお供に。", "aroma"), ("読書 ブックカバー", "お気に入りのブックカバー", "ほどよい距離をとって、自分のための読書時間を。", "book")],
    "istp": [("DIY キット", "DIYのキット", "技の共有の年。誰かと一緒に作ると、教える楽しさが見つかります。", "hobby"), ("レザークラフト キット", "レザークラフトのキット", "手を動かして作る時間が、2027年のあなたの力になります。", "hobby")],
    "isfp": [("インスタントカメラ", "インスタントカメラ", "形に残す年。気に入った景色や作品を一枚ずつ残して。", "hobby"), ("フォトアルバム", "フォトアルバム", "見せる勇気の年に、作ったものを並べて人に見せる一冊を。", "book")],
    "estp": [("家計簿", "家計簿", "腰をすえて積み上げる年。お金の流れを毎日つけてみて。", "stationery"), ("ランニングシューズ", "ランニングシューズ", "毎日続ける運動で、積み上げる感覚を体で覚えて。", "health")],
    "esfp": [("資格 問題集", "気になる資格の問題集", "学びと土台づくりの年。楽しく続けられる学びを一つ。", "book"), ("学習 タイマー", "勉強用のタイマー", "短い時間でも毎日続けると、土台がしっかりしていきます。", "calendar")],
    "top": [("MBTI 本", "MBTIの本", "16タイプの考え方をもっと詳しく知りたい人に。", "book"), ("性格 心理学 本", "性格心理学の入門書", "性格タイプの背景にある心理学の考え方を、やさしく。", "book")],
}
PHONE_TYPE = ("2027年の人間関係で迷ったら", "タイプの傾向はヒントの一つです。恋愛や職場の人間関係など、具体的に迷っていることがあるときは、占い師に事情を話して一緒に考えてもらうのもひとつの方法です。")
PHONE_TOP = ("相性や人間関係で迷ったら", "タイプどうしの相性は目安です。気になる人とのことを具体的に相談したいときは、占い師に話を聞いてもらうのもひとつの方法です。")
LINKS = [("/unsei-2027/", "2027年の運勢まとめ", "九星・干支・数秘術・マヤ暦・星座・誕生日から"),
         ("/366uranai/", "366日の誕生日占い", "誕生日ごとの性格と2027年の運勢"),
         ("/mbti-diag/", "MBTI診断", "質問に答えて自分のタイプを調べる"),
         ("/mbti-compatibility/", "MBTI相性占い", "16タイプ×16タイプの相性")]
LINK_CSS = ("<style>.tp-more{margin:28px 0 8px}.tp-more h2{font-size:1.2rem;margin:0 0 10px}"
            ".tp-more ul{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}"
            ".tp-more li{margin:0}.tp-more a{display:block;border:2px solid #26262E;border-radius:12px;background:#FFFBF2;color:#26262E;padding:10px 12px;text-decoration:none;font-weight:700}"
            ".tp-more a small{display:block;font-weight:500;color:#4A4855;font-size:.8rem;margin-top:2px}"
            "@media (max-width:640px){.tp-more ul{grid-template-columns:1fr}}"
            # 白い背景のMBTIページ用：広告の見出し・PR表記・説明を濃い文字に（共通CSSは暗い背景のページ向け）
            ".fh-b27 .fh-b27-adgoods-h,.fh-b27 .fh-b27-adgoods-h span{color:#26262E}.fh-b27 .fh-b27-adgoods .fh-b27-pr{color:#55525E}.fh-b27 .fh-b27-adgoods-l{color:#3E3C46}</style>")
MARK = "<!-- fh-mbti-add 2026-10-28 -->"


def head():
    return (MARK + "\n<style>.single_thumbnail{display:none!important}</style>\n"
            f'<link rel="stylesheet" href="{WP_ASSET}fh-b27.css?v={ASSET_VER}">\n' + AX.CSS + "\n" + LINK_CSS)


def links(self_url):
    items = "".join(f'<li><a href="{u}">{t} →<small>{s}</small></a></li>' for u, t, s in LINKS if u != self_url)
    return f'<nav class="tp-more" aria-label="あわせて読みたい"><h2>あわせて読みたい</h2><ul>{items}</ul></nav>'


def after_section(body, sid, html):
    m = re.search(rf'<section[^>]*id="{re.escape(sid)}"', body)
    assert m, sid
    end = body.find("</section>", m.end()) + len("</section>")
    return body[:end] + "\n" + html + body[end:]


def before_section(body, sid, html):
    m = re.search(rf'<section[^>]*id="{re.escape(sid)}"', body)
    assert m, sid
    return body[:m.start()] + html + "\n" + body[m.start():]


def wrap(x):
    return f'<div class="fh-b27">{x}</div>'


def process(body, key):
    if MARK in body:
        return body
    if key == "top":
        phone, gsec, psec = PHONE_TOP, "mbti-faq", "mbti-compat"
        last = "mbti-faq"
    else:
        phone, gsec, psec = PHONE_TYPE, f"{key}-lucky", f"{key}-relation"
        last = f"{key}-message"
    pb = AX.phone_box(*phone)
    gb = AX.goods_box("2027年のテーマに合わせて選んだアイテム" if key != "top" else "MBTIをもっと知りたい人に", GOODS[key],
                      lead="楽天・Yahoo!ショッピングの商品ページへ移ります。")
    assert pb and gb
    body = after_section(body, psec, wrap(pb))
    body = before_section(body, gsec, wrap(gb))
    body = after_section(body, last, links("/mbti/" if key == "top" else ""))
    return head() + "\n" + body


def main():
    src, dst = sys.argv[1], sys.argv[2]
    os.makedirs(dst, exist_ok=True)
    for k in TYPES + ["top"]:
        fn = "mbti_top_body.html" if k == "top" else f"{k}_body.html"
        b = open(os.path.join(src, fn), encoding="utf-8").read()
        o = process(b, k)
        open(os.path.join(dst, fn), "w", encoding="utf-8").write(o)
        print(fn, len(b), "→", len(o), "phone", o.count('data-aff="phone"'), "goods", o.count("fh-b27-shop\""), "links", o.count("tp-more\""))


if __name__ == "__main__":
    main()
