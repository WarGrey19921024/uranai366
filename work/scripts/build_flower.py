"""誕生花のページ（既存の固定ページ /flower/・ID 4262）の本文を作り直す（2026-10-15 本人の決定：占いページを見られるようにする）。
理由：今の /flower/ は誕生花の値が366日の誕生日ページ（日本花普及センターの一覧）と違い、出典も書いていない。
      「誕生花」「誕生花 一覧」「花言葉」で探す人向けに、366日の一覧と出典の説明を中心にする。
使い方: python work/scripts/build_flower.py [最終更新日]
出力: work/out/flower.html（投入用）、work/out/sample/flower.html（確認用）
データ: work/data/flower/birth_flowers_366.tsv（日本花普及センター）、work/data/materials_366.json（星座・七十二候）
"""
import collections, csv, datetime as dt, html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_hub import OUT, WORK, DATA, shell  # noqa: E402

URL = "/flower/"
DAYS = {1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
MONTH_FLOWER = {  # 月ごとの花の季節（手書き）
    1: "寒さの中で咲く花や、早春を告げる球根の花が並びます。雪の下で春を待つ花の花言葉には、希望や忍耐にまつわるものが目立ちます。",
    2: "梅や水仙、スミレなど、春の始まりを感じさせる花の季節。花屋に春の花が増えはじめるころで、やわらかな色の花が多く選ばれています。",
    3: "チューリップやフリージアなど、色とりどりの春の花が主役の月。卒業や旅立ちの季節らしく、門出を祝う花言葉も見られます。",
    4: "サクラに始まり、新緑とともに咲く花が並ぶ月。新しい生活のスタートに合う、明るく前向きな花言葉が多く選ばれています。",
    5: "スズランやカーネーション、バラなど、贈り物の花が多い季節。母の日の月らしく、感謝や愛情を伝える花言葉が目立ちます。",
    6: "梅雨の雨に映えるアジサイや、初夏のバラの季節。しっとりした花と華やかな花が入りまじり、結婚の月らしい花言葉もあります。",
    7: "ヒマワリやユリ、アサガオなど夏の花が並ぶ月。強い日差しの中で咲く花にちなんだ、情熱や憧れの花言葉が多く見られます。",
    8: "夏の盛りから秋へ向かう月で、暑さに強い花や涼しげな花が選ばれています。花言葉にも、元気さと静けさの両方があります。",
    9: "キキョウやコスモスなど、秋の七草や秋の花が増える月。実りの季節らしく、誠実さや調和にまつわる花言葉が目立ちます。",
    10: "キクやダリアなど、深い色の秋の花が並ぶ月。季節が深まるにつれて、思い出や感謝を表す花言葉も増えていきます。",
    11: "晩秋の花と、冬に向けて出回る花が交わる月。落ち着いた色合いの花が多く、静かな愛情を表す花言葉が見られます。",
    12: "シクラメンやポインセチアなど、冬の鉢花や祝いの花が並ぶ月。一年の締めくくりにふさわしい、祝福や感謝の花言葉があります。",
}
FAQ = [
    ("誕生花とは何ですか。",
     "1年366日（うるう年の2月29日を含む）それぞれに割り当てられた花のことです。自分や大切な人の誕生日の花として、贈り物やお祝いに使われています。"),
    ("誕生花がサイトによって違うのはなぜですか。",
     "誕生花を公式に決めている団体はなく、本や団体ごとに選び方が違うためです。国立国会図書館のレファレンス協同データベースでも「日付と花の組み合わせは参考資料によって異なる」と紹介されています。このサイトでは、一般財団法人日本花普及センターの一覧1つだけを使っています。"),
    ("1つの誕生日に誕生花は1つだけですか。",
     "このページでは、日本花普及センターの一覧に合わせて1日1つの花を載せています。ほかの資料では1日に複数の花を挙げているものもあります。"),
    ("同じ花が何度も出てくるのはなぜですか。",
     "スミレやストックのように、花の色によって花言葉が変わる花は、色ごとに別の日に割り当てられているためです。"),
    ("誕生花の花言葉は1つだけですか。",
     "花言葉は資料によって複数あることが多く、このページでは日本花普及センターの一覧に載っている花言葉を1つ載せています。"),
    ("誕生日のほかの占いも見られますか。",
     "見られます。日付を選んだあとに出る「誕生日のページへ」から、性格、相性の良い誕生日、誕生石、2027年の運勢まで読めます。"),
]


def esc(s):
    return html.escape(str(s), quote=True)


def load():
    rows = list(csv.reader(open(os.path.join(DATA, "flower", "birth_flowers_366.tsv"), encoding="utf-8"), delimiter="\t"))[1:]
    fl = {r[0]: (r[1], r[2]) for r in rows}
    mats = json.load(open(os.path.join(DATA, "materials_366.json"), encoding="utf-8"))
    assert len(fl) == 366
    for k, (f, h) in fl.items():  # 誕生日ページと同じ値であること
        assert mats[k]["flower"]["flower"] == f and mats[k]["flower"]["hanakotoba"] == h, k
    return fl, mats


def day_url(k):
    return f"/366uranai/{k[:2]}-{k[2:]}/"


CSS = """<style id="fh-b27-fl-css">
.fh-b27[data-fh-page="flower"]{--ink:#EEF2EC;--sub:#CFDACF;--mute:#A9B8AB;--paper:#1D2925;--deep:#18221F;--line:#46604F;--gold:#F4B6C2;--leaf:#A8D5BA;--cream:#FBF5EE;--cream-ink:#2F2A26}
.fh-b27[data-fh-page="flower"] a:hover{color:#FFD3DB}
.fh-b27[data-fh-page="flower"] .fh-b27-note{border-left:0;border-radius:22px;background-color:var(--paper);
  background-image:radial-gradient(circle at 92% 4%,rgba(244,182,194,.18),transparent 36%),radial-gradient(circle at 0% 40%,rgba(168,213,186,.12),transparent 36%),radial-gradient(rgba(255,255,255,.06) 1px,transparent 1.4px);
  background-size:auto,auto,24px 24px;box-shadow:0 14px 40px rgba(0,0,0,.45),inset 0 0 0 1px rgba(244,182,194,.16)}
.fh-b27[data-fh-page="flower"] .fh-b27-hero{align-items:center}
.fh-b27-fl-emb{position:relative;flex:0 0 120px;height:120px}
.fh-b27-fl-emb i{position:absolute;left:38px;top:4px;width:44px;height:58px;border-radius:50% 50% 50% 50%/60% 60% 40% 40%;background:radial-gradient(circle at 50% 30%,#FFE1E7,#E68FA2 75%);transform-origin:22px 56px;opacity:.92}
.fh-b27-fl-emb i:nth-child(2){transform:rotate(72deg)}.fh-b27-fl-emb i:nth-child(3){transform:rotate(144deg)}.fh-b27-fl-emb i:nth-child(4){transform:rotate(216deg)}.fh-b27-fl-emb i:nth-child(5){transform:rotate(288deg)}
.fh-b27-fl-emb b{position:absolute;left:47px;top:47px;width:26px;height:26px;border-radius:50%;background:#F7D774;box-shadow:0 0 0 3px rgba(0,0,0,.08)}
.fh-b27-fl-emb{animation:fh-b27-fl-spin 30s linear infinite}@keyframes fh-b27-fl-spin{to{transform:rotate(360deg)}}
@media (prefers-reduced-motion:reduce){.fh-b27-fl-emb{animation:none}}
.fh-b27[data-fh-page="flower"] .fh-b27-tape{transform:none;border-radius:999px;background:linear-gradient(90deg,var(--gold),var(--leaf));color:#1D2925}
.fh-b27[data-fh-page="flower"] .fh-b27-title{font-family:'Shippori Mincho',serif;font-weight:800;font-size:30px}
.fh-b27[data-fh-page="flower"] h2{font-family:'Shippori Mincho',serif;font-weight:800;font-size:24px}
.fh-b27[data-fh-page="flower"] h2 .fh-b27-n{border:0;background:linear-gradient(135deg,var(--gold),var(--leaf));color:#1D2925;font-weight:800;border-radius:50% 50% 50% 10px}
.fh-b27[data-fh-page="flower"] h3{border-bottom:0;background:linear-gradient(90deg,var(--gold),var(--leaf)) left bottom/100% 2px no-repeat}
.fh-b27-fl-pick{border:1.5px solid rgba(244,182,194,.35);border-radius:18px;background:var(--deep);padding:16px;display:flex;flex-direction:column;gap:12px}
.fh-b27-fl-pick form{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.fh-b27-fl-pick select{min-height:44px;border-radius:10px;border:1.5px solid var(--line);background:var(--paper);color:var(--ink);font:inherit;padding:0 10px}
.fh-b27-fl-pick button{min-height:44px;border:0;border-radius:999px;background:linear-gradient(90deg,#F4B6C2,#E8A3B4);color:#1D2925;font:inherit;font-weight:700;padding:0 18px;cursor:pointer}
.fh-b27-fl-card{background:var(--cream);color:var(--cream-ink);border-radius:14px;padding:18px 20px;line-height:1.75}
.fh-b27-fl-card small{color:#7A6F64;font-size:13px}
.fh-b27 .fh-b27-fl-card .fh-b27-fl-name{font-family:'Shippori Mincho',serif;font-size:28px;font-weight:800;color:var(--cream-ink);margin:2px 0}
.fh-b27 .fh-b27-fl-card p{color:var(--cream-ink)}
.fh-b27 .fh-b27-fl-card .fh-b27-fl-kotoba{font-size:17px}
.fh-b27 .fh-b27-fl-card a{color:#8A3E55;font-weight:700}
.fh-b27 .fh-b27-fl-card b{color:#8A3E55}
.fh-b27-fl-list{display:flex;flex-direction:column;gap:8px}
.fh-b27-fl-list details{border:1px solid rgba(244,182,194,.25);border-radius:14px;background:var(--deep);padding:6px 12px}
.fh-b27-fl-list summary{cursor:pointer;font-family:'Shippori Mincho',serif;font-weight:700;font-size:16px;color:var(--gold)}
.fh-b27-fl-list summary small{color:var(--mute);font-family:inherit;font-weight:400;font-size:12.5px;margin-left:8px}
.fh-b27-fl-list p.fh-b27-fl-m{font-size:14px;color:var(--sub);margin:6px 0}
.fh-b27-fl-t{width:100%;border-collapse:collapse;font-size:14px;line-height:1.65}
.fh-b27-fl-t caption{position:absolute;left:-9999px}
.fh-b27-fl-t th,.fh-b27-fl-t td{border-bottom:1px dashed var(--line);padding:6px 6px;text-align:left;vertical-align:top}
.fh-b27-fl-t thead th{color:var(--gold);font-size:12.5px}
.fh-b27-fl-t tbody th{white-space:nowrap}
.fh-b27-fl-rep{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.fh-b27-fl-rep div{border:1px solid rgba(168,213,186,.3);border-radius:14px;background:var(--deep);padding:10px 14px;font-size:14px;line-height:1.75}
.fh-b27-fl-rep b{font-family:'Shippori Mincho',serif;font-size:17px;color:var(--leaf)}
.fh-b27-fl-src{border-left:3px solid var(--gold);padding:8px 14px;background:rgba(244,182,194,.06);border-radius:0 10px 10px 0;font-size:14.5px}
.fh-b27-fl-use{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;list-style:none;margin:0;padding:0}
.fh-b27 .fh-b27-fl-use li{margin:0;border:1px dashed var(--line);border-radius:12px;padding:10px 14px;font-size:14.5px;line-height:1.8}
.fh-b27-fl-use li::before{content:none}
.fh-b27-fl-use b{display:block;color:var(--gold);font-family:'Shippori Mincho',serif}
.fh-b27-fl-qa details{border-bottom:1px dashed var(--line);padding:8px 2px}
.fh-b27-fl-qa summary{cursor:pointer;font-weight:700}
.fh-b27-fl-qa p{margin-top:6px;font-size:14.5px}
.fh-b27[data-fh-page="flower"] .fh-b27-toc{border-style:solid;border-color:rgba(244,182,194,.25);border-radius:16px}
.fh-b27[data-fh-page="flower"] .fh-b27-toc ol{columns:2;column-gap:28px;list-style:none;padding-left:0}
@media (max-width:640px){.fh-b27-fl-rep,.fh-b27-fl-use{grid-template-columns:1fr}.fh-b27[data-fh-page="flower"] .fh-b27-toc ol{columns:1}.fh-b27-fl-emb{flex-basis:96px;height:96px;transform:scale(.8)}.fh-b27[data-fh-page="flower"] .fh-b27-title{font-size:25px}}
</style>"""


def build(sample, updated):
    fl, mats = load()
    H = []
    a = H.append
    a(CSS)
    a('<div class="fh-b27" data-fh-page="flower">\n<div class="fh-b27-note">')
    a('''<header class="fh-b27-hero">
  <div class="fh-b27-fl-emb" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><b></b></div>
  <div class="fh-b27-hero-body">
    <span class="fh-b27-tape">人生予報 誕生花</span>
    <h1 class="fh-b27-title">誕生花と花言葉<br>366日の一覧</h1>
    <p class="fh-b27-lead">1月1日から12月31日まで、2月29日も入れた366日の誕生花と花言葉です。誕生日を選ぶとその日の花がわかり、同じ誕生日の性格や2027年の運勢のページにも進めます。誕生花は、一般財団法人日本花普及センターの一覧だけを使っています。</p>
  </div>
</header>''')
    items = [("b27-fl-pick", "誕生日の花を調べる"), ("b27-fl-list", "366日の誕生花と花言葉の一覧"), ("b27-fl-rep", "色違いで何度も出てくる花"),
             ("b27-fl-what", "誕生花とは・サイトによって違う理由"), ("b27-fl-use", "誕生花の楽しみ方"), ("b27-fl-faq", "よくある質問")]
    a('<nav class="fh-b27-toc" aria-label="目次"><strong>このページの内容</strong><ol>' +
      "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in items) + "</ol></nav>")
    n = 1

    def h2(t):
        return f'<h2><span class="fh-b27-n">{n}</span><span>{t}</span></h2>'
    # 1 調べる
    data = {k: [f, h, mats[k]["sign"], mats[k]["kou"]] for k, (f, h) in fl.items()}
    mo = "".join(f'<option value="{m:02d}">{m}月</option>' for m in range(1, 13))
    do = "".join(f'<option value="{d:02d}">{d}日</option>' for d in range(1, 32))
    f0, h0 = fl["0101"]
    a(f'''<section class="fh-b27-sec" id="b27-fl-pick">
  {h2("誕生日の花を調べる")}
  <div class="fh-b27-fl-pick">
    <form id="fh-b27-fl-form" aria-label="誕生日を選ぶ"><select name="m" aria-label="月">{mo}</select><select name="d" aria-label="日">{do}</select><button type="submit">花を見る</button>
      <button type="button" id="fh-b27-fl-today" style="background:transparent;border:1.5px solid var(--leaf);color:var(--leaf)">今日の誕生花</button></form>
    <div class="fh-b27-fl-card" id="fh-b27-fl-card" aria-live="polite">
      <small id="fh-b27-fl-date">1月1日の誕生花</small>
      <p class="fh-b27-fl-name" id="fh-b27-fl-name">{esc(f0)}</p>
      <p class="fh-b27-fl-kotoba">花言葉：<b id="fh-b27-fl-kotoba">{esc(h0)}</b></p>
      <p><small id="fh-b27-fl-more">この日の星座：{esc(mats["0101"]["sign"])}／七十二候：{esc(mats["0101"]["kou"])}</small></p>
      <p><a id="fh-b27-fl-link" href="{day_url("0101")}">1月1日生まれの性格・相性と2027年の運勢へ →</a></p>
    </div>
  </div>
  <noscript><p class="fh-b27-small">花を調べるにはJavaScriptを有効にしてください。下の一覧からも探せます。</p></noscript>
</section>''')
    js = ("(function(){var D=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";"
          "var f=document.getElementById('fh-b27-fl-form');if(!f)return;var M=f.querySelector('[name=m]'),Dd=f.querySelector('[name=d]'),"
          "N={1:31,2:29,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31};"
          "function $(i){return document.getElementById(i)}"
          "function fit(){var n=N[+M.value];for(var i=0;i<Dd.options.length;i++){Dd.options[i].disabled=i>=n;}if(+Dd.value>n)Dd.value=String(n).padStart(2,'0');}"
          "function show(m,d){var k=m+d,x=D[k];if(!x)return;var t=(+m)+'月'+(+d)+'日';$('fh-b27-fl-date').textContent=t+'の誕生花';$('fh-b27-fl-name').textContent=x[0];"
          "$('fh-b27-fl-kotoba').textContent=x[1];$('fh-b27-fl-more').textContent='この日の星座：'+x[2]+'／七十二候：'+x[3];"
          "var l=$('fh-b27-fl-link');l.href='/366uranai/'+m+'-'+d+'/';l.textContent=t+'生まれの性格・相性と2027年の運勢へ →';}"
          "M.addEventListener('change',fit);f.addEventListener('submit',function(e){e.preventDefault();show(M.value,Dd.value);});"
          "$('fh-b27-fl-today').addEventListener('click',function(){var n=new Date(),m=String(n.getMonth()+1).padStart(2,'0'),d=String(n.getDate()).padStart(2,'0');M.value=m;fit();Dd.value=d;show(m,d);});"
          "})();")
    a(f"<script>{js}</script>")
    n += 1
    # 2 一覧
    det = ""
    for m in range(1, 13):
        rows = ""
        for d in range(1, DAYS[m] + 1):
            k = f"{m:02d}{d:02d}"
            f, h = fl[k]
            rows += f'<tr><th scope="row"><a href="{day_url(k)}">{m}月{d}日</a></th><td>{esc(f)}</td><td>{esc(h)}</td></tr>'
        det += (f'<details{" open" if m == 1 else ""} id="b27-fl-m{m:02d}"><summary>{m}月の誕生花<small>{DAYS[m]}日分</small></summary>'
                f'<p class="fh-b27-fl-m">{esc(MONTH_FLOWER[m])}</p>'
                f'<table class="fh-b27-fl-t"><caption>{m}月の誕生花と花言葉</caption><thead><tr><th scope="col">誕生日</th><th scope="col">誕生花</th><th scope="col">花言葉</th></tr></thead><tbody>{rows}</tbody></table></details>')
    a(f'''<section class="fh-b27-sec" id="b27-fl-list">
  {h2("366日の誕生花と花言葉の一覧")}
  <p>月を開くと、その月の毎日の誕生花と花言葉が見られます。日付を押すと、その誕生日の性格・相性・誕生石・2027年の運勢のページが開きます。</p>
  <div class="fh-b27-fl-list">{det}</div>
</section>''')
    n += 1
    # 3 色違い
    groups = collections.OrderedDict()
    for k in sorted(fl):
        base = re.sub(r"[（(].*", "", fl[k][0])
        groups.setdefault(base, []).append(k)
    reps = [(b, ks) for b, ks in groups.items() if len(ks) >= 3]
    reps.sort(key=lambda x: -len(x[1]))
    cards = ""
    for b, ks in reps:
        lines = "／".join(f'<a href="{day_url(k)}">{int(k[:2])}/{int(k[2:])}</a> {esc(fl[k][0].replace(b, "").strip("()（）") or b)}「{esc(fl[k][1])}」' for k in ks)
        cards += f"<div><b>{esc(b)}</b>（{len(ks)}日）<br>{lines}</div>"
    a(f'''<section class="fh-b27-sec" id="b27-fl-rep">
  {h2("色違いで何度も出てくる花")}
  <p>366日の中には、同じ花が色や種類を変えて何度も登場します。花の色によって花言葉が変わるためで、同じ花でも誕生日ごとに意味が違います。3日以上に出てくる花をまとめました。</p>
  <div class="fh-b27-fl-rep">{cards}</div>
</section>''')
    n += 1
    # 4 誕生花とは
    a(f'''<section class="fh-b27-sec" id="b27-fl-what">
  {h2("誕生花とは・サイトによって違う理由")}
  <p>誕生花は、1年366日それぞれに花を割り当てたものです。誕生日の贈り物やメッセージカード、お祝いの花選びに使われています。</p>
  <p>実は、誕生花を公式に決めている団体はありません。長野県のページでは、366日それぞれに花が割り当てられていて、その根拠は神話や開花時期などさまざまで、発行元によってまちまちだと紹介されています。国立国会図書館のレファレンス協同データベースでも、日付と花の組み合わせは参考資料によって異なり、1月1日の花が3つの資料で3つとも違う例が紹介されています。</p>
  <div class="fh-b27-fl-src"><b>このサイトの出典</b><br>一般財団法人日本花普及センターの「誕生花」一覧（長野県の公式ページで紹介されているもの）だけを使い、ほかのサイトの値と混ぜていません。366日の誕生日占いのページも、同じ一覧の花を載せています。</div>
  <p>ほかのサイトや本で見た誕生花と違っていても、どちらかが間違いというわけではありません。気に入った花を、自分の誕生花として楽しんでください。</p>
</section>''')
    n += 1
    # 5 楽しみ方
    use = [("誕生日の贈り物に", "相手の誕生日の花を花束やアレンジメントに入れると、日付にちなんだ特別な贈り物になります。季節によっては花屋にない花もあるので、早めに相談しておくと安心です。"),
           ("メッセージカードに", "花の名前と花言葉をカードに一言添えるだけで、贈り物に意味が加わります。花そのものが手に入らないときにも使えます。"),
           ("記念日の花として", "結婚記念日や子どもの誕生日など、家族の大切な日の誕生花を知っておくと、毎年の花選びの楽しみになります。"),
           ("自分の誕生日に", "自分の誕生花を部屋に飾ったり、花言葉を一年の目標の言葉にしたりと、自分のための楽しみ方もできます。")]
    lis = "".join(f"<li><b>{esc(x)}</b>{esc(y)}</li>" for x, y in use)
    a(f'''<section class="fh-b27-sec" id="b27-fl-use">
  {h2("誕生花の楽しみ方")}
  <ul class="fh-b27-fl-use">{lis}</ul>
  <p class="fh-b27-small">花によっては、ペットや小さな子どもが口にすると害のあるものもあります。飾る場所に気をつけてください。</p>
</section>''')
    n += 1
    # 6 FAQ
    qa = "".join(f'<details{" open" if i == 0 else ""}><summary>Q. {q}</summary><p>A. {x}</p></details>' for i, (q, x) in enumerate(FAQ))
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in FAQ]}
    a(f'''<section class="fh-b27-sec" id="b27-fl-faq">
  {h2("よくある質問")}
  <div class="fh-b27-fl-qa">{qa}</div>
</section>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>''')
    a('''<section class="fh-b27-sec" id="b27-fl-more">
  <div class="fh-b27-links">
    <a href="/366uranai/"><b>366日の誕生日占い →</b><small>誕生日から性格・相性・2027年の運勢</small></a>
    <a href="/compatibility/"><b>誕生日相性占い →</b><small>2人の誕生日で相性を見る</small></a>
    <a href="/seinengappi/"><b>生年月日まるごと診断 →</b><small>8つの占いを1枚のカードに</small></a>
  </div>
</section>''')
    up = dt.date.fromisoformat(updated)
    a(f'<p class="fh-b27-foot">誕生花と花言葉は、一般財団法人日本花普及センターの「誕生花」一覧によります。星座と七十二候は、このサイトで計算した値です。<br>'
      f'最終更新日：{up.year}年{up.month}月{up.day}日／<a href="/about/">この記事の作成方針について</a></p>')
    a("</div>\n</div>")
    title = "誕生花一覧｜366日の誕生日の花と花言葉【今日の誕生花も】"
    desc = ("366日の誕生花と花言葉の一覧。誕生日を選ぶとその日の花と花言葉がわかり、今日の誕生花も表示します。"
            "色違いで何度も出てくる花、誕生花がサイトによって違う理由、出典（日本花普及センター）も紹介。")
    out = shell(title, desc, URL, "\n".join(H), sample)
    assert "動物占い" not in out and "！" not in out
    return out


def main():
    updated = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    for sample, path in ((False, os.path.join(OUT, "flower.html")), (True, os.path.join(OUT, "sample", "flower.html"))):
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(build(sample, updated))
        print("→", os.path.relpath(path, WORK))


if __name__ == "__main__":
    main()
