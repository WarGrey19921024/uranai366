"""フェーズ8：重複検査 → work/reports/dup_check.md（対象を絞るときは引数に星座英名。例：python check_dup.py capricorn）
基準（作業指示書フェーズ8＋確認2）
  1) 同じ文が4ページ以上 → 書き直し
  2) ページ同士の文字5-gram Jaccard：全組 0.25未満、同じ星座 0.30未満
  3) 同じセクション同士 0.40以上 → 書き直し
  4) 必ず使う材料（_書き方.md 3章）が入っているか
  5) 月の名前（山の月・慎重な月・分野別）がスコアと一致しているか
  6) 文の型の繰り返し（確認2）：固有の語を伏せた「文の骨組み」と「文末」が、多くのページで同じでないか
"""
import json, os, re, sys, glob, itertools, collections

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.join(HERE, "..")
M = json.load(open(os.path.join(W, "data", "materials_366.json"), encoding="utf-8"))
SIGNS_EN = sys.argv[1:] or None


def load():
    pages = {}
    for f in sorted(glob.glob(os.path.join(W, "text", "*.json"))):
        sign = os.path.basename(f)[:-5]
        if SIGNS_EN and sign not in SIGNS_EN: continue
        for k, v in json.load(open(f, encoding="utf-8")).items():
            pages[k] = (sign, v)
    return pages


def sections(v):
    """本文だけをセクションごとの文字列に"""
    out = {}
    def walk(prefix, x):
        if isinstance(x, str): out[prefix] = out.get(prefix, "") + x
        elif isinstance(x, list):
            for i, y in enumerate(x): walk(prefix, y)
        elif isinstance(x, dict):
            for kk, y in x.items():
                if kk in ("mmdd", "value"): continue
                walk(prefix if kk in ("text", "why", "effect", "name", "item", "title") else f"{prefix}.{kk}", y)
    for part in ("fixed", "y2027"):
        for sec, x in v.get(part, {}).items():
            walk(f"{part}.{sec}", x)
    return out


clean = lambda s: re.sub(r"[\s*=＝]", "", s)
sents = lambda s: [x for x in re.split(r"(?<=[。！？])", clean(s)) if len(x) >= 8]
grams = lambda s, n=5: {s[i:i + n] for i in range(max(0, len(s) - n + 1))}
jac = lambda a, b: len(a & b) / len(a | b) if a | b else 0


def skeleton(s):
    """固有の語（カタカナ・漢字の連なり・数字）を伏せ、ひらがなと記号の骨組みを残す"""
    s = re.sub(r"[0-9０-９]+", "#", s)
    s = re.sub(r"[ァ-ヴー・]+", "カ", s)
    s = re.sub(r"[一-龥々〆ヶ]+", "漢", s)
    return s


def main():
    pages = load()
    secs = {k: sections(v) for k, (s, v) in pages.items()}
    full = {k: "".join(x.values()) for k, x in secs.items()}
    G = {k: grams(full[k]) for k in pages}
    R, bad = [], collections.Counter()
    # 1) 同じ文
    where = collections.defaultdict(set)
    for k, x in secs.items():
        for t in x.values():
            for s in sents(t): where[s].add(k)
    same = sorted(((len(p), s, sorted(p)) for s, p in where.items() if len(p) >= 4), reverse=True)
    bad["同じ文が4ページ以上"] = len(same)
    # 2) ページ同士
    pairs = []
    for a, b in itertools.combinations(sorted(pages), 2):
        j = jac(G[a], G[b])
        lim = .30 if pages[a][0] == pages[b][0] else .25
        pairs.append((j, a, b, j >= lim))
    pairs.sort(reverse=True)
    bad["ページの類似度が基準以上"] = sum(1 for p in pairs if p[3])
    # 3) セクション同士
    secpairs = []
    names = sorted({n for x in secs.values() for n in x})
    for n in names:
        have = [(k, grams(secs[k][n])) for k in pages if n in secs[k] and len(secs[k][n]) >= 30]
        for (a, ga), (b, gb) in itertools.combinations(have, 2):
            j = jac(ga, gb)
            if j >= .40: secpairs.append((j, n, a, b))
    secpairs.sort(reverse=True)
    bad["セクションの類似度0.40以上"] = len(secpairs)
    # 4) 材料
    need = {
        "fixed.personality": lambda m: [m["kou"], m["flower"]["hanakotoba"] if m["flower"] else None, str(m["birthday_number"])],
        "fixed.soul_message": lambda m: [m["flower"]["hanakotoba"] if m["flower"] else None, m["kou"], str(m["birthday_number"])],
        "y2027.fate": lambda m: [f"{m['peak_months'][0]}月"],
        "y2027.bday": lambda m: [m["bday2027"]["weekday"] + "曜", m["bday2027"]["day_kanshi"]],
    }
    miss = []
    for k, (s, v) in pages.items():
        m = M[k]
        for sec, f in need.items():
            t = secs[k].get(sec, "")
            items = [x for x in f(m) if x]
            hit = [x for x in items if x in t]
            if sec in ("fixed.personality",) and len(hit) < 2: miss.append((k, sec, items))
            if sec in ("fixed.soul_message", "y2027.fate") and len(hit) < 1: miss.append((k, sec, items))
            if sec == "y2027.bday" and len(hit) < 2: miss.append((k, sec, items))
    bad["必ず使う材料の不足"] = len(miss)
    # 5) 月の名前
    monthng = []
    for k, (s, v) in pages.items():
        m = M[k]
        for f, txt in v.get("y2027", {}).get("fields", {}).items():
            for want in (m["field_peak"][f], m["field_low"][f]):
                if f"{want}月" not in txt: monthng.append((k, f, want))
            # 本文に「山」「慎重」と一緒に書かれた月が、スコアと合っているか（例：「◯月が山」）
        for t in secs[k].values():
            for mm in re.findall(r"(\d{1,2})月(?:が|は)?(?:いちばんの)?(?:山|好調のピーク)", t):
                if int(mm) not in m["peak_months"] and all(int(mm) != x for x in m["field_peak"].values()):
                    monthng.append((k, "山と書いた月", int(mm)))
            for mm in re.findall(r"(\d{1,2})月(?:が|は)?(?:慎重|谷|注意)", t):
                if int(mm) not in m["low_months"] and all(int(mm) != x for x in m["field_low"].values()):
                    monthng.append((k, "慎重と書いた月", int(mm)))
    bad["月の名前がスコアと不一致"] = len(monthng)
    # 6) 文の型
    sk = collections.defaultdict(set)
    ends = collections.defaultdict(set)
    for k, x in secs.items():
        for t in x.values():
            for s in sents(t):
                sks = skeleton(s)
                if len(sks) >= 14: sk[sks].add(k)
                ends[s[-9:]].add(k)
    n = len(pages)
    rep_sk = sorted(((len(p), s) for s, p in sk.items() if len(p) >= max(4, n * .2)), reverse=True)
    rep_end = sorted(((len(p), s) for s, p in ends.items() if len(p) >= max(4, n * .6)), reverse=True)
    inpage = []
    for k, x in secs.items():
        c = collections.Counter(s[-9:] for t in x.values() for s in sents(t))
        inpage += [(k, e, cnt) for e, cnt in c.items() if cnt >= 4]
    bad["文の骨組みの繰り返し（20%以上のページ）"] = len(rep_sk)
    bad["同じ文末（60%以上のページ）"] = len(rep_end)
    bad["1ページ内で同じ文末4回以上"] = len(inpage)
    # 相性の一言：同じ文末が多すぎないか
    cend = collections.Counter()
    for k, (s, v) in pages.items():
        for y in v.get("fixed", {}).get("compat_good", []) + v.get("fixed", {}).get("compat_bad", []):
            cend[clean(y.get("text", ""))[-6:]] += 1
    tot_c = sum(cend.values()) or 1
    worst_c = cend.most_common(1)[0] if cend else ("", 0)
    if worst_c[1] > max(3, tot_c * .05): bad["相性の一言の同じ締め（5%超）"] = worst_c[1]
    # 字数
    lens = {k: len(full[k]) for k in pages}
    short = []
    for k, (s, v) in pages.items():
        for f, txt in v.get("y2027", {}).get("fields", {}).items():
            L = len(clean(txt))
            if not 190 <= L <= 260: short.append((k, f, L))
    bad["分野別の字数が200〜250字の目安から外れる"] = len(short)

    R.append(f"# 重複検査（{'・'.join(SIGNS_EN) if SIGNS_EN else '全体'}）\n\n`python work/scripts/check_dup.py {' '.join(SIGNS_EN or [])}` で再生成。対象 {n} ページ。\n")
    R.append("| 検査 | 基準 | 引っかかった数 |\n|---|---|---|")
    crit = {"同じ文が4ページ以上": "0", "ページの類似度が基準以上": "全組0.25未満・同じ星座0.30未満", "セクションの類似度0.40以上": "0",
            "必ず使う材料の不足": "0", "月の名前がスコアと不一致": "0", "文の骨組みの繰り返し（20%以上のページ）": "0", "同じ文末（60%以上のページ）": "0", "1ページ内で同じ文末4回以上": "0",
            "相性の一言の同じ締め（5%超）": "0", "分野別の字数が200〜250字の目安から外れる": "0（±10字は許容）"}
    for kk, c in crit.items():
        R.append(f"| {kk} | {c} | {'✅ 0' if not bad[kk] else '⚠ ' + str(bad[kk])} |")
    R.append(f"\n- 本文の字数（ページ）：最小 {min(lens.values())}／平均 {sum(lens.values()) // n}／最大 {max(lens.values())}")
    R.append(f"- ページ同士の類似度：最大 {pairs[0][0]:.3f}（{pairs[0][1]}–{pairs[0][2]}）" if pairs else "")
    R.append("\n## 似ているページの上位50組\n\n| 類似度 | ページ | 判定 |\n|---|---|---|")
    for j, a, b, ng in pairs[:50]: R.append(f"| {j:.3f} | {a}–{b} | {'⚠' if ng else ''} |")
    R.append("\n## 同じ文（4ページ以上）\n")
    for c, s, p in same[:50]: R.append(f"- {c}ページ：{s}（{' '.join(p[:8])}）")
    R.append("\n## セクションの類似度0.40以上\n")
    for j, nme, a, b in secpairs[:50]: R.append(f"- {j:.2f} {nme} {a}–{b}")
    R.append("\n## 文の骨組みの繰り返し\n")
    for c, s in rep_sk[:30]: R.append(f"- {c}ページ：{s}")
    R.append("\n## 同じ文末\n")
    for c, s in rep_end[:30]: R.append(f"- {c}ページ：…{s}")
    R.append("\n## 1ページ内の同じ文末\n")
    for k, e, c in inpage[:40]: R.append(f"- {k}：…{e}（{c}回）")
    R.append("\n## （参考）ページをまたいで多い文末\n")
    for c, s in sorted(((len(p), s) for s, p in ends.items()), reverse=True)[:10]: R.append(f"- {c}ページ：…{s}")
    R.append("\n## 相性の一言の締め（上位）\n\n" + "・".join(f"…{e}（{c}）" for e, c in cend.most_common(10)))
    R.append("\n## 必ず使う材料の不足\n")
    for k, sec, items in miss[:60]: R.append(f"- {k} {sec}：{items}")
    R.append("\n## 月の名前の不一致\n")
    for x in monthng[:60]: R.append(f"- {x}")
    R.append("\n## 分野別の字数\n")
    for x in short[:60]: R.append(f"- {x}")
    open(os.path.join(W, "reports", f"dup_check{'_' + '_'.join(SIGNS_EN) if SIGNS_EN else ''}.md"), "w", encoding="utf-8").write("\n".join(R) + "\n")
    print("\n".join(R[:14]))
    return bad


if __name__ == "__main__":
    main()
