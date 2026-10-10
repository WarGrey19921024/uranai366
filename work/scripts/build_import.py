"""フェーズ9：投入用ファイル
- work/out/wp_all_import_test3.csv … テスト投入用（01-01・02-29・01-20 の3ページ）
- work/out/wp_all_import.csv … WP All Import 用（固定ページ366件。親ページ 366uranai〔既存の固定ページ ID 2743〕・スラッグ MM-DD・本文・メタディスクリプション）
    メタディスクリプションの列名は Diver の「メタディスクリプション」欄のカスタムフィールド名 diver_single_metadescription
    本文の先頭（カスタムHTMLブロックの外）に [no_toc]（Table of Contents Plus の目次を出さない）
- work/out/redirects_301.csv … 301の対応表（/2026-MMDD/ と /2025-MMDD/ → /366uranai/MM-DD/、旧ハブ /366uranai/2026y/・/366uranai/2025y/ → /366uranai/。
    連鎖させない＝すべて最終URLへ直接）
- work/out/redirects_redirection_plugin.csv … Redirection プラグインの「インポート」用（source,target,regex,code。同じ内容）
- work/out/redirects_htaccess.txt … .htaccess に貼る場合の書き方（同じ内容。この表と一致することをここで検査）
本文は work/out/html/MMDD.html の <!-- fh-b27:start -->〜<!-- fh-b27:end --> の間。共通CSS/JSは /wp-content/uploads/fh-b27/ に置く前提。
"""
import os, re, csv, json, html

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.join(HERE, "..")
OUT = os.path.join(W, "out")
M = json.load(open(os.path.join(W, "data", "materials_366.json"), encoding="utf-8"))
HUB = "/366uranai/"
OLD_HUBS = ("/366uranai/2026y/", "/366uranai/2025y/")
# .htaccess（mod_alias）の書き方。下の検査で、この正規表現が301表とまったく同じ転送をすることを確かめる
HTACCESS = [
    (r"^/(?:2025|2026)-(\d{2})(\d{2})/?$", "/366uranai/$1-$2/"),
    (r"^/366uranai/2026y/?$", "/366uranai/"),
    (r"^/366uranai/2025y/?$", "/366uranai/"),
]


def slug(k):
    return f"{k[:2]}-{k[2:]}"


def page_url(k):
    return f"{HUB}{slug(k)}/"


def htaccess_target(path):
    """.htaccess の RedirectMatch を上から順に当てたときの転送先（当たらなければ None）"""
    for pat, tgt in HTACCESS:
        m = re.match(pat, path)
        if m:
            return re.sub(r"\$(\d)", lambda x: m.group(int(x.group(1))), tgt)
    return None


def main():
    rows, redir = [], []
    keys = sorted(M)
    for k in keys:
        p = os.path.join(OUT, "html", f"{k}.html")
        s = open(p, encoding="utf-8").read()
        _m = re.search(r"<!-- fh-b27:start[^>]*-->", s); a, b = (_m.start() if _m else -1), s.find("<!-- fh-b27:end -->")
        if a < 0 or b < 0:
            raise SystemExit(f"{k}: 本文の目印が見つかりません")
        inner = s[a:b + len("<!-- fh-b27:end -->")]
        # 本文の検査：H1 が無い・広告の位置の目印がそろっている・仮リンクが無い
        assert not re.search(r"<h1[\s>]", inner, re.I), f"{k}: 本文に h1 があります"
        for mk in ("<!--OffDef-->", "<!--Ads1-->", "<!--Ads2-->", "<!--Ads3-->"):
            assert inner.count(mk) == 1, f"{k}: {mk} が1か所ではありません"
        assert "affiliate-TODO" not in inner, f"{k}: 仮リンクが残っています"
        # 先頭に [no_toc]（ショートコードのブロック＝カスタムHTMLブロックの外）。
        # 本体は「カスタムHTML」ブロックとして包む：ブロックを含む本文には WordPress の自動段落（wpautop）がかからず、HTMLがそのまま出る
        body = ("<!-- wp:shortcode -->\n[no_toc]\n<!-- /wp:shortcode -->\n\n"
                "<!-- wp:html -->\n" + inner + "\n<!-- /wp:html -->")
        title = html.unescape(re.search(r"<title>([^<]+)</title>", s).group(1))
        desc = html.unescape(re.search(r'<meta name="description" content="([^"]+)"', s).group(1))
        rows.append({"post_title": title, "post_name": slug(k), "post_parent_slug": HUB.strip("/"), "post_type": "page",
                     "post_status": "draft", "menu_order": keys.index(k) + 1,
                     "diver_single_metadescription": desc, "post_content": body})
        for y in (2026, 2025):
            redir.append((f"/{y}-{k}/", page_url(k)))
    for h in OLD_HUBS:
        redir.append((h, HUB))
    with open(os.path.join(OUT, "wp_all_import.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), quoting=csv.QUOTE_ALL)
        w.writeheader(); w.writerows(rows)
    # テスト投入用（手順書の手順4）：01-01・02-29・01-20 の3ページだけ
    test = [r for r in rows if r["post_name"] in ("01-01", "02-29", "01-20")]
    assert len(test) == 3
    with open(os.path.join(OUT, "wp_all_import_test3.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), quoting=csv.QUOTE_ALL)
        w.writeheader(); w.writerows(test)
    with open(os.path.join(OUT, "redirects_301.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f); w.writerow(["元のURL", "転送先（最終URL）", "種類"])
        for s_, t in redir: w.writerow([s_, t, "301"])
    with open(os.path.join(OUT, "redirects_redirection_plugin.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f); w.writerow(["source", "target", "regex", "code"])
        for s_, t in redir: w.writerow([s_, t, "0", "301"])
    with open(os.path.join(OUT, "redirects_htaccess.txt"), "w", encoding="utf-8") as f:
        f.write("# 誕生日占い 2027年版：旧URL → /366uranai/MM-DD/、旧ハブ → /366uranai/（すべて最終URLへ直接。転送の連鎖なし）\n")
        f.write("# .htaccess の「# BEGIN WordPress」より上に貼る。redirects_301.csv（734件）と同じ転送になる：\n")
        for pat, tgt in HTACCESS:
            f.write(f"RedirectMatch 301 {pat} {tgt}\n")

    # 検査：366件・重複なし・連鎖なし・.htaccess と表が一致・転送先が実在のページ
    sources = [s_ for s_, _ in redir]
    targets = {t for _, t in redir}
    pages = {page_url(k) for k in keys}
    assert len(rows) == 366 and len({r["post_name"] for r in rows}) == 366
    assert all(re.fullmatch(r"\d{2}-\d{2}", r["post_name"]) for r in rows)
    assert len(set(sources)) == len(sources) == 734, "301の元のURLに重複がある"
    assert not (targets & set(sources)), "転送先がさらに転送されている（連鎖）"
    assert targets == pages | {HUB}, "転送先が誕生日ページ・一覧ページ以外を指している"
    for s_, t in redir:
        assert htaccess_target(s_) == t, f".htaccess と表が食い違う: {s_} → {htaccess_target(s_)}（表は {t}）"
    for t in targets:
        assert htaccess_target(t) is None, f"転送先 {t} が .htaccess でさらに転送される（連鎖）"
    print(f"WP All Import {len(rows)}件（/366uranai/MM-DD/・[no_toc]・diver_single_metadescription）"
          f"・301 {len(redir)}件（重複なし・連鎖なし・.htaccess と一致）→ work/out/")


if __name__ == "__main__":
    main()
