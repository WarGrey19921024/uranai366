"""work/text/<星座>/MMDD.json（1日1ファイル）を work/text/<星座>.json にまとめる"""
import json, os, glob, sys
HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(HERE, "..", "text")
for d in sorted(glob.glob(os.path.join(T, "*/"))):
    sign = os.path.basename(os.path.dirname(d))
    out = {os.path.basename(f)[:4]: json.load(open(f, encoding="utf-8")) for f in sorted(glob.glob(os.path.join(d, "*.json")))}
    if out:
        json.dump(out, open(os.path.join(T, f"{sign}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(sign, len(out))
