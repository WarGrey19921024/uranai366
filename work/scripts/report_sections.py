"""各セクションの字数を試作ページと比べる → work/reports/section_length.md
使い方: python report_sections.py 0101 0110 0119（work/out/sample/ のHTMLを読む）"""
import re, html, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")


def secs(path):
    s = open(path, encoding="utf-8").read()
    _m = re.search(r"<!-- fh-b27:start[^>]*-->", s); a, b = (_m.start() if _m else -1), s.find("<!-- fh-b27:end -->")
    body = s[a:b] if a >= 0 else s[s.find("<body"):]
    body = re.sub(r"<script.*?</script>|<style.*?</style>", "", body, flags=re.S)
    parts = re.split(r"(<h2[^>]*>.*?</h2>)", body, flags=re.S)
    out = {}
    for i in range(1, len(parts), 2):
        h = re.sub(r'<span class="(?:fh-b27-)?n">\d+</span>', "", parts[i])
        h = re.sub(r"<[^>]+>", "", h).strip()
        h = re.sub(r"\d{1,2}月\d{1,2}日", "M月D日", h)
        t = re.sub(r"\s+", "", html.unescape(re.sub(r"<[^>]+>", "", parts[i + 1])))
        out[h] = len(t)
    return out


days = sys.argv[1:] or ["0101", "0110", "0119"]
proto = secs(os.path.join(ROOT, "docs", "prototype", "birthday-0101-2027_試作.html"))
pages = {d: secs(os.path.join(ROOT, "work", "out", "sample", f"{d}.html")) for d in days}
names = list(dict.fromkeys(list(proto) + [h for p in pages.values() for h in p]))
L = ["# セクションごとの字数（試作ページとの比較）\n", f"`python work/scripts/report_sections.py {' '.join(days)}` で再生成。H2見出しごとに、次のH2までの本文の字数（空白を除く。H3の中身を含む）。\n",
     "| セクション | 試作 | " + " | ".join(f"{int(d[:2])}/{int(d[2:])}" for d in days) + " | 判定 |", "|---|---|" + "---|" * len(days) + "---|"]
fewer = 0
for n in names:
    pv = proto.get(n)
    vals = [pages[d].get(n) for d in days]
    ok = pv is None or all(v is not None and v >= pv * .9 for v in vals)
    fewer += (not ok)
    L.append(f"| {n} | {pv if pv is not None else '—'} | " + " | ".join(str(v) if v is not None else "—" for v in vals) + f" | {'' if ok else '⚠ 試作より1割以上少ない'} |")
L.append(f"| **合計** | **{sum(proto.values())}** | " + " | ".join(f"**{sum(pages[d].values())}**" for d in days) + " | |")
L.append(f"\n- 試作より1割以上少ないセクション：{fewer}")
open(os.path.join(ROOT, "work", "reports", "section_length.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))
