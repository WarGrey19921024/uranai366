"""エンジェルナンバーのページ（新しい固定ページ /angel-number/）を作る（2026-10-16。検索「エンジェルナンバー」月10万〜100万）。
作る前の確認：WordPress の固定ページ・投稿、静的ページに同じ内容のページは無い（/angel-number/ は404。/number-fortune/ は「好きな数字・縁のある数字」の数字占いで別の内容）。
文章：work/scripts/angel_texts.py（このサイトの言葉。数字ごとの意味を組み合わせて読む）
使い方: python work/scripts/build_angel.py [最終更新日]
出力: work/out/angel.html（投入用）、work/out/sample/angel.html（確認用）
"""
import datetime as dt, html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_hub import OUT, WORK, shell  # noqa: E402
import angel_texts as A  # noqa: E402

URL = "/angel-number/"
PREFIX = re.compile(r"^(恋愛では|恋愛の面では|仕事では|仕事の面では|お金では|お金の面では)、")


def esc(s):
    return html.escape(str(s), quote=True)


def clean(d):
    return {k: (PREFIX.sub("", v) if isinstance(v, str) and k in ("love", "work", "money") else v) for k, v in d.items()}


CSS = """<style id="fh-b27-an-css">
.fh-b27[data-fh-page="angel"]{--ink:#F5F1FF;--sub:#DCD5F0;--mute:#B5ADCC;--paper:#221E3A;--deep:#1A1730;--line:#5A5280;--gold:#F3D98B;--rose:#F6C1D4;--cream:#FFFDF7;--cream-ink:#2A2540}
.fh-b27[data-fh-page="angel"] a{color:#F7DE9A}
.fh-b27[data-fh-page="angel"] .fh-b27-note{border-left:0;border-radius:26px;background-color:var(--paper);
 background-image:radial-gradient(ellipse at 50% -10%,rgba(246,193,212,.30),transparent 55%),radial-gradient(circle at 90% 30%,rgba(243,217,139,.14),transparent 30%),
 radial-gradient(rgba(255,255,255,.55) .7px,transparent 1.3px),radial-gradient(rgba(255,255,255,.3) .6px,transparent 1px);
 background-size:auto,auto,80px 80px,31px 31px;background-position:0 0,0 0,7px 13px,0 0;box-shadow:0 14px 40px rgba(0,0,0,.45),inset 0 0 0 1px rgba(243,217,139,.25)}
.fh-b27-an-emb{position:relative;flex:0 0 150px;height:120px;display:flex;align-items:center;justify-content:center}
.fh-b27-an-emb b{font:800 46px 'Shippori Mincho',serif;color:var(--gold);letter-spacing:.06em;text-shadow:0 0 18px rgba(243,217,139,.7);animation:fh-b27-an-glow 3.6s ease-in-out infinite}
.fh-b27-an-emb::before,.fh-b27-an-emb::after{content:"";position:absolute;top:30px;width:48px;height:60px;border-radius:60% 10% 60% 40%;background:linear-gradient(160deg,#fff,rgba(255,255,255,.2));opacity:.55}
.fh-b27-an-emb::before{left:0;transform:rotate(-18deg)}.fh-b27-an-emb::after{right:0;transform:scaleX(-1) rotate(-18deg)}
@keyframes fh-b27-an-glow{50%{text-shadow:0 0 30px rgba(243,217,139,1),0 0 60px rgba(246,193,212,.6)}}
.fh-b27[data-fh-page="angel"] .fh-b27-hero{align-items:center}
.fh-b27[data-fh-page="angel"] .fh-b27-tape{transform:none;border-radius:999px;background:linear-gradient(90deg,var(--rose),var(--gold));color:#2A2540}
.fh-b27[data-fh-page="angel"] .fh-b27-title{font-family:'Shippori Mincho',serif;font-weight:800;font-size:30px}
.fh-b27[data-fh-page="angel"] h2{font-family:'Shippori Mincho',serif;font-weight:800;font-size:24px}
.fh-b27[data-fh-page="angel"] h2 .fh-b27-n{border:0;border-radius:50%;background:linear-gradient(135deg,var(--rose),var(--gold));color:#2A2540}
.fh-b27[data-fh-page="angel"] .fh-b27-toc{border-style:solid;border-radius:18px;border-color:rgba(243,217,139,.3)}
.fh-b27[data-fh-page="angel"] .fh-b27-toc ol{columns:2;column-gap:28px}
.fh-b27-an-box{border:1.5px solid rgba(243,217,139,.4);border-radius:20px;background:var(--deep);padding:16px;display:flex;flex-direction:column;gap:12px}
.fh-b27-an-form{display:flex;gap:8px;flex-wrap:wrap}
.fh-b27-an-form input{flex:1 1 180px;min-width:0;width:100%;box-sizing:border-box;min-height:48px;border-radius:12px;border:1.5px solid var(--line);background:var(--paper);color:var(--ink);font:800 24px 'Shippori Mincho',serif;letter-spacing:.2em;padding:0 14px}
.fh-b27-an-form button{min-height:48px;border:0;border-radius:999px;background:linear-gradient(90deg,#F6C1D4,#F3D98B);color:#2A2540;font:inherit;font-weight:800;padding:0 22px;cursor:pointer}
.fh-b27-an-chips{display:flex;flex-wrap:wrap;gap:6px}
.fh-b27-an-chips button{min-height:36px;border:1px solid rgba(243,217,139,.45);border-radius:999px;background:transparent;color:var(--gold);font:700 14px inherit;padding:0 12px;cursor:pointer}
.fh-b27-an-res{background:var(--cream);color:var(--cream-ink);border-radius:18px;padding:16px 18px;line-height:1.85}
.fh-b27 .fh-b27-an-res p,.fh-b27 .fh-b27-an-res b{color:var(--cream-ink)}
.fh-b27 .fh-b27-an-res a{color:#8A4B6E;font-weight:700}
.fh-b27-an-big{display:flex;justify-content:center;gap:4px;margin:2px 0 8px}
.fh-b27-an-big span{font:800 46px 'Shippori Mincho',serif;color:#2A2540;opacity:0;transform:translateY(12px) scale(.8);animation:fh-b27-an-pop .5s ease forwards;animation-delay:calc(var(--i)*.15s)}
@keyframes fh-b27-an-pop{60%{opacity:1;transform:translateY(-4px) scale(1.1);text-shadow:0 0 18px rgba(243,190,90,.9)}to{opacity:1;transform:none;text-shadow:0 0 8px rgba(243,190,90,.5)}}
.fh-b27-an-card{opacity:0;animation:fh-b27-an-in .6s ease .8s forwards}@keyframes fh-b27-an-in{to{opacity:1}}
.fh-b27-an-res .kw{text-align:center;font-family:'Shippori Mincho',serif;font-size:17px;color:#8A4B6E;margin:0 0 8px}
.fh-b27-an-tabs{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}
.fh-b27-an-tabs button{min-height:38px;border:1px solid #E2C9D6;border-radius:999px;background:#FFF;color:#5A3A50;font:inherit;font-size:14px;font-weight:700;padding:0 14px;cursor:pointer}
.fh-b27-an-tabs button[aria-selected="true"]{background:#8A4B6E;border-color:#8A4B6E;color:#fff}
.fh-b27-an-pane{background:#FFF;border-radius:12px;padding:12px 14px;min-height:5em}
.fh-b27-an-act{margin-top:10px;background:#FFF6DA;border-radius:12px;padding:10px 14px}
.fh-b27-an-list{display:flex;flex-direction:column;gap:8px}
.fh-b27-an-list details{border:1px solid rgba(243,217,139,.25);border-radius:16px;background:var(--deep);padding:6px 14px}
.fh-b27-an-list summary{cursor:pointer;font-family:'Shippori Mincho',serif;font-weight:800;font-size:18px;color:var(--gold)}
.fh-b27-an-list summary small{font-family:'Zen Kaku Gothic New',sans-serif;font-weight:400;color:var(--mute);font-size:12.5px;margin-left:8px}
.fh-b27-an-list p{font-size:14.5px;line-height:1.9;margin:6px 0}
.fh-b27-an-digits{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.fh-b27-an-digits div{border:1px solid rgba(246,193,212,.3);border-radius:16px;background:var(--deep);padding:10px 14px;font-size:14px;line-height:1.8}
.fh-b27-an-digits b{font:800 26px 'Shippori Mincho',serif;color:var(--rose);margin-right:8px}
.fh-b27-an-qa details{border-bottom:1px dashed var(--line);padding:8px 2px}
.fh-b27-an-qa summary{cursor:pointer;font-weight:700}
.fh-b27-an-qa p{margin-top:6px;font-size:14.5px}
@media (max-width:640px){.fh-b27-an-digits{grid-template-columns:1fr}.fh-b27[data-fh-page="angel"] .fh-b27-toc ol{columns:1}.fh-b27[data-fh-page="angel"] .fh-b27-title{font-size:25px}.fh-b27-an-emb{flex-basis:120px;height:100px}.fh-b27-an-emb b{font-size:36px}}
@media (prefers-reduced-motion:reduce){.fh-b27-an-emb b{animation:none}.fh-b27-an-big span,.fh-b27-an-card{animation:none;opacity:1;transform:none}}
</style>"""

JS = r"""(function(){var DG=__DG__,SP=__SP__;function $(i){return document.getElementById(i)}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
var f=$('an-form');if(!f)return;var inp=$('an-in');
function red(n){var s=String(n).split('').reduce(function(a,b){return a+(+b)},0);while(s>9){s=String(s).split('').reduce(function(a,b){return a+(+b)},0);}return s}
function show(v){v=String(v).replace(/[^0-9]/g,'').slice(0,8);if(!v){return}inp.value=v;var r=$('an-res'),sp=SP[v],big=v.split('').map(function(c,i){return '<span style="--i:'+i+'">'+c+'</span>'}).join(''),tx,kw,act;
 if(sp){kw=sp.kw;act=sp.action;tx={m:'<p>'+esc(sp.meaning)+'</p>',love:'<p>'+esc(sp.love)+'</p>',work:'<p>'+esc(sp.work)+'</p>',money:'<p>'+esc(sp.money)+'</p>'};}
 else{var ds=[];v.split('').forEach(function(c){if(ds.indexOf(c)<0)ds.push(c)});var t=red(v),T=DG[t];kw=ds.map(function(c){return DG[c].kw.split('・')[0]}).join('・');
  var m='<p>'+esc(v)+'は、'+ds.map(function(c){return '「'+c+'：'+esc(DG[c].kw)+'」'}).join('')+'の数字が組み合わさった並びです。すべての数字を足して一けたにすると'+t+'。全体のテーマは「'+esc(T.kw)+'」です。</p>'+ds.map(function(c){return '<p><b>'+c+'</b>：'+esc(DG[c].meaning)+'</p>'}).join('');
  tx={m:m,love:'<p>'+esc(T.love)+'</p>'+ds.slice(0,2).map(function(c){return '<p><b>'+c+'</b>：'+esc(DG[c].love)+'</p>'}).join(''),work:'<p>'+esc(T.work)+'</p>'+ds.slice(0,2).map(function(c){return '<p><b>'+c+'</b>：'+esc(DG[c].work)+'</p>'}).join(''),money:'<p>'+esc(T.money)+'</p>'+ds.slice(0,2).map(function(c){return '<p><b>'+c+'</b>：'+esc(DG[c].money)+'</p>'}).join('')};act=null;}
 var tb=[['m','意味'],['love','恋愛'],['work','仕事'],['money','お金']];
 r.innerHTML='<div class="fh-b27-an-big" aria-hidden="true">'+big+'</div><div class="fh-b27-an-card"><p class="kw">'+esc(kw)+'</p><div class="fh-b27-an-tabs" role="tablist">'+tb.map(function(b,i){return '<button type="button" role="tab" data-t="'+b[0]+'" aria-selected="'+(i?'false':'true')+'">'+b[1]+'</button>'}).join('')+'</div><div class="fh-b27-an-pane" id="an-pane">'+tx.m+'</div>'+
  (act?'<div class="fh-b27-an-act"><b>今日できること：</b>'+esc(act)+'</div>':'')+(sp?'<p><a href="#an-'+v+'">'+v+'の説明へ →</a></p>':'<p><small>この並びは、数字ごとの意味を組み合わせて読んでいます。</small></p>')+'</div>';
 r.hidden=false;r.querySelectorAll('.fh-b27-an-tabs button').forEach(function(b){b.addEventListener('click',function(){r.querySelectorAll('.fh-b27-an-tabs button').forEach(function(z){z.setAttribute('aria-selected','false')});b.setAttribute('aria-selected','true');$('an-pane').innerHTML=tx[b.getAttribute('data-t')];});});}
f.addEventListener('submit',function(e){e.preventDefault();show(inp.value)});
document.querySelectorAll('[data-an]').forEach(function(b){b.addEventListener('click',function(){show(b.getAttribute('data-an'));$('an-res').scrollIntoView({behavior:'smooth',block:'center'})})});
})();"""


def build(sample, updated):
    SP = {k: clean(v) for k, v in A.SPECIAL.items()}
    DG = {str(k): clean(v) for k, v in A.DIGITS.items()}
    H = []
    a = H.append
    a(CSS)
    a('<div class="fh-b27" data-fh-page="angel">\n<div class="fh-b27-note">')
    a('''<header class="fh-b27-hero">
  <div class="fh-b27-an-emb" aria-hidden="true"><b>111</b></div>
  <div class="fh-b27-hero-body">
    <span class="fh-b27-tape">人生予報 エンジェルナンバー</span>
    <h1 class="fh-b27-title">エンジェルナンバー<br>よく見る数字の意味</h1>
    <p class="fh-b27-lead">時計やレシート、車のナンバーで、同じ数字を何度も見かけることはありませんか。気になった数字を入れると、その数字の意味と、恋愛・仕事・お金のヒントがわかります。111や1111のようなゾロ目、1234のような並びの数字も一覧で読めます。</p>
  </div>
</header>''')
    rep = [k for k in SP if len(set(k)) == 1]
    other = [k for k in SP if len(set(k)) > 1]
    items = [("b27-an-pick", "気になる数字の意味を調べる"), ("b27-an-rep", "ゾロ目の意味（000〜9999）"), ("b27-an-other", "よく見る並びの数字の意味"),
             ("b27-an-digit", "0〜9の数字の意味"), ("b27-an-how", "エンジェルナンバーの読み方"), ("b27-an-faq", "よくある質問")]
    a('<nav class="fh-b27-toc" aria-label="目次"><strong>このページの内容</strong><ol>' + "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in items) + "</ol></nav>")
    n = [0]

    def h2(t):
        n[0] += 1
        return f'<h2><span class="fh-b27-n">{n[0]}</span><span>{t}</span></h2>'
    chips = "".join(f'<button type="button" data-an="{k}">{k}</button>' for k in ["111", "222", "333", "444", "555", "777", "888", "1111", "1234", "1212", "1122", "2222"])
    a(f'''<section class="fh-b27-sec" id="b27-an-pick">
  {h2("気になる数字の意味を調べる")}
  <div class="fh-b27-an-box">
    <form class="fh-b27-an-form" id="an-form" aria-label="数字を入れる"><input id="an-in" inputmode="numeric" pattern="[0-9]*" maxlength="8" placeholder="例：1111" aria-label="気になる数字（8けたまで）"><button type="submit">意味を見る</button></form>
    <div class="fh-b27-an-chips" aria-label="よく見る数字">{chips}</div>
    <div class="fh-b27-an-res" id="an-res" aria-live="polite" hidden></div>
    <p class="fh-b27-small">8けたまでの数字を読めます。一覧にない数字は、数字ごとの意味を組み合わせて読みます。入れた数字は送信も保存もしません。</p>
  </div>
</section>''')

    def det(keys):
        return "".join(f'<details id="an-{k}"><summary>{k}<small>{esc(SP[k]["kw"])}</small></summary><p>{esc(SP[k]["meaning"])}</p>'
                       f'<p><b>恋愛：</b>{esc(SP[k]["love"])}</p><p><b>仕事：</b>{esc(SP[k]["work"])}</p><p><b>お金：</b>{esc(SP[k]["money"])}</p>'
                       f'<p><b>今日できること：</b>{esc(SP[k]["action"])}</p></details>' for k in keys)
    a(f'''<section class="fh-b27-sec" id="b27-an-rep">
  {h2("ゾロ目の意味（000〜9999）")}
  <p>同じ数字が3つ、4つと並ぶゾロ目は、その数字の意味が強く表れていると読みます。数字を押すと、恋愛・仕事・お金のヒントと、今日できる小さなことが開きます。</p>
  <div class="fh-b27-an-list">{det(sorted(rep, key=lambda k: (len(k), k)))}</div>
</section>''')
    a(f'''<section class="fh-b27-sec" id="b27-an-other">
  {h2("よく見る並びの数字の意味")}
  <p>1234のような階段の数字や、1212のようなくり返しの数字も、よく気にされる並びです。</p>
  <div class="fh-b27-an-list">{det(sorted(other, key=lambda k: (len(k), k)))}</div>
</section>''')
    dg = "".join(f'<div id="an-d{k}"><b>{k}</b><span style="color:var(--gold)">{esc(v["kw"])}</span><br>{esc(v["meaning"])}<br><small>恋愛：{esc(v["love"])}<br>仕事：{esc(v["work"])}<br>お金：{esc(v["money"])}</small></div>' for k, v in DG.items())
    a(f'''<section class="fh-b27-sec" id="b27-an-digit">
  {h2("0〜9の数字の意味")}
  <p>エンジェルナンバーは、0から9までの数字それぞれの意味がもとになっています。一覧にない数字も、ここにある意味を組み合わせて読めます。</p>
  <div class="fh-b27-an-digits">{dg}</div>
</section>''')
    a(f'''<section class="fh-b27-sec" id="b27-an-how">
  {h2("エンジェルナンバーの読み方")}
  <p>エンジェルナンバーは、くり返し目に入る数字を、自分への小さなメッセージとして読む考え方です。2000年代に英語圏で広まった比較的新しい考え方で、科学的な根拠はありません。気持ちを整えるきっかけとして楽しんでください。</p>
  <p><b>組み合わせの読み方：</b>このページでは、一覧にない数字を、出てくる数字それぞれの意味と、すべての数字を足して1けたにした数（例：1225なら1＋2＋2＋5＝10→1＋0＝1）のテーマで読みます。同じ数字が多く並ぶほど、その意味が強いと考えます。</p>
  <p><b>見たときの使い方：</b>数字を見た瞬間に何を考えていたかを思い出すと、メッセージが自分の状況に結びつきやすくなります。気になる数字は手帳やメモに残しておくと、あとで流れを振り返れます。</p>
  <p>誕生日から決まる数（数秘術のライフパスや誕生日の数）は、<a href="/366uranai/">366日の誕生日占い</a>や<a href="/seinengappi/">生年月日まるごと診断</a>で見られます。</p>
</section>''')
    qa = "".join(f'<details{" open" if i == 0 else ""}><summary>Q. {esc(q)}</summary><p>A. {esc(x)}</p></details>' for i, (q, x) in enumerate(A.FAQ))
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in A.FAQ]}
    a(f'''<section class="fh-b27-sec" id="b27-an-faq">
  {h2("よくある質問")}
  <div class="fh-b27-an-qa">{qa}</div>
</section>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<section class="fh-b27-sec" id="b27-an-more">
  <div class="fh-b27-links">
    <a href="/tarot/"><b>タロット占い →</b><small>78枚の意味と1枚引き・3枚引き</small></a>
    <a href="/366uranai/"><b>366日の誕生日占い →</b><small>誕生日から性格と2027年の運勢</small></a>
    <a href="/seinengappi/"><b>生年月日まるごと診断 →</b><small>8つの占いを1枚のカードに</small></a>
  </div>
</section>''')
    js = JS.replace("__DG__", json.dumps(DG, ensure_ascii=False)).replace("__SP__", json.dumps(SP, ensure_ascii=False))
    up = dt.date.fromisoformat(updated)
    a(f'<p class="fh-b27-foot">エンジェルナンバーの意味は、数字ごとに一般に知られている考え方をもとに、このサイトで書いたものです。占いは楽しみと気づきのためにお読みください。<br>'
      f'最終更新日：{up.year}年{up.month}月{up.day}日／<a href="/about/">この記事の作成方針について</a></p>')
    a("</div>\n</div>")
    a(f"<script>document.addEventListener('DOMContentLoaded',function(){{{js}}});</script>")
    title = "エンジェルナンバーの意味一覧｜111・1111・1234など、よく見る数字のメッセージ【恋愛・仕事・お金】"
    desc = ("エンジェルナンバーの意味を、気になる数字を入れて無料で調べられます。000〜9999のゾロ目、1234・1212などよく見る並びの数字、"
            "0〜9の数字の意味を、恋愛・仕事・お金のヒントと今日できることつきで紹介します。")
    out = shell(title, desc, URL, "\n".join(H), sample)
    assert "！" not in out and "動物占い" not in out
    return out


def main():
    updated = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    for sample, path in ((False, os.path.join(OUT, "angel.html")), (True, os.path.join(OUT, "sample", "angel.html"))):
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(build(sample, updated))
        print("→", os.path.relpath(path, WORK))


if __name__ == "__main__":
    main()
