"""フェーズ9：投入用ファイル
- work/out/wp_all_import.csv … WP All Import 用（固定ページ366件。親ページ birthday・スラッグ MMDD・本文・メタディスクリプション）
- work/out/redirects_301.csv … 301の対応表（/2026-MMDD/ と /2025-MMDD/ → /birthday/MMDD/。連鎖させない＝すべて最終URLへ直接）
- work/out/redirects_redirection_plugin.csv … Redirection プラグインの「インポート」用（source,target,regex,code）
- work/out/redirects_htaccess.txt … .htaccess に貼る場合の書き方（同じ内容）
本文は work/out/html/MMDD.html の <!-- fh-b27:start -->〜<!-- fh-b27:end --> の間。共通CSS/JSは /wp-content/uploads/fh-b27/ に置く前提。
"""
import os, re, csv, json, html

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.join(HERE, "..")
OUT = os.path.join(W, "out")
M = json.load(open(os.path.join(W, "data", "materials_366.json"), encoding="utf-8"))


def main():
    rows, redir = [], []
    for k in sorted(M):
        p = os.path.join(OUT, "html", f"{k}.html")
        s = open(p, encoding="utf-8").read()
        a, b = s.find("<!-- fh-b27:start -->"), s.find("<!-- fh-b27:end -->")
        if a < 0 or b < 0:
            raise SystemExit(f"{k}: 本文の目印が見つかりません")
        body = s[a:b + len("<!-- fh-b27:end -->")]
        title = html.unescape(re.search(r"<title>([^<]+)</title>", s).group(1))
        desc = html.unescape(re.search(r'<meta name="description" content="([^"]+)"', s).group(1))
        m, d = int(k[:2]), int(k[2:])
        rows.append({"post_title": title, "post_name": k, "post_parent_slug": "birthday", "post_type": "page",
                     "post_status": "draft", "menu_order": list(sorted(M)).index(k) + 1,
                     "meta_description": desc, "post_content": body})
        for y in (2026, 2025):
            redir.append((f"/{y}-{k}/", f"/birthday/{k}/"))
    with open(os.path.join(OUT, "wp_all_import.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), quoting=csv.QUOTE_ALL)
        w.writeheader(); w.writerows(rows)
    with open(os.path.join(OUT, "redirects_301.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f); w.writerow(["元のURL", "転送先（最終URL）", "種類"])
        for s_, t in redir: w.writerow([s_, t, "301"])
    with open(os.path.join(OUT, "redirects_redirection_plugin.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f); w.writerow(["source", "target", "regex", "code"])
        for s_, t in redir: w.writerow([s_, t, "0", "301"])
    with open(os.path.join(OUT, "redirects_htaccess.txt"), "w", encoding="utf-8") as f:
        f.write("# 誕生日占い 2027年版：旧URL → /birthday/MMDD/（すべて最終URLへ直接。転送の連鎖なし）\n")
        f.write("# 1行で済ませる書き方（推奨）：\nRedirectMatch 301 ^/(?:2025|2026)-(\\d{4})/?$ /birthday/$1/\n")
    # 検査：連鎖が無いこと・重複が無いこと・366件
    targets = {t for _, t in redir}; sources = [s_ for s_, _ in redir]
    assert len(rows) == 366 and len(set(sources)) == len(sources) == 732
    assert not (targets & set(sources)), "転送先がさらに転送されている（連鎖）"
    print(f"WP All Import {len(rows)}件・301 {len(redir)}件（連鎖なし）→ work/out/")


if __name__ == "__main__":
    main()
