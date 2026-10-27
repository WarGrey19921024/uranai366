"""干支（十二支）別 2027年の運勢（/unsei-2027/eto/）と、2027年の運勢の入口（/unsei-2027/）。
数値は calc_eto_2027.py → data/eto_2027.json（支合・三合・冲・五行・月ごとの関係・生まれ年・年男年女）。
文章は eto2027_texts.py（重複検査 check_eto2027.py）。見た目は /kyusei/ と同じ CSS（data-fh-page="kyusei"）を使う。
"""
import datetime as dt, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_hub import OUT, WORK, shell  # noqa: E402
from build_shukuyo import esc  # noqa: E402
from build_kyusei import CSS as KY_CSS  # noqa: E402
from build_nenun2027 import CSS as NY_CSS  # noqa: E402
import eto2027_texts as ET  # noqa: E402

URL = "/unsei-2027/eto/"
HUB = "/unsei-2027/"
DATA = os.path.join(WORK, "data", "eto_2027.json")
SHI = "子丑寅卯辰巳午未申酉戌亥"
YOMI = ["ね", "うし", "とら", "う", "たつ", "み", "うま", "ひつじ", "さる", "とり", "いぬ", "い"]
COL = {"水": "#3D6E9B", "土": "#B88A3E", "木": "#4F8A55", "火": "#C2453A", "金": "#C9C2B0"}
REL_LABEL = {"支合": "支合（結びつく）", "三合": "三合（仲間）", "冲": "冲（向かい合う）", "同じ支": "年男・年女", None: "特別な関係なし"}
MREL = {"支合": "支合", "三合": "三合", "冲": "冲", "同じ支": "自分の支"}

FAQ = [
    ("2027年の干支は何ですか。", "2027年の干支は丁未（ひのとひつじ）です。九星気学や四柱推命と同じく、このページでは2027年2月4日の立春から、翌年の立春の前までを「2027年」として読んでいます。"),
    ("1月生まれは、どの干支を読めばいいですか。", "立春（2月4日ごろ）より前に生まれた人は、ひとつ前の年の干支になります。たとえば2000年1月20日生まれなら、2000年の辰ではなく1999年の卯を読みます。早見表の生まれ年は「その年の立春から翌年の立春の前日まで」です。"),
    ("冲（ちゅう）の年や月は悪いことが起きますか。", "冲は、方角が正反対の支どうしが向かい合う関係です。このサイトでは「変化や動きが起こりやすい」と読み、悪いことが起きるという意味では使っていません。引っ越しや転職など、自分から動く変化には追い風になることもあります。"),
    ("刑・害・破は見ないのですか。", "刑・害・破は流派によって組み合わせや読み方の差が大きいため、このサイトでは扱っていません。支合・三合・冲の3つだけで、年や月との関係を読んでいます。"),
    ("九星気学の運勢とどちらを見ればいいですか。", "どちらも生まれ年から読む占いですが、見ているものが違います。干支は十二支どうしの関係、九星気学は九つの星の位置と方位です。両方読み比べて、共通して出ている時期を大切にするのがおすすめです。"),
]


def mlabel(m):
    s, e = m["start"], m["end"]
    return f"{int(s[5:7])}月", f"{int(s[5:7])}/{int(s[8:])}〜{int(e[5:7])}/{int(e[8:])}"


def build(sample, updated):
    D = json.load(open(DATA, encoding="utf-8"))
    E, MS = D["eto"], D["months"]
    assert len(MS) == 12 and D["year"]["kanshi"] == "丁未"
    H = []
    a = H.append
    a(KY_CSS)
    a(NY_CSS)
    a("""<style>.fh-b27-et-big{display:flex;align-items:center;justify-content:center;width:120px;height:120px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#F6F0E2,#D9C9A3);color:#3A2A14;font:800 54px 'Shippori Mincho',serif;box-shadow:0 0 0 3px rgba(212,175,90,.6),0 10px 30px rgba(0,0,0,.45);margin:10px}
.fh-b27-et-rel{display:inline-block;border-radius:2px;padding:1px 8px;font-size:12.5px;font-weight:700;background:#EFE4C8;color:#4A3B1C;margin-left:6px}
.fh-b27-et-rel.g{background:#DCEBD9;color:#22462A}.fh-b27-et-rel.c{background:#F7DCD6;color:#6E2318}
.fh-b27 .fh-b27-et-char{color:var(--sub);font-size:14px;margin:0 0 6px}
@media (max-width:640px){.fh-b27-et-big{width:84px;height:84px;font-size:38px}}</style>""")
    a('<div class="fh-b27" data-fh-page="kyusei">\n<div class="fh-b27-note">')
    a('''<header class="fh-b27-hero">
  <div class="fh-b27-et-big" aria-hidden="true">未</div>
  <div class="fh-b27-hero-body">
    <span class="fh-b27-tape">2027年の運勢</span>
    <h1 class="fh-b27-title">干支でみる<br>2027年の運勢 十二支別</h1>
    <p class="fh-b27-lead">2027年は丁未（ひのとひつじ）の年です。子年から亥年まで、生まれ年の十二支が「未」とどう結びつくかで、総合運・恋愛・仕事・お金・健康と、月ごとの流れを読みました。生まれ年の早見表と、年男・年女の年齢もまとめています。</p>
  </div>
</header>''')
    items = [("et-hayami", "生まれ年の早見表"), ("et-how", "2027年と干支の関係"), ("et-list", "十二支別 2027年の運勢"), ("et-faq", "よくある質問")]
    a('<nav class="fh-b27-toc" aria-label="目次"><strong>このページの内容</strong><ol>' + "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in items) + "</ol></nav>")
    n = [1]

    def h2(t):
        s = f'<h2><span class="fh-b27-n">{n[0]:02d}</span>{t}</h2>'
        n[0] += 1
        return s

    rows = "".join(f'<tr style="--c:{COL[E[s]["gogyo"]]}"><th scope="row"><i></i><a href="#et-{i}">{s}（{YOMI[i]}）</a></th><td>{"・".join(str(y) for y in E[s]["years"])}年</td></tr>' for i, s in enumerate(SHI))
    jump = "".join(f'<a href="#et-{i}" style="--c:{COL[E[s]["gogyo"]]}">{s}年（{E[s]["animal"]}）<small>{esc(ET.TEXTS[s]["title"])}</small></a>' for i, s in enumerate(SHI))
    a(f'''<section class="fh-b27-sec" id="et-hayami">
  {h2("生まれ年の早見表")}
  <p>生まれた年の十二支を探してください。干支の年は立春（2月4日ごろ）で切り替わるので、<b>1月1日から立春の前日までに生まれた人は、ひとつ前の年の支</b>を読みます。</p>
  <div class="fh-b27-ky-wrap"><table class="fh-b27-ky-t fh-b27-ny-hy"><thead><tr><th>十二支</th><th>生まれ年（1930〜2026年）</th></tr></thead><tbody>{rows}</tbody></table></div>
  <p style="margin-top:12px"><b>読みたい干支へ</b></p>
  <div class="fh-b27-ny-jump">{jump}</div>
</section>''')
    ages = "・".join(str(x) for x in E["未"]["toshi_otoko_ages"])
    rel_rows = "".join(f'<tr><th scope="row">{s}年</th><td>{REL_LABEL[E[s]["rel"]]}</td><td>{E[s]["gogyo"]}（{E[s]["gogyo_rel"]}）</td></tr>' for s in SHI)
    a(f'''<section class="fh-b27-sec" id="et-how">
  {h2("2027年と干支の関係")}
  <p>{esc(ET.INTRO["rels"])}</p>
  <div class="fh-b27-ky-wrap"><table class="fh-b27-ky-t fh-b27-ny-mb" style="min-width:420px"><thead><tr><th>生まれ年</th><th>「未」との関係</th><th>五行（年の土から見て）</th></tr></thead><tbody>{rel_rows}</tbody></table></div>
  <h3>年男・年女の2027年</h3>
  <p>{esc(ET.INTRO["toshi"])}</p>
  <p><small>2027年に年男・年女になる年齢：{ages}歳</small></p>
</section>''')
    a(f'<section class="fh-b27-sec" id="et-list">\n  {h2("十二支別 2027年の運勢")}')
    for i, s in enumerate(SHI):
        T, e = ET.TEXTS[s], E[s]
        rc = "g" if e["rel"] in ("支合", "三合", "同じ支") else "c" if e["rel"] == "冲" else ""
        mrows = []
        for m, r in zip(MS, e["month_rel"]):
            mo, rng = mlabel(m)
            tag = f'<em class="{"s" if r in ("支合", "三合", "同じ支") else ""}">{MREL[r]}</em>' if r else ""
            mrows.append(f'<tr><td class="m">{mo}<br><small>{rng}</small></td><td class="p">{m["branch"]}月{tag}</td></tr>')
        gm = "".join(f"<li>{esc(k)}：{esc(v)}</li>" for k, v in T["good_months"])
        ck, cv = T["care_month"]
        act = "".join(f"<li>{esc(x)}</li>" for x in T["action"])
        a(f'''<article class="fh-b27-ny-star" id="et-{i}" style="--c:{COL[e["gogyo"]]}">
  <h3>{s}年（{e["animal"]}年）生まれ<small>{YOMI[i]}・五行は{e["gogyo"]}</small></h3>
  <p class="fh-b27-et-char">{esc(T["char"])}</p>
  <span class="fh-b27-ny-theme">2027年は「{esc(T["title"])}」</span><span class="fh-b27-et-rel {rc}">{REL_LABEL[e["rel"]]}</span>
  <p>{esc(T["sougou"])}</p>
  <div class="fh-b27-ny-4">
    <div><b>恋愛運</b><p>{esc(T["love"])}</p></div>
    <div><b>仕事運</b><p>{esc(T["work"])}</p></div>
    <div><b>金運</b><p>{esc(T["money"])}</p></div>
    <div><b>健康運</b><p>{esc(T["health"])}</p></div>
  </div>
  <div class="fh-b27-ny-gm"><ul class="g"><strong>追い風の月</strong>{gm}</ul><ul class="c"><strong>変化に備えたい月</strong><li>{esc(ck)}：{esc(cv)}</li></ul></div>
  <details style="margin-top:6px"><summary style="cursor:pointer;font-weight:700">月ごとの支と関係（12か月）</summary>
  <div class="fh-b27-ky-wrap"><table class="fh-b27-ky-t fh-b27-ny-mb" style="min-width:0"><thead><tr><th>月</th><th>月の支と関係</th></tr></thead><tbody>{"".join(mrows)}</tbody></table></div></details>
  <p style="margin-top:8px"><b>2027年の開運アクション</b></p><ul class="fh-b27-ny-act">{act}</ul>
</article>''')
        if i in (3, 7):
            a(f"<!--Ads{(i + 1) // 4}-->")
    a("</section>")
    qa = "".join(f'<details{" open" if i == 0 else ""}><summary>Q. {q}</summary><p>A. {x}</p></details>' for i, (q, x) in enumerate(FAQ))
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in FAQ]}
    a(f'''<section class="fh-b27-sec" id="et-faq">
  {h2("よくある質問")}
  <div class="fh-b27-ky-qa">{qa}</div>
</section>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<section class="fh-b27-sec">
  <div class="fh-b27-links">
    <a href="/kyusei/unsei-2027/"><b>2027年の運勢（九星気学）→</b><small>本命星別の総合運と月ごとの吉方位</small></a>
    <a href="/unsei-2027/"><b>2027年の運勢まとめ →</b><small>九星・干支・数秘術・マヤ暦・星座・誕生日から</small></a>
    <a href="/366uranai/"><b>366日の誕生日占い →</b><small>誕生日ごとの2027年の運勢</small></a>
    <a href="/kaiun/kichijitsu-2027/"><b>2027年の吉日カレンダー →</b><small>開運ライフ｜天赦日・一粒万倍日</small></a>
  </div>
</section>''')
    up = dt.date.fromisoformat(updated)
    a(f'<p class="fh-b27-foot">生まれ年の干支・月の支は、立春と節入りの日時（日本時間）からこのサイトで計算しています。年や月との関係は、支合・三合・冲の3つで読んでいます（刑・害・破は扱いません）。文章はこのサイトで書いたもので、占いは楽しみと気づきのためにお読みください。<br>'
      f'最終更新日：{up.year}年{up.month}月{up.day}日／<a href="/about/">この記事の作成方針について</a></p>')
    a("</div>\n</div>")
    title = "2027年の運勢｜干支（十二支）別 子年〜亥年の総合運・恋愛・仕事・金運【丁未・年男年女の年齢も】"
    desc = "2027年（丁未・ひつじ年）の運勢を、子年から亥年まで十二支別に紹介。生まれ年の支と「未」の関係（支合・三合・冲）から、総合運・恋愛・仕事・金運・健康運、追い風の月を読みます。生まれ年の早見表と年男・年女の年齢つき。"
    out = shell(title, desc, URL, "\n".join(H), sample, ())
    assert "！" not in out
    return out, title, desc


HUB_LINKS = [
    ("/kyusei/unsei-2027/", "九星気学", "本命星別（一白水星〜九紫火星）", "総合運・恋愛・仕事・金運、月ごとのヒントと吉方位"),
    ("/unsei-2027/eto/", "干支", "十二支別（子年〜亥年）", "生まれ年の支と「未」の関係から読む一年"),
    ("/unsei-2027/suhi/", "数秘術", "2027年の数（1〜9）別", "誕生月と誕生日から出す、9年周期のいまの位置"),
    ("/unsei-2027/maya/", "マヤ暦", "20の太陽の紋章別", "7月26日から始まる白い魔法使いの年と、あなたの紋章の関係"),
    ("/star/", "星座", "12星座別", "星の動きから見る2027年のランキングと月ごとの運勢"),
    ("/366uranai/", "誕生日", "366日の誕生日別", "誕生日ごとの性格と2027年の月ごとの運勢"),
    ("/kaiun/kichijitsu-2027/", "吉日", "2027年の吉日カレンダー", "天赦日・一粒万倍日・寅の日など（開運ライフ）"),
]


def build_hub(sample, updated):
    H = []
    a = H.append
    a(KY_CSS)
    a(NY_CSS)
    a('<div class="fh-b27" data-fh-page="kyusei">\n<div class="fh-b27-note">')
    a('''<header class="fh-b27-hero">
  <div class="fh-b27-hero-body">
    <span class="fh-b27-tape">2027年の運勢</span>
    <h1 class="fh-b27-title">2027年の運勢まとめ<br>九星・干支・数秘術・マヤ暦・星座・誕生日から</h1>
    <p class="fh-b27-lead">2027年は九紫火星が年盤の中央に入る、丁未（ひのとひつじ）の年です。このサイトで公開している2027年の運勢を、占い別にまとめました。生まれ年から読むなら九星気学と干支、生まれた月日から読むなら星座と誕生日のページがおすすめです。</p>
  </div>
</header>''')
    cards = "".join(f'<a href="{u}" style="--c:#D4AF5A"><b>{esc(t)}</b><small>{esc(k)}｜{esc(d)}</small></a>' for u, k, t, d in HUB_LINKS)
    a(f'''<section class="fh-b27-sec">
  <h2><span class="fh-b27-n">01</span>占い別 2027年の運勢</h2>
  <div class="fh-b27-links">{cards}</div>
</section>
<section class="fh-b27-sec">
  <h2><span class="fh-b27-n">02</span>2027年はどんな年</h2>
  <p>年の切り替わりは、九星気学と干支では2027年2月4日の立春です。星座と誕生日のページは1月1日から12月31日で読んでいます。九紫火星は明るさや学び、表に出ることを表す星で、丁未は火が土を育てる組み合わせの干支です。物事がはっきりし、これまでの取り組みが形や評価になって表れやすい一年と、このサイトでは読んでいます。</p>
</section>''')
    up = dt.date.fromisoformat(updated)
    a(f'<p class="fh-b27-foot">最終更新日：{up.year}年{up.month}月{up.day}日／<a href="/about/">この記事の作成方針について</a></p>')
    a("</div>\n</div>")
    title = "2027年の運勢まとめ｜九星気学・干支・数秘術・マヤ暦・星座・誕生日から読む一年【無料】"
    desc = "2027年（丁未・九紫火星中宮）の運勢を、九星気学の本命星別、干支（十二支）別、12星座別、366日の誕生日別にまとめた入口ページ。吉日カレンダーもあわせてどうぞ。"
    out = shell(title, desc, HUB, "\n".join(H), sample, ())
    assert "！" not in out
    return out, title, desc


def main():
    updated = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    for fn, name in ((build, "unsei-2027-eto"), (build_hub, "unsei-2027")):
        for sample, path in ((False, os.path.join(OUT, f"{name}.html")), (True, os.path.join(OUT, "sample", f"{name}.html"))):
            with open(path, "w", encoding="utf-8") as fp:
                fp.write(fn(sample, updated)[0])
            print("→", os.path.relpath(path, WORK))


if __name__ == "__main__":
    main()
