"""フェーズ3：誕生日もの・記念日 → work/data/birthday_items_366.csv（＋同じ内容の JSON）
列：MMDD, 項目, 値, 補足, 出典, 確認済み
- 誕生石（月）：全国宝石卸商協同組合 2021年改定（knowledge/10）
- 誕生色（サイト独自）：その日の七十二候にちなむ日本の伝統色。候ごとに6色の候補を、候の中の日の順に割り当てる（隣の日とは必ず別の色）
- 誕生日石（サイト独自）：その月の誕生石・デーカンの支配星に対応する石・誕生色に近い色の石から、販売されている石を選ぶ（隣の日とは別、使用回数を平均化）
- 記念日・できごと：src_events_*.json（1日2〜3件、出典URLつき）
- 誕生花・花言葉：日本花普及センターの一覧PDF待ち（source/birthday/hanakotoba.pdf）
"""
import json, os, csv, glob, colorsys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
BIRTHSTONE = {1: ["ガーネット"], 2: ["アメシスト", "クリソベリル・キャッツアイ"], 3: ["アクアマリン", "サンゴ", "ブラッドストーン", "アイオライト"],
              4: ["ダイヤモンド", "モルガナイト"], 5: ["エメラルド", "ヒスイ"], 6: ["真珠", "ムーンストーン", "アレキサンドライト"],
              7: ["ルビー", "スフェーン"], 8: ["サードオニックス", "ペリドット", "スピネル"], 9: ["サファイア", "クンツァイト"],
              10: ["オパール", "トルマリン"], 11: ["トパーズ", "シトリン"], 12: ["ターコイズ", "ラピスラズリ", "タンザナイト", "ジルコン"]}
BIRTHSTONE_SRC = "全国宝石卸商協同組合 2021年12月改定（デイリースポーツ https://www.daily.co.jp/society/life/2021/12/20/0014929848.shtml ほか。work/knowledge/10_誕生日もの.md）"
OWN_COLOR = "当サイト独自の選び方（七十二候にちなむ日本の伝統色。work/knowledge/10_誕生日もの.md）"
OWN_STONE = "当サイト独自の選び方（誕生石・デーカンの支配星・誕生色から、販売されている石。work/knowledge/10_誕生日もの.md）"


def family(hexs):
    r, g, b = (int(hexs[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    h *= 360
    if l > .88: return "白"
    if l < .15: return "黒"
    if s < .15: return "灰"
    if (h < 40 or h >= 20) and l < .4 and 15 <= h < 50: return "茶"
    if h >= 330 or h < 15: return "桃" if l > .7 else "赤"
    if h < 45: return "橙"
    if h < 70: return "黄"
    if h < 170: return "緑"
    if h < 215: return "青"
    if h < 255: return "藍"
    if h < 300: return "紫"
    return "桃"


def main():
    base = json.load(open(os.path.join(DATA, "base_366.json"), encoding="utf-8"))
    keys = list(base)
    colors = {}
    for f in sorted(glob.glob(os.path.join(DATA, "src_colors_kou*.json"))):
        for k in json.load(open(f, encoding="utf-8"))["kou"]:
            colors[k["kou_serial"]] = k["colors"]
    stones = json.load(open(os.path.join(DATA, "src_stones.json"), encoding="utf-8"))["stones"]
    events = {}
    for f in sorted(glob.glob(os.path.join(DATA, "src_events_*.json"))):
        events.update(json.load(open(f, encoding="utf-8")))

    rows, out = [], {}
    # 誕生色：候ごとに、候の中の日の順番で6色を回す
    color_of = {}
    used = collections.Counter()
    pos = collections.Counter()
    prev = None
    for k in keys:
        s = base[k]["kou_serial"]
        cands = colors.get(s)
        if not cands:
            continue
        i = pos[s]
        order = cands[i % len(cands):] + cands[:i % len(cands)]  # 候の中の順番を基本に
        order = [c for c in order if not prev or c["name"] != prev["name"]]
        order = [c for c in order if c.get("hex_checked")] or order  # 確認済みの色を優先
        c = min(order, key=lambda c: used[c["name"]])  # まだ使っていない色を優先
        pos[s] += 1
        used[c["name"]] += 1
        color_of[k] = c
        prev = c
    # 誕生日石
    use = collections.Counter()
    stone_of, prev = {}, None
    for k in keys:
        r = base[k]
        fam = family(color_of[k]["hex"]) if k in color_of else None
        best = None
        for st in stones:
            sc = 0.0
            why = []
            if st["name"] in BIRTHSTONE[r["month"]]: sc += 2; why.append(f"{r['month']}月の誕生石")
            if r["decan_ruler"] in st.get("planets", []): sc += 2; why.append(f"デーカンの支配星・{r['decan_ruler']}の石")
            if fam and fam in st.get("color_family", []): sc += 1; why.append(f"誕生色（{color_of[k]['name']}）に近い{fam}系")
            if sc == 0: continue
            sc += 1.5 if st.get("sold_checked") else 0
            sc -= .6 * use[st["name"]]
            if prev == st["name"]: continue
            if best is None or sc > best[0]: best = (sc, st, why)
        if best:
            stone_of[k] = (best[1], best[2]); use[best[1]["name"]] += 1; prev = best[1]["name"]
    for k in keys:
        r = base[k]
        m = r["month"]
        items = []
        items.append(["誕生石（月）", "・".join(BIRTHSTONE[m]), "", BIRTHSTONE_SRC, True])
        if k in color_of:
            c = color_of[k]
            items.append(["誕生色", c["name"], f"{c['yomi']}／{c['hex']}／{c['reason']}（{r['kou']}にちなむ）",
                          OWN_COLOR + ("・色の値：" + c["hex_source"] if c.get("hex_source") else ""), bool(c.get("hex_checked"))])
        if k in stone_of:
            st, why = stone_of[k]
            items.append(["誕生日石", st["name"], f"{'・'.join(why)}。{st['meaning']}",
                          OWN_STONE + ("・販売例：" + st["sold_url"] if st.get("sold_url") else ""), bool(st.get("sold_checked"))])
        items.append(["誕生花", "", "日本花普及センターの一覧PDF待ち", "一般財団法人日本花普及センター「誕生花」（長野県 https://www.pref.nagano.lg.jp/enchiku/sangyo/nogyo/engei-suisan/kaki/documents/hanakotoba.pdf）", False])
        for e in events.get(k, []):
            items.append([f"記念日・できごと（{e['kind']}）", e["title"], (f"{e['year']}年。" if e.get("year") else "") + e["text"], e.get("source_url") or "", bool(e.get("confirmed"))])
        out[k] = [dict(zip(["項目", "値", "補足", "出典", "確認済み"], it)) for it in items]
        rows += [[k] + it for it in items]
    with open(os.path.join(DATA, "birthday_items_366.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["MMDD", "項目", "値", "補足", "出典", "確認済み"])
        w.writerows(rows)
    json.dump(out, open(os.path.join(DATA, "birthday_items_366.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    return out, use


if __name__ == "__main__":
    o, use = main()
    print(len(o), "日", sum(len(v) for v in o.values()), "行")
    print("石の使用", use.most_common(8), "種類", len(use))
    for k in ["0101", "0715"]:
        for it in o[k]: print(k, it["項目"], it["値"], it["確認済み"])
