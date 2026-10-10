"""共通JS（work/out/assets/fh-b27.js）の計算が、Python の計算スクリプトと一致するかを突き合わせるテスト。

使い方:
  python work/scripts/build_html.py --sample 0101      # 先にアセットを作る
  python work/scripts/test_js_calc.py                  # node で JS を動かして比較（node 22 で確認）

比べるもの（生まれ年パネルの全項目）:
  本命星・2027年の位置（calc_kanshi_kyusei.honmei / ban）／年柱・月柱・日柱（year_index / month_index / day_index）
  旧暦の月日・本命宿（kyureki_1900_2030.json ＋ calc_kyureki.shuku）／マヤ暦KIN（calc_maya_num_bio.kin）
  ライフパス（life_path）／動物×色（calc_animal_color）／バイオリズムの値・★◎〇△▽（bio / mark）
  2027年の好調日（3本平均0.6以上）・注意日（n〜n+1の間にどれかの線が0を横切る。knowledge/09）
誕生時刻は JS と同じく 12:00（日本時間）とする。

node が無い環境では実行できない。その場合は、ブラウザで work/out/sample/MMDD.html を開き、
開発者ツールのコンソールで FHB27Calc.pillars(1990,1,1) などを呼んで、下の Python の値と見比べる。
"""
import datetime as dt, json, math, os, random, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import calc_kanshi_kyusei as KK  # noqa: E402
import calc_kyureki as KY  # noqa: E402
import calc_maya_num_bio as MN  # noqa: E402
from calc_animal_color import animal_color  # noqa: E402

ASSETS = os.path.normpath(os.path.join(HERE, "..", "out", "assets"))
KYU = json.load(open(os.path.join(HERE, "..", "data", "kyureki_1900_2030.json"), encoding="utf-8"))

NODE_HARNESS = r"""
const fs=require('fs'),vm=require('vm');
const [dir,casesPath]=process.argv.slice(2);
const ctx={console};ctx.window=ctx;ctx.globalThis=ctx;vm.createContext(ctx);
for(const f of ['fh-b27-setsuiri.js','fh-b27-kyureki.js','fh-b27.js'])vm.runInContext(fs.readFileSync(dir+'/'+f,'utf8'),ctx,{filename:f});
const C=ctx.FHB27Calc,cases=JSON.parse(fs.readFileSync(casesPath,'utf8'));
const out=cases.map(([y,m,d])=>{
  const h=C.honmei(y,m,d),p=C.pillars(y,m,d),k=C.kyureki(y,m,d),s=C.shuku(y,m,d),kn=C.kin(y,m,d),a=C.animal(y,m,d);
  const j=C.jdn(y,m,d),bio=[];for(const [mm,dd] of [[1,1],[3,15],[7,7],[12,31]]){const v=C.bioAt(C.jdn(2027,mm,dd)-j);bio.push(v.map(x=>Math.round(x*1e6)/1e6).concat(v.map(x=>C.bioMark(x)[0])));}
  const bd=C.bioDays(y,m,d);
  return {honmei:h.star,palace:C.palace2027(h.star),year:p.year,month:p.month,day:p.day,
    kyu:k?[k.month,k.leap,k.day]:null,shuku:s?s.name:null,kin:kn.kin,seal:kn.seal,tone:kn.tone,
    lp:C.lifePath(y,m,d),animal:a.label,bio:bio,good:bd.good,care:bd.care,setsuDay:C.setsuDay(y,m,d),dk:C.dayKanshiIndex(2027,m===2&&d===29?3:m,m===2&&d===29?1:d)};
});
process.stdout.write(JSON.stringify(out));
"""


def py_case(y, m, d):
    t = dt.datetime(y, m, d, 12, 0)
    date = t.date()
    hs = KK.honmei(t)
    ban = KK.ban(KK.honmei(dt.datetime(2027, 6, 1)))
    palace = next(k for k, v in ban.items() if v == KK.KYUSEI[hs])
    kyu = KYU.get(date.isoformat())
    lab = lambda x: f"{x.month}/{x.day}"  # noqa: E731
    good, care = [], []
    for k in range(365):
        x = dt.date(2027, 1, 1) + dt.timedelta(days=k)
        n = (x - date).days
        if n < 0:  # 生まれる前の日は数えない（2027年生まれ）
            continue
        v = MN.bio(date, x)
        if sum(v.values()) / 3 >= 0.6:
            good.append(lab(x))
        if any(math.ceil(2 * n / p) < 2 * (n + 1) / p for p in (23, 28, 33)):
            care.append(lab(x))
    bio = []
    for mm, dd in [(1, 1), (3, 15), (7, 7), (12, 31)]:
        v = list(MN.bio(date, dt.date(2027, mm, dd)).values())
        bio.append([round(x, 6) for x in v] + [MN.mark(x) for x in v])
    sd = None
    for name, s in KK.setsu()[str(y)].items():
        if s[:10] == date.isoformat() and name in KK.SETSU_ORDER:
            sd = name
    ki = MN.kin_info(date)
    return {"honmei": hs, "palace": palace, "year": KK.kanshi(KK.year_index(t)), "month": KK.kanshi(KK.month_index(t)),
            "day": KK.kanshi(KK.day_index(date)), "kyu": [kyu[1], kyu[2], kyu[3]] if kyu else None,
            "shuku": KY.shuku(kyu[1], kyu[3]) if kyu else None, "kin": ki["kin"], "seal": ki["seal"], "tone": ki["tone_no"],
            "lp": MN.life_path(date), "animal": animal_color(y, m, d)["label"], "bio": bio, "good": good, "care": care,
            "setsuDay": sd, "dk": KK.day_index(dt.date(2027, 3, 1) if (m, d) == (2, 29) else dt.date(2027, m, d)) % 60}


def cases():
    random.seed(2027)
    out = set()
    # 固定の確認用（年初・立春前後・節入り前後・2/29・年末・境目の日）
    for y in (1930, 1950, 1964, 1975, 1984, 1988, 1990, 1996, 2000, 2001, 2012, 2020, 2024, 2027, 2028, 2029, 2030):
        for m, d in [(1, 1), (1, 5), (1, 6), (1, 20), (2, 3), (2, 4), (2, 5), (3, 5), (3, 6), (6, 5), (6, 6),
                     (8, 7), (8, 8), (10, 8), (12, 7), (12, 22), (12, 31)]:
            out.add((y, m, d))
    for y in range(1932, 2031, 4):
        out.add((y, 2, 29))
    # 1930〜2030年のすべての節入りの日（時刻で月が切り替わる日）
    for y in range(1930, 2031):
        for name in KK.SETSU_ORDER:
            s = KK.setsu()[str(y)][name]
            out.add((y, int(s[5:7]), int(s[8:10])))
    # 旧暦の閏月の日・月の変わり目を含む無作為の日
    d0 = dt.date(1930, 1, 1)
    for _ in range(600):
        x = d0 + dt.timedelta(days=random.randrange((dt.date(2030, 12, 31) - d0).days + 1))
        out.add((x.year, x.month, x.day))
    leap_days = [k for k, v in KYU.items() if v[2] and "1930" <= k[:4] <= "2030"]
    for k in random.sample(leap_days, 40):
        x = dt.date.fromisoformat(k)
        out.add((x.year, x.month, x.day))
    return sorted(out)


def main():
    node = shutil.which("node")
    if not node:
        print("node が見つかりません。docstring の手順でブラウザから確認してください。")
        return 2
    for f in ("fh-b27.js", "fh-b27-setsuiri.js", "fh-b27-kyureki.js"):
        if not os.path.exists(os.path.join(ASSETS, f)):
            print(f"{f} がありません。先に build_html.py を実行してください。")
            return 2
    cs = cases()
    with tempfile.TemporaryDirectory() as td:
        cp, hp = os.path.join(td, "cases.json"), os.path.join(td, "h.js")
        json.dump(cs, open(cp, "w"))
        open(hp, "w").write(NODE_HARNESS)
        res = subprocess.run([node, hp, ASSETS, cp], capture_output=True, text=True, check=True)
    js = json.loads(res.stdout)
    fails = {}
    for (y, m, d), j in zip(cs, js):
        p = py_case(y, m, d)
        for k in p:
            if p[k] != j[k]:
                fails.setdefault(k, []).append(((y, m, d), p[k] if k not in ("good", "care") else len(p[k]),
                                                j[k] if k not in ("good", "care") else len(j[k])))
    print(f"突き合わせた生年月日: {len(cs)}件 × {len(js[0])}項目")
    if not fails:
        print("結果: すべて一致")
        return 0
    for k, v in fails.items():
        print(f"不一致 {k}: {len(v)}件 例 {v[:3]}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
