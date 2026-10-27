"""マヤ暦（ドリームスペル）2027年の運勢（/unsei-2027/maya/）。20の太陽の紋章別。
数値は calc_maya_2027.py → data/maya_2027.json（年のKIN・紋章どうしの関係・2027年の紋章の日）。文章は maya2027_texts.py（検査 check_maya2027.py）。
生年月日→KIN は共通JS（fh-b27.js の FHB27Calc.kin）＝/maya/・まるごと診断と同じ結果。見た目は 2027年の運勢シリーズ（/kyusei/ の CSS）。
"""
import datetime as dt, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_hub import OUT, WORK, shell  # noqa: E402
from build_shukuyo import esc  # noqa: E402
from build_kyusei import CSS as KY_CSS  # noqa: E402
from build_nenun2027 import CSS as NY_CSS  # noqa: E402
import maya2027_texts as MT  # noqa: E402

URL = "/unsei-2027/maya/"
DATA = os.path.join(WORK, "data", "maya_2027.json")
SCRIPTS = ("fh-b27-setsuiri.js", "fh-b27-kyureki.js", "fh-b27.js")
COL = {"赤": "#C8463C", "白": "#E9E4D8", "青": "#3E6FB0", "黄": "#E2B33C"}
REL = {"同じ紋章": "年と同じ紋章", "類似": "類似（支え合う）", "反対": "反対（鍛え合う）", "神秘": "神秘（隠れた力）", "同じ色": "同じ色（ガイドの仲間）", None: "色の流れで読む"}

FAQ = [
    ("マヤ暦の2027年はいつから始まりますか。", "ドリームスペルでは、1年は7月26日に始まります。2027年7月26日から2028年7月25日までが「白い魔法使い・銀河の音9」の年です。2027年1月1日〜7月25日は、その前の「赤い月・銀河の音8」の年の後半にあたります。"),
    ("自分の紋章はどうやって調べますか。", "このページの上で生年月日を選ぶと、KIN（1〜260の番号）と太陽の紋章が出ます。計算は、このサイトのマヤ暦占いのページと同じです。"),
    ("このマヤ暦は古代マヤの暦と同じですか。", "同じではありません。ホゼ・アグエイアスらが1987年以降に発表した「ドリームスペル」にもとづく現代の占いです。古代マヤの遺跡に残る暦とは数え方が違います。"),
    ("紋章の日とは何ですか。", "自分の太陽の紋章と同じ紋章がめぐってくる日のことで、20日に1回あります。このページでは、2027年の1年間（1月1日〜12月31日）にめぐってくる日を紋章ごとに並べています。"),
]


def build(sample, updated):
    D = json.load(open(DATA, encoding="utf-8"))
    Y, PV, SE = D["year"], D["prev"], D["seals"]
    assert Y["kin"] == 74 and PV["kin"] == 229
    H = []
    a = H.append
    a(KY_CSS)
    a(NY_CSS)
    a("""<style>.fh-b27-mx-big{display:flex;flex-direction:column;align-items:center;justify-content:center;width:120px;height:120px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#FFFFFF,#E2DCCD);color:#2A2418;font:800 20px 'Shippori Mincho',serif;box-shadow:0 0 0 3px rgba(212,175,90,.6),0 10px 30px rgba(0,0,0,.45);margin:10px;text-align:center;line-height:1.3}
.fh-b27-mx-big small{font:700 12px 'Zen Kaku Gothic New',sans-serif;color:#5A4E3A}
.fh-b27-mx-calc{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:8px 0}
.fh-b27-mx-calc select{min-height:44px;border-radius:2px;border:1px solid var(--line);background:var(--deep);color:var(--ink);font:inherit;padding:0 8px}
.fh-b27-mx-res{background:var(--cream);color:var(--cream-ink);border-radius:4px;padding:12px 14px;margin-top:8px;line-height:1.8}
.fh-b27 .fh-b27-mx-res b{color:#9A3328;font-size:18px}.fh-b27 .fh-b27-mx-res a{color:#9A3328;font-weight:700}
.fh-b27-mx-half{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin:8px 0}
.fh-b27-mx-half div{border:1px solid rgba(212,175,90,.3);border-radius:4px;padding:10px 12px;font-size:14px;line-height:1.85;background:rgba(20,24,21,.6)}
.fh-b27 .fh-b27-mx-half div b{display:block;color:var(--gold);font-size:14px}
.fh-b27-mx-days{display:flex;flex-wrap:wrap;gap:4px;margin:6px 0}
.fh-b27-mx-days span{border-radius:999px;background:#EFE4C8;color:#4A3B1C;padding:1px 9px;font-size:12.5px;font-weight:700}
.fh-b27-mx-rel{display:inline-block;border-radius:2px;padding:1px 8px;font-size:12.5px;font-weight:700;background:#EFE4C8;color:#4A3B1C;margin-left:6px}
@media (max-width:640px){.fh-b27-mx-big{width:96px;height:96px;font-size:16px}.fh-b27-mx-half{grid-template-columns:1fr}}</style>""")
    a('<div class="fh-b27" data-fh-page="kyusei">\n<div class="fh-b27-note">')
    a(f'''<header class="fh-b27-hero">
  <div class="fh-b27-mx-big" aria-hidden="true"><small>7月26日から</small>{Y["seal"]}<small>KIN{Y["kin"]}・音{Y["tone_no"]}</small></div>
  <div class="fh-b27-hero-body">
    <span class="fh-b27-tape">2027年の運勢</span>
    <h1 class="fh-b27-title">マヤ暦でみる<br>2027年の運勢 20の紋章別</h1>
    <p class="fh-b27-lead">マヤ暦（ドリームスペル）の1年は7月26日に始まります。2027年は、7月25日までが「{PV["seal"]}・音{PV["tone_no"]}」の年、7月26日からが「{Y["seal"]}・音{Y["tone_no"]}」の年です。20の太陽の紋章ごとに、年の紋章との関係から総合運・恋愛・仕事・お金・健康と、2027年の紋章の日をまとめました。</p>
  </div>
</header>''')
    items = [("mx-calc", "あなたの紋章を調べる"), ("mx-year", "2027年のマヤ暦"), ("mx-list", "20の紋章別 2027年の運勢"), ("mx-faq", "よくある質問")]
    a('<nav class="fh-b27-toc" aria-label="目次"><strong>このページの内容</strong><ol>' + "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in items) + "</ol></nav>")
    n = [1]

    def h2(t):
        s = f'<h2><span class="fh-b27-n">{n[0]:02d}</span>{t}</h2>'
        n[0] += 1
        return s

    yo = "".join(f'<option value="{y}"{" selected" if y == 1990 else ""}>{y}年</option>' for y in range(1930, 2027))
    mo = "".join(f'<option value="{m}">{m}月</option>' for m in range(1, 13))
    dy = "".join(f'<option value="{d}">{d}日</option>' for d in range(1, 32))
    jump = "".join(f'<a href="#mx-{s}" style="--c:{COL[SE[str(s)]["color"]]}">{SE[str(s)]["name"]}<small>{esc(MT.TEXTS[s]["title"])}</small></a>' for s in range(1, 21))
    a(f'''<section class="fh-b27-sec" id="mx-calc">
  {h2("あなたの紋章を調べる")}
  <p>生年月日を選ぶと、KINと太陽の紋章を計算して、その紋章の2027年の運勢へ案内します。</p>
  <div class="fh-b27-mx-calc"><select id="mx-y" aria-label="生まれ年">{yo}</select><select id="mx-m" aria-label="生まれ月">{mo}</select><select id="mx-d" aria-label="生まれ日">{dy}</select><button type="button" class="fh-b27-ky-btn" id="mx-go">紋章を調べる</button></div>
  <div class="fh-b27-mx-res" id="mx-res" hidden></div>
  <p style="margin-top:12px"><b>紋章から読む</b></p>
  <div class="fh-b27-ny-jump">{jump}</div>
</section>''')
    rel_rows = "".join(f'<tr><th scope="row">{SE[str(s)]["name"]}</th><td>{REL[SE[str(s)]["rel27"]]}</td><td>{REL[SE[str(s)]["rel26"]] if SE[str(s)]["rel26"] else "—"}</td></tr>' for s in range(1, 21) if SE[str(s)]["rel27"] or SE[str(s)]["rel26"])
    a(f'''<section class="fh-b27-sec" id="mx-year">
  {h2("2027年のマヤ暦")}
  <p>{esc(MT.INTRO["year"])}</p>
  <h3>年の紋章との関係</h3>
  <p>{esc(MT.INTRO["rels"])}</p>
  <div class="fh-b27-ky-wrap"><table class="fh-b27-ky-t fh-b27-ny-mb" style="min-width:420px"><thead><tr><th>紋章</th><th>{Y["seal"]}の年（7/26〜）</th><th>{PV["seal"]}の年（〜7/25）</th></tr></thead><tbody>{rel_rows}</tbody></table></div>
  <p><small>表にない紋章は、年の紋章と特別な関係がなく、紋章の色の流れで読みます。</small></p>
</section>''')
    a(f'<section class="fh-b27-sec" id="mx-list">\n  {h2("20の紋章別 2027年の運勢")}')
    for s in range(1, 21):
        T, e = MT.TEXTS[s], SE[str(s)]
        days = "".join(f'<span>{int(d[5:7])}/{int(d[8:])}</span>' for d in e["days2027"])
        act = "".join(f"<li>{esc(x)}</li>" for x in T["action"])
        a(f'''<article class="fh-b27-ny-star" id="mx-{s}" style="--c:{COL[e["color"]]}">
  <h3>{e["name"]}<small>紋章{s}・{e["color"]}の紋章</small></h3>
  <span class="fh-b27-ny-theme">2027年は「{esc(T["title"])}」</span><span class="fh-b27-mx-rel">{REL[e["rel27"]]}</span>
  <p>{esc(T["sougou"])}</p>
  <div class="fh-b27-mx-half"><div><b>1月〜7月25日（{PV["seal"]}の年）</b>{esc(T["first"])}</div><div><b>7月26日から（{Y["seal"]}の年）</b>{esc(T["second"])}</div></div>
  <div class="fh-b27-ny-4">
    <div><b>恋愛運</b><p>{esc(T["love"])}</p></div>
    <div><b>仕事運</b><p>{esc(T["work"])}</p></div>
    <div><b>金運</b><p>{esc(T["money"])}</p></div>
    <div><b>健康運</b><p>{esc(T["health"])}</p></div>
  </div>
  <p style="margin:8px 0 0"><b>2027年の紋章の日（{len(e["days2027"])}日）</b></p><div class="fh-b27-mx-days">{days}</div>
  <p style="font-size:14px">{esc(T["seal_day"])}</p>
  <p style="margin-top:8px"><b>2027年の開運アクション</b></p><ul class="fh-b27-ny-act">{act}</ul>
</article>''')
        if s in (5, 10, 15):
            a(f"<!--Ads{s // 5}-->")
    a("</section>")
    qa = "".join(f'<details{" open" if i == 0 else ""}><summary>Q. {q}</summary><p>A. {x}</p></details>' for i, (q, x) in enumerate(FAQ))
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in FAQ]}
    a(f'''<section class="fh-b27-sec" id="mx-faq">
  {h2("よくある質問")}
  <div class="fh-b27-ky-qa">{qa}</div>
</section>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<section class="fh-b27-sec">
  <div class="fh-b27-links">
    <a href="/maya/"><b>マヤ暦占い →</b><small>KIN・太陽の紋章・銀河の音と相性</small></a>
    <a href="/unsei-2027/"><b>2027年の運勢まとめ →</b><small>九星・干支・数秘術・マヤ暦・星座・誕生日から</small></a>
    <a href="/kyusei/unsei-2027/"><b>2027年の運勢（九星気学）→</b><small>本命星別の総合運と吉方位</small></a>
    <a href="/366uranai/"><b>366日の誕生日占い →</b><small>誕生日ごとの2027年の運勢</small></a>
  </div>
</section>''')
    up = dt.date.fromisoformat(updated)
    a(f'<p class="fh-b27-foot">このページのマヤ暦は、ドリームスペル（13の月の暦）にもとづく現代の占いで、古代マヤの暦とは別のものです。KIN・年の紋章・紋章の日は、2月29日を数えない決まりでこのサイトが計算しています。文章はこのサイトで書いたもので、占いは楽しみと気づきのためにお読みください。<br>'
      f'最終更新日：{up.year}年{up.month}月{up.day}日／<a href="/about/">この記事の作成方針について</a></p>')
    a("</div>\n</div>")
    names = json.dumps({s: SE[str(s)]["name"] for s in range(1, 21)}, ensure_ascii=False)
    a("<script>document.addEventListener('DOMContentLoaded',function(){var C=window.FHB27Calc,N=" + names + ";var b=document.getElementById('mx-go');if(!b)return;"
      "b.addEventListener('click',function(){var y=+document.getElementById('mx-y').value,m=+document.getElementById('mx-m').value,d=+document.getElementById('mx-d').value,r=document.getElementById('mx-res');r.hidden=false;"
      "if(new Date(y,m-1,d).getMonth()!==m-1&&!(m===2&&d===29)){r.innerHTML='その日付はありません。選び直してください。';return;}"
      "if(!C||!C.kin){r.innerHTML='計算の準備ができませんでした。ページを読み込み直してください。';return;}"
      "var k=C.kin(y,m,d);r.innerHTML=y+'年'+m+'月'+d+'日生まれは <b>KIN'+k.kin+'・'+N[k.sealNo]+'</b>（銀河の音'+k.tone+'）です。<br><a href=\"#mx-'+k.sealNo+'\">'+N[k.sealNo]+'の2027年の運勢を読む →</a>';});});</script>")
    title = "マヤ暦 2027年の運勢｜20の太陽の紋章別の総合運・恋愛・仕事・金運【白い魔法使いの年・紋章の日】"
    desc = "マヤ暦（ドリームスペル）で見る2027年の運勢。7月26日から始まる白い魔法使い・銀河の音9の年と、20の太陽の紋章との関係から、総合運・恋愛・仕事・金運・健康運と2027年の紋章の日を紹介。生年月日から紋章を調べる計算つき。"
    out = shell(title, desc, URL, "\n".join(H), sample, SCRIPTS)
    assert "！" not in out
    return out, title, desc


def main():
    updated = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    for sample, path in ((False, os.path.join(OUT, "unsei-2027-maya.html")), (True, os.path.join(OUT, "sample", "unsei-2027-maya.html"))):
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(build(sample, updated)[0])
        print("→", os.path.relpath(path, WORK))


if __name__ == "__main__":
    main()
