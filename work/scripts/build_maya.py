"""マヤ暦（ドリームスペル）のページ（新しい固定ページ /maya/）を作る（2026-10-16 本人の決定：「マヤ暦」月1万〜10万回の検索に入る）。
KINの計算は共通JS（fh-b27.js の FHB27Calc.kin）をそのまま使う＝まるごと診断と同じ結果。紋章・音の文章は work/knowledge/07_マヤ暦.md（このサイトの言葉）。
古代マヤの暦そのものではない（ドリームスペル）ことをページに明記する（knowledge の決まり）。
"""
import datetime as dt, html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_hub import OUT, WORK, shell  # noqa: E402
from build_shukuyo import md_rows, esc  # noqa: E402

import maya_texts as MT  # noqa: E402
import aff_extra  # noqa: E402
URL = "/maya/"
KNOW = os.path.join(WORK, "knowledge", "07_マヤ暦.md")
SCRIPTS = ("fh-b27-setsuiri.js", "fh-b27-kyureki.js", "fh-b27.js")
COLOR = {"赤": ("#C8463C", "始める", "物事を始め、勢いよく動き出す力"), "白": ("#E9E4D8", "洗練する", "余分なものを落とし、整えていく力"),
         "青": ("#3E6FB0", "変容する", "変化を起こし、新しい形に変えていく力"), "黄": ("#E2B33C", "熟す", "実らせ、形にして受け取る力")}
FAQ = [
    ("マヤ暦占いのKINとは何ですか。", "1日ごとに割り当てられた1〜260の番号です。20の太陽の紋章と13の銀河の音の組み合わせ（20×13＝260）で、260日で一巡します。誕生日のKINを、その人の「銀河の署名」として読みます。"),
    ("このページのマヤ暦は、古代マヤの暦と同じですか。", "同じではありません。このページのマヤ暦は、ホゼ・アグエイアスらが1987年以降に発表した「ドリームスペル」（13の月の暦）にもとづく現代の占いです。古代マヤの遺跡に残る暦とは数え方が違い、同じ日でも番号がずれます。"),
    ("2月29日生まれのKINはどうなりますか。", "ドリームスペルでは2月29日を数えないため、このページでは前日の2月28日と同じKINにしています。"),
    ("同じ誕生日なら同じKINですか。", "いいえ。2月29日を数えないため、同じ月日でも1年ごとにKINが105ずつ進みます。KINを出すには生まれた年が必要です。"),
    ("今日のKINも調べられますか。", "調べられます。ページの「今日のKIN」に、今日の紋章と銀河の音を表示しています。2026年8月27日から新しい260日の周期が始まりました。"),
    ("ガイドキンや反対キンは出ますか。", "出ます。KINを調べると、ガイドキン（導く力）・類似キン（支え合う力）・反対キン（鍛え合う力）・神秘キン（隠れた力）の4つも計算して表示します。ドリームスペルの一般的な決まり（ガイドは銀河の音で決まる同じ色の紋章、類似は紋章の番号の和が19、反対は10離れた紋章、神秘は紋章の和が21で音の和が14）で出しています。"),
]


def load():
    seals = []
    for r in md_rows(KNOW, "### 20の太陽の紋章")[1:]:
        seals.append({"no": int(r[0]), "name": r[1], "kw": r[2], "text": r[3]})
    tones = []
    for r in md_rows(KNOW, "### 13の銀河の音")[1:]:
        tones.append({"no": int(r[0]), "name": r[1], "kw": r[2], "text": r[3]})
    assert len(seals) == 20 and len(tones) == 13
    return seals, tones


CSS = """<style id="fh-b27-my-css">
.fh-b27[data-fh-page="maya"]{--ink:#F2ECE0;--sub:#D6CDBA;--mute:#AEA48E;--paper:#1C2422;--deep:#151C1A;--line:#4C5A50;--gold:#E2B33C;--cream:#F5EEDD;--cream-ink:#25201A}
.fh-b27[data-fh-page="maya"] a{color:#F0C963}
.fh-b27[data-fh-page="maya"] .fh-b27-note{border-left:0;border-radius:14px;background-color:var(--paper);
 background-image:repeating-linear-gradient(90deg,rgba(226,179,60,.06) 0 2px,transparent 2px 40px),repeating-linear-gradient(0deg,rgba(226,179,60,.04) 0 2px,transparent 2px 40px),radial-gradient(circle at 50% -20%,rgba(226,179,60,.18),transparent 50%);
 background-size:auto,auto,auto;box-shadow:0 14px 40px rgba(0,0,0,.5);border-top:6px solid transparent;border-image:linear-gradient(90deg,#C8463C 0 25%,#E9E4D8 25% 50%,#3E6FB0 50% 75%,#E2B33C 75%) 1}
.fh-b27-my-emb{width:150px;height:150px;flex:0 0 150px;border-radius:50%;background:conic-gradient(#C8463C 0 25%,#E9E4D8 0 50%,#3E6FB0 0 75%,#E2B33C 0);position:relative;box-shadow:0 0 0 6px rgba(0,0,0,.25),0 0 30px rgba(226,179,60,.25);animation:fh-b27-my-rot 90s linear infinite}
.fh-b27-my-emb:after{content:"KIN";position:absolute;inset:28px;border-radius:50%;background:#1C2422;color:var(--gold);display:flex;align-items:center;justify-content:center;font:800 26px 'Shippori Mincho',serif;letter-spacing:.1em;animation:fh-b27-my-rot 90s linear infinite reverse}
@keyframes fh-b27-my-rot{to{transform:rotate(360deg)}}
@media (prefers-reduced-motion:reduce){.fh-b27-my-emb,.fh-b27-my-emb:after{animation:none}}
.fh-b27[data-fh-page="maya"] .fh-b27-hero{align-items:center}
.fh-b27[data-fh-page="maya"] .fh-b27-tape{transform:none;border-radius:999px;background:var(--gold);color:#1C2422}
.fh-b27[data-fh-page="maya"] .fh-b27-title{font-family:'Shippori Mincho',serif;font-weight:800;font-size:31px}
.fh-b27[data-fh-page="maya"] h2{font-family:'Shippori Mincho',serif;font-weight:800;font-size:24px}
.fh-b27[data-fh-page="maya"] h2 .fh-b27-n{border:0;border-radius:4px;background:var(--gold);color:#1C2422}
.fh-b27[data-fh-page="maya"] .fh-b27-toc{border-style:solid;border-radius:10px}
.fh-b27[data-fh-page="maya"] .fh-b27-toc ol{columns:2;column-gap:28px}
.fh-b27-my-box{border:1px solid rgba(226,179,60,.35);border-radius:12px;background:rgba(21,28,26,.8);padding:16px;display:flex;flex-direction:column;gap:12px}
.fh-b27-my-form{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.fh-b27-my-form select{min-height:44px;border-radius:8px;border:1px solid var(--line);background:var(--deep);color:var(--ink);font:inherit;padding:0 8px}
.fh-b27-my-btn{min-height:44px;border:0;border-radius:999px;background:var(--gold);color:#1C2422;font:inherit;font-weight:700;padding:0 18px;cursor:pointer}
.fh-b27-my-res{background:var(--cream);color:var(--cream-ink);border-radius:12px;padding:16px 18px;line-height:1.85;border-left:8px solid var(--c,#E2B33C)}
.fh-b27 .fh-b27-my-res p,.fh-b27 .fh-b27-my-res b{color:var(--cream-ink)}
.fh-b27-my-res .nm{font:800 28px 'Shippori Mincho',serif}
.fh-b27-my-res small{color:#6A6150}
.fh-b27 .fh-b27-my-res a{color:#8A5A10;font-weight:700}
.fh-b27-my-today{display:flex;align-items:center;gap:12px;border:1px dashed rgba(226,179,60,.5);border-radius:10px;padding:10px 14px}
.fh-b27-my-today b{font:800 22px 'Shippori Mincho',serif;color:var(--gold)}
.fh-b27-my-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
.fh-b27-my-grid a{display:flex;align-items:center;gap:8px;border:1px solid rgba(255,255,255,.12);border-radius:8px;padding:8px;text-decoration:none;background:rgba(21,28,26,.6);font-size:13.5px;color:var(--ink);line-height:1.3}
.fh-b27-my-grid i{flex:0 0 14px;height:14px;border-radius:50%;background:var(--c)}
.fh-b27-my-list{display:flex;flex-direction:column;gap:8px}
.fh-b27-my-list details{border:1px solid rgba(255,255,255,.12);border-left:6px solid var(--c,#E2B33C);border-radius:8px;background:rgba(21,28,26,.55);padding:8px 14px}
.fh-b27-my-list{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.fh-b27-my-list details[open]{grid-column:1/-1}
.fh-b27-my-list summary{cursor:pointer;list-style:none;display:flex;align-items:center;gap:12px}
.fh-b27-my-list summary::-webkit-details-marker{display:none}
.fh-b27-my-bd{flex:none;width:42px;height:42px;border-radius:50%;display:grid;place-items:center;font:800 17px 'Shippori Mincho',serif;color:#1A1A1A;background:var(--c,#E2B33C);box-shadow:0 0 0 3px rgba(255,255,255,.12),0 0 14px color-mix(in srgb,var(--c,#E2B33C) 45%,transparent)}
.fh-b27-my-tl .fh-b27-my-bd{background:radial-gradient(circle at 38% 35%,#FFF4C9,#E2B33C 70%,#A87C1E)}
.fh-b27-my-sm{display:flex;flex-direction:column;line-height:1.5}
.fh-b27-my-sm b{font-size:15.5px;color:#F6E7BC}
.fh-b27-my-sm small{font-size:12px;color:var(--mute)}
.fh-b27-my-list details.me{box-shadow:0 0 0 2px #E2B33C}
.fh-b27-my-list details.me .fh-b27-my-sm b::before{content:"あなた";display:inline-block;font-size:11px;background:#E2B33C;color:#1A1A1A;border-radius:3px;padding:0 6px;margin-right:6px;vertical-align:2px}
@media (max-width:640px){.fh-b27-my-list{grid-template-columns:1fr}}
.fh-b27-my-list p{font-size:14.5px;line-height:1.9;margin-top:6px}
.fh-b27-my-colors{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
.fh-b27-my-colors div{border-radius:10px;padding:10px 12px;background:rgba(21,28,26,.6);border-top:6px solid var(--c);font-size:13.5px;line-height:1.7}
.fh-b27-my-colors b{display:block;font-family:'Shippori Mincho',serif;font-size:17px}
.fh-b27-my-note{border-left:3px solid var(--gold);padding:8px 14px;background:rgba(226,179,60,.07);border-radius:0 8px 8px 0;font-size:14.5px}
.fh-b27-my-qa details{border-bottom:1px dashed var(--line);padding:8px 2px}
.fh-b27-my-qa summary{cursor:pointer;font-weight:700}
.fh-b27-my-qa p{margin-top:6px;font-size:14.5px}
@media (max-width:640px){.fh-b27-my-grid,.fh-b27-my-colors{grid-template-columns:repeat(2,minmax(0,1fr))}.fh-b27[data-fh-page="maya"] .fh-b27-toc ol{columns:1}.fh-b27-my-emb{width:120px;height:120px;flex-basis:120px}.fh-b27[data-fh-page="maya"] .fh-b27-title{font-size:26px}}
.fh-b27-my-flip{perspective:900px;width:200px;height:260px;margin:0 auto 14px}
.fh-b27-my-flip>div{position:relative;width:100%;height:100%;transform-style:preserve-3d;transition:transform 1s cubic-bezier(.3,1.3,.5,1)}
.fh-b27-my-flip.on>div{transform:rotateY(180deg)}
.fh-b27-my-flip .bk,.fh-b27-my-flip .fr{position:absolute;inset:0;border-radius:14px;backface-visibility:hidden;-webkit-backface-visibility:hidden;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;box-shadow:0 10px 26px rgba(0,0,0,.35)}
.fh-b27-my-flip .bk{background:conic-gradient(#C8463C 0 25%,#E9E4D8 0 50%,#3E6FB0 0 75%,#E2B33C 0);border:6px solid #1C2422}
.fh-b27-my-flip .bk:after{content:"KIN";width:96px;height:96px;border-radius:50%;background:#1C2422;color:#E2B33C;display:flex;align-items:center;justify-content:center;font:800 24px 'Shippori Mincho',serif}
.fh-b27-my-flip .fr{transform:rotateY(180deg);background:linear-gradient(160deg,#FFFBF0,#F2E8D2);border:6px solid var(--c,#E2B33C);color:#25201A;text-align:center;padding:10px}
.fh-b27-my-flip .fr small{font-size:12px;color:#6A6150}
.fh-b27-my-flip .fr b{font:800 34px 'Shippori Mincho',serif;color:#25201A;line-height:1.1}
.fh-b27-my-flip .fr em{font-style:normal;font:800 17px 'Shippori Mincho',serif}
.fh-b27-my-num{display:flex;flex-direction:column;align-items:center;gap:4px;margin:4px 0}
.fh-b27-my-num i{display:block;width:60px;height:8px;border-radius:4px;background:#25201A}
.fh-b27-my-num span{display:flex;gap:6px}.fh-b27-my-num span i{width:10px;height:10px;border-radius:50%}
.fh-b27-my-card{opacity:0;transform:translateY(14px);animation:fh-b27-my-in .6s ease 1s forwards}@keyframes fh-b27-my-in{to{opacity:1;transform:none}}
.fh-b27-my-res .ct{font-family:'Shippori Mincho',serif;font-size:16px;color:#8A5A10;margin:-4px 0 8px}
.fh-b27-my-tabs{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 8px}
.fh-b27-my-tabs button{min-height:38px;border:1px solid #D8C59A;border-radius:999px;background:#FFFCF3;color:#5A4415;font:inherit;font-size:14px;font-weight:700;padding:0 14px;cursor:pointer}
.fh-b27-my-tabs button[aria-selected="true"]{background:#8A5A10;border-color:#8A5A10;color:#FFF8E6}
.fh-b27-my-pane{background:#FFFDF8;border-radius:8px;padding:12px 14px;min-height:5em}
.fh-b27-my-rels{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin-top:12px}
.fh-b27-my-rels div{background:#FFFDF8;border-radius:8px;border-left:6px solid var(--c);padding:8px 10px;font-size:13px;line-height:1.65}
.fh-b27-my-rels div b{display:block;font:800 15px 'Shippori Mincho',serif;color:#25201A}
.fh-b27-my-rels div small{color:#6A6150}
.fh-b27[data-fh-page="maya"] .fh-b27-my-res a.fh-b27-shopbtn{color:#FFF5D6}
.fh-b27 .fh-b27-my-res .fh-b27-adgoods-h{color:#25201A}
@media (max-width:640px){.fh-b27-my-rels{grid-template-columns:1fr}}
@media (prefers-reduced-motion:reduce){.fh-b27-my-flip>div{transition:none}.fh-b27-my-card{animation:none;opacity:1;transform:none}}
.fh-b27-my-why{border:1.5px solid rgba(226,179,60,.45);border-radius:14px;background:linear-gradient(135deg,rgba(200,70,60,.14),rgba(62,111,176,.14),rgba(226,179,60,.12));padding:16px 18px}
.fh-b27-my-why-h{font:800 20px 'Shippori Mincho',serif;color:var(--gold);margin:0 0 6px}
.fh-b27 .fh-b27-my-why ul{list-style:none;padding:0;margin:10px 0;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.fh-b27 .fh-b27-my-why li{margin:0;background:var(--cream);color:var(--cream-ink);border-radius:10px;padding:10px 12px;font-size:13.5px;line-height:1.7}
.fh-b27-my-why li::before{content:none}.fh-b27 .fh-b27-my-why li b{display:block;color:#8A5A10;font-size:15px}
.fh-b27-my-tday{margin-top:12px;background:linear-gradient(135deg,#1C2422,#3E4F49);border-radius:12px;padding:12px 14px}
.fh-b27 .fh-b27-my-tday p{color:#F2ECE0}.fh-b27-my-tday .h{font:800 16px 'Shippori Mincho',serif;color:#E2B33C!important;margin:0 0 4px}
@media (max-width:640px){.fh-b27 .fh-b27-my-why ul{grid-template-columns:1fr}}
</style>"""

JS = r"""(function(){var C=window.FHB27Calc;var S=__SEALS__,T=__TONES__,COL=__COL__;
function $(i){return document.getElementById(i)}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
if(!$('my-y'))return;if(!C){$('my-res').hidden=false;$('my-res').innerHTML='<p>計算の準備ができませんでした。ページを読み込み直してください。</p>';return;}
function card(k,head){var s=S[k.sealNo-1],t=T[k.tone-1],c=COL[s.name.charAt(0)];return {c:c[0],h:'<small>'+head+'</small><p class="nm">KIN'+k.kin+'　'+esc(s.name)+'・音'+k.tone+'（'+esc(t.name)+'）</p><p><b>太陽の紋章「'+esc(s.name)+'」</b>（'+esc(s.kw)+'）<br>'+esc(s.text)+'</p><p><b>銀河の音'+k.tone+'「'+esc(t.name)+'」</b>（'+esc(t.kw)+'）<br>'+esc(t.text)+'</p><p><a href="#my-s'+s.no+'">紋章の説明へ →</a>　<a href="#my-t'+t.no+'">音の説明へ →</a></p>'};}
var y=$('my-y'),m=$('my-m'),d=$('my-d');for(var i=C.GEN.yearMin;i<=C.GEN.yearMax;i++){var o=document.createElement('option');o.value=i;o.textContent=i+'年';if(i===1990)o.selected=true;y.appendChild(o);}
for(i=1;i<=12;i++){o=document.createElement('option');o.value=i;o.textContent=i+'月';m.appendChild(o);}
function days(){var n=new Date(+y.value,+m.value,0).getDate(),v=+d.value||1;d.innerHTML='';for(var k=1;k<=n;k++){var o=document.createElement('option');o.value=k;o.textContent=k+'日';if(k===Math.min(v,n))o.selected=true;d.appendChild(o);}}
y.addEventListener('change',days);m.addEventListener('change',days);days();
var MS=__MS__,MTN=__MT__,MR=__MR__;
function kinOf(se,to){for(var q=1;q<=260;q++){if((q-1)%20+1===se&&(q-1)%13+1===to)return q;}return 0}
function w20(v){v=((v-1)%20+20)%20+1;return v}
function rels(se,to){var g={1:0,6:0,11:0,2:12,7:12,12:12,3:4,8:4,13:4,4:16,9:16,5:8,10:8}[to];return [['guide',w20(se+g),to],['analog',w20(19-se),to],['antipode',w20(se+10),to],['occult',21-se,14-to]];}
function num(t){var h='<div class="fh-b27-my-num" aria-hidden="true"><span>';for(var i=0;i<t%5;i++)h+='<i></i>';h+='</span>';for(i=0;i<Math.floor(t/5);i++)h+='<i></i>';return h+'</div>'}
function todayK(k){var n=new Date(),tk=C.kin(n.getFullYear(),n.getMonth()+1,n.getDate()),ts=S[tk.sealNo-1],tt=T[tk.tone-1],rs=rels(k.sealNo,k.tone),nm=null;
 if(tk.kin===k.kin)nm='あなたと同じKINの日。自分らしさがいちばん出やすい日です。';else rs.forEach(function(z){if(kinOf(z[1],z[2])===tk.kin)nm=MR[z[0]].name+'の日。'+MR[z[0]].text});
 if(!nm){var sc=ts.name.charAt(0)===S[k.sealNo-1].name.charAt(0);nm=(sc?'あなたと同じ色の紋章の日。気持ちが動きやすく、ふだんの力を出しやすい日です。':'あなたとは違う色の紋章の日。いつもと違う見方を取り入れるのに向いた日です。')+'銀河の音'+tk.tone+'「'+esc(tt.name)+'」の日なので、'+esc(MTN[tk.tone].tip);}
 return '<div class="fh-b27-my-tday"><p class="h">今日（'+(n.getMonth()+1)+'月'+n.getDate()+'日）はKIN'+tk.kin+' '+esc(ts.name)+'・音'+tk.tone+'</p><p>'+nm+'</p></div>'}
document.addEventListener('click',function(e){var l=e.target.closest&&e.target.closest('a[href^="#my-"]');if(!l)return;var x=document.getElementById(l.getAttribute('href').slice(1));if(x&&x.tagName==='DETAILS')x.open=true;});
$('my-go').addEventListener('click',function(){var k=C.kin(+y.value,+m.value,+d.value),s=S[k.sealNo-1],t=T[k.tone-1],c=COL[s.name.charAt(0)],mt=MS[k.sealNo],r=$('my-res');r.style.setProperty('--c',c[0]);
 var tb=[['seal','紋章'],['tone','音'],['love','恋愛'],['work','仕事'],['money','お金']];
 var tx={seal:'<p><b>太陽の紋章「'+esc(s.name)+'」</b>（'+esc(s.kw)+'）<br>'+esc(s.text)+'</p>',tone:'<p><b>銀河の音'+k.tone+'「'+esc(t.name)+'」</b>（'+esc(t.kw)+'）<br>'+esc(t.text)+'</p><p>'+esc(MTN[k.tone].tip)+'</p>',love:'<p>'+esc(mt.love)+'</p>',work:'<p>'+esc(mt.work)+'</p>',money:'<p>'+esc(mt.money)+'</p>'};
 var rl=rels(k.sealNo,k.tone).map(function(z){var q=kinOf(z[1],z[2]),ss=S[z[1]-1];return '<div style="--c:'+COL[ss.name.charAt(0)][0]+'"><small>'+esc(MR[z[0]].name)+'</small><b>KIN'+q+' '+esc(ss.name)+'・音'+z[2]+'</b>'+esc(MR[z[0]].text)+'</div>'}).join('');
 r.innerHTML='<div class="fh-b27-my-flip" id="my-flip" aria-hidden="true"><div><div class="bk"></div><div class="fr"><small>'+y.value+'.'+m.value+'.'+d.value+'</small><b>KIN'+k.kin+'</b><em>'+esc(s.name)+'</em>'+num(k.tone)+'<small>銀河の音'+k.tone+'「'+esc(t.name)+'」</small></div></div></div>'+
  '<div class="fh-b27-my-card"><small>'+y.value+'年'+m.value+'月'+d.value+'日生まれ</small><p class="nm">KIN'+k.kin+'　'+esc(s.name)+'・音'+k.tone+'</p><p class="ct">'+esc(mt.catch)+'</p>'+
  '<div class="fh-b27-my-tabs" role="tablist">'+tb.map(function(b,i){return '<button type="button" role="tab" data-t="'+b[0]+'" aria-selected="'+(i?'false':'true')+'">'+b[1]+'</button>'}).join('')+'</div><div class="fh-b27-my-pane" id="my-pane">'+tx.seal+'</div>'+
  '<p style="margin-top:12px"><b>あなたを取り巻く4つのKIN</b></p><div class="fh-b27-my-rels">'+rl+'</div>'+todayK(k)+'<div id="my-lucky"></div>'+
  '<p><a href="#my-s'+s.no+'">紋章の説明へ →</a>　<a href="#my-t'+t.no+'">音の説明へ →</a></p></div>';
 document.querySelectorAll('.fh-b27-my-list details').forEach(function(x){x.classList.toggle('me',x.id==='my-s'+s.no||x.id==='my-t'+t.no)});
 r.hidden=false;var src=document.querySelector('#my-lucky-src [data-s="'+k.sealNo+'"]');if(src)$('my-lucky').appendChild(src.cloneNode(true));
 requestAnimationFrame(function(){requestAnimationFrame(function(){var f=$('my-flip');if(f)f.classList.add('on');});});
 r.querySelectorAll('.fh-b27-my-tabs button').forEach(function(b){b.addEventListener('click',function(){r.querySelectorAll('.fh-b27-my-tabs button').forEach(function(z){z.setAttribute('aria-selected','false')});b.setAttribute('aria-selected','true');$('my-pane').innerHTML=tx[b.getAttribute('data-t')];});});
});
var n=new Date(),tk=C.kin(n.getFullYear(),n.getMonth()+1,n.getDate()),ts=S[tk.sealNo-1];$('my-today').innerHTML='<span>今日（'+(n.getMonth()+1)+'月'+n.getDate()+'日）のKIN</span><b>KIN'+tk.kin+'</b><span>'+esc(ts.name)+'・音'+tk.tone+'（'+esc(T[tk.tone-1].name)+'）</span>';
})();"""


def build(sample, updated):
    seals, tones = load()
    H = []
    a = H.append
    a(CSS)
    a('<div class="fh-b27" data-fh-page="maya">\n<div class="fh-b27-note">')
    a('''<header class="fh-b27-hero">
  <div class="fh-b27-my-emb" aria-hidden="true"></div>
  <div class="fh-b27-hero-body">
    <span class="fh-b27-tape">マヤ暦（ドリームスペル）</span>
    <h1 class="fh-b27-title">マヤ暦占い<br>生年月日でKINと紋章を調べる</h1>
    <p class="fh-b27-lead">生年月日を選ぶだけで、マヤ暦のKIN（1〜260）と、20の太陽の紋章・13の銀河の音を計算します。今日のKINもわかります。計算は生年月日まるごと診断と同じです。</p>
    <p class="fh-b27-my-today" id="my-today" aria-live="polite"></p>
  </div>
</header>''')
    items = [("b27-my-calc", "KINを調べる"), ("b27-my-seals", "20の太陽の紋章"), ("b27-my-tones", "13の銀河の音"), ("b27-my-color", "4つの色の意味"),
             ("b27-my-how", "KINの出し方"), ("b27-my-about", "マヤ暦（ドリームスペル）とは"), ("b27-my-faq", "よくある質問")]
    a('<nav class="fh-b27-toc" aria-label="目次"><strong>このページの内容</strong><ol>' + "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in items) + "</ol></nav>")
    n = [1]

    def h2(t):
        s = f'<h2><span class="fh-b27-n">{n[0]}</span><span>{t}</span></h2>'
        n[0] += 1
        return s
    a('''<div class="fh-b27-my-why">
  <p class="fh-b27-my-why-h">マヤ暦は「260日のリズム」で自分を知る占い</p>
  <p>誕生日占いは「月日」で決まるので、同じ誕生日の人は同じ結果になります。マヤ暦のKINは<b>生まれた年・月・日すべて</b>で決まる1〜260の番号で、同じ誕生日でも生まれ年が違えばKINが変わります。<b>あなただけの番号</b>から、持って生まれた役割と、毎日変わるエネルギーを読みます。</p>
  <ul>
    <li><b>紋章×音の260通り</b>20の太陽の紋章（性質）と13の銀河の音（動き方）の組み合わせで、一人ひとりを細かく読み分けます。</li>
    <li><b>あなたを囲む4つのKIN</b>導く力（ガイド）、支え合う人（類似）、鍛え合う人（反対）、隠れた力（神秘）まで計算します。</li>
    <li><b>今日のエネルギー</b>KINは毎日1つずつ進みます。今日のKINとあなたの関係から、その日の過ごし方のヒントがわかります。</li>
  </ul>
  <p class="fh-b27-small">このページのマヤ暦は、古代マヤの暦そのものではなく、1987年以降に広まった「ドリームスペル」の数え方です。誕生日どうしの相性は<a href="/compatibility/">誕生日相性占い</a>もどうぞ。</p>
</div>''')
    a(f'''<section class="fh-b27-sec" id="b27-my-calc">
  {h2("KINを調べる")}
  <div class="fh-b27-my-box">
    <div class="fh-b27-my-form"><select id="my-y" aria-label="生まれた年"></select><select id="my-m" aria-label="生まれた月"></select><select id="my-d" aria-label="生まれた日"></select><button type="button" class="fh-b27-my-btn" id="my-go">KINを調べる</button></div>
    <div class="fh-b27-my-res" id="my-res" aria-live="polite" hidden></div>
    <p class="fh-b27-small">1930〜2030年の生まれに対応しています。生年月日は送信も保存もしません（このページの中だけで計算します）。</p>
  </div>
  <noscript><p class="fh-b27-small">計算にはJavaScriptを使います。下の「KINの出し方」で手でも計算できます。</p></noscript>
</section>''')
    a("<!--Ads1-->")
    col = lambda name: COLOR[name[0]][0]
    TC = {1: '目的を決めて、人と力を集める', 2: '迷いの中から答えを選び取る', 3: '人と人をつなぎ、動きを生む', 4: '形を整えて、土台をつくる', 5: '中心に立って、みんなを引っ張る', 6: 'バランスをとって、流れを整える', 7: 'ひらめきを受け取り、伝える', 8: 'みんなの調和を大切にする', 9: '目標に向かって、粘り強く進む', 10: '思いを形にして、結果を出す', 11: '古いものを手放し、身軽になる', 12: '仲間と力を合わせて広げる', 13: 'すべてを受け入れて、次へつなぐ'}
    grid = "".join(f'<a href="#my-s{s["no"]}" style="--c:{col(s["name"])}"><i></i>{s["no"]}. {esc(s["name"])}</a>' for s in seals)
    det = "".join(f'<details id="my-s{s["no"]}" style="--c:{col(s["name"])}"><summary><span class="fh-b27-my-bd">{s["no"]}</span><span class="fh-b27-my-sm"><b>{esc(MT.SEALS[s["no"]]["catch"])}</b><small>{esc(s["name"])}｜{esc(s["kw"])}</small></span></summary><p>{esc(s["text"])}</p><p><b>恋愛：</b>{esc(MT.SEALS[s["no"]]["love"])}</p><p><b>仕事：</b>{esc(MT.SEALS[s["no"]]["work"])}</p><p><b>お金：</b>{esc(MT.SEALS[s["no"]]["money"])}</p></details>' for s in seals)
    a(f'''<section class="fh-b27-sec" id="b27-my-seals">
  {h2("20の太陽の紋章")}
  <p>太陽の紋章は、その人の本質や持ち味を表す20のシンボルです。キーワードは「行動／力／本質」の3つの言葉で表されます。大きな文字は「その紋章を持つ人をひとことで表すと」です。押すと性格・恋愛・仕事・お金が開きます。上でKINを調べると、あなたの紋章と音に印がつきます。</p>
  <div class="fh-b27-my-list">{det}</div>
</section>''')
    det2 = "".join(f'<details id="my-t{t["no"]}"><summary><span class="fh-b27-my-bd">{t["no"]}</span><span class="fh-b27-my-sm"><b>{esc(TC[t["no"]])}</b><small>音{t["no"]}・{esc(t["name"])}｜{esc(t["kw"])}</small></span></summary><p>{esc(t["text"])}</p></details>' for t in tones)
    a(f'''<section class="fh-b27-sec" id="b27-my-tones">
  {h2("13の銀河の音")}
  <p>銀河の音は、紋章の力をどんなリズムで使うかを表す1〜13の数です。1で始まり13で締めくくる流れになっていて、紋章と組み合わせて読みます。大きな文字は「その音の動き方」です。</p>
  <div class="fh-b27-my-list fh-b27-my-tl">{det2}</div>
</section>''')
    cs = "".join(f'<div style="--c:{v[0]}"><b>{k}の紋章</b>{esc(v[1])}<br><small>{esc(v[2])}</small></div>' for k, v in COLOR.items())
    a(f'''<section class="fh-b27-sec" id="b27-my-color">
  {h2("4つの色の意味")}
  <p>20の紋章は、赤・白・青・黄の4つの色が順にくり返されています。同じ色の紋章は、物事への関わり方が似ているとされます。</p>
  <div class="fh-b27-my-colors">{cs}</div>
</section>''')
    a(f'''<section class="fh-b27-sec" id="b27-my-how">
  {h2("KINの出し方")}
  <ol>
    <li>基準の日を<b>2013年7月26日＝KIN164</b>とします。</li>
    <li>基準の日から生まれた日までの日数を数えます。このとき<b>2月29日は数えません</b>。</li>
    <li>KIN＝（163＋日数）を260で割った余り＋1。基準の日より前に生まれた人は、日数をマイナスにします。</li>
    <li>紋章の番号＝（KIN−1）を20で割った余り＋1、音の番号＝（KIN−1）を13で割った余り＋1。</li>
  </ol>
  <p>2月29日を数えないため、同じ月日でも1年ごとにKINは105ずつ進みます。KINを出すには生まれた年が必要です。2月29日生まれは、前日の2月28日と同じKINになります。</p>
  <p class="fh-b27-small">このサイトの計算は、公開されている10日分の値（2012年12月21日＝KIN207、2026年8月27日＝KIN1 など）とすべて一致することを確かめています。</p>
</section>''')
    a(f'''<section class="fh-b27-sec" id="b27-my-about">
  {h2("マヤ暦（ドリームスペル）とは")}
  <div class="fh-b27-my-note">このページの「マヤ暦」は、ホゼ・アグエイアスとロイディーン・アグエイアスが1987年以降に発表した<b>「ドリームスペル」（日本では「13の月の暦」とも呼ばれます）</b>にもとづく現代の占いです。古代マヤの人々が使っていた暦そのものではありません。</div>
  <p>古代マヤの遺跡や碑文に残る260日の暦（ツォルキン）を今の暦に当てはめるときは、学問の世界では別の数え方が使われます。ドリームスペルは独自の基準日から数え、2月29日を数えないため、同じ日でも古代マヤ式とは番号がずれます。</p>
  <p>ドリームスペルでは、1日ごとに20の太陽の紋章と13の銀河の音が組み合わさって進み、260日でひと回りします。生まれた日のKINを「銀河の署名」と呼び、その人らしさを読み解くヒントにします。</p>
</section>''')
    qa = "".join(f'<details{" open" if i == 0 else ""}><summary>Q. {q}</summary><p>A. {x}</p></details>' for i, (q, x) in enumerate(FAQ))
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in FAQ]}
    a(f'''<section class="fh-b27-sec" id="b27-my-faq">
  {h2("よくある質問")}
  <div class="fh-b27-my-qa">{qa}</div>
</section>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<section class="fh-b27-sec">
  <div class="fh-b27-links">
    <a href="/unsei-2027/maya/"><b>マヤ暦 2027年の運勢 →</b><small>20の紋章別・白い魔法使いの年と紋章の日</small></a>
    <a href="/seinengappi/"><b>生年月日まるごと診断 →</b><small>マヤ暦・九星・宿曜・四柱推命などを1枚に</small></a>
    <a href="/shukuyo/"><b>宿曜占星術 →</b><small>月の暦で本命宿と相性を見る</small></a>
    <a href="/366uranai/"><b>366日の誕生日占い →</b><small>誕生日から性格・相性・2027年の運勢</small></a>
  </div>
</section>''')
    lucky = "".join(f'<div data-s="{no}">{aff_extra.goods_box("あなたの紋章のお守りアイテム", [(v["lucky"][0], v["lucky"][0], v["lucky"][1], "goods")])}</div>' for no, v in MT.SEALS.items())
    a(f'<div id="my-lucky-src" hidden>{lucky}</div>')
    js = (JS.replace("__MS__", json.dumps(MT.SEALS, ensure_ascii=False)).replace("__MT__", json.dumps(MT.TONES, ensure_ascii=False)).replace("__MR__", json.dumps(MT.REL, ensure_ascii=False))
          .replace("__SEALS__", json.dumps(seals, ensure_ascii=False, separators=(",", ":"))).replace("__TONES__", json.dumps(tones, ensure_ascii=False, separators=(",", ":")))
          .replace("__COL__", json.dumps({k: [v[0]] for k, v in COLOR.items()}, ensure_ascii=False)))
    up = dt.date.fromisoformat(updated)
    a(f'<p class="fh-b27-foot">KINはドリームスペルの決まりで、このサイトで計算しています。紋章と音の説明はこのサイトで書いたものです。占いは楽しみと気づきのためにお読みください。<br>'
      f'最終更新日：{up.year}年{up.month}月{up.day}日／<a href="/about/">この記事の作成方針について</a></p>')
    a("</div>\n</div>")
    a(f"<script>document.addEventListener('DOMContentLoaded',function(){{{js}}});</script>")
    title = "マヤ暦占い｜生年月日でKIN・太陽の紋章・銀河の音を計算【無料・今日のKINも】"
    desc = ("生年月日を選ぶだけでマヤ暦（ドリームスペル）のKIN、20の太陽の紋章、13の銀河の音を無料で計算。今日のKINも表示。紋章と音の意味一覧、4つの色、KINの出し方も紹介します。")
    out = shell(title, desc, URL, "\n".join(H), sample, SCRIPTS)
    assert "！" not in out
    return out


def main():
    updated = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    for sample, path in ((False, os.path.join(OUT, "maya.html")), (True, os.path.join(OUT, "sample", "maya.html"))):
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(build(sample, updated))
        print("→", os.path.relpath(path, WORK))


if __name__ == "__main__":
    main()
