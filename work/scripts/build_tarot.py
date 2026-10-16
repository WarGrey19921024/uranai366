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
    ("大アルカナと小アルカナの違いは何ですか。", "タロットは全78枚で、人生の大きなテーマを表す大アルカナ22枚と、日常の出来事を表す小アルカナ56枚に分かれます。このページでは、大アルカナだけで占うか78枚すべてで占うかを選べます。"),
    ("怖いカードが出たらどうすればいいですか。", "死神や塔のように名前が怖いカードも、終わりと再出発、思い込みからの解放といった意味を持っています。悪いことが起こる予言ではなく、今を見直すきっかけとして読んでください。"),
    ("タロットの結果は当たりますか。", "タロットは未来を決めるものではなく、今の気持ちや状況を見つめ直すための道具です。結果は楽しみと気づきとして受け取り、大事な決断はご自身で考えてください。"),
]


def esc(s):
    return html.escape(str(s), quote=True)


CSS = """<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&display=swap" rel="stylesheet">
<style id="fh-b27-tr-css">
.fh-b27[data-fh-page="tarot"]{--ink:#F3EDE2;--sub:#D9CFBF;--mute:#B3A890;--paper:#160F22;--deep:#120B1C;--line:#5A4628;--gold:#D9B45A;--gold2:#F2D98C;--wine:#5A1F33;--cream:#F4E8CC;--cream-ink:#2A1E14}
.fh-b27[data-fh-page="tarot"] a{color:var(--gold2)}.fh-b27[data-fh-page="tarot"] a:hover{color:#FFF0C2}
.fh-b27[data-fh-page="tarot"] .fh-b27-note{border-left:0;border-radius:18px;background-color:var(--paper);
  background-image:radial-gradient(ellipse at 50% 0%,rgba(120,40,70,.45),transparent 55%),radial-gradient(circle at 6% 12%,rgba(255,170,70,.20),transparent 22%),radial-gradient(circle at 94% 12%,rgba(255,170,70,.16),transparent 22%),radial-gradient(ellipse at 50% 120%,rgba(90,31,51,.55),transparent 60%),radial-gradient(rgba(242,217,140,.10) 1px,transparent 1.6px);
  background-size:auto,auto,auto,auto,34px 34px;box-shadow:0 18px 50px rgba(0,0,0,.6),inset 0 0 0 1px rgba(217,180,90,.55),inset 0 0 0 6px rgba(22,15,34,1),inset 0 0 0 7px rgba(217,180,90,.35),inset 0 0 80px rgba(0,0,0,.55)}
.fh-b27[data-fh-page="tarot"] .fh-b27-hero{align-items:center;text-align:left}
.fh-b27-tr-emb{position:relative;flex:0 0 150px;height:170px}
.fh-b27-tr-emb:before{content:"";position:absolute;left:50%;top:58%;width:150px;height:150px;margin:-75px 0 0 -75px;border-radius:50%;background:radial-gradient(circle,rgba(255,190,90,.35),transparent 65%);animation:fh-b27-tr-flick 3.2s ease-in-out infinite alternate}
@keyframes fh-b27-tr-flick{0%{opacity:.7;transform:scale(.96)}100%{opacity:1;transform:scale(1.04)}}
.fh-b27-tr-emb i{position:absolute;left:44px;top:18px;width:66px;height:108px;border-radius:7px;transform-origin:50% 125%}
.fh-b27-tr-emb i:nth-child(1){transform:rotate(-18deg)}.fh-b27-tr-emb i:nth-child(3){transform:rotate(18deg)}
.fh-b27-tr-emb i,.fh-b27-tr-back{background:radial-gradient(circle at 50% 50%,rgba(242,217,140,.95) 0 5px,transparent 6px),radial-gradient(circle at 50% 50%,transparent 0 15px,rgba(217,180,90,.85) 15.5px 16.5px,transparent 17px),radial-gradient(circle at 50% 50%,transparent 0 24px,rgba(217,180,90,.45) 24.5px 25px,transparent 25.5px),radial-gradient(rgba(242,217,140,.35) 1px,transparent 1.5px) 0 0/9px 9px,linear-gradient(160deg,#2A1747,#160C2A 60%,#2A1240);border:2px solid var(--gold);box-shadow:inset 0 0 0 3px #160C2A,inset 0 0 0 4px rgba(217,180,90,.6),0 8px 18px rgba(0,0,0,.55)}
.fh-b27-tr-emb i:nth-child(2){z-index:1;background:linear-gradient(#F7EDD3,#EAD7AE);display:flex;align-items:center;justify-content:center;font:700 22px 'Cinzel',serif;color:#3A2A14}
.fh-b27[data-fh-page="tarot"] .fh-b27-tape{transform:none;border-radius:2px;background:transparent;color:var(--gold2);border:1px solid var(--gold);font-family:'Cinzel','Shippori Mincho',serif;letter-spacing:.12em}
.fh-b27[data-fh-page="tarot"] .fh-b27-title{font-family:'Shippori Mincho',serif;font-weight:800;font-size:32px;color:#FFF6DF;text-shadow:0 0 18px rgba(255,190,90,.25)}
.fh-b27-tr-en{display:block;font:500 13px 'Cinzel',serif;letter-spacing:.35em;color:var(--gold)}
.fh-b27[data-fh-page="tarot"] h2{font-family:'Shippori Mincho',serif;font-weight:800;font-size:24px;justify-content:center;text-align:center;flex-direction:column;gap:2px}
.fh-b27[data-fh-page="tarot"] h2:before{content:"✦ ─────── ✦";font-size:11px;letter-spacing:.2em;color:var(--gold)}
.fh-b27[data-fh-page="tarot"] h2 .fh-b27-n{border:0;width:auto;height:auto;background:none;color:var(--gold);font:700 14px 'Cinzel',serif;letter-spacing:.2em}
.fh-b27[data-fh-page="tarot"] h3{border-bottom:0;background:linear-gradient(90deg,var(--gold),transparent) left bottom/100% 1px no-repeat;color:var(--gold2)}
.fh-b27[data-fh-page="tarot"] .fh-b27-toc{border:1px solid rgba(217,180,90,.45);border-radius:6px;background:rgba(18,11,28,.7)}
.fh-b27[data-fh-page="tarot"] .fh-b27-toc ol{columns:2;column-gap:28px;list-style:none;padding-left:0}
.fh-b27-tr-felt{border-radius:16px;padding:16px;background:radial-gradient(ellipse at 50% 40%,#3B1530,#220B1E 70%);box-shadow:inset 0 0 0 1px rgba(217,180,90,.5),inset 0 0 40px rgba(0,0,0,.6);display:flex;flex-direction:column;gap:12px}
.fh-b27-tr-modes{display:flex;flex-wrap:wrap;gap:8px;justify-content:center}
.fh-b27-tr-modes button,.fh-b27-tr-draw{min-height:44px;border-radius:4px;font:inherit;font-weight:700;padding:0 16px;cursor:pointer}
.fh-b27-tr-modes button{background:rgba(0,0,0,.25);border:1px solid rgba(217,180,90,.4);color:var(--sub)}
.fh-b27-tr-modes button[aria-pressed="true"]{border-color:var(--gold2);color:#1A1022;background:linear-gradient(#F2D98C,#C9A04A)}
.fh-b27-tr-draw{border:1px solid #F2D98C;background:linear-gradient(#E9C46A,#B8893A);color:#1A1022;letter-spacing:.08em;box-shadow:0 0 18px rgba(255,190,90,.35)}
.fh-b27-tr-q{width:100%;min-height:44px;border-radius:4px;border:1px solid rgba(217,180,90,.45);background:rgba(0,0,0,.35);color:var(--ink);font:inherit;padding:0 12px}
.fh-b27-tr-table{display:flex;justify-content:center;gap:14px;flex-wrap:wrap;padding:10px 0}
.fh-b27-tr-slot{display:flex;flex-direction:column;align-items:center;gap:6px;font:500 12.5px 'Cinzel','Zen Kaku Gothic New',sans-serif;color:var(--gold);letter-spacing:.08em}
.fh-b27-tr-card{width:120px;height:198px;perspective:900px}
.fh-b27-tr-in{position:relative;width:100%;height:100%;transition:transform .9s cubic-bezier(.3,.7,.3,1);transform-style:preserve-3d}
.fh-b27-tr-card.is-open .fh-b27-tr-in{transform:rotateY(180deg)}
.fh-b27-tr-back,.fh-b27-tr-face{position:absolute;inset:0;border-radius:8px;backface-visibility:hidden;-webkit-backface-visibility:hidden}
.fh-b27-tr-face{transform:rotateY(180deg);background:linear-gradient(#F8EFD8,#E9D5A9);color:#2A1E14;border:2px solid var(--gold);box-shadow:inset 0 0 0 4px #F8EFD8,inset 0 0 0 5px rgba(150,110,40,.6),0 8px 18px rgba(0,0,0,.55);padding:12px 8px}
.fh-b27-tr-face>div{display:flex;flex-direction:column;align-items:center;justify-content:space-between;height:100%;width:100%}
.fh-b27-tr-card.is-rev .fh-b27-tr-face>div{transform:rotate(180deg)}
.fh-b27-tr-face .r{font:700 15px 'Cinzel',serif;letter-spacing:.1em}
.fh-b27-tr-face .s{font-size:42px;line-height:1;color:#7A3A55;font-family:'Segoe UI Symbol','Noto Sans Symbols 2','Noto Sans Symbols',serif}
.fh-b27-tr-face .n{font:800 15px 'Shippori Mincho',serif;text-align:center;line-height:1.3}
.fh-b27-tr-face .e{font:500 8.5px 'Cinzel',serif;color:#6E5A3A;letter-spacing:.06em;text-align:center}
.fh-b27-tr-res{display:flex;flex-direction:column;gap:12px}
.fh-b27-tr-rc{background:linear-gradient(#F8EFD8,#EFE0BC);color:var(--cream-ink);border-radius:6px;padding:16px 18px;line-height:1.85;font-size:15px;box-shadow:inset 0 0 0 1px rgba(150,110,40,.5)}
.fh-b27 .fh-b27-tr-rc p,.fh-b27 .fh-b27-tr-rc b,.fh-b27 .fh-b27-tr-rc strong{color:var(--cream-ink)}
.fh-b27-tr-rc strong{font-family:'Shippori Mincho',serif;font-size:19px}
.fh-b27-tr-rc small{color:#7A6544}
.fh-b27 .fh-b27-tr-rc a{color:#7A3A55;font-weight:700}
.fh-b27-tr-yes{font:800 30px 'Shippori Mincho',serif;color:#7A3A55}
.fh-b27-tr-spreads{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.fh-b27-tr-spreads a{display:block;border:1px solid rgba(217,180,90,.45);border-radius:6px;padding:12px 14px;text-decoration:none;background:rgba(0,0,0,.25)}
.fh-b27-tr-spreads b{display:block;font-family:'Shippori Mincho',serif;color:var(--gold2)}
.fh-b27-tr-spreads small{color:var(--sub);font-size:13px}
.fh-b27-tr-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:8px}
.fh-b27-tr-grid a{display:flex;flex-direction:column;align-items:center;gap:2px;border:1px solid rgba(217,180,90,.35);border-radius:6px;padding:8px 2px;text-decoration:none;background:rgba(0,0,0,.25);font-size:12.5px;color:var(--ink);line-height:1.3;text-align:center}
.fh-b27-tr-grid a b{font:700 12px 'Cinzel',serif;color:var(--gold)}
.fh-b27-tr-grid a span{font-size:20px;color:#E7A8BE;font-family:'Segoe UI Symbol','Noto Sans Symbols 2',serif}
.fh-b27-tr-list{display:flex;flex-direction:column;gap:8px}
.fh-b27-tr-list details{border:1px solid rgba(217,180,90,.3);border-radius:6px;background:rgba(0,0,0,.22);padding:8px 14px}
.fh-b27-tr-list summary{cursor:pointer;font-family:'Shippori Mincho',serif;font-weight:800;font-size:16.5px;color:var(--ink)}
.fh-b27-tr-list summary small{font-family:'Zen Kaku Gothic New',sans-serif;font-weight:400;color:var(--mute);font-size:12.5px;margin-left:8px}
.fh-b27-tr-list summary .k{color:var(--gold);margin-right:8px;font-family:'Cinzel',serif;font-size:14px}
.fh-b27-tr-list h3{font-size:15.5px;margin:10px 0 4px}
.fh-b27-tr-list p{font-size:14.5px;line-height:1.9}
.fh-b27-tr-kw{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0}
.fh-b27-tr-kw span{border:1px solid var(--line);border-radius:999px;padding:0 10px;font-size:12.5px}
.fh-b27-tr-kw span.u{border-color:var(--gold);color:var(--gold2)}
.fh-b27-tr-kw span.v{border-color:#B07A92;color:#E7A8BE}
.fh-b27-tr-suit{border:1px solid rgba(217,180,90,.35);border-radius:10px;padding:12px 14px;background:rgba(90,31,51,.18)}
.fh-b27-tr-suit h3{margin-top:0}
.fh-b27-tr-two{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.fh-b27-tr-two>div{border:1px solid rgba(217,180,90,.3);border-radius:6px;padding:10px 14px;background:rgba(0,0,0,.2)}
.fh-b27-tr-steps{counter-reset:s;list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:8px}
.fh-b27 .fh-b27-tr-steps li{counter-increment:s;margin:0;padding:8px 12px 8px 46px;position:relative;border:1px solid rgba(217,180,90,.25);border-radius:6px;font-size:14.5px;line-height:1.8;background:rgba(0,0,0,.18)}
.fh-b27-tr-steps li::before{content:counter(s,upper-roman);position:absolute;left:10px;top:9px;width:28px;text-align:center;color:var(--gold);font:700 14px 'Cinzel',serif}
.fh-b27-tr-steps li b{display:block;color:var(--gold2)}
.fh-b27-tr-t{width:100%;border-collapse:collapse;font-size:14px;line-height:1.7}
.fh-b27-tr-t th,.fh-b27-tr-t td{border-bottom:1px solid rgba(217,180,90,.2);padding:7px 6px;text-align:left;vertical-align:top}
.fh-b27-tr-t thead th{color:var(--gold);font-size:13px}
.fh-b27-tr-qa details{border-bottom:1px solid rgba(217,180,90,.25);padding:8px 2px}
.fh-b27-tr-qa summary{cursor:pointer;font-weight:700}
.fh-b27-tr-qa p{margin-top:6px;font-size:14.5px}
@media (max-width:640px){.fh-b27-tr-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.fh-b27-tr-two,.fh-b27-tr-spreads{grid-template-columns:1fr}.fh-b27[data-fh-page="tarot"] .fh-b27-toc ol{columns:1}.fh-b27-tr-card{width:94px;height:156px}.fh-b27-tr-face .s{font-size:32px}.fh-b27-tr-emb{flex-basis:120px;transform:scale(.85)}.fh-b27[data-fh-page="tarot"] .fh-b27-title{font-size:26px}}
@media (prefers-reduced-motion:reduce){.fh-b27-tr-in{transition:none}.fh-b27-tr-emb:before{animation:none}}
 .fh-b27-tr-ql{display:block;text-align:center;font:700 20px 'Shippori Mincho',serif;color:var(--gold);margin-bottom:6px}
textarea.fh-b27-tr-q{resize:vertical;min-height:64px;line-height:1.6}
.fh-b27-tr-topics{display:flex;flex-wrap:wrap;gap:6px;justify-content:center;margin:8px 0}
.fh-b27-tr-topics button{min-height:36px;border:1px solid rgba(217,180,90,.45);border-radius:999px;background:transparent;color:var(--gold);font:700 14px inherit;padding:0 14px;cursor:pointer}
.fh-b27-tr-topics button[aria-pressed="true"]{background:var(--gold);color:#2A0F1A}
.fh-b27-tr-ask{border:1px dashed rgba(217,180,90,.6);border-radius:8px;padding:10px 14px;margin-bottom:10px;background:rgba(0,0,0,.25);text-align:center}
.fh-b27 .fh-b27-tr-ask p{font:700 17px 'Shippori Mincho',serif;color:var(--gold2,#F3E2B0);margin:2px 0}
.fh-b27-tr-sum{margin-top:10px;border-radius:8px;padding:10px 14px;background:linear-gradient(135deg,rgba(217,180,90,.18),rgba(90,31,51,.3));border:1px solid rgba(217,180,90,.4)}
.fh-b27-tr-sum small{color:var(--gold)}
.fh-b27-tr-build{display:flex;flex-direction:column;gap:6px;margin:6px 0 10px}
.fh-b27-tr-row{display:flex;flex-wrap:wrap;gap:6px;align-items:center;justify-content:center}
.fh-b27-tr-row>span{flex:0 0 100%;text-align:center;font-size:12px;color:var(--gold);letter-spacing:.1em}
.fh-b27-tr-row button{min-height:40px;border:1px solid rgba(217,180,90,.5);border-radius:6px;background:linear-gradient(180deg,#3A1424,#2A0F1A);color:#F3E2B0;font:700 14px inherit;padding:0 12px;cursor:pointer;box-shadow:0 2px 0 rgba(0,0,0,.4)}
.fh-b27-tr-row button[aria-pressed="true"]{background:linear-gradient(180deg,#E7C46A,#C9A040);color:#2A0F1A;transform:translateY(-2px) rotate(-1deg)}
.fh-b27-tr-ab{display:flex;gap:6px;margin:6px 0}.fh-b27-tr-ab input{flex:1;min-width:0;min-height:42px;border-radius:6px;border:1px solid rgba(217,180,90,.5);background:rgba(0,0,0,.3);color:#F3E2B0;font:inherit;padding:0 10px}
.fh-b27-tr-verdict{text-align:center;border-radius:10px;padding:14px;margin:6px 0 12px;background:radial-gradient(circle at 50% 0,rgba(231,196,106,.35),rgba(42,15,26,.6));border:1.5px solid rgba(231,196,106,.7);animation:fh-b27-tr-v .8s ease both}
.fh-b27-tr-verdict small{color:var(--gold)}.fh-b27 .fh-b27-tr-verdict b{display:block;font:800 26px 'Shippori Mincho',serif;color:#FFF1C9;margin:2px 0 4px}
.fh-b27 .fh-b27-tr-verdict p{color:#F3E2B0;margin:0}
@keyframes fh-b27-tr-v{from{opacity:0;transform:scale(.9)}to{opacity:1;transform:none}}
.fh-b27-tr-more{text-align:center}.fh-b27-tr-more summary{cursor:pointer;color:var(--gold);font-size:13px}
</style>"""

JS = r"""(function(){var MA=__MAJOR__,MI=__MINOR__,TP=__TP__;var root=document.getElementById('fh-b27-tr');if(!root)return;
var mode='one',deck='major',modes=root.querySelectorAll('[data-mode]'),decks=root.querySelectorAll('[data-deck]'),table=document.getElementById('fh-b27-tr-table'),res=document.getElementById('fh-b27-tr-res'),qa=document.getElementById('fh-b27-tr-q');
var LABEL={one:['MESSAGE'],three:['PAST','PRESENT','FUTURE'],yes:['ANSWER'],when:['SOON','3 MONTHS','6 MONTHS'],choice:['A','B'],feel:['SURFACE','HEART','NEXT'],adv:['ADVICE']},
JP={MESSAGE:'今のあなたへ',PAST:'過去',PRESENT:'現在',FUTURE:'未来',ANSWER:'答え',SOON:'近いうち','3 MONTHS':'3か月ほど先','6 MONTHS':'半年ほど先',A:'Aを選んだら',B:'Bを選んだら',SURFACE:'表に見せている気持ち',HEART:'心の奥の本音',NEXT:'これからの気持ち',ADVICE:'うまくいくためのヒント'};
var TN={kataomoi:'片思い',couple:'恋人との関係',fukuen:'復縁',kimochi:'相手の気持ち',kekkon:'結婚',tenshoku:'仕事・転職',shokuba:'人間関係',kinun:'お金',love:'恋愛',work:'仕事',gen:'全体の流れ'};
var sel={who:null,about:null,want:null};
function rnd(n){var a=new Uint32Array(1);(window.crypto||window.msCrypto).getRandomValues(a);return a[0]%n;}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function face(c){return '<div><span class="r">'+esc(c.r)+'</span><span class="s">'+c.s+'</span><span class="n">'+esc(c.name)+'</span><span class="e">'+esc(c.en.toUpperCase())+'</span></div>';}
function slots(){var L=LABEL[mode];table.innerHTML=L.map(function(l){return '<div class="fh-b27-tr-slot"><div class="fh-b27-tr-card"><div class="fh-b27-tr-in"><div class="fh-b27-tr-back"></div><div class="fh-b27-tr-face"></div></div></div><span>'+(JP[l]&&mode!=='one'&&mode!=='three'?JP[l]:l)+'</span></div>';}).join('');res.innerHTML='';}
function setMode(v){mode=v;modes.forEach(function(x){x.setAttribute('aria-pressed',x.getAttribute('data-mode')===v?'true':'false')});slots();}
modes.forEach(function(b){b.addEventListener('click',function(){setMode(b.getAttribute('data-mode'));})});
decks.forEach(function(b){b.addEventListener('click',function(){deck=b.getAttribute('data-deck');decks.forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false')});slots();})});
function yes(c,rev){var y=c.yesno;if(!rev)return y;return y==='はい'?'どちらとも言えない':'いいえ';}
function kw(p){return (p.rev?p.c.kw_rev:p.c.kw_up)[0];}
// 相談の文から、テーマと質問の種類を読む
function topic(q){if(sel.topic)return sel.topic;
 if(/気持ち|本音|どう思って|脈|好意/.test(q))return 'kimochi';if(/復縁|よりを戻|元カレ|元カノ|元彼|元恋人|別れた/.test(q))return 'fukuen';
 if(/結婚|プロポーズ|婚活|入籍|夫婦|将来を/.test(q))return 'kekkon';if(/片思い|片想い|告白|好きな人|出会い|付き合え/.test(q))return 'kataomoi';
 if(/彼氏|彼女|恋人|パートナー|夫|妻|恋|デート|浮気|けんか|喧嘩/.test(q))return 'couple';if(/転職|就職|仕事|職場で|キャリア|昇進|独立|起業|試験|受験|資格|面接/.test(q))return 'tenshoku';
 if(/友達|友人|人間関係|上司|同僚|部下|家族|親|子ども|子供|ママ友|先輩|後輩|クラス|学校/.test(q))return 'shokuba';if(/お金|金運|収入|貯金|買う|買い|投資|副業|借金|節約|給料|宝くじ/.test(q))return 'kinun';return 'gen';}
function qtype(q){if(sel.want)return sel.want;if(/どっち|どちら|AとB|か、|それとも/.test(q))return 'choice';if(/いつ|時期|何月|いつ頃|いつごろ/.test(q))return 'when';
 if(/気持ち|本音|どう思って/.test(q))return 'feel';if(/どうすれば|どうしたら|方法|コツ|アドバイス/.test(q))return 'adv';
 if(/(か[？?]?$|[？?]$|べき|ほうがいい|方がいい|大丈夫|できる|うまくいく|叶う|かなう)/.test(q))return 'yes';return 'flow';}
var QM={choice:'choice',when:'when',feel:'feel',adv:'adv',yes:'yes',flow:'three'};
// 組み合わせカード
var WHO={me:'わたし',like:'好きな人',lover:'恋人',ex:'元恋人',work:'職場・学校の人',fam:'友達・家族'},ABOUT={love:'恋のゆくえ',heart:'気持ち',marry:'結婚',job:'仕事・転職',rel:'関係',money:'お金'},
WANT={flow:'これからどうなる？',yes:'うまくいく？',when:'いつ動けばいい？',adv:'どうすればいい？',choice:'AとB、どっちがいい？'};
function compose(){var w=sel.who,a=sel.about,t=sel.want,s='';if(!w&&!a&&!t)return;
 var who=w?WHO[w]:'',ab=a?ABOUT[a]:'';
 if(a==='heart')s=(w&&w!=='me'?who+'の':'あの人の')+'気持ち';else if(a==='rel')s=(w&&w!=='me'?who+'との':'')+'関係';else if(a)s=(w&&w!=='me'?who+'との':'')+ab;else s=who;
 s=s+(t?'は、'+WANT[t]:'');qa.value=s.replace(/^は、/,'');
 var tp=a==='heart'?'kimochi':a==='marry'?'kekkon':a==='job'?'tenshoku':a==='money'?'kinun':a==='rel'?(w==='lover'?'couple':w==='ex'?'fukuen':'shokuba'):a==='love'?(w==='lover'?'couple':w==='ex'?'fukuen':'kataomoi'):(w==='ex'?'fukuen':w==='lover'?'couple':w==='like'?'kataomoi':w==='work'||w==='fam'?'shokuba':null);
 sel.topic=tp;var m=(a==='heart'&&(!t||t==='flow'))?'feel':t?QM[t]:null;sel.mode=m;if(m)setMode(m);document.getElementById('fh-b27-tr-ab').hidden=!(mode==='choice');}
root.querySelectorAll('[data-pick]').forEach(function(b){b.addEventListener('click',function(){var g=b.getAttribute('data-pick'),v=b.getAttribute('data-v');sel[g]=sel[g]===v?null:v;
 root.querySelectorAll('[data-pick="'+g+'"]').forEach(function(x){x.setAttribute('aria-pressed',x.getAttribute('data-v')===sel[g]?'true':'false')});compose();});});
qa.addEventListener('input',function(){sel.topic=null;sel.want=null;root.querySelectorAll('[data-pick]').forEach(function(x){x.setAttribute('aria-pressed','false')});sel.who=sel.about=null;});
function ttext(p,tp){var t=TP[p.c.name];if(t&&t[tp])return t[tp][p.rev?'rev':'up'];if(tp==='kinun')return p.c.money||'';if(/work|tenshoku|shokuba/.test(tp))return p.c.work;if(tp!=='gen')return p.c.love;return '';}
function verdict(picks,q,qt,tp){var L=LABEL[mode];
 if(mode==='yes'){var y=yes(picks[0].c,picks[0].rev);return {big:y,txt:'カギになるのは「'+kw(picks[0])+'」。'+(y==='はい'?'流れはあなたの味方です。':y==='いいえ'?'今は無理に進めず、別の道や時期も考えてみて。':'今はまだ決め手が足りない状態です。')};}
 if(mode==='when'){var bi=-1;picks.forEach(function(p,i){if(bi<0&&!p.rev&&p.c.yesno==='はい')bi=i});if(bi<0)picks.forEach(function(p,i){if(bi<0&&!p.rev)bi=i});
  return bi<0?{big:'急がないで',txt:'3枚とも逆位置でした。半年ほどは準備の時期と考え、焦らず土台を整えましょう。'}:{big:JP[L[bi]],txt:'いちばん追い風が吹くのは「'+JP[L[bi]]+'」。'+esc(picks[bi].c.name)+'が「'+kw(picks[bi])+'」を示しています。'};}
 if(mode==='choice'){var mm=q.match(/^(.+?)(?:と|か|、|or)(.+?)(?:[、,]?\s*)(?:どっち|どちら)/),A=document.getElementById('fh-b27-tr-a').value.trim()||(mm?mm[1]:'A'),B=document.getElementById('fh-b27-tr-b').value.trim()||(mm?mm[2]:'B'),sc=picks.map(function(p){return (p.rev?0:2)+(p.c.yesno==='はい'&&!p.rev?1:0)});
  return sc[0]===sc[1]?{big:'どちらも良い',txt:'「'+esc(A)+'」も「'+esc(B)+'」も同じくらいの流れです。決め手は、あなたが心からわくわくするほうです。'}:{big:esc(sc[0]>sc[1]?A:B),txt:'カードは「'+esc(sc[0]>sc[1]?A:B)+'」をすすめています。'+esc(picks[sc[0]>sc[1]?0:1].c.name)+'の「'+kw(picks[sc[0]>sc[1]?0:1])+'」がその理由です。'};}
 if(mode==='feel')return {big:'本音は「'+kw(picks[1])+'」',txt:'表では「'+kw(picks[0])+'」を見せつつ、心の奥には「'+kw(picks[1])+'」があります。これからは「'+kw(picks[2])+'」へ。'};
 if(mode==='three')return {big:'この先は「'+kw(picks[2])+'」',txt:'「'+kw(picks[0])+'」だった流れが、今は「'+kw(picks[1])+'」。この先は「'+kw(picks[2])+'」へ向かいます。'};
 return {big:'カギは「'+kw(picks[0])+'」',txt:esc(picks[0].c.advice)};}
document.getElementById('fh-b27-tr-go').addEventListener('click',function(){var q=qa.value.trim();if(q&&!sel.want&&!sel.about){var qt0=qtype(q);setMode(QM[qt0]);}
 slots();var L=LABEL[mode],pool=deck==='all'?MA.concat(MI):MA.slice(),picks=[];
 for(var i=0;i<L.length;i++){var k=rnd(pool.length);picks.push({c:pool.splice(k,1)[0],rev:rnd(2)===1});}
 var cards=table.querySelectorAll('.fh-b27-tr-card');
 picks.forEach(function(p,i){var el=cards[i];el.querySelector('.fh-b27-tr-face').innerHTML=face(p.c);if(p.rev)el.classList.add('is-rev');setTimeout(function(){el.classList.add('is-open');},300+i*500);});
 var tp=topic(q),qt=qtype(q);
 setTimeout(function(){var v=verdict(picks,q,qt,tp),h='<div class="fh-b27-tr-ask"><small>'+(q?'あなたの相談':'今日のあなたへ')+'</small>'+(q?'<p>「'+esc(q)+'」</p>':'')+'<small>テーマ：'+TN[tp]+'</small></div>';
  h+='<div class="fh-b27-tr-verdict"><small>カードの答え</small><b>'+v.big+'</b><p>'+v.txt+'</p></div>';
  picks.forEach(function(p,i){var c=p.c,pos=p.rev?'逆位置':'正位置',kws=(p.rev?c.kw_rev:c.kw_up).join('・'),th=ttext(p,tp);
   var lab=JP[L[i]]||L[i];if(mode==='choice'){var mm2=q.match(/^(.+?)(?:と|か|、|or)(.+?)(?:[、,]?\s*)(?:どっち|どちら)/),nm2=(document.getElementById(i?'fh-b27-tr-b':'fh-b27-tr-a').value.trim()||(mm2?mm2[i+1]:(i?'B':'A')));lab='「'+esc(nm2)+'」を選んだら';}h+='<div class="fh-b27-tr-rc"><small>'+lab+'</small><br><strong>'+esc(c.name)+'（'+pos+'）</strong><br><small>キーワード：'+esc(kws)+'</small>';
   if(th)h+='<p><b>'+TN[tp]+'では</b>　'+esc(th)+'</p>';
   h+='<p>'+esc(p.rev?c.rev:c.up)+'</p>';
   if(!th&&mode==='one')h+='<p><b>恋愛</b>　'+esc(c.love)+'</p><p><b>仕事</b>　'+esc(c.work)+'</p>';
   h+='<p><a href="#'+c.a+'">'+esc(c.name)+'の意味をくわしく見る →</a></p></div>';});
  h+='<div class="fh-b27-tr-sum fh-b27-tr-adv"><small>カードからのひとこと</small><p>'+esc(picks[picks.length-1].c.advice)+'</p></div>';
  res.innerHTML=h;},400+L.length*500+600);});
slots();})();"""
SUITS = [("wands", "ワンド", "Wands", "♣︎", "火", "情熱・行動・仕事への意欲",
          "棒（杖）が描かれるスートで、四大元素の火に当たります。やる気や挑戦、新しく始めること、仕事への意欲など、前へ進むエネルギーを表します。ワンドが多く出たときは、考えるより動くことが鍵になりやすいときです。"),
         ("cups", "カップ", "Cups", "♥︎", "水", "感情・愛情・人間関係",
          "杯が描かれるスートで、四大元素の水に当たります。恋愛や友情、家族への思い、喜びや寂しさなど、心の動きを表します。カップが多く出たときは、損得よりも気持ちを大切にすると答えが見えてきます。"),
         ("swords", "ソード", "Swords", "♠︎", "風", "思考・言葉・決断と葛藤",
          "剣が描かれるスートで、四大元素の風に当たります。考えること、言葉で伝えること、決断や話し合いを表し、悩みや対立として現れることもあります。ソードが多く出たときは、頭の中を整理して言葉にすることが助けになります。"),
         ("pentacles", "ペンタクル", "Pentacles", "✪︎", "地", "お金・仕事の成果・暮らし",
          "金貨（星の紋章の入った円盤）が描かれるスートで、四大元素の地に当たります。お金や仕事の成果、体や暮らしの土台など、形のあるものを表します。ペンタクルが多く出たときは、地道な積み重ねが実を結ぶときです。")]
RANKS = [("エース", "始まりの種", "そのスートの力が生まれる最初の一歩"), ("2", "選択・バランス", "2つのものの間で釣り合いをとる"), ("3", "広がり", "最初の成果が形になり始める"),
         ("4", "安定", "いったん落ち着き、土台ができる"), ("5", "試練", "ゆさぶりや葛藤が起きる"), ("6", "回復・調和", "試練をこえて流れが整う"),
         ("7", "見直し・挑戦", "立ち止まって考え直す"), ("8", "動き・努力", "目標に向けて積み重ねる"), ("9", "ほぼ完成", "ゴールが見えてくる"),
         ("10", "完成と移行", "ひと区切りがつき、次の段階へ"), ("ペイジ", "学びと知らせ", "素直に学ぶ若い人・新しい知らせ"), ("ナイト", "行動と前進", "目的に向かって動く人"),
         ("クイーン", "受け止める成熟", "そのスートの力を内側で育てる人"), ("キング", "導く成熟", "そのスートの力で周りを導く人")]
RK = ["A", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "PAGE", "KNIGHT", "QUEEN", "KING"]
SPREADS = [("/number-fortune/tarot/hexagram/", "ヘキサグラム（7枚）", "六芒星の形に並べ、相手の気持ちや2人の関係をくわしく読みます。"),
           ("/number-fortune/tarot/celtic/", "ケルト十字（10枚）", "10枚で状況・原因・未来・結果まで読み解く、本格的な占い方です。")]


def kwspan(c):
    return ('<div class="fh-b27-tr-kw">' + "".join(f'<span class="u">正 {esc(k)}</span>' for k in c["kw_up"])
            + "".join(f'<span class="v">逆 {esc(k)}</span>' for k in c["kw_rev"]) + '</div>')


def build(sample, updated):
    cards = json.load(open(os.path.join(DATA, "tarot", "major.json"), encoding="utf-8"))
    minor = json.load(open(os.path.join(DATA, "tarot", "minor.json"), encoding="utf-8"))
    assert len(cards) == 22 and len(minor) == 56
    H = []
    a = H.append
    a(CSS)
    a('<div class="fh-b27" data-fh-page="tarot">\n<div class="fh-b27-note">')
    a(open(os.path.join(HERE, "templates", "tarot_parts.html"), encoding="utf-8").read().split("<!--HOW-->")[0])
    n = [1]

    def h2(t):
        s = f'<h2><span class="fh-b27-n"><span>{ROMAN[n[0]]}</span></span><span>{t}</span></h2>'
        n[0] += 1
        return s
    parts = open(os.path.join(HERE, "templates", "tarot_parts.html"), encoding="utf-8").read().split("<!--HOW-->")
    sp = "".join(f'<a href="{u}"><b>{esc(t)} →</b><small>{esc(d)}</small></a>' for u, t, d in SPREADS)
    a(parts[1].replace("@@H2@@", h2("カードを引いて占う")).replace("@@SPREADS@@", sp))
    keys = ("name", "en", "kw_up", "kw_rev", "up", "rev", "love", "work", "money", "advice", "yesno")
    dma = [dict({k: c[k] for k in keys}, r=ROMAN[c["no"]], s=SYM[c["no"]], a=f'b27-tr-c{c["no"]}') for c in cards]
    sym = {x[1]: x[3] for x in SUITS}
    for c in minor:
        c.setdefault("money", "")
    dmi = [dict({k: c[k] for k in keys}, r=RK[int(c["id"].split("-")[1]) - 1], s=sym[c["suit"]], a=f'b27-tr-{c["id"]}') for c in minor]
    import tarot_topics_major as T1, tarot_topics_wands as T2, tarot_topics_cups as T3, tarot_topics_swords as T4, tarot_topics_pentacles as T5
    TP = {}
    for m in (T1, T2, T3, T4, T5):
        TP.update(m.TOPIC)
    assert len(TP) == 78
    js = (JS.replace("__MAJOR__", json.dumps(dma, separators=(",", ":"))).replace("__MINOR__", json.dumps(dmi, separators=(",", ":")))
          .replace("__TP__", json.dumps(TP, ensure_ascii=False, separators=(",", ":"))))
    a(f"<script>{js}</script>")
    a("<!--Ads1-->")
    a(parts[2].replace("@@H2@@", h2("タロット占いのやり方")))
    a(parts[3].replace("@@H2@@", h2("正位置と逆位置")))
    grid = "".join(f'<a href="#b27-tr-c{c["no"]}"><b>{ROMAN[c["no"]]}</b><span aria-hidden="true">{SYM[c["no"]]}</span>{esc(c["name"])}</a>' for c in cards)
    det = ""
    for c in cards:
        det += (f'<details id="b27-tr-c{c["no"]}"><summary><span class="k">{ROMAN[c["no"]]}</span>{esc(c["name"])}<small>{esc(c["en"])}｜{esc("・".join(c["kw_up"]))}</small></summary>'
                + kwspan(c) + f'<p>{esc(c["motif"])}</p>'
                f'<h3>正位置の意味</h3><p>{esc(c["up"])}</p><h3>逆位置の意味</h3><p>{esc(c["rev"])}</p>'
                f'<h3>恋愛</h3><p>{esc(c["love"])}</p><h3>仕事</h3><p>{esc(c["work"])}</p><h3>お金</h3><p>{esc(c["money"])}</p>'
                f'<h3>アドバイス</h3><p>{esc(c["advice"])}</p><p class="fh-b27-small">Yes/No占いでの答え（正位置）：{esc(c["yesno"])}</p></details>')
    a(f'<section class="fh-b27-sec" id="b27-tr-all">\n  {h2("大アルカナ22枚の意味")}\n'
      '  <p>大アルカナは、0番の愚者から21番の世界まで、旅をするように人生の段階を表す22枚のカードです。カード名を押すと、正位置・逆位置の意味と、恋愛・仕事・お金の読み方が開きます。</p>\n'
      f'  <div class="fh-b27-tr-grid">{grid}</div>\n  <div class="fh-b27-tr-list">{det}</div>\n</section>')
    rk = "".join(f'<tr><th scope="row">{esc(r)}</th><td>{esc(k)}</td><td>{esc(d)}</td></tr>' for r, k, d in RANKS)
    suits_html = ""
    for sid, sj, se, sy, el, kw, intro in SUITS:
        dd = ""
        for c in [c for c in minor if c["suit"] == sj]:
            dd += (f'<details id="b27-tr-{c["id"]}"><summary><span class="k">{RK[int(c["id"].split("-")[1]) - 1]}</span>{esc(c["name"])}<small>{esc(c["en"])}｜{esc("・".join(c["kw_up"]))}</small></summary>'
                   + kwspan(c) + f'<h3>正位置の意味</h3><p>{esc(c["up"])}</p><h3>逆位置の意味</h3><p>{esc(c["rev"])}</p>'
                   f'<h3>恋愛</h3><p>{esc(c["love"])}</p><h3>仕事</h3><p>{esc(c["work"])}</p><h3>アドバイス</h3><p>{esc(c["advice"])}</p></details>')
        suits_html += (f'<div class="fh-b27-tr-suit" id="b27-tr-s-{sid}"><h3>{sy} {esc(sj)}（{se}）　<small style="color:var(--sub);font-weight:400">{el}・{esc(kw)}</small></h3>'
                       f'<p>{esc(intro)}</p><div class="fh-b27-tr-list">{dd}</div></div>')
    snav = "".join(f'<a href="#b27-tr-s-{x[0]}"><span aria-hidden="true">{x[3]}</span>{esc(x[1])}</a>' for x in SUITS)
    a(f'<section class="fh-b27-sec" id="b27-tr-minor">\n  {h2("小アルカナ56枚の意味")}\n'
      '  <p>小アルカナは、ワンド・カップ・ソード・ペンタクルの4つのスートに、エースから10までの数のカードと、ペイジ・ナイト・クイーン・キングの人物のカードが14枚ずつある56枚のカードです。日常の出来事や人の気持ちを具体的に表します。<b>スートの性質</b>と<b>数の流れ</b>を組み合わせて読むと、はじめてでも意味をつかみやすくなります。</p>\n'
      f'  <table class="fh-b27-tr-t"><caption style="text-align:left;color:var(--sub);font-size:13px">数と人物のカードの意味の流れ</caption><thead><tr><th scope="col">カード</th><th scope="col">キーワード</th><th scope="col">読み方</th></tr></thead><tbody>{rk}</tbody></table>\n'
      f'  <div class="fh-b27-tr-grid" style="grid-template-columns:repeat(4,minmax(0,1fr))">{snav}</div>\n  {suits_html}\n'
      '  <p class="fh-b27-small">カードの意味はこのサイトで書き下ろしたものです。カードの絵は特定のデッキの絵柄ではなく、このサイトのデザインです。番号の並びは、日本で広く使われているウェイト版（8番が力、11番が正義）に合わせています。</p>\n</section>')
    qa = "".join(f'<details{" open" if i == 0 else ""}><summary>Q. {q}</summary><p>A. {x}</p></details>' for i, (q, x) in enumerate(FAQ))
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in FAQ]}
    a(f'<section class="fh-b27-sec" id="b27-tr-faq">\n  {h2("よくある質問")}\n  <div class="fh-b27-tr-qa">{qa}</div>\n</section>\n'
      f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>')
    a(parts[4])
    up = dt.date.fromisoformat(updated)
    a(f'<p class="fh-b27-foot">タロット占いは、自分の気持ちや状況を見つめ直すための読み物です。楽しみと気づきのためにお使いください。<br>'
      f'最終更新日：{up.year}年{up.month}月{up.day}日／<a href="/about/">この記事の作成方針について</a></p>')
    a("</div>\n</div>")
    title = "タロット占い【無料】78枚の意味一覧｜1枚引き・3枚引き・Yes/No・ケルト十字"
    desc = ("無料のタロット占い。1枚引き・3枚引き（過去・現在・未来）・Yes/No占いで、今の悩みにカードが答えます。"
            "大アルカナ22枚と小アルカナ56枚、78枚すべての正位置・逆位置の意味と恋愛・仕事の読み方を一覧で紹介。")
    out = shell(title, desc, URL, "\n".join(H), sample)
    assert "！" not in out
    return out


def main():
    updated = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    for sample, path in ((False, os.path.join(OUT, "tarot.html")), (True, os.path.join(OUT, "sample", "tarot.html"))):
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(build(sample, updated))
        print("→", os.path.relpath(path, WORK))


if __name__ == "__main__":
    main()
