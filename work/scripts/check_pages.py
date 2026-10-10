"""フェーズ9：全ページの機械点検 → work/reports/page_check.md
仕様書（docs/02_実装仕様.md）の「現行ページから必ず引き継ぐもの」「収益」「サイト内の行き来」と、本人の決定（確認2・3・4）を1ページずつ確かめる。
アフィリエイトは work/out/affiliate_templates.json（ひな形）と work/reports/affiliate_count.json（build_html.py --all が出す数）も見る。
使い方: python check_pages.py [--dir sample]（既定は work/out/html）"""
import os, re, sys, json, glob, html as H, collections, urllib.parse
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.join(HERE, "..")
d = sys.argv[sys.argv.index("--dir") + 1] if "--dir" in sys.argv else "html"
M = json.load(open(os.path.join(W, "data", "materials_366.json"), encoding="utf-8"))
files = sorted(glob.glob(os.path.join(W, "out", d, "[0-9][0-9][0-9][0-9].html")))
_tp = os.path.join(W, "out", "affiliate_templates.json")
TPL = {k: v for k, v in (json.load(open(_tp, encoding="utf-8")) if os.path.exists(_tp) else {}).items()
       if not k.startswith("_") and isinstance(v, dict) and v.get("href")}  # ひな形のある店だけ
AFF_HOSTS = ("af.moshimo.com", "px.a8.net")
SHOP_NAME = {"rakuten": "楽天市場", "amazon": "Amazon", "phone": "電話占い"}


def url(mmdd):
    return f"/366uranai/{mmdd[:2]}-{mmdd[2:]}/"


def aff_links(s):
    """アフィリエイトのリンク：(店, href, 開始タグ, 直後の文字列)。data-aff つき、または広告のリンク先のもの"""
    out = []
    for m in re.finditer(r"<a\s[^>]*>", s):
        tag = m.group(0)
        hm = re.search(r'href="([^"]*)"', tag)
        href = H.unescape(hm.group(1)) if hm else ""
        sm = re.search(r'data-aff="([^"]*)"', tag)
        host = urllib.parse.urlsplit(href).hostname or ""
        if sm or host in AFF_HOSTS or "affiliate" in href:
            end = s.find("</a>", m.end())
            out.append((sm.group(1) if sm else "", href, tag, s[end + 4:end + 400] if end >= 0 else "", s[m.end():end]))
    return out


VOID = {"img", "br", "meta", "link", "input", "hr", "source", "wbr"}


class Marks(HTMLParser):
    """広告の目印（<!--Ads1--> など）が、どの要素の中にあるか（親要素の class）"""
    def __init__(self):
        super().__init__(); self.stack, self.found = [], {}
    def handle_starttag(self, tag, attrs):
        if tag not in VOID: self.stack.append((tag, dict(attrs).get("class", "")))
    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag: del self.stack[i:]; break
    def handle_comment(self, data):
        if re.fullmatch(r"Ads\d|OffDef", data.strip()):
            self.found.setdefault(data.strip(), []).append([c for _, c in self.stack])


def ads_ok(s):
    p = Marks(); p.feed(s)
    if any(len(p.found.get(k, [])) != 1 for k in ("OffDef", "Ads1", "Ads2", "Ads3")):
        return False
    # Ads1〜3 は手帳（.fh-b27-note）か第1部・第2部のまとまり（.fh-b27-part）の直下＝セクション・カード・付箋・枠の中ではない
    if any(p.found[k][0][-1] not in ("fh-b27-note", "fh-b27-part") for k in ("Ads1", "Ads2", "Ads3")):
        return False
    pos = {k: s.find(f"<!--{k}-->") for k in ("OffDef", "Ads1", "Ads2", "Ads3")}
    at = lambda i: s.find(f'id="{i}"')
    return (pos["OffDef"] < s.find('class="fh-b27"') and at("b27-famous") < pos["Ads1"] < at("b27-2027")
            and at("b27-month") < pos["Ads2"] < at("b27-action") and at("b27-next") < pos["Ads3"] < at("b27-letter"))


def body_text(s):
    _m = re.search(r"<!-- fh-b27:start[^>]*-->", s); a, b = (_m.start() if _m else -1), s.find("<!-- fh-b27:end -->")
    t = s[a:b] if a >= 0 else s
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    return re.sub(r"\s+", "", H.unescape(re.sub(r"<[^>]+>", "", t)))


CHECKS = []
def chk(name, f): CHECKS.append((name, f))

# 3. 現行ページから必ず引き継ぐもの
chk("タイトル（【2027年】M月D日生まれの性格と相性｜…）", lambda s, t, m: re.search(rf"<title>【2027年】{m['month']}月{m['day']}日生まれの性格と相性｜誕生日占い・有名人・運勢", s))
chk("メタディスクリプション", lambda s, t, m: re.search(r'<meta name="description" content="[^"]{60,}', s))
chk("誕生日カード（星座・干支・九星・守護石の概要）", lambda s, t, m: "誕生日カード" in t and m["sign"] in t and "丁未" in t and "九紫火星" in t)
chk("性格・魂のメッセージ", lambda s, t, m: 'id="b27-nature"' in s and "魂のメッセージ" in t)
chk("運命・天からの導き", lambda s, t, m: 'id="b27-2027"' in s and "天からの導き" in t)
chk("分野別5つ（H3）", lambda s, t, m: all(re.search(rf"<h3>{x}", s) for x in ("仕事運", "恋愛運", "金運", "健康運", "人間関係")))
chk("成長・衰え", lambda s, t, m: 'id="b27-grow"' in s and "成長" in t and "衰え" in t)
chk("干支・九星・天体・四半期", lambda s, t, m: 'id="b27-eto"' in s and 'id="b27-season"' in s)
chk("月別グラフ＋良い月／慎重な月のまとめ", lambda s, t, m: 'id="b27-graph"' in s and "慎重" in t)
chk("12か月の運勢（12件）", lambda s, t, m: 'id="b27-month"' in s and all(f"{i}月" in t for i in range(1, 13)))
chk("開運アクション5つ", lambda s, t, m: 'id="b27-action"' in s and len(re.findall(r'<li', s[s.find('id="b27-action"'):s.find('</section>', s.find('id="b27-action"'))])) >= 5)
chk("ラッキーカラー・ナンバー・アイテム5以上・守護石（効果）", lambda s, t, m: all(x in t for x in ("ラッキーカラー", "ラッキーナンバー", "ラッキーアイテム", "守護石")) and s[s.find('id="b27-omamori"'):].count("fh-b27-row") >= 5)
chk("相性：良い5日・気をつけたい3日（一言つき）", lambda s, t, m: "相性の良い誕生日" in t and "気をつけたい誕生日" in t and all(f'href="{url(x["mmdd"])}"' in s for x in m["compat_good"] + m["compat_bad"]))
chk("有名人（日本・海外・肩書き）", lambda s, t, m: 'id="b27-famous"' in s and (not m["famous"]["jp"] or m["famous"]["jp"][0]["name"] in t))
chk("バイオリズムカレンダー（日別表・凡例）", lambda s, t, m: 'id="b27-bio"' in s and "★" in t and "▽" in t)
chk("翌年に向けて・あなたへ", lambda s, t, m: 'id="b27-next"' in s and 'id="b27-letter"' in s)
chk("おすすめの占い（星座・相性診断・MBTI）", lambda s, t, m: f'/{m["sign_en"] if "sign_en" in m else ""}' in s or re.search(r'href="/(aries|taurus|gemini|cancer|leo|virgo|libra|scorpio|sagittarius|capricorn|aquarius|pisces)/"', s))
chk("根拠の注記・最終更新日・作成方針（/about/。/policy/ は使わない）", lambda s, t, m: 'id="b27-about"' in s and "最終更新" in t and 'href="/about/"' in s and "/policy/" not in s)
chk("太字（10〜150か所）", lambda s, t, m: 10 <= len(re.findall(r"<b>|<strong>", s)) <= 150)
# 4. 収益
chk("アフィリエイトはすべて rel=nofollow sponsored", lambda s, t, m: all(re.search(r'rel="nofollow sponsored"', x[2]) for x in aff_links(s)) and (aff_links(s) or not TPL))
chk("仮リンクが0か所（#affiliate-TODO- なし）", lambda s, t, m: "affiliate-TODO" not in s and all(x[1].startswith("https://") for x in aff_links(s)))
chk("アフィリエイトの href は af.moshimo.com か px.a8.net だけ", lambda s, t, m: all(urllib.parse.urlsplit(x[1]).hostname in AFF_HOSTS for x in aff_links(s)))
chk("ひな形のある店だけボタンを出している（Amazon など空の店は0）", lambda s, t, m: all(x[0] in TPL for x in aff_links(s)))
chk("楽天のリンクは楽天の検索ページへ（url= に二重エンコード）", lambda s, t, m: all(
    urllib.parse.unquote(urllib.parse.parse_qs(urllib.parse.urlsplit(x[1]).query)["url"][0]).startswith("https://search.rakuten.co.jp/search/mall/")
    for x in aff_links(s) if x[0] == "rakuten"))
chk("各リンクの直後に表示計測の画像", lambda s, t, m: all(x[3].startswith(TPL[x[0]]["impression"]) for x in aff_links(s) if x[0] in TPL))
chk("「広告を含みます」がある", lambda s, t, m: t.count("広告") >= 2)
chk("誕生日プレゼント4枠", lambda s, t, m: s.count('class="fh-b27-gift"') == 4)
chk("プレゼントとお守りリストで同じ商品が無い", lambda s, t, m: not (set(re.findall(r'class="fh-b27-gift"><small>[^<]*</small><b>([^<]+)', s)) & set(re.findall(r'<div class="fh-b27-who"><small>.*?</small><b>([^<]+)</b>', s[s.find('id="b27-omamori"'):s.find('id="b27-gift"')]))))
chk("電話占いの案内が1か所（ひな形があるとき）", lambda s, t, m: len([x for x in aff_links(s) if x[0] == "phone"]) == (1 if "phone" in TPL else 0))
chk("電話占いのボタンに金額・特典の言葉が無い", lambda s, t, m: not any(re.search(r"円|特典|初回|無料|割引|%|％|ポイント", x[4]) for x in aff_links(s) if x[0] == "phone"))
# 確認4：テーマ・プラグインとのぶつかり
chk("本文に h1 が無い（ページの題は p.fh-b27-title）", lambda s, t, m: not re.search(r"<h1[\s>]", s, re.I) and 'class="fh-b27-title"' in s)
chk("広告の位置の目印（OffDef・Ads1〜3、カード・付箋の外）", lambda s, t, m: ads_ok(s))
# 5. サイト内の行き来
for path in ("/kokoro/", "/compatibility/", "/enmusubi/pair/", "/mbti-compatibility/", "/animal-color/", "/kaiun/", "/dream/", "/mbti/", "/seinengappi/"):
    chk(f"リンク {path}", (lambda p: (lambda s, t, m: f'href="{p}' in s))(path))
chk("前後の日へのリンク（/366uranai/MM-DD/）", lambda s, t, m: f'href="{url(m["prev"])}"' in s and f'href="{url(m["next"])}"' in s)
chk("誕生日ページへのリンクはすべて /366uranai/MM-DD/ の形（/birthday/ なし）", lambda s, t, m: "/birthday/" not in s and all(
    re.fullmatch(r"\d{2}-\d{2}", x) and x.replace("-", "") in M for x in re.findall(r'href="/366uranai/([^"]*)/"', s)) and re.search(r'href="/366uranai/\d{2}-\d{2}/"', s))
chk("canonical が /366uranai/MM-DD/", lambda s, t, m: f'<link rel="canonical" href="https://www.uranai.epoch-compass.com{url(m["key"])}">' in s)
# 本人の決定
chk("星座の境目の注記（境目の日だけ）", lambda s, t, m: (not m["sign_border"]) or "生まれた年" in t)
chk("誕生日石・誕生色に「当サイト独自の選び方」", lambda s, t, m: t.count("当サイト独自") >= 1)
chk("誕生花の出典（日本花普及センター）", lambda s, t, m: "日本花普及センター" in t)
chk("相性の見出しに「ぶつかる」を使っていない", lambda s, t, m: not re.search(r"<h[23][^>]*>[^<]*ぶつか", s))
chk("「動物占い」「六星占術」を使っていない", lambda s, t, m: "動物占い" not in t and "六星" not in t)
chk("本文に度数の数字を出していない（この占いについて以外）", lambda s, t, m: not re.search(r"(?<!東経)(?<!マイナス)(?<![0-9])[0-9０-９]+度", body_text(s[:s.find('id="b27-about"')])))
chk("「！」は3回まで", lambda s, t, m: t.count("！") + t.count("!") <= 3 + body_text(s).count("!=") )
chk("文章が入っている", lambda s, t, m: "文章は未作成" not in t)
chk("CSSは fh-b27- 接頭辞のみ", lambda s, t, m: all(c.startswith("fh-b27") for cl in re.findall(r'class="([^"]+)"', s) for c in cl.split()))

res = collections.defaultdict(list)
lens = []
for f in files:
    k = os.path.basename(f)[:4]
    s = open(f, encoding="utf-8").read()
    t = body_text(s)
    lens.append(len(t))
    m = dict(M[k]); m["sign_en"] = None; m["key"] = k
    for name, fn in CHECKS:
        try:
            ok = bool(fn(s, t, m))
        except Exception as e:
            ok = False
        if not ok: res[name].append(k)
L = [f"# ページ点検（{d}・{len(files)}ページ）\n", f"`python work/scripts/check_pages.py{' --dir ' + d if d != 'html' else ''}` で再生成。\n",
     "| 点検項目 | 結果 | 引っかかったページ（先頭10件） |", "|---|---|---|"]
for name, _ in CHECKS:
    bad = res.get(name, [])
    L.append(f"| {name} | {'✅' if not bad else '⚠ ' + str(len(bad))} | {' '.join(bad[:10])} |")
if lens: L.append(f"\n- ページ全体の字数：最小 {min(lens)}／平均 {sum(lens)//len(lens)}／最大 {max(lens)}（現行は約7,500字）")
# アフィリエイトの入った数（ページから数えた数と、build_html.py --all の数）
cnt = collections.Counter()
for f in files:
    for x in aff_links(open(f, encoding="utf-8").read()):
        cnt[x[0] or "（店不明）"] += 1
_cp = os.path.join(W, "reports", "affiliate_count.json")
bc = json.load(open(_cp, encoding="utf-8")) if d == "html" and os.path.exists(_cp) else None
L.append("\n## アフィリエイトの入った数\n")
L.append("| 店 | ひな形 | ページに入ったリンク | ボタンを出さなかった数（ひな形が無いため） |")
L.append("|---|---|---|---|")
shops = sorted(set(cnt) | set(TPL) | set((bc or {}).get("skipped_buttons", {})))
for sh in shops:
    sk = (bc or {}).get("skipped_buttons", {}).get(sh, "—")
    L.append(f"| {SHOP_NAME.get(sh, sh)} | {'あり' if sh in TPL else 'なし（空）'} | {cnt[sh]}か所 | {sk}{'個' if sk != '—' else ''} |")
L.append(f"\n- 合計 {sum(cnt.values())}か所・仮リンク（#affiliate-TODO-）{sum(open(f, encoding='utf-8').read().count('affiliate-TODO') for f in files)}か所")
if bc is not None:
    same = all(bc.get("links", {}).get(sh, 0) == cnt[sh] for sh in shops)
    L.append(f"- build_html.py --all の数との一致：{'✅' if same else '⚠ 食い違い（build_html.py --all を流し直す）'}")
open(os.path.join(W, "reports", "page_check.md" if d == "html" else f"page_check_{d}.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))
