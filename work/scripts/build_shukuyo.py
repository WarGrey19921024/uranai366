"""宿曜占星術のページ（新しい固定ページ /shukuyo/）を作る（2026-10-16 本人の決定：計算で強みのある「宿曜占星術」月1万〜10万回の検索に入る）。
本命宿の計算は共通JS（fh-b27.js の FHB27Calc.shuku＝旧暦の月日＋『宿曜経』の各月1日の宿）をそのまま使う＝366日・まるごと診断と同じ結果。
27宿の性格と三九の秘法は work/knowledge/06_宿曜.md（このサイトの言葉）から。
使い方: python work/scripts/build_shukuyo.py [最終更新日]
"""
import datetime as dt, html, json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_hub import OUT, WORK, shell  # noqa: E402

import shukuyo_texts as SKT  # noqa: E402
import aff_extra  # noqa: E402
URL = "/shukuyo/"
KNOW = os.path.join(WORK, "knowledge", "06_宿曜.md")
SCRIPTS = ("fh-b27-setsuiri.js", "fh-b27-kyureki.js", "fh-b27.js")
ORDER = ['昴', '畢', '觜', '参', '井', '鬼', '柳', '星', '張', '翼', '軫', '角', '亢', '氐', '房', '心', '尾', '箕', '斗', '女', '虚', '危', '室', '壁', '奎', '婁', '胃']
MONTH_START = {1: '室', 2: '奎', 3: '胃', 4: '畢', 5: '参', 6: '鬼', 7: '張', 8: '角', 9: '氐', 10: '心', 11: '斗', 12: '虚'}
REL_D = {0: "命", 9: "業", 18: "胎"}
for base in (0, 9, 18):
    for i, r in enumerate(["栄", "衰", "安", "危", "成", "壊", "友", "親"], 1):
        REL_D[base + i] = r
PAIR = {"命": "命", "業": "業胎", "胎": "業胎", "栄": "栄親", "親": "栄親", "衰": "友衰", "友": "友衰", "安": "安壊", "壊": "安壊", "危": "危成", "成": "危成"}
FAQ = [
    ("宿曜占星術とは何ですか。", "月の通り道を27の宿に分け、生まれた日の月がどの宿にあったかで性格や相性を読む占いです。もとになった『宿曜経』は平安時代に空海が日本へ伝えたとされ、宿曜道として受け継がれてきました。"),
    ("本命宿はどうやって決まりますか。", "生年月日を旧暦に直し、旧暦の月ごとに決まっている「1日の宿」から日数だけ進めて決めます。このページでは、天文計算で作った1900〜2030年の旧暦の表を使って計算しています。"),
    ("ほかのサイトと本命宿が違うのはなぜですか。", "旧暦の作り方や、月の位置そのもので決める方式など、計算方法が流派やサイトによって違うためです。このサイトは『宿曜経』の「各月1日の宿」から数える方式で、旧暦は国立天文台と同じ決まり（日本時間・定気）で作っています。"),
    ("三九の秘法とは何ですか。", "自分の宿から相手の宿までの距離で、二人の関係を「命・業胎・栄親・友衰・安壊・危成」の6つに分ける相性の読み方です。同じ関係でも、近距離・中距離・遠距離で関わり方の強さが変わるとされます。"),
    ("安壊の相性は避けたほうがいいですか。", "安壊は強く惹かれ合う一方で、振り回されやすい関係とされます。避けるべき相手という意味ではなく、距離感とお互いの役割を意識すると、大きく成長できる関係になります。"),
    ("生まれた時刻は必要ですか。", "必要ありません。このページは生年月日だけで本命宿を出します。旧暦の月が変わる日（新月の日）の前後に生まれた人は、時刻によって宿が変わることがあります。"),
]


def esc(s):
    return html.escape(str(s), quote=True)


def md_rows(path, head):
    t = open(path, encoding="utf-8").read()
    i = t.index(head)
    rows = []
    for line in t[i:].splitlines()[1:]:
        if line.startswith("### ") or line.startswith("## "):
            break
        if line.startswith("|") and not re.match(r"^\|[-| ]+\|$", line):
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
    return rows


def load():
    rows = md_rows(KNOW, "### 3-1.")
    d = {}
    for r in rows[1:]:
        d[r[0]] = {"yomi": r[1], "kw": r[2], "text": r[3]}
    assert list(d) == ORDER or set(d) == set(ORDER), d.keys()
    rel = {}
    for r in md_rows(KNOW, "**各関係の意味と吉凶の傾向**")[1:]:
        rel[r[0].replace("・", "")] = {"mean": r[1], "luck": re.sub(r"\*\*", "", r[2])}
    return d, rel


def ring():
    """27宿の輪（SVG）"""
    out = ['<svg viewBox="0 0 220 220" class="fh-b27-sk-ring" aria-hidden="true"><circle cx="110" cy="110" r="96" fill="none" stroke="rgba(200,210,240,.35)"/><circle cx="110" cy="110" r="74" fill="none" stroke="rgba(200,210,240,.2)"/>']
    for i, s in enumerate(ORDER):
        a = -math.pi / 2 + 2 * math.pi * i / 27
        x, y = 110 + 85 * math.cos(a), 110 + 85 * math.sin(a)
        out.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" dominant-baseline="central">{s}</text>')
    out.append('<circle cx="110" cy="110" r="34" fill="url(#fhskm)"/><defs><radialGradient id="fhskm" cx="40%" cy="38%"><stop offset="0" stop-color="#FFFDF2"/><stop offset=".7" stop-color="#E3E6F2"/><stop offset="1" stop-color="#AEB6D3"/></radialGradient></defs></svg>')
    return "".join(out)


CSS = """<style id="fh-b27-sk-css">
.fh-b27[data-fh-page="shukuyo"]{--ink:#ECEFF7;--sub:#C9CFE2;--mute:#A2AAC6;--paper:#141A33;--deep:#10152A;--line:#3E4A78;--gold:#D8C38A;--silver:#C8D2F0;--cream:#F7F4EA;--cream-ink:#1E2340}
.fh-b27[data-fh-page="shukuyo"] a{color:#E3D29C}
.fh-b27[data-fh-page="shukuyo"] .fh-b27-note{border-left:0;border-radius:6px;background-color:var(--paper);
 background-image:radial-gradient(circle at 85% 8%,rgba(255,250,225,.16),transparent 22%),linear-gradient(transparent 96%,rgba(200,210,240,.05) 96%),linear-gradient(90deg,transparent 96%,rgba(200,210,240,.05) 96%),radial-gradient(rgba(255,255,255,.08) 1px,transparent 1.4px);
 background-size:auto,28px 28px,28px 28px,41px 41px;box-shadow:0 14px 40px rgba(0,0,0,.5),inset 0 0 0 1px rgba(216,195,138,.4),inset 0 0 0 5px var(--paper),inset 0 0 0 6px rgba(216,195,138,.22)}
.fh-b27-sk-ring{width:170px;height:170px;flex:0 0 170px;animation:fh-b27-sk-rot 120s linear infinite}
.fh-b27-sk-ring text{font:600 13px 'Shippori Mincho',serif;fill:#D8DEF3}
@keyframes fh-b27-sk-rot{to{transform:rotate(360deg)}}
@media (prefers-reduced-motion:reduce){.fh-b27-sk-ring{animation:none}}
.fh-b27[data-fh-page="shukuyo"] .fh-b27-hero{align-items:center}
.fh-b27[data-fh-page="shukuyo"] .fh-b27-tape{transform:none;border-radius:0;background:transparent;border-top:1px solid var(--gold);border-bottom:1px solid var(--gold);color:var(--gold);font-family:'Shippori Mincho',serif;letter-spacing:.3em}
.fh-b27[data-fh-page="shukuyo"] .fh-b27-title{font-family:'Shippori Mincho',serif;font-weight:800;font-size:31px}
.fh-b27[data-fh-page="shukuyo"] h2{font-family:'Shippori Mincho',serif;font-weight:800;font-size:24px;border-left:4px solid var(--gold);padding-left:12px}
.fh-b27[data-fh-page="shukuyo"] h2 .fh-b27-n{display:none}
.fh-b27[data-fh-page="shukuyo"] h3{border-bottom:1px solid rgba(216,195,138,.35)}
.fh-b27[data-fh-page="shukuyo"] .fh-b27-toc{border:1px solid rgba(216,195,138,.35);border-radius:4px}
.fh-b27[data-fh-page="shukuyo"] .fh-b27-toc ol{columns:2;column-gap:28px}
.fh-b27-sk-box{border:1px solid rgba(216,195,138,.4);border-radius:6px;background:rgba(16,21,42,.75);padding:16px;display:flex;flex-direction:column;gap:12px}
.fh-b27-sk-form{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.fh-b27-sk-form select{min-height:44px;border-radius:4px;border:1px solid var(--line);background:var(--deep);color:var(--ink);font:inherit;padding:0 8px}
.fh-b27-sk-form b{font-size:13px;color:var(--gold);min-width:4em}
.fh-b27-sk-btn{min-height:44px;border:0;border-radius:4px;background:linear-gradient(#E8D7A2,#BFA463);color:#141A33;font:inherit;font-weight:700;padding:0 18px;cursor:pointer}
.fh-b27-sk-res{background:var(--cream);color:var(--cream-ink);border-radius:6px;padding:16px 18px;line-height:1.85}
.fh-b27 .fh-b27-sk-res p,.fh-b27 .fh-b27-sk-res b{color:var(--cream-ink)}
.fh-b27-sk-res .nm{font:800 34px 'Shippori Mincho',serif;color:#1E2340}
.fh-b27-sk-res small{color:#5A6185}
.fh-b27 .fh-b27-sk-res a{color:#3B4A8C;font-weight:700}
.fh-b27-sk-grid{display:grid;grid-template-columns:repeat(9,minmax(0,1fr));gap:6px}
.fh-b27-sk-grid a{display:flex;flex-direction:column;align-items:center;border:1px solid rgba(200,210,240,.25);border-radius:4px;padding:6px 0;text-decoration:none;background:rgba(16,21,42,.6);line-height:1.3}
.fh-b27-sk-grid b{font:800 20px 'Shippori Mincho',serif;color:var(--ink)}
.fh-b27-sk-grid small{font-size:10.5px;color:var(--mute)}
.fh-b27-sk-list{display:flex;flex-direction:column;gap:8px}
.fh-b27-sk-list details{border:1px solid rgba(200,210,240,.2);border-radius:4px;background:rgba(16,21,42,.55);padding:8px 14px}
.fh-b27-sk-list summary{cursor:pointer;font-family:'Shippori Mincho',serif;font-weight:800;font-size:17px}
.fh-b27-sk-list summary small{font-family:'Zen Kaku Gothic New',sans-serif;font-weight:400;color:var(--mute);font-size:12.5px;margin-left:8px}
.fh-b27-sk-list p{font-size:14.5px;line-height:1.9;margin-top:6px}
.fh-b27-sk-t{width:100%;border-collapse:collapse;font-size:14px;line-height:1.75}
.fh-b27-sk-t caption{text-align:left;color:var(--sub);font-size:13px;padding-bottom:4px}
.fh-b27-sk-t th,.fh-b27-sk-t td{border-bottom:1px solid rgba(200,210,240,.18);padding:7px 6px;text-align:left;vertical-align:top}
.fh-b27-sk-t thead th{color:var(--gold);font-size:13px}
.fh-b27-sk-t tbody th{white-space:nowrap;font-family:'Shippori Mincho',serif;font-size:16px}
.fh-b27-sk-wrap{overflow-x:auto}
.fh-b27-sk-qa details{border-bottom:1px solid rgba(200,210,240,.2);padding:8px 2px}
.fh-b27-sk-qa summary{cursor:pointer;font-weight:700}
.fh-b27-sk-qa p{margin-top:6px;font-size:14.5px}
@media (max-width:640px){.fh-b27-sk-grid{grid-template-columns:repeat(5,minmax(0,1fr))}.fh-b27[data-fh-page="shukuyo"] .fh-b27-toc ol{columns:1}.fh-b27-sk-ring{width:130px;height:130px;flex-basis:130px}.fh-b27[data-fh-page="shukuyo"] .fh-b27-title{font-size:26px}}
.fh-b27-sk-wheel{display:block;width:240px;height:240px;margin:0 auto 10px}
.fh-b27-sk-wheel g.rot{transform-origin:120px 120px;transition:transform 1.4s cubic-bezier(.2,.8,.2,1)}
.fh-b27-sk-wheel text{font:700 12px 'Shippori Mincho',serif;fill:#C9D0EA}
.fh-b27-sk-wheel circle.d{fill:#2A3158;stroke:rgba(200,210,240,.4)}
.fh-b27-sk-wheel circle.me{fill:#F2D27A;stroke:#fff}.fh-b27-sk-wheel circle.ei{fill:#5FA27A}.fh-b27-sk-wheel circle.yu{fill:#5C82C9}.fh-b27-sk-wheel circle.an{fill:#C8564A}.fh-b27-sk-wheel circle.ki{fill:#7D7F93}.fh-b27-sk-wheel circle.gy{fill:#B08A3E}
.fh-b27-sk-wheel text.me{fill:#1E2340;font-size:14px}
.fh-b27-sk-leg{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;font-size:12px;color:#2E3766;margin-bottom:12px}
.fh-b27-sk-leg i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:4px;vertical-align:-1px}
.fh-b27-sk-card{opacity:0;transform:translateY(14px);animation:fh-b27-sk-in .6s ease 1.2s forwards}@keyframes fh-b27-sk-in{to{opacity:1;transform:none}}
.fh-b27-sk-res .ct{font-family:'Shippori Mincho',serif;font-size:16px;color:#3B4A8C;margin:-4px 0 8px}
.fh-b27-sk-tabs{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 8px}
.fh-b27-sk-tabs button{min-height:38px;border:1px solid #B9C0DC;border-radius:999px;background:#FAFBFF;color:#2E3766;font:inherit;font-size:14px;font-weight:700;padding:0 14px;cursor:pointer}
.fh-b27-sk-tabs button[aria-selected="true"]{background:#3B4A8C;border-color:#3B4A8C;color:#fff}
.fh-b27-sk-pane{background:#FFFFFF;border-radius:6px;padding:12px 14px;min-height:5em}
.fh-b27-sk-rels{margin-top:12px;border-top:1px dashed #B9C0DC;padding-top:10px}
.fh-b27-sk-chips{display:flex;flex-wrap:wrap;gap:6px;margin:4px 0 8px}
.fh-b27-sk-chips span{border-radius:999px;padding:2px 12px;font-size:13.5px;font-weight:700;background:#E6E9F5;color:#2E3766}
.fh-b27-sk-chips.ei span{background:#DCEFE2;color:#1F4A2E}.fh-b27-sk-chips.an span{background:#F6DEDA;color:#7A2A20}
.fh-b27[data-fh-page="shukuyo"] .fh-b27-sk-res a.fh-b27-shopbtn{color:#FFF5D6}
.fh-b27 .fh-b27-sk-res .fh-b27-adgoods-h{color:#1E2340}
@media (prefers-reduced-motion:reduce){.fh-b27-sk-wheel g.rot{transition:none}.fh-b27-sk-card{animation:none;opacity:1;transform:none}}
</style>"""

JS = r"""(function(){var C=window.FHB27Calc;var D=__DATA__,ORD=__ORDER__,REL=__REL__,PAIR=__PAIR__,RM=__RM__;
function $(i){return document.getElementById(i)}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function fill(p){var y=$(p+'y'),m=$(p+'m'),d=$(p+'d');var gy=C?C.GEN.yearMin:1930,gx=C?C.GEN.yearMax:2030;
 for(var i=gy;i<=gx;i++){var o=document.createElement('option');o.value=i;o.textContent=i+'年';if(i===1990)o.selected=true;y.appendChild(o);}
 for(i=1;i<=12;i++){o=document.createElement('option');o.value=i;o.textContent=i+'月';m.appendChild(o);}
 function days(){var n=new Date(+y.value,+m.value,0).getDate(),v=+d.value||1;d.innerHTML='';for(var k=1;k<=n;k++){var o=document.createElement('option');o.value=k;o.textContent=k+'日';if(k===Math.min(v,n))o.selected=true;d.appendChild(o);}}
 y.addEventListener('change',days);m.addEventListener('change',days);days();}
function get(p){var y=+$(p+'y').value,m=+$(p+'m').value,d=+$(p+'d').value,s=C&&C.shuku(y,m,d);return s?{y:y,m:m,d:d,s:s}:null;}
if(!$('sk-ay'))return;
if(!C){$('sk-res').innerHTML='<p>計算の準備ができませんでした。ページを読み込み直してください。</p>';return;}
fill('sk-a');fill('sk-b');
var T=__SKT__,CL={'命':'me','業':'gy','胎':'gy','栄':'ei','親':'ei','友':'yu','衰':'yu','安':'an','壊':'an','危':'ki','成':'ki'};
$('sk-go').addEventListener('click',function(){var a=get('sk-a');if(!a){$('sk-res').innerHTML='<p>この日付は計算できません。</p>';$('sk-res').hidden=false;return;}
 var x=D[a.s.name],k=a.s.kyu,t=T[a.s.name],ia=ORD.indexOf(a.s.name),sv='',grp={ei:[],yu:[],an:[]};
 for(var i=0;i<27;i++){var dd=((i-ia)%27+27)%27,rl=RM[dd],c=CL[rl]||'d',an=-Math.PI/2+2*Math.PI*i/27,X=120+96*Math.cos(an),Y=120+96*Math.sin(an);
  sv+='<circle class="'+c+'" cx="'+X.toFixed(1)+'" cy="'+Y.toFixed(1)+'" r="'+(dd?11:14)+'"/><text class="'+(dd?'':'me')+'" x="'+X.toFixed(1)+'" y="'+Y.toFixed(1)+'" text-anchor="middle" dominant-baseline="central" transform="rotate('+(360*i/27).toFixed(1)+' '+X.toFixed(1)+' '+Y.toFixed(1)+')">'+ORD[i]+'</text>';
  if(grp[c]&&dd)grp[c].push(ORD[i]+'宿（'+rl+'）');}
 var rot=-(360*ia/27);
 var tb=[['char','性格'],['love','恋愛'],['work','仕事'],['money','お金']],tx={char:'<p><b>キーワード：</b>'+esc(x.kw)+'</p><p>'+esc(x.text)+'</p>',love:'<p>'+esc(t.love)+'</p>',work:'<p>'+esc(t.work)+'</p>',money:'<p>'+esc(t.money)+'</p>'};
 var chips=function(l,c){return '<div class="fh-b27-sk-chips '+c+'">'+l.map(function(n){return '<span>'+esc(n)+'</span>'}).join('')+'</div>'};
 $('sk-res').innerHTML='<svg class="fh-b27-sk-wheel" viewBox="0 0 240 240" aria-hidden="true"><circle cx="120" cy="120" r="112" fill="#1E2340"/><g class="rot" id="sk-rot">'+sv+'</g><circle cx="120" cy="120" r="42" fill="url(#fhskm2)"/><defs><radialGradient id="fhskm2" cx="40%" cy="38%"><stop offset="0" stop-color="#FFFDF2"/><stop offset=".7" stop-color="#E3E6F2"/><stop offset="1" stop-color="#AEB6D3"/></radialGradient></defs></svg>'+
  '<div class="fh-b27-sk-leg"><span><i style="background:#F2D27A"></i>あなた</span><span><i style="background:#5FA27A"></i>栄親</span><span><i style="background:#5C82C9"></i>友衰</span><span><i style="background:#C8564A"></i>安壊</span><span><i style="background:#7D7F93"></i>危成</span><span><i style="background:#B08A3E"></i>業胎</span></div>'+
  '<div class="fh-b27-sk-card"><small>'+a.y+'年'+a.m+'月'+a.d+'日生まれ（旧暦 '+(k.leap?'閏':'')+k.month+'月'+k.day+'日）の本命宿</small><p class="nm">'+esc(a.s.name)+'宿<small style="font-size:15px;margin-left:8px">'+esc(x.yomi)+'</small></p><p class="ct">'+esc(t.catch)+'</p>'+
  '<div class="fh-b27-sk-tabs" role="tablist">'+tb.map(function(b,i){return '<button type="button" role="tab" data-t="'+b[0]+'" aria-selected="'+(i?'false':'true')+'">'+b[1]+'</button>'}).join('')+'</div><div class="fh-b27-sk-pane" id="sk-pane">'+tx.char+'</div>'+
  '<div class="fh-b27-sk-rels"><p><b>いちばん穏やかに付き合える宿（栄親）</b></p>'+chips(grp.ei,'ei')+'<p><b>気を許せる仲間の宿（友衰）</b></p>'+chips(grp.yu,'')+'<p><b>強く惹かれ合うけれど距離感が大切な宿（安壊）</b></p>'+chips(grp.an,'an')+'</div>'+
  '<div id="sk-lucky"></div><p><a href="#sk-'+ia+'">'+esc(a.s.name)+'宿の説明へ →</a>　<a href="#b27-sk-aisho">二人の相性を見る →</a></p></div>';
 $('sk-res').hidden=false;var src=document.querySelector('#sk-lucky-src [data-s="'+ia+'"]');if(src)$('sk-lucky').appendChild(src.cloneNode(true));
 requestAnimationFrame(function(){requestAnimationFrame(function(){var g=$('sk-rot');if(g)g.style.transform='rotate('+rot+'deg)';});});
 $('sk-res').querySelectorAll('.fh-b27-sk-tabs button').forEach(function(b){b.addEventListener('click',function(){$('sk-res').querySelectorAll('.fh-b27-sk-tabs button').forEach(function(z){z.setAttribute('aria-selected','false')});b.setAttribute('aria-selected','true');$('sk-pane').innerHTML=tx[b.getAttribute('data-t')];});});
});
$('sk-go2').addEventListener('click',function(){var a=get('sk-a'),b=get('sk-b');var r=$('sk-res2');r.hidden=false;if(!a||!b){r.innerHTML='<p>この日付は計算できません。</p>';return;}
 var ia=ORD.indexOf(a.s.name),ib=ORD.indexOf(b.s.name),dd=((ib-ia)%27+27)%27,me=RM[dd],you=RM[(27-dd)%27],pr=PAIR[me],kk=Math.min(dd,27-dd);
 var dist=pr==='命'?'':pr==='業胎'?'':kk<=4?'近距離':kk<=8?'中距離':'遠距離',rel=REL[pr]||{};
 r.innerHTML='<small>あなた：'+esc(a.s.name)+'宿　お相手：'+esc(b.s.name)+'宿</small><p class="nm">'+esc(pr)+(dist?'<small style="font-size:15px;margin-left:8px">'+dist+'</small>':'')+'</p><p>あなたから見てお相手は「'+esc(me)+'」、お相手から見てあなたは「'+esc(you)+'」の関係です。</p><p>'+esc(rel.mean||'')+'</p><p><b>傾向：</b>'+esc(rel.luck||'')+'</p><p><a href="#b27-sk-sankyu">三九の秘法の説明へ →</a></p>';});
})();"""


def build(sample, updated):
    d, rel = load()
    H = []
    a = H.append
    a(CSS)
    a('<div class="fh-b27" data-fh-page="shukuyo">\n<div class="fh-b27-note">')
    a(f'''<header class="fh-b27-hero">
  {ring()}
  <div class="fh-b27-hero-body">
    <span class="fh-b27-tape">宿曜占星術</span>
    <h1 class="fh-b27-title">宿曜占星術<br>生年月日で本命宿と相性を調べる</h1>
    <p class="fh-b27-lead">生年月日を選ぶだけで、月の暦から本命宿（27宿）を計算します。二人の生年月日から、三九の秘法による相性もわかります。本命宿は旧暦の月日と『宿曜経』の決まりで計算しており、366日の誕生日占い・生年月日まるごと診断と同じ結果です。</p>
  </div>
</header>''')
    items = [("b27-sk-calc", "本命宿を調べる"), ("b27-sk-aisho", "二人の相性（三九の秘法）"), ("b27-sk-27", "27宿の性格・恋愛・仕事・お金"),
             ("b27-sk-sankyu", "三九の秘法とは"), ("b27-sk-how", "本命宿の出し方"), ("b27-sk-about", "宿曜占星術とは"), ("b27-sk-faq", "よくある質問")]
    a('<nav class="fh-b27-toc" aria-label="目次"><strong>このページの内容</strong><ol>' + "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in items) + "</ol></nav>")
    h2 = lambda t: f'<h2><span class="fh-b27-n"></span><span>{t}</span></h2>'
    sel = lambda p, who: (f'<div class="fh-b27-sk-form"><b>{who}</b><select id="{p}y" aria-label="{who}の生まれた年"></select>'
                          f'<select id="{p}m" aria-label="{who}の生まれた月"></select><select id="{p}d" aria-label="{who}の生まれた日"></select></div>')
    a(f'''<section class="fh-b27-sec" id="b27-sk-calc">
  {h2("本命宿を調べる")}
  <div class="fh-b27-sk-box">
    {sel("sk-a", "あなた")}
    <div><button type="button" class="fh-b27-sk-btn" id="sk-go">本命宿を調べる</button></div>
    <div class="fh-b27-sk-res" id="sk-res" aria-live="polite" hidden></div>
    <p class="fh-b27-small">1930〜2030年の生まれに対応しています。生年月日は送信も保存もしません（このページの中だけで計算します）。</p>
  </div>
  <noscript><p class="fh-b27-small">計算にはJavaScriptを使います。下の「本命宿の出し方」で手でも調べられます。</p></noscript>
</section>
<section class="fh-b27-sec" id="b27-sk-aisho">
  {h2("二人の相性（三九の秘法）")}
  <div class="fh-b27-sk-box">
    <p class="fh-b27-small">上で選んだ「あなた」の生年月日と、お相手の生年月日で相性を見ます。</p>
    {sel("sk-b", "お相手")}
    <div><button type="button" class="fh-b27-sk-btn" id="sk-go2">相性を見る</button></div>
    <div class="fh-b27-sk-res" id="sk-res2" aria-live="polite" hidden></div>
  </div>
</section>''')
    a("<!--Ads1-->")
    grid = "".join(f'<a href="#sk-{i}"><b>{s}</b><small>{esc(d[s]["yomi"])}</small></a>' for i, s in enumerate(ORDER))
    det = "".join(f'<details id="sk-{i}"><summary>{s}宿<small>{esc(d[s]["yomi"])}｜{esc(d[s]["kw"])}</small></summary><p>{esc(d[s]["text"])}</p><p><b>恋愛：</b>{esc(SKT.TEXTS[s]["love"])}</p><p><b>仕事：</b>{esc(SKT.TEXTS[s]["work"])}</p><p><b>お金：</b>{esc(SKT.TEXTS[s]["money"])}</p></details>' for i, s in enumerate(ORDER))
    a(f'''<section class="fh-b27-sec" id="b27-sk-27">
  {h2("27宿の性格・恋愛・仕事・お金")}
  <p>月の通り道を27に分けた宿を、昴宿から胃宿までの順に並べました。宿を押すと、その宿に生まれた人の性格の特徴が開きます。</p>
  <div class="fh-b27-sk-grid">{grid}</div>
  <div class="fh-b27-sk-list">{det}</div>
</section>''')
    rows = "".join(f'<tr><th scope="row">{esc(k)}</th><td>{esc(v["mean"])}</td><td>{esc(v["luck"])}</td></tr>' for k, v in rel.items())
    a(f'''<section class="fh-b27-sec" id="b27-sk-sankyu">
  {h2("三九の秘法とは")}
  <p>三九の秘法（さんくのひほう）は、自分の宿から相手の宿までの距離で関係を読む、宿曜占星術の相性の見方です。27宿を9つずつ「命の九・業の九・胎の九」の3組に分け、それぞれの組の中で「栄・衰・安・危・成・壊・友・親」の関係がくり返されます。</p>
  <p>関係は必ずペアになっていて、自分にとって「栄」の相手からは自分が「親」に見えます。このペアで、二人の関係は次の6つに分かれます。自分以外の26宿は、栄親・友衰・安壊・危成が6つずつ、業胎が2つです。</p>
  <div class="fh-b27-sk-wrap"><table class="fh-b27-sk-t"><caption>三九の秘法の6つの関係</caption><thead><tr><th scope="col">関係</th><th scope="col">意味</th><th scope="col">傾向</th></tr></thead><tbody>{rows}</tbody></table></div>
  <p>同じ関係でも、宿が近い「近距離」ほど身近で穏やかに、遠い「遠距離」ほど影響が強く出ると説明されることが多いですが、語り方は流派によって違います。結果は二人の関わり方を考えるきっかけとして読んでください。</p>
</section>''')
    ms = "".join(f"<td>{MONTH_START[m]}</td>" for m in range(1, 13))
    a(f'''<section class="fh-b27-sec" id="b27-sk-how">
  {h2("本命宿の出し方")}
  <p>本命宿は、次の3つの手順で決まります。</p>
  <ol>
    <li>生年月日（ふだんの暦）を<b>旧暦</b>に直します。</li>
    <li>旧暦の月ごとに決まっている<b>「1日の宿」</b>を下の表から探します（『宿曜経』による決まり。閏月はもとの月と同じ）。</li>
    <li>その宿から、旧暦の日にちから1を引いた数だけ、昴・畢・觜…の順に進めます（27で一周）。</li>
  </ol>
  <div class="fh-b27-sk-wrap"><table class="fh-b27-sk-t" style="min-width:560px;text-align:center"><caption>旧暦の各月1日の宿</caption><thead><tr><th scope="col">旧暦の月</th>{"".join(f"<th scope='col'>{m}月</th>" for m in range(1, 13))}</tr></thead><tbody><tr><th scope="row">1日の宿</th>{ms}</tr></tbody></table></div>
  <p>例：2027年2月7日は旧暦の1月1日なので、1月1日の宿の<b>室宿</b>です。2027年1月1日は旧暦11月24日なので、斗宿から23進んだ<b>房宿</b>になります。</p>
  <p class="fh-b27-small">旧暦は、国立天文台の暦と同じ決まり（日本時間・定気）で、1900〜2030年分を天文計算で作りました。月の位置で直接決める方式など、ほかの計算方法を使うサイトとは結果が違うことがあります。</p>
</section>''')
    a(f'''<section class="fh-b27-sec" id="b27-sk-about">
  {h2("宿曜占星術とは")}
  <p>宿曜占星術は、インドで生まれた月の暦と占いが中国で漢訳された『宿曜経』をもとにした占いです。日本へは平安時代のはじめに空海が伝えたとされ、宿曜道として朝廷の暦や吉凶の判断にも使われてきました。</p>
  <p>月はおよそ27.3日で空をひと回りします。その通り道を27の宿に分け、生まれた日の月がどの宿にあったかを「本命宿」と呼びます。中国の二十八宿から牛宿を除いた27宿を使うのが特徴です。太陽の位置で決まる西洋の12星座に対して、宿曜占星術は月の動きから人の性格と縁を読む占いといえます。</p>
</section>''')
    qa = "".join(f'<details{" open" if i == 0 else ""}><summary>Q. {q}</summary><p>A. {x}</p></details>' for i, (q, x) in enumerate(FAQ))
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in FAQ]}
    a(f'''<section class="fh-b27-sec" id="b27-sk-faq">
  {h2("よくある質問")}
  <div class="fh-b27-sk-qa">{qa}</div>
</section>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<section class="fh-b27-sec">
  <div class="fh-b27-links">
    <a href="/seinengappi/"><b>生年月日まるごと診断 →</b><small>宿曜・九星・四柱推命・マヤ暦などを1枚に</small></a>
    <a href="/366uranai/"><b>366日の誕生日占い →</b><small>誕生日から性格・相性・2027年の運勢</small></a>
    <a href="/compatibility/"><b>誕生日相性占い →</b><small>2人の誕生日で相性を見る</small></a>
  </div>
</section>''')
    data = {s: {"yomi": d[s]["yomi"], "kw": d[s]["kw"], "text": d[s]["text"]} for s in ORDER}
    lucky = "".join(f'<div data-s="{i}">{aff_extra.goods_box("あなたの宿のお守りアイテム", [(SKT.TEXTS[st]["lucky"][0], SKT.TEXTS[st]["lucky"][0], SKT.TEXTS[st]["lucky"][1], "goods")])}</div>' for i, st in enumerate(ORDER))
    a(f'<div id="sk-lucky-src" hidden>{lucky}</div>')
    js = (JS.replace("__SKT__", json.dumps(SKT.TEXTS, ensure_ascii=False)).replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":"))).replace("__ORDER__", json.dumps(ORDER, ensure_ascii=False))
          .replace("__REL__", json.dumps(rel, ensure_ascii=False)).replace("__PAIR__", json.dumps(PAIR, ensure_ascii=False))
          .replace("__RM__", json.dumps([REL_D[i] for i in range(27)], ensure_ascii=False)))
    up = dt.date.fromisoformat(updated)
    a(f'<p class="fh-b27-foot">本命宿は旧暦の月日と『宿曜経』の各月1日の宿から、このサイトで計算しています。27宿の説明はこのサイトで書いたものです。占いは楽しみと気づきのためにお読みください。<br>'
      f'最終更新日：{up.year}年{up.month}月{up.day}日／<a href="/about/">この記事の作成方針について</a></p>')
    a("</div>\n</div>")
    a(f"<script>document.addEventListener('DOMContentLoaded',function(){{{js}}});</script>")
    title = "宿曜占星術｜生年月日で本命宿を計算・27宿の性格と相性（三九の秘法）【無料】"
    desc = ("生年月日を選ぶだけで宿曜占星術の本命宿（27宿）を無料で計算。27宿の性格一覧と、二人の生年月日から三九の秘法（栄親・友衰・安壊・危成・業胎・命）で相性もわかります。旧暦から正しく計算。")
    out = shell(title, desc, URL, "\n".join(H), sample, SCRIPTS)
    assert "！" not in out
    return out


def main():
    updated = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    for sample, path in ((False, os.path.join(OUT, "shukuyo.html")), (True, os.path.join(OUT, "sample", "shukuyo.html"))):
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(build(sample, updated))
        print("→", os.path.relpath(path, WORK))


if __name__ == "__main__":
    main()
