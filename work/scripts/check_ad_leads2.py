"""第2版の追加分（data/ad_leads/MMDD.json の gifts・mug・queries・check.mug_ok）の検査。2026-10-20 修正指示書 第2版 A・B・G
使い方：python check_ad_leads2.py [MMDD ...]"""
import json, os, sys, re
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = json.load(open(os.path.join(W, "out", "box_plan.json"), encoding="utf-8"))
BAD = ["必ず", "絶対", "確実に", "http", "<", "治る", "効く", "運が上がります"]
def need_q(k, d):
    import glob
    return d
def chk(k):
    p = os.path.join(W, "data", "ad_leads", f"{k}.json")
    d = json.load(open(p, encoding="utf-8"))
    e = []
    want = P[k].get("gifts", [])
    g = d.get("gifts", {})
    if set(g) != set(want): e.append(f"{k}: gifts の品名が違う（必要：{want}）")
    for n, t in g.items():
        if not 40 <= len(t) <= 120: e.append(f"{k}: gifts[{n}] の長さ {len(t)}（40〜120）")
    if P[k].get("mug"):
        if not isinstance(d.get("check", {}).get("mug_ok"), bool): e.append(f"{k}: check.mug_ok が必要")
        if d.get("check", {}).get("mug_ok") and not 40 <= len(d.get("mug", "")) <= 120: e.append(f"{k}: mug の長さ {len(d.get('mug', ''))}（40〜120）")
    q = d.get("queries", {})
    for n, s in q.items():
        ws = s.split()
        if not 1 <= len(ws) <= 3 or any(len(w) > 12 for w in ws) or re.search(r"[のをにへがはで]$", s) or "の" in s:
            e.append(f"{k}: queries[{n}]「{s}」は名詞だけ・3語まで・「の」なし")
    names = set(P[k].get("items", [])) | set(want)
    if set(q) - names: e.append(f"{k}: queries に箱にない品名 {set(q) - names}")
    txt = "".join(list(g.values()) + [d.get("mug", "")] + list((d.get("items") or {}).values()))
    for b in BAD:
        if b in txt: e.append(f"{k}: 使わない言葉「{b}」")
    if "円" in "".join([d.get("mug", "")] + list((d.get("items") or {}).values())): e.append(f"{k}: 金額はプレゼントの予算の目安だけ")
    return e
ks = sys.argv[1:] or sorted(P)
errs = [x for k in ks for x in chk(k)]
print("\n".join(errs) if errs else f"OK {len(ks)}日")
sys.exit(1 if errs else 0)
