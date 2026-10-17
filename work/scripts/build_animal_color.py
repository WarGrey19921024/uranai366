"""動物×色占いのページ（/animal-color/、固定ページ ID 4254）を作り直す（2026-10-18）。
本人の決定：動物を、ほかの有名な動物の占いと重ならない、このサイト独自の12に入れ替える（計算式はそのまま）。
文章：work/scripts/animal_color_texts.py。計算：work/scripts/calc_animal_color.py。決め方：work/knowledge/11_動物×色占い.md
注意：WordPress（Diver）は [sp] [pc] などをショートコードとして消すので、JSで X[sp] のような書き方をしない。
注意：WordPress は絵文字を &#x…; に変えて保存するので、JS の中では絵文字を文字で書かず、コードポイントの数で渡す。
使い方: python work/scripts/build_animal_color.py [最終更新日]
出力: work/out/animal-color.html（投入用）、work/out/sample/animal-color.html（確認用）
"""
import datetime as dt, html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_hub import OUT, WORK, shell  # noqa: E402
from calc_animal_color import animal_color  # noqa: E402
import animal_color_texts as A  # noqa: E402
import aff_extra as AX  # noqa: E402
GF = json.load(open(os.path.join(os.path.dirname(HERE), "data", "goods_family.json"), encoding="utf-8"))
FAM = {'red': '赤', 'gold': '金', 'green': '緑', 'blue': '青', 'purple': '紫'}

URL = "/animal-color/"
CYCLE = [c["key"] for c in A.COLORS]


def esc(s):
    return html.escape(str(s), quote=True)


def score(ai, ci, bj, cj):
    ga, gb = A.ANIMALS[ai]["group"], A.ANIMALS[bj]["group"]
    s = 2 if ga == gb else (1 if A.PARTNER[ga] == gb else 0)
    d = (ci - cj) % 5
    s += 1 if d in (0, 1, 4) else 0
    return s


def mark(s):
    return "◎" if s >= 3 else ("○" if s == 2 else "△")


CSS = """<style id="fh-b27-ac-css">
.fh-b27[data-fh-page="acolor"]{--ink:#F6F2FA;--sub:#DDD5EA;--mute:#B6ABC8;--paper:#1E1A2E;--deep:#171425;--line:#463D63;--gold:#F2C46B;--cream:#FFFCF6;--cream-ink:#2D2640}
.fh-b27[data-fh-page="acolor"] a{color:#FFD58A}
.fh-b27[data-fh-page="acolor"] .fh-b27-sec>p,.fh-b27[data-fh-page="acolor"] .fh-b27-lead{text-shadow:0 1px 2px rgba(0,0,0,.6)}
.fh-b27[data-fh-page="acolor"] .fh-b27-note{border-left:0;border-radius:24px;background-color:var(--paper);
 background-image:radial-gradient(circle at 8% 0%,rgba(224,87,91,.18),transparent 35%),radial-gradient(circle at 50% 0%,rgba(226,179,60,.14),transparent 35%),radial-gradient(circle at 92% 10%,rgba(79,174,122,.16),transparent 35%),radial-gradient(circle at 20% 100%,rgba(76,143,214,.16),transparent 40%),radial-gradient(circle at 90% 90%,rgba(154,107,203,.2),transparent 40%);box-shadow:0 18px 40px rgba(0,0,0,.3);background-size:auto;background-repeat:no-repeat}
.fh-b27[data-fh-page="acolor"] .fh-b27-hero{align-items:center}
.fh-b27-ac-emb{display:grid;grid-template-columns:repeat(4,40px);gap:6px;flex:0 0 auto}
.fh-b27-ac-emb span{width:40px;height:40px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:22px;background:var(--c);box-shadow:0 3px 8px rgba(0,0,0,.3);animation:fh-b27-ac-bob 3.2s ease-in-out infinite;animation-delay:calc(var(--i)*.25s)}
@keyframes fh-b27-ac-bob{50%{transform:translateY(-4px)}}
.fh-b27[data-fh-page="acolor"] .fh-b27-tape{transform:none;border-radius:999px;background:linear-gradient(90deg,#E0575B,#E2B33C,#4FAE7A,#4C8FD6,#9A6BCB);color:#fff;text-shadow:0 1px 2px rgba(0,0,0,.4)}
.fh-b27[data-fh-page="acolor"] .fh-b27-title{font-family:'Shippori Mincho',serif;font-weight:800;font-size:30px}
.fh-b27[data-fh-page="acolor"] h2{font-family:'Shippori Mincho',serif;font-weight:800;font-size:24px}
.fh-b27[data-fh-page="acolor"] h2 .fh-b27-n{border:0;border-radius:50%;background:linear-gradient(135deg,#F2C46B,#9A6BCB);color:#1E1A2E}
.fh-b27[data-fh-page="acolor"] .fh-b27-toc{border-style:solid;border-radius:18px;border-color:rgba(242,196,107,.3)}
.fh-b27[data-fh-page="acolor"] .fh-b27-toc ol{columns:2;column-gap:28px}
.fh-b27-ac-box{border:1.5px solid rgba(242,196,107,.35);border-radius:20px;background:var(--deep);padding:16px;display:flex;flex-direction:column;gap:12px;align-items:center}
.fh-b27-ac-row{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;align-items:flex-end}
.fh-b27-ac-row label{display:flex;flex-direction:column;gap:4px;font-size:13px;color:var(--sub)}
.fh-b27-ac-row input{min-height:46px;border-radius:12px;border:1.5px solid rgba(242,196,107,.45);background:#fff;color:#2D2640;font:inherit;padding:0 10px}
.fh-b27-ac-go{min-height:50px;border:0;border-radius:999px;background:linear-gradient(90deg,#F2C46B,#9A6BCB);color:#1E1A2E;font:inherit;font-weight:800;padding:0 26px;cursor:pointer}
.fh-b27-ac-res{width:100%;background:var(--cream);color:var(--cream-ink);border-radius:18px;padding:16px 18px;line-height:1.85}
.fh-b27 .fh-b27-ac-res p,.fh-b27 .fh-b27-ac-res b,.fh-b27 .fh-b27-ac-res li{color:var(--cream-ink)}
.fh-b27 .fh-b27-ac-res a{color:#6A3FA0;font-weight:700}
.fh-b27-ac-type{display:flex;flex-direction:column;align-items:center;gap:6px;margin-bottom:8px}
.fh-b27-ac-badge{width:96px;height:96px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:52px;background:var(--c);box-shadow:0 0 0 6px rgba(255,255,255,.9),0 0 0 9px var(--c);animation:fh-b27-ac-pop .8s ease both}
@keyframes fh-b27-ac-pop{0%{transform:scale(.2) rotate(-30deg);opacity:0}70%{transform:scale(1.08)}100%{transform:none;opacity:1}}
.fh-b27-ac-tname{font:800 24px 'Shippori Mincho',serif;color:#3B2C5E}
.fh-b27-ac-combo{text-align:center;font-weight:700;color:#5A3E8A}
.fh-b27-ac-res .sec{border-top:1px dashed #E3D9F0;margin-top:10px;padding-top:8px}
.fh-b27-ac-res .cmp{display:flex;flex-wrap:wrap;gap:6px}
.fh-b27-ac-res .cmp span{border-radius:999px;background:#F2ECFA;padding:2px 10px;font-size:13px}
.fh-b27-ac-big{display:flex;gap:16px;justify-content:center;align-items:center}
.fh-b27-ac-big .fh-b27-ac-badge{width:72px;height:72px;font-size:38px}
.fh-b27-ac-mark{font:800 40px 'Shippori Mincho',serif;color:#C2273A}
.fh-b27-ac-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.fh-b27-ac-grid details{border:1px solid rgba(242,196,107,.22);border-radius:14px;background:var(--deep);padding:8px 14px;font-size:14.5px;line-height:1.85}
.fh-b27-ac-grid summary{cursor:pointer;list-style:none;display:flex;gap:10px;align-items:center;font-weight:800;color:#FFE9BF}
.fh-b27-ac-grid summary::-webkit-details-marker{display:none}
.fh-b27-ac-grid summary .e{font-size:28px}
.fh-b27-ac-grid summary small{display:block;font-weight:400;color:var(--mute);font-size:12.5px}
.fh-b27-ac-grid p{margin:6px 0}
.fh-b27-ac-grid ul{margin:4px 0;padding-left:1.1em}
.fh-b27-ac-dot{display:inline-block;width:.9em;height:.9em;border-radius:50%;background:var(--c);vertical-align:-1px;margin-right:4px}
.fh-b27-ac-colors{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px}
.fh-b27-ac-colors div{border-radius:14px;background:var(--deep);border-top:6px solid var(--c);padding:10px 12px;font-size:13.5px;line-height:1.8;border-left:1px solid rgba(255,255,255,.08);border-right:1px solid rgba(255,255,255,.08);border-bottom:1px solid rgba(255,255,255,.08)}
.fh-b27-ac-colors b{display:block;font:800 17px 'Shippori Mincho',serif;color:#FFE9BF}
.fh-b27-ac-groups{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.fh-b27-ac-groups div{border:1px solid rgba(242,196,107,.22);border-radius:14px;background:var(--deep);padding:10px 12px;font-size:14px;line-height:1.8}
.fh-b27-ac-groups b{color:#FFE9BF}
.fh-b27-ac-steps code{font-family:inherit;background:rgba(255,255,255,.08);border-radius:6px;padding:1px 6px;color:#FFE3B8}
.fh-b27-ac-qa details{border-bottom:1px dashed var(--line);padding:8px 2px}
.fh-b27-ac-qa summary{cursor:pointer;font-weight:700}
.fh-b27-ac-qa p{margin-top:6px;font-size:14.5px}
@media (max-width:640px){.fh-b27-ac-grid,.fh-b27-ac-groups{grid-template-columns:1fr}.fh-b27-ac-colors{grid-template-columns:repeat(2,minmax(0,1fr))}.fh-b27[data-fh-page="acolor"] .fh-b27-toc ol{columns:1}
 .fh-b27[data-fh-page="acolor"] .fh-b27-title{font-size:25px}.fh-b27-ac-emb{grid-template-columns:repeat(4,32px)}.fh-b27-ac-emb span{width:32px;height:32px;font-size:18px}}
@media (prefers-reduced-motion:reduce){.fh-b27-ac-emb span,.fh-b27-ac-badge{animation:none}}
</style>"""

JS = r"""(function(){var AN=__A__,CO=__C__,CB=__CB__,GR=__G__,PT=__P__,CT=__CT__;function $(i){return document.getElementById(i)}
if(!$('ac-go'))return;
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function em(a){return String.fromCodePoint.apply(null,a.cp)}
function parse(v){var p=(v||'').split('-');if(p.length!==3)return null;var y=+p[0],m=+p[1],d=+p[2];var t=new Date(y,m-1,d);if(!y||t.getMonth()!==m-1)return null;return {y:y,m:m,d:d}}
function calc(b){var base=(b.y+b.m*12+b.d)%60;return {a:base%12,c:Math.floor(base/12)%5}}
function sc(x,y){var ga=AN[x.a].group,gb=AN[y.a].group,s=ga===gb?2:(PT[ga]===gb?1:0),d=((x.c-y.c)%5+5)%5;return s+((d===0||d===1||d===4)?1:0)}
function mk(s){return s>=3?'◎':(s===2?'○':'△')}
function badge(t){return '<div class="fh-b27-ac-badge" style="--c:'+CO[t.c].hex+'">'+em(AN[t.a])+'</div>'}
function tname(t){return CO[t.c].name+'の'+AN[t.a].name}
$('ac-go').addEventListener('click',function(){var b=parse($('ac-bd').value),r=$('ac-res');r.hidden=false;if(!b){r.innerHTML='<p>生年月日を入れてください。</p>';return}
 var t=calc(b),a=AN[t.a],c=CO[t.c],g=GR[a.group],pg=GR[PT[a.group]];
 var same=AN.filter(function(x,i){return x.group===a.group&&i!==t.a}).map(function(x){return x.name}),part=AN.filter(function(x){return x.group===PT[a.group]}).map(function(x){return x.name});
 var near=[CO[(t.c+4)%5].name,c.name,CO[(t.c+1)%5].name];
 r.innerHTML='<div class="fh-b27-ac-type">'+badge(t)+'<div class="fh-b27-ac-tname">'+esc(tname(t))+'</div><div class="fh-b27-ac-combo">'+esc(CB[a.key][t.c])+'</div></div>'
 +'<p><b>'+esc(a.name)+'：'+esc(a.catch)+'</b>（'+esc(a.kw)+'）</p><p>'+esc(a.text)+'</p>'
 +'<p><span class="fh-b27-ac-dot" style="--c:'+c.hex+'"></span><b>'+esc(c.name)+'（'+esc(c.kw)+'）：</b>'+esc(c.text)+'</p>'
 +'<div class="sec"><p><b>恋愛：</b>'+esc(a.love)+'</p><p><b>仕事：</b>'+esc(a.work)+'</p><p><b>友だち：</b>'+esc(a.friend)+'</p><p><b>いいところ：</b>'+esc(a.strength)+'<br><b>気をつけたいところ：</b>'+esc(a.care)+'<br><b>開運のヒント：</b>'+esc(a.tip)+'</p></div>'
 +'<div class="sec"><p><b>相性のいい動物：</b>同じ'+esc(g.name)+'（'+esc(same.join('・'))+'）と、補い合う'+esc(pg.name)+'（'+esc(part.join('・'))+'）。<br><b>相性のいい色：</b>'+esc(near.join('・'))+'</p></div>'
 +'<p><a href="#ac-'+a.key+'">'+esc(a.name)+'の説明へ →</a>　<a href="/366uranai/'+(b.m<10?'0':'')+b.m+'-'+(b.d<10?'0':'')+b.d+'/">'+b.m+'月'+b.d+'日生まれの誕生日占いへ →</a></p>';CO.forEach(function(x){var e=$('ac-ad-'+x.key);if(e)e.hidden=(x.key!==c.key)});$('ac-ads').hidden=false;});
$('ac-cgo').addEventListener('click',function(){var x=parse($('ac-ca').value),y=parse($('ac-cb').value),r=$('ac-cres');r.hidden=false;if(!x||!y){r.innerHTML='<p>二人の生年月日を入れてください。</p>';return}
 var p=calc(x),q=calc(y),s=sc(p,q),ga=AN[p.a].group,gb=AN[q.a].group,rel=ga===gb?'same':(PT[ga]===gb?'partner':'diff'),d=((p.c-q.c)%5+5)%5,cr=d===0?'csame':((d===1||d===4)?'cnear':'cfar');
 r.innerHTML='<div class="fh-b27-ac-big">'+badge(p)+'<span class="fh-b27-ac-mark">'+mk(s)+'</span>'+badge(q)+'</div><p style="text-align:center"><b>'+esc(tname(p))+'</b> × <b>'+esc(tname(q))+'</b></p><p>'+esc(CT[rel])+'</p><p>'+esc(CT[cr])+'</p>';});
})();"""

COMPAT_TEXT = {
    "same": "同じなかまの動物どうし。大切にしているものが似ているので、説明しなくても通じ合える安心感があります。似ているぶん、苦手なことも重なりやすいので、ときどき役割を入れ替えてみて。",
    "partner": "補い合うなかまどうし。おたがいにない力を持っているので、一緒にいると世界が広がります。違いを面白がれると、心強いコンビになります。",
    "diff": "ペースや大切にするものが違いやすい組み合わせ。だからこそ、相手のやり方から学べることがたくさんあります。予定や気持ちは早めに言葉にして伝え合いましょう。",
    "csame": "色も同じで、気持ちの温度が近い二人です。",
    "cnear": "色がとなり合い、気分の波が自然に合いやすい二人です。",
    "cfar": "色が離れていて、気分の出し方が違う二人。相手の表現をそのまま受け止めると、すれ違いが減ります。",
}


def build(sample, updated):
    H = []
    a = H.append
    a(CSS)
    a('<div class="fh-b27" data-fh-page="acolor">\n<div class="fh-b27-note">')
    emb = "".join(f'<span style="--c:{A.COLORS[i % 5]["hex"]};--i:{i}">{x["emoji"]}</span>' for i, x in enumerate(A.ANIMALS[:8]))
    a(f'''<header class="fh-b27-hero">
  <div class="fh-b27-ac-emb" aria-hidden="true">{emb}</div>
  <div class="fh-b27-hero-body">
    <span class="fh-b27-tape">人生予報 動物×色占い</span>
    <h1 class="fh-b27-title">動物×色占い<br>生年月日でわかる60タイプ</h1>
    <p class="fh-b27-lead">生年月日を入れると、12の動物と5つの色を組み合わせた60タイプから、あなたのタイプがわかります。性格・恋愛・仕事・友だちづきあいの傾向と、相性のいい動物や色、二人の相性も見られる、このサイト独自の無料の占いです。</p>
  </div>
</header>''')
    items = [("b27-ac-calc", "タイプを診断する"), ("b27-ac-compat", "二人の相性を見る"), ("b27-ac-how", "タイプの出し方"),
             ("b27-ac-animals", "12の動物の性格"), ("b27-ac-colors", "5つの色の意味"), ("b27-ac-rule", "相性のしくみ"), ("b27-ac-faq", "よくある質問")]
    a('<nav class="fh-b27-toc" aria-label="目次"><strong>このページの内容</strong><ol>' + "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in items) + "</ol></nav>")
    n = [0]

    def h2(t):
        n[0] += 1
        return f'<h2><span class="fh-b27-n">{n[0]}</span><span>{t}</span></h2>'

    ads = AX.result_boxes("ac-ad", {c["key"]: (f'{c["name"]}のタイプのあなたに', [(GF["stone"][FAM[c["key"]]], f'{c["name"]}系の天然石ブレスレット', f'タイプの色「{c["name"]}」の石を、身につけるお守りに。', "stone"), (GF["color"][FAM[c["key"]]], f'{c["name"]}のマグカップ', f'毎日使うものに「{c["name"]}」を取り入れて、色の力を身近に。', "tableware")]) for c in A.COLORS}, lead="診断したタイプの色に合わせて選びました。楽天・Yahoo!ショッピングの商品ページへ移ります。")
    a(f'''<section class="fh-b27-sec" id="b27-ac-calc">
  {h2("タイプを診断する")}
  <div class="fh-b27-ac-box">
    <div class="fh-b27-ac-row"><label>あなたの生年月日<input type="date" id="ac-bd" min="1900-01-01" max="2030-12-31" value="1995-01-01"></label></div>
    <button type="button" class="fh-b27-ac-go" id="ac-go">タイプを診断する</button>
    <div class="fh-b27-ac-res" id="ac-res" aria-live="polite" hidden></div>
    <div class="fh-b27-ac-ads" id="ac-ads" style="width:100%" hidden>{ads}</div>
  </div>
</section>''')
    a(f'''<section class="fh-b27-sec" id="b27-ac-compat">
  {h2("二人の相性を見る")}
  <div class="fh-b27-ac-box">
    <div class="fh-b27-ac-row"><label>あなたの生年月日<input type="date" id="ac-ca" min="1900-01-01" max="2030-12-31" value="1995-01-01"></label><label>お相手の生年月日<input type="date" id="ac-cb" min="1900-01-01" max="2030-12-31" value="1993-06-15"></label></div>
    <button type="button" class="fh-b27-ac-go" id="ac-cgo">二人の相性を見る</button>
    <div class="fh-b27-ac-res" id="ac-cres" aria-live="polite" hidden></div>
  </div>
</section>''')
    ex = animal_color(1990, 5, 15)
    b = ex["base"]
    a(f'''<section class="fh-b27-sec" id="b27-ac-how">
  {h2("タイプの出し方")}
  <p>タイプは、生まれた年・月・日の数字だけで決まります。1990年5月15日生まれを例にすると、次のようになります。</p>
  <ol class="fh-b27-ac-steps">
    <li>年＋月×12＋日を計算する：<code>1990＋5×12＋15＝{1990 + 60 + 15}</code></li>
    <li>60で割った余りを出す：<code>{1990 + 60 + 15}÷60 の余り＝{b}</code></li>
    <li>その数を12で割った余りが動物：<code>{b}÷12 の余り＝{b % 12}</code> → {esc(ex["animal"])}</li>
    <li>その数を12で割った答え（小数は切り捨て）が色：<code>{b}÷12＝{b // 12}</code> → {esc(ex["color"])}</li>
  </ol>
  <p>この例の人は「{esc(ex["color"])}の{esc(ex["animal"])}」です。動物の番号は0から順に{"・".join(x["name"] for x in A.ANIMALS)}、色の番号は0から順に{"・".join(c["name"] for c in A.COLORS)}です。</p>
</section>''')
    cards = ""
    for i, x in enumerate(A.ANIMALS):
        combos = "".join(f'<li><span class="fh-b27-ac-dot" style="--c:{c["hex"]}"></span><b>{esc(c["name"])}の{esc(x["name"])}</b>：{esc(A.COMBO[x["key"]][j])}</li>' for j, c in enumerate(A.COLORS))
        cards += (f'<details id="ac-{x["key"]}"><summary><span class="e" aria-hidden="true">{x["emoji"]}</span><span>{esc(x["name"])}<small>{esc(A.GROUPS[x["group"]]["name"])}｜{esc(x["kw"])}</small></span></summary>'
                  f'<p><b>{esc(x["catch"])}</b></p><p>{esc(x["text"])}</p><p><b>恋愛：</b>{esc(x["love"])}</p><p><b>仕事：</b>{esc(x["work"])}</p>'
                  f'<p><b>いいところ：</b>{esc(x["strength"])}<br><b>気をつけたいところ：</b>{esc(x["care"])}<br><b>開運のヒント：</b>{esc(x["tip"])}</p>'
                  f'<p><b>5つの色ごとのタイプ</b></p><ul>{combos}</ul></details>')
    a(f'''<section class="fh-b27-sec" id="b27-ac-animals">
  {h2("12の動物の性格")}
  <p>動物を押すと、性格・恋愛・仕事の傾向と、5つの色と組み合わせた5タイプのひとことが開きます。12の動物×5つの色で、全部で60タイプです。</p>
  <div class="fh-b27-ac-grid">{cards}</div>
</section>''')
    cl = "".join(f'<div style="--c:{c["hex"]}"><b>{esc(c["name"])}</b>{esc(c["kw"])}<br>{esc(c["text"])}</div>' for c in A.COLORS)
    a(f'''<section class="fh-b27-sec" id="b27-ac-colors">
  {h2("5つの色の意味")}
  <p>色は、動物の性格がどんな形で表に出やすいかを表します。同じ動物でも、色が違うと印象や得意な場面が変わります。</p>
  <div class="fh-b27-ac-colors">{cl}</div>
</section>''')
    gl = "".join(f'<div><b>{esc(v["name"])}</b>（{esc(v["members"])}）<br>{esc(v["text"])}</div>' for v in A.GROUPS.values())
    a(f'''<section class="fh-b27-sec" id="b27-ac-rule">
  {h2("相性のしくみ")}
  <p>12の動物は、3匹ずつ4つのなかまに分かれます。同じなかまどうしは価値観が近く、空と水、森と野のなかまはおたがいを補い合う関係です。色は「レッド→ゴールド→グリーン→ブルー→パープル→レッド」の順にとなり合う色どうしが、気分の波を合わせやすいとしています。この2つを合わせて、◎・○・△の3段階で相性を出しています（このサイトの決め方です）。</p>
  <div class="fh-b27-ac-groups">{gl}</div>
</section>''')
    qa = "".join(f'<details{" open" if i == 0 else ""}><summary>Q. {esc(q)}</summary><p>A. {esc(x)}</p></details>' for i, (q, x) in enumerate(A.FAQ))
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in A.FAQ]}
    a(f'''<section class="fh-b27-sec" id="b27-ac-faq">
  {h2("よくある質問")}
  <div class="fh-b27-ac-qa">{qa}</div>
</section>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<section class="fh-b27-sec" id="b27-ac-more">
  <div class="fh-b27-links">
    <a href="/seinengappi/"><b>生年月日まるごと診断 →</b><small>動物×色を含む8つの占いをまとめて</small></a>
    <a href="/366uranai/"><b>366日の誕生日占い →</b><small>誕生日ごとの性格と2027年の運勢</small></a>
    <a href="/suhijutsu/"><b>数秘術 →</b><small>生年月日でライフパスを計算</small></a>
    <a href="/compatibility/"><b>誕生日相性占い →</b><small>2人の生年月日で相性を見る</small></a>
  </div>
</section>''')
    an = [{k: v for k, v in x.items() if k != "emoji"} | {"cp": [ord(ch) for ch in x["emoji"]]} for x in A.ANIMALS]
    js = (JS.replace("__A__", json.dumps(an, ensure_ascii=False)).replace("__C__", json.dumps(A.COLORS, ensure_ascii=False))
          .replace("__CB__", json.dumps(A.COMBO, ensure_ascii=False)).replace("__G__", json.dumps(A.GROUPS, ensure_ascii=False))
          .replace("__P__", json.dumps(A.PARTNER, ensure_ascii=False)).replace("__CT__", json.dumps(COMPAT_TEXT, ensure_ascii=False)))
    assert not re.findall(r"\[(sp|pc|tab|mobile)\]", js)
    assert not re.search(r"[\U0001F000-\U0001FFFF]", js), "JSに絵文字"
    up = dt.date.fromisoformat(updated)
    a(f'<p class="fh-b27-foot">動物×色占いは、このサイトが独自に作った占いです。動物と色の組み合わせ、計算のしかた、相性の決め方はこのサイトで決めたもので、ほかの動物を使った占いとは関係ありません。'
      f'最終更新日：{up.year}年{up.month}月{up.day}日／<a href="/about/">この記事の作成方針について</a></p>')
    a("</div>\n</div>")
    a(f"<script>document.addEventListener('DOMContentLoaded',function(){{{js}}});</script>")
    title = "動物×色占い【無料】生年月日でわかる60タイプの性格と相性｜12の動物×5つの色"
    desc = ("生年月日を入れると、12の動物と5つの色を組み合わせた60タイプからあなたのタイプがわかる、このサイト独自の無料の占い。"
            "性格・恋愛・仕事の傾向、相性のいい動物と色、二人の相性も見られます。")
    out = shell(title, desc, URL, "\n".join(H), sample)
    assert "！" not in out and "動物占い" not in out
    return out


def main():
    updated = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    for sample, path in ((False, os.path.join(OUT, "animal-color.html")), (True, os.path.join(OUT, "sample", "animal-color.html"))):
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(build(sample, updated))
        print("→", os.path.relpath(path, WORK))


if __name__ == "__main__":
    main()
