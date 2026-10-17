"""数秘術のページ（新しい固定ページ /suhijutsu/）を作る（2026-10-18。検索「数秘術」月1万〜10万・「数秘術 計算」月1,000〜1万）。
作る前の確認：/number-fortune/（静的ページ「数字占い」＝好きな数字3つで読む遊び）はあるが、生年月日から計算する数秘術のページは無い。
/number-fortune/ はこのページの「好きな数字で読む」にまとめて 301（ローカル）。計算は knowledge/08_数秘術.md と同じ（366日ページと数が食い違わないように）。
文章：work/scripts/suhi_texts.py（このサイトの言葉）。決め方：work/knowledge/14_数秘術ページの規則.md
使い方: python work/scripts/build_suhi.py [最終更新日]
出力: work/out/suhijutsu.html（投入用）、work/out/sample/suhijutsu.html（確認用）
"""
import datetime as dt, html, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_hub import OUT, WORK, shell  # noqa: E402
from calc_maya_num_bio import life_path, reduce  # noqa: E402
import suhi_texts as S  # noqa: E402
import aff_extra as AX  # noqa: E402
PY_GOODS = {1: [('手帳 2027', '2027年の手帳', '「新しい9年の始まり」の年。始めたいことと目標を書き出す手帳を。', 'stationery'), ('やりたいことリストのノート', 'やりたいことリストのノート', '今年やってみたいことを、思いつくまま書き出して。', 'stationery')], 2: [('ペアのマグカップ', 'ペアのマグカップ', '人との協力が実る年。大切な人とそろえて使えるものを。', 'tableware'), ('ペアのキーホルダー', 'ペアのキーホルダー', 'パートナーや仲間とのおそろいに。', 'accessory')], 3: [('アイデアノート', 'アイデアノート', '表現が広がる年。思いついたことをすぐ書きとめられるノートを。', 'stationery'), ('一冊のノート', '気に入った一冊のノート', '作ったものや考えを、人に見せる前の下書きに。', 'stationery')], 4: [('家計簿', '家計簿', '土台を固める年。お金の流れを整える家計簿を。', 'stationery'), ('家計簿ノート', '家計簿ノート', '毎日続ける習慣づくりに。', 'stationery')], 5: [('小さな旅行バッグ', '小さな旅行バッグ', '変化と移動の年。身軽に出かけられるバッグを。', 'travel'), ('旅のお守り袋', '旅のお守り袋', '移動の多い年の、お守りに。', 'omamori')], 6: [('ヒノキの入浴剤セット', 'ヒノキの入浴剤セット', '身近な人を大切にする年。家族でくつろげる時間に。', 'bath'), ('カップル ペア ギフト 名入れ', '名入れのペアギフト', '家族や大切な人への贈り物に。', 'gift')], 7: [('しおり付きの文庫本', 'しおり付きの文庫本', '学びと見直しの年。ひとりで読書する時間を。', 'book'), ('ノート型の日記', 'ノート型の日記', '考えたことを書き残す、ひとりの時間に。', 'stationery')], 8: [('上質な財布', '上質な財布', '実りを受け取る年。お金を大切に扱う財布を。', 'wallet'), ('がま口の財布', 'がま口の財布', '「お金が入る口が大きい」縁起物としても。', 'wallet')], 9: [('アロマキャンドル', 'アロマキャンドル', '締めくくりと手放しの年。気持ちをリセットする香りを。', 'aroma'), ('入浴剤の詰め合わせ', '入浴剤の詰め合わせ', '一日の終わりに、心と体の疲れを手放して。', 'bath')]}

URL = "/suhijutsu/"
ORDER = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 22, 33]
BASE = {11: 2, 22: 4, 33: 6}
COL = {1: "#E8707E", 2: "#F2A65A", 3: "#F2D45B", 4: "#8CC96B", 5: "#4FC1B0", 6: "#5FA8D3", 7: "#7D8CE0", 8: "#B07BD8", 9: "#E07BB5",
       11: "#F6C177", 22: "#F6C177", 33: "#F6C177"}


def esc(s):
    return html.escape(str(s), quote=True)


def grp(n):
    return S.GROUP[BASE.get(n, n)]


def ckey(a, b):
    ga, gb = grp(a), grp(b)
    if ga == gb:
        return "同じ"
    k = "-".join(sorted((ga, gb), key="動整響".index))
    return {"動-響": "動-響", "整-響": "整-響", "動-整": "動-整"}[k]


def hearts(n):
    return "♥︎" * n + "♡︎" * (5 - n)


def py2027(m, d):
    return reduce(2 + 0 + 2 + 7 + sum(int(c) for c in f"{m}{d}"), keep_master=False)


CSS = """<style id="fh-b27-sh-css">
.fh-b27[data-fh-page="suhi"]{--ink:#F4F1FF;--sub:#DAD3F2;--mute:#B4ABD3;--paper:#1C1838;--deep:#15122B;--line:#423A6E;--gold:#F6C177;--cream:#FFFBF2;--cream-ink:#2E2650}
.fh-b27[data-fh-page="suhi"] a{color:#FFD9A0}
.fh-b27[data-fh-page="suhi"] .fh-b27-sec>p,.fh-b27[data-fh-page="suhi"] .fh-b27-lead,.fh-b27[data-fh-page="suhi"] ol{text-shadow:0 1px 2px rgba(0,0,0,.6)}
.fh-b27[data-fh-page="suhi"] .fh-b27-note{border-left:0;border-radius:24px;background-color:var(--paper);
 background-image:radial-gradient(circle at 12% 0%,rgba(246,193,119,.18),transparent 40%),radial-gradient(circle at 100% 55%,rgba(125,140,224,.22),transparent 45%);box-shadow:0 18px 40px rgba(0,0,0,.25);background-size:auto;background-repeat:no-repeat}
.fh-b27[data-fh-page="suhi"] .fh-b27-hero{align-items:center}
.fh-b27-sh-emb{position:relative;width:120px;height:120px;flex:0 0 auto}
.fh-b27-sh-emb span{position:absolute;left:50%;top:50%;width:26px;height:26px;margin:-13px;border-radius:50%;display:flex;align-items:center;justify-content:center;
 font:800 14px 'Shippori Mincho',serif;color:#1C1838;background:var(--c);transform:rotate(calc(var(--i)*40deg)) translateY(-46px) rotate(calc(var(--i)*-40deg))}
.fh-b27-sh-emb b{position:absolute;inset:34px;border-radius:50%;border:1.5px solid rgba(246,193,119,.6);display:flex;align-items:center;justify-content:center;font:800 13px 'Shippori Mincho',serif;color:var(--gold);letter-spacing:.1em}
.fh-b27-sh-emb{animation:fh-b27-sh-turn 40s linear infinite}@keyframes fh-b27-sh-turn{to{transform:rotate(360deg)}}
.fh-b27[data-fh-page="suhi"] .fh-b27-tape{transform:none;border-radius:999px;background:linear-gradient(90deg,#F6C177,#B07BD8);color:#1C1838}
.fh-b27[data-fh-page="suhi"] .fh-b27-title{font-family:'Shippori Mincho',serif;font-weight:800;font-size:30px}
.fh-b27[data-fh-page="suhi"] h2{font-family:'Shippori Mincho',serif;font-weight:800;font-size:24px}
.fh-b27[data-fh-page="suhi"] h2 .fh-b27-n{border:0;border-radius:50%;background:linear-gradient(135deg,#F6C177,#B07BD8);color:#1C1838}
.fh-b27[data-fh-page="suhi"] .fh-b27-toc{border-style:solid;border-radius:18px;border-color:rgba(246,193,119,.3)}
.fh-b27[data-fh-page="suhi"] .fh-b27-toc ol{columns:2;column-gap:28px}
.fh-b27-sh-box{border:1.5px solid rgba(246,193,119,.35);border-radius:20px;background:var(--deep);padding:16px;display:flex;flex-direction:column;gap:14px}
.fh-b27-sh-row{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;align-items:flex-end}
.fh-b27-sh-row label{display:flex;flex-direction:column;gap:4px;font-size:13px;color:var(--sub)}
.fh-b27-sh-row input{min-height:46px;border-radius:12px;border:1.5px solid rgba(246,193,119,.45);background:#fff;color:#2E2650;font:inherit;padding:0 10px}
.fh-b27-sh-row input[type=number]{width:9em}
.fh-b27-sh-go{min-height:48px;border:0;border-radius:999px;background:linear-gradient(90deg,#F6C177,#B07BD8);color:#1C1838;font:inherit;font-weight:800;padding:0 22px;cursor:pointer;align-self:center}
.fh-b27-sh-res{background:var(--cream);color:var(--cream-ink);border-radius:18px;padding:16px 18px;line-height:1.85}
.fh-b27 .fh-b27-sh-res p,.fh-b27 .fh-b27-sh-res b,.fh-b27 .fh-b27-sh-res li{color:var(--cream-ink)}
.fh-b27 .fh-b27-sh-res a{color:#6A3FA0;font-weight:700}
.fh-b27-sh-big{display:flex;justify-content:center;gap:10px;flex-wrap:wrap;margin:0 0 10px}
.fh-b27-sh-big div{min-width:96px;text-align:center;border-radius:16px;background:#fff;border:1px solid #E6DCF5;padding:8px 10px}
.fh-b27-sh-big small{display:block;font-size:12px;color:#6B5F86}
.fh-b27-sh-big b{display:block;font:800 34px/1.1 'Shippori Mincho',serif;color:#6A3FA0}
.fh-b27-sh-big .pop{animation:fh-b27-sh-pop .7s ease both}.fh-b27-sh-big div:nth-child(2) .pop{animation-delay:.15s}.fh-b27-sh-big div:nth-child(3) .pop{animation-delay:.3s}
@keyframes fh-b27-sh-pop{from{transform:scale(.3);opacity:0}to{transform:scale(1);opacity:1}}
.fh-b27-sh-res .ct{text-align:center;font-family:'Shippori Mincho',serif;font-size:18px;color:#6A3FA0;margin:0 0 6px}
.fh-b27-sh-res .py{margin-top:10px;background:#FFF0DA;border-radius:12px;padding:10px 14px}
.fh-b27-sh-steps{counter-reset:s;list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:8px}
.fh-b27-sh-steps li{counter-increment:s;border:1px solid rgba(246,193,119,.25);border-radius:14px;background:var(--deep);padding:10px 14px 10px 48px;position:relative;line-height:1.8}
.fh-b27-sh-steps li::before{content:counter(s);position:absolute;left:12px;top:10px;width:26px;height:26px;border-radius:50%;background:var(--gold);color:#1C1838;font-weight:800;display:flex;align-items:center;justify-content:center}
.fh-b27-sh-steps code{font-family:inherit;background:rgba(255,255,255,.08);border-radius:6px;padding:1px 6px;color:#FFE3B8}
.fh-b27-sh-nums{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.fh-b27-sh-nums details{border:1px solid rgba(246,193,119,.22);border-top:5px solid var(--c);border-radius:14px;background:var(--deep);padding:8px 14px;font-size:14.5px;line-height:1.85}
.fh-b27-sh-nums summary{cursor:pointer;font-weight:800;color:#FFE3B8;list-style:none;display:flex;gap:10px;align-items:center}
.fh-b27-sh-nums summary::-webkit-details-marker{display:none}
.fh-b27-sh-nums summary b{font:800 26px/1 'Shippori Mincho',serif;color:var(--c);min-width:1.6em;text-align:center}
.fh-b27-sh-nums summary small{display:block;font-weight:400;color:var(--mute);font-size:12.5px}
.fh-b27-sh-nums p{margin:6px 0}
.fh-b27-sh-py{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
.fh-b27-sh-py div{border:1px solid rgba(246,193,119,.22);border-radius:14px;background:var(--deep);padding:10px 12px;font-size:14px;line-height:1.8}
.fh-b27-sh-py b{font:800 18px 'Shippori Mincho',serif;color:var(--gold)}
.fh-b27-sh-cyc{display:flex;justify-content:space-between;gap:4px;margin:4px 0 12px}
.fh-b27-sh-cyc span{flex:1;text-align:center;border-radius:10px;padding:6px 0;background:rgba(255,255,255,.06);font-weight:800;font-size:14px;color:var(--sub)}
.fh-b27-sh-cyc span small{display:block;font-weight:400;font-size:10.5px;color:var(--mute)}
.fh-b27-sh-grp{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
.fh-b27-sh-grp div{border:1px solid rgba(246,193,119,.22);border-radius:14px;background:var(--deep);padding:10px 12px;font-size:14px;line-height:1.8}
.fh-b27-sh-grp b{color:#FFE3B8}
.fh-b27-sh-mx{width:100%;border-collapse:separate;border-spacing:3px;text-align:center;font-size:12.5px}
.fh-b27-sh-mx th{color:var(--sub);font-weight:800}
.fh-b27-sh-mx td{border-radius:8px;padding:6px 0;color:#FFE3B8;font-weight:800;background:rgba(255,255,255,.05)}
.fh-b27-sh-mx td.s5{background:rgba(224,123,181,.28)}.fh-b27-sh-mx td.s4{background:rgba(224,123,181,.16)}
.fh-b27-sh-qa details{border-bottom:1px dashed var(--line);padding:8px 2px}
.fh-b27-sh-qa summary{cursor:pointer;font-weight:700}
.fh-b27-sh-qa p{margin-top:6px;font-size:14.5px}
.fh-b27-sh-scroll{overflow-x:auto}
@media (max-width:640px){.fh-b27-sh-nums,.fh-b27-sh-grp{grid-template-columns:1fr}.fh-b27-sh-py{grid-template-columns:repeat(2,minmax(0,1fr))}
 .fh-b27[data-fh-page="suhi"] .fh-b27-toc ol{columns:1}.fh-b27[data-fh-page="suhi"] .fh-b27-title{font-size:25px}.fh-b27-sh-emb{width:96px;height:96px}
 .fh-b27-sh-emb span{transform:rotate(calc(var(--i)*40deg)) translateY(-36px) rotate(calc(var(--i)*-40deg))}.fh-b27-sh-emb b{inset:26px;font-size:11px}.fh-b27-sh-mx{font-size:11px}}
@media (prefers-reduced-motion:reduce){.fh-b27-sh-emb,.fh-b27-sh-big .pop{animation:none}}
</style>"""

JS = r"""(function(){var N=__N__,PY=__PY__,G=__G__,GI=__GI__,C=__C__,BASE={11:2,22:4,33:6};function $(i){return document.getElementById(i)}
if(!$('sh-go'))return;
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function red(n,km){while(n>9&&!(km&&(n===11||n===22||n===33))){n=String(n).split('').reduce(function(a,c){return a+(+c)},0)}return n}
function digits(s){return String(s).replace(/\D/g,'').split('').reduce(function(a,c){return a+(+c)},0)}
function parse(v){var p=(v||'').split('-');if(p.length!==3)return null;var y=+p[0],m=+p[1],d=+p[2];var t=new Date(y,m-1,d);if(!y||t.getMonth()!==m-1)return null;return {y:y,m:m,d:d}}
function lp(b){return red(digits(''+b.y+(b.m<10?'0':'')+b.m+(b.d<10?'0':'')+b.d),true)}
function grp(n){return G[BASE[n]||n]}
function ck(a,b){var x=grp(a),y=grp(b);if(x===y)return '同じ';var o='動整響';var k=[x,y].sort(function(p,q){return o.indexOf(p)-o.indexOf(q)}).join('-');return k}
function hearts(n){var s='';for(var i=0;i<5;i++)s+=i<n?'♥︎':'♡︎';return s}
$('sh-go').addEventListener('click',function(){var b=parse($('sh-bd').value),r=$('sh-res');r.hidden=false;if(!b){r.innerHTML='<p>生年月日を入れてください。</p>';return}
 var L=lp(b),D=red(b.d,true),P=red(2+0+2+7+digits(''+b.m+b.d),false),x=N[L],py=PY[P];
 r.innerHTML='<div class="fh-b27-sh-big"><div><small>ライフパス</small><b class="pop">'+L+'</b></div><div><small>誕生日の数</small><b class="pop">'+D+'</b></div><div><small>2027年の数</small><b class="pop">'+P+'</b></div></div>'
 +'<p class="ct">ライフパス'+L+'「'+esc(x.name)+'」</p><p><b>'+esc(x.catch)+'</b>（'+esc(x.kw)+'）</p><p>'+esc(x.text)+'</p>'
 +'<p><b>恋愛：</b>'+esc(x.love)+'</p><p><b>仕事：</b>'+esc(x.work)+'</p><p><b>開運のヒント：</b>'+esc(x.tip)+'</p>'
 +'<div class="py"><b>2027年の数'+P+'：'+esc(py.theme)+'</b><br>'+esc(py.text)+'<br><b>やるといいこと：</b>'+esc(py.do)+'</div>'
 +'<p><a href="#sh-n'+L+'">ライフパス'+L+'の説明へ →</a>　<a href="/366uranai/'+(b.m<10?'0':'')+b.m+'-'+(b.d<10?'0':'')+b.d+'/">'+b.m+'月'+b.d+'日生まれの誕生日占いへ →</a></p>';for(var q=1;q<=9;q++){var e=$('sh-ad-'+q);if(e)e.hidden=(q!==P)}$('sh-ads').hidden=false;});
$('sh-cgo').addEventListener('click',function(){var a=parse($('sh-ca').value),b=parse($('sh-cb').value),r=$('sh-cres');r.hidden=false;if(!a||!b){r.innerHTML='<p>二人の生年月日を入れてください。</p>';return}
 var A=lp(a),B=lp(b),k=ck(A,B),c=C[k];
 r.innerHTML='<div class="fh-b27-sh-big"><div><small>あなた</small><b class="pop">'+A+'</b></div><div><small>お相手</small><b class="pop">'+B+'</b></div></div><p class="ct">'+hearts(c.score)+'</p><p><b>'+esc(GI[grp(A)].name)+'×'+esc(GI[grp(B)].name)+'</b></p><p>'+esc(c.text)+'</p><p><a href="#sh-n'+A+'">あなたの数</a>・<a href="#sh-n'+B+'">お相手の数</a>の説明も読んでみてください。</p>';});
$('sh-fgo').addEventListener('click',function(){var v=($('sh-fv').value||'').replace(/\D/g,''),r=$('sh-fres');r.hidden=false;if(!v||+v===0){r.innerHTML='<p>1以上の数字を入れてください。</p>';return}
 var n=red(digits(v),true),x=N[n];r.innerHTML='<p class="ct">'+esc(v)+' → '+n+'「'+esc(x.name)+'」</p><p><b>'+esc(x.catch)+'</b>（'+esc(x.kw)+'）</p><p><b>開運のヒント：</b>'+esc(x.tip)+'</p><p><a href="#sh-n'+n+'">'+n+'の説明へ →</a></p>';});
})();"""


def build(sample, updated):
    H = []
    a = H.append
    a(CSS)
    a('<div class="fh-b27" data-fh-page="suhi">\n<div class="fh-b27-note">')
    emb = "".join(f'<span style="--c:{COL[n]};--i:{i}">{n}</span>' for i, n in enumerate(range(1, 10)))
    a(f'''<header class="fh-b27-hero">
  <div class="fh-b27-sh-emb" aria-hidden="true">{emb}<b>11·22·33</b></div>
  <div class="fh-b27-hero-body">
    <span class="fh-b27-tape">人生予報 数秘術</span>
    <h1 class="fh-b27-title">数秘術<br>生年月日でライフパスナンバーを計算</h1>
    <p class="fh-b27-lead">生年月日を入れるだけで、数秘術のライフパスナンバー（生まれ持った性質を表す数）と、誕生日の数、2027年の数（パーソナルイヤー）がわかります。1〜9と11・22・33の12の数の性格・恋愛・仕事、計算のしかた、二人の相性もこのページで読めます。</p>
  </div>
</header>''')
    items = [("b27-sh-calc", "ライフパスナンバーを計算する"), ("b27-sh-how", "数秘術の計算のしかた"), ("b27-sh-nums", "12の数の意味"),
             ("b27-sh-py", "2027年の数（パーソナルイヤー）"), ("b27-sh-compat", "数秘術の相性"), ("b27-sh-fav", "好きな数字で読む"), ("b27-sh-faq", "よくある質問")]
    a('<nav class="fh-b27-toc" aria-label="目次"><strong>このページの内容</strong><ol>' + "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in items) + "</ol></nav>")
    n = [0]

    def h2(t):
        n[0] += 1
        return f'<h2><span class="fh-b27-n">{n[0]}</span><span>{t}</span></h2>'

    ads = AX.result_boxes("sh-ad", {k: (f"2027年の数が{k}のあなたに", v) for k, v in PY_GOODS.items()}, lead="2027年の数（パーソナルイヤー）の「やるといいこと」に合わせて選びました。楽天・Yahoo!ショッピングの商品ページへ移ります。")
    a(f'''<section class="fh-b27-sec" id="b27-sh-calc">
  {h2("ライフパスナンバーを計算する")}
  <div class="fh-b27-sh-box">
    <div class="fh-b27-sh-row"><label>あなたの生年月日<input type="date" id="sh-bd" min="1900-01-01" max="2030-12-31" value="1995-01-01"></label></div>
    <button type="button" class="fh-b27-sh-go" id="sh-go">数を計算する</button>
    <div class="fh-b27-sh-res" id="sh-res" aria-live="polite" hidden></div>
    <div id="sh-ads" style="width:100%" hidden>{ads}</div>
  </div>
</section>''')
    # 計算のしかた（例はスクリプトで計算）
    ex = dt.date(1990, 5, 15)
    dg = [int(c) for c in ex.strftime("%Y%m%d")]
    s1 = sum(dg)
    lp_ex = life_path(ex)
    pysum = 2 + 0 + 2 + 7 + 5 + 1 + 5
    py_ex = py2027(5, 15)
    assert lp_ex == 3 and py_ex == reduce(pysum, keep_master=False)
    ex2 = dt.date(1982, 11, 29)
    s2 = sum(int(c) for c in ex2.strftime("%Y%m%d"))
    a(f'''<section class="fh-b27-sec" id="b27-sh-how">
  {h2("数秘術の計算のしかた")}
  <p>数秘術では、数字を1けたになるまで足していきます。手で計算するときは、次の順に進めてください。例は1990年5月15日生まれの人です。</p>
  <ol class="fh-b27-sh-steps">
    <li><b>生年月日を8けたの数字にする</b><br>1990年5月15日 → <code>19900515</code></li>
    <li><b>すべての数字を1つずつ足す</b><br><code>{"+".join(map(str, dg))}＝{s1}</code></li>
    <li><b>2けたなら、またそのけたを足す</b><br><code>{"+".join(str(s1))}＝{lp_ex}</code> → ライフパスナンバーは<b>{lp_ex}</b></li>
    <li><b>11・22・33になったら、そこで止める</b><br>たとえば1982年11月29日生まれは、すべて足すと<code>{s2}</code>。33はそのまま残し、ライフパスは<b>{life_path(ex2)}</b>です。</li>
  </ol>
  <h3>誕生日の数と、2027年の数の出し方</h3>
  <p><b>誕生日の数</b>は、生まれた「日」だけを1けたにした数です（15日なら1+5＝6）。11日・29日（2+9＝11）・22日はそのまま11・22とします。</p>
  <p><b>2027年の数（パーソナルイヤー）</b>は、2027と誕生月・誕生日の数字をすべて足して1けたにします。5月15日生まれなら<code>2+0+2+7+5+1+5＝{pysum}</code>、<code>{"+".join(str(pysum))}＝{py_ex}</code>で、2027年は「{py_ex}」の年です。この数は11・22を残さず、必ず1〜9にします。</p>
  <p class="fh-b27-small">このサイトは、生年月日のすべての数字を一度に足す方法で計算しています。年・月・日を先にそれぞれ1けたにしてから足す方法をとるサイトもあり、11・22・33が出る日が少し変わることがあります。<a href="/366uranai/">366日の誕生日占い</a>や<a href="/seinengappi/">生年月日まるごと診断</a>の数も、このページと同じ方法です。</p>
</section>''')
    cards = "".join(
        f'<details id="sh-n{k}" style="--c:{COL[k]}"><summary><b>{k}</b><span>{esc(v["name"])}<small>{esc(v["kw"])}</small></span></summary>'
        f'<p><b>{esc(v["catch"])}</b></p><p>{esc(v["text"])}</p><p><b>恋愛：</b>{esc(v["love"])}</p><p><b>仕事：</b>{esc(v["work"])}</p>'
        f'<p><b>いいところ：</b>{esc(v["strength"])}<br><b>気をつけたいところ：</b>{esc(v["care"])}<br><b>開運のヒント：</b>{esc(v["tip"])}</p></details>'
        for k, v in ((k, S.NUMS[k]) for k in ORDER))
    a(f'''<section class="fh-b27-sec" id="b27-sh-nums">
  {h2("12の数の意味")}
  <p>ライフパスナンバーは1〜9の9つと、マスターナンバーと呼ばれる11・22・33の、全部で12あります。数字を押すと、性格・恋愛・仕事・開運のヒントが開きます。</p>
  <div class="fh-b27-sh-nums">{cards}</div>
</section>''')
    cyc = "".join(f'<span>{k}<small>{esc(S.PY[k]["theme"].replace("の年", ""))}</small></span>' for k in range(1, 10))
    pyc = "".join(f'<div><b>{k}の年</b>　{esc(S.PY[k]["theme"])}<br>{esc(S.PY[k]["text"])}<br><small>やるといいこと：{esc(S.PY[k]["do"])}／気をつけたいこと：{esc(S.PY[k]["care"])}</small></div>' for k in range(1, 10))
    a(f'''<section class="fh-b27-sec" id="b27-sh-py">
  {h2("2027年の数（パーソナルイヤー）")}
  <p>パーソナルイヤーは、1から9までの9年でひと回りする流れのうち、今年がどの段階かを表す数です。1で種をまき、9で締めくくって、また1から新しい周期が始まります。</p>
  <div class="fh-b27-sh-scroll"><div class="fh-b27-sh-cyc" aria-label="9年の流れ">{cyc}</div></div>
  <div class="fh-b27-sh-py">{pyc}</div>
</section>''')
    gi = "".join(f'<div><b>{esc(S.GROUP_INFO[g]["name"])}</b><br>{esc(S.GROUP_INFO[g]["text"])}</div>' for g in "動整響")
    head = "".join(f"<th scope='col'>{k}</th>" for k in ORDER)
    rows = ""
    for x in ORDER:
        rows += f"<tr><th scope='row'>{x}</th>"
        for y in ORDER:
            sc = S.COMPAT[ckey(x, y)]["score"]
            rows += f'<td class="s{sc}" title="{x}と{y}">{ {5: "◎", 4: "○", 3: "△"}[sc]}</td>'
        rows += "</tr>"
    ct = "".join(f'<p><b>{hearts(v["score"])}　{"同じグループどうし" if k == "同じ" else S.GROUP_INFO[k[0]]["name"] + "×" + S.GROUP_INFO[k[2]]["name"]}</b><br>{esc(v["text"])}</p>' for k, v in S.COMPAT.items())
    a(f'''<section class="fh-b27-sec" id="b27-sh-compat">
  {h2("数秘術の相性")}
  <p>このサイトでは、1〜9の数を大切にしているものの近さで3つのグループに分け、二人の相性の目安にしています。11は2、22は4、33は6のグループとして見ます。</p>
  <div class="fh-b27-sh-grp">{gi}</div>
  <div class="fh-b27-sh-box" style="margin-top:14px">
    <div class="fh-b27-sh-row"><label>あなたの生年月日<input type="date" id="sh-ca" min="1900-01-01" max="2030-12-31" value="1995-01-01"></label><label>お相手の生年月日<input type="date" id="sh-cb" min="1900-01-01" max="2030-12-31" value="1993-06-15"></label></div>
    <button type="button" class="fh-b27-sh-go" id="sh-cgo">二人の相性を見る</button>
    <div class="fh-b27-sh-res" id="sh-cres" aria-live="polite" hidden></div>
  </div>
  <h3>ライフパスナンバーの相性早見表</h3>
  <p class="fh-b27-small">◎＝同じグループでわかり合いやすい　○＝補い合える　△＝ペースの違いを話し合うと強いコンビに</p>
  <div class="fh-b27-sh-scroll"><table class="fh-b27-sh-mx"><thead><tr><th></th>{head}</tr></thead><tbody>{rows}</tbody></table></div>
  {ct}
</section>''')
    a(f'''<section class="fh-b27-sec" id="b27-sh-fav">
  {h2("好きな数字で読む")}
  <p>{esc(S.FAV_NOTE)}</p>
  <div class="fh-b27-sh-box">
    <div class="fh-b27-sh-row"><label>好きな数字・気になる数字<input type="number" id="sh-fv" min="1" max="99999999" value="7" inputmode="numeric"></label></div>
    <button type="button" class="fh-b27-sh-go" id="sh-fgo">数字を読む</button>
    <div class="fh-b27-sh-res" id="sh-fres" aria-live="polite" hidden></div>
  </div>
  <p class="fh-b27-small">時計やナンバープレートで同じ数字をくり返し見るときは、<a href="/angel-number/">エンジェルナンバーの意味一覧</a>も参考にしてください。</p>
</section>''')
    qa = "".join(f'<details{" open" if i == 0 else ""}><summary>Q. {esc(q)}</summary><p>A. {esc(x)}</p></details>' for i, (q, x) in enumerate(S.FAQ))
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in S.FAQ]}
    a(f'''<section class="fh-b27-sec" id="b27-sh-faq">
  {h2("よくある質問")}
  <div class="fh-b27-sh-qa">{qa}</div>
</section>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<section class="fh-b27-sec" id="b27-sh-more">
  <div class="fh-b27-links">
    <a href="/366uranai/"><b>366日の誕生日占い →</b><small>誕生日ごとの性格と2027年の運勢</small></a>
    <a href="/seinengappi/"><b>生年月日まるごと診断 →</b><small>数秘術を含む8つの占いをまとめて</small></a>
    <a href="/angel-number/"><b>エンジェルナンバー →</b><small>くり返し見る数字の意味</small></a>
    <a href="/compatibility/"><b>誕生日相性占い →</b><small>2人の生年月日で相性を見る</small></a>
  </div>
</section>''')
    js = (JS.replace("__N__", json.dumps({str(k): v for k, v in S.NUMS.items()}, ensure_ascii=False))
          .replace("__PY__", json.dumps({str(k): v for k, v in S.PY.items()}, ensure_ascii=False))
          .replace("__G__", json.dumps({str(k): v for k, v in S.GROUP.items()}, ensure_ascii=False))
          .replace("__GI__", json.dumps(S.GROUP_INFO, ensure_ascii=False))
          .replace("__C__", json.dumps(S.COMPAT, ensure_ascii=False)))
    up = dt.date.fromisoformat(updated)
    a(f'<p class="fh-b27-foot">数秘術は、数字に意味を重ねて楽しむ占いで、科学的に確かめられたものではありません。このページの文章と相性の決め方は、広く知られている数の意味をもとに、このサイトで書いたものです。'
      f'最終更新日：{up.year}年{up.month}月{up.day}日／<a href="/about/">この記事の作成方針について</a></p>')
    a("</div>\n</div>")
    a(f"<script>document.addEventListener('DOMContentLoaded',function(){{{js}}});</script>")
    title = "数秘術【無料】生年月日でライフパスナンバーを計算｜1〜9・11・22・33の意味と相性・2027年の運勢"
    desc = ("生年月日を入れるだけで数秘術のライフパスナンバー・誕生日の数・2027年の数（パーソナルイヤー）がわかる無料の数秘術。"
            "計算のしかた、1〜9と11・22・33の性格・恋愛・仕事、二人の相性、好きな数字の読み方も紹介します。")
    out = shell(title, desc, URL, "\n".join(H), sample)
    assert "！" not in out and "動物占い" not in out
    return out


def main():
    updated = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    for sample, path in ((False, os.path.join(OUT, "suhijutsu.html")), (True, os.path.join(OUT, "sample", "suhijutsu.html"))):
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(build(sample, updated))
        print("→", os.path.relpath(path, WORK))


if __name__ == "__main__":
    main()
