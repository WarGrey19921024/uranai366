"""トランプ占いのページ（/trump/ を WordPress の固定ページに作り直す）（2026-10-18。検索「トランプ占い」「トランプ 意味」月1,000〜1万）。
作る前の確認：/trump/・/trump/one/・/trump/two/・/trump/three/ は静的ページ（手もとのトランプで引いたカードを選ぶ形・各カードの意味は1行）。
このページ1つにまとめ（画面で引く＋手もとのカードを選ぶ・1〜3枚・テーマ別・53枚の意味）、静的のフォルダはローカルで退避し、one/two/three は /trump/ へ301。
文章：work/scripts/trump_texts.py（このサイトの言葉）。決め方：work/knowledge/16_トランプ占いページの規則.md
注意：WordPress（Diver）は [sp] [pc] などをショートコードとして消すので、JSで X[sp] のような書き方をしない。
使い方: python work/scripts/build_trump.py [最終更新日]
出力: work/out/trump.html（投入用）、work/out/sample/trump.html（確認用）
"""
import datetime as dt, html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_hub import OUT, WORK, shell  # noqa: E402
import trump_texts as T  # noqa: E402
import aff_extra as AX  # noqa: E402
TP_GOODS = {'heart': ('ハートが出たあなたに', [('ペアのキーホルダー', 'ペアのキーホルダー', '気持ちのつながりを表すハートの日に、おそろいの小物を。', 'accessory'), ('ペアのマグカップ', 'ペアのマグカップ', '大切な人と過ごす時間を、もっと楽しく。', 'tableware')]), 'diamond': ('ダイヤが出たあなたに', [('上質な財布', '上質な財布', 'お金と現実を表すダイヤの日に、お金を大切に扱う財布を。', 'wallet'), ('家計簿', '家計簿', '数字や条件を確かめる習慣づくりに。', 'stationery')]), 'club': ('クラブが出たあなたに', [('手帳 2027', '2027年の手帳', '行動と成長を表すクラブの日に、やることを書き出す手帳を。', 'stationery'), ('名刺入れ', '名刺入れ', '人との協力や新しい出会いの場に。', 'accessory')]), 'spade': ('スペードが出たあなたに', [('勾玉のお守り', '勾玉のお守り', '試練と知恵を表すスペードの日に、厄よけのお守りを。', 'omamori'), ('アロマキャンドル', 'アロマキャンドル', '冷静に考えたい夜に、気持ちを落ち着ける香りを。', 'aroma')])}

URL = "/trump/"
SO = ["heart", "diamond", "club", "spade"]


def esc(s):
    return html.escape(str(s), quote=True)


def rk(n):
    return T.RANK_NAME.get(n, str(n))


CSS = """<style id="fh-b27-tp-css">
.fh-b27[data-fh-page="trump"]{--ink:#F5F1EA;--sub:#DED6C8;--mute:#B9AE9B;--paper:#14261F;--deep:#0F1D18;--line:#3B5A4C;--gold:#E8C77A;--cream:#FFFDF8;--cream-ink:#2A2620}
.fh-b27[data-fh-page="trump"] a{color:#F2D99A}
.fh-b27[data-fh-page="trump"] .fh-b27-sec>p,.fh-b27[data-fh-page="trump"] .fh-b27-lead{text-shadow:0 1px 2px rgba(0,0,0,.6)}
.fh-b27[data-fh-page="trump"] .fh-b27-note{border-left:0;border-radius:24px;background-color:var(--paper);
 background-image:radial-gradient(ellipse at 50% 0%,rgba(46,110,80,.55),transparent 60%),radial-gradient(circle at 100% 100%,rgba(232,199,122,.10),transparent 40%);box-shadow:0 18px 40px rgba(0,0,0,.3),inset 0 0 0 1px rgba(232,199,122,.35);background-size:auto;background-repeat:no-repeat}
.fh-b27[data-fh-page="trump"] .fh-b27-hero{align-items:center}
.fh-b27-tp-emb{position:relative;width:150px;height:130px;flex:0 0 auto}
.fh-b27-tp-emb .fh-b27-tp-card{position:absolute;left:44px;top:6px;transform-origin:50% 120%}
.fh-b27-tp-emb .fh-b27-tp-card:nth-child(1){transform:rotate(-22deg)}.fh-b27-tp-emb .fh-b27-tp-card:nth-child(2){transform:rotate(-7deg)}.fh-b27-tp-emb .fh-b27-tp-card:nth-child(3){transform:rotate(8deg)}.fh-b27-tp-emb .fh-b27-tp-card:nth-child(4){transform:rotate(23deg)}
.fh-b27-tp-card{width:62px;height:88px;border-radius:8px;background:#FFFDF8;box-shadow:0 4px 12px rgba(0,0,0,.35);border:1px solid #E7DFD0;position:relative;display:flex;align-items:center;justify-content:center;font:800 30px 'Shippori Mincho',serif;color:#1F1B16}
.fh-b27-tp-card.red{color:#C2273A}
.fh-b27-tp-card i{position:absolute;left:5px;top:3px;font-style:normal;font-size:13px;line-height:1.05;text-align:center}
.fh-b27-tp-card i+i{left:auto;top:auto;right:5px;bottom:3px;transform:rotate(180deg)}
.fh-b27-tp-card.jk{font-size:13px;letter-spacing:.05em;color:#6B3FA0}
.fh-b27-tp-card.back{background:repeating-linear-gradient(45deg,#7A1F2E 0 6px,#8E2A3A 6px 12px);border:3px solid #FFFDF8}
.fh-b27[data-fh-page="trump"] .fh-b27-tape{transform:none;border-radius:999px;background:linear-gradient(90deg,#E8C77A,#C2273A);color:#1F1B16}
.fh-b27[data-fh-page="trump"] .fh-b27-title{font-family:'Shippori Mincho',serif;font-weight:800;font-size:30px}
.fh-b27[data-fh-page="trump"] h2{font-family:'Shippori Mincho',serif;font-weight:800;font-size:24px}
.fh-b27[data-fh-page="trump"] h2 .fh-b27-n{border:0;border-radius:50%;background:linear-gradient(135deg,#E8C77A,#C2273A);color:#1F1B16}
.fh-b27[data-fh-page="trump"] .fh-b27-toc{border-style:solid;border-radius:18px;border-color:rgba(232,199,122,.3)}
.fh-b27[data-fh-page="trump"] .fh-b27-toc ol{columns:2;column-gap:28px}
.fh-b27-tp-box{border:1.5px solid rgba(232,199,122,.35);border-radius:20px;background:var(--deep);padding:16px;display:flex;flex-direction:column;gap:12px;align-items:center}
.fh-b27-tp-opts{display:flex;flex-wrap:wrap;gap:8px;justify-content:center}
.fh-b27-tp-opts small{width:100%;text-align:center;color:var(--sub);font-size:12.5px}
.fh-b27-tp-opts button{min-height:42px;border-radius:999px;border:1.5px solid rgba(232,199,122,.45);background:transparent;color:var(--sub);font:inherit;font-weight:700;padding:0 16px;cursor:pointer}
.fh-b27-tp-opts button[aria-pressed="true"]{background:#E8C77A;border-color:#E8C77A;color:#1F1B16}
.fh-b27-tp-own{display:flex;flex-direction:column;gap:8px;align-items:center}
.fh-b27-tp-own[hidden]{display:none}
.fh-b27-tp-own label{display:flex;gap:6px;align-items:center;font-size:13px;color:var(--sub)}
.fh-b27-tp-own select{min-height:42px;border-radius:10px;border:1.5px solid rgba(232,199,122,.45);background:#fff;color:#2A2620;font:inherit;padding:0 8px}
.fh-b27-tp-go{min-height:50px;border:0;border-radius:999px;background:linear-gradient(90deg,#E8C77A,#C2273A);color:#1F1B16;font:inherit;font-weight:800;padding:0 26px;cursor:pointer}
.fh-b27-tp-res{width:100%;display:flex;flex-direction:column;gap:12px}
.fh-b27-tp-lay{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
.fh-b27-tp-pick{display:flex;flex-direction:column;align-items:center;gap:4px;font-size:12px;color:var(--sub);perspective:600px}
.fh-b27-tp-flip{position:relative;width:62px;height:88px;transform-style:preserve-3d;animation:fh-b27-tp-flip .7s ease forwards;animation-delay:calc(var(--i)*.35s)}
.fh-b27-tp-flip>div{position:absolute;inset:0;backface-visibility:hidden}.fh-b27-tp-flip>div+div{transform:rotateY(180deg)}
@keyframes fh-b27-tp-flip{from{transform:rotateY(0)}to{transform:rotateY(180deg)}}
.fh-b27-tp-sum{background:#FFF3D6;color:#3A2E16;border-radius:14px;padding:10px 14px;line-height:1.8}
.fh-b27 .fh-b27-tp-sum b{color:#3A2E16}
.fh-b27-tp-cardtxt{background:var(--cream);color:var(--cream-ink);border-radius:16px;padding:14px 16px;line-height:1.85;opacity:0;animation:fh-b27-tp-in .5s ease forwards;animation-delay:calc(var(--i)*.35s + .6s)}
@keyframes fh-b27-tp-in{to{opacity:1}}
.fh-b27 .fh-b27-tp-cardtxt p,.fh-b27 .fh-b27-tp-cardtxt b{color:var(--cream-ink)}
.fh-b27 .fh-b27-tp-cardtxt a{color:#8E2A3A;font-weight:700}
.fh-b27-tp-cardtxt .pos{display:inline-block;border-radius:999px;background:#2E6E50;color:#fff;font-size:12px;font-weight:800;padding:1px 10px;margin-right:6px}
.fh-b27-tp-cardtxt .nm{font-family:'Shippori Mincho',serif;font-size:18px;font-weight:800}
.fh-b27-tp-cardtxt p{margin:6px 0}
.fh-b27-tp-suits{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.fh-b27-tp-suits div{border:1px solid rgba(232,199,122,.22);border-radius:14px;background:var(--deep);padding:10px 14px;font-size:14px;line-height:1.8}
.fh-b27-tp-suits b{font:800 18px 'Shippori Mincho',serif;color:#F2D99A}.fh-b27-tp-suits b span{color:#FF8A98}
.fh-b27-tp-ranks{width:100%;border-collapse:collapse;font-size:14px}
.fh-b27-tp-ranks th,.fh-b27-tp-ranks td{border-bottom:1px dashed var(--line);padding:6px 8px;text-align:left}
.fh-b27-tp-ranks th{color:#F2D99A;width:4em;font-family:'Shippori Mincho',serif;font-size:17px}
.fh-b27-tp-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.fh-b27-tp-list details{border:1px solid rgba(232,199,122,.2);border-radius:12px;background:var(--deep);padding:6px 12px;font-size:14px;line-height:1.85}
.fh-b27-tp-list summary{cursor:pointer;font-weight:800;color:#F7E6BE}
.fh-b27-tp-list summary .r{color:#FF8A98}
.fh-b27-tp-list summary small{font-weight:400;color:var(--mute);margin-left:6px}
.fh-b27-tp-list p{margin:4px 0}
.fh-b27-tp-qa details{border-bottom:1px dashed var(--line);padding:8px 2px}
.fh-b27-tp-qa summary{cursor:pointer;font-weight:700}
.fh-b27-tp-qa p{margin-top:6px;font-size:14.5px}
@media (max-width:640px){.fh-b27-tp-suits,.fh-b27-tp-list{grid-template-columns:1fr}.fh-b27[data-fh-page="trump"] .fh-b27-toc ol{columns:1}.fh-b27[data-fh-page="trump"] .fh-b27-title{font-size:25px}.fh-b27-tp-emb{width:120px;height:110px}.fh-b27-tp-emb .fh-b27-tp-card{left:30px}}
@media (prefers-reduced-motion:reduce){.fh-b27-tp-flip,.fh-b27-tp-cardtxt{animation:none;opacity:1}.fh-b27-tp-flip{transform:rotateY(180deg)}}
</style>"""

JS = r"""(function(){var C=__C__,SU=__SU__,SPS=__S__,THS=__T__,JK=__J__,ORD=['heart','diamond','club','spade'],RN={1:'A',11:'J',12:'Q',13:'K'};function $(i){return document.getElementById(i)}
if(!$('tp-go'))return;var spK='one',thK='all',mdK='screen';
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function rk(n){return RN[n]||String(n)}
function face(su,n){if(su==='joker')return '<div class="fh-b27-tp-card jk">JOKER</div>';var s=SU[su],r=rk(n);return '<div class="fh-b27-tp-card'+(s.red?' red':'')+'"><i>'+r+'<br>'+s.mark+'</i>'+s.mark+'<i>'+r+'<br>'+s.mark+'</i></div>'}
function own(){var pos=SPS[spK].pos,h='';for(var k=0;k<pos.length;k++){h+='<label>'+esc(pos[k])+'<select id="tp-s'+k+'">'+ORD.map(function(su){return '<option value="'+su+'">'+SU[su].mark+' '+SU[su].name+'</option>'}).join('')+'<option value="joker">ジョーカー</option></select><select id="tp-n'+k+'">';for(var n=1;n<=13;n++)h+='<option value="'+n+'">'+rk(n)+'</option>';h+='</select></label>'}$('tp-own').innerHTML=h}
function bind(id,set){document.querySelectorAll('#'+id+' button').forEach(function(b){b.addEventListener('click',function(){document.querySelectorAll('#'+id+' button').forEach(function(z){z.setAttribute('aria-pressed','false')});b.setAttribute('aria-pressed','true');set(b.getAttribute('data-v'));})})}
bind('tp-sp',function(v){spK=v;own()});bind('tp-th',function(v){thK=v});bind('tp-md',function(v){mdK=v;$('tp-own').hidden=(v!=='own');$('tp-go').textContent=v==='own'?'カードの意味を見る':'カードを引く'});own();
function rnd(n){if(window.crypto&&crypto.getRandomValues){var a=new Uint32Array(1);crypto.getRandomValues(a);return a[0]%n}return Math.floor(Math.random()*n)}
$('tp-go').addEventListener('click',function(){var pos=SPS[spK].pos,picks=[];
 if(mdK==='own'){for(var k=0;k<pos.length;k++){picks.push({su:$('tp-s'+k).value,n:+$('tp-n'+k).value})}}
 else{var deck=[];ORD.forEach(function(su){for(var n=1;n<=13;n++)deck.push({su:su,n:n})});deck.push({su:'joker',n:0});for(var k=0;k<pos.length;k++){picks.push(deck.splice(rnd(deck.length),1)[0])}}
 var cnt={};picks.forEach(function(p){cnt[p.su]=(cnt[p.su]||0)+1});
 var lay='<div class="fh-b27-tp-lay">'+picks.map(function(p,k){return '<div class="fh-b27-tp-pick"><div class="fh-b27-tp-flip" style="--i:'+k+'"><div class="fh-b27-tp-card back"></div><div>'+face(p.su,p.n)+'</div></div>'+esc(pos[k])+'</div>'}).join('')+'</div>';
 var sum='';if(picks.length>1){var top=ORD.filter(function(su){return (cnt[su]||0)>=2});sum='<div class="fh-b27-tp-sum"><b>全体の流れ：</b>'+(top.length?esc(SU[top[0]].name)+'が'+cnt[top[0]]+'枚。今回のテーマは「'+esc(SU[top[0]].theme)+'」が中心です。':'マークがばらばらに出ました。いくつかのことが同時に動いているときです。一つずつ順番に向き合いましょう。')+'</div>'}
 var cards=picks.map(function(p,k){var nm,x;if(p.su==='joker'){nm='ジョーカー';x=[JK[1],JK[2],JK[3],JK[4]]}else{nm=SU[p.su].mark+' '+SU[p.su].name+'の'+rk(p.n);x=C[p.su][p.n]}
  var ext=thK==='love'?x[1]:thK==='work'?x[2]:'';var id=p.su==='joker'?'tp-joker':'tp-'+p.su+'-'+p.n;
  return '<div class="fh-b27-tp-cardtxt" style="--i:'+k+'"><p><span class="pos">'+esc(pos[k])+'</span><span class="nm">'+esc(nm)+'</span></p><p>'+esc(x[0])+'</p>'+(ext?'<p><b>'+esc(THS[thK])+'では：</b>'+esc(ext)+'</p>':'')+'<p><b>ひとこと：</b>'+esc(x[3])+'</p><p><a href="#'+id+'">このカードの意味をくわしく →</a></p></div>'}).join('');
 var r=$('tp-res');r.hidden=false;r.innerHTML=lay+sum+cards;var best='',bc=0;ORD.forEach(function(su){if((cnt[su]||0)>bc){bc=cnt[su];best=su}});if(!best)best='club';ORD.forEach(function(su){var e=$('tp-ad-'+su);if(e)e.hidden=(su!==best)});$('tp-ads').hidden=false;if(mdK==='screen')$('tp-go').textContent='もう一度引く';});
})();"""


def face(su, n):
    s = T.SUITS[su]
    r = rk(n)
    return f'<div class="fh-b27-tp-card{" red" if s["red"] else ""}"><i>{r}<br>{s["mark"]}</i>{s["mark"]}<i>{r}<br>{s["mark"]}</i></div>'


def build(sample, updated):
    H = []
    a = H.append
    a(CSS)
    a('<div class="fh-b27" data-fh-page="trump">\n<div class="fh-b27-note">')
    emb = face("spade", 1) + face("heart", 13) + face("diamond", 7) + face("club", 9)
    a(f'''<header class="fh-b27-hero">
  <div class="fh-b27-tp-emb" aria-hidden="true">{emb}</div>
  <div class="fh-b27-hero-body">
    <span class="fh-b27-tape">人生予報 トランプ占い</span>
    <h1 class="fh-b27-title">トランプ占い<br>52枚の意味と1〜3枚引き</h1>
    <p class="fh-b27-lead">画面でカードを引くことも、手もとのトランプで引いたカードを選ぶこともできる無料のトランプ占いです。1枚引き・2枚引き・3枚引きから選べて、恋愛や仕事のテーマに合わせた読み方も出ます。ハート・ダイヤ・クラブ・スペードの52枚とジョーカーの意味も、このページで一覧できます。</p>
  </div>
</header>''')
    items = [("b27-tp-draw", "トランプで占う"), ("b27-tp-about", "トランプ占いとは"), ("b27-tp-suits", "4つのマークの意味"),
             ("b27-tp-ranks", "数字の意味"), ("b27-tp-list", "52枚の意味一覧"), ("b27-tp-faq", "よくある質問")]
    a('<nav class="fh-b27-toc" aria-label="目次"><strong>このページの内容</strong><ol>' + "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in items) + "</ol></nav>")
    n = [0]

    def h2(t):
        n[0] += 1
        return f'<h2><span class="fh-b27-n">{n[0]}</span><span>{t}</span></h2>'

    spb = "".join(f'<button type="button" data-v="{k}" aria-pressed="{"true" if k == "one" else "false"}">{esc(v["name"])}</button>' for k, v in T.SPREADS.items())
    thb = "".join(f'<button type="button" data-v="{k}" aria-pressed="{"true" if k == "all" else "false"}">{esc(v)}</button>' for k, v in T.THEMES.items())
    ads = AX.result_boxes("tp-ad", TP_GOODS, lead="いちばん多く出たマークに合わせて選びました。楽天・Yahoo!ショッピングの商品ページへ移ります。")
    a(f'''<section class="fh-b27-sec" id="b27-tp-draw">
  {h2("トランプで占う")}
  <div class="fh-b27-tp-box">
    <div class="fh-b27-tp-opts" id="tp-md"><small>カードの出し方</small><button type="button" data-v="screen" aria-pressed="true">画面で引く</button><button type="button" data-v="own" aria-pressed="false">手もとのカードを選ぶ</button></div>
    <div class="fh-b27-tp-opts" id="tp-sp"><small>枚数</small>{spb}</div>
    <div class="fh-b27-tp-opts" id="tp-th"><small>知りたいこと</small>{thb}</div>
    <div class="fh-b27-tp-own" id="tp-own" hidden></div>
    <button type="button" class="fh-b27-tp-go" id="tp-go">カードを引く</button>
    <div class="fh-b27-tp-res" id="tp-res" aria-live="polite" hidden></div>
    <div id="tp-ads" style="width:100%" hidden>{ads}</div>
  </div>
</section>''')
    sps = "".join(f'<li><b>{esc(v["name"])}</b>：{esc(v["desc"])}（{"・".join(v["pos"])}）</li>' for v in T.SPREADS.values())
    a(f'''<section class="fh-b27-sec" id="b27-tp-about">
  {h2("トランプ占いとは")}
  <p>トランプ占いは、どこの家にもあるトランプを使って、引いたカードのマークと数字から答えを読む占いです。4つのマークが「何についての答えか」を、AからKまでの数字が「その物事が今どの段階にあるか」を表します。タロットのような特別な道具がなくても、すぐに始められます。</p>
  <p>手もとで占うときは、トランプをよく混ぜ、聞きたいことを一つ思い浮かべてから、上から決めた枚数を引きます。このページでは、次の3つの引き方が選べます。</p>
  <ul>{sps}</ul>
  <p>2枚以上引いたときは、同じマークが何枚出たかも見てください。同じマークが重なると、その分野が今いちばん動いているサインです。</p>
</section>''')
    su = "".join(f'<div><b><span>{esc(v["mark"])}</span> {esc(v["name"])}</b>　{esc(v["theme"])}<br>{esc(v["text"])}</div>' if v["red"] else
                 f'<div><b>{esc(v["mark"])} {esc(v["name"])}</b>　{esc(v["theme"])}<br>{esc(v["text"])}</div>' for v in T.SUITS.values())
    a(f'''<section class="fh-b27-sec" id="b27-tp-suits">
  {h2("4つのマークの意味")}
  <p>トランプの4つのマークは、春夏秋冬の4つの季節になぞらえられることもあります。マークを見るだけで、答えのおおまかな方向がわかります。</p>
  <div class="fh-b27-tp-suits">{su}</div>
</section>''')
    rows = "".join(f'<tr><th scope="row">{rk(k)}</th><td>{esc(v)}</td></tr>' for k, v in T.RANKS.items())
    a(f'''<section class="fh-b27-sec" id="b27-tp-ranks">
  {h2("数字の意味")}
  <p>数字は、Aの「始まり」から10の「完成」へと進む流れを表します。J・Q・Kの絵札は、出来事よりも「人」を表すことが多いカードです。</p>
  <table class="fh-b27-tp-ranks"><tbody>{rows}</tbody></table>
</section>''')
    lists = ""
    for s in SO:
        v = T.SUITS[s]
        cards = "".join(
            f'<details id="tp-{s}-{k}"><summary><span{" class=r" if v["red"] else ""}>{v["mark"]}</span>{v["name"]}の{rk(k)}<small>{esc(T.RANKS[k].split("（")[0])}</small></summary>'
            f'<p>{esc(x[0])}</p><p><b>恋愛：</b>{esc(x[1])}<br><b>仕事：</b>{esc(x[2])}<br><b>ひとこと：</b>{esc(x[3])}</p></details>'
            for k, x in T.CARDS[s].items())
        lists += f'<h3>{v["mark"]} {v["name"]}（{esc(v["theme"])}）</h3><div class="fh-b27-tp-list">{cards}</div>'
    j = T.JOKER
    lists += (f'<h3>ジョーカー</h3><div class="fh-b27-tp-list"><details id="tp-joker"><summary>ジョーカー<small>特別なカード</small></summary>'
              f'<p>{esc(j[1])}</p><p><b>恋愛：</b>{esc(j[2])}<br><b>仕事：</b>{esc(j[3])}<br><b>ひとこと：</b>{esc(j[4])}</p></details></div>')
    a(f'''<section class="fh-b27-sec" id="b27-tp-list">
  {h2("52枚の意味一覧")}
  <p>カードの名前を押すと、意味と、恋愛・仕事での読み方が開きます。</p>
  {lists}
</section>''')
    qa = "".join(f'<details{" open" if i == 0 else ""}><summary>Q. {esc(q)}</summary><p>A. {esc(x)}</p></details>' for i, (q, x) in enumerate(T.FAQ))
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in T.FAQ]}
    a(f'''<section class="fh-b27-sec" id="b27-tp-faq">
  {h2("よくある質問")}
  <div class="fh-b27-tp-qa">{qa}</div>
</section>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<section class="fh-b27-sec" id="b27-tp-more">
  <div class="fh-b27-links">
    <a href="/tarot/"><b>タロット占い →</b><small>78枚のカードで相談に答える</small></a>
    <a href="/rune/"><b>ルーン占い →</b><small>25のルーンで短い答えを</small></a>
    <a href="/dice/"><b>サイコロ占い →</b><small>1〜4個のサイコロで今日の運勢</small></a>
    <a href="/omikuji/"><b>おみくじ →</b><small>今日の運勢を一枚で</small></a>
  </div>
</section>''')
    js = (JS.replace("__C__", json.dumps({s: {str(k): v for k, v in T.CARDS[s].items()} for s in SO}, ensure_ascii=False))
          .replace("__SU__", json.dumps(T.SUITS, ensure_ascii=False)).replace("__S__", json.dumps(T.SPREADS, ensure_ascii=False))
          .replace("__T__", json.dumps(T.THEMES, ensure_ascii=False)).replace("__J__", json.dumps(T.JOKER, ensure_ascii=False)))
    bad = re.findall(r"\[(sp|pc|tab|mobile)\]", js)
    assert not bad, bad
    up = dt.date.fromisoformat(updated)
    a(f'<p class="fh-b27-foot">トランプ占いは、気持ちを整理するための読み物として楽しむもので、未来を決めるものではありません。カードの意味は、トランプ占いで広く使われているマークと数字の読み方をもとに、このサイトで書いたものです。'
      f'最終更新日：{up.year}年{up.month}月{up.day}日／<a href="/about/">この記事の作成方針について</a></p>')
    a("</div>\n</div>")
    a(f"<script>document.addEventListener('DOMContentLoaded',function(){{{js}}});</script>")
    title = "トランプ占い【無料】52枚の意味一覧｜1枚引き・2枚引き・3枚引きで恋愛・仕事を占う"
    desc = ("画面で引くことも、手もとのトランプで引いたカードを選ぶこともできる無料のトランプ占い。1枚引き・2枚引き・3枚引きで、恋愛・仕事の読み方も出ます。"
            "ハート・ダイヤ・クラブ・スペードの52枚とジョーカーの意味、マークと数字の読み方も紹介します。")
    out = shell(title, desc, URL, "\n".join(H), sample)
    assert "！" not in out and "動物占い" not in out
    return out


def main():
    updated = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    for sample, path in ((False, os.path.join(OUT, "trump.html")), (True, os.path.join(OUT, "sample", "trump.html"))):
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(build(sample, updated))
        print("→", os.path.relpath(path, WORK))


if __name__ == "__main__":
    main()
