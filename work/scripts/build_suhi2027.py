"""数秘術 2027年の運勢（/unsei-2027/suhi/）。2027年の数（パーソナルイヤー）1〜9別。
数値は calc_suhi_2027.py → data/suhi_2027.json（PY・月の数・366日の早見表）。文章は suhi2027_texts.py（検査 check_suhi2027.py）。
見た目は /kyusei/ と同じ CSS を使う（2027年の運勢シリーズでそろえる）。
"""
import datetime as dt, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_hub import OUT, WORK, shell  # noqa: E402
from build_shukuyo import esc  # noqa: E402
from build_kyusei import CSS as KY_CSS  # noqa: E402
from build_nenun2027 import CSS as NY_CSS  # noqa: E402
import suhi2027_texts as ST  # noqa: E402

URL = "/unsei-2027/suhi/"
DATA = os.path.join(WORK, "data", "suhi_2027.json")
COL = ["", "#C2453A", "#E9E6DC", "#D9B23C", "#5E9B5E", "#3D8B8B", "#D98BA0", "#7A4D9C", "#B88A3E", "#3D6E9B"]
PMW = {1: "始める", 2: "協力", 3: "表現", 4: "整える", 5: "変化", 6: "身近な人", 7: "見直す", 8: "実り", 9: "区切り"}

FAQ = [
    ("2027年の数はいつからいつまでですか。", "このサイトでは1月1日から12月31日までを2027年として計算しています。誕生日で切り替える読み方もありますが、ここではカレンダーの年で切り替えます。"),
    ("2027年は11の年なのに、なぜ1〜9で読むのですか。", "2027の数字を足すと11になり、11は特別な数（マスターナンバー）です。ただ、一人ひとりの2027年の数は、誕生月と誕生日を足して必ず1〜9にする決まりで計算しています。11は、その年全体の空気として読んでいます。"),
    ("2月29日生まれはどうなりますか。", "2027年に2月29日はありませんが、月日の数字（2と29）でそのまま計算します。2月29日生まれの2027年の数は6です。"),
    ("ライフパスナンバーとの違いは何ですか。", "ライフパスナンバーは生年月日すべてから出す、一生変わらない数です。2027年の数は誕生月と誕生日と年から出す、その一年だけの数で、9年で一巡します。性格はライフパス、今年の流れは2027年の数で読むと使い分けやすくなります。"),
]


def build(sample, updated):
    D = json.load(open(DATA, encoding="utf-8"))
    P, TB = D["py"], D["table"]
    H = []
    a = H.append
    a(KY_CSS)
    a(NY_CSS)
    a("""<style>.fh-b27-su-big{display:flex;align-items:center;justify-content:center;width:120px;height:120px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#F6F0E2,#D9C9A3);color:#3A2A14;font:800 50px 'Shippori Mincho',serif;box-shadow:0 0 0 3px rgba(212,175,90,.6),0 10px 30px rgba(0,0,0,.45);margin:10px}
.fh-b27-su-calc{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:8px 0}
.fh-b27-su-calc select{min-height:44px;border-radius:2px;border:1px solid var(--line);background:var(--deep);color:var(--ink);font:inherit;padding:0 8px}
.fh-b27-su-res{background:var(--cream);color:var(--cream-ink);border-radius:4px;padding:12px 14px;margin-top:8px;line-height:1.8}
.fh-b27 .fh-b27-su-res b{color:#9A3328;font-size:20px}.fh-b27 .fh-b27-su-res a{color:#9A3328;font-weight:700}
.fh-b27-su-mx{min-width:760px;font-size:12px}.fh-b27-su-mx td,.fh-b27-su-mx th{text-align:center;padding:4px 2px}
.fh-b27-su-pm{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:4px;margin:6px 0}
.fh-b27-su-pm div{background:#FFFBF1;border:1px solid #E3D6B5;border-radius:4px;padding:4px 2px;text-align:center;font-size:12px;color:#4A3B1C;line-height:1.4}
.fh-b27 .fh-b27-su-pm div b{display:block;font-size:15px;color:#26211B}
@media (max-width:640px){.fh-b27-su-big{width:84px;height:84px;font-size:34px}.fh-b27-su-pm{grid-template-columns:repeat(4,minmax(0,1fr))}}</style>""")
    a('<div class="fh-b27" data-fh-page="kyusei">\n<div class="fh-b27-note">')
    a('''<header class="fh-b27-hero">
  <div class="fh-b27-su-big" aria-hidden="true">11</div>
  <div class="fh-b27-hero-body">
    <span class="fh-b27-tape">2027年の運勢</span>
    <h1 class="fh-b27-title">数秘術でみる<br>2027年の運勢 1〜9の数別</h1>
    <p class="fh-b27-lead">誕生月と誕生日から出す「2027年の数（パーソナルイヤー）」は、9年で一巡する流れのいまの位置を表します。1〜9の数ごとに、総合運・恋愛・仕事・お金・健康と、月ごとの数とヒントをまとめました。誕生日を選ぶと、あなたの2027年の数がその場でわかります。</p>
  </div>
</header>''')
    items = [("su-calc", "あなたの2027年の数"), ("su-year", "2027年は「11」の年"), ("su-list", "2027年の数別の運勢"), ("su-table", "誕生日の早見表"), ("su-faq", "よくある質問")]
    a('<nav class="fh-b27-toc" aria-label="目次"><strong>このページの内容</strong><ol>' + "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in items) + "</ol></nav>")
    n = [1]

    def h2(t):
        s = f'<h2><span class="fh-b27-n">{n[0]:02d}</span>{t}</h2>'
        n[0] += 1
        return s

    mo = "".join(f'<option value="{m}">{m}月</option>' for m in range(1, 13))
    dy = "".join(f'<option value="{d}">{d}日</option>' for d in range(1, 32))
    titles = {int(k): ST.TEXTS[int(k)]["title"] for k in P}
    a(f'''<section class="fh-b27-sec" id="su-calc">
  {h2("あなたの2027年の数")}
  <p>{esc(ST.INTRO["how"])}</p>
  <div class="fh-b27-su-calc"><select id="su-m" aria-label="誕生月">{mo}</select><select id="su-d" aria-label="誕生日">{dy}</select><button type="button" class="fh-b27-ky-btn" id="su-go">2027年の数を出す</button></div>
  <div class="fh-b27-su-res" id="su-res" hidden></div>
  <div class="fh-b27-ny-jump" style="margin-top:12px">{"".join(f'<a href="#su-{p}" style="--c:{COL[p]}">2027年の数 {p}<small>{esc(titles[p])}</small></a>' for p in range(1, 10))}</div>
</section>''')
    a(f'''<section class="fh-b27-sec" id="su-year">
  {h2("2027年は「11」の年")}
  <p>{esc(ST.INTRO["year11"])}</p>
</section>''')
    a(f'<section class="fh-b27-sec" id="su-list">\n  {h2("2027年の数別の運勢")}')
    for p in range(1, 10):
        T, pm = ST.TEXTS[p], P[str(p)]["pm"]
        grid = "".join(f"<div>{m + 1}月<b>{v}</b>{PMW[v]}</div>" for m, v in enumerate(pm))
        mrows = "".join(f'<tr><td class="m">{m + 1}月</td><td class="p">月の数 {pm[m]}</td><td>{esc(T["months"][m])}</td></tr>' for m in range(12))
        pu = "".join(f"<li>{esc(k)}：{esc(v)}</li>" for k, v in T["push_months"])
        rs = "".join(f"<li>{esc(k)}：{esc(v)}</li>" for k, v in T["rest_months"])
        act = "".join(f"<li>{esc(x)}</li>" for x in T["action"])
        a(f'''<article class="fh-b27-ny-star" id="su-{p}" style="--c:{COL[p]}">
  <h3>2027年の数が「{p}」の人<small>誕生日{P[str(p)]["count"]}日分</small></h3>
  <span class="fh-b27-ny-theme">2027年は「{esc(T["title"])}」</span>
  <p class="fh-b27-et-char" style="color:var(--sub);font-size:14px">{esc(T["where"])}</p>
  <p>{esc(T["sougou"])}</p>
  <div class="fh-b27-ny-4">
    <div><b>恋愛運</b><p>{esc(T["love"])}</p></div>
    <div><b>仕事運</b><p>{esc(T["work"])}</p></div>
    <div><b>金運</b><p>{esc(T["money"])}</p></div>
    <div><b>健康運</b><p>{esc(T["health"])}</p></div>
  </div>
  <p style="margin:8px 0 0"><b>月ごとの数</b></p><div class="fh-b27-su-pm">{grid}</div>
  <div class="fh-b27-ny-gm"><ul class="g"><strong>動き出したい月</strong>{pu}</ul><ul class="c"><strong>整えたい月</strong>{rs}</ul></div>
  <div class="fh-b27-ky-wrap"><table class="fh-b27-ky-t fh-b27-ny-mt"><caption>2027年の数が{p}の人の月ごとのヒント</caption>
  <thead><tr><th>月</th><th>月の数</th><th>その月のヒント</th></tr></thead><tbody>{mrows}</tbody></table></div>
  <p style="margin-top:8px"><b>2027年の開運アクション</b></p><ul class="fh-b27-ny-act">{act}</ul>
</article>''')
        if p in (3, 6):
            a(f"<!--Ads{p // 3}-->")
    a("</section>")
    # 早見表（月×日）
    head = "".join(f"<th>{d}</th>" for d in range(1, 32))
    body = ""
    for m in range(1, 13):
        cells = "".join(f'<td>{TB.get(f"{m:02d}-{d:02d}", "")}</td>' for d in range(1, 32))
        body += f'<tr><th scope="row">{m}月</th>{cells}</tr>'
    a(f'''<section class="fh-b27-sec" id="su-table">
  {h2("誕生日の早見表")}
  <p>誕生月の行と誕生日の列が交わる数が、あなたの2027年の数です（空欄はその月にない日）。</p>
  <div class="fh-b27-ky-wrap"><table class="fh-b27-ky-t fh-b27-su-mx"><thead><tr><th>月＼日</th>{head}</tr></thead><tbody>{body}</tbody></table></div>
</section>''')
    qa = "".join(f'<details{" open" if i == 0 else ""}><summary>Q. {q}</summary><p>A. {x}</p></details>' for i, (q, x) in enumerate(FAQ))
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in FAQ]}
    a(f'''<section class="fh-b27-sec" id="su-faq">
  {h2("よくある質問")}
  <div class="fh-b27-ky-qa">{qa}</div>
</section>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<section class="fh-b27-sec">
  <div class="fh-b27-links">
    <a href="/suhijutsu/"><b>数秘術 →</b><small>ライフパスナンバーの計算と1〜9・11・22・33の意味</small></a>
    <a href="/unsei-2027/"><b>2027年の運勢まとめ →</b><small>九星・干支・数秘術・マヤ暦・星座・誕生日から</small></a>
    <a href="/kyusei/unsei-2027/"><b>2027年の運勢（九星気学）→</b><small>本命星別の総合運と吉方位</small></a>
    <a href="/366uranai/"><b>366日の誕生日占い →</b><small>誕生日ごとの2027年の運勢</small></a>
  </div>
</section>''')
    up = dt.date.fromisoformat(updated)
    a(f'<p class="fh-b27-foot">2027年の数（パーソナルイヤー）は、2027と誕生月・誕生日の数字をすべて足して1〜9にしたものです（1月1日切り替え・11・22は残さない）。月の数は、2027年の数にその月を足して1〜9にしています。文章はこのサイトで書いたもので、占いは楽しみと気づきのためにお読みください。<br>'
      f'最終更新日：{up.year}年{up.month}月{up.day}日／<a href="/about/">この記事の作成方針について</a></p>')
    a("</div>\n</div>")
    tbl = json.dumps(TB, separators=(",", ":"))
    tt = json.dumps({str(k): v for k, v in titles.items()}, ensure_ascii=False)
    a("<script>document.addEventListener('DOMContentLoaded',function(){var T=" + tbl + ",N=" + tt + ";"
      "var b=document.getElementById('su-go');if(!b)return;b.addEventListener('click',function(){var m=+document.getElementById('su-m').value,d=+document.getElementById('su-d').value;"
      "var k=(m<10?'0':'')+m+'-'+(d<10?'0':'')+d,r=document.getElementById('su-res'),p=T[k];r.hidden=false;"
      "if(!p){r.innerHTML='その日付はありません。月と日を選び直してください。';return;}"
      "r.innerHTML=m+'月'+d+'日生まれの2027年の数は <b>'+p+'</b>（'+N[p]+'）です。<br><a href=\"#su-'+p+'\">2027年の数'+p+'の運勢を読む →</a>';});});</script>")
    title = "数秘術 2027年の運勢｜2027年の数（パーソナルイヤー）1〜9別の総合運・恋愛・仕事・金運と月ごとの数"
    desc = "数秘術で見る2027年の運勢。誕生月と誕生日から出す2027年の数（パーソナルイヤー）1〜9ごとに、総合運・恋愛・仕事・金運・健康運、月ごとの数とヒントを紹介。誕生日を選ぶだけの計算と366日の早見表つき。"
    out = shell(title, desc, URL, "\n".join(H), sample, ())
    assert "！" not in out
    return out, title, desc


def main():
    updated = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    for sample, path in ((False, os.path.join(OUT, "unsei-2027-suhi.html")), (True, os.path.join(OUT, "sample", "unsei-2027-suhi.html"))):
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(build(sample, updated)[0])
        print("→", os.path.relpath(path, WORK))


if __name__ == "__main__":
    main()
