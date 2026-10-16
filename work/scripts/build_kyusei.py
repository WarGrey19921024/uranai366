"""九星気学のページ（新しい固定ページ /kyusei/）を作る（2026-10-16 本人の決定：「九星気学」月1万〜10万回の検索に入る）。
本命星の計算は共通JS（FHB27Calc.honmei＝立春で年が切り替わる。366日・まるごと診断と同じ）。
九星の象意・相性表・2027年の年盤／月盤は work/knowledge/04_九星気学.md（スクリプトで計算・照合済み）から。
"""
import datetime as dt, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_hub import OUT, WORK, shell  # noqa: E402
from build_shukuyo import md_rows, esc  # noqa: E402

import kyusei_texts as KT  # noqa: E402
import aff_extra  # noqa: E402
URL = "/kyusei/"
KNOW = os.path.join(WORK, "knowledge", "04_九星気学.md")
SCRIPTS = ("fh-b27-setsuiri.js", "fh-b27-kyureki.js", "fh-b27.js")
STARS = ['一白水星', '二黒土星', '三碧木星', '四緑木星', '五黄土星', '六白金星', '七赤金星', '八白土星', '九紫火星']
COLOR = ["#F4F1EA", "#3A3530", "#3D8B8B", "#5E9B5E", "#D9B23C", "#E9E6DC", "#C8463C", "#EFEBE0", "#7A4D9C"]
# 2027年の年盤（九紫中宮）：本命星→方位（knowledge 3-4）
POS2027 = {1: "北西", 2: "西", 3: "北東", 4: "南", 5: "北", 6: "南西", 7: "東", 8: "南東", 9: "中央"}
# 本命星別 2027年の運勢（このサイトの言葉。その星が2027年に入る宮の一般的な意味＋九紫との五行の関係から）
YEAR2027 = {
    1: ("北西（乾宮）", "責任と充実の年", "大きな仕事や目上の人からの期待が集まり、忙しくも手ごたえのある一年です。引き受けたことを最後までやり通すと評価につながります。働きすぎて体を休める時間がなくならないよう、予定に余白を作りましょう。"),
    2: ("西（兌宮）", "実りと楽しみの年", "これまでの努力が形になり、収入や人付き合いに楽しみが増える年です。会食や趣味など、人と喜びを分かち合う場面で運が開きます。気がゆるんで出費や口約束が増えやすいので、使い道を決めてから楽しみましょう。"),
    3: ("北東（艮宮）", "変化と切り替えの年", "仕事や住まい、人間関係などに切り替えのタイミングが訪れやすい年です。急がずに一度立ち止まり、続けるものと手放すものを整理すると、次の流れに乗りやすくなります。家族や身内との話し合いも大切に。"),
    4: ("南（離宮）", "注目と表舞台の年", "これまでの取り組みが表に出て、人から注目されやすい年です。学びや見た目を整えることに追い風が吹きます。一方で、隠していたことも明らかになりやすいので、誠実な行動を心がけると、得た評価が長く続きます。"),
    5: ("北（坎宮）", "充電と準備の年", "表立った動きより、内側を整えるのに向いた静かな年です。新しく大きく始めるより、学び直しや体調管理、信頼できる人との関係づくりに力を注ぐと、次の年からの上昇につながります。焦らず力をためましょう。"),
    6: ("南西（坤宮）", "地道な積み重ねの年", "足元を固め、こつこつ努力することが実を結ぶ年です。目立つ成果はすぐに出なくても、準備や下支えの役目で信頼を得られます。人を支える立場に回ることで、自分の土台も強くなっていきます。"),
    7: ("東（震宮）", "スタートと発展の年", "新しいことを始める勢いに恵まれる年です。温めてきた計画を動かしたり、声を上げて発信したりすると、思った以上の反応があります。勢い任せの発言や早とちりには気をつけ、準備を一つ確かめてから動きましょう。"),
    8: ("南東（巽宮）", "信用とご縁の年", "人とのつながりが広がり、信用が形になる年です。紹介や取引、遠方との縁など、人を通じてよい話が舞い込みます。頼まれごとが重なって迷ったら、自分にとって大切なものを優先して、丁寧に返事をしましょう。"),
    9: ("中央（中宮）", "節目と見直しの年", "自分の星が年盤の中央に入る、9年に一度の節目の年です。周りから注目されやすい一方で、物事が思うように進まない場面もあります。新しく広げるより、これまでを見直し、生活や考え方を整えることで次の9年の土台ができます。"),
}
FAQ = [
    ("本命星とは何ですか。", "生まれた年で決まる九星のことで、九星気学でその人の基本の性格や運勢を見るときに使います。一白水星から九紫火星までの9つがあり、1年ごとに1つずつ数が減っていきます。"),
    ("1月や2月の初めに生まれた人の本命星は。", "九星気学では年が立春（毎年2月4日ごろ）で切り替わるため、1月1日から立春の前日までに生まれた人は、前の年の星になります。このページの計算は、その切り替えを日付ごとに反映しています。"),
    ("2027年はどんな年ですか。", "2027年は九紫火星が年盤の中央に入る年で、干支は丁未です（どちらも2027年2月4日の立春から）。明るさや知性、名誉を表す星の年なので、物事がはっきりし、学びや表現に追い風が吹く年と読みます。"),
    ("2027年の凶方位はどこですか。", "年盤では、五黄殺が北、暗剣殺が南、歳破が北東です（2027年2月4日の立春から2028年2月4日の立春まで）。引っ越しや旅行の方角を考えるときの目安にしてください。"),
    ("相性がよくない星どうしは付き合わないほうがいいですか。", "五行の関係で「剋される」組み合わせでも、付き合わないほうがいいという意味ではありません。お互いの違いを知り、相手の得意を認めると、刺激を与え合える関係になります。"),
    ("月命星も出ますか。", "このページでは本命星を扱っています。生まれた月の九星（月命星）は、生年月日まるごと診断と366日の誕生日ページで、2027年の月ごとの運勢として見られます。"),
]


def esc_(s):
    return esc(s)


def load():
    rows = md_rows(KNOW, "### 3-1.")[1:]
    info = {r[0]: {"kw": r[1], "good": r[2], "bad": r[3], "color": r[4].split("／")[0], "sym": r[5]} for r in rows}
    base = {r[1]: {"yomi": r[2], "gogyo": r[3], "pos": r[4]} for r in md_rows(KNOW, "### 九星の一覧")[1:] if len(r) > 4 and r[1] in STARS}
    aisho = {}
    for r in md_rows(KNOW, "### 3-3.")[1:]:
        if r[0] in STARS:
            aisho[r[0]] = r[1:10]
    months = [r for r in md_rows(KNOW, "### 3-5.")[1:] if len(r) >= 8]
    assert len(info) == 9 and len(aisho) == 9 and len(base) == 9
    return info, base, aisho, months


CSS = """<style id="fh-b27-ky-css">
.fh-b27[data-fh-page="kyusei"]{--ink:#F1ECE2;--sub:#D5CCBC;--mute:#ADA392;--paper:#1A1F1C;--deep:#141815;--line:#4E5A50;--gold:#D4AF5A;--ver:#C2453A;--cream:#F6F0E2;--cream-ink:#26211B}
.fh-b27[data-fh-page="kyusei"] a{color:#E8C878}
.fh-b27[data-fh-page="kyusei"] .fh-b27-note{border-left:0;border-radius:4px;background-color:var(--paper);
 background-image:radial-gradient(circle at 15% 0%,rgba(194,69,58,.18),transparent 35%),radial-gradient(circle at 100% 100%,rgba(212,175,90,.12),transparent 40%),repeating-linear-gradient(45deg,rgba(255,255,255,.025) 0 2px,transparent 2px 9px);
 background-size:auto,auto,auto;box-shadow:0 14px 40px rgba(0,0,0,.5),inset 0 0 0 2px rgba(194,69,58,.55),inset 0 0 0 7px var(--paper),inset 0 0 0 8px rgba(212,175,90,.4)}
.fh-b27-ky-ban{display:grid;grid-template-columns:repeat(3,44px);grid-template-rows:repeat(3,44px);gap:3px;flex:0 0 auto;padding:10px;background:rgba(0,0,0,.25);border:1px solid rgba(212,175,90,.5);margin:6px}
.fh-b27-ky-ban span{display:flex;align-items:center;justify-content:center;font:800 18px 'Shippori Mincho',serif;color:#1A1F1C;border-radius:2px}
.fh-b27[data-fh-page="kyusei"] .fh-b27-hero{align-items:center}
.fh-b27[data-fh-page="kyusei"] .fh-b27-tape{transform:none;border-radius:2px;background:var(--ver);color:#FFF4E8;font-family:'Shippori Mincho',serif;letter-spacing:.2em}
.fh-b27[data-fh-page="kyusei"] .fh-b27-title{font-family:'Shippori Mincho',serif;font-weight:800;font-size:31px}
.fh-b27[data-fh-page="kyusei"] h2{font-family:'Shippori Mincho',serif;font-weight:800;font-size:24px}
.fh-b27[data-fh-page="kyusei"] h2 .fh-b27-n{border:0;border-radius:2px;background:var(--ver);color:#FFF4E8;font-family:'Shippori Mincho',serif}
.fh-b27[data-fh-page="kyusei"] h3{border-bottom:1px solid rgba(212,175,90,.35)}
.fh-b27[data-fh-page="kyusei"] .fh-b27-toc{border-style:solid;border-radius:2px;border-color:rgba(212,175,90,.35)}
.fh-b27[data-fh-page="kyusei"] .fh-b27-toc ol{columns:2;column-gap:28px}
.fh-b27-ky-box{border:1px solid rgba(212,175,90,.4);border-radius:4px;background:rgba(20,24,21,.8);padding:16px;display:flex;flex-direction:column;gap:12px}
.fh-b27-ky-form{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.fh-b27-ky-form b{font-size:13px;color:var(--gold);min-width:4em}
.fh-b27-ky-form select{min-height:44px;border-radius:2px;border:1px solid var(--line);background:var(--deep);color:var(--ink);font:inherit;padding:0 8px}
.fh-b27-ky-btn{min-height:44px;border:0;border-radius:2px;background:var(--ver);color:#FFF4E8;font:inherit;font-weight:700;padding:0 18px;cursor:pointer}
.fh-b27-ky-res{background:var(--cream);color:var(--cream-ink);border-radius:2px;padding:16px 18px;line-height:1.85;border-top:6px solid var(--c,#D4AF5A)}
.fh-b27 .fh-b27-ky-res p,.fh-b27 .fh-b27-ky-res b{color:var(--cream-ink)}
.fh-b27-ky-res .nm{font:800 32px 'Shippori Mincho',serif}
.fh-b27-ky-res small{color:#6A6150}
.fh-b27 .fh-b27-ky-res a{color:#9A3328;font-weight:700}
.fh-b27-ky-t{width:100%;border-collapse:collapse;font-size:14px;line-height:1.7}
.fh-b27-ky-t caption{text-align:left;color:var(--sub);font-size:13px;padding-bottom:4px}
.fh-b27-ky-t th,.fh-b27-ky-t td{border-bottom:1px solid rgba(212,175,90,.18);padding:7px 6px;text-align:left;vertical-align:top}
.fh-b27-ky-t thead th{color:var(--gold);font-size:13px}
.fh-b27-ky-t tbody th{white-space:nowrap;font-family:'Shippori Mincho',serif}
.fh-b27-ky-wrap{overflow-x:auto}
.fh-b27-ky-mx{min-width:540px;text-align:center}.fh-b27-ky-mx td,.fh-b27-ky-mx th{text-align:center}
.fh-b27-ky-cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
.fh-b27-ky-cards div{border:1px solid rgba(212,175,90,.3);border-top:5px solid var(--c);border-radius:2px;background:rgba(20,24,21,.6);padding:10px 12px;font-size:13.5px;line-height:1.75}
.fh-b27-ky-cards b{display:block;font:800 18px 'Shippori Mincho',serif}
.fh-b27-ky-cards small{color:var(--mute)}
.fh-b27-ky-y{display:flex;flex-direction:column;gap:8px}
.fh-b27-ky-y details{border:1px solid rgba(212,175,90,.25);border-left:5px solid var(--c);border-radius:2px;background:rgba(20,24,21,.55);padding:8px 14px}
.fh-b27-ky-y summary{cursor:pointer;font-family:'Shippori Mincho',serif;font-weight:800;font-size:16.5px}
.fh-b27-ky-y summary small{font-family:'Zen Kaku Gothic New',sans-serif;font-weight:400;color:var(--mute);font-size:12.5px;margin-left:8px}
.fh-b27-ky-y p{font-size:14.5px;line-height:1.9;margin-top:6px}
.fh-b27-ky-grid9{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:4px;max-width:420px;margin:0 auto}
.fh-b27-ky-grid9 div{border:1px solid rgba(212,175,90,.35);padding:10px 4px;text-align:center;background:rgba(20,24,21,.6);font-size:12.5px;line-height:1.5}
.fh-b27-ky-grid9 b{display:block;font:800 16px 'Shippori Mincho',serif;color:var(--ink)}
.fh-b27-ky-grid9 .bad{border-color:var(--ver);background:rgba(194,69,58,.15)}
.fh-b27-ky-qa details{border-bottom:1px solid rgba(212,175,90,.2);padding:8px 2px}
.fh-b27-ky-qa summary{cursor:pointer;font-weight:700}
.fh-b27-ky-qa p{margin-top:6px;font-size:14.5px}
@media (max-width:640px){.fh-b27-ky-cards{grid-template-columns:1fr}.fh-b27[data-fh-page="kyusei"] .fh-b27-toc ol{columns:1}.fh-b27-ky-ban{grid-template-columns:repeat(3,34px);grid-template-rows:repeat(3,34px);margin:16px}.fh-b27-ky-ban span{font-size:14px}.fh-b27[data-fh-page="kyusei"] .fh-b27-title{font-size:26px}}
.fh-b27-ky-rv{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:4px;max-width:300px;margin:0 auto 14px}
.fh-b27-ky-rv span{aspect-ratio:1/1;display:flex;flex-direction:column;align-items:center;justify-content:center;border:1px solid rgba(212,175,90,.35);background:rgba(20,24,21,.7);
 font:800 20px 'Shippori Mincho',serif;color:var(--sub);opacity:0;transform:scale(.6);animation:fh-b27-ky-in .45s ease forwards;animation-delay:calc(var(--i)*.08s)}
.fh-b27-ky-rv span small{font:400 10.5px 'Zen Kaku Gothic New',sans-serif;color:var(--mute)}
.fh-b27-ky-rv span.me{background:var(--c);color:#1A1F1C;border-color:var(--gold);animation:fh-b27-ky-in .45s ease forwards,fh-b27-ky-glow 1.6s ease-in-out .9s 3;animation-delay:calc(var(--i)*.08s),.9s}
.fh-b27-ky-rv span.me small{color:#1A1F1C;font-weight:700}
@keyframes fh-b27-ky-in{to{opacity:1;transform:none}}
@keyframes fh-b27-ky-glow{50%{box-shadow:0 0 0 4px rgba(212,175,90,.6),0 0 26px 6px var(--c)}}
.fh-b27-ky-card{opacity:0;transform:translateY(16px);animation:fh-b27-ky-in .6s ease 1s forwards}
.fh-b27-ky-res .ct{font-family:'Shippori Mincho',serif;font-size:16px;color:#7A2E22;margin:-4px 0 8px}
.fh-b27-ky-tabs{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 8px}
.fh-b27-ky-tabs button{min-height:38px;border:1px solid #CBB98F;border-radius:999px;background:#FFFBF1;color:#5A4A2A;font:inherit;font-size:14px;font-weight:700;padding:0 14px;cursor:pointer}
.fh-b27-ky-tabs button[aria-selected="true"]{background:#9A3328;border-color:#9A3328;color:#FFF4E8}
.fh-b27-ky-pane{background:#FFFDF7;border-radius:4px;padding:12px 14px;min-height:5em}
.fh-b27-ky-27{margin-top:14px;border-top:1px dashed #CBB98F;padding-top:12px}
.fh-b27-ky-27 h4{margin:0 0 4px;font:800 18px 'Shippori Mincho',serif;color:#26211B}
.fh-b27 .fh-b27-ky-27 ul{margin:6px 0;padding-left:1.2em}
.fh-b27 .fh-b27-ky-27 li{margin:2px 0}
.fh-b27-ky-chips{display:flex;flex-wrap:wrap;gap:6px;margin:4px 0}
.fh-b27-ky-chips span{border-radius:999px;background:#EFE4C8;color:#4A3B1C;padding:2px 12px;font-size:13.5px;font-weight:700}
.fh-b27-ky-chips span.g{background:#DCEBD9;color:#22462A}
.fh-b27-ky-ms{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:4px;margin:6px 0}
.fh-b27-ky-ms div{background:#FFFBF1;border:1px solid #E3D6B5;border-radius:4px;padding:5px 3px;text-align:center;font-size:11.5px;line-height:1.45;color:#4A3B1C}
.fh-b27-ky-ms div b{display:block;font-size:12.5px;color:#26211B}
.fh-b27-ky-ms div.w{background:#F7DCD6;border-color:#D79A8E}
.fh-b27-ky-lucky{margin-top:12px}
.fh-b27[data-fh-page="kyusei"] .fh-b27-ky-res a.fh-b27-shopbtn{color:#FFF5D6}
.fh-b27 .fh-b27-ky-res .fh-b27-adgoods-h{color:#26211B}
@media (max-width:640px){.fh-b27-ky-ms{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media (prefers-reduced-motion:reduce){.fh-b27-ky-rv span,.fh-b27-ky-card{animation:none;opacity:1;transform:none}}
.fh-b27-ky-why{border:1.5px solid rgba(212,175,90,.5);border-radius:6px;background:linear-gradient(135deg,rgba(194,69,58,.18),rgba(212,175,90,.08));padding:16px 18px}
.fh-b27-ky-why-h{font:800 20px 'Shippori Mincho',serif;color:var(--gold);margin:0 0 6px}
.fh-b27 .fh-b27-ky-why ul{list-style:none;padding:0;margin:10px 0;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.fh-b27 .fh-b27-ky-why li{margin:0;background:var(--cream);color:var(--cream-ink);border-radius:6px;padding:10px 12px;font-size:13.5px;line-height:1.7}
.fh-b27-ky-why li::before{content:none}.fh-b27 .fh-b27-ky-why li b{display:block;color:#9A3328;font-size:15px}
.fh-b27-ky-ml{min-width:760px;font-size:12.5px}.fh-b27-ky-ml td{text-align:center}
.fh-b27-ky-ml th[scope=row]{white-space:nowrap}.fh-b27-ky-ml th[scope=row] i{display:inline-block;width:10px;height:10px;border-radius:2px;background:var(--c);margin-right:6px;box-shadow:inset 0 0 0 1px rgba(0,0,0,.3)}
.fh-b27-ky-ms div small.l{display:block;color:#1F6B3A;font-weight:700}
@media (max-width:640px){.fh-b27 .fh-b27-ky-why ul{grid-template-columns:1fr}}
</style>"""

JS = r"""(function(){var C=window.FHB27Calc;var ST=__STARS__,INFO=__INFO__,AI=__AISHO__,COL=__COL__,POS=__POS__,Y27=__Y27__;
function $(i){return document.getElementById(i)}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
if(!$('ky-ay'))return;if(!C){$('ky-res').hidden=false;$('ky-res').innerHTML='<p>計算の準備ができませんでした。ページを読み込み直してください。</p>';return;}
function fill(p){var y=$(p+'y'),m=$(p+'m'),d=$(p+'d');for(var i=C.GEN.yearMin;i<=C.GEN.yearMax;i++){var o=document.createElement('option');o.value=i;o.textContent=i+'年';if(i===1990)o.selected=true;y.appendChild(o);}
 for(i=1;i<=12;i++){o=document.createElement('option');o.value=i;o.textContent=i+'月';m.appendChild(o);}
 function days(){var n=new Date(+y.value,+m.value,0).getDate(),v=+d.value||1;d.innerHTML='';for(var k=1;k<=n;k++){var o=document.createElement('option');o.value=k;o.textContent=k+'日';if(k===Math.min(v,n))o.selected=true;d.appendChild(o);}}
 y.addEventListener('change',days);m.addEventListener('change',days);days();}
fill('ky-a');fill('ky-b');
function get(p){var y=+$(p+'y').value,m=+$(p+'m').value,d=+$(p+'d').value;return {y:y,m:m,d:d,h:C.honmei(y,m,d)};}
var T=__KT__,LD=__LD__,MS=__MS__,PAL=__PAL__,ML=__ML__,OPP={1:8,8:1,2:7,7:2,3:6,6:3,4:5,5:4};
function at(c,p){return ((c-1+p)%9)+1}function pal(c,s){return ((s-c)%9+9)%9}
$('ky-go').addEventListener('click',function(){var a=get('ky-a'),s=a.h.star,nm=ST[s-1],x=INFO[nm],t=T[nm],yy=Y27[s];var r=$('ky-res');r.style.setProperty('--c',COL[s-1]);
 var bd=[8,4,6,7,0,2,3,5,1].map(function(p,i){var st=at(9,p);return '<span style="--i:'+i+';--c:'+COL[st-1]+'" class="'+(st===s?'me':'')+'">'+st+'<small>'+(st===s?'あなた':PAL[p][0])+'</small></span>'}).join('');
 var tb=[['char','性格'],['love','恋愛'],['work','仕事'],['money','お金'],['people','人付き合い']];
 var tx={char:'<p><b>性質：</b>'+esc(x.kw)+'</p><p><b>長所：</b>'+esc(x.good)+'<br><b>気をつけたい点：</b>'+esc(x.bad)+'</p><p><b>色：</b>'+esc(x.color)+'　<b>象徴：</b>'+esc(x.sym)+'</p>',love:'<p>'+esc(t.love)+'</p>',work:'<p>'+esc(t.work)+'</p>',money:'<p>'+esc(t.money)+'</p>',people:'<p>'+esc(t.people)+'</p>'};
 var ms=MS.map(function(m,mi){var p=pal(m[1],s),w=false,lk=ML[s][mi];if(m[1]!==5){var q=pal(m[1],5);w=(p===q||p===OPP[q]);}return '<div class="'+(w?'w':'')+'"><b>'+m[0]+'</b>'+PAL[p][0]+'<br>'+PAL[p][1]+(w?'<br>※凶方位':'')+(lk&&lk.length?'<small class="l">吉：'+lk.join('・')+'</small>':'')+'</div>'}).join('');
 var ai=AI[nm],g1=[],g2=[];ai.forEach(function(k,i){if(k==='◎')g1.push(ST[i]);else if(k==='○')g2.push(ST[i]);});
 var ld=LD[s].length?LD[s].map(function(d){return '<span class="g">'+d+'</span>'}).join(''):'<span>年盤では吉方位なし</span>';
 r.innerHTML='<div class="fh-b27-ky-rv" aria-hidden="true">'+bd+'</div><div class="fh-b27-ky-card"><small>'+a.y+'年'+a.m+'月'+a.d+'日生まれの本命星</small><p class="nm">'+esc(nm)+'</p><p class="ct">'+esc(t.catch)+'</p>'+
  (a.h.prev?'<p><small>立春より前の生まれなので、前の年（'+a.h.etoYear+'年）の星です。</small></p>':'')+
  '<div class="fh-b27-ky-tabs" role="tablist">'+tb.map(function(b,i){return '<button type="button" role="tab" data-t="'+b[0]+'" aria-selected="'+(i?'false':'true')+'">'+b[1]+'</button>'}).join('')+'</div><div class="fh-b27-ky-pane" id="ky-pane">'+tx.char+'</div>'+
  '<div class="fh-b27-ky-27"><h4>2027年は「'+esc(yy[1])+'」</h4><p>'+esc(nm)+'は2027年、年盤の'+esc(yy[0])+'に入ります。'+esc(yy[2])+'</p>'+
  '<p><b>2027年にやるとよいこと</b></p><ul>'+t.do.map(function(d){return '<li>'+esc(d)+'</li>'}).join('')+'</ul><p><b>気をつけたいこと：</b>'+esc(t.avoid)+'</p>'+
  '<p><b>2027年の吉方位（年盤）</b></p><div class="fh-b27-ky-chips">'+ld+'</div>'+
  '<p><b>2027年の月ごとの流れ</b><br><small>その月、あなたの星が月盤のどこに入るか。赤は五黄殺・暗剣殺に当たる月です。</small></p><div class="fh-b27-ky-ms">'+ms+'</div>'+
  '<p><b>助けてくれる星（◎）</b></p><div class="fh-b27-ky-chips">'+g1.map(function(n){return '<span class="g">'+n+'</span>'}).join('')+'</div><p><b>あなたが支える星（○）</b></p><div class="fh-b27-ky-chips">'+g2.map(function(n){return '<span>'+n+'</span>'}).join('')+'</div></div>'+
  '<div class="fh-b27-ky-lucky" id="ky-lucky"></div><p><a href="#ky-y'+s+'">'+esc(nm)+'の2027年を一覧で見る →</a></p></div>';
 r.hidden=false;var src=document.querySelector('#ky-lucky-src [data-s="'+s+'"]');if(src)$('ky-lucky').appendChild(src.cloneNode(true));
 r.querySelectorAll('.fh-b27-ky-tabs button').forEach(function(b){b.addEventListener('click',function(){r.querySelectorAll('.fh-b27-ky-tabs button').forEach(function(z){z.setAttribute('aria-selected','false')});b.setAttribute('aria-selected','true');$('ky-pane').innerHTML=tx[b.getAttribute('data-t')];});});
});
$('ky-go2').addEventListener('click',function(){var a=get('ky-a'),b=get('ky-b'),sa=ST[a.h.star-1],sb=ST[b.h.star-1],mk=AI[sa][b.h.star-1];
 var M={'◎':'相手が自分を生む関係。お相手から力や助けをもらいやすい、最良の相性です。','○':'自分が相手を生む関係。あなたがお相手を支え、育てる役になりやすい吉の相性です。','◇':'同じ五行の比和。似た者どうしで分かり合いやすく、良い面も悪い面も重なりやすい関係です。','△':'自分が相手を剋す関係。あなたが主導しやすい一方、押しつけにならない配慮が要ります。','×':'相手に剋される関係。お相手のペースに押されやすいので、自分の考えを言葉にすると対等になれます。'};
 var r=$('ky-res2');r.innerHTML='<small>あなた：'+esc(sa)+'　お相手：'+esc(sb)+'</small><p class="nm">'+mk+'</p><p>'+M[mk]+'</p><p><a href="#b27-ky-aisho">九星の相性表へ →</a></p>';r.hidden=false;});
})();"""


OPPD = {"北": "南", "南": "北", "東": "西", "西": "東", "北東": "南西", "南西": "北東", "北西": "南東", "南東": "北西"}


def month_lucky(aisho, months):
    """2027年の月ごとの吉方位（本命星別）。月盤の中宮から星の位置を出し、本命星から見て相生・比和（◎○◇）の星がいる方位から、
    その月の五黄殺・暗剣殺・月破と、本命殺（自分の星の方位）・本命的殺（その反対）を除く。年盤の凶方位（北・南・北東）も除く（knowledge 3-7）"""
    at = lambda c, p: ((c - 1 + p) % 9) + 1  # noqa: E731
    pal = lambda c, st: (st - c) % 9  # noqa: E731
    out = {}
    for st in range(1, 10):
        rows = []
        for r in months:
            if "前年" in r[0]:
                continue
            if r[1] == "小寒":  # 立春より前はまだ2026年（一白水星の年）の年盤なので、この表では扱わない
                rows.append(None)
                continue
            c = STARS.index(r[4]) + 1
            bad = {r[5], r[6], r[7], "北", "南", "北東"}
            ps = pal(c, st)
            if ps:
                bad |= {KT.PALACE[ps][0], OPPD[KT.PALACE[ps][0]]}
            good = [KT.PALACE[p][0] for p in range(1, 9) if KT.PALACE[p][0] not in bad and aisho[STARS[st - 1]][at(c, p) - 1] in "◎○◇"]
            rows.append(good)
        out[st] = rows
    return out


def build(sample, updated):
    info, base, aisho, months = load()
    MLD = month_lucky(aisho, months)
    MLABEL = [f"{int(r[0][5:7])}/{int(r[0][8:10])}〜" for r in months if "前年" not in r[0]]
    H = []
    a = H.append
    a(CSS)
    a('<div class="fh-b27" data-fh-page="kyusei">\n<div class="fh-b27-note">')
    # 2027年盤の絵（上が南）：南東 南 南西 / 東 中 西 / 北東 北 北西
    order = ["南東", "南", "南西", "東", "中央", "西", "北東", "北", "北西"]
    inv = {v: k for k, v in POS2027.items()}
    ban = "".join(f'<span style="background:{COLOR[inv[o] - 1]};{"color:#F1ECE2;" if inv[o] == 2 else ""}">{inv[o]}</span>' for o in order)
    a(f'''<header class="fh-b27-hero">
  <div class="fh-b27-ky-ban" aria-hidden="true">{ban}</div>
  <div class="fh-b27-hero-body">
    <span class="fh-b27-tape">九星気学</span>
    <h1 class="fh-b27-title">九星気学<br>本命星でわかる2027年の吉方位と運気</h1>
    <p class="fh-b27-lead">九星気学は、生まれ年の星（本命星）と、年や月ごとに入れ替わる星の配置から、動くタイミングと方角を読む占いです。生年月日を選ぶと本命星を計算し、2027年の吉方位と月ごとの流れ、年盤の凶方位まで一度にわかります。立春で年が切り替わる決まりも日付ごとに反映しています。</p>
  </div>
</header>''')
    items = [("b27-ky-calc", "本命星を調べる"), ("b27-ky-aisho2", "二人の相性"), ("b27-ky-list", "九星の性格一覧"), ("b27-ky-read", "本命星別 恋愛・仕事・お金"), ("b27-ky-2027", "本命星別 2027年の運勢"), ("b27-ky-mlucky", "2027年の月ごとの吉方位"), ("b27-ky-ban", "2027年の年盤と凶方位"), ("b27-ky-month", "2027年の月盤"), ("b27-ky-aisho", "九星の相性表"), ("b27-ky-how", "本命星の出し方"), ("b27-ky-faq", "よくある質問")]
    a('<nav class="fh-b27-toc" aria-label="目次"><strong>このページの内容</strong><ol>' + "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in items) + "</ol></nav>")
    n = [1]

    def h2(t):
        s = f'<h2><span class="fh-b27-n">{n[0]}</span><span>{t}</span></h2>'
        n[0] += 1
        return s
    sel = lambda p, who: (f'<div class="fh-b27-ky-form"><b>{who}</b><select id="{p}y" aria-label="{who}の生まれた年"></select>'
                          f'<select id="{p}m" aria-label="{who}の生まれた月"></select><select id="{p}d" aria-label="{who}の生まれた日"></select></div>')
    a('''<div class="fh-b27-ky-why">
  <p class="fh-b27-ky-why-h">九星気学は「いつ・どの方角へ動くか」の占い</p>
  <p>誕生日占いが「生まれた日の性格」を読むのに対して、九星気学は<b>生まれ年の星（本命星）と、年・月ごとに入れ替わる星の配置</b>から、<b>動くタイミングと方角</b>を読む占いです。同じ人でも、年や月によって良い方角が変わるのが特徴です。</p>
  <ul>
    <li><b>引っ越し・旅行の方角</b>2027年の年盤と月盤から、あなたの星にとっての吉方位を月ごとに出します。</li>
    <li><b>始めごとの時期</b>あなたの星が盤のどこに入るかで、その月が「スタート」「充電」「注目」のどれに向くかがわかります。</li>
    <li><b>家族や職場の星との関係</b>五行の関係で、助けてくれる星・支える星がわかります。</li>
  </ul>
  <p class="fh-b27-small">性格や恋愛の相性をくわしく見たいときは<a href="/366uranai/">誕生日占い</a>・<a href="/compatibility/">誕生日相性占い</a>、生まれ年まで入れて8つの占いをまとめて見たいときは<a href="/seinengappi/">まるごと診断</a>がおすすめです。</p>
</div>''')
    a(f'''<section class="fh-b27-sec" id="b27-ky-calc">
  {h2("本命星を調べる")}
  <div class="fh-b27-ky-box">
    {sel("ky-a", "あなた")}
    <div><button type="button" class="fh-b27-ky-btn" id="ky-go">本命星を調べる</button></div>
    <div class="fh-b27-ky-res" id="ky-res" aria-live="polite" hidden></div>
    <p class="fh-b27-small">1930〜2030年の生まれに対応しています。立春の当日に生まれた人は、生まれた時刻によって前の年の星になることがあります。生年月日は送信も保存もしません。</p>
  </div>
</section>
<section class="fh-b27-sec" id="b27-ky-aisho2">
  {h2("二人の相性")}
  <div class="fh-b27-ky-box">
    <p class="fh-b27-small">上の「あなた」と、お相手の生年月日から、本命星どうしの五行の相性を見ます。</p>
    {sel("ky-b", "お相手")}
    <div><button type="button" class="fh-b27-ky-btn" id="ky-go2">相性を見る</button></div>
    <div class="fh-b27-ky-res" id="ky-res2" aria-live="polite" hidden></div>
  </div>
</section>''')
    a("<!--Ads1-->")
    cards = "".join(f'<div style="--c:{COLOR[i]}"><b>{s}</b><small>{esc(base[s]["yomi"])}｜五行：{esc(base[s]["gogyo"])}｜定位：{esc(base[s]["pos"])}</small><br>'
                    f'<b style="font:700 14px inherit;display:inline">性質</b> {esc(info[s]["kw"])}<br>長所：{esc(info[s]["good"])}<br>気をつけたい点：{esc(info[s]["bad"])}<br><small>色：{esc(info[s]["color"])}／象徴：{esc(info[s]["sym"])}</small></div>'
                    for i, s in enumerate(STARS))
    a(f'''<section class="fh-b27-sec" id="b27-ky-list">
  {h2("九星の性格一覧")}
  <p>九星は、一白水星から九紫火星までの9つの星です。それぞれに五行（木・火・土・金・水）と、方位盤の定位置があります。生まれた年の星（本命星）で、その人の基本の性質を読みます。</p>
  <div class="fh-b27-ky-cards">{cards}</div>
</section>''')
    rd = "".join(f'<details id="ky-r{i + 1}" style="--c:{COLOR[i]}"{" open" if i == 0 else ""}><summary>{st}<small>{esc(KT.TEXTS[st]["catch"])}</small></summary>'
                 f'<p><b>恋愛：</b>{esc(KT.TEXTS[st]["love"])}</p><p><b>仕事：</b>{esc(KT.TEXTS[st]["work"])}</p>'
                 f'<p><b>お金：</b>{esc(KT.TEXTS[st]["money"])}</p><p><b>人付き合い：</b>{esc(KT.TEXTS[st]["people"])}</p></details>' for i, st in enumerate(STARS))
    a(f'''<section class="fh-b27-sec" id="b27-ky-read">
  {h2("本命星別 恋愛・仕事・お金")}
  <p>同じ星の人に共通しやすい、恋愛・仕事・お金・人付き合いの傾向です。上で本命星を調べると、あなたの星の内容がタブで読めます。</p>
  <div class="fh-b27-ky-y">{rd}</div>
</section>''')
    yy = "".join(f'<details id="ky-y{i}" style="--c:{COLOR[i - 1]}"{" open" if i == 1 else ""}><summary>{STARS[i - 1]}<small>{esc(YEAR2027[i][0])}｜{esc(YEAR2027[i][1])}</small></summary><p>{esc(YEAR2027[i][2])}</p></details>' for i in range(1, 10))
    a(f'''<section class="fh-b27-sec" id="b27-ky-2027">
  {h2("本命星別 2027年の運勢")}
  <p>2027年は九紫火星が中央に入る年です。明るさ・知性・名誉を表す星の年なので、物事がはっきりし、学びや表現に追い風が吹く一方、勢い任せの判断や見栄の出費には注意したい年と読みます。本命星が2027年の年盤でどこに入るかで、その人の一年の流れを見ます。</p>
  <div class="fh-b27-ky-y">{yy}</div>
  <p class="fh-b27-small">九星の年は2027年2月4日の立春から2028年2月4日の立春までです。月ごとの流れは、366日の誕生日ページで生まれ年を選ぶと見られます。</p>
</section>''')
    head = "".join(f'<th scope="col">{x}</th>' for x in MLABEL)
    rowsx = "".join(f'<tr><th scope="row" style="--c:{COLOR[i]}"><i></i>{st}</th>' + "".join(
        f'<td>{"—" if v is None else ("・".join(v) if v else "なし")}</td>' for v in MLD[i + 1]) + "</tr>" for i, st in enumerate(STARS))
    a(f'''<section class="fh-b27-sec" id="b27-ky-mlucky">
  {h2("本命星別 2027年の月ごとの吉方位")}
  <p>旅行や引っ越し、大事な用事で出かける方角を選ぶときの目安です。その月の月盤で、あなたの星と相性のよい星（相生・比和）がいる方角から、五黄殺・暗剣殺・月破と、本命殺・本命的殺、2027年の年の凶方位（北・南・北東）を除いて出しています。</p>
  <div class="fh-b27-ky-wrap"><table class="fh-b27-ky-t fh-b27-ky-ml"><caption>本命星別・2027年の月ごとの吉方位（月は節入り日から）</caption><thead><tr><th scope="col">本命星</th>{head}</tr></thead><tbody>{rowsx}</tbody></table></div>
  <p class="fh-b27-small">「—」の1月5日〜は、立春前でまだ2026年（一白水星の年）の盤のため、この表では扱っていません。「なし」の月は、近場の用事で済ませるか、別の月を選ぶのがおすすめです。引っ越しなど長く住む場所は、年の吉方位（あなたの星を調べると表示）を優先してください。</p>
</section>''')
    g9 = "".join(f'<div class="{"bad" if o in ("北", "南", "北東") else ""}"><small>{o}</small><b>{STARS[inv[o] - 1]}</b>{"五黄殺" if o == "北" else "暗剣殺" if o == "南" else "歳破" if o == "北東" else ""}</div>' for o in order)
    a(f'''<section class="fh-b27-sec" id="b27-ky-ban">
  {h2("2027年の年盤と凶方位")}
  <p>九星気学の盤は、上を南にして描くのが決まりです。2027年は九紫火星が中央に入り、ほかの星が下のように並びます。</p>
  <div class="fh-b27-ky-grid9">{g9}</div>
  <ul>
    <li><b>五黄殺：北</b>（五黄土星がいる方位）</li>
    <li><b>暗剣殺：南</b>（五黄殺の反対の方位）</li>
    <li><b>歳破：北東</b>（2027年の干支・未の反対の方位）</li>
  </ul>
  <p class="fh-b27-small">期間は2027年2月4日10時46分（立春）から2028年2月4日の立春まで。引っ越しや旅行の方角の目安にしてください。8方位の読み方は<a href="/kaiun/compass/">開運ライフの方位盤</a>でも紹介しています。</p>
</section>''')
    mr = "".join(f'<tr><th scope="row">{esc(r[0].replace("（前年から続く）", "〜"))}</th><td>{esc(r[1])}</td><td>{esc(r[3])}</td><td>{esc(r[4])}</td><td>{esc(r[5])}</td><td>{esc(r[6])}</td><td>{esc(r[7])}</td></tr>' for r in months)
    a(f'''<section class="fh-b27-sec" id="b27-ky-month">
  {h2("2027年の月盤")}
  <p>九星気学の月は、毎月の節入り（二十四節気の「節」）で切り替わります。月盤の中央に入る星と、その月の凶方位です。</p>
  <div class="fh-b27-ky-wrap"><table class="fh-b27-ky-t" style="min-width:600px"><caption>2027年の月盤（日時は日本時間・節入り）</caption><thead><tr><th scope="col">始まり</th><th scope="col">節</th><th scope="col">月柱</th><th scope="col">中央の星</th><th scope="col">五黄殺</th><th scope="col">暗剣殺</th><th scope="col">月破</th></tr></thead><tbody>{mr}</tbody></table></div>
  <p class="fh-b27-small">1月1日から立春の前日までは、九星の年はまだ2026年（一白水星の年）です。</p>
</section>''')
    head = "".join(f"<th scope='col'>{s[:2]}</th>" for s in STARS)
    rows = "".join(f'<tr><th scope="row">{s}</th>' + "".join(f"<td>{m}</td>" for m in aisho[s]) + "</tr>" for s in STARS)
    a(f'''<section class="fh-b27-sec" id="b27-ky-aisho">
  {h2("九星の相性表")}
  <p>九星の相性は、五行の関係で見ます。木は火を、火は土を、土は金を、金は水を、水は木を生み（相生）、木は土を、土は水を、水は火を、火は金を、金は木を抑えます（相剋）。同じ五行どうしは比和です。</p>
  <p>◎＝相手が自分を生む（助けてもらえる）／○＝自分が相手を生む（支える）／◇＝比和（似た者どうし）／△＝自分が相手を剋す（押さえる側）／×＝相手に剋される（押される側）</p>
  <div class="fh-b27-ky-wrap"><table class="fh-b27-ky-t fh-b27-ky-mx"><caption>本人（左）から見た相手（上）との相性</caption><thead><tr><th scope="col">本人＼相手</th>{head}</tr></thead><tbody>{rows}</tbody></table></div>
</section>''')
    a(f'''<section class="fh-b27-sec" id="b27-ky-how">
  {h2("本命星の出し方")}
  <p>本命星は、生まれた年の数字から次の式で出せます。</p>
  <p style="text-align:center;font-family:'Shippori Mincho',serif;font-size:18px">本命星の番号 ＝（11 − 生まれ年を9で割った余り）を9で割った余り<br><small>（答えが0なら9）</small></p>
  <p>例：1990年生まれ → 1990÷9 の余りは1 → 11−1＝10 → 10÷9 の余りは1 → <b>一白水星</b>。2027年は余りが2なので、11−2＝9 → <b>九紫火星</b>です。</p>
  <p>ただし九星気学の年は<b>立春</b>（毎年2月4日ごろ）で切り替わります。1月1日から立春の前日までに生まれた人は、前の年の数字で計算してください。このページの計算は、立春の日時（国立天文台の暦と同じ決まりで計算した値）で切り替えています。</p>
</section>''')
    qa = "".join(f'<details{" open" if i == 0 else ""}><summary>Q. {q}</summary><p>A. {x}</p></details>' for i, (q, x) in enumerate(FAQ))
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in FAQ]}
    a(f'''<section class="fh-b27-sec" id="b27-ky-faq">
  {h2("よくある質問")}
  <div class="fh-b27-ky-qa">{qa}</div>
</section>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<section class="fh-b27-sec">
  <div class="fh-b27-links">
    <a href="/seinengappi/"><b>生年月日まるごと診断 →</b><small>九星・宿曜・四柱推命・マヤ暦などを1枚に</small></a>
    <a href="/shukuyo/"><b>宿曜占星術 →</b><small>月の暦で本命宿と相性を見る</small></a>
    <a href="/maya/"><b>マヤ暦占い →</b><small>KINと太陽の紋章・銀河の音</small></a>
    <a href="/kaiun/compass/"><b>方位盤 →</b><small>開運ライフ｜8方位の読み方</small></a>
  </div>
</section>''')
    OPP = {1: 8, 8: 1, 2: 7, 7: 2, 3: 6, 6: 3, 4: 5, 5: 4}
    at = lambda c, p: ((c - 1 + p) % 9) + 1  # noqa: E731
    pal = lambda c, st: (st - c) % 9  # noqa: E731
    LD = {}
    for st in range(1, 10):  # 2027年（九紫中宮）の吉方位：相生・比和の星の方位から、五黄殺・暗剣殺・歳破（北東）・本命殺・本命的殺を除く
        bad = {pal(9, 5), OPP[pal(9, 5)], 3}
        ps = pal(9, st)
        if ps:
            bad |= {ps, OPP[ps]}
        LD[st] = [KT.PALACE[p][0] for p in range(1, 9) if p not in bad and aisho[STARS[st - 1]][at(9, p) - 1] in "◎○◇"]
    MS = []
    for r in months:
        if "前年" in r[0]:
            continue
        mo, dd = int(r[0][5:7]), int(r[0][8:10])
        MS.append([f"{mo}/{dd}〜", STARS.index(r[4]) + 1])
    assert len(MS) == 12
    lucky = "".join(f'<div data-s="{i + 1}">{aff_extra.goods_box("2027年のお守りアイテム", [(KT.TEXTS[st]["lucky"][0], KT.TEXTS[st]["lucky"][0], KT.TEXTS[st]["lucky"][1], "goods")])}</div>' for i, st in enumerate(STARS))
    a(f'<div id="ky-lucky-src" hidden>{lucky}</div>')
    js = (JS.replace("__KT__", json.dumps(KT.TEXTS, ensure_ascii=False)).replace("__LD__", json.dumps(LD, ensure_ascii=False))
          .replace("__MS__", json.dumps(MS, ensure_ascii=False)).replace("__ML__", json.dumps(MLD, ensure_ascii=False)).replace("__PAL__", json.dumps(KT.PALACE, ensure_ascii=False))
          .replace("__STARS__", json.dumps(STARS, ensure_ascii=False)).replace("__INFO__", json.dumps(info, ensure_ascii=False, separators=(",", ":")))
          .replace("__AISHO__", json.dumps(aisho, ensure_ascii=False)).replace("__COL__", json.dumps(COLOR)).replace("__POS__", json.dumps(POS2027, ensure_ascii=False))
          .replace("__Y27__", json.dumps(YEAR2027, ensure_ascii=False)))
    up = dt.date.fromisoformat(updated)
    a(f'<p class="fh-b27-foot">本命星・年盤・月盤は、立春と節入りの日時をもとにこのサイトで計算しています。九星の性質と2027年の運勢の文章はこのサイトで書いたものです。占いは楽しみと気づきのためにお読みください。<br>'
      f'最終更新日：{up.year}年{up.month}月{up.day}日／<a href="/about/">この記事の作成方針について</a></p>')
    a("</div>\n</div>")
    a(f"<script>document.addEventListener('DOMContentLoaded',function(){{{js}}});</script>")
    title = "九星気学｜本命星で見る2027年の吉方位と運勢・月ごとの吉方位表・凶方位【無料計算】"
    desc = ("生年月日から九星気学の本命星を無料で計算し、2027年の吉方位と月ごとの吉方位表、年盤の凶方位（五黄殺・暗剣殺・歳破）、本命星別の運勢と恋愛・仕事・お金、九星どうしの相性を紹介。引っ越しや旅行の方角選びに。")
    out = shell(title, desc, URL, "\n".join(H), sample, SCRIPTS)
    assert "！" not in out
    return out


def main():
    updated = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    for sample, path in ((False, os.path.join(OUT, "kyusei.html")), (True, os.path.join(OUT, "sample", "kyusei.html"))):
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(build(sample, updated))
        print("→", os.path.relpath(path, WORK))


if __name__ == "__main__":
    main()
