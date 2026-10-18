"""記念日の話題（例：登山の日→「登山」）が本文に何回出るかを数える（2026-10-18 依頼書 5：使用回数に上限）。
上限：記念日欄（fixed.events_note）＋本文2か所まで（開運アクションなど）。品名（amulet.items[].name・present[].item）は数えない。
使い方：python motif_report.py [--dump DIR]（DIR に担当ごとの書き直し用の一覧を出す）"""
import json, os, re, sys, glob
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = json.load(open(os.path.join(W, "data", "materials_366.json"), encoding="utf-8"))
SKIP = re.compile(r"\.events_note$|\.items\[\d+\]\.name$|\.present\[\d+\]\.item$|\.mmdd$")


def words(e):
    out = []
    for ev in (e.get("events") or []):
        w = re.sub(r"(の日|記念日|デー|の日（.*）)$", "", ev["title"]).strip()
        if len(w) >= 2:
            out.append(w)
    return out


def walk(o, p=""):
    if isinstance(o, str):
        yield p, o
    elif isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, f"{p}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, f"{p}[{i}]")


def day_file(k):
    return glob.glob(os.path.join(W, "text", "*", f"{k}.json"))[0]


def report():
    rows = []
    for k in sorted(M):
        d = json.load(open(day_file(k), encoding="utf-8"))
        d = d.get(k, d)
        for w in words(M[k]):
            occ = [(p, s) for p, s in walk(d) if w in s and not SKIP.search(p)]
            n = sum(s.count(w) for _, s in occ)
            if n > 2:
                rows.append(dict(mmdd=k, word=w, count=n, occ=[dict(path=p, text=s) for p, s in occ]))
    return rows


if __name__ == "__main__":
    rows = report()
    print(f"上限（本文2か所）を超える：{len(rows)}件（{len({r['mmdd'] for r in rows})}日）")
    if "--dump" in sys.argv:
        d = sys.argv[sys.argv.index("--dump") + 1]
        os.makedirs(d, exist_ok=True)
        days = sorted({r["mmdd"] for r in rows})
        n = 6
        sz = -(-len(days) // n)
        for i in range(n):
            part = [r for r in rows if r["mmdd"] in days[i * sz:(i + 1) * sz]]
            json.dump(part, open(os.path.join(d, f"in_{i}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
