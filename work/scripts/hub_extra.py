"""366日一覧（/366uranai/）に足す、検索向けの解説（2026-10-15 本人の決定：「誕生日占い」「生年月日占い」で見つけてもらうための強化）。
build_hub.py から呼ぶ。値はすべて materials_366.json（計算済みの材料）から出し、文章はこのサイトで書いたもの。
"""
import html
import json

import json as _jj, os as _os
STD = _jj.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "data", "bday_standard_366.json"), encoding="utf-8"))["days"]

DAYS = {1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
MONTH_TEXT = {  # 誕生月ごとの空気（手書き。各月の暦と星座の移り変わりから）
    1: "新しい年の始まりと寒さの底が重なる月。山羊座から水瓶座へ移り、地に足のついた粘り強さと、型にはまらない発想の両方が見られます。",
    2: "立春を迎えて暦の上では春になる月。水瓶座から魚座へと移り、仲間を大切にする心と、人の気持ちに寄り添うやさしさが育ちます。",
    3: "春分をはさみ、星座の一年が魚座から牡羊座へと始まり直す月。感受性の豊かさと、思い立ったらすぐ動ける勢いが同居します。",
    4: "花が咲きそろい、新しい環境が動き出す月。牡羊座の行動力から牡牛座の落ち着きへと移り、始めたことを形にする力が加わります。",
    5: "若葉が伸び、夏の気配が近づく月。牡牛座の着実さから双子座の好奇心へ。五感で味わう豊かさと、軽やかな会話の楽しさが持ち味です。",
    6: "梅雨と夏至が訪れ、昼がいちばん長くなる月。双子座から蟹座へと移り、知りたい気持ちの強さに、身近な人を守る温かさが重なります。",
    7: "梅雨が明け、夏の光が強まる月。蟹座の面倒見のよさから獅子座の華やかさへ。人を包む力と、自分を表現する力がそろいます。",
    8: "暑さの盛りから立秋へ向かう月。獅子座の明るさから乙女座の丁寧さへと移り、堂々とした存在感と細やかな気配りを持ち合わせます。",
    9: "秋分をはさみ、昼と夜の長さがそろう月。乙女座から天秤座へ。物事を整える力と、人と人とのバランスをとる感覚に優れています。",
    10: "空が澄み、実りが深まる月。天秤座の社交性から蠍座の集中力へと移り、人当たりのよさの奥に、一つを深く掘り下げる芯があります。",
    11: "立冬を迎え、冬の支度が始まる月。蠍座の粘り強さから射手座の自由さへ。じっくり向き合う力と、遠くを目指す視野の広さが持ち味です。",
    12: "冬至で昼がいちばん短くなり、一年が締めくくられる月。射手座の楽天性から山羊座の堅実さへと移り、夢と現実の両方を見る目が育ちます。",
}
FAQ = [
    ("誕生日占いと生年月日占いは何が違いますか。",
     "誕生日占いは月日だけで決まる占い（星座・七十二候・誕生花・誕生日の数など）、生年月日占いは生まれた年も使う占い（九星・干支・四柱推命・マヤ暦など）を指すことが多いです。このサイトの366日のページは誕生日で占い、生まれ年を選ぶと生年月日占いの結果も加わります。"),
    ("誕生日だけで何がわかりますか。",
     "性格の特徴、相性の良い誕生日と気をつけたい誕生日、誕生花と花言葉、誕生石、同じ誕生日の有名人、2027年の分野別・月別の運勢がわかります。"),
    ("星座の境目の日に生まれた場合はどうなりますか。",
     "太陽が星座を移る時刻は年によって違うため、境目の日は生まれた年と時刻によって隣の星座になることがあります。一覧では金色の点線で示し、各ページにもそのことを書いています。"),
    ("2月29日生まれのページはありますか。",
     "あります。2月29日を含めた366日すべてにページがあります。"),
    ("2027年の運勢はいつからいつまでですか。",
     "2027年1月から12月までの12か月です。なお干支と九星の年は立春（2027年2月4日）で切り替わるため、九星の運勢は立春からの1年として読みます。"),
    ("同じ誕生日なら、性格も同じですか。",
     "同じ誕生日の人は太陽の位置や暦の季節が近く、共通する傾向があります。ただ生まれた年や時刻、育った環境で一人ひとりは違うので、ページの内容は「その日に生まれた人に出やすい傾向」として読んでください。"),
    ("誕生花や誕生石は何をもとにしていますか。",
     "誕生花は日本花普及センター、誕生石は全国宝石卸商協同組合（2021年）の一覧によります。誕生日石・誕生色は、広く使われている一覧を複数突き合わせて載せています。このサイトが独自に選んだ守護石・ラッキーカラーは、そのことを各ページに書いています。"),
    ("無料で使えますか。生年月日は保存されますか。",
     "すべて無料です。選んだ生年月日は送信も保存もせず、ページの中だけで計算します。"),
]


def esc(s):
    return html.escape(str(s), quote=True)


def url(k):
    return f"/366uranai/{k[:2]}-{k[2:]}/"


def css():
    return """<style id="fh-b27-hx-css">
.fh-b27-hx-go{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:4px}
.fh-b27-hx-go select{min-height:44px;border-radius:8px;border:1.5px solid var(--line);background:var(--deep);color:var(--ink);font:inherit;padding:0 10px}
.fh-b27-hx-go button{min-height:44px;border:0;border-radius:999px;background:var(--gold);color:var(--paper);font:inherit;font-weight:700;padding:0 18px;cursor:pointer}
.fh-b27-hx-know{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;list-style:none;margin:0;padding:0}
.fh-b27 .fh-b27-hx-know li{margin:0;border:1.5px dashed var(--line);border-radius:8px;background:var(--deep);padding:10px 14px;font-size:14.5px;line-height:1.8}
.fh-b27-hx-know li::before{content:none}
.fh-b27-hx-know b{display:block;font-family:'Klee One',cursive;font-size:16.5px;color:var(--gold)}
.fh-b27-hx-sample{background:var(--cream);color:var(--cream-ink);border-radius:10px;padding:16px 18px;line-height:1.75;font-size:14.5px}
.fh-b27-hx-sample strong{font-family:'Shippori Mincho',serif;font-size:19px}
.fh-b27-hx-sample dl{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:4px 16px;margin:8px 0 0}
.fh-b27-hx-sample dl div{display:flex;gap:10px;border-bottom:1px dashed #CFC6B5;padding:3px 0}
.fh-b27-hx-sample dt{color:#6B645B;flex:0 0 6.5em}.fh-b27-hx-sample dd{margin:0;font-weight:700}
.fh-b27 .fh-b27-hx-sample a{color:#8A5A1E}
.fh-b27 .fh-b27-hx-sample p,.fh-b27 .fh-b27-hx-sample strong{color:var(--cream-ink)}
.fh-b27-hx-t{width:100%;border-collapse:collapse;font-size:14px;line-height:1.7}
.fh-b27-hx-t caption{text-align:left;color:var(--sub);font-size:13px;padding-bottom:4px}
.fh-b27-hx-t th,.fh-b27-hx-t td{border-bottom:1px dashed var(--line);padding:7px 6px;text-align:left;vertical-align:top}
.fh-b27-hx-t thead th{color:var(--gold);font-size:13px}
.fh-b27-hx-months{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.fh-b27-hx-months div{border:1.5px dashed var(--line);border-radius:10px;background:var(--deep);padding:12px 14px}
.fh-b27-hx-months h3{font-size:18px;margin-bottom:4px}
.fh-b27-hx-months p{font-size:14px;line-height:1.8}
.fh-b27-hx-months small{display:block;color:var(--mute);font-size:12.5px;line-height:1.7;margin-top:4px}
.fh-b27-hx-list{display:flex;flex-direction:column;gap:8px}
.fh-b27-hx-list details{border:1.5px dashed var(--line);border-radius:8px;background:var(--deep);padding:6px 12px}
.fh-b27-hx-list summary{cursor:pointer;font-family:'Klee One',cursive;font-size:16px;color:var(--gold)}
.fh-b27-hx-wrap{overflow-x:auto}
.fh-b27-hx-wrap .fh-b27-hx-t{min-width:560px;font-size:13.5px}
.fh-b27-hx-py{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.fh-b27-hx-py div{border:1.5px dashed var(--line);border-radius:8px;padding:8px 12px;background:var(--deep);font-size:13.5px;line-height:1.7}
.fh-b27-hx-py b{font-family:'Shippori Mincho',serif;font-size:20px;color:var(--gold);margin-right:6px}
.fh-b27-hx-qa details{border-bottom:1px dashed var(--line);padding:8px 2px}
.fh-b27-hx-qa summary{cursor:pointer;font-weight:700}
.fh-b27-hx-qa p{margin-top:6px;font-size:14.5px}
.fh-b27-hx-mon .fh-b27-month{display:none}.fh-b27-hx-mon .fh-b27-month.is-on{display:block}
.fh-b27-hx-mon .fh-b27-mnav a[aria-current="true"]{background:var(--gold);color:var(--paper);border-color:var(--gold)}
.fh-b27-hx-hint{font-size:13.5px;color:var(--sub)}
@media (max-width:640px){.fh-b27-hx-know,.fh-b27-hx-months,.fh-b27-hx-sample dl{grid-template-columns:1fr}.fh-b27-hx-py{grid-template-columns:repeat(2,minmax(0,1fr))}}
</style>"""


def picker(mats=None):
    """ヒーローの下：月と日を選ぶと、その日の「誕生日カード」がめくれて出る → その日のページへ（2026-10-16 ワクワク感の改善）。
    JSが動かなくても、送信すればその日のページへ移動する（form の action）。"""
    import json as _j
    mo = "".join(f'<option value="{m:02d}">{m}月</option>' for m in range(1, 13))
    do = "".join(f'<option value="{d:02d}">{d}日</option>' for d in range(1, 32))
    data = {}
    for k, v in (mats or {}).items():
        sd = STD[f"{k[:2]}-{k[2:]}"]
        data[k] = [v["sign"], v["flower"]["flower"], v["flower"]["hanakotoba"], v["birthstone_month"].split("・")[0], sd["color"], sd["color_hex"] or "#C9B98F", sd["stone"]]
    js = ("(function(){var f=document.getElementById('fh-b27-hx-go');if(!f)return;var X=" + _j.dumps(data, ensure_ascii=False, separators=(",", ":")) + ","
          "M=f.querySelector('[name=m]'),D=f.querySelector('[name=d]'),C=document.getElementById('fh-b27-hx-card'),"
          "N={1:31,2:29,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31};function e(s){return String(s).replace(/[&<>\"]/g,'')}"
          "function fit(){var n=N[+M.value];for(var i=0;i<D.options.length;i++){D.options[i].disabled=i>=n;}if(+D.value>n)D.value=String(n).padStart(2,'0');}"
          "function show(m,d){var x=X[m+d];if(!x||!C){location.href='/366uranai/'+m+'-'+d+'/';return}var t=(+m)+'月'+(+d)+'日';"
          "C.innerHTML='<div class=\"in\"><small>'+t+'生まれの</small><b class=\"ttl\">誕生日カード</b><dl><div><dt>誕生花</dt><dd>'+e(x[1])+'<small>「'+e(x[2])+'」</small></dd></div><div><dt>星座</dt><dd>'+e(x[0])+'</dd></div>"
          "<div><dt>誕生石</dt><dd>'+e(x[3])+'</dd></div><div><dt>誕生日石</dt><dd>'+e(x[6])+'</dd></div><div><dt>誕生色</dt><dd><i style=\"background:'+x[5]+'\"></i>'+e(x[4])+'</dd></div></dl>"
          "<a class=\"go\" href=\"/366uranai/'+m+'-'+d+'/\">'+t+'生まれの性格と2027年の運勢を見る →</a></div>';C.hidden=false;C.classList.remove('on');void C.offsetWidth;C.classList.add('on');}"
          "M.addEventListener('change',fit);f.addEventListener('submit',function(ev){ev.preventDefault();show(M.value,D.value);});"
          "var td=document.getElementById('fh-b27-hx-today');if(td)td.addEventListener('click',function(){var n=new Date(),m=String(n.getMonth()+1).padStart(2,'0'),d=String(n.getDate()).padStart(2,'0');M.value=m;fit();D.value=d;show(m,d);});})();")
    css = ("<style>.fh-b27-hx-card{perspective:900px;margin-top:12px}.fh-b27-hx-card .in{background:linear-gradient(160deg,#FFFBF0,#F1E6CC);color:#2E2A26;border-radius:14px;padding:16px 18px;"
           "box-shadow:0 10px 26px rgba(0,0,0,.35);border:2px solid #D9B45A;text-align:center}.fh-b27-hx-card.on .in{animation:fh-b27-hx-flip .8s cubic-bezier(.2,1.2,.4,1) both}"
           "@keyframes fh-b27-hx-flip{from{transform:rotateY(90deg);opacity:0}to{transform:none;opacity:1}}"
           ".fh-b27 .fh-b27-hx-card small{color:#7A6A4E}.fh-b27-hx-card .ttl{display:block;font:800 22px 'Shippori Mincho',serif;color:#2E2A26;margin-bottom:6px}"
           ".fh-b27-hx-card dl{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px;margin:0 0 12px;text-align:left}.fh-b27-hx-card dl div{background:#fff;border-radius:8px;padding:6px 10px}"
           ".fh-b27-hx-card dl div:nth-child(1){grid-column:span 2}.fh-b27 .fh-b27-hx-card dt{font-size:11px;color:#8A7A5E;margin:0}.fh-b27 .fh-b27-hx-card dd{margin:0;font-weight:800;color:#2E2A26}"
           ".fh-b27-hx-card dd small{font-weight:400;margin-left:4px}.fh-b27-hx-card dd i{display:inline-block;width:12px;height:12px;border-radius:50%;margin-right:6px;box-shadow:inset 0 0 0 1px rgba(0,0,0,.2)}"
           ".fh-b27 a.go{display:inline-block;background:#B5462E;color:#FFF5E6;border-radius:999px;padding:10px 18px;font-weight:800;text-decoration:none}"
           ".fh-b27-hx-today{min-height:40px;border:1.5px solid currentColor;border-radius:999px;background:transparent;color:inherit;font:inherit;padding:0 14px;cursor:pointer}"
           "@media (prefers-reduced-motion:reduce){.fh-b27-hx-card.on .in{animation:none}}</style>")
    return (css + f'<form class="fh-b27-hx-go" id="fh-b27-hx-go" action="/366uranai/" aria-label="誕生日のカードを見る">'
            f'<label class="fh-b27-small" for="fh-b27-hx-m">誕生日を選んでください</label>'
            f'<select id="fh-b27-hx-m" name="m" aria-label="月">{mo}</select><select name="d" aria-label="日">{do}</select>'
            f'<button type="submit">めくる →</button><button type="button" class="fh-b27-hx-today" id="fh-b27-hx-today">今日の誕生日</button></form>'
            f'<div class="fh-b27-hx-card" id="fh-b27-hx-card" aria-live="polite" hidden></div><script>{js}</script>')

def sections(mats, n, h2):
    out = [css()]
    e = mats["0101"]
    fl = e["flower"]
    # わかること
    know = [
        ("性格と本質", "太陽の星座とデーカン、生まれた日の七十二候、誕生日の数から、その日に生まれた人の長所と気をつけたい点を読み解きます。"),
        ("相性の良い誕生日", "366日の中から、相性の良い誕生日5つと気をつけたい誕生日3つを、太陽の位置の角度と誕生日の数で選んでいます。"),
        ("誕生花・誕生石・誕生色", "その日の誕生花と花言葉、月の誕生石、誕生日石と誕生色に加えて、当サイトで選んだ守護石とラッキーカラーを載せています。"),
        ("同じ誕生日の有名人", "同じ日に生まれた国内外の有名人を、職業と一緒に紹介しています。"),
        ("2027年の運勢", "仕事・恋愛・金運・健康・人間関係の分野別の運勢と、1月〜12月の月別の運勢をグラフと文章で見られます。"),
        ("生まれ年を選ぶと", "九星・四柱推命・宿曜・マヤ暦・ライフパス・動物×色占いなど、生年月日で決まる占いの結果も加わります。"),
    ]
    lis = "".join(f"<li><b>{esc(a)}</b>{esc(b)}</li>" for a, b in know)
    fam = e["famous"]["jp"][0]["name"] if e.get("famous", {}).get("jp") else ""
    sample = (f'<div class="fh-b27-hx-sample"><strong>見本：1月1日生まれ</strong>'
              f'<dl><div><dt>星座</dt><dd>{esc(e["sign"])}（第{e["decan"]}デーカン）</dd></div>'
              f'<div><dt>七十二候</dt><dd>{esc(e["kou"])}</dd></div>'
              f'<div><dt>誕生花</dt><dd>{esc(fl["flower"])}（{esc(fl["hanakotoba"])}）</dd></div>'
              f'<div><dt>誕生石</dt><dd>{esc(e["birthstone_month"])}</dd></div>'
              f'<div><dt>誕生日の数</dt><dd>{esc(e["birthday_number"])}</dd></div>'
              f'<div><dt>2027年の数</dt><dd>{esc(e["py2027"])}</dd></div></dl>'
              f'<p style="margin-top:8px">ページでは、これらの材料から性格・相性・2027年の運勢を読み解いています。'
              f'{"同じ誕生日の有名人には" + esc(fam) + "さんなど。" if fam else ""}<a href="{url("0101")}">1月1日のページを見る →</a></p></div>')
    out.append(f'''<section class="fh-b27-sec" id="b27-know">
  {h2(n, "card", "誕生日のページで読めること")}
  <p>1つの誕生日につき1ページ。どのページにも、次のことがそろっています。</p>
  <ul class="fh-b27-hx-know">{lis}</ul>
  {sample}
  @@KIND@@
</section>''')
    n += 1
    # 誕生日占いと生年月日占い
    rows = [
        ("星座（太陽の位置）・デーカン", "月日", "誕生日ページ"),
        ("七十二候・二十四節気", "月日", "誕生日ページ"),
        ("誕生花・誕生石", "月日", "誕生日ページ"),
        ("誕生日の数・2027年の数（数秘術）", "月日", "誕生日ページ"),
        ("相性の良い誕生日", "月日", "誕生日ページ・相性占い"),
        ("九星（本命星）・干支", "生年月日", "生まれ年を選ぶ・まるごと診断"),
        ("四柱推命・宿曜・マヤ暦", "生年月日", "生まれ年を選ぶ・まるごと診断"),
        ("ライフパス・動物×色占い", "生年月日", "生まれ年を選ぶ・まるごと診断"),
    ]
    tr = "".join(f"<tr><th scope=\"row\">{esc(a)}</th><td>{b}</td><td>{c}</td></tr>" for a, b, c in rows)
    kind = (f'''<h3>誕生日占いと生年月日占いの違い</h3>
  <p>占いには、<b>月日だけで決まるもの</b>（誕生日占い）と、<b>生まれた年も必要なもの</b>（生年月日占い）があります。366日のページは誕生日で占い、ページの中で生まれ年を選ぶと生年月日占いの結果も加わります。1枚のカードにまとめて見たいときは<a href="/seinengappi/">生年月日まるごと診断</a>が便利です。</p>
  <details class="fh-b27-hx-list"><summary>占いと、必要なもの（表）</summary><table class="fh-b27-hx-t"><thead><tr><th scope="col">占い</th><th scope="col">必要なもの</th><th scope="col">見られる場所</th></tr></thead><tbody>{tr}</tbody></table></details>''')
    out[-1] = out[-1].replace("@@KIND@@", kind)
    # 2027年はどんな年
    py = {}
    for k in sorted(mats):
        p = mats[k]["py2027"]
        py.setdefault(str(p), mats[k]["py2027_meaning"])
    order = [x for x in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "11", "22", "33"] if x in py]
    cards = "".join(f'<div><b>{x}</b>{esc(py[x])}</div>' for x in order)
    out.append(f'''<section class="fh-b27-sec" id="b27-2027">
  {h2(n, "calendar-next", "2027年はどんな年？")}
  <p>2027年は<b>丁未（ひのと・ひつじ）</b>の年で、九星では<b>九紫火星</b>が中央に入ります（どちらも立春の2027年2月4日から）。各誕生日のページでは、この年の干支と星の動きに、誕生日ごとの数秘術を重ねて2027年の運勢を出しています。</p>
  <p>数秘術の<b>2027年の数</b>は、2027と誕生日の月日の数字をすべて足し、1けたになるまで足したものです（例：1月1日生まれは 2+0+2+7+1+1＝13 → 1+3＝4）。誕生日ごとに、2027年をどんな年として過ごすかの目安になります。</p>
  <div class="fh-b27-hx-py">{cards}</div>
</section>''')
    n += 1
    # 誕生月ごとの特徴
    mcards = ""
    for m in range(1, 13):
        ks = [k for k in sorted(mats) if int(k[:2]) == m]
        signs = []
        for k in ks:
            if mats[k]["sign"] not in signs:
                signs.append(mats[k]["sign"])
        sek = [mats[k]["sekki"] for k in ks if mats[k]["sekki_day"] not in (None, "None")]
        stone = mats[ks[0]]["birthstone_month"]
        mcards += (f'<div><h3>{m}月生まれ</h3><p>{esc(MONTH_TEXT[m])}</p>'
                   f'<small>星座：{"・".join(signs)}／誕生石：{esc(stone)}{("／節気：" + "・".join(dict.fromkeys(sek))) if sek else ""}</small></div>')
    out.append(f'''<section class="fh-b27-sec" id="b27-month">
  {h2(n, "season", "誕生月ごとの特徴")}
  <p>同じ月に生まれた人は、季節の空気と太陽の星座の移り変わりを共有しています。くわしくは、それぞれの誕生日のページで読めます。</p>
  <div class="fh-b27-hx-months">{mcards}</div>
</section>''')
    n += 1
    # 366日の早見表
    det = ""
    for m in range(1, 13):
        rows = ""
        for d in range(1, DAYS[m] + 1):
            k = f"{m:02d}{d:02d}"
            x = mats[k]
            rows += (f'<tr><th scope="row"><a href="{url(k)}">{m}月{d}日</a></th><td>{esc(x["sign"])}</td>'
                     f'<td>{esc(x["flower"]["flower"])}<small style="color:var(--mute)">（{esc(x["flower"]["hanakotoba"])}）</small></td>'
                     f'<td>{esc(x["kou"])}</td><td>{esc(x["birthday_number"])}</td></tr>')
        det += (f'<details><summary>{m}月生まれ</summary><div class="fh-b27-hx-wrap"><table class="fh-b27-hx-t">'
                f'<caption>{m}月の誕生日の星座・誕生花・七十二候・誕生日の数</caption><thead><tr><th scope="col">誕生日</th><th scope="col">星座</th>'
                f'<th scope="col">誕生花（花言葉）</th><th scope="col">七十二候</th><th scope="col">誕生日の数</th></tr></thead><tbody>{rows}</tbody></table></div></details>')
    out.append(f'''<section class="fh-b27-sec" id="b27-table">
  {h2(n, "flower", "366日の早見表（星座・誕生花・七十二候）")}
  <p>366日それぞれの星座、誕生花と花言葉、七十二候、誕生日の数を月ごとにまとめました。日付を押すと、その誕生日のページが開きます。</p>
  <div class="fh-b27-hx-list">{det}</div>
  <p class="fh-b27-small">星座は1930〜2027年の太陽の位置の平均、七十二候は正午（日本時間）の太陽の位置から決めています。境目の日は年によって前後します。誕生花は日本花普及センターの一覧によります。</p>
</section>''')
    n += 1
    return "\n".join(out), n


def faq(n, h2):
    qa = "".join(f'<details{" open" if i == 0 else ""}><summary>Q. {q}</summary><p>A. {a}</p></details>' for i, (q, a) in enumerate(FAQ))
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    return f'''<section class="fh-b27-sec" id="b27-faq">
  {h2(n, "kokoro", "よくある質問")}
  <div class="fh-b27-hx-qa">{qa}</div>
</section>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'''


def month_js():
    """「誕生日から選ぶ」：月を押した月だけ日のボタンを出す（JSが動かないときは12か月すべて表示＝今までどおり）"""
    return ("<script>(function(){var s=document.getElementById('b27-days');if(!s)return;var ms=s.querySelectorAll('.fh-b27-month'),"
            "ns=s.querySelectorAll('.fh-b27-mnav a');if(!ms.length)return;s.classList.add('fh-b27-hx-mon');"
            "function on(id,scroll){ms.forEach(function(m){m.classList.toggle('is-on',m.id===id);});"
            "ns.forEach(function(a){a.setAttribute('aria-current',a.getAttribute('href')==='#'+id?'true':'false');});"
            "if(scroll){var t=document.getElementById(id);if(t)t.scrollIntoView({behavior:'smooth',block:'nearest'});}}"
            "ns.forEach(function(a){a.addEventListener('click',function(e){e.preventDefault();on(a.getAttribute('href').slice(1),true);});});"
            "var h=location.hash.match(/^#b27-m(\\d\\d)$/),m=h?h[1]:('0'+(new Date().getMonth()+1)).slice(-2);on('b27-m'+m,false);})();</script>")
