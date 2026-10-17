"""おみくじ（/omikuji/、固定ページ ID 4194）を作り直す（2026-10-18 本人の要望：大きな神社のようにパターンを増やす）。
12段階の吉凶＋総合のことば＋10項目（願望〜病気）の言葉＋ラッキーな方角・色・時間。引くたびに組み合わせが変わる。
結果の帯（よい・まずまず・気をつけたい）に合わせて、開運アイテムの広告を出し分ける（商品は build_omikuji_ads.py の CATS）。
文章：work/scripts/omikuji_texts.py。注意：Diver は JS の [sp] [pc] を消す・WordPress は絵文字を &#x…; にする・
遅延読み込みがスクリプト内の画像タグを書き換える → JS では絵文字と画像タグを使わない（広告の箱はHTMLで3つ用意して出し分ける）。
使い方: python work/scripts/build_omikuji.py [最終更新日]
出力: work/out/omikuji.html（投入用）、work/out/sample/omikuji.html（確認用）
"""
import datetime as dt, html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_hub import OUT, WORK, shell  # noqa: E402
import aff_extra as AX  # noqa: E402
import omikuji_texts as O  # noqa: E402
from build_omikuji_ads import CATS  # noqa: E402

URL = "/omikuji/"
BAND = {"good": ("よい運勢", "#C2273A"), "mid": ("まずまずの運勢", "#B7791F"), "bad": ("気をつけたい運勢", "#4A5568")}


def esc(s):
    return html.escape(str(s), quote=True)


CSS = """<style id="fh-b27-om-css">
.fh-b27[data-fh-page="omikuji"]{--ink:#2B2420;--sub:#5A4E45;--mute:#8A7B6E;--paper:#FBF5EA;--deep:#F3E9D8;--line:#E2D3BA;--gold:#B8862E;--cream:#FFFDF8;--cream-ink:#2B2420}
.fh-b27[data-fh-page="omikuji"] a{color:#A3222F}
.fh-b27[data-fh-page="omikuji"] .fh-b27-note{border-left:0;border-radius:20px;background-color:#FBF5EA;background-image:linear-gradient(180deg,#FFF9EF,#F6ECDB);background-size:auto;background-repeat:no-repeat;box-shadow:0 14px 34px rgba(80,50,20,.18),inset 0 0 0 1px #E9DAC0}
.fh-b27[data-fh-page="omikuji"] .fh-b27-hero{align-items:center}
.fh-b27-om-box{width:96px;height:150px;flex:0 0 auto;position:relative;border-radius:10px 10px 14px 14px;background:linear-gradient(90deg,#9E1B28,#C2273A 45%,#9E1B28);box-shadow:inset 0 0 0 3px #E2B65B,0 8px 18px rgba(80,20,20,.3)}
.fh-b27-om-box:before{content:"御\\Aみ\\Aく\\Aじ";white-space:pre;position:absolute;left:50%;top:18px;transform:translateX(-50%);width:34px;padding:6px 0;background:#FFF6E0;border:1px solid #E2B65B;text-align:center;font:800 15px/1.3 'Shippori Mincho',serif;color:#7A1520}
.fh-b27-om-box i{position:absolute;left:50%;top:-30px;width:8px;height:44px;margin-left:-4px;border-radius:3px;background:#F2E2BC;box-shadow:0 0 0 1px #C9A86A;opacity:0}
.fh-b27-om-box.shake{animation:fh-b27-om-shake .18s linear 6}
.fh-b27-om-box.out i{animation:fh-b27-om-stick .7s ease forwards}
@keyframes fh-b27-om-shake{25%{transform:rotate(-8deg)}75%{transform:rotate(8deg)}}
@keyframes fh-b27-om-stick{from{opacity:0;top:0}to{opacity:1;top:-34px}}
.fh-b27[data-fh-page="omikuji"] .fh-b27-tape{transform:none;border-radius:999px;background:#C2273A;color:#fff}
.fh-b27[data-fh-page="omikuji"] .fh-b27-title{font-family:'Shippori Mincho',serif;font-weight:800;font-size:30px;color:#2B2420}
.fh-b27[data-fh-page="omikuji"] .fh-b27-lead{color:#4A3F36}
.fh-b27[data-fh-page="omikuji"] h2{font-family:'Shippori Mincho',serif;font-weight:800;font-size:24px;color:#2B2420}
.fh-b27[data-fh-page="omikuji"] h2 .fh-b27-n{border:0;border-radius:50%;background:#C2273A;color:#fff}
.fh-b27[data-fh-page="omikuji"] .fh-b27-sec>p,.fh-b27[data-fh-page="omikuji"] li,.fh-b27[data-fh-page="omikuji"] td{color:#2B2420}
.fh-b27[data-fh-page="omikuji"] .fh-b27-toc{border-style:solid;border-radius:16px;border-color:#E2D3BA;background:#FFFDF8}
.fh-b27[data-fh-page="omikuji"] .fh-b27-toc ol{columns:2;column-gap:28px}
.fh-b27-om-stage{border:1.5px solid #E2D3BA;border-radius:20px;background:#FFFDF8;padding:18px 16px;display:flex;flex-direction:column;align-items:center;gap:14px}
.fh-b27-om-stage .fh-b27-om-box{width:110px;height:170px}
.fh-b27-om-go{min-height:52px;border:0;border-radius:999px;background:#C2273A;color:#fff;font:inherit;font-weight:800;font-size:17px;padding:0 30px;cursor:pointer;box-shadow:0 4px 0 #7A1520}
.fh-b27-om-go:active{transform:translateY(2px);box-shadow:0 2px 0 #7A1520}
.fh-b27-om-paper{width:100%;max-width:560px;background:#FFFEFA;border:1px solid #D9C7A6;border-radius:6px;box-shadow:0 6px 18px rgba(80,50,20,.15);padding:18px 18px 14px;position:relative;opacity:0;transform:translateY(-14px);transition:opacity .6s,transform .6s}
.fh-b27-om-paper.on{opacity:1;transform:none}
.fh-b27-om-paper:before{content:"";position:absolute;inset:6px;border:1px solid #E9D9BC;border-radius:3px;pointer-events:none}
.fh-b27-om-no{text-align:center;font:700 13px 'Shippori Mincho',serif;color:#8A7B6E;letter-spacing:.2em}
.fh-b27-om-lv{text-align:center;font:800 54px/1.15 'Shippori Mincho',serif;letter-spacing:.12em;margin:4px 0}
.fh-b27-om-band{text-align:center;font-size:12px;color:#fff;border-radius:999px;display:table;margin:0 auto 8px;padding:1px 12px}
.fh-b27-om-sum{font-family:'Shippori Mincho',serif;font-size:16px;line-height:2;color:#2B2420;margin:6px 4px 10px}
.fh-b27-om-items{width:100%;border-collapse:collapse;font-size:14.5px}
.fh-b27-om-items th{width:4.6em;text-align:left;vertical-align:top;padding:6px 6px 6px 2px;border-top:1px dashed #E2D3BA;font-family:'Shippori Mincho',serif;color:#7A1520;white-space:nowrap}
.fh-b27-om-items td{padding:6px 2px;border-top:1px dashed #E2D3BA;color:#2B2420}
.fh-b27-om-lucky{display:flex;flex-wrap:wrap;gap:6px;justify-content:center;margin-top:10px}
.fh-b27-om-lucky span{border:1px solid #E2D3BA;border-radius:999px;padding:2px 10px;font-size:13px;background:#FFF8EA;color:#5A4E45}
.fh-b27-om-ads{width:100%}
.fh-b27-om-ads>div[hidden]{display:none}
.fh-b27-om-tbl{width:100%;border-collapse:collapse;font-size:14px}
.fh-b27-om-tbl th,.fh-b27-om-tbl td{border-bottom:1px dashed #E2D3BA;padding:6px;text-align:left;color:#2B2420}
.fh-b27-om-tbl thead th{color:#7A1520;font-weight:800}
.fh-b27-om-qa details{border-bottom:1px dashed #E2D3BA;padding:8px 2px}
.fh-b27-om-qa summary{cursor:pointer;font-weight:700;color:#2B2420}
.fh-b27-om-qa p{margin-top:6px;font-size:14.5px;color:#2B2420}
.fh-b27[data-fh-page="omikuji"] .fh-b27-om-sum,.fh-b27[data-fh-page="omikuji"] .fh-b27-om-stage p,.fh-b27[data-fh-page="omikuji"] .fh-b27-adgoods-h,.fh-b27[data-fh-page="omikuji"] .fh-b27-adgoods-l,.fh-b27[data-fh-page="omikuji"] .fh-b27-adphone,.fh-b27[data-fh-page="omikuji"] .fh-b27-adphone p,.fh-b27[data-fh-page="omikuji"] .fh-b27-toc,.fh-b27[data-fh-page="omikuji"] .fh-b27-toc a,.fh-b27[data-fh-page="omikuji"] .fh-b27-foot{color:#2B2420}
.fh-b27[data-fh-page="omikuji"] a.fh-b27-shopbtn,.fh-b27[data-fh-page="omikuji"] a.fh-b27-shopbtn:visited{color:#fff}
.fh-b27[data-fh-page="omikuji"] .fh-b27-links a{color:#2B2420}
.fh-b27[data-fh-page="omikuji"] .fh-b27-adphone small,.fh-b27[data-fh-page="omikuji"] .fh-b27-links small,.fh-b27[data-fh-page="omikuji"] .fh-b27-pr{color:#5A4E45}
.fh-b27[data-fh-page="omikuji"] a.fh-b27-ghost{color:#7A1520;border-color:#C2273A}
@media (max-width:640px){.fh-b27[data-fh-page="omikuji"] .fh-b27-toc ol{columns:1}.fh-b27[data-fh-page="omikuji"] .fh-b27-title{font-size:25px}.fh-b27-om-lv{font-size:44px}.fh-b27-om-box{width:76px;height:120px}.fh-b27-om-box:before{font-size:12px;width:28px}}
@media (prefers-reduced-motion:reduce){.fh-b27-om-box.shake,.fh-b27-om-box.out i{animation:none}.fh-b27-om-paper{transition:none}}
</style>"""

JS = r"""(function(){var LV=__LV__,SM=__SM__,IT=__IT__,IO=__IO__,LD=__LD__,LC=__LC__,LT=__LT__,BC=__BC__;function $(i){return document.getElementById(i)}
if(!$('om-go'))return;
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function rnd(n){if(window.crypto&&crypto.getRandomValues){var a=new Uint32Array(1);crypto.getRandomValues(a);return a[0]%n}return Math.floor(Math.random()*n)}
function pick(a){return a[rnd(a.length)]}
function lot(){var t=0,i,r=rnd(100);for(i=0;i<LV.length;i++){t+=LV[i][2];if(r<t)return LV[i]}return LV[LV.length-1]}
var busy=false;
$('om-go').addEventListener('click',function(){if(busy)return;busy=true;var box=$('om-box'),p=$('om-paper');p.classList.remove('on');box.classList.remove('out');void box.offsetWidth;box.classList.add('shake');
 setTimeout(function(){box.classList.remove('shake');box.classList.add('out');
  var L=lot(),nm=L[0],bd=L[3],no=1+rnd(100),rows=IO.map(function(k){return '<tr><th scope="row">'+esc(k)+'</th><td>'+esc(pick(IT[k][bd]))+'</td></tr>'}).join('');
  p.innerHTML='<div class="fh-b27-om-no">第 '+no+' 番</div><div class="fh-b27-om-lv" style="color:'+BC[bd][1]+'">'+esc(nm)+'</div><div class="fh-b27-om-band" style="background:'+BC[bd][1]+'">'+esc(BC[bd][0])+'（12段階の'+(LV.map(function(x){return x[0]}).indexOf(nm)+1)+'番目）</div>'
   +'<p class="fh-b27-om-sum">'+esc(pick(SM[nm]))+'</p><table class="fh-b27-om-items"><tbody>'+rows+'</tbody></table>'
   +'<div class="fh-b27-om-lucky"><span>方角：'+esc(pick(LD))+'</span><span>色：'+esc(pick(LC))+'</span><span>時間：'+esc(pick(LT))+'</span></div>';
  p.hidden=false;setTimeout(function(){p.classList.add('on')},30);
  ['good','mid','bad'].forEach(function(k){var e=$('om-ad-'+k);if(e)e.hidden=(k!==bd)});$('om-ads').hidden=false;
  $('om-go').textContent='もう一度引く';busy=false;
  setTimeout(function(){p.scrollIntoView({behavior:'smooth',block:'start'})},400);
 },1100);});
})();"""


def build(sample, updated):
    H = [CSS]
    a = H.append
    a('<div class="fh-b27" data-fh-page="omikuji">\n<div class="fh-b27-note">')
    a('''<header class="fh-b27-hero">
  <div class="fh-b27-om-box" aria-hidden="true"><i></i></div>
  <div class="fh-b27-hero-body">
    <span class="fh-b27-tape">人生予報 おみくじ</span>
    <h1 class="fh-b27-title">おみくじ<br>12段階の吉凶と10の項目で今日を占う</h1>
    <p class="fh-b27-lead">大吉から大凶までの12段階の吉凶に、願望・待人・失物・旅行・商売・学問・争事・恋愛・縁談・病気の10項目の言葉がつく、神社のおみくじのような無料のおみくじです。言葉の組み合わせは引くたびに変わります。</p>
  </div>
</header>''')
    items = [("b27-om-draw", "おみくじを引く"), ("b27-om-order", "12段階の吉凶の順番"), ("b27-om-items", "項目の読み方"),
             ("b27-om-after", "引いたおみくじはどうする？"), ("b27-om-faq", "よくある質問")]
    a('<nav class="fh-b27-toc" aria-label="目次"><strong>このページの内容</strong><ol>' + "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in items) + "</ol></nav>")
    n = [0]

    def h2(t):
        n[0] += 1
        return f'<h2><span class="fh-b27-n">{n[0]}</span><span>{t}</span></h2>'

    lead = "引いた運勢に合わせて、身につけたり飾ったりできる開運アイテムを選びました。楽天・Yahoo!ショッピングの商品ページへ移ります。"
    ads = ""
    for k, cat in (("good", "good"), ("mid", "normal"), ("bad", "bad")):
        c = CATS[cat]
        ads += f'<div id="om-ad-{k}" hidden>' + AX.goods_box(c["title"], [x + ("omamori",) for x in c["items"]], lead=lead) + "</div>"
    a(f'''<section class="fh-b27-sec" id="b27-om-draw">
  {h2("おみくじを引く")}
  <div class="fh-b27-om-stage">
    <div class="fh-b27-om-box" id="om-box" aria-hidden="true"><i></i></div>
    <p style="margin:0;font-size:14px;color:#5A4E45">心を静めて、今日のことを思い浮かべてから引いてください。</p>
    <button type="button" class="fh-b27-om-go" id="om-go">おみくじを引く</button>
    <div class="fh-b27-om-paper" id="om-paper" aria-live="polite" hidden></div>
    <div class="fh-b27-om-ads" id="om-ads" hidden>{ads}</div>
  </div>
</section>''')
    rows = "".join(f'<tr><td>{i + 1}</td><td><b>{esc(nm)}</b>（{esc(yomi)}）</td><td>{esc(BAND[bd][0])}</td><td>{pct}%</td></tr>' for i, (nm, yomi, pct, bd) in enumerate(O.LEVELS))
    assert sum(x[2] for x in O.LEVELS) == 100
    a(f'''<section class="fh-b27-sec" id="b27-om-order">
  {h2("12段階の吉凶の順番")}
  <p>大きな神社やお寺のおみくじには、大吉・吉・凶だけでなく、半吉や末小吉、小凶など、たくさんの段階があります。順番は社寺によって違い、「吉」を「中吉」より上にするところもあります。このページのおみくじは、次の12段階の順番と出やすさで作っています。</p>
  <table class="fh-b27-om-tbl"><thead><tr><th>順</th><th>吉凶</th><th>分け方</th><th>出やすさ</th></tr></thead><tbody>{rows}</tbody></table>
  <p>「末」がつくものは「今はまだでも、後でよくなる（悪くなる）」、「半」がつくものは「よいことと気がかりが半分ずつ」という意味で読まれます。順番よりも、書かれている言葉の中身を大切にするのがおみくじの楽しみ方です。</p>
</section>''')
    ex = {"願望": "いま心の中で願っていることが、どう進みそうか", "待人": "会いたい人や、助けてくれる人が来るかどうか", "失物": "なくした物が見つかるかどうか、どのあたりを探すとよいか",
          "旅行": "旅や外出、引っ越しなどの移動の運", "商売": "仕事やお金のやりとり、取引の運", "学問": "勉強や試験、学び事の進み方",
          "争事": "もめごとや勝負ごとをどう収めるとよいか", "恋愛": "恋の進み方や、相手との向き合い方", "縁談": "結婚や、人との大きなご縁の話",
          "病気": "体の調子の整え方（気になる症状があるときは必ず医療機関へ）"}
    ir = "".join(f'<tr><td><b>{esc(k)}</b></td><td>{esc(ex[k])}</td></tr>' for k in O.ITEM_ORDER)
    a(f'''<section class="fh-b27-sec" id="b27-om-items">
  {h2("項目の読み方")}
  <p>神社やお寺のおみくじには、吉凶のほかに、暮らしのいろいろな場面についての短い言葉が書かれています。このページのおみくじにも、次の10の項目がつきます。</p>
  <table class="fh-b27-om-tbl"><thead><tr><th>項目</th><th>何についての言葉か</th></tr></thead><tbody>{ir}</tbody></table>
  <p>吉凶が同じでも、項目ごとの言葉はさまざまです。大吉でも「欲張らず」と書かれていたり、凶でも「季節が変われば便りあり」と書かれていたりします。いちばん気になっている項目の言葉を、今日のヒントにしてください。</p>
</section>''')
    a(f'''<section class="fh-b27-sec" id="b27-om-after">
  {h2("引いたおみくじはどうする？")}
  <p>神社やお寺で引いたおみくじは、境内の「おみくじ掛け」に結んで帰っても、持ち帰ってお守りのように手元に置いてもかまいません。よくない結果を結んで帰り、よい結果は持ち帰って読み返す、という人も多くいます。木の枝に結ぶと木が傷むため、結ぶ場所を決めている社寺もあります。結ぶときは、決められた場所に結びましょう。</p>
  <p>おみくじの始まりには諸説あり、平安時代の僧・良源（元三大師）にちなむ「観音籤（かんのんくじ）」が、今のおみくじのもとのひとつと言われています。昔の人も、迷ったときにくじを引いて、心を決めるきっかけにしていました。</p>
</section>''')
    qa = "".join(f'<details{" open" if i == 0 else ""}><summary>Q. {esc(q)}</summary><p>A. {esc(x)}</p></details>' for i, (q, x) in enumerate(O.FAQ))
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in O.FAQ]}
    a(f'''<section class="fh-b27-sec" id="b27-om-faq">
  {h2("よくある質問")}
  <div class="fh-b27-om-qa">{qa}</div>
</section>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<section class="fh-b27-sec" id="b27-om-more">
  <div class="fh-b27-links">
    <a href="/tarot/"><b>タロット占い →</b><small>悩みを相談して答えをもらう</small></a>
    <a href="/coin/"><b>コイン占い →</b><small>表と裏で今日の運勢を</small></a>
    <a href="/hoshi/"><b>星のこよみ2027 →</b><small>新月・満月・逆行の日付</small></a>
    <a href="/366uranai/"><b>366日の誕生日占い →</b><small>誕生日ごとの2027年の運勢</small></a>
  </div>
</section>''')
    js = (JS.replace("__LV__", json.dumps(O.LEVELS, ensure_ascii=False)).replace("__SM__", json.dumps(O.SUMMARY, ensure_ascii=False))
          .replace("__IT__", json.dumps(O.ITEMS, ensure_ascii=False)).replace("__IO__", json.dumps(O.ITEM_ORDER, ensure_ascii=False))
          .replace("__LD__", json.dumps(O.LUCKY_DIR, ensure_ascii=False)).replace("__LC__", json.dumps(O.LUCKY_COLOR, ensure_ascii=False))
          .replace("__LT__", json.dumps(O.LUCKY_TIME, ensure_ascii=False)).replace("__BC__", json.dumps(BAND, ensure_ascii=False)))
    assert not re.findall(r"\[(sp|pc|tab|mobile)\]", js) and "<img" not in js
    assert not re.search(r"[\U0001F000-\U0001FFFF]", js)
    up = dt.date.fromisoformat(updated)
    a(f'<p class="fh-b27-foot">このおみくじは、気軽に今日の運勢を楽しむためのものです。吉凶の段階や言葉は、社寺のおみくじによく見られる形をもとに、このサイトで書いたもので、特定の神社やお寺のおみくじとは関係ありません。'
      f'最終更新日：{up.year}年{up.month}月{up.day}日／<a href="/about/">この記事の作成方針について</a></p>')
    a("</div>\n</div>")
    a(f"<script>document.addEventListener('DOMContentLoaded',function(){{{js}}});</script>")
    title = "おみくじ【無料】12段階の吉凶と10項目で今日の運勢｜大吉〜大凶・願望・待人・恋愛・商売"
    desc = ("大吉から大凶までの12段階の吉凶に、願望・待人・失物・旅行・商売・学問・争事・恋愛・縁談・病気の10項目の言葉がつく無料のおみくじ。"
            "引くたびに言葉の組み合わせが変わります。吉凶の順番、項目の読み方、引いたおみくじの扱い方も紹介します。")
    out = shell(title, desc, URL, "\n".join(H), sample)
    assert "！" not in out and "動物占い" not in out
    return out


def main():
    updated = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    for sample, path in ((False, os.path.join(OUT, "omikuji.html")), (True, os.path.join(OUT, "sample", "omikuji.html"))):
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(build(sample, updated))
        print("→", os.path.relpath(path, WORK))


if __name__ == "__main__":
    main()
