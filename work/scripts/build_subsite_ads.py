"""姉妹サイト（/enmusubi/・/kaiun/・/dream/）の各ページに入れる広告の箱を作る（2026-10-23 本人「サブページの広告を先に」）。
- 1ページ1か所。記事の本文（X-art）の後、出典（X-src）の前に入れる。目印 <!-- fh-sub-ad:start/end --> で囲み、入れ直しのときは差し替える
- 中身：A8 の文字リンク1つ（電話占い・パワーストーンの店）＋楽天/Yahoo!の商品の箱1つ（写真と商品が確かめ済みの品名だけ）
- 色は箱の中で固定（淡い地に濃い文字、濃い色のボタンに白い文字）。本人の絶対ルール「淡い色に白文字・濃い色に黒文字を置かない」
- 心コンパス（/kokoro/）は心理学の読み物なので、占いの広告は入れない（2026-10-23 判断）
出力：out/subsite_ads/<site>.json（パス → 入れるHTML）"""
import html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_html as B  # noqa: E402
import goods_media as GM  # noqa: E402

OUT = os.path.join(HERE, "..", "out", "subsite_ads")
SKIP = re.compile(r"/(privacy|privacy-policy|disclaimer|contact|operator|about|articles|glossary|unconfirmed)/$")
esc = lambda s: html.escape(s or "", quote=True)

CSS = ("<style>.fhad{margin:28px auto;max-width:760px;border:1px solid #D8C9A8;border-radius:14px;background:#F7F1E3;color:#2E2A26;"
       "padding:16px 18px;font-size:15px;line-height:1.8;box-sizing:border-box}"
       ".fhad *{box-sizing:border-box}.fhad p{margin:0 0 10px;color:#2E2A26}.fhad b{color:#2E2A26}"
       ".fhad-h{font-weight:700;font-size:14px;color:#5E574D;margin:0 0 8px}.fhad-pr{display:inline-block;border:1px solid #8A6A2A;"
       "color:#6B4E10;border-radius:4px;font-size:11px;line-height:1.4;padding:0 5px;margin-right:6px;background:#FFF9EA}"
       ".fhad a.fhad-line{color:#8A3B12;font-weight:700;text-decoration:underline}"
       ".fhad-box{display:grid;grid-template-columns:96px minmax(0,1fr);gap:12px;align-items:center;background:#FFFDF7;border:1px solid #E6DCC6;"
       "border-radius:12px;padding:10px;margin-top:10px}"
       ".fhad-pic{display:block;width:96px;height:96px;border-radius:8px;background:#fff center/contain no-repeat}"
       ".fhad-name{display:block;font-weight:700;color:#2E2A26;font-size:15px;line-height:1.5}"
       ".fhad-prod{display:block;color:#5E574D;font-size:12px;line-height:1.5;margin-top:2px}"
       ".fhad-btns{grid-column:1/-1;display:flex;gap:8px;flex-wrap:wrap}"
       ".fhad a.fhad-btn{flex:1 1 140px;display:inline-flex;align-items:center;justify-content:center;min-height:44px;border-radius:999px;"
       "font-weight:700;font-size:14px;color:#FFFFFF;text-decoration:none}"
       ".fhad a.fhad-rk{background:#BF0000}.fhad a.fhad-yh{background:#C7004C}"
       "@media(max-width:480px){.fhad{padding:14px}.fhad-box{grid-template-columns:72px minmax(0,1fr)}.fhad-pic{width:72px;height:72px}}</style>")

PHONE_LINE = {"enmusubi": "ご縁や相手の気持ちについて、ひとりで考えこむより人に話して整理したいときは、占い師に直接相談できる電話占いもひとつの方法です。",
              "dream": "気になる夢が続くときは、夢の内容を人に話すだけで気持ちが整理されることもあります。占い師に直接相談できる電話占いもひとつの方法です。"}
STONE_LINE = "身につけるお守りとして天然石を選ぶなら、石の種類や色から探せるパワーストーンの専門店もあります。"


def page_plan(site, path):
    """(A8 の文字リンクの種類, 楽天の品名, 品の前の一言)"""
    p = path
    if site == "enmusubi":
        if "/shrine" in p or "/tool-shurin" in p:
            return ("phone", "お守り袋", "授かったお守りや大切な小物を持ち歩くなら、口の閉まるお守り袋に入れておくと傷みにくくなります。")
        if "/world" in p:
            return ("hariqua", "ローズクォーツ ブレスレット", "恋愛の石として知られるローズクォーツは、やわらかな桃色で毎日身につけやすい石です。")
        if "/calendar" in p or "/step-record" in p or "/step-review" in p:
            return ("phone", "一行日記帳", "読んだ結果や日々の小さな変化は、一行だけでも書き残しておくと、あとで見直すときの手がかりになります。")
        return ("phone", "ローズクォーツ ブレスレット", "恋愛の石として知られるローズクォーツは、やわらかな桃色で毎日身につけやすい石です。")
    if site == "kaiun":
        if "/wallet" in p or "/money" in p:
            return ("pascle", "上質な財布", "財布を替えるときは、色や形より、お札が折れずに入るか・小銭が取り出しやすいかで選ぶと長く気持ちよく使えます。")
        if "/purify-aroma" in p:
            return ("hariqua", "アロマディフューザー", "香りで部屋の空気を整えるなら、強すぎない香りを少しずつ広げるディフューザーが気軽です。")
        if "/interior-plants" in p:
            return ("hariqua", "小さな観葉植物", "置き場所に迷ったら、日当たりが弱くても育つ小さな鉢から始めると続けやすくなります。")
        if "/layout-bedroom" in p or "/step-sleep" in p:
            return ("hariqua", "安眠用のアイピロー", "寝る前に目元を温めたり暗くしたりすると、気持ちが落ち着き眠りに入りやすくなります。")
        if "/season" in p or "/calendar" in p:
            return ("pascle", "一行日記帳", "季節の行事や吉日に何をしたかを一行ずつ書き残しておくと、一年の流れが見えてきます。")
        if "/wallet-choose" in p:
            return ("pascle", "上質な財布", "")
        return ("pascle" if sum(map(ord, p)) % 2 else "hariqua", "ルチルクォーツ ブレスレット", "金色の針のような結晶が入ったルチルクォーツは、前へ進む力の石として人気があります。")
    if site == "dream":
        return ("phone", "一行日記帳", "夢は起きてすぐに書き留めると、あとで読み返したときに意味が見えやすくなります。枕元に小さな日記帳を置いておくのがおすすめです。")
    return None


def a8_line(kind, site):
    if kind == "phone":
        t = B.AFF_TPL.get("phone")
        if not t:
            return ""
        return (f'<p><span class="fhad-pr">PR</span>{esc(PHONE_LINE[site])} '
                f'<a class="fhad-line" href="{esc(t["href"])}" rel="nofollow sponsored">電話占いで相談してみる →</a>{t["impression"]}</p>')
    v = B.A8S.get(kind)
    if not v:
        return ""
    return (f'<p><span class="fhad-pr">PR</span>{esc(STONE_LINE)} '
            f'<a class="fhad-line" href="{esc(v["href"])}" rel="nofollow sponsored">{esc(v["name"])}で天然石を見る →</a>{v["impression"]}</p>')


def product_box(q, lead):
    it = GM.photo(q)
    if not it:
        return ""
    rk, yh = B.aff_href("rakuten", q), B.aff_href("yahoo", q)
    prod = re.sub(r"<[^>]+>", "", GM.price_html(q))
    pic = f'<a class="fhad-pic" href="{esc(rk)}" rel="nofollow sponsored" tabindex="-1" aria-hidden="true" style="background-image:url(\'{esc(it["img"])}\')"></a>'
    btns = (f'<a class="fhad-btn fhad-rk" href="{esc(rk)}" rel="nofollow sponsored">楽天で見る</a>{B.AFF_TPL["rakuten"]["impression"]}'
            f'<a class="fhad-btn fhad-yh" href="{esc(yh)}" rel="nofollow sponsored">Yahoo!で探す</a>{B.AFF_TPL["yahoo"]["impression"]}')
    return ((f"<p>{esc(lead)}</p>" if lead else "") +
            f'<div class="fhad-box">{pic}<div><span class="fhad-pr">PR</span><span class="fhad-name">{esc(B.disp_name(q))}</span>'
            f'<span class="fhad-prod">{esc(prod)}</span></div><div class="fhad-btns">{btns}</div></div>')


def build(site, path):
    if SKIP.search(path):
        return None
    pl = page_plan(site, path)
    if not pl:
        return None
    kind, q, lead = pl
    body = a8_line(kind, site) + product_box(q, lead)
    if not body:
        return None
    return ("<!-- fh-sub-ad:start -->" + CSS + '<aside class="fhad" aria-label="広告">'
            '<p class="fhad-h">この記事に関連して（広告）</p>' + body + "</aside><!-- fh-sub-ad:end -->")


def main():
    B.AFF_TPL.update(B.load_aff_templates())
    B.A8S.update(B.load_a8_shops())
    os.makedirs(OUT, exist_ok=True)
    paths = json.load(open(os.path.join(OUT, "paths.json"), encoding="utf-8"))  # {site: [path,...]}（本番のページ一覧）
    for site, ps in paths.items():
        res = {p: h for p in ps if (h := build(site, p))}
        json.dump(res, open(os.path.join(OUT, f"{site}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(site, len(ps), "ページ中", len(res), "ページに広告")


if __name__ == "__main__":
    main()
