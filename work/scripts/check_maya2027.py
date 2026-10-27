# -*- coding: utf-8 -*-
"""maya2027_texts.py（マヤ暦 2027年の運勢｜20の太陽の紋章別）の検査。
使い方: python3 work/scripts/check_maya2027.py   （Windows: .venv\\Scripts\\python -X utf8 work\\scripts\\check_maya2027.py）
"""
import ast
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import maya2027_texts as T  # noqa: E402

N = 15  # 同じ文字の並びの上限（これ以上は重複とみなす）
errors = []


def err(msg):
    errors.append(msg)


def strings_in(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from strings_in(v)
    elif isinstance(obj, (list, tuple, set)):
        for v in obj:
            yield from strings_in(v)


def assigned_literals(path, names):
    """ファイルを実行せず、指定した名前の代入値（リテラル）を取り出す"""
    tree = ast.parse(open(path, encoding="utf-8").read())
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and (names is None or t.id in names):
                    try:
                        out[t.id] = ast.literal_eval(node.value)
                    except Exception:
                        pass
    return out


def y2027_strings(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "y2027":
                yield from strings_in(v)
            else:
                yield from y2027_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from y2027_strings(v)


def md_table_texts(path):
    """知識ファイルの表（紋章・音）の説明文の列"""
    out = []
    for line in open(path, encoding="utf-8"):
        if line.startswith("|") and not line.startswith("|---"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 4 and cells[0].isdigit():
                out.append(cells[-1])
    return out


def rng(s, lo, hi, where):
    n = len(s)
    if not (lo <= n <= hi):
        err(f"{where}: {n}字（{lo}〜{hi}）")


# ---- 計算値 ----
data = json.load(open(os.path.join(WORK, "data", "maya_2027.json"), encoding="utf-8"))
SEALS = {int(k): v for k, v in data["seals"].items()}

# ---- 形と分量 ----
if sorted(T.TEXTS) != list(range(1, 21)):
    err("TEXTS のキーが 1〜20 ではない")
rng(T.INTRO.get("year", ""), 230, 300, "INTRO.year")
rng(T.INTRO.get("rels", ""), 160, 230, "INTRO.rels")
y = T.INTRO.get("year", "")
for must in ("7月26日", "白い魔法使い", "音9", "赤い月", "音8", "ドリームスペル", "現代"):
    if must not in y:
        err(f"INTRO.year:「{must}」がない")
for must in ("同じ紋章", "類似", "反対", "神秘", "同じ色"):
    if must not in T.INTRO.get("rels", ""):
        err(f"INTRO.rels:「{must}」がない")

FIELDS = {"title": (6, 12), "sougou": (220, 290), "first": (80, 120), "second": (80, 120),
          "love": (140, 190), "work": (140, 190), "money": (110, 160), "health": (90, 140),
          "seal_day": (50, 80)}
for no in range(1, 21):
    t = T.TEXTS.get(no, {})
    s = SEALS[no]
    for f, (lo, hi) in FIELDS.items():
        if f not in t:
            err(f"{no}{s['name']}: {f} がない")
            continue
        rng(t[f], lo, hi, f"{no}{s['name']}.{f}")
    acts = t.get("action", [])
    if len(acts) != 3:
        err(f"{no}{s['name']}.action: {len(acts)}件（3件）")
    for a in acts:
        rng(a, 15, 30, f"{no}{s['name']}.action「{a}」")
    sg = t.get("sougou", "")
    if s["name"] not in sg:
        err(f"{no}: sougou に紋章名「{s['name']}」がない")
    if s["rel27"] and s["rel27"] not in sg:
        err(f"{no}{s['name']}: sougou に今年の関係「{s['rel27']}」がない")
    if s["rel26"] and s["rel26"] not in sg + t.get("first", ""):
        err(f"{no}{s['name']}: sougou/first に前年の関係「{s['rel26']}」がない")
    # 関係のない語を誤って書いていないか（関係のある語以外の関係名）
    rels = {s["rel27"], s["rel26"]} - {None}
    for word in ("類似", "反対", "神秘"):
        if word in sg and word not in rels:
            err(f"{no}{s['name']}: sougou に関係のない「{word}」がある")
    if "白い魔法使い" not in sg or "赤い月" not in sg:
        err(f"{no}: sougou に両方の年の紋章名がない")

titles = [T.TEXTS[p]["title"] for p in T.TEXTS]
if len(set(titles)) != len(titles):
    err("title が重複")
heads = [T.TEXTS[p]["sougou"][:6] for p in T.TEXTS]
if len(set(heads)) != len(heads):
    err(f"sougou の書き出しが重複: {sorted(h for h in heads if heads.count(h) > 1)}")

# ---- 禁止表現 ----
mine = list(strings_in(T.INTRO)) + list(strings_in(T.TEXTS))
for s in mine:
    for bad in ("！", "!", "六星占術", "動物占い", "ウェイブスペル", "ウェーブスペル", "黒KIN", "黒キン"):
        if bad in s:
            err(f"禁止表現「{bad}」: {s[:30]}")

# ---- 15字の重複検査 ----
mine_long = [s for s in mine if len(s) >= N]


def grams(s):
    return {s[i:i + N] for i in range(len(s) - N + 1)}


seen = {}
for idx, s in enumerate(mine_long):
    for g in grams(s):
        if g in seen and seen[g] != idx:
            err(f"ファイル内の重複「{g}」")
        seen.setdefault(g, idx)

pub = []
pub += list(strings_in(assigned_literals(os.path.join(HERE, "maya_texts.py"), None)))
pub += list(strings_in(assigned_literals(os.path.join(HERE, "build_maya.py"), {"FAQ", "COLOR"})))
pub += list(strings_in(assigned_literals(os.path.join(HERE, "nenun2027_texts.py"), {"TEXTS2027", "ETO2027"})))
pub += list(strings_in(assigned_literals(os.path.join(HERE, "eto2027_texts.py"), {"TEXTS", "INTRO"})))
pub += list(strings_in(assigned_literals(os.path.join(HERE, "suhi2027_texts.py"), {"TEXTS", "INTRO"})))
pub += md_table_texts(os.path.join(WORK, "knowledge", "07_マヤ暦.md"))
n_files = 0
for f in glob.glob(os.path.join(WORK, "text", "*", "*.json")):
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception:
        continue
    n_files += 1
    pub += list(y2027_strings(d))
pubgrams = set()
for s in pub:
    pubgrams |= grams(s)
for s in mine_long:
    for g in sorted(grams(s) & pubgrams):
        err(f"公開済みの文と重複「{g}」")

print(f"検査した自分の文: {len(mine)} 本")
print(f"照合した公開済みの文: {len(pub)} 本（日ごとのJSON {n_files} ファイル）")
if errors:
    print(f"NG: {len(errors)} 件")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("OK: すべての検査に合格")
