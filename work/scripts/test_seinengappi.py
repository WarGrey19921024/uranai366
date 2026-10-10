"""生年月日まるごと診断の結果が Python の計算と一致するかを確かめるテスト。

使い方:
  python work/scripts/build_seinengappi.py
  NODE_PATH=/opt/node22/lib/node_modules PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node work/scripts/screenshot_hub.js /tmp/sg.json
  python work/scripts/test_seinengappi.py /tmp/sg.json

1. 星座（fh-b27.js の sunSign ＋ fh-b27-sign.js）を、1930〜2030年の星座の切り替わりの日の前後すべてと無作為の日で、
   Python（common.lon：正午・日本時間の太陽の視黄経）と突き合わせる（node で実行）
2. screenshot_hub.js が画面から読み取ったカードの表示（何件かの生年月日）を、calc_*.py の計算（test_js_calc.py_case）と突き合わせる
"""
import datetime as dt, json, os, random, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import JST, jd_from_jst, lon  # noqa: E402
from test_js_calc import ASSETS, py_case  # noqa: E402
import calc_kanshi_kyusei as KK  # noqa: E402

SIGNS = ["牡羊座", "牡牛座", "双子座", "蟹座", "獅子座", "乙女座", "天秤座", "蠍座", "射手座", "山羊座", "水瓶座", "魚座"]
EN = ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]
ANI = ["ね", "うし", "とら", "う", "たつ", "み", "うま", "ひつじ", "さる", "とり", "いぬ", "い"]
ANI_JS = ['ねずみ', 'うし', 'とら', 'うさぎ', 'たつ', 'へび', 'うま', 'ひつじ', 'さる', 'とり', 'いぬ', 'いのしし']

HARNESS = r"""
const fs=require('fs'),vm=require('vm');const [dir,cp]=process.argv.slice(2);
const ctx={console};ctx.window=ctx;ctx.globalThis=ctx;vm.createContext(ctx);
for(const f of ['fh-b27-setsuiri.js','fh-b27-kyureki.js','fh-b27-sign.js','fh-b27.js'])vm.runInContext(fs.readFileSync(dir+'/'+f,'utf8'),ctx,{filename:f});
const C=ctx.FHB27Calc;process.stdout.write(JSON.stringify(JSON.parse(fs.readFileSync(cp,'utf8')).map(([y,m,d])=>{const s=C.sunSign(y,m,d);return s?[s.name,s.border]:null;})));
"""


def py_sign(y, m, d):
    return SIGNS[int(lon(jd_from_jst(dt.datetime(y, m, d, 12, tzinfo=JST))) // 30)]


def sign_cases():
    random.seed(366)
    out = set()
    import calc_sekki
    from common import jst_from_jd
    for deg, jd in calc_sekki.crossings(1930, 2030, step_deg=30):
        t = jst_from_jd(jd).date()
        for k in (-1, 0, 1):
            x = t + dt.timedelta(days=k)
            if 1930 <= x.year <= 2030:
                out.add((x.year, x.month, x.day))
    d0 = dt.date(1930, 1, 1)
    for _ in range(500):
        x = d0 + dt.timedelta(days=random.randrange(36889))
        out.add((x.year, x.month, x.day))
    return sorted(out)


def check_signs(node):
    cs = sign_cases()
    with tempfile.TemporaryDirectory() as td:
        cp, hp = os.path.join(td, "c.json"), os.path.join(td, "h.js")
        json.dump(cs, open(cp, "w"))
        open(hp, "w").write(HARNESS)
        js = json.loads(subprocess.run([node, hp, ASSETS, cp], capture_output=True, text=True, check=True).stdout)
    bad = [(c, py_sign(*c), j) for c, j in zip(cs, js) if j is None or j[0] != py_sign(*c)]
    print(f"星座：{len(cs)}件（1930〜2030年の切り替わりの日の前後すべて＋無作為500日）→ 不一致 {len(bad)}件", bad[:5])
    return not bad


def expect(y, m, d):
    p = py_case(y, m, d)
    nk = {"甲": "大樹", "乙": "草花・つる草", "丙": "太陽", "丁": "灯火", "戊": "山", "己": "田畑の土", "庚": "鉄・刃物",
          "辛": "宝石・装飾品", "壬": "海・大河", "癸": "雨・露"}
    eto = KK.kanshi((y - 4) % 60)
    s = py_sign(y, m, d)
    return {"c-sign": s, "c-star": KK.KYUSEI[p["honmei"]], "c-eto": f"{eto}（{ANI_JS[(y - 4) % 12]}）",
            "c-pillars": f'{p["year"]}・{p["month"]}・{p["day"]}', "c-nikkan": f'{p["day"][0]}（{nk[p["day"][0]]}）',
            "c-shuku": f'{p["shuku"]}宿', "c-kin": f'KIN{p["kin"]}', "c-seal": f'{p["seal"]}／音{p["tone"]}',
            "c-lp": str(p["lp"]), "c-animal": p["animal"], "dayHref": f"/366uranai/{m:02d}-{d:02d}/",
            "signHref": f"/{EN[SIGNS.index(s)]}/", "date": f"{y}/{m}/{d}"}


def check_shown(path):
    rows = json.load(open(path, encoding="utf-8"))
    nbad = 0
    for r in rows:
        y, m, d = r["date"]
        ex = expect(y, m, d)
        diff = {k: (v, r["shown"].get(k)) for k, v in ex.items() if r["shown"].get(k) != v}
        nbad += bool(diff)
        print(f"{y}-{m:02d}-{d:02d}", "一致" if not diff else f"不一致 {diff}",
              "｜", r["shown"]["c-sign"], r["shown"]["c-star"], r["shown"]["c-pillars"], r["shown"]["c-shuku"],
              r["shown"]["c-kin"], "LP" + r["shown"]["c-lp"], r["shown"]["c-animal"])
    print(f"画面の表示：{len(rows)}件 × {len(ex)}項目 → 不一致 {nbad}件")
    return nbad == 0


def main():
    node = shutil.which("node")
    if not node:
        print("node が見つかりません")
        return 2
    ok = check_signs(node)
    if len(sys.argv) > 1:
        ok = check_shown(sys.argv[1]) and ok
    print("結果:", "すべて一致" if ok else "不一致あり")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
