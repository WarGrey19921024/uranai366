"""フェーズ4-1：誕生日どうしの相性 → work/data/compat_366.json
規則（work/knowledge/12_スコアと相性の規則.md）：
  良い相性の点 = 太陽の度数どうしの調和の角度（120度・60度・同じ星座の0度）＋ 誕生日の数のグループ
  ぶつかりやすさの点 = 緊張の角度（90度・180度）＋ 誕生日の数のグループの食い違い
  選び方：全日付まとめて、点の高い組から「お互いに」選ぶ（対称）。1日につき良い5日・ぶつかる3日。
  自分自身・前後1日・（ぶつかる側は）良い側に入った相手は選ばない。宿曜は使わない（月日だけでは本命宿が決まらないため）
"""
import json, os, random, collections

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
GOOD_N, BAD_N = 5, 3
NUM_GROUP = {1: "行動", 5: "行動", 7: "行動", 2: "調和", 4: "調和", 8: "調和", 3: "表現", 6: "表現", 9: "表現"}
GROUP_WORD = {"行動": "自分で道を切り開く行動派", "調和": "足元を固める堅実派", "表現": "気持ちを伝える表現派"}
ELEM_GOOD = {frozenset(["火"]): "火のエレメントどうしで熱意が通じ合う", frozenset(["地"]): "地のエレメントどうしで価値観が近い",
             frozenset(["風"]): "風のエレメントどうしで会話がはずむ", frozenset(["水"]): "水のエレメントどうしで気持ちを察し合える",
             frozenset(["火", "風"]): "火と風で互いの勢いをあおり合う", frozenset(["地", "水"]): "地と水で互いを育て合う"}
ASP = {0: "同じ星座の重なり", 60: "60度の協力", 120: "120度の調和", 90: "90度の摩擦", 180: "180度の向かい合わせ"}


def reduce1(n):
    return {11: 2, 22: 4}.get(n, n)


def ang(a, b):
    return abs((a - b + 180) % 360 - 180)


def scores(A, B, wide=0):
    d = ang(A["sun_lon"], B["sun_lon"])
    na, nb = reduce1(A["birthday_number"]), reduce1(B["birthday_number"])
    ga, gb = NUM_GROUP[na], NUM_GROUP[nb]
    good = bad = 0.0
    g_asp = b_asp = None
    for a, orb, w in ((120, 8 + wide, 1.0), (60, 6 + wide, .7), (0, 8 + wide, .45)):
        if abs(d - a) <= orb:
            good, g_asp = w * (1 - abs(d - a) / orb) + .1, a
    for a, orb, w in ((90, 8 + wide, 1.0), (180, 8 + wide, .75)):
        if abs(d - a) <= orb:
            bad, b_asp = w * (1 - abs(d - a) / orb) + .1, a
    if g_asp is not None:
        good += .45 if ga == gb else 0
        good += .15 if na == nb else 0
    if b_asp is not None:
        bad += .4 if {ga, gb} == {"行動", "調和"} else .15 if ga != gb else 0
    return good, g_asp, bad, b_asp, d


def select(keys, cand, need, forbid=set()):
    """点の高い組から対称に選ぶ＋足りない日を組み替えで埋める"""
    adj = {k: set() for k in keys}
    edges = sorted(((s, a, b) for (a, b), s in cand.items() if (a, b) not in forbid), reverse=True)
    for s, a, b in edges:
        if len(adj[a]) < need and len(adj[b]) < need:
            adj[a].add(b); adj[b].add(a)
    sc = lambda a, b: cand.get((a, b), cand.get((b, a), 0))
    ok = lambda a, b: a != b and ((a, b) in cand or (b, a) in cand) and (a, b) not in forbid and (b, a) not in forbid
    for _ in range(50):
        lack = [k for k in keys if len(adj[k]) < need]
        if not lack: break
        for u in lack:
            if len(adj[u]) >= need: continue
            # u と、まだ足りない x を、v-w の組を外して u-v・w-x でつなぎ直す
            done = False
            for v in sorted((v for v in keys if ok(u, v) and v not in adj[u]), key=lambda v: -sc(u, v)):
                if len(adj[v]) < need:
                    adj[u].add(v); adj[v].add(u); done = True; break
                for w in list(adj[v]):
                    if w == u: continue
                    for x in keys:
                        if x != w and len(adj[x]) < need and x not in adj[w] and ok(w, x) and (x != u or len(adj[u]) + 1 < need):
                            adj[v].discard(w); adj[w].discard(v)
                            adj[u].add(v); adj[v].add(u)
                            adj[w].add(x); adj[x].add(w)
                            done = True; break
                    if done: break
                if done: break
    return adj


def main():
    B = json.load(open(os.path.join(DATA, "base_366.json"), encoding="utf-8"))
    keys = list(B)
    idx = {k: i for i, k in enumerate(keys)}
    near = lambda a, b: min((idx[a] - idx[b]) % 366, (idx[b] - idx[a]) % 366) <= 1
    goodc, badc, info = {}, {}, {}
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if near(a, b): continue
            g, ga, bd, ba, d = scores(B[a], B[b])
            info[(a, b)] = (ga, ba, d)
            if g > 0: goodc[(a, b)] = g
            if bd > 0: badc[(a, b)] = bd
    def widen(cand, adj, need, which, w=4):
        """足りない日だけ、角度の許容幅を4度広げた候補を足す（規則に明記）"""
        lack = {k for k in keys if len(adj[k]) < need}
        for i, a in enumerate(keys):
            for b in keys[i + 1:]:
                if near(a, b) or (a not in lack and b not in lack) or (a, b) in cand or (a, b) in forbid_all: continue
                g, ga, bd, ba, d = scores(B[a], B[b], wide=w)
                v = g if which == "good" else bd
                if v > 0:
                    cand[(a, b)] = v * .5
                    info[(a, b)] = (ga, ba, d)
        return lack

    forbid_all = set()
    gadj = select(keys, goodc, GOOD_N)
    for w in (4, 8, 12):
        if not widen(goodc, gadj, GOOD_N, "good", w): break
        gadj = select(keys, goodc, GOOD_N)
    forbid = {(a, b) for a in keys for b in gadj[a]}
    badc = {e: s for e, s in badc.items() if e not in forbid and (e[1], e[0]) not in forbid}
    forbid_all = forbid | {(b, a) for a, b in forbid}
    badj = select(keys, badc, BAD_N)
    for w in (4, 8, 12):
        if not widen(badc, badj, BAD_N, "bad", w): break
        badj = select(keys, badc, BAD_N)

    def text(a, b, kind):
        A, Bb = B[a], B[b]
        ga, ba, d = info[(a, b)] if (a, b) in info else info[(b, a)]
        asp = ga if kind == "good" else ba
        na, nb = A["birthday_number"], Bb["birthday_number"]
        gA, gB = NUM_GROUP[reduce1(na)], NUM_GROUP[reduce1(nb)]
        degA, degB = int(A["sun_deg_in_sign"]), int(Bb["sun_deg_in_sign"])
        head = f"{A['sign']}{degA}度と{Bb['sign']}{degB}度は太陽の角度が{round(d)}度"
        if kind == "good":
            el = ELEM_GOOD.get(frozenset([A["element"], Bb["element"]]))
            mid = {120: "の調和", 60: "の協力関係", 0: "で同じ星座の仲間"}[asp]
            num = (f"誕生日の数{na}と{nb}はどちらも{GROUP_WORD[gA]}" if gA == gB else f"誕生日の数{na}と{nb}は違う持ち味で補い合える")
            return f"{head}{mid}{'で、' + el if el else ''}、{num}。"
        mid = {90: "の摩擦", 180: "の向かい合わせ"}[asp]
        tail = {90: "急ぐ場面ほど一呼吸おくと噛み合います", 180: "相手を鏡にすると学びの多い間柄です"}[asp]
        num = (f"誕生日の数{na}と{nb}は{GROUP_WORD[gA][-3:]}と{GROUP_WORD[gB][-3:]}で歩く速さが違うため" if gA != gB
               else f"誕生日の数{na}と{nb}は似た者どうしで張り合いやすいため")
        return f"{head}{mid}、{num}、{tail}。"

    out = {}
    for a in keys:
        out[a] = {"good": [{"mmdd": b, "text": text(a, b, "good")} for b in sorted(gadj[a], key=lambda b: -goodc.get((a, b), goodc.get((b, a), 0)))],
                  "bad": [{"mmdd": b, "text": text(a, b, "bad")} for b in sorted(badj[a], key=lambda b: -badc.get((a, b), badc.get((b, a), 0)))]}
    json.dump(out, open(os.path.join(DATA, "compat_366.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    return out


if __name__ == "__main__":
    o = main()
    for k in ["0101", "0102"]:
        print(k, [g["mmdd"] for g in o[k]["good"]], [g["mmdd"] for g in o[k]["bad"]])
        print("  ", o[k]["good"][0]["text"]); print("  ", o[k]["bad"][0]["text"])
