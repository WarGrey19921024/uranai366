"""2027年の運勢｜九星気学（本命星9タイプ別）のページ（/kyusei/unsei-2027/。/kyusei/ の子ページ）。
数値は calc_nenun_2027.py → data/kyusei_nenun_2027.json（年盤・月盤・凶方位・吉方位・早見表）。
文章は nenun2027_texts.py（このサイトで書いたもの。/kyusei/ の文章とは重ならないように検査済み）。
見た目は /kyusei/ と同じ（data-fh-page="kyusei" の CSS をそのまま使う）。
"""
import datetime as dt, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_hub import OUT, WORK, shell  # noqa: E402
from build_shukuyo import esc  # noqa: E402
from build_kyusei import CSS as KY_CSS, STARS, COLOR  # noqa: E402
import nenun2027_texts as NT  # noqa: E402

URL = "/kyusei/unsei-2027/"
DATA = os.path.join(WORK, "data", "kyusei_nenun_2027.json")
YOMI = ["いっぱくすいせい", "じこくどせい", "さんぺきもくせい", "しろくもくせい", "ごおうどせい", "ろっぱくきんせい", "しちせききんせい", "はっぱくどせい", "きゅうしかせい"]
MARK = {"中央": "節目", "暗剣殺": "暗剣殺", "月破": "月破", "歳破": "歳破"}

CSS = """<style id="fh-b27-ny-css">
.fh-b27-ny-jump{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px}
.fh-b27 .fh-b27-ny-jump a{display:block;border:1px solid rgba(212,175,90,.35);border-left:6px solid var(--c);border-radius:2px;background:rgba(20,24,21,.6);padding:8px 10px;color:var(--ink);text-decoration:none;font-family:'Shippori Mincho',serif;font-weight:800}
.fh-b27 .fh-b27-ny-jump a small{display:block;font:400 12px 'Zen Kaku Gothic New',sans-serif;color:var(--mute)}
.fh-b27-ny-star{border:1px solid rgba(212,175,90,.3);border-top:6px solid var(--c);border-radius:4px;background:rgba(20,24,21,.55);padding:14px 16px;margin:18px 0}
.fh-b27 .fh-b27-ny-star h3{margin:0 0 4px;border:0;font:800 23px 'Shippori Mincho',serif;color:var(--ink)}
.fh-b27-ny-star h3 small{font:400 13px 'Zen Kaku Gothic New',sans-serif;color:var(--mute);margin-left:8px}
.fh-b27-ny-theme{display:inline-block;background:var(--ver);color:#FFF4E8;border-radius:2px;padding:2px 12px;font-family:'Shippori Mincho',serif;font-weight:800;margin:2px 0 8px}
.fh-b27-ny-star p{font-size:15px;line-height:1.95}
.fh-b27-ny-4{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin:10px 0}
.fh-b27-ny-4 div{background:var(--cream);color:var(--cream-ink);border-radius:4px;padding:10px 12px;font-size:14px;line-height:1.85}
.fh-b27 .fh-b27-ny-4 div b{display:block;color:#9A3328;font-size:15px;margin-bottom:2px}
.fh-b27 .fh-b27-ny-4 div p{color:var(--cream-ink);font-size:14px;margin:0}
.fh-b27-ny-chips{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:6px 0}
.fh-b27-ny-chips b{font-size:13.5px;color:var(--gold);margin-right:4px}
.fh-b27-ny-chips span{border-radius:999px;background:#DCEBD9;color:#22462A;padding:2px 12px;font-size:13.5px;font-weight:700}
.fh-b27-ny-chips span.c{background:#F7DCD6;color:#6E2318}
.fh-b27-ny-gm{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin:8px 0}
.fh-b27-ny-gm ul{margin:0;padding:10px 12px 10px 1.6em;border-radius:4px;font-size:13.5px;line-height:1.8}
.fh-b27 .fh-b27-ny-gm ul.g{background:#E6F0E2;color:#1E3B24}.fh-b27 .fh-b27-ny-gm ul.c{background:#F6E4DF;color:#4E1F17}
.fh-b27 .fh-b27-ny-gm ul li{color:inherit;margin:2px 0}
.fh-b27 .fh-b27-ny-gm ul strong{display:block;margin-left:-1em;font-size:14px;color:inherit}
.fh-b27 .fh-b27-ny-gm ul.g strong{color:#1E5A2C}.fh-b27 .fh-b27-ny-gm ul.c strong{color:#8A2A1C}
.fh-b27-ny-mt{min-width:560px}
.fh-b27-ny-mt td.m{white-space:nowrap;font-weight:700}
.fh-b27-ny-mt td.p{white-space:nowrap}
.fh-b27-ny-mt em{font-style:normal;display:inline-block;margin-left:4px;border-radius:2px;padding:0 6px;font-size:11.5px;background:#F7DCD6;color:#6E2318}
.fh-b27-ny-mt em.s{background:#EFE4C8;color:#4A3B1C}
.fh-b27-ny-mt small{color:var(--mute)}
.fh-b27-ny-act{margin:6px 0 0;padding-left:1.2em;font-size:14px}
.fh-b27-ny-hy{min-width:520px}.fh-b27-ny-hy td{font-size:13px;line-height:1.7}
.fh-b27-ny-hy th[scope=row] i{display:inline-block;width:10px;height:10px;border-radius:2px;background:var(--c);margin-right:6px;box-shadow:inset 0 0 0 1px rgba(0,0,0,.3)}
.fh-b27-ny-mb{min-width:560px}.fh-b27-ny-mb small{color:var(--mute)}
@media (max-width:640px){.fh-b27-ny-mt{min-width:0}.fh-b27-ny-mt thead{display:none}.fh-b27-ny-mt tr{display:grid;grid-template-columns:auto 1fr;gap:2px 12px;padding:8px 0;border-bottom:1px solid rgba(212,175,90,.18)}
.fh-b27 .fh-b27-ny-mt td{border:0;padding:1px 2px}.fh-b27-ny-mt td:nth-child(3){grid-column:1/-1}.fh-b27-ny-mt td:nth-child(4){grid-column:1/-1;color:var(--sub);font-size:13px}.fh-b27-ny-mt td:nth-child(4)::before{content:"月の吉方位：";color:var(--gold)}
.fh-b27-ny-mt td.m br{display:none}.fh-b27-ny-mt td.m small{margin-left:6px}}
@media (max-width:640px){.fh-b27-ny-jump{grid-template-columns:repeat(2,minmax(0,1fr))}.fh-b27-ny-4,.fh-b27-ny-gm{grid-template-columns:1fr}}
</style>"""

FAQ = [
    ("2027年の運勢は、いつからいつまでのことですか。", "九星気学では年の切り替わりが立春なので、このページの「2027年」は2027年2月4日の立春から、2028年2月4日の立春の前までです。月も節入り（毎月4〜8日ごろ）で切り替わるため、表の月の欄には始まりの日を入れています。"),
    ("1月生まれですが、どの星を読めばいいですか。", "1月1日から立春の前日までに生まれた人は、前の年の星になります。早見表の年は「その年の立春から翌年の立春の前日まで」です。迷ったら九星気学のページで生年月日を選ぶと、本命星をその場で計算できます。"),
    ("暗剣殺や月破の月は、何もしないほうがいいですか。", "何もしないほうがいいという意味ではありません。思いがけない出来事や、約束ごとの行き違いが起こりやすいと読む月なので、確認を一つ増やす・大きな決断は前後の月にずらすなど、少し慎重に過ごす目安にしてください。"),
    ("吉方位はどう使えばいいですか。", "旅行や散歩、引っ越しの方角を選ぶときの目安です。年の吉方位は1年を通しての方角、月の吉方位はその月に動くときの方角です。月の吉方位は、年盤の凶方位（北・南・北東）も外して計算しています。"),
    ("家族で星が違うときは、どう読めばいいですか。", "それぞれの星の欄を読み比べると、同じ月でも誰が動きやすく、誰が休みたい時期なのかがわかります。予定を立てるときに、無理をしやすい人の月を家族で気にかけるといった使い方がおすすめです。"),
]


def mlabel(m):
    s = dt.datetime.strptime(m["start"], "%Y-%m-%d %H:%M")
    e = dt.datetime.strptime(m["end"], "%Y-%m-%d %H:%M") - dt.timedelta(days=1)
    return f"{s.month}月", f"{s.month}/{s.day}〜{e.month}/{e.day}"


def build(sample, updated):
    D = json.load(open(DATA, encoding="utf-8"))
    Y, MS = D["year"], D["months"]
    assert len(MS) == 12 and Y["kanshi"] == "丁未" and Y["center"] == 9
    H = []
    a = H.append
    a(KY_CSS)
    a(CSS)
    a('<div class="fh-b27" data-fh-page="kyusei">\n<div class="fh-b27-note">')
    order = ["南東", "南", "南西", "東", "中央", "西", "北東", "北", "北西"]
    inv = {Y["stars"][str(s)]["palace"]: s for s in range(1, 10)}
    ban = "".join(f'<span style="background:{COLOR[inv[o] - 1]};{"color:#F1ECE2;" if inv[o] == 2 else ""}">{inv[o]}</span>' for o in order)
    a(f'''<header class="fh-b27-hero">
  <div class="fh-b27-ky-ban" aria-hidden="true">{ban}</div>
  <div class="fh-b27-hero-body">
    <span class="fh-b27-tape">2027年の運勢</span>
    <h1 class="fh-b27-title">九星気学で見る<br>2027年の運勢 9つの本命星別</h1>
    <p class="fh-b27-lead">2027年は九紫火星が年盤の中央に入る、丁未（ひのとひつじ）の年です。一白水星から九紫火星まで、本命星ごとに総合運・恋愛・仕事・お金・健康と、月ごとの流れ、吉方位をまとめました。星の位置と方位は、立春と節入りの日時からこのサイトで計算しています。</p>
  </div>
</header>''')
    items = [("ny-hayami", "本命星の早見表"), ("ny-year", "2027年はどんな年"), ("ny-stars", "本命星別 2027年の運勢"), ("ny-months", "2027年の月盤と凶方位"), ("ny-faq", "よくある質問")]
    a('<nav class="fh-b27-toc" aria-label="目次"><strong>このページの内容</strong><ol>' + "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in items) + "</ol></nav>")
    n = [1]

    def h2(t):
        s = f'<h2><span class="fh-b27-n">{n[0]:02d}</span>{t}</h2>'
        n[0] += 1
        return s

    # 早見表
    by = {s: [] for s in range(1, 10)}
    for y, s in D["hayami"].items():
        by[s].append(int(y))
    rows = "".join(f'<tr style="--c:{COLOR[s - 1]}"><th scope="row"><i></i><a href="#ny-s{s}">{STARS[s - 1]}</a></th><td>{"・".join(str(y) for y in sorted(by[s], reverse=True))}年</td></tr>' for s in range(1, 10))
    jump = "".join(f'<a href="#ny-s{s}" style="--c:{COLOR[s - 1]}">{STARS[s - 1]}<small>{esc(NT.TEXTS2027[STARS[s - 1]]["title"])}</small></a>' for s in range(1, 10))
    a(f'''<section class="fh-b27-sec" id="ny-hayami">
  {h2("本命星の早見表")}
  <p>生まれた年から、自分の本命星を探してください。年の切り替わりは立春（2月4日ごろ）なので、<b>1月1日から立春の前日までに生まれた人は、ひとつ前の年の星</b>を読みます。生年月日から計算したいときは<a href="/kyusei/">九星気学のページ</a>で調べられます。</p>
  <div class="fh-b27-ky-wrap"><table class="fh-b27-ky-t fh-b27-ny-hy"><thead><tr><th>本命星</th><th>生まれ年（1930〜2026年）</th></tr></thead><tbody>{rows}</tbody></table></div>
  <p style="margin-top:12px"><b>本命星から読みたい星へ</b></p>
  <div class="fh-b27-ny-jump">{jump}</div>
</section>''')
    # 2027年はどんな年
    E = NT.ETO2027
    a(f'''<section class="fh-b27-sec" id="ny-year">
  {h2("2027年はどんな年")}
  <h3>九紫火星が中央に入る「丁未」の年</h3>
  <p>{esc(E["about"])}</p>
  <p>{esc(E["with9"])}</p>
  <h3>2027年の年盤と凶方位</h3>
  <p>年盤は上が南です。2027年の凶方位は、<b>五黄殺が{Y["gohou"]}、暗剣殺が{Y["anken"]}、歳破が{Y["ha"]}</b>です（{int(Y["start"][5:7])}月{int(Y["start"][8:10])}日の立春から、翌年の立春の前まで）。</p>
  <div class="fh-b27-ky-grid9">{"".join(f'<div class="{"bad" if o in (Y["gohou"], Y["anken"], Y["ha"]) else ""}"><b>{STARS[inv[o] - 1]}</b>{o}{"（五黄殺）" if o == Y["gohou"] else "（暗剣殺）" if o == Y["anken"] else "（歳破）" if o == Y["ha"] else ""}</div>' for o in order)}</div>
</section>''')
    # 本命星別
    a(f'<section class="fh-b27-sec" id="ny-stars">\n  {h2("本命星別 2027年の運勢")}')
    for s in range(1, 10):
        nm = STARS[s - 1]
        T = NT.TEXTS2027[nm]
        ys = Y["stars"][str(s)]
        luck = "".join(f"<span>{d}</span>" for d in ys["lucky"]) or '<span class="c">年盤では吉方位なし</span>'
        mrows = []
        for i, m in enumerate(MS):
            st = m["stars"][str(s)]
            mo, rng = mlabel(m)
            marks = "".join(f'<em class="{"s" if k == "中央" else ""}">{MARK[k]}</em>' for k in st["marks"])
            lk = "・".join(st["lucky"]) or "なし"
            mrows.append(f'<tr><td class="m">{mo}<br><small>{rng}</small></td><td class="p">{st["palace"]}{marks}</td><td>{esc(T["months"][i])}</td><td class="p">{lk}</td></tr>')
        gm = "".join(f"<li>{esc(k)}：{esc(v)}</li>" for k, v in T["good_months"])
        cm = "".join(f"<li>{esc(k)}：{esc(v)}</li>" for k, v in T["care_months"])
        act = "".join(f"<li>{esc(x)}</li>" for x in T["action"])
        ym = "・".join(MARK[k] for k in ys["marks"])
        a(f'''<article class="fh-b27-ny-star" id="ny-s{s}" style="--c:{COLOR[s - 1]}">
  <h3>{nm}<small>{YOMI[s - 1]}</small></h3>
  <span class="fh-b27-ny-theme">2027年は「{esc(T["title"])}」</span>
  <p>{esc(T["sougou"])}</p>
  <div class="fh-b27-ny-4">
    <div><b>恋愛運</b><p>{esc(T["love"])}</p></div>
    <div><b>仕事運</b><p>{esc(T["work"])}</p></div>
    <div><b>金運</b><p>{esc(T["money"])}</p></div>
    <div><b>健康運</b><p>{esc(T["health"])}</p></div>
  </div>
  <div class="fh-b27-ny-chips"><b>年盤の位置</b><span class="{"c" if ys["marks"] else ""}">{ys["palace"]}{"（" + ym + "）" if ym else ""}</span><b>2027年の吉方位</b>{luck}</div>
  <div class="fh-b27-ny-gm"><ul class="g"><strong>運気に乗りやすい月</strong>{gm}</ul><ul class="c"><strong>慎重に過ごしたい月</strong>{cm}</ul></div>
  <div class="fh-b27-ky-wrap"><table class="fh-b27-ky-t fh-b27-ny-mt"><caption>{nm}の月ごとの運勢（位置＝その月の月盤で星が入る方位。吉方位はその月に動くときの方角）</caption>
  <thead><tr><th>月</th><th>位置</th><th>その月のヒント</th><th>月の吉方位</th></tr></thead><tbody>{"".join(mrows)}</tbody></table></div>
  <p style="margin-top:8px"><b>2027年の開運アクション</b></p><ul class="fh-b27-ny-act">{act}</ul>
</article>''')
        if s in (3, 6):
            a(f"<!--Ads{s // 3}-->")
    a("</section>")
    # 月盤
    mr = []
    for m in MS:
        mo, rng = mlabel(m)
        mr.append(f'<tr><th scope="row">{mo}<br><small>{rng}</small></th><td>{m["setsu"]}</td><td>{m["kanshi"]}</td><td>{STARS[m["center"] - 1]}</td><td>{m["gohou"] or "なし"}</td><td>{m["anken"] or "なし"}</td><td>{m["ha"]}</td></tr>')
    a(f'''<section class="fh-b27-sec" id="ny-months">
  {h2("2027年の月盤と凶方位")}
  <p>月は節入りの日時で切り替わります。五黄土星が中央に入る月（2月と11月）は、五黄殺・暗剣殺の方位がありません。</p>
  <div class="fh-b27-ky-wrap"><table class="fh-b27-ky-t fh-b27-ny-mb"><thead><tr><th>月</th><th>節</th><th>月の干支</th><th>月盤の中央</th><th>五黄殺</th><th>暗剣殺</th><th>月破</th></tr></thead><tbody>{"".join(mr)}</tbody></table></div>
  <p>年の切り替わりと同じく、月の切り替わりも日付の途中になることがあります。旅行や引っ越しの日取りは、<a href="/kaiun/kichijitsu-2027/">2027年の吉日カレンダー</a>（開運ライフ）とあわせて見ると選びやすくなります。</p>
</section>''')
    qa = "".join(f'<details{" open" if i == 0 else ""}><summary>Q. {q}</summary><p>A. {x}</p></details>' for i, (q, x) in enumerate(FAQ))
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in FAQ]}
    a(f'''<section class="fh-b27-sec" id="ny-faq">
  {h2("よくある質問")}
  <div class="fh-b27-ky-qa">{qa}</div>
</section>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<section class="fh-b27-sec">
  <div class="fh-b27-links">
    <a href="/kyusei/"><b>九星気学 →</b><small>生年月日から本命星を計算・相性・月ごとの吉方位</small></a>
    <a href="/366uranai/"><b>366日の誕生日占い →</b><small>誕生日ごとの2027年の運勢</small></a>
    <a href="/seinengappi/"><b>生年月日まるごと診断 →</b><small>九星・宿曜・マヤ暦などを1枚に</small></a>
    <a href="/kaiun/kichijitsu-2027/"><b>2027年の吉日カレンダー →</b><small>開運ライフ｜天赦日・一粒万倍日</small></a>
  </div>
</section>''')
    up = dt.date.fromisoformat(updated)
    a(f'<p class="fh-b27-foot">年盤・月盤・凶方位・吉方位は、立春と節入りの日時（日本時間）をもとにこのサイトで計算しています。吉方位は、本命星から見て相性のよい星がいる方位から、五黄殺・暗剣殺・破・本命殺・本命的殺を除いたものです。文章はこのサイトで書いたもので、占いは楽しみと気づきのためにお読みください。<br>'
      f'最終更新日：{up.year}年{up.month}月{up.day}日／<a href="/about/">この記事の作成方針について</a></p>')
    a("</div>\n</div>")
    title = "2027年の運勢｜九星気学 9つの本命星別（一白水星〜九紫火星）の総合運・恋愛・仕事・金運と吉方位"
    desc = ("九星気学で見る2027年（丁未・九紫火星中宮）の運勢を、一白水星から九紫火星まで本命星別に紹介。総合運・恋愛・仕事・金運・健康運、月ごとの運勢と吉方位、凶方位、本命星の早見表つき。")
    out = shell(title, desc, URL, "\n".join(H), sample, ())
    assert "！" not in out
    return out, title, desc


def main():
    updated = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    for sample, path in ((False, os.path.join(OUT, "kyusei-unsei-2027.html")), (True, os.path.join(OUT, "sample", "kyusei-unsei-2027.html"))):
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(build(sample, updated)[0])
        print("→", os.path.relpath(path, WORK))


if __name__ == "__main__":
    main()
