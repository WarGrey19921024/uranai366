"""フェーズ5：素材表 → work/data/materials_366.json
その日だけの材料を1か所に集める（文章はこの表だけを見て書く）。
- 確認済み（confirmed/確認済み）の値だけを入れる。未確認は入れない（入れたらページに使われてしまうため）
- 誕生花は work/data/flower/birth_flowers_366.tsv（日本花普及センターの一覧の書き起こし。2回読み比べ済みのもの）
"""
import json, os, re, csv, collections

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.join(HERE, "..")
K = os.path.join(W, "knowledge")
SRC = os.path.join(W, "..", "source")
rd = lambda p: open(p, encoding="utf-8").read()


def table_rows(text, ncol_min):
    for line in text.splitlines():
        if line.startswith("|") and not line.startswith("|---"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= ncol_min:
                yield cells


def knowledge():
    k = {}
    t3 = rd(os.path.join(K, "03_二十四節気・七十二候.md"))
    k["kou"] = {int(c[0]): {"meaning": c[7]} for c in table_rows(t3, 8) if c[0].isdigit() and len(c) == 8}
    t1 = rd(os.path.join(K, "01_西洋占星術.md"))
    k["decan"] = {(c[1], int(c[2])): c[8] for c in table_rows(t1, 9) if c[0].isdigit() and c[2] in "123" and len(c) == 9}
    k["sign_traits"] = {}
    for c in table_rows(t1, 3):
        if c[0].endswith("座") and len(c) == 3 and "・" in c[1] and c[0] not in k["sign_traits"]:
            k["sign_traits"][c[0]] = {"good": c[1].split("・"), "bad": c[2].split("・")}
    k["planet"] = {c[0]: {"keywords": c[2], "fields": c[3], "color": c[4]} for c in table_rows(t1, 6)
                   if c[0] in ("太陽", "月", "水星", "金星", "火星", "木星", "土星", "天王星", "海王星", "冥王星") and len(c) == 6}
    t8 = rd(os.path.join(K, "08_数秘術.md"))
    k["num"], k["num_cycle"] = {}, {}
    for c in table_rows(t8, 4):
        if c[0].isdigit():
            n = int(c[0])
            if len(c) == 5 and n not in k["num"]:
                k["num"][n] = {"keyword": c[1], "good": c[2], "bad": c[3], "text": c[4]}
            elif len(c) == 4 and n <= 9:
                k["num_cycle"][n] = {"year": c[1], "month": c[2], "day": c[3]}
    t5 = rd(os.path.join(K, "05_干支・五行・四柱推命.md"))
    k["kanshi"] = {}
    for line in t5.splitlines():
        m = re.match(r"^\|(\d+)\|(..)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|", line)
        if m:
            k["kanshi"][m.group(2)] = {"yomi": m.group(3), "meaning": m.group(6)}
    return k


def famous():
    out = {}
    for f in sorted(os.listdir(os.path.join(SRC, "famous"))):
        cur = None
        for line in rd(os.path.join(SRC, "famous", f)).splitlines():
            m = re.match(r"== (\d{4}) ==", line)
            if m: cur = m.group(1); out[cur] = {"jp": [], "world": []}; continue
            if cur and (line.startswith("JP:") or line.startswith("FR:")):
                key = "jp" if line.startswith("JP:") else "world"
                for p in line[3:].split(" / "):
                    if "|" in p:
                        name, job = p.strip().split("|", 1)
                        out[cur][key].append({"name": name.strip(), "job": job.strip()})
    return out


def main():
    J = lambda n: json.load(open(os.path.join(W, "data", n), encoding="utf-8"))
    base, scores, compat, items = J("base_366.json"), J("scores_366.json"), J("compat_366.json"), J("birthday_items_366.json")
    kn, fam = knowledge(), famous()
    flowers = {}
    fp = os.path.join(W, "data", "flower", "birth_flowers_366.tsv")
    if os.path.exists(fp):
        for row in csv.reader(open(fp, encoding="utf-8"), delimiter="\t"):
            if row and row[0].isdigit():
                flowers[row[0]] = {"flower": row[1], "hanakotoba": row[2]}
    out = {}
    for k, b in base.items():
        s = scores[k]
        it = items.get(k, [])
        pick = lambda name: [i for i in it if i["項目"].startswith(name) and i["確認済み"] and i["値"]]
        stone = pick("誕生日石")
        color = pick("誕生色")
        events = [{"title": i["値"], "kind": i["項目"][i["項目"].find("（") + 1:-1], "text": i["補足"], "source": i["出典"]} for i in pick("記念日")]
        m = {
            "mmdd": k, "month": b["month"], "day": b["day"],
            "sign": b["sign"], "element": b["element"], "mode": b["mode"], "ruler": b["ruler"],
            "sign_traits": kn["sign_traits"].get(b["sign"]),
            "sun_deg_in_sign": b["sun_deg_in_sign"], "sun_lon": b["sun_lon"],
            "sign_border": b["sign_border"], "sign_border_other": b["sign_border_other"],
            "decan": b["decan"], "decan_ruler": b["decan_ruler"], "decan_sign": b["decan_sign"],
            "decan_meaning": kn["decan"].get((b["sign"], b["decan"])), "decan_border": b["decan_border"],
            "decan_ruler_info": kn["planet"].get(b["decan_ruler"]),
            "sekki": b["sekki"], "sekki_day": b["sekki_day"],
            "kou": b["kou"], "kou_yomi": b["kou_yomi"], "kou_serial": b["kou_serial"],
            "kou_meaning": kn["kou"].get(b["kou_serial"], {}).get("meaning"),
            "kou_border": b["kou_border"], "kou_alt": b["kou_alt"],
            "birthday_number": b["birthday_number"], "birthday_number_info": kn["num"].get(b["birthday_number"]),
            "py2027": b["py2027"], "py2027_meaning": kn["num_cycle"].get(b["py2027"], {}).get("year"),
            "flower": flowers.get(k),
            "birthstone_month": [i["値"] for i in it if i["項目"] == "誕生石（月）"][0],
            "birthday_stone": {"name": stone[0]["値"], "note": stone[0]["補足"]} if stone else None,
            "birthday_color": {"name": color[0]["値"], "note": color[0]["補足"]} if color else None,
            "events": events,
            "compat_good": compat[k]["good"], "compat_bad": compat[k]["bad"],
            "scores": {x: s[x] for x in ("astro", "num", "gogyo", "total", "marks")},
            "peak_months": s["peak_months"], "low_months": s["low_months"],
            "field_peak": s["field_peak"], "field_low": s["field_low"], "field_marks": s["field_marks"], "field_peak2": s["field_peak2"], "field_low2": s["field_low2"], "field_peak_use": s["field_peak_use"], "field_low_use": s["field_low_use"], "fields": s["fields"],
            "astro_hits": s["astro_hits"], "gogyo_rel": s["gogyo_rel"],
            "bday2027": dict(b["bday2027"], kanshi_meaning=kn["kanshi"].get(b["bday2027"]["day_kanshi"], {}).get("meaning"),
                             pd_meaning=kn["num_cycle"].get(b["bday2027"]["personal_day"], {}).get("day")),
            "pm2027": b["pm2027"],
            "famous": fam.get(k, {"jp": [], "world": []}),
            "prev": b["prev"], "next": b["next"],
        }
        out[k] = m
    json.dump(out, open(os.path.join(W, "data", "materials_366.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out, kn


if __name__ == "__main__":
    o, kn = main()
    print({x: len(v) for x, v in kn.items()})
    miss = collections.Counter()
    for k, m in o.items():
        for f in ("decan_meaning", "kou_meaning", "birthday_number_info", "flower", "birthday_stone", "birthday_color", "sign_traits", "py2027_meaning"):
            if not m[f]: miss[f] += 1
        if len(m["events"]) < 1: miss["events0"] += 1
        if not m["famous"]["jp"]: miss["famous"] += 1
        if not m["bday2027"]["kanshi_meaning"]: miss["kanshi_meaning"] += 1
    print("欠け", dict(miss))
    print(json.dumps({x: o["0101"][x] for x in ("kou_meaning", "decan_meaning", "flower", "events", "bday2027")}, ensure_ascii=False)[:900])
