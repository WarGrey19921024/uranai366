"""公開後の作り直し：公開中の366ページを上書きするための CSV（Really Simple CSV Importer 用・ID 列つき）

使い方（build_html.py --all のあと）:
  python work/scripts/build_update_csv.py

出力:
  work/out/rsci_update_test3.csv      テスト用（01-25・02-29・07-07 の3ページだけ）
  work/out/rsci_update_partN.csv      全366ページ（1ファイル10MB未満になるように分ける）

決まり（docs/04_本人の決定.md「公開後の改善 第1弾」）:
  - 列は rsci_*.csv と同じ＋先頭に ID（本番のページID。work/out/wp_page_ids.csv の slug→ID）
    Really Simple CSV Importer は ID が既存の投稿なら、その投稿を上書きする
  - 公開中のページなので post_status は publish（draft にすると非公開に戻ってしまう）
  - 本文に \\ を残さない（取り込み時に消えるため）。\\uXXXX の形も無いこと
  - 本文は build_import.py と同じ形：先頭に [no_toc]（ショートコードのブロック）、本体はカスタムHTMLブロック
"""
import csv, html, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.join(HERE, "..")
OUT = os.path.join(W, "out")
M = json.load(open(os.path.join(W, "data", "materials_366.json"), encoding="utf-8"))
PARENT_ID = "2743"  # 一覧ページ /366uranai/
LIMIT = 10 * 1000 * 1000 - 200 * 1000  # 10MB未満（余裕をみて9.8MBで切る）
TEST = ("01-25", "02-29", "07-07")
COLS = ["ID", "post_title", "post_name", "post_type", "post_status", "post_parent", "menu_order",
        "diver_single_metadescription", "post_content"]


def page_ids():
    ids = {}
    with open(os.path.join(OUT, "wp_page_ids.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if re.fullmatch(r"\d{2}-\d{2}", r["slug"]):
                ids[r["slug"]] = r["ID"]
    return ids


def rows():
    ids = page_ids()
    keys = sorted(M)
    assert len(ids) == 366 and set(ids) == {f"{k[:2]}-{k[2:]}" for k in keys}, "wp_page_ids.csv の366件とページが合いません"
    assert len(set(ids.values())) == 366, "ページIDに重複があります"
    out = []
    for i, k in enumerate(keys):
        slug = f"{k[:2]}-{k[2:]}"
        s = open(os.path.join(OUT, "html", f"{k}.html"), encoding="utf-8").read()
        m = re.search(r"<!-- fh-b27:start[^>]*-->", s)
        b = s.find("<!-- fh-b27:end -->")
        assert m and b > 0, f"{k}: 本文の目印が見つかりません"
        inner = s[m.start():b + len("<!-- fh-b27:end -->")]
        body = ("<!-- wp:shortcode -->\n[no_toc]\n<!-- /wp:shortcode -->\n\n"
                "<!-- wp:html -->\n" + inner + "\n<!-- /wp:html -->")
        assert "\\" not in body, f"{k}: 本文に \\ があります（取り込みで消えます）"
        assert not re.search(r"<h1[\s>]", inner, re.I), f"{k}: 本文に h1 があります"
        for mk in ("<!--OffDef-->", "<!--Ads1-->", "<!--Ads2-->", "<!--Ads3-->"):
            assert inner.count(mk) == 1, f"{k}: {mk} が1か所ではありません"
        assert "affiliate-TODO" not in inner, f"{k}: 仮リンクが残っています"
        title = html.unescape(re.search(r"<title>([^<]+)</title>", s).group(1))
        desc = html.unescape(re.search(r'<meta name="description" content="([^"]+)"', s).group(1))
        assert "\\" not in title + desc
        out.append({"ID": ids[slug], "post_title": title, "post_name": slug, "post_type": "page", "post_status": "publish",
                    "post_parent": PARENT_ID, "menu_order": str(i + 1), "diver_single_metadescription": desc,
                    "post_content": body})
    return out


def write(path, rs):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rs)
    return os.path.getsize(path)


def size_of(rs):
    import io
    b = io.StringIO()
    w = csv.DictWriter(b, fieldnames=COLS, quoting=csv.QUOTE_ALL)
    w.writeheader()
    w.writerows(rs)
    return len(b.getvalue().encode("utf-8"))


def main():
    rs = rows()
    for p in os.listdir(OUT):  # 前回の分け方の残りを消す
        if re.fullmatch(r"rsci_update_part\d+\.csv", p):
            os.remove(os.path.join(OUT, p))
    test = [r for r in rs if r["post_name"] in TEST]
    assert len(test) == 3
    print(f"rsci_update_test3.csv  {write(os.path.join(OUT, 'rsci_update_test3.csv'), test):,} bytes（{', '.join(TEST)}）")
    parts, cur = [], []
    for r in rs:
        if cur and size_of(cur + [r]) > LIMIT:
            parts.append(cur)
            cur = []
        cur.append(r)
    parts.append(cur)
    total = 0
    for i, part in enumerate(parts, 1):
        n = write(os.path.join(OUT, f"rsci_update_part{i}.csv"), part)
        assert n < 10 * 1000 * 1000
        total += len(part)
        print(f"rsci_update_part{i}.csv  {len(part)}件 {part[0]['post_name']}〜{part[-1]['post_name']}  {n:,} bytes")
    assert total == 366
    # 読み戻して確かめる：366件・ID重複なし・本文に \ なし
    back = []
    csv.field_size_limit(10 ** 9)
    for i in range(1, len(parts) + 1):
        with open(os.path.join(OUT, f"rsci_update_part{i}.csv"), encoding="utf-8") as f:
            back += list(csv.DictReader(f))
    assert len(back) == 366 and len({r["ID"] for r in back}) == 366
    assert all("\\" not in r["post_content"] and r["post_status"] == "publish" for r in back)
    print("読み戻し：366件・ID重複なし・本文に \\ なし・すべて publish")


if __name__ == "__main__":
    main()
