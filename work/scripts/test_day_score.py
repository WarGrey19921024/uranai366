"""「その日の総合」（カレンダーの印＝その日のひとことの5段階）の試算（改善第2弾）。

使い方（build_html.py のあと。node で共通JS fh-b27.js の dayScore をそのまま動かす）:
  python work/scripts/test_day_score.py            # 試算 → work/reports/day_score_check.md
  python work/scripts/test_day_score.py --scores [--noyear]  # 点の分布だけ（DAY_CUT・DAY_CUT_NY を決めるとき用）

試算のしかた（本人側の試算と同じ形）:
  無作為の200人（誕生日は366日から、生まれ年は1930〜2020年）× 2027年の365日。生まれ年なし（200人×365日）も別に数える。
  その月の◎○△は、その人の誕生日ページの12か月の運勢（materials_366.json の scores.marks）。
見るもの:
  - 5段階の割合（目安：追い風10〜20%・いい流れ20〜30%・ふつう30〜45%・ひと息15〜25%・休む3〜8%）
  - ◎の月と△の月での「追い風の日」の割合の差
  - 前の作り（カレンダーの印＝バイオリズム3本の平均、ひとこと＝月の運勢を見ない点を四捨五入）で、印とひとことが2段階以上ずれていた日の割合
  - 今の作り：カレンダーの印とひとことは同じ dayScore の結果なので、ずれは0（ページでも screenshot_sample.js で確かめる）
"""
import collections, json, math, os, random, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.join(HERE, "..")
ASSETS = os.path.join(W, "out", "assets")
M = json.load(open(os.path.join(W, "data", "materials_366.json"), encoding="utf-8"))
ELEM_GOGYO = {"火": "火", "地": "土", "風": "木", "水": "水"}
LABEL = ["休む（▽）", "ひと息（△）", "ふつう（〇）", "いい流れ（◎）", "追い風（★）"]
TARGET = [(3, 8), (15, 25), (30, 45), (20, 30), (10, 20)]
N = 200

HARNESS = r"""
const fs=require('fs'),vm=require('vm');const [dir,cp]=process.argv.slice(2);
const ctx={console};ctx.window=ctx;ctx.globalThis=ctx;vm.createContext(ctx);
for(const f of ['fh-b27-setsuiri.js','fh-b27-kyureki.js','fh-b27.js'])vm.runInContext(fs.readFileSync(dir+'/'+f,'utf8'),ctx,{filename:f});
const C=ctx.FHB27Calc,cases=JSON.parse(fs.readFileSync(cp,'utf8'));
const out=cases.map(o=>{const r=[];for(let m=1;m<=12;m++){const n=new Date(2027,m,0).getDate();for(let d=1;d<=n;d++){const x=C.dayScore(o,m,d);
  let bm=null;if(x.bio){const a=x.bio.av;bm=a>=.8?4:a>=.4?3:a>=-.2?2:a>=-.6?1:0;}
  r.push([m,x.score,x.vi,x.mm,bm]);}}return r;});
process.stdout.write(JSON.stringify({cut:Array.from(C.DAY_CUT),cutny:Array.from(C.DAY_CUT_NY),out}));
"""


def people(with_year):
    rnd = random.Random(2027 if with_year else 2028)
    keys = sorted(M)
    out = []
    while len(out) < N:
        k = rnd.choice(keys)
        e = M[k]
        y = rnd.randint(1930, 2020) if with_year else None
        if y and k == "0229" and not (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)):
            continue
        out.append({"M": e["month"], "D": e["day"], "py": e["py2027"], "gogyo": ELEM_GOGYO[e["element"]], "year": y,
                    "marks": e["scores"]["marks"]})
    return out


def run(cases):
    with tempfile.TemporaryDirectory() as td:
        cp, hp = os.path.join(td, "c.json"), os.path.join(td, "h.js")
        json.dump(cases, open(cp, "w", encoding="utf-8"), ensure_ascii=False)
        open(hp, "w").write(HARNESS)
        r = subprocess.run([shutil.which("node"), hp, ASSETS, cp], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def summarize(res, title):
    rows = [x for p in res["out"] for x in p]
    c = collections.Counter(x[2] for x in rows)
    n = len(rows)
    L = [f"### {title}（{n:,}日）", "", "| 5段階 | 割合 | 目安 | |", "|---|---|---|---|"]
    ok_all = True
    for v in range(4, -1, -1):
        pct = 100 * c[v] / n
        lo, hi = TARGET[v]
        ok = lo <= pct <= hi
        ok_all &= ok
        L.append(f"| {LABEL[v]} | {pct:.1f}% | {lo}〜{hi}% | {'✅' if ok else '⚠'} |")
    # 月の◎○△ごとの追い風の割合
    L += ["", "| その月の運勢 | 日数 | 追い風（★）の割合 | 休む・ひと息（▽△）の割合 |", "|---|---|---|---|"]
    by = collections.defaultdict(list)
    for x in rows:
        by[x[3]].append(x[2])
    for mk in ("◎", "○", "△"):
        v = by.get(mk, [])
        if v:
            L.append(f"| {mk}の月 | {len(v):,} | {100 * sum(1 for t in v if t == 4) / len(v):.1f}% | {100 * sum(1 for t in v if t <= 1) / len(v):.1f}% |")
    # 前の作りでのずれ
    old = [x for x in rows if x[4] is not None]
    if old:
        madj = {"◎": .5, "△": -.5}
        def old_vi(x):
            s = x[1] - madj.get(x[3], 0)
            return max(0, min(4, math.floor(s + .5)))
        gap = sum(1 for x in old if abs(old_vi(x) - x[4]) >= 2)
        L.append(f"\n- 前の作り（印＝バイオリズムの平均、ひとこと＝月を見ない点の四捨五入）で、印とひとことが2段階以上ずれていた日：**{100 * gap / len(old):.1f}%**")
    L.append("- 今の作り：カレンダーの印とひとことは同じ計算（dayScore）なので、ずれは **0%**")
    return L, ok_all


def main():
    if "--scores" in sys.argv:
        res = run(people("--noyear" not in sys.argv))
        c = collections.Counter(x[1] for p in res["out"] for x in p)
        n = sum(c.values())
        acc = 0
        for k in sorted(c):
            acc += c[k]
            print(f"{k:6.2f} {100 * c[k] / n:5.1f}% 累計 {100 * acc / n:5.1f}%")
        return 0
    r1 = run(people(True))
    r2 = run(people(False))
    L1, ok1 = summarize(r1, "生まれ年あり（200人×365日）")
    L2, ok2 = summarize(r2, "生まれ年なし（200人×365日）")
    L = ["# その日の総合の試算（改善第2弾）", "", f"`python work/scripts/test_day_score.py` で再生成。区切り：生まれ年あり DAY_CUT＝{r1['cut']}・生まれ年なし DAY_CUT_NY＝{r1['cutny']}（点がこの値以上で △・〇・◎・★）。", ""]
    L += L1 + [""] + L2
    open(os.path.join(W, "reports", "day_score_check.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))
    return 0 if ok1 and ok2 else 1


if __name__ == "__main__":
    sys.exit(main())
