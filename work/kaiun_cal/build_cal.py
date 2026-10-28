"""開運ライフ「2027年の吉日カレンダー」のページ本文を作る（2026-10-25）。
テンプレート：/kaiun/season-kichijitsu/（ID 50）の公開HTML（src_pages.json）からヘッダー・フッター・「つづき」を流用。
日付：data/kichijitsu_2027.json（scripts/calc_kichijitsu.py で計算）。出力：out_kichijitsu_2027.html"""
import json, os, sys, html, datetime as dt, collections
HERE = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(W, "scripts"))
import build_html as B, goods_media as GM, build_subsite_ads as SA  # noqa
esc = lambda s: html.escape(s, quote=True)
R = json.load(open(os.path.join(W, "data", "kichijitsu_2027.json"), encoding="utf-8"))
T = json.load(open(os.path.join(HERE, "src_pages.json"), encoding="utf-8"))["50"]["html"]
pre = T[:T.find('<section class="k-ph">')]
xv = T[T.find('<section class="k-xv-wrap"'):]
xv = xv.replace("© 2026 開運ライフ", "© 2026 開運ライフ")
MD = lambda d: f"{int(d[5:7])}月{int(d[8:])}日"
def lab(x): return f'{MD(x["date"])}（{x["wd"]}）'
def tags_txt(x, skip=()):
    t = [g for g in x["tags"] if g not in skip]
    return "・".join(t) if t else "—"
by = lambda tag: [x for x in R if tag in x["tags"]]
TEN = by("天赦日"); MAN = by("一粒万倍日"); TORA = by("寅の日"); MI = by("巳の日"); TSUCHI = by("己巳の日"); KOSHI = by("甲子の日"); TAI = by("大安"); FU = by("不成就日")
BEST = [x for x in TEN if "一粒万倍日" in x["tags"]]

CSS = """<style>#kzf .kc-legend{display:flex;flex-wrap:wrap;gap:8px 14px;margin:6px 0 18px;font-size:13px;color:var(--fg)}
#kzf .kc-b{display:inline-block;min-width:1.6em;padding:0 5px;border-radius:4px;border:1px solid var(--line);font-size:11px;line-height:1.6;text-align:center;color:var(--navy);background:var(--paper2)}
#kzf .kc-b.t{border-color:#B23A48;color:#8E2433;background:#FBEDEE}#kzf .kc-b.m{border-color:#C09A4E;color:#6B4E10;background:#FBF3E2}
#kzf .kc-b.r{border-color:#2E6B4F;color:#1F4E39;background:#EAF4EE}#kzf .kc-b.s{border-color:#3F5E8C;color:#24406A;background:#EBF0F8}
#kzf .kc-b.f{border-color:#A09A8B;color:#5E574D;background:#F2F0EB}
#kzf .kc-months{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:22px;margin:10px 0 8px}
#kzf .kc-mon{background:var(--paper2);border:1px solid var(--line);border-radius:12px;padding:12px 12px 10px}
#kzf .kc-mon h3{font-size:17px;margin:0 0 8px;color:var(--navy)}
#kzf .kc-grid{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:3px}
#kzf .kc-wd{font-size:11px;text-align:center;color:var(--muted)}
#kzf .kc-d{min-height:52px;border-radius:6px;padding:2px 2px 3px;background:#FFFFFF;border:1px solid var(--line2);font-size:12px;line-height:1.25;color:var(--fg)}
#kzf .kc-d .n{display:block;font-weight:700;color:var(--navy)}#kzf .kc-d.sun .n{color:#8E2433}#kzf .kc-d.sat .n{color:#24406A}
#kzf .kc-d.ten{background:#FBEDEE;border-color:#B23A48}#kzf .kc-d.e{background:transparent;border:0}
#kzf .kc-d .kc-b{display:block;margin-top:2px;padding:0 1px;font-size:10px;min-width:0}
#kzf .kc-rk{display:block;font-size:10px;color:var(--muted)}
#kzf .kc-list{columns:2 220px;column-gap:28px;margin:8px 0 6px;padding-left:1.2em}#kzf .kc-list li{break-inside:avoid;margin:0 0 4px}
#kzf .kc-hl{background:#FBF3E2;border:1px solid #C09A4E;border-radius:12px;padding:14px 16px;margin:12px 0}#kzf .kc-hl p{color:var(--fg)}
@media(max-width:480px){#kzf .kc-d{min-height:46px;font-size:11px}#kzf .kc-d .kc-b{font-size:9px}}</style>"""

def badge(tag):
    m = {"天赦日": ("t", "天赦"), "一粒万倍日": ("m", "万倍"), "寅の日": ("r", "寅"), "巳の日": ("s", "巳"), "己巳の日": ("s", "己巳"), "甲子の日": ("r", "甲子"), "大安": ("", "大安"), "不成就日": ("f", "不成就")}
    c, t = m[tag]; return f'<span class="kc-b {c}">{t}</span>'

def month_grid(m):
    days = [x for x in R if int(x["date"][5:7]) == m]
    first = dt.date(2027, m, 1).weekday()  # 月=0
    off = (first + 1) % 7  # 日曜はじまり
    cells = ['<span class="kc-d e"></span>'] * off
    order = ["天赦日", "一粒万倍日", "寅の日", "己巳の日", "巳の日", "甲子の日", "不成就日"]
    for x in days:
        d = dt.date.fromisoformat(x["date"]); cls = ["kc-d"]
        if d.weekday() == 6: cls.append("sun")
        if d.weekday() == 5: cls.append("sat")
        if "天赦日" in x["tags"]: cls.append("ten")
        tg = [t for t in order if t in x["tags"]]
        if "己巳の日" in tg and "巳の日" in tg: tg.remove("巳の日")
        bs = "".join(badge(t) for t in tg[:3])
        aria = f'{m}月{d.day}日 {x["rokuyo"]} ' + "・".join(tg)
        cells.append(f'<span class="{" ".join(cls)}" aria-label="{esc(aria)}"><span class="n">{d.day}</span><span class="kc-rk">{x["rokuyo"]}</span>{bs}</span>')
    wd = "".join(f'<span class="kc-wd">{w}</span>' for w in "日月火水木金土")
    cnt = collections.Counter(t for x in days for t in x["tags"])
    return (f'<div class="kc-mon"><h3>2027年{m}月</h3><div class="kc-grid">{wd}{"".join(cells)}</div>'
            f'<p style="font-size:12px;color:var(--muted);margin-top:6px">一粒万倍日 {cnt["一粒万倍日"]}日・寅の日 {cnt["寅の日"]}日・大安 {cnt["大安"]}日' + (f'・天赦日 {cnt["天赦日"]}日' if cnt["天赦日"] else "") + '</p></div>')

def ul(items): return '<ul class="kc-list">' + "".join(f"<li>{i}</li>" for i in items) + "</ul>"
def months_list(xs):
    g = collections.OrderedDict()
    for x in xs: g.setdefault(int(x["date"][5:7]), []).append(x)
    return ul([f'<b>{m}月</b>　' + "、".join(f'{int(x["date"][8:])}日（{x["wd"]}）' for x in v) for m, v in g.items()])

rows_ten = "".join(f'<tr><td>{lab(x)}</td><td>{x["rokuyo"]}</td><td>{tags_txt(x, ("天赦日","大安"))}</td></tr>' for x in TEN)
best_li = "".join(f'<li><b>{lab(x)}</b>　{x["rokuyo"]}' + ("・不成就日とも重なる" if "不成就日" in x["tags"] else "") + ("・甲子の日" if "甲子の日" in x["tags"] else "") + "</li>" for x in BEST)
tora_man = [x for x in TORA if "一粒万倍日" in x["tags"]]

body = f'''<section class="k-ph"><div class="k-wrap"><nav class="k-bc"><a href="/kaiun/">ホーム</a><span class="k-sp">/</span><a href="/kaiun/seasonal/">季節の開運</a><span class="k-sp">/</span><span class="k-cur">2027年の吉日カレンダー</span></nav>
<p class="k-mono">seasonal / Calendar 2027</p><h1>2027年の吉日カレンダー</h1><p class="k-lead">天赦日{len(TEN)}日・一粒万倍日{len(MAN)}日・寅の日{len(TORA)}日・己巳の日{len(TSUCHI)}日。2027年の吉日を、月ごとのカレンダーと一覧で。</p><p class="k-meta">2026.10.25　／　季節の開運　／　日付は暦の決まりから計算</p></div></section>
<section class="k-sec" style="padding-top:64px"><div class="k-wrap"><div class="k-art">{CSS}<nav class="k-toc"><p class="k-toc-t">目次 / Contents</p><ol><li><a href="#c1">2027年の天赦日と、一粒万倍日が重なる日</a></li><li><a href="#c2">月ごとのカレンダー</a></li><li><a href="#c3">一粒万倍日の一覧</a></li><li><a href="#c4">寅の日・巳の日・己巳の日・甲子の日</a></li><li><a href="#c5">大安と不成就日</a></li><li><a href="#c6">日付の出し方</a></li><li><a href="#c7">よくある質問</a></li></ol></nav>
<p>2027年（丁未・ひのとひつじの年）の吉日を、暦の決まりにしたがって計算しました。天赦日は年に{len(TEN)}回、一粒万倍日は{len(MAN)}回あります。予定を立てるときの目安としてお使いください。吉日の意味や使い方は<a href="/kaiun/season-kichijitsu/" style="text-decoration:underline">吉日の使い方</a>で詳しく扱っています。</p>
<h2 id="c1">2027年の天赦日と、一粒万倍日が重なる日</h2>
<p>天赦日（てんしゃにち）は、季節ごとに決まった干支の日にあたる、暦の上で最上とされる吉日です。2027年は次の{len(TEN)}日です。</p>
<div class="k-tbwrap"><table><thead><tr><th>日付</th><th>六曜</th><th>重なるほかの暦注</th></tr></thead><tbody>{rows_ten}</tbody></table></div>
<div class="kc-hl"><p><b>天赦日と一粒万倍日が重なる日（{len(BEST)}日）</b></p><ul style="margin:6px 0 0 1.2em">{best_li}</ul><p style="font-size:13px;color:var(--muted);margin-top:6px">重なる日は「最上の吉日」と説明されることがあります。ただし、効果を検証したものではありません。</p></div>
<h2 id="c2">月ごとのカレンダー</h2>
<div class="kc-legend"><span>{badge("天赦日")} 天赦日</span><span>{badge("一粒万倍日")} 一粒万倍日</span><span>{badge("寅の日")} 寅の日</span><span>{badge("己巳の日")} 己巳の日</span><span>{badge("巳の日")} 巳の日</span><span>{badge("甲子の日")} 甲子の日</span><span>{badge("不成就日")} 不成就日</span></div>
<p style="font-size:13px;color:var(--muted)">日付の下の小さな文字は六曜（大安・仏滅など）です。1日に表示する印は3つまで（天赦日→一粒万倍日→寅の日…の順）。すべての印は下の一覧で確認できます。</p>
<div class="kc-months">{"".join(month_grid(m) for m in range(1, 13))}</div>
<h2 id="c3">一粒万倍日の一覧（{len(MAN)}日）</h2>
<p>一粒の籾が万倍に実るとされる日で、何かを始めるのによいとされます。月（節月）ごとに決まった十二支の日にあたるため、月に4〜6回あります。</p>
{months_list(MAN)}
<h2 id="c4">寅の日・巳の日・己巳の日・甲子の日</h2>
<p><b>寅の日（{len(TORA)}日）</b>　「出て行ったものが戻る」とされ、財布の新調や旅立ちによい日といわれます。一粒万倍日と重なるのは{len(tora_man)}日（{"、".join(MD(x["date"]) for x in tora_man)}）。</p>
{months_list(TORA)}
<p><b>己巳の日（{len(TSUCHI)}日）</b>　60日に一度の巳の日で、弁財天にゆかりの日とされます。{"、".join(lab(x) for x in TSUCHI)}。</p>
<p><b>巳の日（{len(MI)}日）</b>　12日に一度。弁財天の縁日とされ、金運にまつわる日として知られます。</p>
{months_list(MI)}
<p><b>甲子の日（{len(KOSHI)}日）</b>　干支のはじまりの日で、新しいことを始める区切りとされます。{"、".join(lab(x) for x in KOSHI)}。</p>
<h2 id="c5">大安と不成就日</h2>
<p><b>大安（{len(TAI)}日）</b>　六曜のうち、万事によいとされる日です。</p>
{months_list(TAI)}
<p><b>不成就日（{len(FU)}日）</b>　何事も成就しないとされる日です。吉日と重なる日もあり、気になる場合は避ける目安にしてください。</p>
{months_list(FU)}
<h2 id="c6">日付の出し方</h2>
<div class="k-tbwrap"><table><thead><tr><th>暦注</th><th>決まり</th></tr></thead><tbody>
<tr><td>天赦日</td><td>春（立春〜立夏の前日）は戊寅、夏（立夏〜）は甲午、秋（立秋〜）は戊申、冬（立冬〜）は甲子の日</td></tr>
<tr><td>一粒万倍日</td><td>節月ごとに決まった十二支の日（寅月は丑・午の日、卯月は酉・寅の日 など）。月の区切りは節入りの日</td></tr>
<tr><td>寅の日・巳の日・己巳の日・甲子の日</td><td>その日の干支から</td></tr>
<tr><td>大安・不成就日</td><td>旧暦の月と日から</td></tr></tbody></table></div>
<p>節入りの日時は太陽の位置から計算し、旧暦は月の満ち欠けから計算しています。暦によっては、節入りの日を前の月として扱うなどの違いから、1日ずれることがあります。大切な予定は、お使いの暦でもあわせて確認してください。</p>
<h2 id="c7">よくある質問</h2>
<div class="k-faq"><div class="k-q"><p class="k-qq">2027年の天赦日はいつですか。</p><p class="k-qa">{"、".join(lab(x) for x in TEN)}の{len(TEN)}日です。</p></div>
<div class="k-q"><p class="k-qq">2027年で一番よい日はいつですか。</p><p class="k-qa">天赦日と一粒万倍日が重なる{"、".join(MD(x["date"]) for x in BEST)}が、最上の吉日として挙げられることが多い日です。</p></div>
<div class="k-q"><p class="k-qq">吉日と不成就日が重なったらどうしますか。</p><p class="k-qa">「効果が半減する」と説明されることがあります。気になる場合はほかの吉日を選ぶか、日付よりも準備が整っているかで決めてください。</p></div>
<div class="k-q"><p class="k-qq">吉日に始めないと運が悪くなりますか。</p><p class="k-qa">なりません。吉日は予定を決めるための目印です。当サイトは日付に効果があると断定しません。</p></div></div>
<p class="k-note"><b>この記事の立場</b>　日付は暦の決まりにもとづいて当サイトで計算しました。吉日の吉凶に効果があると主張するものではありません。</p>
'''
# 広告（財布）
SA.B.AFF_TPL.update(SA.B.load_aff_templates()); SA.B.A8S.update(SA.B.load_a8_shops())
ad = SA.a8_line("pascle", "kaiun") + SA.product_box("上質な財布", "寅の日や一粒万倍日は、財布を新調する日として選ばれることもあります。選ぶときは、色よりもお札が折れずに入るか、小銭が取り出しやすいかを目安にすると長く使えます。")
ad = "<!-- fh-sub-ad:start -->" + SA.CSS + '<aside class="fhad" id="fhad" aria-label="広告"><p class="fhad-h">この記事に関連して（広告）</p>' + ad + "</aside><!-- fh-sub-ad:end -->"
src = '''<div class="k-src"><p class="k-st">出典</p><ul><li>国立国会図書館「日本の暦」吉凶を表す言葉③下段（天赦日など）<br><a href="https://www.ndl.go.jp/koyomi/chapter3/s5.html">https://www.ndl.go.jp/koyomi/chapter3/s5.html</a></li><li>暦の吉凶：選日（一粒万倍日など）と暦注についての解説<br><a href="https://saijigoyomi.com/senjitsu/">https://saijigoyomi.com/senjitsu/</a></li></ul><p class="k-us"><b>注記</b>　日付は当サイトの計算です（節入りは太陽の黄経、旧暦は朔の計算から）。一般的な暦と照合し、2027年の天赦日6日・一粒万倍日の日付が一致することを確認しました（2026-10-25）。</p></div>
<div class="k-pager"><a href="/kaiun/season-kichijitsu/"><span class="k-pl">あわせて読む</span><span class="k-pt">吉日の使い方</span></a></div>
</div>'''
cards = '''<div class="k-sh" style="margin:56px 0 26px"><div class="k-or"><i></i></div><h2 style="font-size:clamp(19px,2.6vw,24px)">関連する読みもの</h2></div><div class="k-cards"><a class="k-card" href="/kaiun/season-kichijitsu/"><p class="k-k">季節の開運</p><h3>吉日の使い方</h3><p>一粒万倍日・天赦日・大安・寅の日。由来と分類、そして「口実」として使う方法。</p><p class="k-go">読む →</p></a><a class="k-card" href="/kaiun/calendar/"><p class="k-k">開運カレンダー</p><h3>開運カレンダー</h3><p>二十四節気の円盤、五節句の一覧、吉日の意味をまとめました。</p><p class="k-go">読む →</p></a><a class="k-card" href="/unsei-2027/"><p class="k-k">人生予報</p><h3>2027年の運勢まとめ</h3><p>九星気学・干支・数秘術・マヤ暦・星座・誕生日から、2027年の運勢を占い別に読めます。</p><p class="k-go">読む →</p></a><a class="k-card" href="/kaiun/wallet-choose/"><p class="k-k">金運とお財布</p><h3>財布の選び方</h3><p>色の吉凶より、閉じ方と収まり。長財布・二つ折りの選び方と、替えどきの判断まで。</p><p class="k-go">読む →</p></a></div>
</div></section>'''
out = pre + body + ad + src + cards + xv
open(os.path.join(HERE, "out_kichijitsu_2027.html"), "w", encoding="utf-8").write(out)
print(len(out), len(TEN), len(MAN), len(BEST))
