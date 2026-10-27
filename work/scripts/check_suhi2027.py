# -*- coding: utf-8 -*-
"""suhi2027_texts.py（数秘術 2027年の運勢）の検査。
使い方: python3 work/scripts/check_suhi2027.py   （Windows: .venv\\Scripts\\python -X utf8 work\\scripts\\check_suhi2027.py）
"""
import ast
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import suhi2027_texts as T  # noqa: E402

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


# ---- 計算値 ----
data = json.load(open(os.path.join(WORK, "data", "suhi_2027.json"), encoding="utf-8"))
PM = {int(k): v["pm"] for k, v in data["py"].items()}


def pm_of(py, month_label):
    m = int(month_label.rstrip("月"))
    return PM[py][m - 1]


def rng(s, lo, hi, where):
    n = len(s)
    if not (lo <= n <= hi):
        err(f"{where}: {n}字（{lo}〜{hi}）")


# ---- 形と分量 ----
if sorted(T.TEXTS) != list(range(1, 10)):
    err("TEXTS のキーが 1〜9 ではない")
rng(T.INTRO.get("year11", ""), 200, 280, "INTRO.year11")
rng(T.INTRO.get("how", ""), 120, 180, "INTRO.how")

# 例の計算（5月15日→4）
ex = sum(int(c) for c in "2027" + "5" + "15")
while ex > 9:
    ex = sum(int(c) for c in str(ex))
if ex != 4 or "=22" not in T.INTRO["how"] or "「4」" not in T.INTRO["how"]:
    err("INTRO.how の計算例が合わない")
if "4+3=7" in T.INTRO["how"] and PM[4][2] != 7:
    err("INTRO.how の月の例（4の人の3月）が計算値と合わない")

FIELDS = {"title": (6, 12), "where": (60, 100), "sougou": (220, 290), "love": (140, 190),
          "work": (140, 190), "money": (110, 160), "health": (90, 140)}
all_months = []
for py in range(1, 10):
    t = T.TEXTS.get(py, {})
    for f, (lo, hi) in FIELDS.items():
        if f not in t:
            err(f"PY{py}: {f} がない")
            continue
        rng(t[f], lo, hi, f"PY{py}.{f}")
    prev = 9 if py == 1 else py - 1
    if f"2026年は{prev}の年" not in t.get("where", ""):
        err(f"PY{py}.where: 2026年＝{prev}の年 の記述がない")

    # 総合運の月の数
    claims = re.findall(r"月の数が(\d)になる(\d{1,2})月", t.get("sougou", ""))
    if not (1 <= len(claims) <= 2):
        err(f"PY{py}.sougou: 月の数の記述が {len(claims)} 件（1〜2件）")
    for n, m in claims:
        if PM[py][int(m) - 1] != int(n):
            err(f"PY{py}.sougou: {m}月の月の数は {PM[py][int(m)-1]}（本文は{n}）")
    named = set(re.findall(r"(?<![\d年])(\d{1,2})月", t.get("sougou", "")))
    if named - {m for _, m in claims}:
        err(f"PY{py}.sougou: 月の数を書いていない月 {named - {m for _, m in claims}}")

    for key, allowed, lo, hi in (("push_months", {1, 3, 5, 8}, 2, 3), ("rest_months", {4, 7, 9}, 1, 2)):
        lst = t.get(key, [])
        if not (lo <= len(lst) <= hi):
            err(f"PY{py}.{key}: {len(lst)}件（{lo}〜{hi}）")
        for mon, why in lst:
            p = pm_of(py, mon)
            if p not in allowed:
                err(f"PY{py}.{key}: {mon} の月の数は {p}（{sorted(allowed)} のみ）")
            mm = re.match(r"月の数が(\d)", why)
            if mm and int(mm.group(1)) != p:
                err(f"PY{py}.{key}: {mon} 理由の数 {mm.group(1)} が計算値 {p} と違う")
            rng(why, 25, 40, f"PY{py}.{key}.{mon}")
        if len({m for m, _ in lst}) != len(lst):
            err(f"PY{py}.{key}: 同じ月が重複")
    if {m for m, _ in t.get("push_months", [])} & {m for m, _ in t.get("rest_months", [])}:
        err(f"PY{py}: push と rest に同じ月")

    ms = t.get("months", [])
    if len(ms) != 12:
        err(f"PY{py}.months: {len(ms)}件（12件）")
    for i, s in enumerate(ms):
        rng(s, 35, 60, f"PY{py}.months[{i+1}月]")
        mm = re.search(r"月の数が(\d)", s)
        if mm and int(mm.group(1)) != PM[py][i]:
            err(f"PY{py}.months[{i+1}月]: 月の数 {mm.group(1)} が計算値 {PM[py][i]} と違う")
    all_months += ms

    acts = t.get("action", [])
    if len(acts) != 3:
        err(f"PY{py}.action: {len(acts)}件（3件）")
    for a in acts:
        rng(a, 15, 30, f"PY{py}.action「{a}」")

if len(all_months) != 108 or len(set(all_months)) != 108:
    err(f"months: 108件のうち重複なしは {len(set(all_months))} 件")

titles = [T.TEXTS[p]["title"] for p in T.TEXTS]
if len(set(titles)) != len(titles):
    err("title が重複")
heads = [T.TEXTS[p]["sougou"][:6] for p in T.TEXTS]
if len(set(heads)) != len(heads):
    err("sougou の書き出しが重複")

# ---- 禁止表現 ----
mine = list(strings_in(T.INTRO)) + list(strings_in(T.TEXTS))
for s in mine:
    for bad in ("！", "!", "六星占術", "動物占い"):
        if bad in s:
            err(f"禁止表現「{bad}」: {s[:30]}")

# ---- 15字の重複検査 ----
# 対象にする自分の文：月名だけ（"4月" など）は除く
mine_long = [s for s in mine if len(s) >= N]


def grams(s):
    return {s[i:i + N] for i in range(len(s) - N + 1)}


# 自分のファイルの中（別の文どうし）
seen = {}
for idx, s in enumerate(mine_long):
    for g in grams(s):
        if g in seen and seen[g] != idx:
            err(f"ファイル内の重複「{g}」")
        seen.setdefault(g, idx)

# 公開済みの文
pub = []
pub += list(strings_in(assigned_literals(os.path.join(HERE, "suhi_texts.py"), None)))
pub += list(strings_in(assigned_literals(os.path.join(HERE, "build_suhi.py"), {"PY_GOODS"})))
pub += list(strings_in(assigned_literals(os.path.join(HERE, "nenun2027_texts.py"), {"TEXTS2027", "ETO2027"})))
pub += list(strings_in(assigned_literals(os.path.join(HERE, "eto2027_texts.py"), {"TEXTS", "INTRO"})))
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
    hit = grams(s) & pubgrams
    for g in sorted(hit):
        err(f"公開済みの文と重複「{g}」")

print(f"検査した自分の文: {len(mine)} 本 / 月のヒント: {len(all_months)} 本（重複なし {len(set(all_months))}）")
print(f"照合した公開済みの文: {len(pub)} 本（日ごとのJSON {n_files} ファイル）")
if errors:
    print(f"NG: {len(errors)} 件")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("OK: すべての検査に合格")
