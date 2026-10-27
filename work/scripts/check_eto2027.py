"""eto2027_texts.py（干支別 2027年の運勢）の検査。

使い方: python3 work/scripts/check_eto2027.py
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import eto2027_texts as T  # noqa: E402
import kyusei_texts  # noqa: E402
import nenun2027_texts  # noqa: E402

RUN = 15
MONTHS = ["2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月", "1月"]
SHI = "子丑寅卯辰巳午未申酉戌亥"
RANGES = {
    "title": (6, 12), "sougou": (220, 290), "love": (140, 190), "work": (140, 190),
    "money": (110, 160), "health": (90, 140), "char": (20, 35),
}
BANNED = ["！", "!", "六星占術", "動物占い", "刑", "害"]

errors = []
data = json.load(open(os.path.join(WORK, "data", "eto_2027.json"), encoding="utf-8"))["eto"]


def strings_of(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from strings_of(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from strings_of(v)


def check_len(label, s, lo, hi):
    n = len(s)
    if not lo <= n <= hi:
        errors.append(f"{label}: 長さ {n}（{lo}〜{hi}）")


# --- 構造と長さ ---
if set(T.TEXTS) != set(SHI):
    errors.append(f"TEXTS のキーが12支と一致しない: {sorted(T.TEXTS)}")
for k in SHI:
    t = T.TEXTS.get(k, {})
    for f, (lo, hi) in RANGES.items():
        if f not in t:
            errors.append(f"{k}.{f} がない")
        else:
            check_len(f"{k}.{f}", t[f], lo, hi)
    rel = data[k]["month_rel"]
    ok_good = {MONTHS[i] for i, r in enumerate(rel) if r in ("支合", "三合", "同じ支")}
    chu = [MONTHS[i] for i, r in enumerate(rel) if r == "冲"]
    gm = t.get("good_months", [])
    if not 2 <= len(gm) <= 3:
        errors.append(f"{k}.good_months の数 {len(gm)}")
    for m, why in gm:
        if m not in ok_good:
            errors.append(f"{k}.good_months {m} は支合/三合/同じ支の月ではない（可: {sorted(ok_good)}）")
        check_len(f"{k}.good_months {m}", why, 25, 40)
    cm = t.get("care_month")
    if not cm or [cm[0]] != chu:
        errors.append(f"{k}.care_month {cm and cm[0]} ≠ 冲の月 {chu}")
    else:
        check_len(f"{k}.care_month", cm[1], 25, 40)
    acts = t.get("action", [])
    if len(acts) != 3:
        errors.append(f"{k}.action の数 {len(acts)}")
    for i, a in enumerate(acts):
        check_len(f"{k}.action[{i}]", a, 15, 30)
    # 総合運に出てくる「○月」がデータと矛盾しないか（良い月として挙げた月・冲の月以外は警告）
    sg = t.get("sougou", "")
    mentioned = {m + "月" for m in re.findall(r"(?<![0-9０-９])([0-9]{1,2})月", sg)}
    for m in mentioned:
        if m not in ok_good and m not in chu:
            errors.append(f"{k}.sougou に関係のない月 {m} が出てくる")

check_len("INTRO.rels", T.INTRO["rels"], 200, 280)
check_len("INTRO.toshi", T.INTRO["toshi"], 120, 180)
for age in (12, 24, 36, 48, 60, 72, 84, 96):
    if str(age) not in T.INTRO["toshi"]:
        errors.append(f"INTRO.toshi に {age} がない")

# --- 禁止語 ---
own = list(strings_of(T.TEXTS)) + list(strings_of(T.INTRO))
for s in own:
    for b in BANNED:
        if b in s:
            errors.append(f"禁止語「{b}」: {s[:30]}…")

# --- 15字以上の一致（ファイル内・既存テキスト） ---
# 月名だけの短いタプルの説明等は対象。総合運などの長文が主な対象。
def grams(s):
    return {s[i:i + RUN] for i in range(len(s) - RUN + 1)}


seen = {}
for idx, s in enumerate(own):
    for g in grams(s):
        if g in seen and seen[g] != idx:
            errors.append(f"ファイル内で15字一致: 「{g}」")
        seen.setdefault(g, idx)

ext = []
ext += list(strings_of(nenun2027_texts.ETO2027))
ext += list(strings_of(nenun2027_texts.TEXTS2027))
ext += list(strings_of(kyusei_texts.TEXTS))
for p in glob.glob(os.path.join(WORK, "text", "*", "*.json")) + glob.glob(os.path.join(WORK, "text", "*.json")):
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:
        continue
    e = d.get("y2027", {}).get("eto") if isinstance(d, dict) else None
    if e:
        ext += list(strings_of(e))
ext_grams = set()
for s in ext:
    ext_grams |= grams(s)
for s in own:
    for g in grams(s) & ext_grams:
        errors.append(f"既存テキストと15字一致: 「{g}」")

# --- 総合運の書き出しの重複 ---
heads = [T.TEXTS[k]["sougou"][:6] for k in SHI]
if len(set(heads)) != len(heads):
    errors.append(f"総合運の書き出しが重複: {heads}")

print(f"既存テキスト {len(ext)} 件と比較")
if errors:
    print(f"NG {len(errors)} 件")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("OK: 12支すべての項目・長さ・月・禁止語・15字一致の検査に合格")
