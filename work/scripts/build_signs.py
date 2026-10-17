"""12星座の記事（/aries/ など。投稿 2396〜2409）を 2027年版に作り直す（2026-10-17 本人「1（作り直す）。誕生日占いとの差別化はしっかり」）。
誕生日占い（366日）＝誕生日の太陽の度数への角度で見る個人の運勢。
12星座ページ＝天体が星座から数えて何番目の部屋にいるか（ソーラーサイン・ハウス）で見る星座全体の天気図＋12星座の比べっこ＋月のカレンダー。
数字はすべて calc_signs_2027.py（data/signs_2027.json）と calc_planets_2027.py（data/planets_2027.json）。文章は text/signs/<en>.json。
広告：ラッキーカラーのマグ・ラッキーアイテム5つ・電話占い（build_sign_ads.py の部品をそのまま使う）。
使い方：python build_signs.py 2026-10-17 [aries ...] → out/signs/<en>.html と out/sample/signs/<en>.html"""
import datetime as dt, html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_hub import OUT, WORK, shell  # noqa: E402
from build_sign_ads import SIGN_COLORS  # noqa: E402

DATA = os.path.join(WORK, "data")
EN = {"牡羊座": "aries", "牡牛座": "taurus", "双子座": "gemini", "蟹座": "cancer", "獅子座": "leo", "乙女座": "virgo",
      "天秤座": "libra", "蠍座": "scorpio", "射手座": "sagittarius", "山羊座": "capricorn", "水瓶座": "aquarius", "魚座": "pisces"}
JA = {"aries": "おひつじ座", "taurus": "おうし座", "gemini": "ふたご座", "cancer": "かに座", "leo": "しし座", "virgo": "おとめ座",
      "libra": "てんびん座", "scorpio": "さそり座", "sagittarius": "いて座", "capricorn": "やぎ座", "aquarius": "みずがめ座", "pisces": "うお座"}
GLYPH = {"aries": "♈", "taurus": "♉", "gemini": "♊", "cancer": "♋", "leo": "♌", "virgo": "♍", "libra": "♎", "scorpio": "♏",
         "sagittarius": "♐", "capricorn": "♑", "aquarius": "♒", "pisces": "♓"}
ELEM = {"aries": "火", "leo": "火", "sagittarius": "火", "taurus": "地", "virgo": "地", "capricorn": "地",
        "gemini": "風", "libra": "風", "aquarius": "風", "cancer": "水", "scorpio": "水", "pisces": "水"}
RULER = {"aries": "火星", "taurus": "金星", "gemini": "水星", "cancer": "月", "leo": "太陽", "virgo": "水星", "libra": "金星",
         "scorpio": "冥王星（古くは火星）", "sagittarius": "木星", "capricorn": "土星", "aquarius": "天王星（古くは土星）", "pisces": "海王星（古くは木星）"}
EC = {"火": "#E0603A", "地": "#7FA05A", "風": "#E2C24A", "水": "#4A8FD0"}
NUMBERS = {"aries": "1, 9, 17", "taurus": "2, 6, 24", "gemini": "3, 5, 21", "cancer": "4, 7, 22", "leo": "1, 9, 19", "virgo": "5, 8, 17",
           "libra": "6, 11, 24", "scorpio": "9, 18, 22", "sagittarius": "3, 14, 27", "capricorn": "4, 8, 21", "aquarius": "7, 22, 31", "pisces": "3, 12, 27"}
FIELDS = ["総合", "恋愛", "仕事", "金運", "健康"]
FCOL = {"総合": "#F2C14E", "恋愛": "#F28CA8", "仕事": "#6FB3E8", "金運": "#E8B04A", "健康": "#7CC98B"}
PLAN_COL = {"木星": "#E8B04A", "土星": "#9C8FD0", "火星": "#E0603A", "金星": "#F28CA8"}
POSTS = {"aries": 2396, "taurus": 2399, "gemini": 2400, "cancer": 2401, "leo": 2402, "virgo": 2403, "libra": 2404, "scorpio": 2405,
         "sagittarius": 2406, "capricorn": 2407, "aquarius": 2408, "pisces": 2409}


def esc(s):
    return html.escape(str(s), quote=True)


CSS = """<style id="fh-b27-sg-css">
.fh-b27[data-fh-page="sign"]{--ink:#EEF0F7;--sub:#C9CDE0;--mute:#9DA3BE;--paper:#161A2C;--deep:#10142A;--line:#3B4266;--gold:#F2C14E;--el:#F2C14E}
.fh-b27[data-fh-page="sign"] a{color:#F5CF6E}
.fh-b27[data-fh-page="sign"] .fh-b27-note{background-color:var(--paper);background-image:radial-gradient(circle at 85% 0%,color-mix(in srgb,var(--el) 22%,transparent),transparent 40%),radial-gradient(circle at 0% 100%,rgba(120,140,255,.12),transparent 45%)}
.fh-b27-sg-glyph{flex:0 0 auto;width:118px;height:118px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:66px;color:#10142A;
 background:radial-gradient(circle at 35% 30%,#fff,var(--el));box-shadow:0 0 0 6px rgba(255,255,255,.08),0 0 40px color-mix(in srgb,var(--el) 60%,transparent);margin:6px}
.fh-b27-sg-chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.fh-b27-sg-chips span{border:1px solid var(--line);border-radius:999px;padding:2px 12px;font-size:13px;color:var(--sub);background:rgba(255,255,255,.04)}
.fh-b27-sg-why{border:1.5px solid color-mix(in srgb,var(--el) 60%,transparent);border-radius:12px;background:linear-gradient(135deg,color-mix(in srgb,var(--el) 16%,transparent),rgba(255,255,255,.02));padding:16px 18px}
.fh-b27-sg-why b.h{display:block;font-size:18px;color:var(--gold);margin-bottom:4px}
.fh-b27 .fh-b27-sg-why ul{list-style:none;padding:0;margin:10px 0 4px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.fh-b27 .fh-b27-sg-why li{margin:0;background:rgba(0,0,0,.25);border-radius:8px;padding:10px 12px;font-size:13.5px;line-height:1.7}
.fh-b27-sg-why li::before{content:none}.fh-b27-sg-why li b{display:block;color:var(--ink)}
.fh-b27-sg-catch{font-size:21px;font-weight:800;color:var(--gold);margin:0 0 8px}
.fh-b27-sg-kw{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:12px 0}
.fh-b27-sg-kw div{background:#FFF8E6;color:#2A2416;border-radius:10px;padding:10px 12px;font-size:13.5px;line-height:1.7}
.fh-b27-sg-kw b{display:block;font-size:17px;color:#9A5A12}
.fh-b27-sg-chart{background:rgba(0,0,0,.25);border:1px solid var(--line);border-radius:12px;padding:12px}
.fh-b27-sg-tabs{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px}
.fh-b27-sg-tabs button{min-height:36px;border:1px solid var(--line);border-radius:999px;background:transparent;color:var(--sub);font:inherit;font-size:13.5px;font-weight:700;padding:0 14px;cursor:pointer}
.fh-b27-sg-tabs button[aria-pressed="true"]{background:var(--c);border-color:var(--c);color:#10142A}
.fh-b27-sg-chart svg{display:block;width:100%;height:auto}
.fh-b27-sg-chart .ln{fill:none;stroke-width:3;stroke-linejoin:round;stroke-linecap:round;transition:opacity .3s}
.fh-b27-sg-chart .ln.off,.fh-b27-sg-chart .dt.off{opacity:0}
.fh-b27-sg-chart text{fill:#C9CDE0;font-size:11px}
.fh-b27-sg-tl{display:grid;grid-template-columns:52px minmax(0,1fr);gap:4px 6px;font-size:11.5px;align-items:center}
.fh-b27-sg-tl .p{color:var(--sub);font-weight:700}
.fh-b27-sg-tl .bar{position:relative;height:34px;background:rgba(255,255,255,.04);border-radius:6px}
.fh-b27-sg-tl .bar.mh{height:18px;background:none}.fh-b27-sg-tl .bar.mh span{position:absolute;top:0;color:var(--mute);font-size:11px}
.fh-b27-sg-tl .seg{position:absolute;top:0;bottom:0;border-radius:5px;color:#10142A;font-weight:700;font-size:11px;line-height:1.25;padding:2px 4px;overflow:hidden;box-shadow:inset -1px 0 0 rgba(0,0,0,.35);display:flex;align-items:center}
.fh-b27-sg-months{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.fh-b27-sg-months div{background:rgba(255,255,255,.04);border:1px solid var(--line);border-left:6px solid var(--c);border-radius:8px;padding:10px 12px;font-size:14px;line-height:1.8}
.fh-b27-sg-months b{font-size:16px}.fh-b27-sg-months small{float:right;color:var(--mute);font-size:12px}
.fh-b27-sg-months i{font-style:normal;display:inline-block;min-width:2.4em;text-align:center;border-radius:6px;background:var(--c);color:#10142A;font-weight:800;margin-left:6px;font-size:12.5px}
.fh-b27-sg-cal{background:#F7F5FF;color:#24203A;border-radius:12px;padding:12px}
.fh-b27-sg-cal .hd{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:8px}
.fh-b27-sg-cal .hd b{font-size:18px}
.fh-b27-sg-cal .hd button{min-height:38px;min-width:44px;border:1px solid #C9C2E8;border-radius:8px;background:#fff;color:#3B3466;font:inherit;font-weight:700;cursor:pointer}
.fh-b27-sg-cal table{width:100%;border-collapse:collapse;table-layout:fixed}
.fh-b27-sg-cal th{font-size:12px;color:#6A6290;padding:4px 0;background:none}
.fh-b27 .fh-b27-sg-cal td{border:1px solid #E3DEF5;height:64px;vertical-align:top;padding:3px 4px;font-size:12px;background:#fff;color:#24203A}
.fh-b27 .fh-b27-sg-cal td.g2{background:#FFE29A!important}.fh-b27 .fh-b27-sg-cal td.g1{background:#FFF4CF!important}.fh-b27 .fh-b27-sg-cal td.b{background:#E6E8F2!important}
.fh-b27-sg-cal td.today{outline:3px solid #7A5CFF;outline-offset:-3px}
.fh-b27-sg-cal td b{display:block;font-size:13px}.fh-b27-sg-cal td span{display:block;font-size:16px;line-height:1.2}.fh-b27-sg-cal td small{display:block;font-size:10px;color:#6A6290;line-height:1.3}
.fh-b27-sg-cal .lg{display:flex;flex-wrap:wrap;gap:10px;font-size:12px;margin-top:8px;color:#4A4470}
.fh-b27-sg-fields{display:grid;grid-template-columns:minmax(0,1fr);gap:8px}
.fh-b27-sg-fields div{border:1px solid var(--line);border-top:5px solid var(--c);border-radius:8px;padding:10px 14px;background:rgba(255,255,255,.03);font-size:14.5px;line-height:1.85}
.fh-b27-sg-fields b{font-size:17px;color:var(--c)}.fh-b27-sg-fields small{display:block;color:var(--mute);font-size:12.5px}
.fh-b27-sg-rank{overflow-x:auto}.fh-b27-sg-rank table{border-collapse:collapse;min-width:640px;width:100%;font-size:12.5px;text-align:center}
.fh-b27-sg-rank th,.fh-b27-sg-rank td{border-bottom:1px solid var(--line);padding:5px 3px;background:none;color:var(--sub)}
.fh-b27-sg-rank td.me{background:var(--el);color:#10142A;font-weight:800;border-radius:4px}
.fh-b27-sg-two{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.fh-b27-sg-two>div{background:rgba(255,255,255,.04);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.fh-b27 .fh-b27-sg-two ul{margin:6px 0 0;padding-left:1.1em}.fh-b27 .fh-b27-sg-two li{margin:3px 0;font-size:14px}
.fh-b27-sg-days{display:flex;flex-wrap:wrap;gap:6px}
.fh-b27-sg-days a{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:4px 10px;font-size:13px;text-decoration:none;background:rgba(255,255,255,.04)}
.fh-b27-sg-tips{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.fh-b27-sg-tips div{background:#FFF8E6;color:#2A2416;border-radius:10px;padding:10px 12px;font-size:13.5px;line-height:1.7}.fh-b27-sg-tips b{display:block;color:#9A5A12;font-size:15.5px}
.fh-b27-sg-qa details{border-bottom:1px solid var(--line);padding:8px 2px}.fh-b27-sg-qa summary{cursor:pointer;font-weight:700}.fh-b27-sg-qa p{margin-top:6px;font-size:14.5px}
.fh-b27-sg-lk{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.fh-b27-sg-lk div{background:rgba(255,255,255,.04);border:1px solid var(--line);border-radius:10px;padding:10px 12px}
.fh-b27-sg-lk b{display:block;color:var(--gold);font-size:13px}.fh-b27-sg-lk span{font-size:15px}
.fh-b27[data-fh-page="sign"] .om-ad{margin:12px 0}
@media (max-width:640px){.fh-b27-sg-kw,.fh-b27-sg-tips,.fh-b27-sg-two,.fh-b27-sg-months,.fh-b27-sg-lk{grid-template-columns:1fr}.fh-b27 .fh-b27-sg-why ul{grid-template-columns:1fr}
 .fh-b27-sg-glyph{width:84px;height:84px;font-size:46px}.fh-b27-sg-tl .seg{font-size:9.5px;padding:1px 2px}.fh-b27-sg-tl .bar.mh span{font-size:9px}
 .fh-b27-sg-cal td{height:54px;padding:2px}.fh-b27-sg-cal td small{display:none}}
</style>"""

JS = r"""(function(){var root=document.querySelector('.fh-b27[data-fh-page="sign"]');if(!root)return;
var bs=root.querySelectorAll('.fh-b27-sg-tabs button');bs.forEach(function(b){b.addEventListener('click',function(){var on=b.getAttribute('aria-pressed')!=='true';b.setAttribute('aria-pressed',on?'true':'false');
 root.querySelectorAll('[data-f="'+b.dataset.f+'"]').forEach(function(e){e.classList.toggle('off',!on)});});});
var C=__CAL__,PH=__PH__,cal=root.querySelector('.fh-b27-sg-cal');if(!cal)return;var tb=cal.querySelector('tbody'),ti=cal.querySelector('.hd b');
var now=new Date(),m=(now.getFullYear()===2027)?now.getMonth()+1:1;var WHY={0:'月があなたの星座に',4:'月が同じエレメントに',2:'月が相性のいい星座に',1:'月がとなりの星座に',5:'月が少し遠い星座に',3:'月が直角の星座に',6:'月が向かい側に'};
function draw(){ti.textContent='2027年'+m+'月';var first=new Date(2027,m-1,1).getDay(),days=new Date(2027,m,0).getDate(),h='<tr>',i;for(i=0;i<first;i++)h+='<td></td>';
 for(var d=1;d<=days;d++){var k='2027-'+(m<10?'0':'')+m+'-'+(d<10?'0':'')+d,x=C[k];var cls=x[2]===0||x[2]===4?'g2':(x[2]===2?'g1':(x[2]===3||x[2]===6?'b':''));
  if(now.getFullYear()===2027&&now.getMonth()+1===m&&now.getDate()===d)cls+=' today';var p=PH[k]?(PH[k]==='新月'?'● 新月':'○ 満月'):'';
  h+='<td class="'+cls+'"><b>'+d+'</b><span>'+x[0]+'</span><small>'+x[1]+(p?'<br>'+p:'')+'</small></td>';if((first+d)%7===0&&d<days)h+='</tr><tr>';}
 h+='</tr>';tb.innerHTML=h;}
cal.querySelector('[data-mv="-1"]').addEventListener('click',function(){m=m>1?m-1:12;draw();});cal.querySelector('[data-mv="1"]').addEventListener('click',function(){m=m<12?m+1:1;draw();});draw();})();"""


def chart_svg(months):
    W, H, L, R, T, B = 640, 240, 34, 12, 14, 30
    x = lambda i: L + (W - L - R) * i / 11  # noqa: E731
    y = lambda v: T + (H - T - B) * (100 - v) / 70  # 30〜100
    g = []
    for v in (40, 60, 80, 100):
        g.append(f'<line x1="{L}" x2="{W - R}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="rgba(255,255,255,.1)"/><text x="4" y="{y(v) + 4:.1f}">{v}</text>')
    for i in range(12):
        g.append(f'<text x="{x(i):.1f}" y="{H - 8}" text-anchor="middle">{i + 1}月</text>')
    for f in FIELDS:
        pts = " ".join(f"{x(i):.1f},{y(months[str(i + 1)][f]):.1f}" for i in range(12))
        off = "" if f == "総合" else " off"
        g.append(f'<polyline class="ln{off}" data-f="{f}" stroke="{FCOL[f]}" points="{pts}"/>')
        for i in range(12):
            v = months[str(i + 1)][f]
            g.append(f'<circle class="dt{off}" data-f="{f}" cx="{x(i):.1f}" cy="{y(v):.1f}" r="4" fill="{FCOL[f]}"><title>{i + 1}月 {f} {v}</title></circle>')
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="2027年の月ごとの運勢グラフ">{"".join(g)}</svg>'


def timeline(houses):
    """1年を横棒にして、天体がどの部屋にいるかを日数どおりの長さで描く"""
    y0 = dt.date(2027, 1, 1)
    hd = '<div class="fh-b27-sg-tl"><div class="p"></div><div class="bar mh">' + "".join(
        f'<span style="left:{(dt.date(2027, m, 1) - y0).days / 365 * 100:.2f}%">{m}月</span>' for m in range(1, 13)) + "</div>"
    rows = []
    for p in ("木星", "土星", "火星", "金星"):
        segs = []
        for s in houses[p]:
            a = (dt.date.fromisoformat(s["from"]) - y0).days
            b = (dt.date.fromisoformat(s["to"]) - y0).days + 1
            w = (b - a) / 365 * 100
            lab = f'{s["house"]}番目' + (f'｜{esc(s["theme"].split("・")[0])}' if w > 14 else "")
            segs.append(f'<span class="seg" style="left:{a / 365 * 100:.2f}%;width:{w:.2f}%;background:{PLAN_COL[p]}" title="{esc(s["from"])}〜{esc(s["to"])}：{s["house"]}番目の部屋（{esc(s["theme"])}）">{lab}</span>')
        rows.append(f'<div class="p">{p}</div><div class="bar">{"".join(segs)}</div>')
    return hd + "".join(rows) + "</div>"


def build(en, sample, updated):
    S = json.load(open(os.path.join(DATA, "signs_2027.json"), encoding="utf-8"))
    B = json.load(open(os.path.join(DATA, "base_366.json"), encoding="utf-8"))
    A = json.load(open(os.path.join(OUT, "sign_ads.json"), encoding="utf-8"))
    T = json.load(open(os.path.join(WORK, "text", "signs", f"{en}.json"), encoding="utf-8"))
    sg = [k for k, v in EN.items() if v == en][0]
    D = S["signs"][sg]
    M = D["months"]
    ja = JA[en]
    el = ELEM[en]
    days = sorted([k for k, v in B.items() if v["sign"] == sg], key=lambda k: (k < "0601", k) if sg == "山羊座" else k)
    rng = f'{int(days[0][:2])}月{int(days[0][2:])}日〜{int(days[-1][:2])}月{int(days[-1][2:])}日'
    H = []
    a = H.append
    a(CSS)
    a(f'<div class="fh-b27" data-fh-page="sign" style="--el:{EC[el]}">\n<div class="fh-b27-note">')
    best = max(range(1, 13), key=lambda m: M[str(m)]["総合"])
    a(f'''<header class="fh-b27-hero">
  <div class="fh-b27-sg-glyph" aria-hidden="true">{GLYPH[en]}&#xFE0E;</div>
  <div class="fh-b27-hero-body">
    <span class="fh-b27-tape">星座占い 2027</span>
    <p class="fh-b27-title">{ja}の2027年の運勢</p>
    <p class="fh-b27-lead">{esc(T["lead"])}</p>
    <div class="fh-b27-sg-chips"><span>{rng}生まれ</span><span>{el}のエレメント</span><span>守護星：{esc(RULER[en])}</span><span>2027年のピーク：{best}月</span></div>
  </div>
</header>''')
    items = [("b27-sg-year", "2027年の全体運"), ("b27-sg-graph", "運勢グラフ"), ("b27-sg-stars", "2027年の星の動き"), ("b27-sg-month", "月ごとの運勢"),
             ("b27-sg-cal", "ラッキーデーのカレンダー"), ("b27-sg-field", "恋愛・仕事・お金・健康"), ("b27-sg-rank", "12星座の順位"),
             ("b27-sg-char", "性格と相性"), ("b27-sg-lucky", "ラッキーカラーとアイテム"), ("b27-sg-days", "誕生日ごとの運勢"), ("b27-sg-faq", "よくある質問")]
    a('<nav class="fh-b27-toc" aria-label="目次"><strong>このページの内容</strong><ol>' + "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in items) + "</ol></nav>")
    n = [1]

    def h2(t):
        s = f'<h2><span class="fh-b27-n">{n[0]}</span><span>{t}</span></h2>'
        n[0] += 1
        return s
    a(f'''<div class="fh-b27-sg-why"><b class="h">星座占いと誕生日占いのちがい</b>
  <p>このページは、天体が{ja}から数えて<b>何番目の部屋（ハウス）</b>にいるかで1年を読む「星座全体の天気図」です。雑誌の星座占いと同じ考え方で、{ja}の人みんなに共通する流れがわかります。</p>
  <ul><li><b>星座占い（このページ）</b>星座の30日分をまとめて、2027年の追い風の時期・12星座の中での順位・月の巡りのカレンダーを出します。</li>
  <li><b>誕生日占い（366日）</b>生まれた日の太陽の位置に星が作る角度で、その日生まれの人だけの運勢を出します。同じ{ja}でも、誕生日によって山場の月がちがいます。</li></ul>
  <p class="fh-b27-small">あなたの誕生日の運勢は<a href="#b27-sg-days">このページの下の日付</a>から開けます。</p></div>''')
    kw = "".join(f'<div><b>{esc(k)}</b>{esc(v)}</div>' for k, v in T["keywords"])
    a(f'''<section class="fh-b27-sec" id="b27-sg-year">
  {h2("2027年の全体運")}
  <p class="fh-b27-sg-catch">{esc(T["catch"])}</p>
  <p>{esc(T["year"])}</p>
  <div class="fh-b27-sg-kw">{kw}</div>
</section>''')
    tabs = "".join(f'<button type="button" data-f="{f}" aria-pressed="{"true" if f == "総合" else "false"}" style="--c:{FCOL[f]}">{f}</button>' for f in FIELDS)
    a(f'''<section class="fh-b27-sec" id="b27-sg-graph">
  {h2(f"{ja}の運勢グラフ（2027年）")}
  <p>月ごとの追い風の強さを、総合・恋愛・仕事・金運・健康で見られます。ボタンを押すと線を重ねられます。点は12星座×12か月の中での位置（35〜95）なので、ほかの星座のページの点と比べることもできます。</p>
  <div class="fh-b27-sg-chart"><div class="fh-b27-sg-tabs">{tabs}</div>{chart_svg(M)}</div>
  <p class="fh-b27-small">毎日12時の太陽・水星・金星・火星・木星・土星の星座から、{ja}との角度（同じ星座・120度は追い風、90度・180度は向かい風）と、天体が入る部屋（恋愛なら5番目と7番目など）で点を出し、月ごとに平均しています。</p>
</section>''')
    a("<!--Ads1-->")
    a(f'''<section class="fh-b27-sec" id="b27-sg-stars">
  {h2("2027年の星の動きと、" + ja + "の部屋")}
  <p>天体が{ja}から数えて何番目の部屋にいるかの1年の地図です。部屋ごとにテーマがあり、そこに入った天体の性質がそのテーマに影響します。</p>
  {timeline(D["houses"])}
  <h3>木星（幸運と拡大の星）</h3><p>{esc(T["jupiter"])}</p>
  <h3>土星（試練と成長の星）</h3><p>{esc(T["saturn"])}</p>
  <p class="fh-b27-small">2027年は天王星が1年中ふたご座、海王星がおひつじ座、冥王星がみずがめ座にいます。部屋の区切りは毎日12時（日本時間）の位置で見ています。</p>
</section>''')
    mc = []
    for m in range(1, 13):
        v = M[str(m)]["総合"]
        c = "#F2C14E" if v >= 80 else ("#7CC98B" if v >= 60 else ("#9DA3BE" if v >= 45 else "#8E7FBF"))
        mc.append(f'<div style="--c:{c}"><b>{m}月</b><i>{v}</i><small>12星座中{S["rank"][str(m)].index(sg) + 1}位</small><br>{esc(T["months"][str(m)])}</div>')
    a(f'''<section class="fh-b27-sec" id="b27-sg-month">
  {h2("月ごとの運勢")}
  <div class="fh-b27-sg-months">{"".join(mc)}</div>
</section>''')
    cal = {d: [mk, f"月：{ms[:-1] if ms.endswith('座') else ms}", k] for d, mk, ms, k in D["moon"]}
    ph = {p["date"]: p["kind"] for p in S["phases"]}
    g2 = sum(1 for x in D["moon"] if x[3] in (0, 4))
    a(f'''<section class="fh-b27-sec" id="b27-sg-cal">
  {h2("ラッキーデーのカレンダー（月の巡り）")}
  <p>月はおよそ2日半ごとに星座を移り、1か月で12星座をひと回りします。月が{ja}や同じ{el}のエレメントの星座にいる日は気持ちが乗りやすい「ラッキーデー（◎）」、向かい側や直角の星座にいる日は無理をしない「ひと休みの日（△）」です。毎日の調子の波を見る、バイオリズムのような使い方ができます。2027年の◎は{g2}日あります。</p>
  <div class="fh-b27-sg-cal"><div class="hd"><button type="button" data-mv="-1" aria-label="前の月">‹</button><b></b><button type="button" data-mv="1" aria-label="次の月">›</button></div>
  <table><thead><tr><th>日</th><th>月</th><th>火</th><th>水</th><th>木</th><th>金</th><th>土</th></tr></thead><tbody></tbody></table>
  <div class="lg"><span>◎ ラッキーデー</span><span>○ 相性のいい日</span><span>・ ふつうの日</span><span>△ ひと休みの日</span><span>● 新月　○ 満月</span></div></div>
  <p class="fh-b27-small">毎日12時（日本時間）の月の星座で見ています。月が星座を移る日は、時間帯によって印がずれることがあります。</p>
</section>''')
    fc = []
    for f, key in (("恋愛", "恋愛"), ("仕事", "仕事"), ("金運", "金運"), ("健康", "健康"), ("人間関係", None)):
        if key:
            top = sorted(range(1, 13), key=lambda m: -M[str(m)][key])[:3]
            sub = "追い風の月：" + "・".join(f"{m}月" for m in sorted(top))
        else:
            sub = "人との縁は、金星と木星が入る部屋で読みます"
        fc.append(f'<div style="--c:{FCOL.get(key or "総合")}"><b>{f}運</b><small>{sub}</small>{esc(T["fields"][f])}</div>')
    a(f'''<section class="fh-b27-sec" id="b27-sg-field">
  {h2("恋愛・仕事・お金・健康・人間関係")}
  <div class="fh-b27-sg-fields">{"".join(fc)}</div>
</section>''')
    a(A["signs"][en]["phone"].replace('<div class="fh-b27 om-ad">', '<div class="om-ad">'))
    hd = "".join(f"<th>{m}月</th>" for m in range(1, 13))
    rows = []
    for r in range(12):
        tds = "".join(f'<td class="{"me" if S["rank"][str(m)][r] == sg else ""}">{JA[EN[S["rank"][str(m)][r]]][:-1]}</td>' for m in range(1, 13))
        rows.append(f"<tr><th>{r + 1}位</th>{tds}</tr>")
    a(f'''<section class="fh-b27-sec" id="b27-sg-rank">
  {h2("12星座の順位（2027年・月ごと）")}
  <p>総合の点で並べた、月ごとの12星座の順位です。{ja}は色のついた欄です。</p>
  <div class="fh-b27-sg-rank"><table><thead><tr><th></th>{hd}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>
</section>''')
    gd = "".join(f"<li><b>{JA[EN[s]]}</b>：{esc(t)}</li>" for s, t in T["compat"]["good"])
    cr = "".join(f"<li><b>{JA[EN[s]]}</b>：{esc(t)}</li>" for s, t in T["compat"]["care"])
    a(f'''<section class="fh-b27-sec" id="b27-sg-char">
  {h2(ja + "の性格と相性")}
  <p>{esc(T["personality"])}</p>
  <div class="fh-b27-sg-two"><div><b>長所</b><ul>{"".join(f"<li>{esc(x)}</li>" for x in T["strengths"])}</ul></div><div><b>気をつけたいところ</b><ul>{"".join(f"<li>{esc(x)}</li>" for x in T["cautions"])}</ul></div></div>
  <h3>相性のいい星座・コツがいる星座</h3>
  <div class="fh-b27-sg-two"><div><b>相性のいい星座</b><ul>{gd}</ul></div><div><b>付き合い方にコツがいる星座</b><ul>{cr}</ul></div></div>
  <p class="fh-b27-small">二人の誕生日で相性を見るなら<a href="/compatibility/">誕生日相性占い</a>へ。</p>
</section>''')
    a(f'''<section class="fh-b27-sec" id="b27-sg-lucky">
  {h2(ja + "のラッキーカラーとアイテム")}
  <div class="fh-b27-sg-lk"><div><b>ラッキーカラー</b><span>{esc(SIGN_COLORS[en])}</span></div><div><b>ラッキーナンバー</b><span>{esc(NUMBERS[en])}</span></div></div>
  {A["signs"][en]["colors"].replace('<div class="fh-b27 om-ad">', '<div class="om-ad">')}
  {A["signs"][en]["items"].replace('<div class="fh-b27 om-ad">', '<div class="om-ad">')}
</section>''')
    tips = "".join(f'<div><b>{esc(h)}</b>{esc(t)}</div>' for h, t in T["tips"])
    dl = "".join(f'<a href="/366uranai/{k[:2]}-{k[2:]}/">{int(k[:2])}/{int(k[2:])}</a>' for k in days)
    a(f'''<section class="fh-b27-sec" id="b27-sg-days">
  {h2(ja + "の誕生日ごとの運勢")}
  <p>同じ{ja}でも、生まれた日の太陽の位置によって、2027年の山場の月や得意なことがちがいます。日付を押すと、その日生まれの人の2027年の運勢（12か月・相性・ラッキーアイテム）が開きます。</p>
  <div class="fh-b27-sg-days">{dl}</div>
  <h3>2027年を過ごすコツ</h3>
  <div class="fh-b27-sg-tips">{tips}</div>
</section>''')
    qa = "".join(f'<details{" open" if i == 0 else ""}><summary>Q. {esc(q)}</summary><p>A. {esc(x)}</p></details>' for i, (q, x) in enumerate(T["faq"]))
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in T["faq"]]}
    a(f'''<section class="fh-b27-sec" id="b27-sg-faq">
  {h2("よくある質問")}
  <div class="fh-b27-sg-qa">{qa}</div>
</section>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<section class="fh-b27-sec"><div class="fh-b27-links">
  <a href="/star/"><b>12星座占い一覧 →</b><small>12星座の期間と性格・早見表</small></a>
  <a href="/366uranai/"><b>366日の誕生日占い →</b><small>生まれた日の2027年の運勢</small></a>
  <a href="/hoshi/"><b>星のこよみ →</b><small>新月・満月と星の動き</small></a>
  <a href="/compatibility/"><b>誕生日相性占い →</b><small>二人の誕生日で相性を見る</small></a>
</div></section>''')
    up = dt.date.fromisoformat(updated)
    a(f'<p class="fh-b27-foot">天体の位置・部屋・月の巡り・点数は、このサイトで計算したものです（Swiss Ephemeris・日本時間）。文章はこのサイトで書いたものです。占いは楽しみと気づきのためにお読みください。<br>最終更新日：{up.year}年{up.month}月{up.day}日／<a href="/about/">この記事の作成方針について</a></p>')
    a("</div>\n</div>")
    js = JS.replace("__CAL__", json.dumps(cal, ensure_ascii=False, separators=(",", ":"))).replace("__PH__", json.dumps(ph, ensure_ascii=False))
    a(f"<script>document.addEventListener('DOMContentLoaded',function(){{{js}}});</script>")
    title = f"{ja}の2027年の運勢｜運勢グラフ・ラッキーデーのカレンダー・12星座の順位"
    desc = f"{ja}（{rng}生まれ）の2027年の運勢を、星の位置から計算。月ごとの運勢グラフ、木星・土星が入る部屋、ラッキーデーのカレンダー、12星座の順位、恋愛・仕事・金運、性格と相性、ラッキーアイテムまで。"
    body = "\n".join(H)
    out = shell(title, desc, f"/{en}/", body, sample, ("fh-b27.js",))
    assert "！" not in out
    return out, title, desc


def main():
    updated = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    targets = sys.argv[2:] or [en for en in JA if os.path.exists(os.path.join(WORK, "text", "signs", f"{en}.json"))]
    os.makedirs(os.path.join(OUT, "signs"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "sample", "signs"), exist_ok=True)
    meta = {}
    for en in targets:
        for sample, path in ((False, os.path.join(OUT, "signs", f"{en}.html")), (True, os.path.join(OUT, "sample", "signs", f"{en}.html"))):
            out, title, desc = build(en, sample, updated)
            open(path, "w", encoding="utf-8").write(out)
        meta[en] = {"post": POSTS[en], "title": title, "desc": desc}
        print("→", en)
    mp = os.path.join(OUT, "signs", "meta.json")
    old = json.load(open(mp, encoding="utf-8")) if os.path.exists(mp) else {}
    old.update(meta)
    json.dump(old, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
