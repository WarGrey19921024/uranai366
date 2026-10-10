"""フェーズ9：366ページのHTMLを生成する。

使い方（Python は pyswisseph 入りの仮想環境で）:
  python work/scripts/build_html.py 0101 0229 0120     # 指定した日 → work/out/html/MMDD.html
  python work/scripts/build_html.py --all              # 366日すべて
  python work/scripts/build_html.py --sample 0101      # 確認用 → work/out/sample/MMDD.html（相対パスの共通CSS/JS）
  オプション: --text-dir DIR（文章JSONの置き場所。既定 work/text）／--updated 2026-10-10（最終更新日）

出力:
  work/out/assets/fh-b27.css            共通CSS（templates/fh-b27.css をそのまま）
  work/out/assets/fh-b27.js             共通JS（templates/fh-b27.js に知識ベースの表・2027年の月盤を埋め込む）
  work/out/assets/fh-b27-setsuiri.js    節入り日時（1930〜2030年。setsuiri_1900_2100.json から）
  work/out/assets/fh-b27-kyureki.js     旧暦の月の表（1930〜2030年。kyureki_1900_2030.json から月の長さと月番号だけ）
  work/out/html/MMDD.html               ページ（<!-- fh-b27:start --> 〜 <!-- fh-b27:end --> が WordPress に貼る本文）

材料:
  work/data/materials_366.json（計算値・誕生日もの・記念日・相性・スコア・有名人）
  work/text/<星座英名>.json（文章。形は work/text/_書き方.md の2章。無い日は「（文章は未作成）」）
  work/knowledge/*.md（節気の意味・九星・十干・27宿・マヤ暦・数秘のキーワード表）
"""
import argparse, datetime as dt, glob, html, json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, ".."))
DATA = os.path.join(WORK, "data")
KNOW = os.path.join(WORK, "knowledge")
OUT = os.path.join(WORK, "out")
TPL = os.path.join(HERE, "templates")
sys.path.insert(0, HERE)
import calc_kanshi_kyusei as KK  # noqa: E402

WP_ASSET = "/wp-content/uploads/fh-b27/"
FONTS = "https://fonts.googleapis.com/css2?family=Klee+One:wght@400;600&family=Shippori+Mincho:wght@600;800&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap"
YEAR_MIN, YEAR_MAX = 1930, 2020
SIGN_EN = {"牡羊座": "aries", "牡牛座": "taurus", "双子座": "gemini", "蟹座": "cancer", "獅子座": "leo",
           "乙女座": "virgo", "天秤座": "libra", "蠍座": "scorpio", "射手座": "sagittarius",
           "山羊座": "capricorn", "水瓶座": "aquarius", "魚座": "pisces"}
SIGN_HIRA = {"牡羊座": "おひつじ座", "牡牛座": "おうし座", "双子座": "ふたご座", "蟹座": "かに座", "獅子座": "しし座",
             "乙女座": "おとめ座", "天秤座": "てんびん座", "蠍座": "さそり座", "射手座": "いて座",
             "山羊座": "やぎ座", "水瓶座": "みずがめ座", "魚座": "うお座"}
ELEM_GOGYO = {"火": "火", "地": "土", "風": "木", "水": "水"}
FIELDS = [("仕事", "仕事運"), ("恋愛", "恋愛運"), ("金運", "金運"), ("健康", "健康運"), ("人間関係", "人間関係")]
DREAM = [("crush", "好きな人が夢に出てきたら？"), ("confession", "告白される夢・する夢の意味は？"),
         ("ex-lover", "元恋人が夢に出てきたら？")]
MARK_CLS = {"◎": "good", "○": "ok", "△": "care"}
MISSING = "（文章は未作成）"


# ---------------------------------------------------------------- 文字の処理
def esc(s):
    return html.escape(str(s), quote=True)


def inline(s):
    """本文の **太字** → <b>、==マーカー== → <mark class="fh-b27-mk">（先にエスケープ）"""
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"==(.+?)==", r'<mark class="fh-b27-mk">\1</mark>', s)
    return s


def miss_p():
    return f'<p class="fh-b27-missing">{MISSING}</p>'


def paras(v):
    """文字列（改行で段落）または文字列のリスト → <p>…</p>。無ければ未作成の表示"""
    if not v:
        return miss_p()
    items = v if isinstance(v, list) else str(v).split("\n")
    out = [f"<p>{inline(x.strip())}</p>" for x in items if str(x).strip()]
    return "\n".join(out) if out else miss_p()


def span(v):
    return inline(v) if v else f'<span class="fh-b27-missing">{MISSING}</span>'


def md_label(mmdd):
    return f"{int(mmdd[:2])}月{int(mmdd[2:])}日"


def months_label(ms):
    return "・".join(f"{m}月" for m in sorted(ms))


# ---------------------------------------------------------------- 知識ベースの表
def md_table(path, heading):
    """heading を含む見出しの直後にある表の行（セルのリスト）"""
    lines = open(path, encoding="utf-8").read().split("\n")
    rows, inside = [], False
    for ln in lines:
        if ln.startswith("#"):
            if inside and rows:
                break
            inside = heading in ln
            continue
        if inside and ln.startswith("|"):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if set("".join(cells)) <= set("-: "):
                continue
            rows.append(cells)
    return rows[1:]  # 先頭は見出し行


def knowledge():
    k = {}
    k["sekki"] = {r[0]: r[-1] for r in md_table(os.path.join(KNOW, "03_二十四節気・七十二候.md"), "③-1")}
    k["kou_pos"] = {r[3]: r[2] for r in md_table(os.path.join(KNOW, "03_二十四節気・七十二候.md"), "③-2")}
    k["kyuseiKw"] = {i + 1: r[1] for i, r in enumerate(md_table(os.path.join(KNOW, "04_九星気学.md"), "3-1"))}
    k["nikkan"] = {r[0]: f"{r[4]}（{r[5]}）" for r in md_table(os.path.join(KNOW, "05_干支・五行・四柱推命.md"), "1-1. 十干")}
    k["shukuKw"] = {r[0]: r[2] for r in md_table(os.path.join(KNOW, "06_宿曜.md"), "3-1")}
    maya = os.path.join(KNOW, "07_マヤ暦.md")
    k["sealKw"] = {int(r[0]): r[2] for r in md_table(maya, "20の太陽の紋章")}
    k["toneKw"] = {int(r[0]): r[2] for r in md_table(maya, "13の銀河の音")}
    k["lpKw"] = {int(r[0]): r[1] for r in md_table(os.path.join(KNOW, "08_数秘術.md"), "1〜9・11・22・33")}
    return k


def stones():
    s = json.load(open(os.path.join(DATA, "src_stones.json"), encoding="utf-8"))["stones"]
    idx = {}
    for x in s:
        idx[x["name"]] = x
        for a in x.get("aka", []):
            idx.setdefault(a, x)
    return idx


def split_stones(txt, idx):
    """「アメシスト・クリソベリル・キャッツアイ」→ カタログにある名前で区切る"""
    tok, out, i = txt.split("・"), [], 0
    while i < len(tok):
        if i + 1 < len(tok) and f"{tok[i]}・{tok[i+1]}" in idx:
            out.append(f"{tok[i]}・{tok[i+1]}")
            i += 2
        else:
            out.append(tok[i])
            i += 1
    return out


# ---------------------------------------------------------------- 共通の値（2027年）
def year_consts():
    t = dt.datetime(2027, 6, 1, 12, 0)
    yi = KK.year_index(t)
    t8 = dt.datetime(2028, 6, 1, 12, 0)
    yi8 = KK.year_index(t8)
    return {
        "eto": KK.kanshi(yi), "eto_yomi": KK.KAN_YOMI[yi % 10] + KK.SHI_YOMI[yi % 12],
        "eto2028": KK.kanshi(yi8), "eto2028_yomi": KK.KAN_YOMI[yi8 % 10] + KK.SHI_YOMI[yi8 % 12],
        "center": KK.honmei(t), "star": KK.KYUSEI[KK.honmei(t)],
        "month_star": [KK.month_star(dt.datetime(2027, m, 15, 12, 0)) for m in range(1, 13)],
    }


def sekki_2027():
    """月ごとの「節」の名前（季節の流れの小見出し）"""
    rows = json.load(open(os.path.join(DATA, "sekki_2027.json"), encoding="utf-8"))
    out = {}
    for r in rows:
        if r.get("sekki_kind") == "節":
            out[int(r["date"][:2])] = r["sekki"]
    return out


def star_rows():
    """2027年の主な星の動き（全ページ共通の部品。planets_2027.json の計算値から）"""
    p = json.load(open(os.path.join(DATA, "planets_2027.json"), encoding="utf-8"))
    rows = []
    for e in p["eclipses"]:
        if "日食" in e["type"]:
            d = dt.datetime.strptime(e["jst_max"], "%Y-%m-%d %H:%M")
            rows.append((d, "good", f"{d.month}月{d.day}日ごろ {e['type']}",
                         f"{e['sign']}で起こる日食（{e['japan']}）。区切りと仕切り直しの合図とされます。"))
    slow = {"木星": "幸運と広がりの星", "土星": "試練と積み重ねの星"}
    moved = set()
    for e in p["ingress"]:
        if e["planet"] in slow and not e["retrograde"]:
            d = dt.datetime.strptime(e["jst"], "%Y-%m-%d %H:%M")
            moved.add(e["planet"])
            rows.append((d, "good", f"{d.month}月{d.day}日ごろ {e['planet']}が{e['to']}へ",
                         f"{slow[e['planet']]}が{e['to']}に移ります。"))
    rows.sort()
    for pl in ("木星", "土星"):
        if pl not in moved:
            sign = p["start_positions"][pl].split()[0]
            rows.append((None, "ok", f"{pl}は一年を通して{sign}", f"{slow[pl]}が、一年じゅう{sign}にとどまります。"))
    return [(c, t, s) for _, c, t, s in rows]


# ---------------------------------------------------------------- 日付の範囲（七十二候・デーカン・星座）
def ranges(mats, keyf):
    order = sorted(mats)
    groups = []
    for k in order:
        key = keyf(mats[k])
        if groups and groups[-1][0] == key:
            groups[-1][1].append(k)
        else:
            groups.append([key, [k]])
    if len(groups) > 1 and groups[0][0] == groups[-1][0]:
        groups[0][1] = groups[-1][1] + groups[0][1]
        groups.pop()
    out = {}
    for key, ks in groups:
        a, b = ks[0], ks[-1]
        if a == b:
            lab = md_label(a)
        elif a[:2] == b[:2]:
            lab = f"{md_label(a)}〜{int(b[2:])}日"
        else:
            lab = f"{md_label(a)}〜{md_label(b)}"
        short = f"{int(a[:2])}/{int(a[2:])}〜{int(b[:2])}/{int(b[2:])}"
        for k in ks:
            out[k] = (lab, short)
    return out


# ---------------------------------------------------------------- 文章JSON
def load_texts(text_dir):
    texts = {}
    for p in sorted(glob.glob(os.path.join(text_dir, "*.json"))):
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception as e:  # 壊れたファイルでも他の日は作る
            print(f"警告: {p} を読めません: {e}", file=sys.stderr)
            continue
        for k, v in d.items():
            if re.fullmatch(r"\d{4}", k) and isinstance(v, dict):
                texts[k] = v
    return texts


# ---------------------------------------------------------------- アセット
def build_assets(gen):
    adir = os.path.join(OUT, "assets")
    os.makedirs(adir, exist_ok=True)
    shutil.copyfile(os.path.join(TPL, "fh-b27.css"), os.path.join(adir, "fh-b27.css"))
    js = open(os.path.join(TPL, "fh-b27.js"), encoding="utf-8").read()
    js = js.replace("/*@GEN@*/", "var GEN=" + json.dumps(gen, ensure_ascii=False, separators=(",", ":")) + ";")
    open(os.path.join(adir, "fh-b27.js"), "w", encoding="utf-8").write(js)
    # 節入り（1930〜2030年、各年12個 "MMDDhhmm"）
    st = KK.setsu()
    rows = []
    for y in range(1930, 2031):
        s = ""
        for name in KK.SETSU_ORDER:
            v = st[str(y)][name]  # "YYYY-MM-DD HH:MM"
            assert v[:4] == str(y), (y, name, v)
            s += v[5:7] + v[8:10] + v[11:13] + v[14:16]
        rows.append(s)
    with open(os.path.join(adir, "fh-b27-setsuiri.js"), "w", encoding="utf-8") as f:
        f.write("/* 節入り日時（日本時間）1930〜2030年。各年 小寒・立春・啓蟄・清明・立夏・芒種・小暑・立秋・白露・寒露・立冬・大雪 の順に MMDDhhmm。"
                "出典: work/data/setsuiri_1900_2100.json（calc_sekki.py）*/\n")
        f.write("window.FH_B27_SETSU=" + json.dumps({"y0": 1930, "d": rows}, separators=(",", ":")) + ";\n")
    # 旧暦：1930-01-01 を含む月から 2030-12-31 まで、月ごとに長さ（9=29日/0=30日）と月番号（a-l、閏月は A-L）
    ky = json.load(open(os.path.join(DATA, "kyureki_1900_2030.json"), encoding="utf-8"))
    d0, d1 = dt.date(1930, 1, 1), dt.date(2030, 12, 31)
    d = d0 - dt.timedelta(days=ky[d0.isoformat()][3] - 1)  # 月の1日に戻す
    start, lens, mons = d, "", ""
    while d <= d1:
        y, m, leap, day = ky[d.isoformat()]
        assert day == 1, d
        n = 0
        while True:
            n += 1
            nd = d + dt.timedelta(days=n)
            if nd.isoformat() not in ky or ky[nd.isoformat()][3] == 1:
                break
        if nd.isoformat() not in ky:  # 表の最後の月（2030年12月25日〜）は終わりが表の外。日数は使わない範囲なので30日で閉じる
            n = 30
            nd = d + dt.timedelta(days=30)
        assert n in (29, 30), (d, n)
        lens += "9" if n == 29 else "0"
        mons += (chr(64 + m) if leap else chr(96 + m))
        d = nd
    assert d > d1, f"旧暦の表が {d} で終わっています"
    with open(os.path.join(adir, "fh-b27-kyureki.js"), "w", encoding="utf-8") as f:
        f.write("/* 旧暦の月の表（宿曜の本命宿用）1930〜2030年。s=最初の月の1日（新暦）、len=各月の日数（9=29日・0=30日）、"
                "mon=月番号（a=1月…l=12月、大文字は閏月）。出典: work/data/kyureki_1900_2030.json（calc_kyureki.py）*/\n")
        f.write("window.FH_B27_KYUREKI=" + json.dumps({"s": start.isoformat(), "len": lens, "mon": mons},
                                                       separators=(",", ":")) + ";\n")


# ---------------------------------------------------------------- ページ
def aff(label):
    return f'href="#" rel="nofollow sponsored" data-aff="[{esc(label)}]"'


def render(mmdd, mats, texts, ctx, sample=False, updated="2026-10-10"):
    e = mats[mmdd]
    M, D = e["month"], e["day"]
    md = f"{M}月{D}日"
    T = texts.get(mmdd, {})
    fx, yr = T.get("fixed", {}) or {}, T.get("y2027", {}) or {}
    Y = ctx["year"]
    K = ctx["know"]
    sign, en = e["sign"], SIGN_EN[e["sign"]]
    order = ctx["order"]
    no = order.index(mmdd) + 1
    kou_pos = K["kou_pos"].get(e["kou"], "")
    kou_rng = ctx["kou_rng"][mmdd][0]
    dec_rng = ctx["dec_rng"][mmdd][0]
    sign_rng = ctx["sign_rng"][mmdd][1]
    flower = e["flower"]
    st_idx = ctx["stones"]
    bm_list = split_stones(e["birthstone_month"], st_idx)
    bm_first = st_idx.get(bm_list[0], {})
    bd_stone = st_idx.get(e["birthday_stone"]["name"], {})
    col_yomi, col_hex, col_desc = (e["birthday_color"]["note"].split("／") + ["", "", ""])[:3]
    sc = e["scores"]
    warnings = []

    title = f"【2027年】{md}生まれの性格と相性｜誕生日占い・有名人・運勢"
    desc = (f"{md}生まれの性格と2027年の運勢。{sign}・七十二候「{e['kou']}」・誕生花の{flower['flower']}から読む本質と、"
            f"{Y['eto']}・{Y['star']}の年の月ごとの運勢、ラッキーカラー、相性の良い誕生日、同じ誕生日の有名人まで。")

    H = []
    a = H.append
    base = [
        {"key": "star", "name": "星座", "color": "#3987e5", "values": sc["astro"]},
        {"key": "num", "name": "数秘", "color": "#d95926", "values": sc["num"]},
        {"key": "gogyo", "name": "暦の五行", "color": "#199e70", "values": sc["gogyo"]},
    ]
    a(f'<div class="fh-b27" data-m="{M}" data-d="{D}" data-base="{esc(json.dumps(base, separators=(",", ":")))}">')
    a('<div class="fh-b27-note">')

    # ヒーロー
    lead_first = e["kou_meaning"].split("。")[0] + "。"
    a(f'''<header class="fh-b27-hero">
  <div class="fh-b27-kou" aria-hidden="true">{esc(e["kou"])}</div>
  <div class="fh-b27-hero-body">
    <span class="fh-b27-tape">2027年版 誕生日占い</span>
    <h1>{md}生まれの性格と<br>2027年の運勢</h1>
    <p class="fh-b27-lead">{esc(e["sekki"])}の{esc(kou_pos)}「{esc(e["kou"])}（{esc(e["kou_yomi"])}）」。{esc(lead_first)}この頃に生まれた人の、変わらない本質と、2027年の歩き方を読み解きます。</p>
  </div>
</header>''')

    # 誕生日カード
    card_title = fx.get("card_title") or f"{e['kou']}の生まれ"
    a(f'''<div class="fh-b27-cardwrap">
  <div class="fh-b27-card-outer">
    <div class="fh-b27-card" data-mmdd="{mmdd}" data-label="{M}/{D}" data-no="No.{no:03d} ／ 366" data-title="{esc(card_title)}">
      <div class="fh-b27-card-top"><span class="fh-b27-hand">誕生日カード</span><span>No.{no:03d} ／ 366</span></div>
      <div class="fh-b27-card-name"><span class="d">{M}/{D}</span><span class="t">{esc(card_title)}</span></div>
      <dl>
        <div><dt>星座</dt><dd>{esc(sign)}（第{e["decan"]}）</dd></div>
        <div><dt>七十二候</dt><dd>{esc(e["kou"])}</dd></div>
        <div><dt>誕生花</dt><dd>{esc(flower["flower"])}</dd></div>
        <div><dt>誕生石</dt><dd>{esc(bm_list[0])}</dd></div>
        <div><dt>誕生日の数</dt><dd>{e["birthday_number"]}</dd></div>
        <div><dt>2027年の数</dt><dd>{e["py2027"]}</dd></div>
        <div><dt>2027年</dt><dd>{esc(Y["eto"])}</dd></div>
        <div><dt>2027年の中宮</dt><dd>{esc(Y["star"])}</dd></div>
      </dl>
      <a class="fh-b27-btn" href="#" data-fh-action="save-card">カードを画像で保存</a>
    </div>
  </div>
</div>''')
    if e["sign_border"]:
        other = "・".join(e["sign_border_other"])
        a(f'<p class="fh-b27-signnote">{md}は星座の境目の日です。生まれた年と時刻によっては<b>{esc(other)}</b>の場合があります（太陽が星座を移る時刻は年によって違うため）。</p>')

    # 生まれ年
    a(f'''<div class="fh-b27-yearbar" id="b27-yearbar">
  <div class="fh-b27-pick"><label for="fh-b27-y">生まれ年（任意）</label><select id="fh-b27-y" data-fh-year></select></div>
  <p class="fh-b27-small">選ぶと、このページの3か所が「あなた専用」に変わります。<a href="#b27-graph">①月別グラフ</a>に九星とバイオリズムの線が加わる／<a href="#b27-year">②生まれ年でわかること</a>（命式・宿曜・マヤ暦など）／<a href="#b27-bio">③バイオリズムカレンダー</a>。生まれ年は送信・保存しません。</p>
</div>''')

    # 目次
    a(f'''<nav class="fh-b27-toc" aria-label="目次">
  <strong>このページの目次</strong>
  <ol>
    <li><a href="#b27-nature">{md}生まれの性格（ずっと変わらない本質）</a>
      <ol>
        <li><a href="#b27-koyomi">この日の暦と星</a></li>
        <li><a href="#b27-mono">誕生花・誕生石・記念日</a></li>
        <li><a href="#b27-aisho">相性の良い誕生日</a></li>
        <li><a href="#b27-famous">同じ誕生日の有名人</a></li>
      </ol>
    </li>
    <li><a href="#b27-2027">2027年の運命</a>
      <ol>
        <li><a href="#b27-field">仕事・恋愛・金運・健康・人間関係</a></li>
        <li><a href="#b27-graph">占いごとの月別グラフ</a></li>
        <li><a href="#b27-month">12か月の運勢</a></li>
        <li><a href="#b27-omamori">ラッキーカラー・ラッキーアイテム</a></li>
        <li><a href="#b27-gift">誕生日プレゼント</a></li>
      </ol>
    </li>
    <li><a href="#b27-today">{esc(ctx["bday_label"])}の運勢</a></li>
    <li><a href="#b27-year">生まれ年でわかること（九星・四柱推命・宿曜・マヤ暦）</a></li>
    <li><a href="#b27-bio">2027年バイオリズムカレンダー</a></li>
    <li><a href="#b27-next">2028年に向けて</a></li>
  </ol>
</nav>''')

    # ===== 第1部
    a('<div class="fh-b27-part">\n  <div class="fh-b27-partlabel">第1部 ずっと変わらない本質</div>')
    st = fx.get("strengths") or []
    ca = fx.get("cautions") or []
    a(f'''<section class="fh-b27-sec" id="b27-nature">
  <h2><span class="n">1</span>{md}生まれの性格</h2>
  {paras(fx.get("personality"))}
  <div class="fh-b27-stickies">
    <div class="fh-b27-sticky y"><strong>いいところ</strong><span>{"／".join(inline(x) for x in st) if st else MISSING}</span></div>
    <div class="fh-b27-sticky b"><strong>気をつけたいところ</strong><span>{"／".join(inline(x) for x in ca) if ca else MISSING}</span></div>
  </div>
  <h3>魂のメッセージ</h3>
  {paras(fx.get("soul_message"))}
  <a class="fh-b27-next" href="/kokoro/"><small>性格をもっと深く知りたい人へ</small><b>心コンパスでエニアグラム・ビッグファイブを試す →</b></a>
</section>''')

    # 2 暦と星
    sekki_dd = K["sekki"].get(e["sekki"], "")
    if e.get("sekki_day"):
        sekki_dd = f"暦の上では、この日が「{e['sekki_day']}」の始まりの日です（年によって1日前後します）。" + sekki_dd
    kou_dd = e["kou_meaning"]
    if e.get("kou_border") and e.get("kou_alt"):
        kou_dd += f"（生まれた年によっては「{'」「'.join(e['kou_alt'])}」の時期に当たります）"
    bn = e["birthday_number_info"]
    bn_dd = f"「{bn['keyword']}」の数。" + bn["text"].split("。")[0] + "。"
    a(f'''<section class="fh-b27-sec" id="b27-koyomi">
  <h2><span class="n">2</span>{md}の暦と星</h2>
  {paras(fx.get("koyomi"))}
  <dl class="fh-b27-koyomi">
    <div><dt><b>{esc(e["sekki"])}</b>二十四節気</dt><dd>{esc(sekki_dd)}</dd></div>
    <div><dt><b>{esc(e["kou"])}</b>七十二候（{kou_rng}ごろ）</dt><dd>{esc(kou_dd)}</dd></div>
    <div><dt><b>{esc(sign)}・第{e["decan"]}デーカン</b>星座（{dec_rng}ごろ）</dt><dd>{esc(e["decan_meaning"])}</dd></div>
    <div><dt><b>{e["birthday_number"]}</b>誕生日の数（数秘）</dt><dd>{esc(bn_dd)}</dd></div>
  </dl>
</section>''')

    # 3 誕生日もの・記念日
    def sw(hexv):
        return f'<span class="sw" style="background:{esc(hexv)}"></span>' if hexv and re.fullmatch(r"#[0-9A-Fa-f]{6}", hexv) else ""
    a(f'''<section class="fh-b27-sec" id="b27-mono">
  <h2><span class="n">3</span>{md}の誕生花・誕生石・誕生色</h2>
  <div class="fh-b27-mono">
    <div class="fh-b27-mono-card"><small>誕生花</small><b>{esc(flower["flower"])}</b><p>花言葉は「{esc(flower["hanakotoba"])}」。</p><span class="fh-b27-src">出典：日本花普及センター「誕生花」一覧</span></div>
    <div class="fh-b27-mono-card">{sw(bm_first.get("color_hex"))}<small>誕生石（{M}月）</small><b>{esc(e["birthstone_month"])}</b><p>{esc(bm_first.get("meaning", ""))}</p></div>
    <div class="fh-b27-mono-card">{sw(bd_stone.get("color_hex"))}<small>誕生日石（{md}）</small><b>{esc(e["birthday_stone"]["name"])}<em>当サイト独自の選び方</em></b><p>{esc(e["birthday_stone"]["note"])}</p></div>
    <div class="fh-b27-mono-card">{sw(col_hex)}<small>誕生色（{md}）</small><b>{esc(e["birthday_color"]["name"])}（{esc(col_yomi)}）<em>当サイト独自の選び方</em></b><p>{esc(col_desc)}</p></div>
  </div>
  {paras(fx.get("items"))}
  <p class="fh-b27-small">誕生日石と誕生色は、当サイト独自の選び方で決めています（決め方はページ下の「この占いについて」）。</p>''')
    evs = e.get("events") or []
    if evs:
        a(f'  <h3>{md}の記念日・できごと</h3>\n  <div class="fh-b27-rows">')
        for ev in evs:
            m = re.match(r"^(\d{3,4})年[。、]?", ev["text"])
            yl = f"{m.group(1)}年" if m else "毎年"
            body = ev["text"][m.end():] if m else ev["text"]
            a(f'    <div class="fh-b27-row"><span class="fh-b27-year">{yl}</span><div class="who"><b>{esc(ev["title"])}</b><small>{esc(body)}</small></div></div>')
        a("  </div>")
        if fx.get("events_note"):
            a("  " + paras(fx.get("events_note")))
    elif fx.get("events_note"):
        a(f"  <h3>{md}のころの季節の話題</h3>\n  " + paras(fx.get("events_note")))
    a("</section>")

    # 4 相性
    def compat_list(src, txt):
        tmap = {c.get("mmdd"): c.get("text") for c in (txt or []) if isinstance(c, dict)}
        out = []
        for c in src:
            o = mats[c["mmdd"]]
            out.append(f'<li>{md_label(c["mmdd"])}<small>{esc(o["sign"])}・誕生日の数{o["birthday_number"]}</small><br>'
                       f'<span class="fh-b27-why">{span(tmap.get(c["mmdd"]))}</span></li>')
        return "\n          ".join(out)
    a(f'''<section class="fh-b27-sec" id="b27-aisho">
  <h2><span class="n">4</span>相性の良い誕生日・気をつけたい誕生日</h2>
  <div class="fh-b27-two">
    <div class="fh-b27-box">
      <strong>相性の良い誕生日</strong>
      <ul>
          {compat_list(e["compat_good"], fx.get("compat_good"))}
      </ul>
    </div>
    <div class="fh-b27-box">
      <strong>気をつけたい誕生日</strong>
      <ul>
          {compat_list(e["compat_bad"], fx.get("compat_bad"))}
      </ul>
    </div>
  </div>
  <p class="fh-b27-small">選び方：生まれた日の太陽の位置どうしの関係と、誕生日の数の組み合わせから選んでいます（くわしくはページ下の「この占いについて」）。</p>
  <div class="fh-b27-nexts"><a class="fh-b27-next" href="/compatibility/"><small>人生予報</small><b>2人の生年月日で相性を見る →</b></a><a class="fh-b27-next" href="/enmusubi/pair/"><small>縁結び診断室</small><b>ご縁の相性診断 →</b></a><a class="fh-b27-next" href="/mbti-compatibility/"><small>人生予報</small><b>MBTI相性占い →</b></a></div>
</section>''')

    # 5 有名人
    def fam(lst):
        return "\n        ".join(f'<li>{esc(p["name"])}<small>{esc(p["job"])}</small></li>' for p in lst) or "<li>—</li>"
    a(f'''<section class="fh-b27-sec" id="b27-famous">
  <h2><span class="n">5</span>{md}生まれの有名人</h2>
  {paras(fx.get("famous_note"))}
  <div class="fh-b27-two">
    <div class="fh-b27-box">
      <strong>日本</strong>
      <ul>
        {fam(e["famous"]["jp"])}
      </ul>
    </div>
    <div class="fh-b27-box">
      <strong>海外</strong>
      <ul>
        {fam(e["famous"]["world"])}
      </ul>
    </div>
  </div>
</section>''')
    a("</div>")

    # ===== 第2部
    a('<div class="fh-b27-part">\n  <div class="fh-b27-partlabel">第2部 2027年の運勢</div>')
    a(f'''<section class="fh-b27-sec" id="b27-2027">
  <h2><span class="n">6</span>2027年の運命</h2>
  {paras(yr.get("fate"))}
  <p>3つの占いを重ねると、山場は<span class="fh-b27-em">{months_label(e["peak_months"])}</span>。慎重にしたいのは<span class="fh-b27-em">{months_label(e["low_months"])}</span>です（<a href="#b27-graph">月別グラフ</a>）。</p>
  <h3>天からの導き</h3>
  {paras(yr.get("guidance"))}
</section>''')

    fields_txt = yr.get("fields") or {}
    a('<section class="fh-b27-sec" id="b27-field">\n  <h2><span class="n">7</span>分野別の運勢</h2>')
    dream = DREAM[(no - 1) % len(DREAM)]
    for key, lab in FIELDS:
        a(f'  <h3>{lab}</h3>\n  <p class="fh-b27-fieldmeta">いちばん良い月：{e["field_peak"][key]}月 ／ 慎重な月：{e["field_low"][key]}月</p>')
        a("  " + paras(fields_txt.get(key)))
        if key == "恋愛":
            a(f'  <p class="fh-b27-small"><a href="/dream/keyword/{dream[0]}/">{dream[1]}（夢解き図鑑）→</a></p>')
    a("</section>")

    a(f'''<section class="fh-b27-sec" id="b27-grow">
  <h2><span class="n">8</span>2027年の成長と衰え</h2>
  <div class="fh-b27-stickies">
    <div class="fh-b27-sticky y"><h3 class="fh-b27-sth">成長（伸ばしたいこと）</h3><span>{span(yr.get("growth"))}</span></div>
    <div class="fh-b27-sticky b"><h3 class="fh-b27-sth">衰え（気をつけたいこと）</h3><span>{span(yr.get("decline"))}</span></div>
  </div>
</section>''')

    rows = "\n    ".join(f'<div class="fh-b27-row"><span class="fh-b27-mark {c}">☆</span><div class="who"><b>{esc(t)}</b><small>{esc(s)}</small></div></div>'
                         for c, t, s in ctx["stars"])
    a(f'''<section class="fh-b27-sec" id="b27-eto">
  <h2><span class="n">9</span>2027年の干支・九星・星の動き</h2>
  <h3>{esc(Y["eto"])}（{esc(Y["eto_yomi"])}）の年</h3>
  {paras(yr.get("eto"))}
  <h3>{esc(Y["star"])}が中宮に入る年</h3>
  {paras(yr.get("kyusei"))}
  <h3>2027年の主な星の動き</h3>
  <div class="fh-b27-rows">
    {rows}
  </div>
  {paras(yr.get("stars"))}
</section>''')

    seas = yr.get("seasons") or []
    sk = ctx["setsu_by_month"]
    tl = []
    for i, (lab, col) in enumerate([("冬 1〜3月", "#9FB8E8"), ("春 4〜6月", "#8FC7A0"), ("夏 7〜9月", "#E9A07A"), ("秋冬 10〜12月", "#C9A0F0")]):
        names = "・".join(sk.get(m, "") for m in range(i * 3 + 1, i * 3 + 4))
        body = inline(seas[i]) if i < len(seas) and seas[i] else f'<span class="fh-b27-missing">{MISSING}</span>'
        tl.append(f'<div><i style="background:{col}"></i><b>{lab}<small>{names}</small></b><p>{body}</p></div>')
    a('<section class="fh-b27-sec" id="b27-season">\n  <h2><span class="n">10</span>季節ごとの流れ</h2>\n  <div class="fh-b27-tl">\n    '
      + "\n    ".join(tl) + "\n  </div>\n</section>")

    gg = ELEM_GOGYO[e["element"]]
    a(f'''<section class="fh-b27-sec" id="b27-graph">
  <h2><span class="n">11</span>占いごとの月別グラフ</h2>
  <p>西洋占星術・数秘術・暦の五行の3つで、2027年の月ごとの運気を出して重ねました。線がそろって上がる月は「どの占いで見ても追い風」の月です。</p>
  <p class="fh-b27-yearnote" data-fh-yearnote></p>
  <div class="fh-b27-leg" id="fh-b27-leg" role="group" aria-label="グラフに表示する占い"></div>
  <div class="fh-b27-chart" id="fh-b27-chart"></div>
  <details class="fh-b27-table"><summary>数値を表で見る</summary><div id="fh-b27-tbl"></div></details>
  <h3>それぞれの線の出し方</h3>
  <dl class="fh-b27-koyomi">
    <div><dt><b>星座</b>西洋占星術</dt><dd>2027年の毎日の太陽・金星・火星・木星・土星の位置と、{md}生まれの太陽の位置との関係を月ごとにまとめた点です。調和の関係が多い月ほど高くなります。</dd></div>
    <div><dt><b>数秘</b>数秘術</dt><dd>2027年の数「{e["py2027"]}」に月を足した「月の数」で判定。始まり・表現・実りの月は高く、見直し・締めくくりの月は低めです。</dd></div>
    <div><dt><b>暦の五行</b>干支</dt><dd>その月の干支の五行と、{esc(sign)}の「{gg}」の関係で判定。{gg}を生む月は高く、{gg}を抑える月は低くなります。</dd></div>
    <div><dt><b>九星・バイオリズム</b>生まれ年を選んだとき</dt><dd>九星は、月ごとの九星とあなたの本命星の五行の関係。バイオリズムは、身体・感情・知性の月平均です。</dd></div>
    <div><dt><b>総合</b>平均</dt><dd>表示している線の平均。下の◎○△は、生まれ年を選ばないときの総合で決めています。</dd></div>
  </dl>
</section>''')

    # 12 12か月
    marks, tot = sc["marks"], sc["total"]
    months = yr.get("months") or []
    grid = "\n    ".join(f'<div><span>{i+1}月</span><b class="fh-b27-mark {MARK_CLS.get(marks[i], "ok")}">{marks[i]}</b><small>{tot[i]}</small></div>' for i in range(12))
    care = [i + 1 for i in range(12) if marks[i] == "△"]
    first_care = care[0] if care else 12  # 電話占いの案内は、最初の△の月（続く△の月はまとめて）の直後に1か所
    while first_care < 12 and marks[first_care] == "△":
        first_care += 1
    ad = f'''<div class="fh-b27-ad">
    <small>△の月に迷ったら</small>
    <p>{months_label(care) if care else "流れが重く感じる月"}のように流れが重い月は、人に話すだけで整理がつくことがあります。占い師に直接相談できる電話占いも選択肢のひとつです。</p>
    <a class="fh-b27-btn ghost" {aff("電話占い:初回特典ページ")}>電話占いの初回特典を見る</a>
    <span class="fh-b27-pr">広告を含みます</span>
  </div>'''
    ml1, ml2 = [], []
    for i in range(12):
        body = inline(months[i]) if i < len(months) and months[i] else f'<span class="fh-b27-missing">{MISSING}</span>'
        (ml1 if i + 1 <= first_care else ml2).append(
            f'<div><b>{i+1}月</b><span class="fh-b27-mark {MARK_CLS.get(marks[i], "ok")}">{marks[i]}</span><span>{body}</span></div>')
    a(f'''<section class="fh-b27-sec" id="b27-month">
  <h2><span class="n">12</span>12か月の運勢</h2>
  <div class="fh-b27-months" aria-label="月ごとの調子">
    {grid}
  </div>
  <div class="fh-b27-monthlist">
    {"".join(ml1)}
  </div>
  {ad}''')
    if ml2:
        a(f'  <div class="fh-b27-monthlist">\n    {"".join(ml2)}\n  </div>')
    a('  <p class="fh-b27-small">◎ とても良い ／ ○ 良い ／ △ 慎重に。数字は上のグラフの「総合」で、366日×12か月の総合点の上位4分の1を◎、下位4分の1を△にしています。</p>\n</section>')

    # 13 開運アクション
    acts = yr.get("actions") or []
    if acts:
        li = "\n    ".join(f'<li><span><b>{inline(x.get("title", ""))}</b>{inline(x.get("text", ""))}</span></li>' for x in acts)
        a(f'<section class="fh-b27-sec" id="b27-action">\n  <h2><span class="n">13</span>2027年の開運アクション</h2>\n  <ol class="fh-b27-acts">\n    {li}\n  </ol>\n</section>')
    else:
        a(f'<section class="fh-b27-sec" id="b27-action">\n  <h2><span class="n">13</span>2027年の開運アクション</h2>\n  {miss_p()}\n</section>')

    # 14 お守りリスト
    am = yr.get("amulet") or {}
    a('<section class="fh-b27-sec" id="b27-omamori">\n  <h2><span class="n">14</span>2027年のお守りリスト</h2>\n  <h3>ラッキーカラー</h3>')
    cols = am.get("colors") or []
    if cols:
        a('  <div class="fh-b27-rows">')
        for i, c in enumerate(cols):
            tag = ["メイン", "サブ", "アクセント"][i] if i < 3 else ""
            hx = c.get("hex")
            swh = f'<span class="fh-b27-sw" style="background:{esc(hx)}"></span>' if hx and re.fullmatch(r"#[0-9A-Fa-f]{6}", hx) else ""
            a(f'''    <div class="fh-b27-row">
      {swh}<div class="who"><b>{esc(c.get("name", ""))}{f"（{tag}）" if tag else ""}</b><small>{inline(c.get("why", ""))}</small></div>
      <a class="fh-b27-btn{"" if i == 0 else " ghost"}" {aff("楽天:" + c.get("name", "") + " 小物")}>この色の小物を見る</a>
    </div>''')
        a("  </div>")
    else:
        a("  " + miss_p())
    a("  <h3>ラッキーアイテム</h3>")
    items = am.get("items") or []
    if items:
        a('  <div class="fh-b27-rows">')
        for it in items:
            a(f'    <div class="fh-b27-row"><div class="who"><small>{inline(it.get("why", ""))}</small><b>{esc(it.get("name", ""))}</b></div><a class="fh-b27-btn" {aff("楽天/Amazon:" + it.get("name", ""))}>見てみる</a></div>')
        a("  </div>")
    else:
        a("  " + miss_p())
    a('  <p class="fh-b27-pr">※ このリストには広告（アフィリエイトリンク）を含みます。</p>')
    num = am.get("number") or {}
    a("  <h3>ラッキーナンバー</h3>")
    if num.get("value") is not None:
        a(f'  <div class="fh-b27-nums"><span>{esc(num["value"])}</span></div>\n  <p class="fh-b27-small">{inline(num.get("why", ""))}</p>')
    else:
        a("  " + miss_p())
    stn = am.get("stone") or {}
    a(f'  <h3>守護石 {esc(stn.get("name", ""))}</h3>')
    a(f'  <p>{inline(stn["effect"])}</p>' if stn.get("effect") else "  " + miss_p())
    a("</section>")

    # 15 誕生日プレゼント
    pres = fx.get("present") or []
    a(f'<section class="fh-b27-sec" id="b27-gift">\n  <h2><span class="n">15</span>{md}生まれの人への誕生日プレゼント</h2>')
    if pres:
        a('  <div class="fh-b27-gifts">')
        for i, p in enumerate(pres):
            a(f'    <div class="fh-b27-gift"><small>おすすめ {i+1}</small><b>{esc(p.get("item", ""))}</b><span>{inline(p.get("why", ""))}</span><a class="fh-b27-btn" {aff("楽天:" + p.get("item", "") + " ギフト")}>見てみる</a></div>')
        a('  </div>\n  <p class="fh-b27-pr">※ 広告（アフィリエイトリンク）を含みます。</p>')
        am_names = {x.get("name") for x in items}
        dup = [p.get("item") for p in pres if p.get("item") in am_names]
        if dup:
            warnings.append(f"{mmdd}: 誕生日プレゼントとお守りリストで同じ商品 {dup}")
    else:
        a("  " + miss_p())
    a("</section>")
    a("</div>")

    # 誕生日当日
    b = e["bday2027"]
    a(f'''<section class="fh-b27-today" id="b27-today">
  <h2 class="fh-b27-hand">{esc(ctx["bday_label"])}の運勢</h2>
  {paras(yr.get("bday"))}
  <p>{b["weekday"]}曜日・{esc(b["day_kanshi"])}の日。2027年のこの日の数は{b["personal_day"]}（{esc(b["pd_meaning"])}）。</p>
</section>''')

    # 16 生まれ年
    a(f'''<section class="fh-b27-sec" id="b27-year">
  <h2><span class="n">16</span>生まれ年でわかること</h2>
  <p>ここから先の2つは、月日だけでは決まらない占いです。ページ上の「生まれ年」を選ぶと表示されます。</p>
  <div class="fh-b27-panel" data-fh-panel>
    <p class="fh-b27-yearnote" data-fh-yearnote></p>
    <div id="fh-b27-mine" hidden>
      <div class="fh-b27-res">
        <div><small>九星気学の本命星</small><b id="fh-b27-star">—</b><span id="fh-b27-star-n"></span><a id="fh-b27-dir" href="/kaiun/compass/">この方角の意味を開運ライフで見る →</a></div>
        <div><small>干支（生まれ年）</small><b id="fh-b27-eto">—</b><span id="fh-b27-eto-n"></span></div>
        <div class="wide"><small>四柱推命の命式（年柱・月柱・日柱）</small><b id="fh-b27-pillars">—</b><span id="fh-b27-nikkan-n"></span></div>
        <div><small>宿曜の本命宿</small><b id="fh-b27-shuku">—</b><span id="fh-b27-shuku-n"></span></div>
        <div><small>マヤ暦（KIN）</small><b id="fh-b27-kin">—</b><span id="fh-b27-kin-n"></span></div>
        <div><small>数秘のライフパス</small><b id="fh-b27-lp">—</b><span id="fh-b27-lp-n"></span></div>
        <div><small>動物×色占い</small><b id="fh-b27-animal">—</b><span><a href="/animal-color/">60タイプの性格を見る →</a></span></div>
      </div>
      <p class="fh-b27-calcnote fh-b27-small">生まれた時刻は正午として計算しています。節入りの日や立春の日に生まれた人は、時刻によって結果が変わることがあります。</p>
    </div>
  </div>
</section>''')

    # 17 バイオリズム
    a('''<section class="fh-b27-sec" id="b27-bio">
  <h2><span class="n">17</span>2027年バイオリズムカレンダー</h2>
  <p>バイオリズムは、<b>身体（23日）・感情（28日）・知性（33日）</b>の3つの周期で、体調や気分の波を見る考え方です。<mark class="fh-b27-mk">大切な予定は「好調日」に、「注意日」は無理をしない日に。</mark>上の月別グラフが「月ごとの運勢」なのに対し、こちらは「日ごとの体調の波」です。</p>
  <p class="fh-b27-yearnote" data-fh-yearnote></p>
  <div id="fh-b27-biowrap" hidden>
    <div class="fh-b27-mbtn" id="fh-b27-mbtn" role="group" aria-label="月を選ぶ"></div>
    <div class="fh-b27-chart" id="fh-b27-bchart"></div>
    <div class="fh-b27-bleg"><span><i style="background:#d95926"></i>身体</span><span><i style="background:#3987e5"></i>感情</span><span><i style="background:#199e70"></i>知性</span><span><i class="band g"></i>好調日</span><span><i class="band c"></i>注意日</span></div>
    <details class="fh-b27-table" open><summary id="fh-b27-btitle">日ごとの表</summary><div id="fh-b27-btable"></div></details>
    <p class="fh-b27-small">凡例：★ 絶好調 ／ ◎ 好調 ／ 〇 普通 ／ △ 低調 ／ ▽ 注意。好調日＝3本の平均が0.6以上の日、注意日＝どれかの線が0を横切る日（切り替わりの日）。バイオリズムは科学的な根拠が認められていない読み物として楽しんでください。</p>
    <div class="fh-b27-bio" id="fh-b27-bio"></div>
  </div>
</section>''')

    # 18 2028年に向けて
    a(f'''<section class="fh-b27-sec" id="b27-next">
  <h2><span class="n">18</span>2028年に向けて</h2>
  {paras(yr.get("next_year"))}
</section>''')
    a('''<a class="fh-b27-promo" href="/seinengappi/">
  <small>生年月日を入れるだけ</small>
  <b>生年月日まるごと診断</b>
  <span>星座・九星・干支・四柱推命・宿曜・マヤ暦・数秘・動物×色をまとめて一枚のカードに。</span>
</a>''')
    a(f'''<section class="fh-b27-sec fh-b27-letter" id="b27-letter">
  <h2 class="fh-b27-hand">{md}生まれのあなたへ</h2>
  {paras(yr.get("to_you"))}
</section>''')

    # 19 あわせて読みたい
    pv, nx = e["prev"], e["next"]
    a(f'''<section class="fh-b27-sec" id="b27-links">
  <h2><span class="n">19</span>あわせて読みたい</h2>
  <div class="fh-b27-links">
    <a href="/{en}/"><b>{SIGN_HIRA[sign]}の運勢</b><small>{sign_rng}生まれの性格と2027年</small></a>
    <a href="/compatibility/"><b>誕生日相性占い</b><small>2人の生年月日で相性を見る</small></a>
    <a href="/kaiun/compass/"><b>8方位の読み方</b><small>開運ライフ｜本命星の吉方位に</small></a>
    <a href="/animal-color/"><b>動物×色占い</b><small>生年月日で60タイプ</small></a>
    <a href="/mbti/"><b>MBTI占い</b><small>性格タイプで見る2027年</small></a>
    <a href="/dream/"><b>夢解き図鑑</b><small>気になる夢の意味を調べる</small></a>
    <a href="/birthday/{nx}/"><b>{md_label(nx)}生まれ</b><small>次の日の誕生日占い</small></a>
    <a href="/birthday/{pv}/"><b>{md_label(pv)}生まれ</b><small>前の日の誕生日占い</small></a>
  </div>
</section>''')

    # この占いについて（根拠の注記は1か所だけ）
    a(f'''<section class="fh-b27-about" id="b27-about">
  <h3>この占いについて</h3>
  <ul>
    <li><b>星座と度数：</b>{md}生まれの太陽の位置は、1930〜2027年の各年の{md}正午（日本時間）の太陽の位置の平均で、{esc(sign)}の約{int(e["sun_deg_in_sign"])}度にあたります。星座の境目の日は、生まれた年と時刻で星座が変わることがあります。</li>
    <li><b>相性の選び方：</b>太陽の位置どうしが約120度・約60度・同じ星座の近い位置にある日を「相性の良い誕生日」、約90度・約180度の日を「気をつけたい誕生日」とし、誕生日の数のグループ（1・5・7＝行動派、2・4・8＝堅実派、3・6・9＝表現派）の組み合わせを加えて選んでいます。</li>
    <li><b>月別スコア：</b>西洋占星術（2027年の太陽・金星・火星・木星・土星）・数秘術（月の数）・暦の五行（月の干支）の3つを20〜100点にそろえて平均したものです。◎○△は366日×12か月の総合点の上位・下位4分の1で決めています。</li>
    <li><b>誕生日石・誕生色：</b>当サイト独自の選び方です。誕生色は日本の伝統色から七十二候や誕生花にちなんで、誕生日石はその月の誕生石・デーカンの星に対応する石・誕生色に近い石の中から、実際に販売されている石を選んでいます。</li>
    <li><b>誕生花：</b>日本花普及センターの「誕生花」一覧によります。</li>
    <li><b>暦：</b>二十四節気・七十二候・干支・九星・旧暦は、天文計算で求めた日時（日本時間）にもとづいています。</li>
  </ul>
</section>''')
    up = dt.date.fromisoformat(updated)
    a(f'<p class="fh-b27-foot">この記事は、西洋占星術・九星気学・干支・数秘術・七十二候・誕生花・誕生石・バイオリズムにもとづいて構成しています。月ごとの◎○△とグラフは計算で出したもので、占いの結果としてお読みください。<br>最終更新日：{up.year}年{up.month}月{up.day}日／<a href="/policy/">この記事の作成方針について</a></p>')
    a("</div>\n</div>")

    body = "\n".join(H)
    pre = "../assets/" if sample else WP_ASSET
    head_assets = (f'<link rel="preconnect" href="https://fonts.googleapis.com">\n'
                   f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
                   f'<link href="{FONTS}" rel="stylesheet">\n'
                   f'<link rel="stylesheet" href="{pre}fh-b27.css">')
    tail_assets = (f'<script src="{pre}fh-b27-setsuiri.js"></script>\n<script src="{pre}fh-b27-kyureki.js"></script>\n'
                   f'<script src="{pre}fh-b27.js"></script>')
    page = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="https://www.uranai.epoch-compass.com/birthday/{mmdd}/">
<style>/* 確認用（WordPressでは不要） */body{{margin:0;background:#141824}}</style>
</head>
<body>
<!-- fh-b27:start  WordPress の本文に貼るのはここから（URL: /birthday/{mmdd}/、親ページ birthday） -->
{head_assets}
{body}
{tail_assets}
<!-- fh-b27:end -->
</body>
</html>
'''
    return page, warnings, {"title": title, "description": desc, "has_text": bool(T)}


def make_ctx(mats, text_dir):
    ycon = year_consts()
    know = knowledge()
    gen = {"center2027": ycon["center"], "monthStar2027": ycon["month_star"], "yearMin": YEAR_MIN, "yearMax": YEAR_MAX,
           "kyuseiKw": know["kyuseiKw"], "nikkan": know["nikkan"], "shukuKw": know["shukuKw"],
           "sealKw": know["sealKw"], "toneKw": know["toneKw"], "lpKw": know["lpKw"]}
    ctx = {"year": ycon, "know": know, "gen": gen, "order": sorted(mats), "stones": stones(),
           "kou_rng": ranges(mats, lambda x: x["kou"]),
           "dec_rng": ranges(mats, lambda x: (x["sign"], x["decan"])),
           "sign_rng": ranges(mats, lambda x: x["sign"]),
           "setsu_by_month": sekki_2027(), "stars": star_rows(), "texts": load_texts(text_dir)}
    return ctx


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mmdd", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--sample", action="store_true", help="work/out/sample/ に相対パスで出す")
    ap.add_argument("--text-dir", default=os.path.join(WORK, "text"))
    ap.add_argument("--updated", default=dt.date.today().isoformat())
    args = ap.parse_args()
    mats = json.load(open(os.path.join(DATA, "materials_366.json"), encoding="utf-8"))
    targets = sorted(mats) if args.all else args.mmdd
    if not targets:
        ap.error("MMDD を1つ以上指定するか --all をつけてください")
    bad = [t for t in targets if t not in mats]
    if bad:
        ap.error(f"不明な日付: {bad}")
    ctx = make_ctx(mats, args.text_dir)
    build_assets(ctx["gen"])
    odir = os.path.join(OUT, "sample" if args.sample else "html")
    os.makedirs(odir, exist_ok=True)
    allw, notext = [], []
    for k in targets:
        ctx_k = dict(ctx)
        b = mats[k]["bday2027"]["date"]
        ctx_k["bday_label"] = (f"2027年{int(b[5:7])}月{int(b[8:])}日（誕生日）" if b[5:] == f"{k[:2]}-{k[2:]}"
                               else f"2027年{int(b[5:7])}月{int(b[8:])}日（2月29日生まれの2027年の誕生日）")
        page, w, info = render(k, mats, ctx["texts"], ctx_k, sample=args.sample, updated=args.updated)
        allw += w
        if not info["has_text"]:
            notext.append(k)
        with open(os.path.join(odir, f"{k}.html"), "w", encoding="utf-8") as f:
            f.write(page)
    print(f"{len(targets)}ページ → {os.path.relpath(odir, WORK)}/  共通CSS/JS → out/assets/")
    if notext:
        print(f"文章が未作成の日: {len(notext)}件（例: {', '.join(notext[:5])}）")
    for w in allw:
        print("警告:", w)


if __name__ == "__main__":
    main()
