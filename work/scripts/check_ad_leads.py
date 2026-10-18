"""誕生日ページの「広告の前の本文説明」（data/ad_leads/MMDD.json）の形と長さを確かめる。2026-10-18 依頼書 4-1
使い方：python check_ad_leads.py [MMDD ...]（省略で全部）"""
import json, os, sys, glob, re
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = json.load(open(os.path.join(W, "out", "box_plan.json"), encoding="utf-8"))
M = json.load(open(os.path.join(W, "data", "materials_366.json"), encoding="utf-8"))
BAD = ["必ず", "絶対", "確実に", "円", "http", "<", "治る", "効く", "効果があります", "運が上がります"]
def chk(k):
    p = os.path.join(W, "data", "ad_leads", f"{k}.json")
    if not os.path.exists(p):
        return [f"{k}: ファイルがない"]
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception as x:
        return [f"{k}: 読めない {x}"]
    e = []
    for f in ("flower", "stone"):
        if not 70 <= len(d.get(f, "")) <= 160: e.append(f"{k}: {f} の長さ {len(d.get(f, ''))}（70〜160）")
    want = P[k].get("items", [])
    got = d.get("items", {})
    if set(got) != set(want): e.append(f"{k}: items の品名が違う（必要：{want}）")
    for n, t in got.items():
        if not 60 <= len(t) <= 150: e.append(f"{k}: items[{n}] の長さ {len(t)}（60〜150）")
    c = d.get("check", {})
    if not (isinstance(c.get("flower_ok"), bool) and isinstance(c.get("stone_ok"), bool)): e.append(f"{k}: check.flower_ok / stone_ok（true/false）")
    txt = "".join([d.get("flower", ""), d.get("stone", "")] + list(got.values()))
    for b in BAD:
        if b in txt: e.append(f"{k}: 使わない言葉「{b}」")
    for ev in (M[k].get("events") or []):
        w = re.sub(r"の日$|記念日$", "", ev["title"])
        if len(w) >= 2 and txt.count(w) > 1: e.append(f"{k}: 記念日の言葉「{w}」が説明文に{txt.count(w)}回（1回まで）")
    return e
ks = sys.argv[1:] or sorted(M)
errs = [x for k in ks for x in chk(k)]
print("\n".join(errs) if errs else f"OK {len(ks)}日")
sys.exit(1 if errs else 0)
