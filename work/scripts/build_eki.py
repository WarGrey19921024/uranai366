"""易占いのページ（2026-10-18 新規。検索「易占い」月1万〜10万）。本人「ちゃんと検索されるように作りこみましょう」。
- ハブ /eki/：画面で易を立てる（略筮法）＋易の基本＋八卦＋64卦の早見表と一覧＋FAQ
- 子ページ /eki/NN-romaji/（64）：卦ごとの意味・卦辞と大象・11項目・六爻・関係する卦・FAQ
作る前の確認：同じ内容の既存ページなし（/eki/ /ekisen/ /iching/ などは404、WordPress の検索でも該当なし。2026-10-18）
計算：scripts/calc_eki.py → data/eki_64.json。文章：data/eki_texts/NN.json（このサイトで書いたもの）。規則：knowledge/17_易占いページの規則.md
使い方: python work/scripts/build_eki.py [最終更新日]
出力: out/eki/index.html と out/eki/NN-xxx.html（投入用）、out/sample/eki/（確認用）"""
import datetime as dt, html, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_hub import OUT, WORK, shell  # noqa: E402
import aff_extra as AX  # noqa: E402

D = json.load(open(os.path.join(WORK, "data", "eki_64.json"), encoding="utf-8"))
HX = D["hexagrams"]
TRI = D["trigrams"]
T = {n: json.load(open(os.path.join(WORK, "data", "eki_texts", f"{n:02d}.json"), encoding="utf-8")) for n in range(1, 65)}
THEMES = ['恋愛', '結婚・縁談', '仕事', 'お金', '健康', '人間関係', '願い事', '待ち人', '失せ物', '試験・勉強', '引っ越し・旅行']
JG = {'大いに進んでよい': 'go', '進んでよい': 'go', '慎重に進む': 'care', '待つ': 'wait', '守りに徹する': 'wait'}
POSN = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻']
POSM = ['物事の始まり・足もと', '内側の中心・準備が整う所', '内から外へ出る境目・試される所', '外の世界に入った所・上に近い所', '外側の中心・いちばん力のある所', '行き着いた先・終わりと行き過ぎ']
TRI_ORDER = ['乾', '兌', '離', '震', '巽', '坎', '艮', '坤']  # 先天八卦の順（略筮法の余りの数 1〜8）
GOODS = {
    'go': ('動き出すときに', [('ひとり用の手帳', '2027年の手帳', '進むと決めたら、目標と日付を書き出して。', 'stationery'),
                          ('上質な財布', '上質な財布', '運が開く時期に、受け取るものを大切にしまう財布を。', 'wallet')]),
    'care': ('慎重に進むときに', [('令和9年 運勢暦', '2027年の運勢暦', '吉日や方位を確かめて、動く日を選びたい人へ。', 'book'),
                             ('お守り袋', 'お守り袋', '気を引きしめて進む日の、小さなお守りに。', 'omamori')]),
    'wait': ('待つとき・守るときに', [('しおり付きの文庫本', 'しおり付きの文庫本', '動かない時間は、じっくり読む一冊と。', 'book'),
                               ('水晶 天然石', '浄化用の水晶さざれ', '部屋に置いて、気持ちを静かに整えるお守りに。', 'stone')]),
}
GOODS_EKI = ('易を手もとで立てるなら', [('筮竹 易占い', '筮竹（ぜいちく）', '50本の竹の棒。略筮法も本筮法も、これ1組でできます。', 'star'),
                                  ('易経 本', '易経の本', '64卦の言葉を、原文と訳でじっくり読みたい人へ。', 'book')])
PHONE = ('易の答えを、自分の悩みに当てはめたいときは',
         '易の言葉は短く、読み方に幅があります。出た卦を今の状況にどう当てはめるか迷うときは、占い師に直接たずねてみるのもひとつの方法です。')


def esc(s):
    return html.escape(str(s), quote=True)


def url(h):
    return f"/eki/{h['slug']}/"


def svg(lines, size=64, hl=None, cls="fh-b27-ek-svg"):
    """卦の絵（下から上）。hl は強調する爻の番号（0〜5）"""
    w, gap, hh = 100, 6, 10
    rows = []
    for i, v in enumerate(lines):
        y = (5 - i) * (hh + gap)
        c = ' class="hl"' if hl == i else ""
        rows.append(f'<rect{c} x="0" y="{y}" width="100" height="{hh}" rx="2"/>' if v else
                    f'<rect{c} x="0" y="{y}" width="43" height="{hh}" rx="2"/><rect{c} x="57" y="{y}" width="43" height="{hh}" rx="2"/>')
    return (f'<svg class="{cls}" viewBox="0 0 {w} {6 * hh + 5 * gap}" width="{size}" height="{int(size * 0.9)}" role="img" aria-hidden="true">{"".join(rows)}</svg>')


def tri_svg(k, size=34):
    return svg(TRI[k]["lines"] + [0, 0, 0], size)[:0] + (
        f'<svg class="fh-b27-ek-svg" viewBox="0 0 100 42" width="{size}" height="{int(size * 0.5)}" aria-hidden="true">'
        + "".join((f'<rect x="0" y="{(2 - i) * 16}" width="100" height="10" rx="2"/>' if v else
                   f'<rect x="0" y="{(2 - i) * 16}" width="43" height="10" rx="2"/><rect x="57" y="{(2 - i) * 16}" width="43" height="10" rx="2"/>')
                  for i, v in enumerate(TRI[k]["lines"])) + '</svg>')


def ylabel(h, i):
    return h["yao_src"][i][0]


CSS = """<style id="fh-b27-ek-css">
.fh-b27[data-fh-page="eki"]{--ink:#F1ECE4;--sub:#D8CFC2;--mute:#AFA597;--paper:#1C1A1E;--deep:#151317;--line:#4A4038;--gold:#E0B868;--shu:#D9573B;--cream:#F6F0E4;--cream-ink:#2A2420}
.fh-b27[data-fh-page="eki"] a{color:#F0C98A}
.fh-b27[data-fh-page="eki"] .fh-b27-note{border-left:0;border-radius:24px;background-color:var(--paper);background-image:radial-gradient(circle at 10% 0%,rgba(217,87,59,.14),transparent 40%),radial-gradient(circle at 100% 80%,rgba(224,184,104,.12),transparent 45%);background-size:auto;background-repeat:no-repeat;box-shadow:0 18px 40px rgba(0,0,0,.3)}
.fh-b27[data-fh-page="eki"] .fh-b27-sec>p,.fh-b27[data-fh-page="eki"] .fh-b27-lead{text-shadow:0 1px 2px rgba(0,0,0,.5)}
.fh-b27[data-fh-page="eki"] .fh-b27-tape{transform:none;border-radius:4px;background:var(--shu);color:#fff}
.fh-b27[data-fh-page="eki"] .fh-b27-title{font-family:'Shippori Mincho',serif;font-weight:800;font-size:30px}
.fh-b27[data-fh-page="eki"] h2{font-family:'Shippori Mincho',serif;font-weight:800;font-size:24px}
.fh-b27[data-fh-page="eki"] h3{font-family:'Shippori Mincho',serif;font-weight:800}
.fh-b27[data-fh-page="eki"] h2 .fh-b27-n{border:0;border-radius:4px;background:var(--shu);color:#fff}
.fh-b27[data-fh-page="eki"] .fh-b27-toc{border-style:solid;border-radius:14px;border-color:rgba(224,184,104,.3)}
.fh-b27[data-fh-page="eki"] .fh-b27-toc ol{columns:2;column-gap:28px}
.fh-b27-ek-svg rect{fill:#E9DFCF}.fh-b27-ek-svg rect.hl{fill:#E2664A}
.fh-b27-ek-emb{display:flex;align-items:center;justify-content:center;flex:0 0 auto;width:120px;height:120px;border-radius:50%;background:radial-gradient(circle at 40% 35%,#2C2730,#141216);box-shadow:0 0 0 2px rgba(224,184,104,.35),0 10px 24px rgba(0,0,0,.4)}
.fh-b27-ek-emb .fh-b27-ek-svg{animation:fh-b27-ek-br 4s ease-in-out infinite}
@keyframes fh-b27-ek-br{50%{transform:scale(1.06)}}
.fh-b27-ek-box{border:1.5px solid rgba(224,184,104,.35);border-radius:18px;background:var(--deep);padding:16px;display:flex;flex-direction:column;gap:12px;align-items:center}
.fh-b27-ek-opts{display:flex;flex-wrap:wrap;gap:6px;justify-content:center}
.fh-b27-ek-opts small{width:100%;text-align:center;color:var(--sub);font-size:12.5px}
.fh-b27-ek-opts button{min-height:40px;border-radius:999px;border:1.5px solid rgba(224,184,104,.45);background:transparent;color:var(--sub);font:inherit;font-size:14px;font-weight:700;padding:0 14px;cursor:pointer}
.fh-b27-ek-opts button[aria-pressed="true"]{background:var(--gold);border-color:var(--gold);color:#1C1A1E}
.fh-b27-ek-go{min-height:52px;border:0;border-radius:999px;background:linear-gradient(90deg,#D9573B,#E0B868);color:#1C1A1E;font:inherit;font-weight:800;font-size:17px;padding:0 28px;cursor:pointer}
.fh-b27-ek-q{font-size:13.5px;color:var(--mute);text-align:center;margin:0}
.fh-b27-ek-sticks{display:flex;gap:3px;height:70px;align-items:flex-end;justify-content:center;width:100%}
.fh-b27-ek-sticks i{display:block;width:4px;height:64px;border-radius:2px;background:linear-gradient(#E8D3A6,#B88F52);transition:transform .5s ease}
.fh-b27-ek-sticks.split i.l{transform:translateX(-18px) rotate(-6deg)}.fh-b27-ek-sticks.split i.r{transform:translateX(18px) rotate(6deg)}
.fh-b27-ek-steps{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;width:100%}
.fh-b27-ek-steps div{border:1px solid rgba(224,184,104,.25);border-radius:12px;padding:8px;text-align:center;font-size:13px;color:var(--sub);min-height:62px}
.fh-b27-ek-steps b{display:block;font-size:16px;color:#F6E2B8}
.fh-b27-ek-res{width:100%;display:flex;flex-direction:column;gap:12px}
.fh-b27-ek-card{background:var(--cream);color:var(--cream-ink);border-radius:16px;padding:16px;line-height:1.85;animation:fh-b27-ek-in .6s ease both}
@keyframes fh-b27-ek-in{from{opacity:0;transform:translateY(8px)}}
.fh-b27 .fh-b27-ek-card p,.fh-b27 .fh-b27-ek-card b,.fh-b27 .fh-b27-ek-card small{color:var(--cream-ink)}
.fh-b27 .fh-b27-ek-card a{color:#9A3A22;font-weight:700}
.fh-b27-ek-card .fh-b27-ek-svg rect{fill:#3A3029}.fh-b27-ek-card .fh-b27-ek-svg rect.hl{fill:#D9573B}
.fh-b27-ek-head{display:flex;gap:14px;align-items:center}
.fh-b27-ek-head .nm{font-family:'Shippori Mincho',serif;font-size:22px;font-weight:800;color:#5A2416;line-height:1.3}
.fh-b27-ek-tag{display:inline-block;border-radius:999px;background:#5A2416;color:#fff !important;font-size:12px;font-weight:800;padding:1px 10px;margin:2px 4px 2px 0}
.fh-b27-ek-card p{margin:6px 0}
.fh-b27-ek-tri{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
.fh-b27-ek-tri div{border:1px solid rgba(224,184,104,.25);border-radius:12px;background:var(--deep);padding:10px;font-size:13.5px;line-height:1.7;text-align:center}
.fh-b27-ek-tri b{display:block;font-size:17px;color:#F6E2B8}
.fh-b27-ek-grid{overflow-x:auto}
.fh-b27-ek-grid table{border-collapse:collapse;min-width:620px;width:100%;font-size:13px}
.fh-b27-ek-grid th,.fh-b27-ek-grid td{border:1px solid var(--line);padding:6px 4px;text-align:center}
.fh-b27-ek-grid td a{display:block;text-decoration:none;line-height:1.4}
.fh-b27-ek-grid td small{display:block;color:var(--mute);font-size:11px}
.fh-b27-ek-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.fh-b27-ek-list a{display:flex;gap:10px;align-items:center;border:1px solid rgba(224,184,104,.22);border-radius:12px;background:var(--deep);padding:8px 12px;text-decoration:none;color:var(--ink);font-size:14px;line-height:1.6}
.fh-b27-ek-list a b{color:#F6E2B8}.fh-b27-ek-list a small{display:block;color:var(--mute);font-size:12.5px}
.fh-b27-ek-qa details{border-bottom:1px dashed var(--line);padding:8px 2px}
.fh-b27-ek-qa summary{cursor:pointer;font-weight:700}
.fh-b27-ek-qa p{margin-top:6px;font-size:14.5px}
.fh-b27-ek-cols{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.fh-b27-ek-cols>div{border:1px solid rgba(224,184,104,.22);border-radius:14px;background:var(--deep);padding:10px 14px;font-size:14.5px;line-height:1.85}
.fh-b27-ek-cols b{color:#F6E2B8}
.fh-b27-ek-kd{border-left:4px solid var(--shu);background:var(--deep);border-radius:0 12px 12px 0;padding:10px 14px;margin:10px 0;font-family:'Shippori Mincho',serif;font-size:16px;line-height:1.9}
.fh-b27-ek-kd small{display:block;font-family:inherit;color:var(--mute);font-size:12.5px}
.fh-b27-ek-yao{display:flex;flex-direction:column;gap:10px}
.fh-b27-ek-yao>div{display:grid;grid-template-columns:70px minmax(0,1fr);gap:12px;border:1px solid rgba(224,184,104,.22);border-radius:14px;background:var(--deep);padding:12px;font-size:14.5px;line-height:1.85}
.fh-b27-ek-yao .lb{text-align:center;font-family:'Shippori Mincho',serif;font-weight:800;color:#F6E2B8}
.fh-b27-ek-yao .lb svg{display:block;margin:0 auto 4px}
.fh-b27-ek-yao .lb small{display:block;font-family:inherit;font-weight:400;color:var(--mute);font-size:11.5px}
.fh-b27-ek-yao p{margin:4px 0}
.fh-b27-ek-yao .kd{font-family:'Shippori Mincho',serif;color:#F6E2B8}
.fh-b27-ek-nav{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap}
.fh-b27-ek-nav a{border:1px solid rgba(224,184,104,.35);border-radius:999px;padding:6px 14px;text-decoration:none;font-size:14px}
.fh-b27-ek-judge{display:inline-block;border:1.5px solid var(--gold);border-radius:999px;color:#F6E2B8;font-weight:800;padding:2px 14px;font-size:14px}
.fh-b27-ek-th{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.fh-b27-ek-th div{border:1px solid rgba(224,184,104,.22);border-radius:12px;background:var(--deep);padding:10px 12px;font-size:14px;line-height:1.8}
.fh-b27-ek-th b{display:block;color:#F6E2B8}
@media (max-width:640px){.fh-b27-ek-list,.fh-b27-ek-cols,.fh-b27-ek-th{grid-template-columns:1fr}.fh-b27-ek-tri{grid-template-columns:repeat(2,minmax(0,1fr))}
 .fh-b27[data-fh-page="eki"] .fh-b27-toc ol{columns:1}.fh-b27[data-fh-page="eki"] .fh-b27-title{font-size:25px}.fh-b27-ek-emb{width:88px;height:88px}
 .fh-b27-ek-yao>div{grid-template-columns:1fr}.fh-b27-ek-yao .lb{text-align:left;display:flex;gap:10px;align-items:center}.fh-b27-ek-yao .lb svg{margin:0}}
@media (prefers-reduced-motion:reduce){.fh-b27-ek-emb .fh-b27-ek-svg,.fh-b27-ek-card{animation:none}.fh-b27-ek-sticks i{transition:none}}
</style>"""

JS = r"""(function(){var H=__H__,TO=__TO__,JG=__JG__,TN=__TN__,PN=__PN__;function $(i){return document.getElementById(i)}
if(!$('ek-go'))return;var thK='総合',busy=false;
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
document.querySelectorAll('#ek-th button').forEach(function(b){b.addEventListener('click',function(){document.querySelectorAll('#ek-th button').forEach(function(z){z.setAttribute('aria-pressed','false')});b.setAttribute('aria-pressed','true');thK=b.getAttribute('data-v');})});
function rnd(n){if(window.crypto&&crypto.getRandomValues){var a=new Uint32Array(1);crypto.getRandomValues(a);return a[0]%n}return Math.floor(Math.random()*n)}
function svg(L,hl){var r='';for(var i=0;i<6;i++){var y=(5-i)*16,c=(hl===i)?' class="hl"':'';r+=L[i]?'<rect'+c+' x="0" y="'+y+'" width="100" height="10" rx="2"/>':'<rect'+c+' x="0" y="'+y+'" width="43" height="10" rx="2"/><rect'+c+' x="57" y="'+y+'" width="43" height="10" rx="2"/>'}return '<svg class="fh-b27-ek-svg" viewBox="0 0 100 90" width="72" height="65" aria-hidden="true">'+r+'</svg>'}
var st=$('ek-sticks');var sh='';for(var i=0;i<49;i++){sh+='<i></i>'}st.innerHTML=sh;
function once(mod){var left=1+rnd(47),cnt=left+1,r=cnt%mod;return {left:left,cnt:cnt,r:r===0?mod:r}}
function split(left,cb){var s=st.querySelectorAll('i');st.classList.remove('split');s.forEach(function(e,k){e.className=k<left?'l':'r'});setTimeout(function(){st.classList.add('split')},60);setTimeout(cb,900)}
$('ek-go').addEventListener('click',function(){if(busy)return;busy=true;$('ek-res').hidden=true;$('ek-ads').hidden=true;['ek-s1','ek-s2','ek-s3'].forEach(function(k){$(k).innerHTML='<b>…</b>'});
 var a=once(8),b=once(8),c=once(6);
 split(a.left,function(){$('ek-s1').innerHTML='<b>'+TO[a.r-1]+'（'+TN[TO[a.r-1]]+'）</b>下の卦｜余り'+a.r;
 split(b.left,function(){$('ek-s2').innerHTML='<b>'+TO[b.r-1]+'（'+TN[TO[b.r-1]]+'）</b>上の卦｜余り'+b.r;
 split(c.left,function(){$('ek-s3').innerHTML='<b>'+PN[c.r-1]+'</b>変わる爻｜余り'+c.r;show(TO[a.r-1],TO[b.r-1],c.r-1)})})})});
function pick(doc,yi){var o={y:'',t:''};try{var y=doc.getElementById('ek-y'+(yi+1));if(y){y.querySelectorAll('p').forEach(function(p){var b=p.querySelector('b');if(b&&b.textContent.indexOf('占いでは')===0)o.y=p.textContent.replace(/^占いでは：/,'')})}
 if(thK!=='総合'){doc.querySelectorAll('#ek-theme .fh-b27-ek-th div').forEach(function(d){var b=d.querySelector('b');if(b&&b.textContent===thK)o.t=d.textContent.slice(thK.length)})}}catch(e){}return o}
function show(lo,up,yi){var h=null;for(var k in H){if(H[k].lo===lo&&H[k].up===up){h=H[k];break}}var z=H[h.zhi[yi]];
 var r=$('ek-res');r.innerHTML='<div class="fh-b27-ek-card"><div class="fh-b27-ek-head">'+svg(h.L,yi)+'<div><small>本卦（いまの状態）第'+h.n+'卦</small><div class="nm">'+esc(h.nm)+'</div><small>'+esc(h.yo)+'</small></div></div>'
 +'<p><span class="fh-b27-ek-tag">'+esc(h.jd)+'</span><b>'+esc(h.ca)+'</b></p><p>'+esc(h.now)+'</p><p id="ek-r-th"></p><p><b>心がけ：</b>'+esc(h.ad)+'</p>'
 +'<p id="ek-r-y"><b>変わる爻は「'+esc(h.yl[yi])+'」（'+PN[yi]+'）</b></p><p><a href="'+h.u+'#ek-y'+(yi+1)+'">'+esc(h.nm)+'の意味と'+esc(h.yl[yi])+'の言葉をくわしく読む →</a></p></div>'
 +'<div class="fh-b27-ek-card" style="animation-delay:.3s"><div class="fh-b27-ek-head">'+svg(z.L)+'<div><small>之卦（これからの流れ）第'+z.n+'卦</small><div class="nm">'+esc(z.nm)+'</div><small>'+esc(z.yo)+'</small></div></div>'
 +'<p><b>'+esc(z.ca)+'</b></p><p>'+esc(z.now)+'</p><p><a href="'+z.u+'">'+esc(z.nm)+'の意味をくわしく読む →</a></p></div>';
 r.hidden=false;var g=JG[h.jd];['go','care','wait'].forEach(function(k){var e=$('ek-ad-'+k);if(e)e.hidden=(k!==g)});$('ek-ads').hidden=false;$('ek-go').textContent='もう一度、易を立てる';busy=false;
 fetch(h.u,{credentials:'same-origin'}).then(function(x){return x.text()}).then(function(t){var o=pick(new DOMParser().parseFromString(t,'text/html'),yi);
  if(o.y)$('ek-r-y').innerHTML='<b>変わる爻は「'+esc(h.yl[yi])+'」（'+PN[yi]+'）：</b>'+esc(o.y);if(o.t)$('ek-r-th').innerHTML='<b>'+esc(thK)+'：</b>'+esc(o.t)}).catch(function(){});}
})();"""


def h2f():
    n = [0]

    def h2(t):
        n[0] += 1
        return f'<h2><span class="fh-b27-n">{n[0]}</span><span>{t}</span></h2>'
    return h2


def foot(updated, extra=""):
    up = dt.date.fromisoformat(updated)
    return (f'<p class="fh-b27-foot">易占いは、気持ちを整理し、動き方を考えるための読み物として楽しむもので、未来を決めるものではありません。'
            f'卦辞・爻辞・大象は古典『周易』（易経）の本文を書き下したもので、現代語訳と占いの読みはこのサイトで書いたものです。{extra}'
            f'最終更新日：{up.year}年{up.month}月{up.day}日／<a href="/about/">この記事の作成方針について</a></p>')


LINKS = '''<div class="fh-b27-links">
    <a href="/eki/"><b>易占い（トップ）→</b><small>画面で易を立てる・64卦の一覧</small></a>
    <a href="/tarot/"><b>タロット占い →</b><small>78枚のカードで相談に答える</small></a>
    <a href="/rune/"><b>ルーン占い →</b><small>25のルーンを引く</small></a>
    <a href="/omikuji/"><b>おみくじ →</b><small>50番・18種類の吉凶</small></a>
  </div>'''

HUB_FAQ = [
    ("易占いと「八卦」は同じものですか。", "八卦は、易の土台になる8つの図形（乾・兌・離・震・巽・坎・艮・坤）のことです。八卦を上下に2つ重ねた64の卦で占うのが易占いです。「当たるも八卦、当たらぬも八卦」ということわざの八卦は、易占いのことを指しています。"),
    ("同じことを何度も占ってもいいですか。", "易では、同じ問いを何度もくり返すことはよくないとされます。64卦のひとつ「山水蒙」の卦辞にも、最初の問いには答えるが、くり返し問えばけがれて答えない、という意味の言葉があります。最初に出た卦を、まずじっくり読んでみてください。"),
    ("本卦と之卦は、どちらを重く見ればいいですか。", "中心はいまの状態を表す本卦です。変わる爻（変爻）の言葉で、本卦の中のどの段階にいるのかを読み、之卦は「この先どう移っていくか」の参考にします。"),
    ("コインで占って、変わる爻が2つ以上出たらどう読みますか。", "読み方には流派がありますが、このサイトでは、本卦を中心に読み、変わる爻のうちいちばん上の爻の言葉を主に読むことにしています。変わる爻が1つもなければ本卦の卦辞だけを、6つとも変わるときは之卦を中心に読みます。"),
    ("筮竹がなくても占えますか。", "このページのボタンで、50本の筮竹を使う略筮法と同じ手順で卦を出せます。手もとで占うなら、10円玉などのコイン3枚でも易を立てられます（やり方は上の「占い方」にあります）。"),
    ("易経と周易は違うものですか。", "ほぼ同じものを指します。周の時代にまとめられた易という意味で『周易』と呼ばれ、儒教の大切な書物（経）のひとつになってから『易経』とも呼ばれるようになりました。"),
]


def hub(sample, updated):
    H = []
    a = H.append
    a(CSS)
    a('<div class="fh-b27" data-fh-page="eki">\n<div class="fh-b27-note">')
    a(f'''<header class="fh-b27-hero">
  <div class="fh-b27-ek-emb" aria-hidden="true">{svg(HX[62]["lines"], 70)}</div>
  <div class="fh-b27-hero-body">
    <span class="fh-b27-tape">人生予報 易占い</span>
    <h1 class="fh-b27-title">易占い<br>六十四卦で、いまの答えを読む</h1>
    <p class="fh-b27-lead">古代中国の『易経』にもとづく、無料の易占いです。日本でいちばん広く使われている「略筮法」と同じ手順で、画面の50本の筮竹を分けて卦を立てます。いまの状態を表す本卦、変わる爻、これからの流れを表す之卦を、恋愛・仕事・お金など11のテーマで読めます。64卦すべての意味もこのページから読めます。</p>
  </div>
</header>''')
    items = [("b27-ek-draw", "易を立てる"), ("b27-ek-about", "易占いとは"), ("b27-ek-how", "占い方（略筮法・コイン）"),
             ("b27-ek-read", "本卦・変爻・之卦の読み方"), ("b27-ek-tri", "八卦の意味"), ("b27-ek-grid", "64卦の早見表"),
             ("b27-ek-list", "64卦の意味一覧"), ("b27-ek-faq", "よくある質問")]
    a('<nav class="fh-b27-toc" aria-label="目次"><strong>このページの内容</strong><ol>' + "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in items) + "</ol></nav>")
    h2 = h2f()
    thb = "".join(f'<button type="button" data-v="{t}" aria-pressed="{"true" if t == "総合" else "false"}">{t}</button>' for t in ['総合'] + THEMES)
    ads = AX.result_boxes("ek-ad", GOODS, lead="出た卦の「動き方」に合わせて選びました。楽天・Yahoo!ショッピングの商品ページへ移ります。")
    a(f'''<section class="fh-b27-sec" id="b27-ek-draw">
  {h2("易を立てる")}
  <div class="fh-b27-ek-box">
    <div class="fh-b27-ek-opts" id="ek-th"><small>知りたいこと</small>{thb}</div>
    <p class="fh-b27-ek-q">占いたいことを、ひとつだけ心の中ではっきり思い浮かべてから、ボタンを押してください。</p>
    <div class="fh-b27-ek-sticks" id="ek-sticks" aria-hidden="true"></div>
    <div class="fh-b27-ek-steps"><div id="ek-s1"><b>一</b>下の卦</div><div id="ek-s2"><b>二</b>上の卦</div><div id="ek-s3"><b>三</b>変わる爻</div></div>
    <button type="button" class="fh-b27-ek-go" id="ek-go">易を立てる</button>
    <div class="fh-b27-ek-res" id="ek-res" aria-live="polite" hidden></div>
    <div id="ek-ads" style="width:100%" hidden>{ads}</div>
  </div>
</section>''')
    a(f'''<section class="fh-b27-sec" id="b27-ek-about">
  {h2("易占いとは")}
  <p>易占いは、古代中国で生まれた占いです。もとになる書物『易経』（周易）は、儒教の大切な古典のひとつとして、日本でも長く読まれてきました。「当たるも八卦、当たらぬも八卦」ということわざの八卦も、この易のことです。</p>
  <p>易では、世の中のすべてを「陽（—）」と「陰（- -）」の組み合わせで考えます。この線を3本重ねたものが八卦で、天・沢・火・雷・風・水・山・地の8つの自然を表します。八卦をさらに上下に2つ重ねると、6本の線でできた64の卦ができます。1本ずつの線を「爻（こう）」と呼び、下から初爻・二爻・三爻・四爻・五爻・上爻と数えます。</p>
  <p>『易経』には、64の卦それぞれに、卦全体の意味を述べた「卦辞」と、6本の爻ごとの言葉「爻辞」が書かれています。易占いでは、偶然に出た卦と爻の言葉を、自分の問いに当てはめて読みます。答えを決めつけるというより、いまの状況を別の角度から見せてくれる占いです。</p>
</section>''')
    a(f'''<section class="fh-b27-sec" id="b27-ek-how">
  {h2("占い方（略筮法・コイン）")}
  <h3>略筮法（このページのやり方）</h3>
  <p>略筮法は、50本の細い竹の棒（筮竹）を使う、日本でいちばん一般的な易の立て方です。このページでは、筮竹を分ける場所を乱数で決め、同じ計算で卦を出しています。</p>
  <div class="fh-b27-ek-cols">
    <div><b>1. 1本を除く</b><br>50本のうち1本を「太極」として別に置き、49本で占います。</div>
    <div><b>2. 2つに分けて数える</b><br>49本を左右に分け、右から1本取って左に加えます。左の束を8本ずつ数えて、余りの数（1〜8）で八卦を決めます。1回目が下の卦、2回目が上の卦です。</div>
    <div><b>3. 変わる爻を決める</b><br>3回目は6本ずつ数え、余り（1〜6）で、変わる爻が下から何本目かを決めます。</div>
    <div><b>余りと八卦</b><br>1 乾（天）・2 兌（沢）・3 離（火）・4 震（雷）・5 巽（風）・6 坎（水）・7 艮（山）・8 坤（地）。余りが0のときは8（6）とします。</div>
  </div>
  <h3>コイン3枚で占う（手もとでやるとき）</h3>
  <p>同じ種類のコインを3枚用意し、表を3、裏を2と決めます。3枚を投げて合計を出すことを6回くり返し、1回目を初爻（いちばん下）として下から積み上げます。合計が7なら陽、8なら陰、9は「陽が陰に変わる爻」、6は「陰が陽に変わる爻」です。変わる爻を反対にした卦が之卦になります。</p>
</section>''')
    a(f'''<section class="fh-b27-sec" id="b27-ek-read">
  {h2("本卦・変爻・之卦の読み方")}
  <div class="fh-b27-ek-cols">
    <div><b>本卦（ほんか）</b><br>最初に出た卦で、いまの状態や問いへの答えの中心です。まず卦辞と、その卦の全体の意味を読みます。</div>
    <div><b>変爻（へんこう）</b><br>6本のうち、変わる1本です。その卦の中で、あなたがいまどの段階にいるのかを示します。爻辞の言葉を、いちばん具体的な助言として読みます。</div>
    <div><b>之卦（しか）</b><br>変爻の陰陽を反対にしてできる卦です。いまの状態がこれからどこへ移っていくのか、その行き先として参考にします。</div>
    <div><b>爻の位置の目安</b><br>{"・".join(f"{p}＝{m}" for p, m in zip(POSN, POSM))}。</div>
  </div>
</section>''')
    tri = "".join(f'<div>{tri_svg(k, 46)}<b>{k}（{v["yomi"]}）</b>{v["nature"]}｜{esc(v["mean"])}</div>' for k, v in [(k, TRI[k]) for k in TRI_ORDER])
    a(f'''<section class="fh-b27-sec" id="b27-ek-tri">
  {h2("八卦の意味")}
  <p>八卦は、3本の爻でできた8つの図形です。それぞれが自然の姿と、人の性質や動きを表します。64卦の名前は「上の卦の自然＋下の卦の自然＋卦の名」でできています（例：上が地・下が天で「地天泰」）。</p>
  <div class="fh-b27-ek-tri">{tri}</div>
</section>''')
    key = {(h["lower"], h["upper"]): h for h in HX}
    head = "".join(f'<th scope="col">{k}<small>{TRI[k]["nature"]}</small></th>' for k in TRI_ORDER)
    rows = "".join(f'<tr><th scope="row">{u}<small>{TRI[u]["nature"]}</small></th>' + "".join(
        f'<td><a href="{url(key[(l, u)])}">{key[(l, u)]["n"]}<br>{esc(key[(l, u)]["name"])}<small>{esc(key[(l, u)]["yomi"])}</small></a></td>' for l in TRI_ORDER) + "</tr>"
        for u in TRI_ORDER)
    a(f'''<section class="fh-b27-sec" id="b27-ek-grid">
  {h2("64卦の早見表")}
  <p>縦が上の卦、横が下の卦です。手もとで占ったときは、ここから卦を探してください。数字は『易経』の並び（序卦）の番号です。</p>
  <div class="fh-b27-ek-grid"><table><thead><tr><th>上＼下</th>{head}</tr></thead><tbody>{rows}</tbody></table></div>
</section>''')
    lst = "".join(f'<a href="{url(h)}">{svg(h["lines"], 40)}<span><b>第{h["n"]}卦 {esc(h["name"])}</b>（{esc(h["yomi"])}）<small>{esc(T[h["n"]]["catch"])}｜{esc(T[h["n"]]["judge"])}</small></span></a>' for h in HX)
    a(f'''<section class="fh-b27-sec" id="b27-ek-list">
  {h2("64卦の意味一覧")}
  <p>卦の名前を押すと、その卦の意味・卦辞と大象・恋愛や仕事など11のテーマ・6本の爻の読み方を、くわしく読めます。</p>
  <div class="fh-b27-ek-list">{lst}</div>
</section>''')
    qa = "".join(f'<details{" open" if i == 0 else ""}><summary>Q. {esc(q)}</summary><p>A. {esc(x)}</p></details>' for i, (q, x) in enumerate(HUB_FAQ))
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in HUB_FAQ]}
    a(f'''<section class="fh-b27-sec" id="b27-ek-faq">
  {h2("よくある質問")}
  <div class="fh-b27-ek-qa">{qa}</div>
</section>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<section class="fh-b27-sec" id="b27-ek-more">
  <div class="fh-b27-links">
    <a href="/tarot/"><b>タロット占い →</b><small>78枚のカードで相談に答える</small></a>
    <a href="/rune/"><b>ルーン占い →</b><small>25のルーンを引く</small></a>
    <a href="/kyusei/"><b>九星気学 →</b><small>本命星と2027年の吉方位</small></a>
    <a href="/omikuji/"><b>おみくじ →</b><small>50番・18種類の吉凶</small></a>
  </div>
</section>''')
    data = {str(h["n"]): dict(n=h["n"], nm=h["name"], yo=h["yomi"], u=url(h), L=h["lines"], lo=h["lower"], up=h["upper"], zhi=h["zhi"],
                              ca=T[h["n"]]["catch"], jd=T[h["n"]]["judge"], now=T[h["n"]]["now"], ad=T[h["n"]]["advice"],
                              yl=[y[0] for y in h["yao_src"]]) for h in HX}
    js = (JS.replace("__H__", json.dumps(data, ensure_ascii=False)).replace("__TO__", json.dumps(TRI_ORDER, ensure_ascii=False))
          .replace("__JG__", json.dumps(JG, ensure_ascii=False)).replace("__TN__", json.dumps({k: v["nature"] for k, v in TRI.items()}, ensure_ascii=False))
          .replace("__PN__", json.dumps(POSN, ensure_ascii=False)))
    a(foot(updated, "画面の占いは、略筮法の手順を乱数でなぞったものです。"))
    a("</div>\n</div>")
    a(f"<script>document.addEventListener('DOMContentLoaded',function(){{{js}}});</script>")
    title = "易占い【無料】六十四卦で占う｜本卦・変爻・之卦の読み方と64卦の意味一覧"
    desc = ("略筮法の手順で画面の筮竹を分けて卦を立てる、無料の易占い。本卦・変わる爻・之卦を、恋愛・仕事・お金など11のテーマで読めます。"
            "易の基本、八卦の意味、64卦の早見表と、乾為天から火水未済まで64卦すべての意味も紹介します。")
    body = "\n".join(H)
    body = body.replace('<section class="fh-b27-sec" id="b27-ek-about">', AX.phone_box(*PHONE) + '\n<section class="fh-b27-sec" id="b27-ek-about">', 1)
    body = body.replace('<section class="fh-b27-sec" id="b27-ek-faq">', AX.goods_box(*GOODS_EKI, lead="手もとで本式に易を立てたい人・易経を読みたい人へ。楽天・Yahoo!ショッピングの商品ページへ移ります。") + '\n<section class="fh-b27-sec" id="b27-ek-faq">', 1)
    body = AX.CSS + "\n" + body
    out = shell(title, desc, "/eki/", body, sample)
    assert "[sp]" not in out and "[pc]" not in out and "動物占い" not in out
    return out


def sub(h, sample, updated):
    t = T[h["n"]]
    n = h["n"]
    H = []
    a = H.append
    a(CSS)
    a('<div class="fh-b27" data-fh-page="eki">\n<div class="fh-b27-note">')
    lo, up = TRI[h["lower"]], TRI[h["upper"]]
    a(f'''<header class="fh-b27-hero">
  <div class="fh-b27-ek-emb" aria-hidden="true">{svg(h["lines"], 70)}</div>
  <div class="fh-b27-hero-body">
    <span class="fh-b27-tape">易占い 第{n}卦</span>
    <h1 class="fh-b27-title">{esc(h["name"])}（{esc(h["yomi"])}）の意味</h1>
    <p class="fh-b27-lead">{esc(t["catch"])}。易の第{n}卦「{esc(h["name"])}」は、上に{h["upper"]}（{up["nature"]}）、下に{h["lower"]}（{lo["nature"]}）を重ねた卦です。キーワードは「{"」「".join(esc(k) for k in t["kw"])}」。卦辞と大象の書き下し、恋愛・仕事など11のテーマ、6本の爻の読み方をまとめました。</p>
  </div>
</header>''')
    items = [("ek-mean", f"{h['name']}の意味"), ("ek-text", "卦辞と大象"), ("ek-theme", "テーマ別の読み方"), ("ek-yao", "六爻（変爻）の読み方"),
             ("ek-rel", "関係する卦"), ("ek-faq", "よくある質問")]
    a('<nav class="fh-b27-toc" aria-label="目次"><strong>このページの内容</strong><ol>' + "".join(f'<li><a href="#{i}">{esc(x)}</a></li>' for i, x in items) + "</ol></nav>")
    h2 = h2f()
    a(f'''<section class="fh-b27-sec" id="ek-mean">
  {h2(esc(h["name"]) + "の意味")}
  <p><span class="fh-b27-ek-judge">動き方：{esc(t["judge"])}</span></p>
  <p>{esc(t["overall"])}</p>
  <div class="fh-b27-ek-cols">
    <div><b>卦の形</b><br>{esc(t["shape"])}</div>
    <div><b>いまの状況</b><br>{esc(t["now"])}</div>
  </div>
  <p><b>心がけ：</b>{esc(t["advice"])}</p>
</section>''')
    ex = (f'<div class="fh-b27-ek-kd"><small>{"用九" if n == 1 else "用六"}（6本すべてが変わるとき）</small>{esc(t["extra"]["kudashi"])}</div><p>{esc(t["extra"]["mean"])}</p>'
          if n in (1, 2) and t.get("extra") else "")
    a(f'''<section class="fh-b27-sec" id="ek-text">
  {h2("卦辞と大象")}
  <p>卦辞は、この卦全体について『易経』が述べた言葉です。大象は、上下の卦の姿から「人はどうふるまうとよいか」を説いた言葉です。</p>
  <div class="fh-b27-ek-kd"><small>卦辞（書き下し）</small>{esc(t["kudashi"])}</div>
  <p>{esc(t["gua_mean"])}</p>
  <div class="fh-b27-ek-kd"><small>大象（書き下し）</small>{esc(t["xiang_kudashi"])}</div>
  {ex}
</section>''')
    th = "".join(f'<div><b>{x}</b>{esc(t["themes"][x])}</div>' for x in THEMES)
    a(f'''<section class="fh-b27-sec" id="ek-theme">
  {h2("テーマ別の読み方")}
  <p>{esc(h["name"])}が出たときの、問いのテーマごとの読み方です。</p>
  <div class="fh-b27-ek-th">{th}</div>
</section>''')
    yao = ""
    for i in range(6):
        y = t["yao"][i]
        z = HX[h["zhi"][i] - 1]
        yao += (f'<div id="ek-y{i + 1}"><div class="lb">{svg(h["lines"], 52, hl=i)}{esc(ylabel(h, i))}<small>{POSN[i]}</small></div><div>'
                f'<p class="kd">{esc(y["kudashi"])}</p><p>{esc(y["mean"])}</p><p><b>占いでは：</b>{esc(y["read"])}</p>'
                f'<p><small>この爻が変わると之卦は <a href="{url(z)}">第{z["n"]}卦 {esc(z["name"])}</a></small></p></div></div>')
    a(f'''<section class="fh-b27-sec" id="ek-yao">
  {h2("六爻（変爻）の読み方")}
  <p>略筮法などで「変わる爻」が出たときは、その爻の言葉をいちばん具体的な助言として読みます。爻は下から初爻・二爻…上爻と数え、陽の爻は「九」、陰の爻は「六」で呼びます。</p>
  <div class="fh-b27-ek-yao">{yao}</div>
</section>''')
    if AX.tpl():
        a(AX.goods_box(*GOODS[JG[t["judge"]]], lead=f"{h['name']}の動き方「{t['judge']}」に合わせて選びました。楽天・Yahoo!ショッピングの商品ページへ移ります。"))
    rel = [("綜卦（さかさまにした卦）", h["zong"], "相手の側や、反対の立場から見たときの姿です。"),
           ("錯卦（陰陽を反対にした卦）", h["cuo"], "裏側に隠れている性質や、足りないものを表します。"),
           ("互卦（内側の2〜5爻でできる卦）", h["hu"], "表には出ていない、物事の内側の流れを表します。")]
    rl = "".join(f'<a href="{url(HX[k - 1])}">{svg(HX[k - 1]["lines"], 40)}<span><b>{lab}</b><br>第{k}卦 {esc(HX[k - 1]["name"])}<small>{d}{"（この卦自身）" if k == n else ""}</small></span></a>' for lab, k, d in rel)
    a(f'''<section class="fh-b27-sec" id="ek-rel">
  {h2("関係する卦")}
  <p>易では、ひとつの卦を別の角度から見るために、形を変えた卦を合わせて読むことがあります。</p>
  <div class="fh-b27-ek-list">{rl}</div>
</section>''')
    faq = [(q["q"], q["a"]) for q in t["faq"]] + [
        (f"{h['name']}の読み方は？", f"「{h['yomi']}」と読みます。易の64卦の第{n}番目の卦で、上の卦が{h['upper']}（{up['nature']}）、下の卦が{h['lower']}（{lo['nature']}）です。短く「{h['short']}」とも呼びます。")]
    qa = "".join(f'<details{" open" if i == 0 else ""}><summary>Q. {esc(q)}</summary><p>A. {esc(x)}</p></details>' for i, (q, x) in enumerate(faq))
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in faq]}
    pv, nx = HX[(n - 2) % 64], HX[n % 64]
    a(f'''<section class="fh-b27-sec" id="ek-faq">
  {h2("よくある質問")}
  <div class="fh-b27-ek-qa">{qa}</div>
</section>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<section class="fh-b27-sec" id="ek-more">
  <p><a class="fh-b27-btn" href="/eki/#b27-ek-draw">画面で易を立ててみる →</a></p>
  <div class="fh-b27-ek-nav"><a href="{url(pv)}">← 第{pv["n"]}卦 {esc(pv["name"])}</a><a href="/eki/#b27-ek-list">64卦の一覧</a><a href="{url(nx)}">第{nx["n"]}卦 {esc(nx["name"])} →</a></div>
  {LINKS}
</section>''')
    a(foot(updated))
    a("</div>\n</div>")
    title = f"{h['name']}（{h['yomi']}）の意味｜易占い 第{n}卦 恋愛・仕事と六爻の読み方"
    desc = (f"易の第{n}卦「{h['name']}（{h['yomi']}）」の意味を、卦辞と大象の書き下し・現代語訳でやさしく解説。{t['catch']}。"
            f"恋愛・結婚・仕事・お金など11のテーマ、初爻〜上爻の変爻の読み方、関係する卦も紹介します。")
    body = "\n".join(H)
    if AX.tpl():
        body = body.replace('<section class="fh-b27-sec" id="ek-text">', AX.phone_box(*PHONE) + '\n<section class="fh-b27-sec" id="ek-text">', 1)
        body = AX.CSS + "\n" + body
    out = shell(title, desc, url(h), body, sample)
    assert "[sp]" not in out and "[pc]" not in out
    return out, title, desc


def main():
    updated = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    meta = {}
    for sample in (False, True):
        base = os.path.join(OUT, "sample", "eki") if sample else os.path.join(OUT, "eki")
        os.makedirs(base, exist_ok=True)
        open(os.path.join(base, "index.html"), "w", encoding="utf-8").write(hub(sample, updated))
        for h in HX:
            out, title, desc = sub(h, sample, updated)
            open(os.path.join(base, f"{h['slug']}.html"), "w", encoding="utf-8").write(out)
            meta[h["slug"]] = dict(n=h["n"], title=title, desc=desc)
    json.dump(meta, open(os.path.join(OUT, "eki", "meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("→ out/eki/（ハブ＋64）")


if __name__ == "__main__":
    main()
