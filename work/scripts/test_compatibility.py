"""誕生日相性占い（/compatibility/）の JS（work/out/assets/fh-b27-compat.js）が、366日の誕生日ページと同じ相性の計算
（work/scripts/build_compat.py の scores()）になっているかを node で突き合わせるテスト。

使い方:
  python work/scripts/build_html.py --sample 0101      # 共通JS（fh-b27.js ほか）を作る
  python work/scripts/build_compatibility.py           # fh-b27-compat.js を作る
  python work/scripts/test_compatibility.py

調べること:
  1. 良い相性の点・ぶつかりやすさの点・角度の型・2人の角度が Python と一致する（全366日×1月1日、2月29日×全366日、同じ日どうし、
     ランダムな5,000組、幅を広げた計算 wide=4/8/12 も）
  2. compat_366.json の「相性の良い誕生日」5つは、JS で良い型（調和・協力・似た者どうし）・5段階の4以上になる。
     「気をつけたい誕生日」3つは、刺激し合う・向かい合うの型・5段階の2以下になる
  3. 文が組み立てられる（空の欄や {X} の残りがない・度数の数字を出さない・「動物占い」「六星」がない）。文の種類の数も出す
  4. 九星どうしの相性の表が knowledge の表と同じ（本命星は FHB27Calc.honmei）
"""
import datetime as dt, json, os, random, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_compat import scores  # noqa: E402
from build_compatibility import kyusei_table  # noqa: E402
import calc_kanshi_kyusei as KK  # noqa: E402

ASSETS = os.path.normpath(os.path.join(HERE, "..", "out", "assets"))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
BASE = json.load(open(os.path.join(DATA, "base_366.json"), encoding="utf-8"))
COMP = json.load(open(os.path.join(DATA, "compat_366.json"), encoding="utf-8"))
KEYS = list(BASE)

HARNESS = r"""
const fs=require('fs'),vm=require('vm');
const [dir,casesPath]=process.argv.slice(2);
const ctx={console};ctx.window=ctx;ctx.globalThis=ctx;vm.createContext(ctx);
for(const f of ['fh-b27-setsuiri.js','fh-b27-kyureki.js','fh-b27.js','fh-b27-compat.js'])vm.runInContext(fs.readFileSync(dir+'/'+f,'utf8'),ctx,{filename:f});
const X=ctx.FHB27Compat,C=ctx.FHB27Calc,cases=JSON.parse(fs.readFileSync(casesPath,'utf8'));
const sc=cases.scores.map(([i,j,w])=>{const s=X.scores(X.day(i),X.day(j),w);return [s.good,s.gAsp,s.bad,s.bAsp,s.d];});
const rel=cases.rel.map(([i,j])=>{const r=X.relation(i,j),t=X.texts(r);return {type:r.type,level:r.level,listed:r.listed,t:t};});
const ky=[];for(let a=1;a<=9;a++){let row='';for(let b=1;b<=9;b++)row+=X.kyusei(a,b).mark;ky.push(row);}
const hon=cases.hon.map(([y,m,d])=>C.honmei(y,m,d).star);
const keys=X.KEYS.map(([m,d])=>(m<10?'0':'')+m+(d<10?'0':'')+d);
const count={rel:{},num:{},el:0};for(const k in X.REL)count.rel[k]=[X.REL[k].s.length,X.REL[k].t.length];
for(const k in X.NUMTXT)count.num[k]=[X.NUMTXT[k].g.length,X.NUMTXT[k].t.length,X.NUMTXT[k].tip.length];
for(const k in X.ELTXT)count.el+=X.ELTXT[k].length;
process.stdout.write(JSON.stringify({sc,rel,ky,hon,keys,count}));
"""


def main():
    node = shutil.which("node") or "/opt/node22/bin/node"
    random.seed(2027)
    i0229 = KEYS.index("0229")
    pairs = [(i, 0) for i in range(366)] + [(i0229, j) for j in range(366)] + [(i, i) for i in range(366)]
    pairs += [(random.randrange(366), random.randrange(366)) for _ in range(5000)]
    sc_cases = [(i, j, 0) for i, j in pairs] + [(i, j, w) for i, j in pairs[:800] for w in (4, 8, 12)]
    rel_cases = []
    for a in KEYS:
        for g in COMP[a]["good"]:
            rel_cases.append((KEYS.index(a), KEYS.index(g["mmdd"])))
        for g in COMP[a]["bad"]:
            rel_cases.append((KEYS.index(a), KEYS.index(g["mmdd"])))
    n_listed = len(rel_cases)
    rel_cases += pairs
    hon_cases = [(1990, 1, 25), (1992, 7, 7), (1990, 2, 3), (1990, 2, 5), (1988, 2, 29), (2030, 12, 31), (1930, 1, 1)]
    tmp = tempfile.mkdtemp()
    try:
        hp, cp = os.path.join(tmp, "h.js"), os.path.join(tmp, "c.json")
        open(hp, "w").write(HARNESS)
        json.dump({"scores": sc_cases, "rel": rel_cases, "hon": hon_cases}, open(cp, "w"))
        out = json.loads(subprocess.run([node, hp, ASSETS, cp], check=True, capture_output=True, text=True).stdout)
    finally:
        shutil.rmtree(tmp)
    bad = []
    assert out["keys"] == KEYS, "日付の並びが base_366.json と違う"
    # 1. 点数・型
    for (i, j, w), js in zip(sc_cases, out["sc"]):
        py = scores(BASE[KEYS[i]], BASE[KEYS[j]], wide=w)
        same = (abs(js[0] - py[0]) < 1e-9 and js[1] == py[1] and abs(js[2] - py[2]) < 1e-9 and js[3] == py[3]
                and abs(js[4] - py[4]) < 1e-9)
        if not same:
            bad.append(f"scores {KEYS[i]}-{KEYS[j]} wide={w}: js={js} py={py}")
    # 2. 誕生日ページの相性リストと型
    for k, ((i, j), r) in enumerate(zip(rel_cases[:n_listed], out["rel"][:n_listed])):
        kind = "good" if KEYS[j] in [g["mmdd"] for g in COMP[KEYS[i]]["good"]] else "bad"
        ok = (r["listed"] == kind and ((kind == "good" and r["type"] in "hkn" and r["level"] >= 4) or
                                        (kind == "bad" and r["type"] in "sm" and r["level"] <= 2)))
        if not ok:
            bad.append(f"list {KEYS[i]}-{KEYS[j]} {kind}: {r['type']} {r['level']} {r['listed']}")
    # 型と5段階の対応（リスト外の組も）
    for (i, j), r in zip(rel_cases, out["rel"]):
        py = scores(BASE[KEYS[i]], BASE[KEYS[j]])
        if r["listed"] is None:
            exp_t = {120: "h", 60: "k", 0: "n"}.get(py[1]) or {90: "s", 180: "m"}.get(py[3]) or "o"
            exp_l = 5 if py[0] >= 1 else 4 if py[0] > 0 else 1 if py[2] >= .9 else 2 if py[2] > 0 else 3
            if (r["type"], r["level"]) != (exp_t, exp_l):
                bad.append(f"rel {KEYS[i]}-{KEYS[j]}: {r['type']}{r['level']} != {exp_t}{exp_l}")
    # 3. 文
    combos = set()
    for (i, j), r in zip(rel_cases, out["rel"]):
        t = r["t"]
        alltext = t["name"] + t["lead"] + t["num"] + t["elem"] + "".join(t["tips"]) + t["list"]
        if (not all([t["name"], t["lead"], t["num"], t["elem"], t["list"]]) or len(t["tips"]) != 2 or "{" in alltext
                or "undefined" in alltext or re.search(r"[0-9０-９]+ *度|度数|角度", alltext) or "動物占い" in alltext
                or "六星" in alltext or "\\" in alltext or "！" in alltext):
            bad.append(f"text {KEYS[i]}-{KEYS[j]}: {alltext[:80]}")
        combos.add((t["lead"], t["num"], t["elem"]))
    # 4. 九星
    if out["ky"] != kyusei_table():
        bad.append(f"kyusei table {out['ky']}")
    exp_h = [KK.honmei(dt.datetime(y, m, d, 12, 0)) for y, m, d in hon_cases]  # 正午で計算（JS と同じ）
    if out["hon"] != exp_h:
        bad.append(f"honmei {out['hon']} != {exp_h}")
    c = out["count"]
    n_rel = sum(v[0] for v in c["rel"].values())
    n_tip = sum(v[1] for v in c["rel"].values())
    n_num = sum(v[0] + v[1] for v in c["num"].values())
    n_ntip = sum(v[2] for v in c["num"].values())
    print(f"点数の照合 {len(sc_cases)}組／相性リストの照合 {n_listed}組／型と5段階 {len(rel_cases)}組")
    print(f"文の種類：関係の型の文 {n_rel}・数のグループの文 {n_num}・星座の性質の文 {c['el']}・コツ {n_tip}＋{n_ntip}")
    print(f"テストした {len(rel_cases)} 組で、本文（型の文＋数の文＋星座の文）の組み合わせは {len(combos)} 通り")
    for b in bad[:20]:
        print("NG", b)
    print("OK" if not bad else f"NG {len(bad)}件")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
