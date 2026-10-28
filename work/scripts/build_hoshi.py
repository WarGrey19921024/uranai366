"""星のこよみ（/hoshi/、ID 5802）と水星逆行（/hoshi/mercury-retrograde/、ID 5803）を2027年版に作り直す（2026-10-18）。
日時は calc_hoshi.py（data/hoshi_2027.json）と sekki_2027.json の計算。2027年の新月・満月25回と二十四節気は国立天文台の暦要項と照合済み
（清明だけ計算が1分ずれるので暦要項の 9:17 を使う）。2026年10〜12月の残りの予定も載せる（年末まではまだ使えるため）。
注意：WordPress（Diver）は [sp] [pc] などをショートコードとして消すので、JSを使わない（このページは静的な表だけ）。
使い方: python work/scripts/build_hoshi.py [最終更新日]
出力: work/out/hoshi.html・work/out/mercury.html（投入用）、work/out/sample/ に確認用
"""
import datetime as dt, html, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_hub import OUT, WORK, DATA, shell  # noqa: E402

H27 = json.load(open(os.path.join(DATA, "hoshi_2027.json"), encoding="utf-8"))
SK = json.load(open(os.path.join(DATA, "sekki_2027.json"), encoding="utf-8"))
SK = SK if isinstance(SK, list) else SK["list"]
NAOJ_FIX = {"清明": "2027-04-05 09:17"}
SIGNS = ["牡羊座", "牡牛座", "双子座", "蟹座", "獅子座", "乙女座", "天秤座", "蠍座", "射手座", "山羊座", "水瓶座", "魚座"]
SIGN_URL = ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]
WD = "月火水木金土日"
HOUSE = {1: "自分のこと・見た目・始め方", 2: "お金・持ち物・稼ぎ方", 3: "連絡・学び・近所や身近な人", 4: "家・家族・住まい", 5: "恋愛・趣味・子ども",
         6: "仕事の段取り・体調・毎日の習慣", 7: "パートナー・契約・一対一の関係", 8: "共有のお金・深い信頼関係", 9: "旅行・勉強・遠くの人",
         10: "仕事の目標・立場・評価", 11: "友人・仲間・将来の夢", 12: "心の整理・休息・ひとりの時間"}


def esc(s):
    return html.escape(str(s), quote=True)


def pt(s):
    t = dt.datetime.strptime(s[:16], "%Y-%m-%d %H:%M") if len(s) > 10 else dt.datetime.strptime(s, "%Y-%m-%d")
    return t


def md(s, time=True):
    t = pt(s)
    base = f"{t.month}月{t.day}日（{WD[t.weekday()]}）"
    return base + (f" {t.hour}:{t.minute:02d}" if time and len(s) > 10 else "")


CSS = """<style id="fh-b27-hs-css">
.fh-b27[data-fh-page="hoshi"]{--ink:#EEF2FF;--sub:#D0D7F2;--mute:#A9B2D6;--paper:#141A33;--deep:#0F1429;--line:#38406B;--gold:#F4D58A;--cream:#FFFCF4;--cream-ink:#232846}
.fh-b27[data-fh-page="hoshi"] a{color:#FFE2A3}
.fh-b27[data-fh-page="hoshi"] .fh-b27-sec>p,.fh-b27[data-fh-page="hoshi"] .fh-b27-lead{text-shadow:0 1px 2px rgba(0,0,0,.6)}
.fh-b27[data-fh-page="hoshi"] .fh-b27-note{border-left:0;border-radius:24px;background-color:var(--paper);
 background-image:radial-gradient(1.5px 1.5px at 8% 3%,#fff 50%,transparent 51%),radial-gradient(1px 1px at 22% 1.5%,#fff 50%,transparent 51%),radial-gradient(1.5px 1.5px at 47% 4%,#fff 50%,transparent 51%),radial-gradient(1px 1px at 63% 2%,#fff 50%,transparent 51%),radial-gradient(2px 2px at 88% 3.5%,#FFE9B0 50%,transparent 51%),radial-gradient(1px 1px at 95% 1%,#fff 50%,transparent 51%),linear-gradient(180deg,#1C2448 0%,#141A33 35%,#10152B 100%);background-size:auto;background-repeat:no-repeat;box-shadow:0 18px 40px rgba(0,0,0,.3)}
.fh-b27[data-fh-page="hoshi"] .fh-b27-hero{align-items:center}
.fh-b27-hs-moon{width:110px;height:110px;border-radius:50%;flex:0 0 auto;background:radial-gradient(circle at 35% 35%,#FFF7DC,#F4D58A 55%,#C9A24F);box-shadow:0 0 40px rgba(244,213,138,.55);position:relative;overflow:hidden}
.fh-b27-hs-moon:after{content:"";position:absolute;inset:0;border-radius:50%;background:#141A33;transform:translateX(60%);animation:fh-b27-hs-phase 8s ease-in-out infinite alternate}
@keyframes fh-b27-hs-phase{to{transform:translateX(105%)}}
.fh-b27[data-fh-page="hoshi"] .fh-b27-tape{transform:none;border-radius:999px;background:linear-gradient(90deg,#F4D58A,#8E9BE8);color:#141A33}
.fh-b27[data-fh-page="hoshi"] .fh-b27-title{font-family:'Shippori Mincho',serif;font-weight:800;font-size:30px}
.fh-b27[data-fh-page="hoshi"] h2{font-family:'Shippori Mincho',serif;font-weight:800;font-size:24px}
.fh-b27[data-fh-page="hoshi"] h2 .fh-b27-n{border:0;border-radius:50%;background:linear-gradient(135deg,#F4D58A,#8E9BE8);color:#141A33}
.fh-b27[data-fh-page="hoshi"] .fh-b27-toc{border-style:solid;border-radius:18px;border-color:rgba(244,213,138,.3)}
.fh-b27[data-fh-page="hoshi"] .fh-b27-toc ol{columns:2;column-gap:28px}
.fh-b27-hs-soon{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:6px}
.fh-b27-hs-soon li{border:1px solid rgba(244,213,138,.25);border-radius:12px;background:var(--deep);padding:8px 12px;font-size:14.5px;display:flex;gap:10px;flex-wrap:wrap}
.fh-b27-hs-soon li b{color:#FFE2A3;min-width:9.5em}
.fh-b27-hs-tbl{width:100%;border-collapse:collapse;font-size:14px}
.fh-b27-hs-tbl th,.fh-b27-hs-tbl td{border-bottom:1px dashed var(--line);padding:6px 6px;text-align:left;vertical-align:top}
.fh-b27-hs-tbl thead th{color:#FFE2A3;font-weight:800}.fh-b27-hs-tbl tbody th{white-space:nowrap;color:#FFE2A3}
.fh-b27-hs-tbl td small{color:var(--mute)}
.fh-b27-hs-tag{display:inline-block;border-radius:999px;background:rgba(244,213,138,.18);color:#FFE2A3;font-size:11.5px;padding:0 8px;margin-left:4px}
.fh-b27-hs-cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.fh-b27-hs-cards div{border:1px solid rgba(244,213,138,.22);border-radius:14px;background:var(--deep);padding:10px 14px;font-size:14px;line-height:1.85}
.fh-b27-hs-cards b{color:#FFE2A3;font-size:15.5px}
.fh-b27-hs-bar{position:relative;height:30px;border-radius:8px;background:rgba(255,255,255,.06);margin:6px 0 2px;overflow:hidden}
.fh-b27-hs-bar span{position:absolute;top:0;bottom:0;display:flex;align-items:center;justify-content:center;font-size:11.5px;font-weight:800;color:#141A33;white-space:nowrap;overflow:hidden}
.fh-b27-hs-bar .sh{background:rgba(244,213,138,.65)}.fh-b27-hs-bar .rx{background:#F4D58A}
.fh-b27-hs-signs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.fh-b27-hs-signs details{border:1px solid rgba(244,213,138,.2);border-radius:12px;background:var(--deep);padding:6px 12px;font-size:14px;line-height:1.85}
.fh-b27-hs-signs summary{cursor:pointer;font-weight:800;color:#FFE2A3}
.fh-b27-hs-signs ul{margin:4px 0;padding-left:1.1em}
.fh-b27-hs-qa details{border-bottom:1px dashed var(--line);padding:8px 2px}
.fh-b27-hs-qa summary{cursor:pointer;font-weight:700}
.fh-b27-hs-qa p{margin-top:6px;font-size:14.5px}
.fh-b27-hs-scroll{overflow-x:auto}
@media (max-width:640px){.fh-b27-hs-cards,.fh-b27-hs-signs{grid-template-columns:1fr}.fh-b27[data-fh-page="hoshi"] .fh-b27-toc ol{columns:1}.fh-b27[data-fh-page="hoshi"] .fh-b27-title{font-size:25px}.fh-b27-hs-moon{width:80px;height:80px}.fh-b27-hs-soon li b{min-width:0}}
@media (prefers-reduced-motion:reduce){.fh-b27-hs-moon:after{animation:none}}
</style>"""


def hero(tape, title, lead):
    return f'''<header class="fh-b27-hero">
  <div class="fh-b27-hs-moon" aria-hidden="true"></div>
  <div class="fh-b27-hero-body">
    <span class="fh-b27-tape">{tape}</span>
    <h1 class="fh-b27-title">{title}</h1>
    <p class="fh-b27-lead">{lead}</p>
  </div>
</header>'''


def toc(items):
    return '<nav class="fh-b27-toc" aria-label="目次"><strong>このページの内容</strong><ol>' + "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in items) + "</ol></nav>"


def mk_h2():
    n = [0]

    def h2(t):
        n[0] += 1
        return f'<h2><span class="fh-b27-n">{n[0]}</span><span>{t}</span></h2>'
    return h2


def foot(updated):
    up = dt.date.fromisoformat(updated)
    return (f'<p class="fh-b27-foot">新月・満月・二十四節気・日食の日時は、このサイトで計算し、国立天文台暦計算室の「令和9年（2027）暦要項」と照合した日本時です（分は四捨五入）。'
            f'逆行や星座の移り変わりはこのサイトの計算（Swiss Ephemeris）です。星占いでの意味づけは、広く知られている読み方をもとにこのサイトで書いたものです。'
            f'最終更新日：{up.year}年{up.month}月{up.day}日／<a href="/about/">この記事の作成方針について</a></p>')


def soon_items():
    ev = []
    for m in H27["moons"]:
        if m["jst"] < "2027-01-01":
            ev.append((m["jst"], f'{m["kind"]}（{m["sign"]}）' + ("　2026年でいちばん大きく見える満月" if m["jst"].startswith("2026-12-24") else "")))
    for s in H27["sekki_2026q4"]:
        ev.append((s["jst"], s["name"]))
    for n, lst in H27["stations"].items():
        for s in lst:
            if s["jst"] < "2027-01-01":
                ev.append((s["jst"], f'{n}の{s["kind"]}（{s["sign"]}）'))
    ev.sort()
    return ev


def faq_html(faq):
    qa = "".join(f'<details{" open" if i == 0 else ""}><summary>Q. {esc(q)}</summary><p>A. {esc(x)}</p></details>' for i, (q, x) in enumerate(faq))
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in faq]}
    return qa, json.dumps(ld, ensure_ascii=False)


def build_hoshi(sample, updated):
    H, a = [], None
    H.append(CSS)
    a = H.append
    a('<div class="fh-b27" data-fh-page="hoshi">\n<div class="fh-b27-note">')
    a(hero("人生予報 星のこよみ", "星のこよみ2027<br>新月・満月・日食・逆行の日付",
           "2027年の空で起こる新月・満月、日食・月食、水星逆行などの星の動き、二十四節気の日時をひとつにまとめました。2026年の年末までの予定も先にのせています。「新月にお願いごと」「水星逆行は見直しの時期」など、星占いでよく聞く日付を確かめるためのページです。"))
    items = [("b27-hs-soon", "これからの星の予定（2026年10〜12月）"), ("b27-hs-moon", "2027年の新月・満月"), ("b27-hs-ecl", "2027年の日食・月食"),
             ("b27-hs-rx", "2027年の逆行"), ("b27-hs-big", "2027年の大きな星の動き"), ("b27-hs-sekki", "2027年の二十四節気"), ("b27-hs-use", "新月・満月の過ごし方"), ("b27-hs-faq", "よくある質問")]
    a(toc(items))
    h2 = mk_h2()
    li = "".join(f'<li><b>{esc(md(t))}</b><span>{esc(x)}</span></li>' for t, x in soon_items())
    a(f'''<section class="fh-b27-sec" id="b27-hs-soon">
  {h2("これからの星の予定（2026年10〜12月）")}
  <p>2026年も、まだ大事な星の動きが続きます。10月24日からは今年3回目の水星逆行、10月3日から11月14日までは金星も逆行しています。くわしくは<a href="/hoshi/mercury-retrograde/">水星逆行のページ</a>へ。</p>
  <ul class="fh-b27-hs-soon">{li}</ul>
</section>''')
    m27 = [m for m in H27["moons"] if m["jst"].startswith("2027")]
    fulls = [m for m in m27 if m["kind"] == "満月"]
    big = min(fulls, key=lambda x: x["km"])["jst"]
    small = max(fulls, key=lambda x: x["km"])["jst"]
    rows = ""
    for mo in range(1, 13):
        nm = [m for m in m27 if m["kind"] == "新月" and int(m["jst"][5:7]) == mo]
        fm = [m for m in m27 if m["kind"] == "満月" and int(m["jst"][5:7]) == mo]
        f = lambda L: "／".join(f'{esc(md(m["jst"]))}<br><small>{esc(m["sign"])}</small>' + ('<span class="fh-b27-hs-tag">いちばん大きい満月</span>' if m["jst"] == big else '') + ('<span class="fh-b27-hs-tag">いちばん小さい満月</span>' if m["jst"] == small else '') for m in L) or "—"
        rows += f"<tr><th scope='row'>{mo}月</th><td>{f(nm)}</td><td>{f(fm)}</td></tr>"
    nnew = sum(1 for m in m27 if m["kind"] == "新月")
    a(f'''<section class="fh-b27-sec" id="b27-hs-moon">
  {h2("2027年の新月・満月")}
  <p>2027年の新月は{nnew}回、満月は{len(fulls)}回です。9月は新月が2回あります。月のある星座は、その時刻に月がいる星座です。見た目がいちばん大きい満月は{esc(md(big, False))}、いちばん小さい満月は{esc(md(small, False))}です。</p>
  <div class="fh-b27-hs-scroll"><table class="fh-b27-hs-tbl"><thead><tr><th>月</th><th>新月</th><th>満月</th></tr></thead><tbody>{rows}</tbody></table></div>
</section>''')
    ec = "".join(f'<tr><td>{esc(md(e["jst_max"]))}</td><td>{esc(e["type"])}</td><td>{esc(e["sign"])}</td><td><small>{esc(e["japan"])}</small></td></tr>' for e in H27["eclipses_2027"])
    a(f'''<section class="fh-b27-sec" id="b27-hs-ecl">
  {h2("2027年の日食・月食")}
  <p>2027年の日食は2月7日の金環日食と8月2日の皆既日食の2回で、どちらも日本からは見られません（国立天文台の暦要項）。月食は、地球の薄い影に入るだけの「半影月食」が3回あり、肉眼では月が少し暗くなる程度で、ほとんど気づかないほどです。時刻は食がいちばん大きくなる時刻です。</p>
  <div class="fh-b27-hs-scroll"><table class="fh-b27-hs-tbl"><thead><tr><th>日時</th><th>種類</th><th>星座</th><th>日本から</th></tr></thead><tbody>{ec}</tbody></table></div>
  <p>星占いでは、日食は「新しい流れの始まり」、月食は「ひとつの区切り」と読まれることが多い日です。</p>
</section>''')
    rx = ""
    for n, lst in H27["stations"].items():
        L = [s for s in lst if s["jst"].startswith("2027")]
        for i in range(0, len(L) - 1, 2):
            rx += f'<tr><td>{esc(n)}</td><td>{esc(md(L[i]["jst"], False))}〜{esc(md(L[i + 1]["jst"], False))}</td><td>{esc(L[i]["sign"])}→{esc(L[i + 1]["sign"])}</td></tr>'
    a(f'''<section class="fh-b27-sec" id="b27-hs-rx">
  {h2("2027年の逆行")}
  <p>逆行は、地球から見て星が空を後ろ向きに動いているように見える期間です。星占いでは、その星が表すことを「見直す」時期とされます。2027年は水星が3回、火星が1回逆行し、金星の逆行はありません。</p>
  <table class="fh-b27-hs-tbl"><thead><tr><th>星</th><th>期間</th><th>星座</th></tr></thead><tbody>{rx}</tbody></table>
  <p>水星逆行の前後の注意期間や、12星座別の見直しポイントは<a href="/hoshi/mercury-retrograde/">水星逆行2027のページ</a>でくわしく紹介しています。</p>
</section>''')
    ing = "".join(f'<li><b>{esc(md(x["jst"], False))}</b><span>{esc(x["planet"])}が{esc(x["to"])}へ</span></li>' for x in H27["ingress_2027"])
    sp = H27.get("start", {})
    a(f'''<section class="fh-b27-sec" id="b27-hs-big">
  {h2("2027年の大きな星の動き")}
  <p>動きのゆっくりした星は、1つの星座に長く（木星は約1年、土星は約2年半）とどまり、時代の空気や、その星座の人の大きなテーマを表すとされます。2027年に星座を移るのは次のとおりです。</p>
  <ul class="fh-b27-hs-soon">{ing}</ul>
  <p>土星と海王星は牡羊座、天王星は双子座、冥王星は水瓶座に1年を通してとどまります。12星座それぞれへの影響は、各星座の2027年の運勢（<a href="/star/">星座占い2027</a>から選べます）で読めます。</p>
</section>''')
    srows = ""
    for x in SK:
        if not x.get("sekki"):
            continue
        t = NAOJ_FIX.get(x["sekki"], x["jst"])
        srows += f'<tr><td>{esc(x["sekki"])}<br><small>{esc(x["sekki_yomi"])}</small></td><td>{esc(md(t))}</td></tr>'
    a(f'''<section class="fh-b27-sec" id="b27-hs-sekki">
  {h2("2027年の二十四節気")}
  <p>二十四節気は、太陽の通り道を24に分けた季節の目印です。立春や春分、夏至、冬至などがあり、九星気学や暦の運勢では「節」の日が月の変わり目になります。</p>
  <div class="fh-b27-hs-scroll"><table class="fh-b27-hs-tbl"><thead><tr><th>名前</th><th>日時</th></tr></thead><tbody>{srows}</tbody></table></div>
</section>''')
    a(f'''<section class="fh-b27-sec" id="b27-hs-use">
  {h2("新月・満月の過ごし方")}
  <div class="fh-b27-hs-cards">
    <div><b>新月は「始める日」</b><br>月が見えなくなる新月は、星占いで種まきのタイミングとされます。始めたいことや願いごとを紙に書き出すと、自分が本当に望んでいることがはっきりします。新月の星座が表すテーマに合わせて書くのもおすすめです。</div>
    <div><b>満月は「実りと手放しの日」</b><br>月がいちばん明るい満月は、それまでの流れがひとつ形になるときとされます。できたことを振り返って自分をねぎらい、続けるのがつらいことや使っていない物を手放すのに向いています。</div>
    <div><b>日食・月食の前後は無理をしない</b><br>日食や月食は、物事が大きく切り替わる区切りと読まれます。大事な契約や決断は、できれば食の前後数日を避けて、気持ちが落ち着いてからにすると安心です。</div>
    <div><b>逆行中は「再」のつくことを</b><br>逆行の期間は、新しく始めるより、見直し・再確認・再会・修理など「再」のつくことがうまくいきやすいとされます。予定には少し余裕を持たせておきましょう。</div>
  </div>
</section>''')
    faq = [("新月・満月の日時はどこで決まりますか。", "太陽と月の位置関係で決まり、太陽と月が同じ方向に並んだ瞬間が新月、反対側に来た瞬間が満月です。このページの日時は計算で出し、国立天文台の暦要項と照合した日本時です。"),
           ("新月のお願いごとは、いつまでにすればいいですか。", "星占いでは、新月の時刻から48時間以内がよいと言われることが多いです。時間にこだわりすぎず、新月の日に落ち着いて書ける時間を選んでください。"),
           ("2027年に日本で見られる日食・月食はありますか。", "日食は2回ともに日本からは見られません。月食は半影月食だけで、肉眼ではほとんどわかりません。2027年は、日本で欠けて見える月食はありません。"),
           ("水星逆行はいつですか。", "2027年は2月10日〜3月3日、6月11日〜7月5日、10月7日〜10月28日の3回です。2026年は10月24日〜11月14日が今年最後の逆行です。"),
           ("2026年のこよみは見られますか。", "このページは2027年版に更新しました。2026年の残り（10〜12月）の予定は、ページの最初にのせています。")]
    qa, ld = faq_html(faq)
    a(f'''<section class="fh-b27-sec" id="b27-hs-faq">
  {h2("よくある質問")}
  <div class="fh-b27-hs-qa">{qa}</div>
</section>
<script type="application/ld+json">{ld}</script>
<section class="fh-b27-sec" id="b27-hs-more">
  <div class="fh-b27-links">
    <a href="/hoshi/mercury-retrograde/"><b>水星逆行2027 →</b><small>3回の期間と12星座別の見直しポイント</small></a>
    <a href="/star/"><b>星座占い2027 →</b><small>12星座の運勢ランキングと月ごとの順位</small></a>
    <a href="/366uranai/"><b>366日の誕生日占い →</b><small>誕生日ごとの2027年の運勢</small></a>
    <a href="/kyusei/"><b>九星気学 →</b><small>2027年の吉方位と運勢</small></a>
  </div>
</section>''')
    a(foot(updated))
    a("</div>\n</div>")
    title = "星のこよみ2027｜新月・満月・日食月食・水星逆行・二十四節気の日付一覧"
    desc = "2027年の新月・満月（月の星座つき）、日食・月食、水星逆行と火星逆行、木星の星座移動、二十四節気の日時を一覧にまとめました。2026年10〜12月の残りの予定ものせています。"
    return shell(title, desc, "/hoshi/", "\n".join(H), sample)


def build_mercury(sample, updated):
    H = [CSS]
    a = H.append
    a('<div class="fh-b27" data-fh-page="hoshi">\n<div class="fh-b27-note">')
    a(hero("人生予報 星のこよみ", "水星逆行2027はいつ？<br>3回の期間と過ごし方",
           "2027年の水星逆行は3回。いつからいつまでか、前後の注意期間、逆行中に気をつけたいことと向いていること、12星座それぞれの見直しポイントをまとめました。2026年11月14日までの今年最後の逆行ものせています。"))
    items = [("b27-mr-when", "水星逆行はいつ？（2026年〜2027年）"), ("b27-mr-what", "水星逆行とは"), ("b27-mr-how", "逆行中の過ごし方"),
             ("b27-mr-signs", "12星座別の見直しポイント"), ("b27-mr-other", "金星と火星の逆行"), ("b27-mr-faq", "よくある質問")]
    a(toc(items))
    h2 = mk_h2()
    cards = ""
    for i, s in enumerate(H27["shadows"]):
        a0, b0 = pt(s["pre_start"]), pt(s["post_end"])
        r, d = pt(s["retro"]), pt(s["direct"])
        tot = (b0 - a0).days or 1
        x1, x2 = (r - a0).days / tot * 100, (d - a0).days / tot * 100
        y = s["retro"][:4]
        label = "2026年（今年最後）" if y == "2026" else f"2027年 {sum(1 for t in H27['shadows'][:i + 1] if t['retro'].startswith('2027'))}回目"
        signs = s["from_sign"] if s["from_sign"] == s["to_sign"] else f'{s["from_sign"]}→{s["to_sign"]}'
        cards += (f'<div><b>{label}：{esc(md(s["retro"], False))}〜{esc(md(s["direct"], False))}</b><br>星座：{esc(signs)}<br>'
                  f'<small>前の注意期間：{esc(md(s["pre_start"], False))}〜／あとの注意期間：〜{esc(md(s["post_end"], False))}</small>'
                  f'<div class="fh-b27-hs-bar" aria-hidden="true"><span class="sh" style="left:0;width:{x1:.1f}%">前</span><span class="rx" style="left:{x1:.1f}%;width:{x2 - x1:.1f}%">逆行</span><span class="sh" style="left:{x2:.1f}%;width:{100 - x2:.1f}%">あと</span></div></div>')
    a(f'''<section class="fh-b27-sec" id="b27-mr-when">
  {h2("水星逆行はいつ？（2026年〜2027年）")}
  <p>水星逆行は、ふつう1年に3回、1回あたり3週間ほど起こります。逆行の前後には、水星が逆行で戻る範囲を通る「注意期間（シャドー期間）」もあり、星占いでは逆行と同じように見直しが大切な時期とされます。日付は逆行の始まりと終わり（水星が止まって見える日）です。</p>
  <div class="fh-b27-hs-cards">{cards}</div>
</section>''')
    a(f'''<section class="fh-b27-sec" id="b27-mr-what">
  {h2("水星逆行とは")}
  <p>水星は地球より内側を速く回っているため、地球が水星を追い越していくように見える時期に、空の上で後ろ向きに動いているように見えます。これが水星逆行です。実際に水星が戻っているわけではありません。</p>
  <p>星占いでは、水星は「言葉・連絡・情報・移動・契約」を表す星です。そのため逆行中は、行き違いや予定の遅れ、機械の不調が起きやすく、新しく始めるより、これまでのことを見直すのに向いた時期と読まれます。</p>
</section>''')
    a(f'''<section class="fh-b27-sec" id="b27-mr-how">
  {h2("逆行中の過ごし方")}
  <div class="fh-b27-hs-cards">
    <div><b>気をつけたいこと</b><br>大事な連絡は文字で残し、送る前に宛先と日時をもう一度確認しましょう。大きな契約や高い買い物は、できれば逆行が終わってから。移動は時間に余裕を持ち、スマホやパソコンのバックアップも取っておくと安心です。</div>
    <div><b>向いていること</b><br>やりかけのことの仕上げ、部屋や書類の片づけ、昔の友人への連絡、学び直し、計画の見直しなど「再」のつくことがうまくいきやすい時期です。立ち止まって考えたことが、逆行明けの一歩を確かなものにしてくれます。</div>
  </div>
</section>''')
    r27 = [s for s in H27["shadows"] if s["retro"].startswith("2027")]
    sg = ""
    for i, nm in enumerate(SIGNS):
        lis = ""
        for s in r27:
            k = SIGNS.index(s["from_sign"])
            h = (k - i) % 12 + 1
            k2 = SIGNS.index(s["to_sign"])
            h2b = (k2 - i) % 12 + 1
            more = f'（後半は「{HOUSE[h2b]}」も）' if h2b != h else ""
            lis += f'<li><b>{esc(md(s["retro"], False))}〜：</b>「{HOUSE[h]}」を見直す時期{more}</li>'
        sg += f'<details><summary>{esc(nm)}</summary><ul>{lis}</ul><p><a href="/{SIGN_URL[i]}/">{esc(nm)}の2027年の運勢 →</a></p></details>'
    a(f'''<section class="fh-b27-sec" id="b27-mr-signs">
  {h2("12星座別の見直しポイント")}
  <p>水星が逆行する星座が、あなたの星座から数えて何番目にあたるかで、見直しのテーマが変わります（星占いの「ハウス」の考え方）。あなたの太陽星座を選んでください。</p>
  <div class="fh-b27-hs-signs">{sg}</div>
</section>''')
    v = H27["stations"]["金星"]
    m = H27["stations"]["火星"]
    a(f'''<section class="fh-b27-sec" id="b27-mr-other">
  {h2("金星と火星の逆行")}
  <div class="fh-b27-hs-cards">
    <div><b>金星逆行：{esc(md(v[0]["jst"], False))}〜{esc(md(v[1]["jst"], False))}（{esc(v[0]["sign"])}→{esc(v[1]["sign"])}）</b><br>金星は恋愛・お金・楽しみを表す星。逆行中は昔の恋や人間関係を見直したり、お金の使い方を整えたりするのに向いています。2027年は金星の逆行はありません。</div>
    <div><b>火星逆行：{esc(md(m[0]["jst"], False))}〜{esc(md(m[1]["jst"], False))}（{esc(m[0]["sign"])}→{esc(m[1]["sign"])}）</b><br>火星は行動力・やる気・争いを表す星。約2年に1度の逆行中は、勢いで動くより、やり方を見直して力をためる時期です。けんかや無理な日程は避けましょう。</div>
  </div>
</section>''')
    faq = [("水星逆行は悪いことが起きる時期ですか。", "悪いことが起きると決まっているわけではありません。連絡の行き違いや遅れが起きやすいので、確認を丁寧にするとよい時期、と考えてください。見直しや再会には、むしろ向いている時期です。"),
           ("注意期間（シャドー期間）とは何ですか。", "逆行で水星が戻る範囲を、逆行の前に初めて通り始めてから、逆行の後にもう一度通り終えるまでの期間です。逆行の前の注意期間には見直すべきことが見えはじめ、あとの注意期間には見直したことを形にしていくとされます。"),
           ("逆行中に契約や買い物をしてはいけませんか。", "してはいけないわけではありません。どうしても必要なときは、書類や条件をいつもより丁寧に確認してください。急がない大きな決断は、逆行が終わってからにすると安心です。"),
           ("自分の星座の見直しポイントはどう決まりますか。", "水星が逆行する星座が、あなたの太陽星座から数えて何番目かで決めています。たとえば牡羊座の人にとって、魚座は12番目の「心の整理」の場所です。")]
    qa, ld = faq_html(faq)
    a(f'''<section class="fh-b27-sec" id="b27-mr-faq">
  {h2("よくある質問")}
  <div class="fh-b27-hs-qa">{qa}</div>
</section>
<script type="application/ld+json">{ld}</script>
<section class="fh-b27-sec" id="b27-mr-more">
  <div class="fh-b27-links">
    <a href="/hoshi/"><b>星のこよみ2027 →</b><small>新月・満月・日食月食・二十四節気</small></a>
    <a href="/star/"><b>星座占い2027 →</b><small>12星座の運勢ランキング</small></a>
    <a href="/tarot/"><b>タロット占い →</b><small>見直したいことを相談してみる</small></a>
  </div>
</section>''')
    a(foot(updated))
    a("</div>\n</div>")
    title = "水星逆行2027はいつ？3回の期間と注意期間・過ごし方・12星座別の見直しポイント"
    desc = "2027年の水星逆行は2月10日〜3月3日、6月11日〜7月5日、10月7日〜10月28日の3回。前後の注意期間、逆行中の過ごし方、12星座別の見直しポイント、2026年11月14日までの逆行と金星・火星の逆行もまとめました。"
    return shell(title, desc, "/hoshi/mercury-retrograde/", "\n".join(H), sample)


def main():
    updated = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    for fn, nm in ((build_hoshi, "hoshi"), (build_mercury, "mercury")):
        for sample, path in ((False, os.path.join(OUT, f"{nm}.html")), (True, os.path.join(OUT, "sample", f"{nm}.html"))):
            out = fn(sample, updated)
            assert "！" not in out
            open(path, "w", encoding="utf-8").write(out)
            print("→", os.path.relpath(path, WORK))


if __name__ == "__main__":
    main()
