"""血液型相性占いのページ（新しい固定ページ /blood/）を作る（2026-10-16。検索「血液型 相性」月1万〜10万）。
作る前の確認：/blood-week/（血液型×誕生曜日の28タイプ）はあるが、血液型どうしの相性だけを扱うページは無い（/blood/ は未使用）。
2026-10-18：/blood-week/（28タイプのうち1タイプしか文章が無かった）を、このページの「生まれた曜日も合わせて見る」にまとめて301。文章：work/scripts/blood_texts.py（このサイトの言葉）。
使い方: python work/scripts/build_blood.py [最終更新日]
出力: work/out/blood.html（投入用）、work/out/sample/blood.html（確認用）
"""
import datetime as dt, html, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_hub import OUT, WORK, shell  # noqa: E402
import blood_texts as B  # noqa: E402

URL = "/blood/"
TY = ["A", "B", "O", "AB"]
COL = {"A": "#E8707E", "B": "#5FA8D3", "O": "#F2B84B", "AB": "#9C7BD0"}


def esc(s):
    return html.escape(str(s), quote=True)


def key(a, b):
    i, j = sorted((TY.index(a), TY.index(b)))
    return f"{TY[i]}-{TY[j]}"


def stars(n):
    return "♥︎" * n + "♡︎" * (5 - n)


CSS = """<style id="fh-b27-bl-css">
.fh-b27[data-fh-page="blood"]{--ink:#FFF3F4;--sub:#F1D9DC;--mute:#C9AEB3;--paper:#2A1B22;--deep:#21151B;--line:#5E3F4A;--gold:#F6C177;--cream:#FFF9F6;--cream-ink:#3A2129}
.fh-b27[data-fh-page="blood"] a{color:#FFC7CE}
.fh-b27[data-fh-page="blood"] .fh-b27-sec>p,.fh-b27[data-fh-page="blood"] .fh-b27-lead,.fh-b27[data-fh-page="blood"] .fh-b27-bl-mx,.fh-b27[data-fh-page="blood"] ol{text-shadow:0 1px 2px rgba(0,0,0,.6)}
.fh-b27[data-fh-page="blood"] .fh-b27-note{border-left:0;border-radius:24px;background-color:var(--paper);
 background-image:radial-gradient(circle at 10% 0%,rgba(232,112,126,.25),transparent 40%),radial-gradient(circle at 100% 60%,rgba(156,123,208,.18),transparent 40%);background-size:auto,auto;box-shadow:0 14px 40px rgba(0,0,0,.45),inset 0 0 0 1px rgba(255,199,206,.2)}
.fh-b27-bl-emb{display:flex;gap:6px;flex:0 0 auto;align-items:flex-end}
.fh-b27-bl-drop{width:44px;height:58px;border-radius:50% 50% 50% 50%/60% 60% 40% 40%;position:relative;display:flex;align-items:center;justify-content:center;font:800 15px 'Zen Kaku Gothic New',sans-serif;color:#fff;
 background:radial-gradient(circle at 35% 35%,rgba(255,255,255,.55),transparent 30%),var(--c);clip-path:polygon(50% 0,100% 62%,92% 85%,70% 100%,30% 100%,8% 85%,0 62%)}
.fh-b27-bl-emb .fh-b27-bl-drop{animation:fh-b27-bl-bob 3s ease-in-out infinite;animation-delay:calc(var(--i)*.3s)}@keyframes fh-b27-bl-bob{50%{transform:translateY(-6px)}}
.fh-b27[data-fh-page="blood"] .fh-b27-hero{align-items:center}
.fh-b27[data-fh-page="blood"] .fh-b27-tape{transform:none;border-radius:999px;background:linear-gradient(90deg,#E8707E,#9C7BD0);color:#fff}
.fh-b27[data-fh-page="blood"] .fh-b27-title{font-family:'Shippori Mincho',serif;font-weight:800;font-size:30px}
.fh-b27[data-fh-page="blood"] h2{font-family:'Shippori Mincho',serif;font-weight:800;font-size:24px}
.fh-b27[data-fh-page="blood"] h2 .fh-b27-n{border:0;border-radius:50%;background:linear-gradient(135deg,#E8707E,#9C7BD0);color:#fff}
.fh-b27[data-fh-page="blood"] .fh-b27-toc{border-style:solid;border-radius:18px;border-color:rgba(255,199,206,.3)}
.fh-b27[data-fh-page="blood"] .fh-b27-toc ol{columns:2;column-gap:28px}
.fh-b27-bl-box{border:1.5px solid rgba(255,199,206,.35);border-radius:20px;background:var(--deep);padding:16px;display:flex;flex-direction:column;gap:14px}
.fh-b27-bl-pick{display:grid;grid-template-columns:1fr auto 1fr;gap:10px;align-items:center}
.fh-b27-bl-pick fieldset{border:0;margin:0;padding:0;display:flex;flex-direction:column;gap:6px;align-items:center}
.fh-b27-bl-pick legend{font-size:13px;color:var(--sub);margin-bottom:4px;text-align:center}
.fh-b27-bl-pick .row{display:flex;gap:6px}
.fh-b27-bl-pick label{cursor:pointer}
.fh-b27-bl-pick input{position:absolute;opacity:0}
.fh-b27-bl-pick label span{display:flex;width:52px;height:52px;border-radius:50%;align-items:center;justify-content:center;font:800 17px inherit;border:2px solid var(--c);color:var(--c);background:transparent;transition:.2s}
.fh-b27-bl-pick input:checked+span{background:var(--c);color:#fff;transform:scale(1.08)}
.fh-b27-bl-pick input:focus-visible+span{outline:2px solid #fff}
.fh-b27-bl-x{font:800 26px 'Shippori Mincho',serif;color:var(--gold)}
.fh-b27-bl-go{min-height:48px;border:0;border-radius:999px;background:linear-gradient(90deg,#E8707E,#9C7BD0);color:#fff;font:inherit;font-weight:800;padding:0 22px;cursor:pointer;align-self:center}
/* 2026-10-29 明るい色（血液型の4色・ピンク〜紫）の上は濃い文字に（絶対ルール） */.fh-b27-bl-drop,.fh-b27-bl-pick input:checked+span,.fh-b27-bl-go,.fh-b27[data-fh-page="blood"] .fh-b27-tape,.fh-b27[data-fh-page="blood"] h2 .fh-b27-n{color:#2A2233}
.fh-b27-bl-res{background:var(--cream);color:var(--cream-ink);border-radius:18px;padding:16px 18px;line-height:1.85}
.fh-b27 .fh-b27-bl-res p,.fh-b27 .fh-b27-bl-res b{color:var(--cream-ink)}
.fh-b27 .fh-b27-bl-res a{color:#A23B52;font-weight:700}
.fh-b27-bl-meet{display:flex;justify-content:center;gap:4px;height:70px;margin:2px 0 8px}
.fh-b27-bl-meet .fh-b27-bl-drop{animation:fh-b27-bl-l .8s ease forwards}.fh-b27-bl-meet .fh-b27-bl-drop+.fh-b27-bl-drop{animation-name:fh-b27-bl-r}
@keyframes fh-b27-bl-l{from{transform:translateX(-60px);opacity:0}to{transform:translateX(6px);opacity:1}}@keyframes fh-b27-bl-r{from{transform:translateX(60px);opacity:0}to{transform:translateX(-6px);opacity:1}}
.fh-b27-bl-score{text-align:center;font-size:26px;color:#D2405C;letter-spacing:.1em;opacity:0;animation:fh-b27-bl-in .5s ease .8s forwards}
.fh-b27-bl-card{opacity:0;animation:fh-b27-bl-in .6s ease 1s forwards}@keyframes fh-b27-bl-in{to{opacity:1}}
.fh-b27-bl-res .ct{text-align:center;font-family:'Shippori Mincho',serif;font-size:18px;color:#A23B52;margin:0 0 6px}
.fh-b27-bl-tabs{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}
.fh-b27-bl-tabs button{min-height:38px;border:1px solid #EBC5CD;border-radius:999px;background:#fff;color:#6A3040;font:inherit;font-size:14px;font-weight:700;padding:0 14px;cursor:pointer}
.fh-b27-bl-tabs button[aria-selected="true"]{background:#A23B52;border-color:#A23B52;color:#fff}
.fh-b27-bl-pane{background:#fff;border-radius:12px;padding:12px 14px;min-height:5em}
.fh-b27-bl-tip{margin-top:10px;background:#FFF0DA;border-radius:12px;padding:10px 14px}
.fh-b27-bl-mx{width:100%;max-width:520px;margin:0 auto;border-collapse:separate;border-spacing:4px;text-align:center}
.fh-b27-bl-mx th{font-weight:800;color:var(--sub)}
.fh-b27-bl-mx td a{display:block;border-radius:10px;padding:8px 2px;background:rgba(255,255,255,.06);color:#FFB7C3;text-decoration:none;font-size:13px;letter-spacing:-.05em}
.fh-b27-bl-mx td a b{display:block;font-size:12px;color:var(--sub);letter-spacing:0}
.fh-b27-bl-types{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.fh-b27-bl-types div{border:1px solid rgba(255,199,206,.25);border-top:5px solid var(--c);border-radius:14px;background:var(--deep);padding:10px 14px;font-size:14px;line-height:1.8}
.fh-b27-bl-types b{font:800 20px 'Shippori Mincho',serif}
.fh-b27-bl-list{display:flex;flex-direction:column;gap:8px}
.fh-b27-bl-list details{border:1px solid rgba(255,199,206,.25);border-radius:16px;background:var(--deep);padding:6px 14px}
.fh-b27-bl-list summary{cursor:pointer;font-family:'Shippori Mincho',serif;font-weight:800;font-size:17px;color:#FFC7CE}
.fh-b27-bl-list summary small{font-family:'Zen Kaku Gothic New',sans-serif;font-weight:400;color:var(--mute);font-size:12.5px;margin-left:8px}
.fh-b27-bl-list p{font-size:14.5px;line-height:1.9;margin:6px 0}
.fh-b27-bl-qa details{border-bottom:1px dashed var(--line);padding:8px 2px}
.fh-b27-bl-qa summary{cursor:pointer;font-weight:700}
.fh-b27-bl-qa p{margin-top:6px;font-size:14.5px}
.fh-b27-bl-wk{display:flex;flex-wrap:wrap;gap:10px;align-items:flex-end;justify-content:center}
.fh-b27-bl-wk label{display:flex;flex-direction:column;gap:4px;font-size:13px;color:var(--sub)}
.fh-b27-bl-wk input[type=date]{min-height:46px;border-radius:12px;border:1.5px solid rgba(255,199,206,.45);background:#fff;color:#3A2129;font:inherit;padding:0 10px}
.fh-b27-bl-wkres .wd{display:inline-block;border-radius:999px;background:#A23B52;color:#fff;font-weight:800;padding:2px 12px;font-size:13px;margin-bottom:6px}
.fh-b27-bl-days{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.fh-b27-bl-days details{border:1px solid rgba(255,199,206,.25);border-radius:14px;background:var(--deep);padding:8px 14px;font-size:14px;line-height:1.85}
.fh-b27-bl-days summary{cursor:pointer;font-weight:800;color:#FFC7CE}
.fh-b27-bl-days summary small{font-weight:400;color:var(--mute);margin-left:6px}
.fh-b27-bl-days ul{margin:6px 0 0;padding-left:1.1em}
@media (max-width:640px){.fh-b27-bl-days{grid-template-columns:1fr}}
@media (max-width:640px){.fh-b27-bl-types{grid-template-columns:1fr}.fh-b27[data-fh-page="blood"] .fh-b27-toc ol{columns:1}.fh-b27[data-fh-page="blood"] .fh-b27-title{font-size:25px}
 .fh-b27-bl-pick{grid-template-columns:1fr}.fh-b27-bl-x{text-align:center}.fh-b27-bl-pick label span{width:56px;height:56px}}
@media (prefers-reduced-motion:reduce){.fh-b27-bl-emb .fh-b27-bl-drop,.fh-b27-bl-meet .fh-b27-bl-drop{animation:none}.fh-b27-bl-score,.fh-b27-bl-card{animation:none;opacity:1}}
</style>"""

JS = r"""(function(){var P=__P__,COL=__COL__,TY=['A','B','O','AB'];function $(i){return document.getElementById(i)}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
if(!$('bl-go'))return;function val(n){var e=document.querySelector('input[name="'+n+'"]:checked');return e?e.value:null}
function key(a,b){var i=TY.indexOf(a),j=TY.indexOf(b);return i<=j?a+'-'+b:b+'-'+a}
function drop(t){return '<span class="fh-b27-bl-drop" style="--c:'+COL[t]+'">'+t+'</span>'}
function show(a,b){var k=key(a,b),x=P[k],r=$('bl-res'),st='';for(var i=0;i<5;i++)st+=i<x.score?'♥︎':'♡︎';
 var tb=[['love','恋愛'],['friend','友達'],['work','仕事'],['marriage','結婚'],['male_female','男女で違う？']];
 r.innerHTML='<div class="fh-b27-bl-meet" aria-hidden="true">'+drop(a)+drop(b)+'</div><div class="fh-b27-bl-score" aria-label="相性 5段階中'+x.score+'">'+st+'</div><div class="fh-b27-bl-card"><p class="ct">'+a+'型×'+b+'型：'+esc(x.catch)+'</p><div class="fh-b27-bl-tabs" role="tablist">'+tb.map(function(t,i){return '<button type="button" role="tab" data-t="'+t[0]+'" aria-selected="'+(i?'false':'true')+'">'+t[1]+'</button>'}).join('')+'</div><div class="fh-b27-bl-pane" id="bl-pane"><p>'+esc(x.love)+'</p></div><div class="fh-b27-bl-tip"><b>仲良くいるコツ：</b>'+esc(x.tip)+'</div><p><a href="#bl-'+k+'">'+a+'型×'+b+'型の説明へ →</a>　<a href="#b27-bl-week">生まれた曜日も合わせると？ →</a></p></div>';
 r.hidden=false;r.querySelectorAll('.fh-b27-bl-tabs button').forEach(function(btn){btn.addEventListener('click',function(){r.querySelectorAll('.fh-b27-bl-tabs button').forEach(function(z){z.setAttribute('aria-selected','false')});btn.setAttribute('aria-selected','true');$('bl-pane').innerHTML='<p>'+esc(x[btn.getAttribute('data-t')])+'</p>';});});}
$('bl-go').addEventListener('click',function(){var a=val('bl-a'),b=val('bl-b');if(a&&b)show(a,b)});
var W=__W__,T=__T__;if($('bl-wgo'))$('bl-wgo').addEventListener('click',function(){var v=$('bl-wd').value,t=val('bl-w'),r=$('bl-wres');if(!v||!t){r.hidden=false;r.innerHTML='<p>生年月日と血液型を選んでください。</p>';return}
 var p=v.split('-'),d=new Date(+p[0],+p[1]-1,+p[2]);if(isNaN(d)){return}var w=W[d.getDay()];
 r.hidden=false;r.innerHTML='<div class="fh-b27-bl-card" style="opacity:1;animation:none"><p class="ct">'+t+'型×'+w.name+'生まれ</p><span class="wd">'+w.name+'＝'+w.star+'の日｜'+esc(w.kw)+'</span><p>'+esc(w.text)+'</p><p><b>'+t+'型と合わさると：</b>'+esc(w.by[t])+'</p><p><b>'+t+'型の基本：</b>'+esc(T[t].catch)+'（'+esc(T[t].kw)+'）</p><p><a href="#bl-days">7つの曜日をすべて見る →</a></p></div>';});
document.querySelectorAll('[data-bl]').forEach(function(l){l.addEventListener('click',function(e){e.preventDefault();var p=l.getAttribute('data-bl').split('-');document.querySelector('input[name="bl-a"][value="'+p[0]+'"]').checked=true;document.querySelector('input[name="bl-b"][value="'+p[1]+'"]').checked=true;show(p[0],p[1]);$('b27-bl-pick').scrollIntoView({behavior:'smooth'});})});
})();"""


def build(sample, updated):
    H = []
    a = H.append
    a(CSS)
    a('<div class="fh-b27" data-fh-page="blood">\n<div class="fh-b27-note">')
    emb = "".join(f'<span class="fh-b27-bl-drop" style="--c:{COL[t]};--i:{i}">{t}</span>' for i, t in enumerate(TY))
    a(f'''<header class="fh-b27-hero">
  <div class="fh-b27-bl-emb" aria-hidden="true">{emb}</div>
  <div class="fh-b27-hero-body">
    <span class="fh-b27-tape">人生予報 血液型相性</span>
    <h1 class="fh-b27-title">血液型相性占い<br>恋愛・友達・仕事・結婚の相性</h1>
    <p class="fh-b27-lead">あなたとお相手の血液型を選ぶだけで、二人の相性がわかります。A型・B型・O型・AB型の10通りの組み合わせについて、恋愛・友達・仕事・結婚の相性と、男女が入れ替わったときの違い、仲良くいるコツまで紹介します。</p>
  </div>
</header>''')
    items = [("b27-bl-pick", "二人の相性を占う"), ("b27-bl-table", "相性の早見表とランキング"), ("b27-bl-types", "4つの血液型の性格"),
             ("b27-bl-pairs", "10通りの組み合わせの相性"), ("b27-bl-week", "生まれた曜日も合わせて見る（28タイプ）"), ("b27-bl-faq", "よくある質問")]
    a('<nav class="fh-b27-toc" aria-label="目次"><strong>このページの内容</strong><ol>' + "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in items) + "</ol></nav>")
    n = [0]

    def h2(t):
        n[0] += 1
        return f'<h2><span class="fh-b27-n">{n[0]}</span><span>{t}</span></h2>'

    def grp(name, who, dflt):
        lab = "".join(f'<label><input type="radio" name="{name}" value="{t}"{" checked" if t == dflt else ""}><span style="--c:{COL[t]}">{t}型</span></label>' for t in TY)
        return f'<fieldset><legend>{who}の血液型</legend><div class="row">{lab}</div></fieldset>'
    a(f'''<section class="fh-b27-sec" id="b27-bl-pick">
  {h2("二人の相性を占う")}
  <div class="fh-b27-bl-box">
    <div class="fh-b27-bl-pick">{grp("bl-a", "あなた", "A")}<span class="fh-b27-bl-x" aria-hidden="true">×</span>{grp("bl-b", "お相手", "O")}</div>
    <button type="button" class="fh-b27-bl-go" id="bl-go">相性を見る</button>
    <div class="fh-b27-bl-res" id="bl-res" aria-live="polite" hidden></div>
  </div>
</section>''')
    head = "".join(f"<th scope='col'>{t}型</th>" for t in TY)
    rows = ""
    for x in TY:
        rows += f"<tr><th scope='row'>{x}型</th>"
        for y in TY:
            k = key(x, y)
            rows += f'<td><a href="#bl-{k}" data-bl="{x}-{y}"><b>{x}×{y}</b>{stars(B.PAIRS[k]["score"])}</a></td>'
        rows += "</tr>"
    rk = sorted(B.PAIRS.items(), key=lambda kv: (-kv[1]["score"], list(B.PAIRS).index(kv[0])))
    rank = "".join(f'<li><a href="#bl-{k}">{k.replace("-", "型×")}型</a>　{stars(v["score"])}　{esc(v["catch"])}</li>' for k, v in rk)
    a(f'''<section class="fh-b27-sec" id="b27-bl-table">
  {h2("相性の早見表とランキング")}
  <p>ハートが多いほど、自然に仲良くなりやすい組み合わせです。少ない組み合わせも「合わない」という意味ではなく、違いを知ると補い合える関係です。マスを押すと、その組み合わせの結果が上に出ます。</p>
  <table class="fh-b27-bl-mx"><thead><tr><th></th>{head}</tr></thead><tbody>{rows}</tbody></table>
  <h3>相性ランキング</h3>
  <ol>{rank}</ol>
</section>''')
    tc = "".join(f'<div style="--c:{COL[t]}"><b style="color:{COL[t]}">{t}型</b>　<small>{esc(B.TYPES[t]["kw"])}</small><br>{esc(B.TYPES[t]["text"])}'
                 f'<br><small>恋愛：{esc(B.TYPES[t]["love"])}<br>いいところ：{esc(B.TYPES[t]["strength"])}<br>気をつけたいところ：{esc(B.TYPES[t]["care"])}</small></div>' for t in TY)
    a(f'''<section class="fh-b27-sec" id="b27-bl-types">
  {h2("4つの血液型の性格")}
  <p>日本の血液型占いでよく語られる、それぞれの血液型の傾向です。</p>
  <div class="fh-b27-bl-types">{tc}</div>
</section>''')
    pd = "".join(f'<details id="bl-{k}"><summary>{k.replace("-", "型×")}型<small>{stars(v["score"])}　{esc(v["catch"])}</small></summary>'
                 f'<p><b>恋愛：</b>{esc(v["love"])}</p><p><b>友達：</b>{esc(v["friend"])}</p><p><b>仕事：</b>{esc(v["work"])}</p><p><b>結婚：</b>{esc(v["marriage"])}</p>'
                 f'<p><b>男女で違う？：</b>{esc(v["male_female"])}</p><p><b>仲良くいるコツ：</b>{esc(v["tip"])}</p></details>' for k, v in B.PAIRS.items())
    a(f'''<section class="fh-b27-sec" id="b27-bl-pairs">
  {h2("10通りの組み合わせの相性")}
  <div class="fh-b27-bl-list">{pd}</div>
  <p class="fh-b27-small">誕生日どうしの相性は<a href="/compatibility/">誕生日相性占い</a>で見られます。</p>
</section>''')
    wr = "".join(f'<label><input type="radio" name="bl-w" value="{t}"{" checked" if t == "A" else ""}><span style="--c:{COL[t]}">{t}型</span></label>' for t in TY)
    dd = "".join(f'<details><summary>{esc(w["name"])}生まれ<small>{esc(w["star"])}｜{esc(w["kw"])}</small></summary><p>{esc(w["text"])}</p><ul>'
                 + "".join(f'<li><b>{t}型：</b>{esc(w["by"][t])}</li>' for t in TY) + '</ul></details>' for w in B.WEEKDAYS)
    a(f'''<section class="fh-b27-sec" id="b27-bl-week">
  {h2("生まれた曜日も合わせて見る（28タイプ）")}
  <p>曜日の名前は、昔の人が空に見ていた7つの星に由来します。生まれた曜日の星のイメージを血液型と重ねると、4つの血液型×7つの曜日で28タイプに分かれます。生年月日を入れると、生まれた曜日を自動で計算します。</p>
  <div class="fh-b27-bl-box">
    <div class="fh-b27-bl-wk"><label>あなたの生年月日<input type="date" id="bl-wd" min="1900-01-01" max="2030-12-31" value="1995-01-01"></label></div>
    <div class="fh-b27-bl-pick" style="grid-template-columns:1fr"><fieldset><legend>あなたの血液型</legend><div class="row">{wr}</div></fieldset></div>
    <button type="button" class="fh-b27-bl-go" id="bl-wgo">28タイプを見る</button>
    <div class="fh-b27-bl-res fh-b27-bl-wkres" id="bl-wres" aria-live="polite" hidden></div>
  </div>
  <h3 id="bl-days">7つの曜日の性格と、血液型との組み合わせ</h3>
  <div class="fh-b27-bl-days">{dd}</div>
</section>''')
    qa = "".join(f'<details{" open" if i == 0 else ""}><summary>Q. {esc(q)}</summary><p>A. {esc(x)}</p></details>' for i, (q, x) in enumerate(B.FAQ))
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in B.FAQ]}
    a(f'''<section class="fh-b27-sec" id="b27-bl-faq">
  {h2("よくある質問")}
  <div class="fh-b27-bl-qa">{qa}</div>
</section>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<section class="fh-b27-sec" id="b27-bl-more">
  <div class="fh-b27-links">
    <a href="/seinengappi/"><b>生年月日まるごと診断 →</b><small>8つの占いをまとめて</small></a>
    <a href="/compatibility/"><b>誕生日相性占い →</b><small>2人の生年月日で相性を見る</small></a>
    <a href="/mbti-compatibility/"><b>MBTI相性占い →</b><small>性格タイプどうしの相性</small></a>
  </div>
</section>''')
    js = JS.replace("__W__", json.dumps(B.WEEKDAYS, ensure_ascii=False)).replace("__T__", json.dumps({t: {"catch": B.TYPES[t]["catch"], "kw": B.TYPES[t]["kw"]} for t in TY}, ensure_ascii=False)).replace("__P__", json.dumps(B.PAIRS, ensure_ascii=False)).replace("__COL__", json.dumps(COL))
    up = dt.date.fromisoformat(updated)
    a(f'<p class="fh-b27-foot">血液型と性格・相性の関係は、科学的には確かめられていません。このページは、日本で親しまれている血液型占いの考え方をもとに、このサイトで書いたものです。楽しみと会話のきっかけとしてお読みください。<br>'
      f'最終更新日：{up.year}年{up.month}月{up.day}日／<a href="/about/">この記事の作成方針について</a></p>')
    a("</div>\n</div>")
    a(f"<script>document.addEventListener('DOMContentLoaded',function(){{{js}}});</script>")
    title = "血液型相性占い｜A型・B型・O型・AB型の恋愛・友達・仕事・結婚の相性ランキング【無料】"
    desc = ("血液型を選ぶだけで二人の相性がわかる無料の血液型相性占い。A型・B型・O型・AB型の10通りの組み合わせの恋愛・友達・仕事・結婚の相性、"
            "男女で違うところ、仲良くいるコツ、相性の早見表、生まれた曜日と合わせた28タイプの性格を紹介します。")
    out = shell(title, desc, URL, "\n".join(H), sample)
    assert "！" not in out and "動物占い" not in out
    return out


def main():
    updated = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    for sample, path in ((False, os.path.join(OUT, "blood.html")), (True, os.path.join(OUT, "sample", "blood.html"))):
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(build(sample, updated))
        print("→", os.path.relpath(path, WORK))


if __name__ == "__main__":
    main()
