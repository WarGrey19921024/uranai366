"""生年月日まるごと診断（新しい固定ページ /seinengappi/）を作る。

使い方:
  python work/scripts/build_html.py --sample 0101   # 共通CSS/JS（fh-b27.css・fh-b27.js ほか）を先に作る
  python work/scripts/build_seinengappi.py

出力:
  work/out/seinengappi.html          投入用。<!-- fh-b27:start --> 〜 <!-- fh-b27:end --> の中身（[no_toc] ＋ カスタムHTMLブロック）を
                                     新しい固定ページ（スラッグ seinengappi・親なし）の本文に貼る
  work/out/sample/seinengappi.html   確認用（共通CSS/JSを ../assets/ から読む）
  work/out/assets/fh-b27-sign.js     太陽が星座を移る日時（日本時間）1930〜2030年。各年12個 × "DDhhmm"（1月＝水瓶座入り … 12月＝山羊座入り）。
                                     calc_sekki.py の crossings（太陽の視黄経が30度の倍数を通る時刻）で計算

しくみ:
  生年月日（1930〜2030年＝節入り・旧暦の表の範囲）を選ぶと、共通JS fh-b27.js の計算（FHB27Calc：honmei・pillars・shuku・kin・
  lifePath・animal・sunSign）で、星座・九星・干支・四柱推命・宿曜・マヤ暦・数秘・動物×色を1枚のカードに出す。
  表示の処理も fh-b27.js の bootSeinen（<div class="fh-b27" data-fh-page="seinengappi"> のときだけ動く）。計算をこのページで書き直さない。
  生年月日は送信・保存しない（ページの中だけで計算）。
読み込むJS（この順）: fh-b27-setsuiri.js → fh-b27-kyureki.js → fh-b27-sign.js → fh-b27.js
"""
import datetime as dt, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_hub import OUT, WORK, esc, shell  # noqa: E402
from calc_sekki import crossings  # noqa: E402
from common import jst_from_jd  # noqa: E402

URL = "/seinengappi/"
Y0, Y1 = 1930, 2030
SCRIPTS = ("fh-b27-setsuiri.js", "fh-b27-kyureki.js", "fh-b27-sign.js", "fh-b27.js")
# 黄経（度）→ その星座に入る月（30度＝牡牛座入りは4月 …）
SIGN_MONTH = {300: 1, 330: 2, 0: 3, 30: 4, 60: 5, 90: 6, 120: 7, 150: 8, 180: 9, 210: 10, 240: 11, 270: 12}


def sign_table():
    rows = {}
    for deg, jd in crossings(Y0, Y1, step_deg=30):
        t = jst_from_jd(jd)
        m = SIGN_MONTH[deg]
        assert t.month == m, (deg, t)
        rows.setdefault(t.year, {})[m] = t.strftime("%d%H%M")
    out = []
    for y in range(Y0, Y1 + 1):
        r = rows[y]
        assert sorted(r) == list(range(1, 13)), (y, sorted(r))
        out.append("".join(r[m] for m in range(1, 13)))
    return out


def write_sign_js(rows):
    path = os.path.join(OUT, "assets", "fh-b27-sign.js")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"/* 太陽が星座を移る日時（日本時間）{Y0}〜{Y1}年。各年 1月（水瓶座入り）〜12月（山羊座入り）の順に DDhhmm。"
                "生年月日まるごと診断（/seinengappi/）用。出典: 天文計算（work/scripts/calc_sekki.py の crossings、build_seinengappi.py が出力）*/\n")
        f.write("window.FH_B27_SIGN=" + json.dumps({"y0": Y0, "d": rows}, separators=(",", ":")) + ";\n")
    return path


def res_box(key, label, link=None, wide=False, icon=None, extra=""):
    """結果の箱：アイコン・ラベル・結果・計算の注記（-n）・タイプの短い解説（-d、type_texts.json を共通JSが入れる）"""
    a = f'<a id="fh-b27-sg-{key}-a" href="{link[0]}">{esc(link[1])}</a>' if link else ""
    cls = ' class="fh-b27-wide"' if wide else ""
    ic = f'<i class="fh-b27-ic fh-b27-ic-{icon} fh-b27-resic" aria-hidden="true"></i>' if icon else ""
    return (f'    <div{cls}>{ic}<small>{esc(label)}</small><b id="fh-b27-sg-{key}">—</b>'
            f'<p class="fh-b27-sg-desc" id="fh-b27-sg-{key}-d"></p>{extra}'
            f'<span id="fh-b27-sg-{key}-n"></span>{a}</div>')


CARD_ROWS = [("sign", "星座"), ("star", "九星"), ("eto", "干支"), ("pillars", "四柱推命"), ("nikkan", "日干"),
             ("shuku", "宿曜"), ("kin", "マヤ暦"), ("seal", "紋章・音"), ("lp", "ライフパス"), ("animal", "動物×色")]


SG_CSS = '<style>\n.fh-b27[data-fh-page="seinengappi"] .fh-b27-hero{position:relative;overflow:hidden}\n.fh-b27-sg-orbit{position:absolute;right:-30px;top:50%;width:230px;height:230px;margin-top:-115px;pointer-events:none;opacity:.9}\n.fh-b27-sg-orbit:before{content:"";position:absolute;inset:28px;border:1px dashed rgba(232,199,106,.45);border-radius:50%}\n.fh-b27-sg-orbit>div{position:absolute;inset:0;animation:fh-sg-rot 40s linear infinite}\n.fh-b27-sg-orbit i{position:absolute;left:50%;top:50%;width:34px;height:34px;margin:-17px;transform:rotate(calc(var(--k)*45deg)) translateY(-87px) rotate(calc(var(--k)*-45deg))}\n.fh-b27-sg-orbit i b{display:grid;place-items:center;width:100%;height:100%;border-radius:50%;background:var(--c);color:#fff;font:800 15px \'Shippori Mincho\',serif;box-shadow:0 0 14px var(--c);animation:fh-sg-rot 40s linear infinite reverse}\n@keyframes fh-sg-rot{to{transform:rotate(360deg)}}\n.fh-b27[data-fh-page="seinengappi"] .fh-b27-hero-body{position:relative;z-index:1}\n@media (max-width:640px){.fh-b27-sg-orbit{width:170px;height:170px;top:10px;margin-top:0;right:-50px;opacity:.28}.fh-b27-sg-orbit i{transform:rotate(calc(var(--k)*45deg)) translateY(-62px) rotate(calc(var(--k)*-45deg))}}\n.fh-b27-sg-rit{position:fixed;inset:0;z-index:99999;display:none;place-items:center;background:radial-gradient(circle at 50% 45%,rgba(40,30,70,.96),rgba(8,8,20,.98));color:#F6E7BC}\n.fh-b27-sg-rit.on{display:grid;animation:fh-sg-fade .3s both}\n.fh-b27-sg-rit.off{animation:fh-sg-out .5s both}\n@keyframes fh-sg-fade{from{opacity:0}}@keyframes fh-sg-out{to{opacity:0;transform:scale(1.08)}}\n.fh-b27-sg-rit-in{position:relative;width:280px;height:280px}\n.fh-b27-sg-rit ul{list-style:none;margin:0;padding:0;position:absolute;inset:0;animation:fh-sg-rot 6s linear infinite}\n.fh-b27-sg-rit li{position:absolute;left:50%;top:50%;width:54px;height:54px;margin:-27px;transform:rotate(calc(var(--k)*45deg)) translateY(-112px) rotate(calc(var(--k)*-45deg));opacity:.25;transition:opacity .2s}\n.fh-b27-sg-rit li b{display:grid;place-items:center;width:54px;height:54px;border-radius:50%;border:2px solid var(--c);color:var(--c);font:800 20px \'Shippori Mincho\',serif;background:rgba(0,0,0,.4);animation:fh-sg-rot 6s linear infinite reverse}\n.fh-b27-sg-rit li span{position:absolute;left:50%;top:58px;transform:translateX(-50%);white-space:nowrap;font-size:11px;color:#E8D9B8;animation:fh-sg-rot 6s linear infinite reverse}\n.fh-b27-sg-rit li.lit{opacity:1}.fh-b27-sg-rit li.lit b{background:var(--c);color:#fff;box-shadow:0 0 22px var(--c)}\n.fh-b27-sg-rit-c{position:absolute;left:50%;top:50%;width:150px;margin-left:-75px;transform:translateY(-50%);text-align:center}\n.fh-b27-sg-rit-c small{display:block;font-size:12px;color:#C9B98F;letter-spacing:.2em}\n.fh-b27-sg-rit-c b{display:block;font:800 22px \'Shippori Mincho\',serif;margin:6px 0}\n.fh-b27-sg-rit-c em{display:block;font-style:normal;font-size:13px;min-height:1.6em;color:#F6E7BC}\n.fh-b27-sg-rit-flash{position:absolute;inset:-60px;border-radius:50%;background:radial-gradient(circle,rgba(255,244,200,.95),rgba(255,244,200,0) 60%);opacity:0}\n.fh-b27-sg-rit.flash .fh-b27-sg-rit-flash{animation:fh-sg-flash .6s both}\n@keyframes fh-sg-flash{50%{opacity:1}to{opacity:0;transform:scale(1.6)}}\n.fh-b27-sg-out.fh-sg-show .fh-b27-sg-card{animation:fh-sg-card .9s cubic-bezier(.2,.8,.2,1) both}\n@keyframes fh-sg-card{from{opacity:0;transform:perspective(900px) rotateY(-80deg) scale(.9)}}\n.fh-b27-sg-card{position:relative;overflow:hidden}\n.fh-b27-sg-out.fh-sg-show .fh-b27-sg-card:after{content:"";position:absolute;top:-50%;left:-60%;width:40%;height:200%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.55),transparent);transform:rotate(20deg);animation:fh-sg-shine 1.4s .8s both}\n@keyframes fh-sg-shine{to{left:130%}}\n.fh-b27-sg-out.fh-sg-show .fh-b27-sg-card dl>div{animation:fh-sg-up .5s both;animation-delay:calc(.7s + var(--i)*.09s)}\n.fh-b27-sg-out.fh-sg-show .fh-b27-res>div{animation:fh-sg-up .6s both;animation-delay:calc(.2s + var(--i)*.08s)}\n@keyframes fh-sg-up{from{opacity:0;transform:translateY(16px)}}\n.fh-b27[data-fh-page="seinengappi"] .fh-b27-res>div{border-top:4px solid var(--c,#E8C76A)}\n.fh-b27[data-fh-page="seinengappi"] #b27-more .fh-b27-links{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}\n.fh-b27[data-fh-page="seinengappi"] #b27-more .fh-b27-links a{position:relative;padding-left:52px;border-left:4px solid var(--c,#E8C76A);background:linear-gradient(90deg,color-mix(in srgb,var(--c,#E8C76A) 18%,transparent),transparent 70%)}\n.fh-b27[data-fh-page="seinengappi"] #b27-more .fh-b27-links a i{position:absolute;left:10px;top:50%;margin-top:-16px;width:32px;height:32px;border-radius:50%;display:grid;place-items:center;background:var(--c,#E8C76A);color:#fff;font:800 14px \'Shippori Mincho\',serif;font-style:normal}\n@media (max-width:640px){.fh-b27[data-fh-page="seinengappi"] #b27-more .fh-b27-links{grid-template-columns:1fr}}\n@media (prefers-reduced-motion:reduce){.fh-b27-sg-orbit>div,.fh-b27-sg-orbit i b,.fh-b27-sg-rit ul,.fh-b27-sg-rit li b,.fh-b27-sg-rit li span{animation:none}}\n</style>'
SG_JS = '<script>(function(){var go=document.getElementById(\'fh-b27-sg-go\'),out=document.getElementById(\'fh-b27-sg-out\');if(!go||!out)return;\nvar R=document.createElement(\'div\');R.className=\'fh-b27-sg-rit\';R.setAttribute(\'aria-hidden\',\'true\');R.innerHTML=\'<div class="fh-b27-sg-rit-in"><div class="fh-b27-sg-rit-flash"></div><ul><li style="--k:0;--c:#E8A23A"><b>♈︎</b><span>星座</span></li><li style="--k:1;--c:#C2453A"><b>九</b><span>九星</span></li><li style="--k:2;--c:#6E9A4B"><b>干</b><span>干支</span></li><li style="--k:3;--c:#8C6BB1"><b>柱</b><span>四柱推命</span></li><li style="--k:4;--c:#4B6FB5"><b>宿</b><span>宿曜</span></li><li style="--k:5;--c:#2E9C8E"><b>◈</b><span>マヤ暦</span></li><li style="--k:6;--c:#D46A8C"><b>数</b><span>数秘</span></li><li style="--k:7;--c:#B88A3E"><b>動</b><span>動物×色</span></li></ul><div class="fh-b27-sg-rit-c"><small>READING</small><b id="fh-sg-rit-d"></b><em id="fh-sg-rit-t">8つの星を読んでいます</em></div></div>\';document.body.appendChild(R);\nvar L=R.querySelectorAll(\'li\'),busy=false,red=window.matchMedia&&window.matchMedia(\'(prefers-reduced-motion: reduce)\').matches;\nfunction idx(){[].forEach.call(document.querySelectorAll(\'.fh-b27-sg-card dl>div\'),function(e,i){e.style.setProperty(\'--i\',i)});[].forEach.call(document.querySelectorAll(\'#b27-detail .fh-b27-res>div\'),function(e,i){e.style.setProperty(\'--i\',i);var C=[\'#C2453A\',\'#E8A23A\',\'#6E9A4B\',\'#8C6BB1\',\'#4B6FB5\',\'#2E9C8E\',\'#D46A8C\',\'#B88A3E\',\'#E8C76A\'];e.style.setProperty(\'--c\',C[i%C.length])});}\nidx();\ngo.addEventListener(\'click\',function(){var y=document.getElementById(\'fh-b27-sg-y\'),m=document.getElementById(\'fh-b27-sg-m\'),d=document.getElementById(\'fh-b27-sg-d\');if(busy||!y.value||!m.value||!d.value)return;\n out.classList.remove(\'fh-sg-show\');if(red){out.classList.add(\'fh-sg-show\');return;}\n busy=true;out.style.visibility=\'hidden\';document.getElementById(\'fh-sg-rit-d\').textContent=y.value+\'.\'+m.value+\'.\'+d.value;\n [].forEach.call(L,function(x){x.classList.remove(\'lit\')});R.classList.remove(\'off\',\'flash\');R.classList.add(\'on\');\n var t=document.getElementById(\'fh-sg-rit-t\');[].forEach.call(L,function(x,i){setTimeout(function(){x.classList.add(\'lit\');t.textContent=x.querySelector(\'span\').textContent+\'を読んでいます\';},250+i*230);});\n setTimeout(function(){t.textContent=\'あなたのカードができました\';R.classList.add(\'flash\');},250+L.length*230+150);\n setTimeout(function(){R.classList.add(\'off\');out.style.visibility=\'\';void out.offsetWidth;out.classList.add(\'fh-sg-show\');var c=document.querySelector(\'.fh-b27-sg-cardwrap\');if(c&&c.scrollIntoView)c.scrollIntoView({block:\'start\'});},250+L.length*230+700);\n setTimeout(function(){R.classList.remove(\'on\',\'off\',\'flash\');busy=false;},250+L.length*230+1250);},true);\n})();</script>'


def build(sample, updated):
    H = []
    a = H.append
    a(SG_CSS)
    a('<div class="fh-b27" data-fh-page="seinengappi">\n<div class="fh-b27-note">')
    a('''<header class="fh-b27-hero">
  <div class="fh-b27-sg-orbit" aria-hidden="true"><div><i style="--k:0;--c:#E8A23A"><b>♈︎</b></i><i style="--k:1;--c:#C2453A"><b>九</b></i><i style="--k:2;--c:#6E9A4B"><b>干</b></i><i style="--k:3;--c:#8C6BB1"><b>柱</b></i><i style="--k:4;--c:#4B6FB5"><b>宿</b></i><i style="--k:5;--c:#2E9C8E"><b>◈</b></i><i style="--k:6;--c:#D46A8C"><b>数</b></i><i style="--k:7;--c:#B88A3E"><b>動</b></i></div></div>
  <div class="fh-b27-kou" aria-hidden="true">生年月日</div>
  <div class="fh-b27-hero-body">
    <span class="fh-b27-tape">人生予報 まるごと診断</span>
    <p class="fh-b27-title">生年月日まるごと診断<br>8つの占いを1枚のカードに</p>
    <p class="fh-b27-lead">生年月日を選ぶだけで、星座・九星・干支・四柱推命・宿曜・マヤ暦・数秘・動物×色の8つの占いの結果を、1枚のカードにまとめて表示します。気になった占いは、それぞれのページでくわしく読めます。</p>
  </div>
</header>''')
    a(f'''<section class="fh-b27-sec" id="b27-input">
  <h2><span class="fh-b27-n">1</span>生年月日を選ぶ</h2>
  <div class="fh-b27-yearbar">
    <div class="fh-b27-sg-form">
      <label class="fh-b27-sg-yl" for="fh-b27-sg-y">生まれた年<select id="fh-b27-sg-y" data-fh-sg="y"></select></label>
      <label for="fh-b27-sg-m">月<select id="fh-b27-sg-m" data-fh-sg="m"></select></label>
      <label for="fh-b27-sg-d">日<select id="fh-b27-sg-d" data-fh-sg="d"></select></label>
      <button type="button" class="fh-b27-btn" id="fh-b27-sg-go">診断する</button>
    </div>
    <p class="fh-b27-small">選べるのは{Y0}〜{Y1}年です。<b>生年月日は送信も保存もしません</b>（このページの中だけで計算します）。生まれた時刻はわからないものとして、正午（日本時間）に生まれたとして計算します。</p>
  </div>
  <noscript><p class="fh-b27-small">この診断はJavaScriptで計算します。ブラウザの設定でJavaScriptを有効にしてください。</p></noscript>
</section>''')
    a('<div class="fh-b27-sg-out" id="fh-b27-sg-out" hidden>')
    a('''<div class="fh-b27-cardwrap fh-b27-sg-cardwrap">
  <div class="fh-b27-card-outer">
    <div class="fh-b27-card fh-b27-sg-card">
      <div class="fh-b27-card-top"><span class="fh-b27-hand">生年月日まるごとカード</span><span>人生予報</span></div>
      <div class="fh-b27-card-name"><span class="fh-b27-d" id="fh-b27-sg-date">—</span></div>
      <span class="fh-b27-sub" id="fh-b27-sg-sub"></span>
      <dl>''')
    for k, lab in CARD_ROWS:
        a(f'        <div><dt>{lab}</dt><dd id="fh-b27-sg-c-{k}">—</dd></div>')
    a('''      </dl>
      <button type="button" class="fh-b27-btn" data-fh-action="save-sg">カードを画像で保存</button>
    </div>
  </div>
</div>''')
    a('''<a class="fh-b27-promo" id="fh-b27-sg-day" href="/366uranai/">
  <small>この誕生日のページへ</small>
  <b id="fh-b27-sg-day-t">誕生日占い（2027年版）</b>
  <span>性格・相性・誕生花と誕生石、2027年の月ごとの運勢とグラフ、バイオリズムまで。</span>
</a>''')
    a('''<section class="fh-b27-sec" id="b27-detail">
  <h2><span class="fh-b27-n">2</span>ひとつずつ、くわしく</h2>
  <div class="fh-b27-res">''')
    a(res_box("star", "本命星（九星気学）", ("/kyusei/", "九星気学のページで、本命星の性格と2027年の運勢・年盤を見る →"), wide=True, icon="kyusei",
              extra='<p class="fh-b27-sg-y27"><span>2027年のひとこと</span><em id="fh-b27-sg-star-y"></em></p>'
                    '<a href="/kaiun/compass/">本命星の吉方位を8方位の読み方で見る →</a>'))
    a(res_box("sign", "星座（西洋占星術）", ("/366uranai/", "星座のページを見る →"), icon="aries"))
    a(res_box("eto", "生まれ年の干支", icon="eto"))
    a(res_box("pillars", "四柱推命（年柱・月柱・日柱）", icon="shichu"))
    a(res_box("shuku", "宿曜（本命宿）", ("/shukuyo/", "宿曜占星術のページで、27宿の性格と相性を見る →"), icon="shuku"))
    a(res_box("kin", "マヤ暦（ドリームスペル）", ("/maya/", "マヤ暦のページで、紋章と音の意味を見る →"), icon="maya"))
    a(res_box("lp", "数秘術（ライフパス）", icon="suhi"))
    a('''    <div><i class="fh-b27-ic fh-b27-ic-animal fh-b27-resic" aria-hidden="true"></i><small>動物×色占い</small><b id="fh-b27-sg-animal">—</b><p class="fh-b27-sg-desc" id="fh-b27-sg-animal-d"></p><span>12の動物×5つの色＝60タイプの、このサイト独自の占いです。</span><a href="/animal-color/">60タイプの性格を見る →</a></div>''')
    a('''    <div class="fh-b27-wide"><small>もっと知りたい人へ</small><span>干支・四柱推命・宿曜・マヤ暦・数秘の意味と、2027年のあなたの運勢は、誕生日のページで生まれ年を選ぶと読めます。</span><a id="fh-b27-sg-day-a" href="/366uranai/">誕生日のページを見る →</a></div>''')
    a('''  </div>
</section>''')
    a('</div>')
    a(SG_JS)
    a("<!--Ads1-->")
    a('''<section class="fh-b27-sec" id="b27-more">
  <h2><span class="fh-b27-n">3</span>あわせて占う</h2>
  <div class="fh-b27-links">
    <a href="/366uranai/" style="--c:#E8A23A"><i aria-hidden="true">誕</i><b>366日の誕生日占い</b><small>誕生日から性格と2027年の運勢を見る</small></a>
    <a href="/compatibility/" style="--c:#D46A8C"><i aria-hidden="true">♡︎</i><b>誕生日相性占い</b><small>2人の生年月日で相性を見る</small></a>
    <a href="/kyusei/" style="--c:#C2453A"><i aria-hidden="true">九</i><b>九星気学</b><small>本命星と2027年の運勢・年盤</small></a>
    <a href="/shukuyo/" style="--c:#4B6FB5"><i aria-hidden="true">宿</i><b>宿曜占星術</b><small>本命宿と三九の秘法の相性</small></a>
    <a href="/maya/" style="--c:#2E9C8E"><i aria-hidden="true">◈</i><b>マヤ暦占い</b><small>KIN・太陽の紋章・銀河の音</small></a>
    <a href="/birthstone/" style="--c:#8C6BB1"><i aria-hidden="true">石</i><b>誕生石一覧</b><small>1月〜12月の誕生石と366日の誕生日石</small></a>
    <a href="/enmusubi/pair/" style="--c:#D46A8C"><i aria-hidden="true">縁</i><b>ご縁の相性診断</b><small>縁結び診断室</small></a>
    <a href="/animal-color/" style="--c:#B88A3E"><i aria-hidden="true">動</i><b>動物×色占い</b><small>生年月日で60タイプ</small></a>
    <a href="/mbti/" style="--c:#4B6FB5"><i aria-hidden="true">M</i><b>MBTI占い</b><small>性格タイプで見る2027年</small></a>
    <a href="/mbti-compatibility/" style="--c:#8C6BB1"><i aria-hidden="true">相</i><b>MBTI相性占い</b><small>性格タイプどうしの相性</small></a>
    <a href="/kokoro/" style="--c:#6E9A4B"><i aria-hidden="true">心</i><b>心コンパス</b><small>エニアグラム・ビッグファイブで性格を深く知る</small></a>
    <a href="/kaiun/compass/" style="--c:#C2453A"><i aria-hidden="true">方</i><b>8方位の読み方</b><small>開運ライフ｜本命星の吉方位に</small></a>
    <a href="/dream/" style="--c:#2E9C8E"><i aria-hidden="true">夢</i><b>夢解き図鑑</b><small>気になる夢の意味を調べる</small></a>
  </div>
</section>''')
    a(f'''<section class="fh-b27-about" id="b27-about">
  <h3>この診断について</h3>
  <ul>
    <li><b>計算のしかた：</b>星座・節入り・旧暦は、天文計算で求めた日時（日本時間）をもとにしています。生まれた時刻はわからないので、正午に生まれたとして計算します。</li>
    <li><b>星座：</b>太陽が星座を移る日は年によって違うため、生まれた年の実際の日時で判定します。移る日に生まれた人は、時刻によって隣の星座になることがあります。</li>
    <li><b>九星・干支・四柱推命：</b>九星気学と四柱推命は立春で年が、節入り（立春・啓蟄など）で月が切り替わります。立春より前に生まれた人は前年の星・干支になります。ふだんの干支は1月1日で切り替えて表示しています。</li>
    <li><b>宿曜：</b>旧暦の月日と『宿曜経』の「各月1日の宿」の表から本命宿を出しています。</li>
    <li><b>マヤ暦：</b>ドリームスペル方式（2013年7月26日＝KIN164を基準に、2月29日は数えない）です。古代マヤの暦そのものとは別物です。</li>
    <li><b>数秘術：</b>ライフパスは生年月日の数字をすべて足して1けたにする方式です（11・22・33は残します）。流派によって数が違うことがあります。</li>
    <li><b>動物×色占い：</b>当サイト独自の60タイプです。</li>
    <li><b>タイプの解説：</b>本命星・干支・日干・宿・マヤの紋章と音・ライフパスの短い解説は、それぞれの占いで一般に言われる性質をもとに当サイトがまとめたものです。動物×色の解説は、動物の解説に色の解説を重ねた当サイト独自の文です。2027年のひとことは、2027年（九紫火星が中宮の年）の年盤で本命星が入る方位から読んでいます。</li>
    <li><b>選べる年：</b>{Y0}〜{Y1}年（節入りと旧暦の表を用意している範囲）です。生年月日は送信も保存もしません。</li>
  </ul>
</section>''')
    up = dt.date.fromisoformat(updated)
    a(f'<p class="fh-b27-foot">この診断は、西洋占星術・九星気学・干支・四柱推命・宿曜・マヤ暦・数秘術と、当サイト独自の動物×色占いの計算をまとめたものです。占いの結果として、楽しみと気づきのためにお読みください。<br>'
      f'最終更新日：{up.year}年{up.month}月{up.day}日／<a href="/about/">この記事の作成方針について</a></p>')
    a("</div>\n</div>")
    title = "生年月日まるごと診断｜星座・九星・干支・四柱推命・宿曜・マヤ暦・数秘を1枚に"
    desc = ("生年月日を選ぶだけで、星座・九星（本命星）・干支・四柱推命・宿曜・マヤ暦・数秘（ライフパス）・動物×色の8つの占いを"
            "1枚のカードにまとめて表示。画像で保存もできます。生年月日は送信・保存しません。")
    return shell(title, desc, URL, "\n".join(H), sample, SCRIPTS)


def main():
    updated = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    p = write_sign_js(sign_table())
    print("→", os.path.relpath(p, WORK))
    js = os.path.join(OUT, "assets", "fh-b27.js")
    if not os.path.exists(js) or "bootSeinen" not in open(js, encoding="utf-8").read():
        print("注意: out/assets/fh-b27.js が古い（まるごと診断の処理 bootSeinen が無い）。先に build_html.py を実行してください。")
    for sample, path in ((False, os.path.join(OUT, "seinengappi.html")), (True, os.path.join(OUT, "sample", "seinengappi.html"))):
        with open(path, "w", encoding="utf-8") as f:
            f.write(build(sample, updated))
        print("→", os.path.relpath(path, WORK))


if __name__ == "__main__":
    main()
