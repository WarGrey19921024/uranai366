"""ルーン占いのページ（/rune/ を WordPress の固定ページに作り直す）（2026-10-18。検索「ルーン占い」月1,000〜1万）。
作る前の確認：/rune/ は静的ページ（5つのクロスだけ・文章約1,800字）。同じURLのまま WordPress に移す（静的のフォルダはローカルで退避）。
文章：work/scripts/rune_texts.py（このサイトの言葉）。決め方：work/knowledge/15_ルーン占いページの規則.md
使い方: python work/scripts/build_rune.py [最終更新日]
出力: work/out/rune.html（投入用）、work/out/sample/rune.html（確認用）
"""
import datetime as dt, html, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_hub import OUT, WORK, shell  # noqa: E402
import rune_texts as R  # noqa: E402
import aff_extra as AX  # noqa: E402
RN_FAM = {'Fehu': 'yutaka', 'Jera': 'yutaka', 'Othala': 'yutaka', 'Ingwaz': 'yutaka', 'Gebo': 'tsunagari', 'Wunjo': 'tsunagari', 'Berkana': 'tsunagari', 'Laguz': 'tsunagari', 'Ehwaz': 'tsunagari', 'Mannaz': 'tsunagari', 'Thurisaz': 'mamori', 'Algiz': 'mamori', 'Eihwaz': 'mamori', 'Hagalaz': 'mamori', 'Nauthiz': 'mamori', 'Isa': 'mamori', 'Uruz': 'zenshin', 'Raidho': 'zenshin', 'Tiwaz': 'zenshin', 'Sowilo': 'zenshin', 'Dagaz': 'zenshin', 'Ansuz': 'chie', 'Kenaz': 'chie', 'Perthro': 'chie', 'Wyrd': 'chie'}
RN_GOODS = {'yutaka': ('豊かさのルーンが出たあなたに', [('上質な財布', '上質な財布', '実りを表すルーンの日に、受け取ったものを大切にしまう財布を。', 'wallet'), ('小さな鈴のお守り', '鈴のお守り', 'よい流れを呼びこむ、澄んだ音のお守りに。', 'omamori')]), 'tsunagari': ('つながりのルーンが出たあなたに', [('ペアのキーホルダー', 'ペアのキーホルダー', '人との絆を表すルーンの日に、おそろいの小物を。', 'accessory'), ('ふたり分のマグカップ', 'ふたり分のマグカップ', '大切な人とゆっくり話す時間に。', 'tableware')]), 'mamori': ('守りのルーンが出たあなたに', [('勾玉のお守り', '勾玉のお守り', '立ち止まって身を守るルーンの日に、厄よけの縁起物を。', 'omamori'), ('水晶 天然石', '浄化用の水晶さざれ', '部屋に置いて、気持ちを整えるお守りに。', 'stone')]), 'zenshin': ('前へ進むルーンが出たあなたに', [('小さな旅行バッグ', '小さな旅行バッグ', '動き出すルーンの日に、身軽に出かけられるバッグを。', 'travel'), ('手帳 2027', '2027年の手帳', '次の目標と計画を書き出して。', 'stationery')]), 'chie': ('知恵のルーンが出たあなたに', [('しおり付きの文庫本', 'しおり付きの文庫本', 'ひらめきや知らせを表すルーンの日に、ゆっくり読む一冊を。', 'book'), ('アイデアノート', 'アイデアノート', '思いついたことを、その日のうちに書きとめて。', 'stationery')])}
# 注意：WordPress（Diver）は [sp] [pc] などをショートコードとして消すので、JSで SP[sp] のような書き方をしない（2026-10-18）

URL = "/rune/"


def esc(s):
    return html.escape(str(s), quote=True)


CSS = """<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Runic&display=swap" rel="stylesheet">
<style id="fh-b27-rn-css">
.fh-b27[data-fh-page="rune"]{--ink:#ECF3F1;--sub:#CBDAD6;--mute:#9FB3AE;--paper:#17201F;--deep:#111817;--line:#35504B;--gold:#8FD3C1;--cream:#F4F1E8;--cream-ink:#22302D}
.fh-b27[data-fh-page="rune"] a{color:#A9E6D6}
.fh-b27[data-fh-page="rune"] .fh-b27-sec>p,.fh-b27[data-fh-page="rune"] .fh-b27-lead{text-shadow:0 1px 2px rgba(0,0,0,.6)}
.fh-b27[data-fh-page="rune"] .fh-b27-note{border-left:0;border-radius:24px;background-color:var(--paper);
 background-image:radial-gradient(circle at 15% 0%,rgba(143,211,193,.16),transparent 40%),radial-gradient(circle at 100% 70%,rgba(110,140,190,.16),transparent 45%);box-shadow:0 18px 40px rgba(0,0,0,.3);background-size:auto;background-repeat:no-repeat}
.fh-b27-rn-g{font-family:'Noto Sans Runic','Segoe UI Historic','Segoe UI Symbol',serif}
.fh-b27[data-fh-page="rune"] .fh-b27-hero{align-items:center}
.fh-b27-rn-emb{display:flex;gap:8px;flex:0 0 auto}
.fh-b27-rn-stone{width:58px;height:70px;border-radius:46% 54% 48% 52%/52% 46% 54% 48%;display:flex;align-items:center;justify-content:center;
 background:radial-gradient(circle at 35% 30%,#6E7C78,#3E4A47 60%,#2C3533);box-shadow:inset 0 -4px 8px rgba(0,0,0,.4),0 6px 14px rgba(0,0,0,.35);color:#BFF3E4;font-size:30px;text-shadow:0 0 10px rgba(143,211,193,.8)}
.fh-b27-rn-emb .fh-b27-rn-stone{animation:fh-b27-rn-glow 3.5s ease-in-out infinite;animation-delay:calc(var(--i)*.6s)}
@keyframes fh-b27-rn-glow{50%{text-shadow:0 0 18px rgba(143,211,193,1);transform:translateY(-4px)}}
.fh-b27[data-fh-page="rune"] .fh-b27-tape{transform:none;border-radius:999px;background:linear-gradient(90deg,#8FD3C1,#6E8CBE);color:#111817}
.fh-b27[data-fh-page="rune"] .fh-b27-title{font-family:'Shippori Mincho',serif;font-weight:800;font-size:30px}
.fh-b27[data-fh-page="rune"] h2{font-family:'Shippori Mincho',serif;font-weight:800;font-size:24px}
.fh-b27[data-fh-page="rune"] h2 .fh-b27-n{border:0;border-radius:50%;background:linear-gradient(135deg,#8FD3C1,#6E8CBE);color:#111817}
.fh-b27[data-fh-page="rune"] .fh-b27-toc{border-style:solid;border-radius:18px;border-color:rgba(143,211,193,.3)}
.fh-b27[data-fh-page="rune"] .fh-b27-toc ol{columns:2;column-gap:28px}
.fh-b27-rn-box{border:1.5px solid rgba(143,211,193,.35);border-radius:20px;background:var(--deep);padding:16px;display:flex;flex-direction:column;gap:12px;align-items:center}
.fh-b27-rn-opts{display:flex;flex-wrap:wrap;gap:8px;justify-content:center}
.fh-b27-rn-opts small{width:100%;text-align:center;color:var(--sub);font-size:12.5px}
.fh-b27-rn-opts button{min-height:42px;border-radius:999px;border:1.5px solid rgba(143,211,193,.45);background:transparent;color:var(--sub);font:inherit;font-weight:700;padding:0 16px;cursor:pointer}
.fh-b27-rn-opts button[aria-pressed="true"]{background:#8FD3C1;border-color:#8FD3C1;color:#111817}
.fh-b27-rn-go{min-height:50px;border:0;border-radius:999px;background:linear-gradient(90deg,#8FD3C1,#6E8CBE);color:#111817;font:inherit;font-weight:800;padding:0 26px;cursor:pointer}
.fh-b27-rn-bag{font-size:13px;color:var(--mute);text-align:center}
.fh-b27-rn-res{width:100%;display:flex;flex-direction:column;gap:12px}
.fh-b27-rn-lay{display:grid;gap:10px;justify-content:center}
.fh-b27-rn-lay.one{grid-template-columns:auto}.fh-b27-rn-lay.three{grid-template-columns:repeat(3,auto)}
.fh-b27-rn-lay.cross{grid-template-columns:repeat(3,auto);grid-template-areas:". a ." "b c d" ". e ."}
.fh-b27-rn-lay.cross>div:nth-child(1){grid-area:c}.fh-b27-rn-lay.cross>div:nth-child(2){grid-area:b}.fh-b27-rn-lay.cross>div:nth-child(3){grid-area:d}.fh-b27-rn-lay.cross>div:nth-child(4){grid-area:a}.fh-b27-rn-lay.cross>div:nth-child(5){grid-area:e}
.fh-b27-rn-pick{display:flex;flex-direction:column;align-items:center;gap:4px;font-size:12px;color:var(--sub)}
.fh-b27-rn-pick .fh-b27-rn-stone{opacity:0;animation:fh-b27-rn-drop .6s ease forwards;animation-delay:calc(var(--i)*.35s)}
.fh-b27-rn-pick .fh-b27-rn-stone span{display:inline-block}.fh-b27-rn-pick .rev span{transform:rotate(180deg)}
@keyframes fh-b27-rn-drop{from{opacity:0;transform:translateY(-30px) rotate(-20deg)}to{opacity:1;transform:none}}
.fh-b27-rn-card{background:var(--cream);color:var(--cream-ink);border-radius:16px;padding:14px 16px;line-height:1.85;opacity:0;animation:fh-b27-rn-in .5s ease forwards;animation-delay:calc(var(--i)*.35s + .5s)}
@keyframes fh-b27-rn-in{to{opacity:1}}
.fh-b27 .fh-b27-rn-card p,.fh-b27 .fh-b27-rn-card b{color:var(--cream-ink)}
.fh-b27 .fh-b27-rn-card a{color:#1F6B5C;font-weight:700}
.fh-b27-rn-card .pos{display:inline-block;border-radius:999px;background:#2F6F62;color:#fff;font-size:12px;font-weight:800;padding:1px 10px;margin-right:6px}
.fh-b27-rn-card .nm{font-family:'Shippori Mincho',serif;font-size:18px;font-weight:800;color:#1F4F46}
.fh-b27-rn-card p{margin:6px 0}
.fh-b27-rn-aett h3{margin-top:18px}
.fh-b27-rn-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.fh-b27-rn-list details{border:1px solid rgba(143,211,193,.22);border-radius:14px;background:var(--deep);padding:8px 14px;font-size:14.5px;line-height:1.85}
.fh-b27-rn-list summary{cursor:pointer;list-style:none;display:flex;gap:12px;align-items:center;font-weight:800;color:#CFF5EA}
.fh-b27-rn-list summary::-webkit-details-marker{display:none}
.fh-b27-rn-list summary .fh-b27-rn-g{font-size:28px;min-width:1.3em;text-align:center;color:#BFF3E4;text-shadow:0 0 8px rgba(143,211,193,.7)}
.fh-b27-rn-list summary small{display:block;font-weight:400;color:var(--mute);font-size:12.5px}
.fh-b27-rn-list p{margin:6px 0}
.fh-b27-rn-steps{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
.fh-b27-rn-steps div{border:1px solid rgba(143,211,193,.22);border-radius:14px;background:var(--deep);padding:10px 12px;font-size:14px;line-height:1.8}
.fh-b27-rn-steps b{color:#CFF5EA}
.fh-b27-rn-fixed{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}
.fh-b27-rn-fixed span{border:1px solid rgba(143,211,193,.35);border-radius:10px;padding:4px 10px;font-size:13px}
.fh-b27-rn-fixed .fh-b27-rn-g{font-size:18px;margin-right:4px;color:#BFF3E4}
.fh-b27-rn-qa details{border-bottom:1px dashed var(--line);padding:8px 2px}
.fh-b27-rn-qa summary{cursor:pointer;font-weight:700}
.fh-b27-rn-qa p{margin-top:6px;font-size:14.5px}
@media (max-width:640px){.fh-b27-rn-list,.fh-b27-rn-steps{grid-template-columns:1fr}.fh-b27[data-fh-page="rune"] .fh-b27-toc ol{columns:1}.fh-b27[data-fh-page="rune"] .fh-b27-title{font-size:25px}
 .fh-b27-rn-emb .fh-b27-rn-stone{width:44px;height:54px;font-size:22px}.fh-b27-rn-pick .fh-b27-rn-stone{width:52px;height:62px;font-size:26px}}
@media (prefers-reduced-motion:reduce){.fh-b27-rn-emb .fh-b27-rn-stone,.fh-b27-rn-pick .fh-b27-rn-stone,.fh-b27-rn-card{animation:none;opacity:1}}
</style>"""

JS = r"""(function(){var RN=__R__,SP=__S__,TH=__T__,FM=__F__;function $(i){return document.getElementById(i)}
if(!$('rn-go'))return;var spK='three',thK='all';
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function bind(id,set){document.querySelectorAll('#'+id+' button').forEach(function(b){b.addEventListener('click',function(){document.querySelectorAll('#'+id+' button').forEach(function(z){z.setAttribute('aria-pressed','false')});b.setAttribute('aria-pressed','true');set(b.getAttribute('data-v'));})})}
bind('rn-sp',function(v){spK=v});bind('rn-th',function(v){thK=v});
function rnd(n){if(window.crypto&&crypto.getRandomValues){var a=new Uint32Array(1);crypto.getRandomValues(a);return a[0]%n}return Math.floor(Math.random()*n)}
$('rn-go').addEventListener('click',function(){var pos=SP[spK].pos,bag=RN.map(function(_,i){return i}),picks=[];
 for(var k=0;k<pos.length;k++){var j=rnd(bag.length),idx=bag.splice(j,1)[0],r=RN[idx];picks.push({r:r,i:idx,rev:!!(r.rev&&rnd(3)===0)})}
 var lay='<div class="fh-b27-rn-lay '+spK+'">'+picks.map(function(p,k){return '<div class="fh-b27-rn-pick"><div class="fh-b27-rn-stone fh-b27-rn-g'+(p.rev?' rev':'')+'" style="--i:'+k+'"><span>'+p.r.ch+'</span></div>'+esc(pos[k])+'</div>'}).join('')+'</div>';
 var cards=picks.map(function(p,k){var r=p.r,ext=thK==='love'?r.love:thK==='work'?r.work:'';
  return '<div class="fh-b27-rn-card" style="--i:'+k+'"><p><span class="pos">'+esc(pos[k])+'</span><span class="nm">'+esc(r.name)+'</span>　'+(p.rev?'逆位置':'正位置')+'<br><small>'+esc(r.en)+'｜もとの意味：'+esc(r.orig)+'｜'+esc(r.kw)+'</small></p>'
  +'<p>'+esc(p.rev?r.rev:r.up)+'</p>'+(ext?'<p><b>'+esc(TH[thK])+'では：</b>'+esc(ext)+'</p>':'')+'<p><b>ひとこと：</b>'+esc(r.advice)+'</p><p><a href="#rn-'+p.i+'">'+esc(r.name)+'の意味をくわしく →</a></p></div>'}).join('');
 var r=$('rn-res');r.hidden=false;r.innerHTML=lay+cards;var mi=pos.indexOf('現在');if(mi<0)mi=0;var fam=FM[picks[mi].r.en]||'chie';['yutaka','tsunagari','mamori','zenshin','chie'].forEach(function(k){var e=$('rn-ad-'+k);if(e)e.hidden=(k!==fam)});$('rn-ads').hidden=false;$('rn-go').textContent='もう一度引く';});
})();"""


def build(sample, updated):
    H = []
    a = H.append
    a(CSS)
    a('<div class="fh-b27" data-fh-page="rune">\n<div class="fh-b27-note">')
    emb = "".join(f'<span class="fh-b27-rn-stone fh-b27-rn-g" style="--i:{i}">{R.RUNES[k]["ch"]}</span>' for i, k in enumerate((0, 15, 23)))
    a(f'''<header class="fh-b27-hero">
  <div class="fh-b27-rn-emb" aria-hidden="true">{emb}</div>
  <div class="fh-b27-hero-body">
    <span class="fh-b27-tape">人生予報 ルーン占い</span>
    <h1 class="fh-b27-title">ルーン占い<br>25のルーンの意味と引き方</h1>
    <p class="fh-b27-lead">古い北欧のルーン文字を刻んだ石を引いて、今のあなたへの答えを読む無料の占いです。1つ引き・3つ引き・5つのクロスから選べて、恋愛や仕事のテーマに合わせた読み方も出ます。25のルーンの意味（正位置・逆位置）の一覧もこのページで読めます。</p>
  </div>
</header>''')
    items = [("b27-rn-draw", "ルーンを引く"), ("b27-rn-about", "ルーン占いとは"), ("b27-rn-how", "引き方と並べ方"),
             ("b27-rn-updown", "正位置と逆位置"), ("b27-rn-list", "25のルーンの意味一覧"), ("b27-rn-faq", "よくある質問")]
    a('<nav class="fh-b27-toc" aria-label="目次"><strong>このページの内容</strong><ol>' + "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in items) + "</ol></nav>")
    n = [0]

    def h2(t):
        n[0] += 1
        return f'<h2><span class="fh-b27-n">{n[0]}</span><span>{t}</span></h2>'

    spb = "".join(f'<button type="button" data-v="{k}" aria-pressed="{"true" if k == "three" else "false"}">{esc(v["name"])}</button>' for k, v in R.SPREADS.items())
    thb = "".join(f'<button type="button" data-v="{k}" aria-pressed="{"true" if k == "all" else "false"}">{esc(v)}</button>' for k, v in R.THEMES.items())
    ads = AX.result_boxes("rn-ad", RN_GOODS, lead="「現在」（1つ引きは「答え」）に出たルーンに合わせて選びました。楽天・Yahoo!ショッピングの商品ページへ移ります。")
    a(f'''<section class="fh-b27-sec" id="b27-rn-draw">
  {h2("ルーンを引く")}
  <div class="fh-b27-rn-box">
    <div class="fh-b27-rn-opts" id="rn-sp"><small>引き方</small>{spb}</div>
    <div class="fh-b27-rn-opts" id="rn-th"><small>知りたいこと</small>{thb}</div>
    <p class="fh-b27-rn-bag">心の中で聞きたいことをひとつ思い浮かべてから、ボタンを押してください。</p>
    <button type="button" class="fh-b27-rn-go" id="rn-go">ルーンを引く</button>
    <div class="fh-b27-rn-res" id="rn-res" aria-live="polite" hidden></div>
    <div id="rn-ads" style="width:100%" hidden>{ads}</div>
  </div>
</section>''')
    aett = "".join(f'<div><b>{esc(nm)}</b><br>{esc(ds)}。{"・".join(r["name"] for r in R.RUNES[i * 8:(i + 1) * 8])}</div>' for i, (nm, ds) in enumerate(R.AETT))
    a(f'''<section class="fh-b27-sec" id="b27-rn-about">
  {h2("ルーン占いとは")}
  <p>ルーン文字は、2世紀ごろからゲルマン系の人々が使っていた古い文字です。一つひとつの文字に「家畜」「太陽」「氷」などの意味があり、石や木に刻んでお守りや占いにも使われてきたと伝えられています。</p>
  <p>今のルーン占いでよく使われるのは、最も古い形の24文字「エルダー・フサルク」です。名前は最初の6文字（フ・ウ・ス・ア・ル・ク）の音から来ています。24文字は8文字ずつ3つの組（エット）に分かれ、それぞれ北欧神話の神の名前で呼ばれます。これに、現代になって加えられた何も刻まれていない石「ウィルド（ブランク）」を足した25個で占います。</p>
  <div class="fh-b27-rn-steps">{aett}</div>
</section>''')
    sps = "".join(f'<div><b>{esc(v["name"])}</b><br>{esc(v["desc"])}<br><small>位置：{"・".join(v["pos"])}</small></div>' for v in R.SPREADS.values())
    a(f'''<section class="fh-b27-sec" id="b27-rn-how">
  {h2("引き方と並べ方")}
  <p>ルーンは、袋に入れた石を目を閉じて引くのが基本です。このページでは、ボタンを押すと25個の中から重ならないように選びます。引き方は次の3つから選べます。</p>
  <div class="fh-b27-rn-steps">{sps}</div>
  <p>5つのクロスでは、まん中に「現在」、左に「過去」、右に「未来」、上に「助言」、下に「障害」を置きます。まず「現在」を読み、そこから過去と未来の流れ、最後に障害と助言を合わせて読むと、全体の答えが見えてきます。</p>
  <p>手もとでやりたいときは、小石や厚紙に25の文字を書いて袋に入れれば、自分だけのルーンになります。</p>
</section>''')
    fixed = "".join(f'<span><span class="fh-b27-rn-g">{r["ch"]}</span>{esc(r["name"])}</span>' for r in R.RUNES if r["rev"] is None)
    nfix = sum(1 for r in R.RUNES[:24] if r["rev"] is None)
    a(f'''<section class="fh-b27-sec" id="b27-rn-updown">
  {h2("正位置と逆位置")}
  <p>引いたルーンが正しい向きなら「正位置」、上下が逆なら「逆位置」です。逆位置は悪い意味というより、その力がうまく働いていない、または内側に向いている状態として読みます。</p>
  <p>24文字のうち{nfix}つは、上下を逆にしても形が変わらないため、逆位置がありません。このページでは、次のルーンとブランクは正位置だけで読みます。</p>
  <div class="fh-b27-rn-fixed">{fixed}</div>
</section>''')
    lists = ""
    for i, (nm, ds) in enumerate(R.AETT + [("ブランク", "現代に加えられた石")]):
        rs = list(enumerate(R.RUNES))[i * 8:(i + 1) * 8] if i < 3 else [(24, R.RUNES[24])]
        cards = "".join(
            f'<details id="rn-{k}"><summary><span class="fh-b27-rn-g" aria-hidden="true">{r["ch"]}</span><span>{esc(r["name"])}（{esc(r["en"])}）<small>{esc(r["orig"])}｜{esc(r["kw"])}</small></span></summary>'
            f'<p>{esc(r["text"])}</p><p><b>正位置：</b>{esc(r["up"])}</p>'
            + (f'<p><b>逆位置：</b>{esc(r["rev"])}</p>' if r["rev"] else '<p><b>逆位置：</b>このルーンは逆位置を取りません。</p>')
            + f'<p><b>恋愛：</b>{esc(r["love"])}<br><b>仕事：</b>{esc(r["work"])}<br><b>ひとこと：</b>{esc(r["advice"])}</p></details>'
            for k, r in rs)
        lists += f'<div class="fh-b27-rn-aett"><h3>{esc(nm)}（{esc(ds)}）</h3><div class="fh-b27-rn-list">{cards}</div></div>'
    a(f'''<section class="fh-b27-sec" id="b27-rn-list">
  {h2("25のルーンの意味一覧")}
  <p>ルーンの名前を押すと、意味・正位置・逆位置・恋愛と仕事での読み方が開きます。</p>
  {lists}
</section>''')
    qa = "".join(f'<details{" open" if i == 0 else ""}><summary>Q. {esc(q)}</summary><p>A. {esc(x)}</p></details>' for i, (q, x) in enumerate(R.FAQ))
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in R.FAQ]}
    a(f'''<section class="fh-b27-sec" id="b27-rn-faq">
  {h2("よくある質問")}
  <div class="fh-b27-rn-qa">{qa}</div>
</section>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<section class="fh-b27-sec" id="b27-rn-more">
  <div class="fh-b27-links">
    <a href="/tarot/"><b>タロット占い →</b><small>78枚のカードで相談に答える</small></a>
    <a href="/suhijutsu/"><b>数秘術 →</b><small>生年月日でライフパスを計算</small></a>
    <a href="/omikuji/"><b>おみくじ →</b><small>今日の運勢を一枚で</small></a>
    <a href="/eki/"><b>易占い →</b><small>六十四卦で答えを読む</small></a>
    <a href="/angel-number/"><b>エンジェルナンバー →</b><small>くり返し見る数字の意味</small></a>
  </div>
</section>''')
    js = (JS.replace("__F__", json.dumps(RN_FAM)).replace("__R__", json.dumps(R.RUNES, ensure_ascii=False)).replace("__S__", json.dumps(R.SPREADS, ensure_ascii=False))
          .replace("__T__", json.dumps(R.THEMES, ensure_ascii=False)))
    up = dt.date.fromisoformat(updated)
    a(f'<p class="fh-b27-foot">ルーン占いは、気持ちを整理するための読み物として楽しむもので、未来を決めるものではありません。ルーンの意味は、広く知られている文字の由来と解説をもとに、このサイトで書いたものです。'
      f'最終更新日：{up.year}年{up.month}月{up.day}日／<a href="/about/">この記事の作成方針について</a></p>')
    a("</div>\n</div>")
    a(f"<script>document.addEventListener('DOMContentLoaded',function(){{{js}}});</script>")
    title = "ルーン占い【無料】25のルーンの意味一覧（正位置・逆位置）｜1つ引き・3つ引き・5つのクロス"
    desc = ("ルーン文字を刻んだ石を引いて答えを読む無料のルーン占い。1つ引き・3つ引き・5つのクロスから選べ、恋愛・仕事の読み方も出ます。"
            "エルダー・フサルク24文字とブランクの25のルーンの意味（正位置・逆位置）、引き方も紹介します。")
    out = shell(title, desc, URL, "\n".join(H), sample)
    assert "！" not in out and "動物占い" not in out
    return out


def main():
    updated = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    for sample, path in ((False, os.path.join(OUT, "rune.html")), (True, os.path.join(OUT, "sample", "rune.html"))):
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(build(sample, updated))
        print("→", os.path.relpath(path, WORK))


if __name__ == "__main__":
    main()
