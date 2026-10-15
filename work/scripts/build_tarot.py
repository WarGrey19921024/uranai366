"""タロット占い（新しい固定ページ /tarot/）を作る（2026-10-15 本人の決定：「タロット占い」月10万〜100万回の検索に入る）。
大アルカナ22枚。カードの意味は書き下ろし（data/tarot/major.json）。絵は既存デッキを使わず、このサイトの独自デザイン（CSS）。
使い方: python work/scripts/build_tarot.py [最終更新日]
出力: work/out/tarot.html（投入用）、work/out/sample/tarot.html（確認用）
"""
import datetime as dt, html, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_hub import OUT, WORK, DATA, shell  # noqa: E402

URL = "/tarot/"
ROMAN = ["0", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI"]
SYM = ["✧", "∞", "☾", "♀", "♂", "✠", "♡", "➤", "♌", "✦", "⊕", "⚖", "▽", "☩", "♒", "⛓", "ϟ", "★", "☽", "☀", "♪", "◎"]
SYM = [x + "\ufe0e" for x in SYM]  # 絵文字ではなく文字として表示させる
FAQ = [
    ("タロット占いは無料ですか。", "無料です。登録も不要で、何度でも引き直せます。引いたカードはこのページの中だけで決め、どこにも送信しません。"),
    ("正位置と逆位置はどう違いますか。", "カードがまっすぐ出たときが正位置、上下が逆に出たときが逆位置です。逆位置は「悪い意味」ではなく、カードの力がうまく出ていない状態や、見直したほうがよい点を表すと読むのが一般的です。"),
    ("同じ質問で何回も引いてもいいですか。", "引き直すたびに答えがぶれて迷いやすくなるため、同じ質問は1日1回を目安にするのがおすすめです。時間をおいて状況が変わったら、もう一度引いてみてください。"),
    ("大アルカナと小アルカナの違いは何ですか。", "タロットは全78枚で、人生の大きなテーマを表す大アルカナ22枚と、日常の出来事を表す小アルカナ56枚に分かれます。このページでは大アルカナ22枚で占います。"),
    ("怖いカードが出たらどうすればいいですか。", "死神や塔のように名前が怖いカードも、終わりと再出発、思い込みからの解放といった意味を持っています。悪いことが起こる予言ではなく、今を見直すきっかけとして読んでください。"),
    ("タロットの結果は当たりますか。", "タロットは未来を決めるものではなく、今の気持ちや状況を見つめ直すための道具です。結果は楽しみと気づきとして受け取り、大事な決断はご自身で考えてください。"),
]


def esc(s):
    return html.escape(str(s), quote=True)


CSS = """<style id="fh-b27-tr-css">
.fh-b27[data-fh-page="tarot"]{--ink:#F1ECF8;--sub:#D3CBE3;--mute:#ADA3C4;--paper:#221A36;--deep:#1B142C;--line:#4F4470;--gold:#E9C46A;--lilac:#C9B6FF;--cream:#FBF6EA;--cream-ink:#2B2340}
.fh-b27[data-fh-page="tarot"] a:hover{color:#F6DD9C}
.fh-b27[data-fh-page="tarot"] .fh-b27-note{border-left:0;border-radius:22px;background-color:var(--paper);
  background-image:radial-gradient(circle at 50% -10%,rgba(201,182,255,.20),transparent 45%),radial-gradient(rgba(255,255,255,.08) 1px,transparent 1.5px),radial-gradient(rgba(233,196,106,.10) 1px,transparent 1.5px);
  background-size:auto,30px 30px,47px 47px;background-position:0 0,0 0,13px 21px;box-shadow:0 14px 40px rgba(0,0,0,.5),inset 0 0 0 1px rgba(233,196,106,.18)}
.fh-b27[data-fh-page="tarot"] .fh-b27-hero{align-items:center}
.fh-b27-tr-emb{position:relative;flex:0 0 130px;height:150px}
.fh-b27-tr-emb i{position:absolute;left:35px;top:10px;width:62px;height:100px;border-radius:8px;border:2px solid var(--gold);background:repeating-linear-gradient(45deg,#3A2C5E 0 6px,#2C2148 6px 12px);box-shadow:0 6px 14px rgba(0,0,0,.4);transform-origin:50% 120%}
.fh-b27-tr-emb i:nth-child(1){transform:rotate(-16deg)}.fh-b27-tr-emb i:nth-child(3){transform:rotate(16deg)}
.fh-b27-tr-emb i:nth-child(2){background:var(--cream);display:flex;align-items:center;justify-content:center;font:800 26px 'Shippori Mincho',serif;color:#2B2340;z-index:1}
.fh-b27[data-fh-page="tarot"] .fh-b27-tape{transform:none;border-radius:999px;background:linear-gradient(90deg,var(--gold),var(--lilac));color:#221A36}
.fh-b27[data-fh-page="tarot"] .fh-b27-title{font-family:'Shippori Mincho',serif;font-weight:800;font-size:31px}
.fh-b27[data-fh-page="tarot"] h2{font-family:'Shippori Mincho',serif;font-weight:800;font-size:24px}
.fh-b27[data-fh-page="tarot"] h2 .fh-b27-n{border:1.5px solid var(--gold);background:transparent;color:var(--gold);font-family:'Shippori Mincho',serif;border-radius:4px;transform:rotate(45deg)}
.fh-b27[data-fh-page="tarot"] h2 .fh-b27-n>*{transform:rotate(-45deg)}
.fh-b27[data-fh-page="tarot"] h3{border-bottom:0;background:linear-gradient(90deg,var(--gold),transparent) left bottom/100% 1.5px no-repeat}
.fh-b27[data-fh-page="tarot"] .fh-b27-toc{border-style:solid;border-color:rgba(233,196,106,.25);border-radius:16px}
.fh-b27[data-fh-page="tarot"] .fh-b27-toc ol{columns:2;column-gap:28px;list-style:none;padding-left:0}
.fh-b27-tr-modes{display:flex;flex-wrap:wrap;gap:8px}
.fh-b27-tr-modes button,.fh-b27-tr-draw{min-height:44px;border-radius:999px;font:inherit;font-weight:700;padding:0 18px;cursor:pointer}
.fh-b27-tr-modes button{background:transparent;border:1.5px solid var(--line);color:var(--sub)}
.fh-b27-tr-modes button[aria-pressed="true"]{border-color:var(--gold);color:var(--gold);background:rgba(233,196,106,.08)}
.fh-b27-tr-draw{border:0;background:linear-gradient(90deg,#E9C46A,#F3D98E);color:#221A36}
.fh-b27-tr-q{width:100%;min-height:44px;border-radius:10px;border:1.5px solid var(--line);background:var(--deep);color:var(--ink);font:inherit;padding:0 12px}
.fh-b27-tr-table{display:flex;justify-content:center;gap:14px;flex-wrap:wrap;padding:8px 0}
.fh-b27-tr-slot{display:flex;flex-direction:column;align-items:center;gap:6px;font-size:13px;color:var(--mute)}
.fh-b27-tr-card{width:120px;height:196px;perspective:800px}
.fh-b27-tr-in{position:relative;width:100%;height:100%;transition:transform .8s;transform-style:preserve-3d}
.fh-b27-tr-card.is-open .fh-b27-tr-in{transform:rotateY(180deg)}
.fh-b27-tr-back,.fh-b27-tr-face{position:absolute;inset:0;border-radius:10px;backface-visibility:hidden;-webkit-backface-visibility:hidden}
.fh-b27-tr-back{border:2px solid var(--gold);background:radial-gradient(circle,rgba(233,196,106,.35) 0 14px,transparent 15px),repeating-linear-gradient(45deg,#3A2C5E 0 7px,#2C2148 7px 14px);box-shadow:0 6px 16px rgba(0,0,0,.45)}
.fh-b27-tr-face{transform:rotateY(180deg);background:var(--cream);color:#2B2340;border:2px solid var(--gold);display:flex;flex-direction:column;align-items:center;justify-content:space-between;padding:10px 6px;box-shadow:0 6px 16px rgba(0,0,0,.45)}
.fh-b27-tr-face .r{font:800 15px 'Shippori Mincho',serif;letter-spacing:.1em}
.fh-b27-tr-face .s{font-size:44px;line-height:1;color:#6B4FA0;font-family:'Segoe UI Symbol','Noto Sans Symbols 2','Noto Sans Symbols',serif}
.fh-b27-tr-face .n{font:800 16px 'Shippori Mincho',serif;text-align:center;line-height:1.3}
.fh-b27-tr-face .e{font-size:10px;color:#7A6F8E;letter-spacing:.05em}
.fh-b27-tr-card.is-rev .fh-b27-tr-face>div{transform:rotate(180deg);display:flex;flex-direction:column;align-items:center;justify-content:space-between;height:100%;width:100%}
.fh-b27-tr-card:not(.is-rev) .fh-b27-tr-face>div{display:flex;flex-direction:column;align-items:center;justify-content:space-between;height:100%;width:100%}
.fh-b27-tr-res{display:flex;flex-direction:column;gap:12px}
.fh-b27-tr-rc{background:var(--cream);color:var(--cream-ink);border-radius:14px;padding:16px 18px;line-height:1.8;font-size:15px}
.fh-b27 .fh-b27-tr-rc p,.fh-b27 .fh-b27-tr-rc b,.fh-b27 .fh-b27-tr-rc strong{color:var(--cream-ink)}
.fh-b27-tr-rc strong{font-family:'Shippori Mincho',serif;font-size:19px}
.fh-b27-tr-rc small{color:#6E6584}
.fh-b27 .fh-b27-tr-rc a{color:#5B3E95;font-weight:700}
.fh-b27-tr-yes{font:800 30px 'Shippori Mincho',serif;color:#5B3E95}
.fh-b27-tr-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:8px}
.fh-b27-tr-grid a{display:flex;flex-direction:column;align-items:center;gap:2px;border:1px solid rgba(233,196,106,.3);border-radius:8px;padding:8px 2px;text-decoration:none;background:var(--deep);font-size:12.5px;color:var(--ink);line-height:1.3;text-align:center}
.fh-b27-tr-grid a b{font:800 13px 'Shippori Mincho',serif;color:var(--gold)}
.fh-b27-tr-grid a span{font-size:20px;color:var(--lilac)}
.fh-b27-tr-list{display:flex;flex-direction:column;gap:10px}
.fh-b27-tr-list details{border:1px solid rgba(233,196,106,.25);border-radius:14px;background:var(--deep);padding:8px 14px}
.fh-b27-tr-list summary{cursor:pointer;font-family:'Shippori Mincho',serif;font-weight:800;font-size:17px;color:var(--ink)}
.fh-b27-tr-list summary small{font-family:'Zen Kaku Gothic New',sans-serif;font-weight:400;color:var(--mute);font-size:12.5px;margin-left:8px}
.fh-b27-tr-list summary .k{color:var(--gold);margin-right:8px}
.fh-b27-tr-list h3{font-size:16px;margin:10px 0 4px}
.fh-b27-tr-list p{font-size:14.5px;line-height:1.9}
.fh-b27-tr-kw{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0}
.fh-b27-tr-kw span{border:1px solid var(--line);border-radius:999px;padding:0 10px;font-size:12.5px}
.fh-b27-tr-kw span.u{border-color:var(--gold);color:var(--gold)}
.fh-b27-tr-kw span.v{border-color:var(--lilac);color:var(--lilac)}
.fh-b27-tr-two{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.fh-b27-tr-two>div{border:1px dashed var(--line);border-radius:12px;padding:10px 14px}
.fh-b27-tr-steps{counter-reset:s;list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:8px}
.fh-b27 .fh-b27-tr-steps li{counter-increment:s;margin:0;padding:8px 12px 8px 46px;position:relative;border:1px dashed var(--line);border-radius:12px;font-size:14.5px;line-height:1.8}
.fh-b27-tr-steps li::before{content:counter(s);position:absolute;left:12px;top:9px;width:24px;height:24px;border-radius:50%;background:var(--gold);color:#221A36;font-weight:800;font-size:13px;display:flex;align-items:center;justify-content:center}
.fh-b27-tr-qa details{border-bottom:1px dashed var(--line);padding:8px 2px}
.fh-b27-tr-qa summary{cursor:pointer;font-weight:700}
.fh-b27-tr-qa p{margin-top:6px;font-size:14.5px}
@media (max-width:640px){.fh-b27-tr-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.fh-b27-tr-two{grid-template-columns:1fr}.fh-b27[data-fh-page="tarot"] .fh-b27-toc ol{columns:1}.fh-b27-tr-card{width:96px;height:158px}.fh-b27-tr-face .s{font-size:34px}.fh-b27-tr-emb{flex-basis:110px;transform:scale(.85)}.fh-b27[data-fh-page="tarot"] .fh-b27-title{font-size:26px}}
@media (prefers-reduced-motion:reduce){.fh-b27-tr-in{transition:none}}
</style>"""

JS = r"""(function(){var C=__DATA__,S=__SYM__,R=__ROMAN__;var root=document.getElementById('fh-b27-tr');if(!root)return;
var mode='one',modes=root.querySelectorAll('[data-mode]'),table=document.getElementById('fh-b27-tr-table'),res=document.getElementById('fh-b27-tr-res');
var LABEL={one:['今日のメッセージ'],three:['過去','現在','未来'],yes:['答え']};
function rnd(n){var a=new Uint32Array(1);(window.crypto||window.msCrypto).getRandomValues(a);return a[0]%n;}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function face(c){return '<div><span class="r">'+R[c.no]+'</span><span class="s">'+S[c.no]+'</span><span class="n">'+esc(c.name)+'</span><span class="e">'+esc(c.en.toUpperCase())+'</span></div>';}
function slots(){var L=LABEL[mode];table.innerHTML=L.map(function(l){return '<div class="fh-b27-tr-slot"><div class="fh-b27-tr-card"><div class="fh-b27-tr-in"><div class="fh-b27-tr-back"></div><div class="fh-b27-tr-face"></div></div></div><span>'+l+'</span></div>';}).join('');res.innerHTML='';}
modes.forEach(function(b){b.addEventListener('click',function(){mode=b.getAttribute('data-mode');modes.forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false');});slots();});});
function yes(c,rev){var y=c.yesno;if(!rev)return y;return y==='はい'?'どちらとも言えない':'いいえ';}
document.getElementById('fh-b27-tr-go').addEventListener('click',function(){slots();var L=LABEL[mode],pool=C.slice(),picks=[];
 for(var i=0;i<L.length;i++){var k=rnd(pool.length);picks.push({c:pool.splice(k,1)[0],rev:rnd(2)===1});}
 var cards=table.querySelectorAll('.fh-b27-tr-card');
 picks.forEach(function(p,i){var el=cards[i];el.querySelector('.fh-b27-tr-face').innerHTML=face(p.c);if(p.rev)el.classList.add('is-rev');setTimeout(function(){el.classList.add('is-open');},250+i*450);});
 var q=(document.getElementById('fh-b27-tr-q').value||'').trim();
 setTimeout(function(){var h=q?'<p class="fh-b27-small">質問：'+esc(q)+'</p>':'';
  picks.forEach(function(p,i){var c=p.c,pos=p.rev?'逆位置':'正位置',kw=(p.rev?c.kw_rev:c.kw_up).join('・');
   h+='<div class="fh-b27-tr-rc"><small>'+L[i]+'</small><br><strong>'+R[c.no]+' '+esc(c.name)+'（'+pos+'）</strong><br><small>キーワード：'+esc(kw)+'</small>';
   if(mode==='yes')h+='<p class="fh-b27-tr-yes">'+yes(c,p.rev)+'</p>';
   h+='<p>'+esc(p.rev?c.rev:c.up)+'</p>';
   if(mode!=='three')h+='<p><b>恋愛</b>　'+esc(c.love)+'</p><p><b>仕事</b>　'+esc(c.work)+'</p>';
   h+='<p><b>アドバイス</b>　'+esc(c.advice)+'</p><p><a href="#b27-tr-c'+c.no+'">'+esc(c.name)+'の意味をくわしく見る →</a></p></div>';});
  res.innerHTML=h;},350+L.length*450+500);});
slots();})();"""


def build(sample, updated):
    cards = json.load(open(os.path.join(DATA, "tarot", "major.json"), encoding="utf-8"))
    assert len(cards) == 22
    H = []
    a = H.append
    a(CSS)
    a('<div class="fh-b27" data-fh-page="tarot">\n<div class="fh-b27-note">')
    a('''<header class="fh-b27-hero">
  <div class="fh-b27-tr-emb" aria-hidden="true"><i></i><i>★</i><i></i></div>
  <div class="fh-b27-hero-body">
    <span class="fh-b27-tape">人生予報 タロット占い</span>
    <h1 class="fh-b27-title">タロット占い<br>大アルカナ22枚で占う</h1>
    <p class="fh-b27-lead">質問を思い浮かべてカードを引くだけの、無料のタロット占いです。1枚引き・3枚引き（過去・現在・未来）・Yes/Noの3つの占い方から選べます。下には大アルカナ22枚の正位置・逆位置の意味と、恋愛・仕事・お金の読み方をまとめました。</p>
  </div>
</header>''')
    items = [("b27-tr-play", "カードを引いて占う"), ("b27-tr-how", "タロット占いのやり方"), ("b27-tr-pos", "正位置と逆位置"),
             ("b27-tr-all", "大アルカナ22枚の意味一覧"), ("b27-tr-faq", "よくある質問")]
    a('<nav class="fh-b27-toc" aria-label="目次"><strong>このページの内容</strong><ol>' + "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in items) + "</ol></nav>")
    n = [1]

    def h2(t):
        s = f'<h2><span class="fh-b27-n"><span>{n[0]}</span></span><span>{t}</span></h2>'
        n[0] += 1
        return s
    a(f'''<section class="fh-b27-sec" id="b27-tr-play">
  {h2("カードを引いて占う")}
  <div id="fh-b27-tr" class="fh-b27-sec" style="gap:12px">
    <div class="fh-b27-tr-modes" role="group" aria-label="占い方を選ぶ"><button type="button" data-mode="one" aria-pressed="true">1枚引き</button><button type="button" data-mode="three" aria-pressed="false">3枚引き（過去・現在・未来）</button><button type="button" data-mode="yes" aria-pressed="false">Yes/No占い</button></div>
    <input class="fh-b27-tr-q" id="fh-b27-tr-q" type="text" maxlength="60" placeholder="占いたいことを1つ（書かなくても占えます）" aria-label="占いたいこと">
    <div><button type="button" class="fh-b27-tr-draw" id="fh-b27-tr-go">シャッフルして引く</button></div>
    <div class="fh-b27-tr-table" id="fh-b27-tr-table" aria-live="polite"></div>
    <div class="fh-b27-tr-res" id="fh-b27-tr-res" aria-live="polite"></div>
    <p class="fh-b27-small">カードは22枚の中から毎回ランダムに選び、上下（正位置・逆位置）も半分ずつの確率で決めます。入力した質問は送信も保存もしません。</p>
  </div>
  <noscript><p class="fh-b27-small">カードを引くにはJavaScriptを有効にしてください。下の一覧でカードの意味は読めます。</p></noscript>
</section>''')
    data = [{k: c[k] for k in ("no", "name", "en", "kw_up", "kw_rev", "up", "rev", "love", "work", "advice", "yesno")} for c in cards]
    js = JS.replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":"))).replace("__SYM__", json.dumps(SYM)).replace("__ROMAN__", json.dumps(ROMAN))
    a(f"<script>{js}</script>")
    a("<!--Ads1-->")
    a(f'''<section class="fh-b27-sec" id="b27-tr-how">
  {h2("タロット占いのやり方")}
  <ol class="fh-b27-tr-steps">
    <li><b>占いたいことを1つに決める</b>「あの人とうまくいくには」「今の仕事で何を大切にすればいいか」のように、自分が動ける形の質問にすると答えを生かしやすくなります。</li>
    <li><b>占い方を選ぶ</b>今日の過ごし方や短い問いには1枚引き、物事の流れを知りたいときは3枚引き、迷っていることの答えがほしいときはYes/No占いが向いています。</li>
    <li><b>気持ちを落ち着けてカードを引く</b>深呼吸をして質問を思い浮かべながら、「シャッフルして引く」を押してください。</li>
    <li><b>キーワードから読む</b>まずカードのキーワードと全体の意味を読み、次に恋愛・仕事など質問に近い読み方を見ます。自分の状況に当てはめて考えるのがタロットのいちばんの楽しみ方です。</li>
  </ol>
  <div class="fh-b27-tr-two">
    <div><b>1枚引き</b><br>今日のテーマや、ひとつの問いへのメッセージを1枚で受け取ります。毎朝の習慣にも向いています。</div>
    <div><b>3枚引き（過去・現在・未来）</b><br>左から過去・現在・未来として並べ、流れの中で今の状況を読みます。3枚のつながりを考えると答えが見えてきます。</div>
  </div>
</section>''')
    a(f'''<section class="fh-b27-sec" id="b27-tr-pos">
  {h2("正位置と逆位置")}
  <p>引いたカードがまっすぐなら<b>正位置</b>、上下さかさまなら<b>逆位置</b>です。正位置はカードの意味がそのまま素直に表れている状態、逆位置はその力が弱まっていたり、行き過ぎていたり、内側にこもっていたりする状態を表します。</p>
  <p>逆位置は「悪い結果」という意味ではありません。今うまく流れていないところや、少し見直すとよくなるところを教えてくれるサインとして読んでください。このページのYes/No占いでは、逆位置のときは答えを一段階控えめにしています（「はい」→「どちらとも言えない」、それ以外→「いいえ」）。</p>
</section>''')
    grid = "".join(f'<a href="#b27-tr-c{c["no"]}"><b>{ROMAN[c["no"]]}</b><span aria-hidden="true">{SYM[c["no"]]}</span>{esc(c["name"])}</a>' for c in cards)
    det = ""
    for c in cards:
        det += (f'<details id="b27-tr-c{c["no"]}"><summary><span class="k">{ROMAN[c["no"]]}</span>{esc(c["name"])}<small>{esc(c["en"])}｜{esc("・".join(c["kw_up"]))}</small></summary>'
                f'<div class="fh-b27-tr-kw">' + "".join(f'<span class="u">正 {esc(k)}</span>' for k in c["kw_up"]) + "".join(f'<span class="v">逆 {esc(k)}</span>' for k in c["kw_rev"]) + '</div>'
                f'<p>{esc(c["motif"])}</p>'
                f'<h3>正位置の意味</h3><p>{esc(c["up"])}</p><h3>逆位置の意味</h3><p>{esc(c["rev"])}</p>'
                f'<h3>恋愛</h3><p>{esc(c["love"])}</p><h3>仕事</h3><p>{esc(c["work"])}</p><h3>お金</h3><p>{esc(c["money"])}</p>'
                f'<h3>アドバイス</h3><p>{esc(c["advice"])}</p><p class="fh-b27-small">Yes/No占いでの答え（正位置）：{esc(c["yesno"])}</p></details>')
    a(f'''<section class="fh-b27-sec" id="b27-tr-all">
  {h2("大アルカナ22枚の意味一覧")}
  <p>大アルカナは、0番の愚者から21番の世界まで、旅をするように人生の段階を表す22枚のカードです。カード名を押すと、正位置・逆位置の意味と、恋愛・仕事・お金の読み方が開きます。</p>
  <div class="fh-b27-tr-grid">{grid}</div>
  <div class="fh-b27-tr-list">{det}</div>
  <p class="fh-b27-small">カードの意味はこのサイトで書き下ろしたものです。カードの絵は特定のデッキの絵柄ではなく、このサイトのデザインです。番号の並びは、日本で広く使われているウェイト版（8番が力、11番が正義）に合わせています。</p>
</section>''')
    qa = "".join(f'<details{" open" if i == 0 else ""}><summary>Q. {q}</summary><p>A. {x}</p></details>' for i, (q, x) in enumerate(FAQ))
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in FAQ]}
    a(f'''<section class="fh-b27-sec" id="b27-tr-faq">
  {h2("よくある質問")}
  <div class="fh-b27-tr-qa">{qa}</div>
</section>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>''')
    a('''<section class="fh-b27-sec" id="b27-tr-more">
  <div class="fh-b27-links">
    <a href="/366uranai/"><b>366日の誕生日占い →</b><small>誕生日から性格・相性・2027年の運勢</small></a>
    <a href="/compatibility/"><b>誕生日相性占い →</b><small>2人の誕生日で相性を見る</small></a>
    <a href="/rune/"><b>ルーン占い →</b><small>5つのルーンで現状・障害・助言を読む</small></a>
    <a href="/trump/"><b>トランプ占い →</b><small>手元のトランプで1〜3枚引き</small></a>
  </div>
</section>''')
    up = dt.date.fromisoformat(updated)
    a(f'<p class="fh-b27-foot">タロット占いは、自分の気持ちや状況を見つめ直すための読み物です。楽しみと気づきのためにお使いください。<br>'
      f'最終更新日：{up.year}年{up.month}月{up.day}日／<a href="/about/">この記事の作成方針について</a></p>')
    a("</div>\n</div>")
    title = "タロット占い【無料】大アルカナ22枚の意味一覧と1枚引き・3枚引き・Yes/No占い"
    desc = ("無料のタロット占い。1枚引き・3枚引き（過去・現在・未来）・Yes/No占いで、今の悩みにカードが答えます。"
            "大アルカナ22枚の正位置・逆位置の意味と、恋愛・仕事・お金の読み方も一覧で紹介。")
    out = shell(title, desc, URL, "\n".join(H), sample)
    assert "！" not in out.replace("&#x27;", "")
    return out


def main():
    updated = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    for sample, path in ((False, os.path.join(OUT, "tarot.html")), (True, os.path.join(OUT, "sample", "tarot.html"))):
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(build(sample, updated))
        print("→", os.path.relpath(path, WORK))


if __name__ == "__main__":
    main()
