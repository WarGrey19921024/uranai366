import sys, json, re, importlib
sys.path.insert(0, "/home/claude/uranai366/work/scripts")
import nenun2027_texts as M; importlib.reload(M)
import kyusei_texts, build_kyusei
D = json.load(open("/home/claude/uranai366/work/data/kyusei_nenun_2027.json"))
STARS = ["一白水星","二黒土星","三碧木星","四緑木星","五黄土星","六白金星","七赤金星","八白土星","九紫火星"]
ML = ["2月","3月","4月","5月","6月","7月","8月","9月","10月","11月","12月","1月"]
DIRS = ["北西","北東","南西","南東","北","南","東","西"]
err = []
def L(s, lo, hi, tag):
    if not lo <= len(s) <= hi: err.append(f"{tag}: len {len(s)} not in {lo}-{hi}")
strs = []  # (tag, text)
for i, st in enumerate(STARS):
    t = M.TEXTS2027.get(st); n = str(i+1)
    if not t: err.append(f"missing {st}"); continue
    for k in ["title","sougou","love","work","money","health","good_months","care_months","months","action"]:
        if k not in t: err.append(f"{st} missing {k}")
    L(t["title"],6,12,f"{st} title"); L(t["sougou"],230,300,f"{st} sougou"); L(t["love"],150,200,f"{st} love")
    L(t["work"],150,200,f"{st} work"); L(t["money"],120,170,f"{st} money"); L(t["health"],100,150,f"{st} health")
    y = D["year"]["stars"][n]
    if y["palace"] not in t["sougou"]: err.append(f"{st} sougou lacks palace {y['palace']}")
    if not 2 <= len(t["good_months"]) <= 3: err.append(f"{st} good count")
    if not 1 <= len(t["care_months"]) <= 3: err.append(f"{st} care count")
    for m, r in t["good_months"]:
        mi = ML.index(m); ms = D["months"][mi]["stars"][n]
        if ms["marks"]: err.append(f"{st} good {m} has marks {ms['marks']}")
        L(r,25,40,f"{st} good {m}"); strs.append((f"{st} good {m}", r))
    for m, r in t["care_months"]:
        mi = ML.index(m); ms = D["months"][mi]["stars"][n]
        if not ms["marks"]: err.append(f"{st} care {m} no marks")
        L(r,25,40,f"{st} care {m}"); strs.append((f"{st} care {m}", r))
    if len(t["months"]) != 12: err.append(f"{st} months {len(t['months'])}")
    for j, s in enumerate(t["months"]):
        L(s,35,60,f"{st} month {ML[j]}"); strs.append((f"{st} month {ML[j]}", s))
    if len(t["action"]) != 3: err.append(f"{st} action count")
    for a in t["action"]: L(a,15,30,f"{st} action {a}"); strs.append((f"{st} action", a))
    for k in ["title","sougou","love","work","money","health"]: strs.append((f"{st} {k}", t[k]))
    # directions in non-sougou texts must be lucky (sougou mentions palace)
    for k in ["love","work","money","health"]:
        for d_ in re.findall("北西|北東|南西|南東|北|南|東|西", t[k] + "".join(t["action"])):
            if d_ not in y["lucky"]: err.append(f"{st} {k}/action dir {d_} not lucky")
L(M.ETO2027["about"],250,350,"eto about"); L(M.ETO2027["with9"],150,220,"eto with9")
strs += [("eto about", M.ETO2027["about"]), ("eto with9", M.ETO2027["with9"])]
for tag, s in strs:
    if "！" in s or "!" in s: err.append(f"{tag}: has ！")
    for bad in ["六星占術","動物占い"]:
        if bad in s: err.append(f"{tag}: has {bad}")
ext = []
for st, d in kyusei_texts.TEXTS.items():
    for k, v in d.items():
        if isinstance(v, str): ext.append((f"PUB {st} {k}", v))
        elif isinstance(v, (list, tuple)):
            for x in v: ext.append((f"PUB {st} {k}", x))
for k, v in build_kyusei.YEAR2027.items():
    for x in v: ext.append((f"PUB Y{k}", x))
N = 15
seen = {}
for idx, (tag, s) in enumerate(strs + ext):
    for p in range(len(s) - N + 1):
        g = s[p:p+N]
        if g in seen and seen[g][0] != idx:
            o = seen[g]
            if not (tag.startswith("PUB") and o[1].startswith("PUB")):
                err.append(f"DUP {g!r}: {o[1]} / {tag}")
        else: seen.setdefault(g, (idx, tag))
ms = [s for t_, s in strs if " month " in t_]
if len(set(ms)) != len(ms): err.append("month lines not unique")
# dedupe repeated dup lines per pair
out = []; [out.append(e) for e in err if e not in out]
print("\n".join(out) if out else "ALL CHECKS PASSED")
print("strings checked:", len(strs), "month lines:", len(ms), "vs published:", len(ext))
