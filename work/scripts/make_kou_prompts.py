"""七十二候の見出し画像（72枚）を ComfyUI で作るための指示文の一覧を出す。
出力：images/kou_prompts.csv（ファイル名・候・読み・指示文）と images/kou_prompts.md（本人向けの手順）"""
import csv, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(HERE, "..")
SCENE = {
1: "spring east wind melting thin ice on a pond, cracks in the ice, early morning light",
2: "Japanese bush warbler (uguisu) singing on a plum branch in a quiet village garden",
3: "fish rising near broken ice on a cold clear river",
4: "spring rain falling on soft moist farmland soil, mist",
5: "first spring haze over gentle hills and fields, pale sky",
6: "grasses and young shoots sprouting in a meadow, delicate green",
7: "hibernating insects waking, opening the earth, small beetle on fresh soil",
8: "first peach blossoms opening on a branch",
9: "cabbage white butterflies emerging from cocoons among spring flowers",
10: "sparrows starting to build a nest under the eaves of an old wooden house",
11: "first cherry blossoms opening, a single branch against soft sky",
12: "distant spring thunder clouds over fields, first rumble",
13: "swallows arriving, flying low over rice fields",
14: "wild geese flying north in a V formation at dusk",
15: "first rainbow after a spring shower over a valley",
16: "reeds sprouting at the edge of a water pond",
17: "frost ending, rice seedlings growing in a seedbed",
18: "peony flowers in full bloom in a garden",
19: "frogs beginning to sing in a flooded rice paddy at evening",
20: "earthworms appearing on damp garden soil after rain",
21: "bamboo shoots emerging from the forest floor",
22: "silkworms eating mulberry leaves",
23: "safflower (benibana) field in bloom, orange-red flowers",
24: "golden wheat ripening in a field, early summer",
25: "praying mantis hatching on a green leaf",
26: "fireflies rising from wet grass by a stream at night",
27: "green plums turning yellow on a tree in early summer rain",
28: "self-heal (utsubogusa) flowers withering in a summer meadow",
29: "iris flowers (ayame) blooming by a pond",
30: "crow-dipper (hange) plant growing in a rice field edge",
31: "warm summer wind blowing through bamboo and wind chimes",
32: "lotus flowers beginning to bloom in a pond, morning",
33: "young hawk learning to fly over summer forest",
34: "paulownia tree bearing fruit pods, midsummer",
35: "steamy hot humid ground after summer rain, lush green",
36: "great summer rain shower over mountains and rice fields",
37: "cool breeze arriving at the end of summer, white curtains, evening",
38: "evening cicadas (higurashi) singing in a cedar forest at dusk",
39: "thick morning fog over a mountain lake",
40: "cotton bolls opening on the plant",
41: "heat finally easing, early autumn sky with high clouds",
42: "rice ears ripening in golden paddies",
43: "white dew drops on grass in early autumn morning",
44: "wagtails singing by a river stone",
45: "swallows leaving, flying south over autumn fields",
46: "thunder quietening, clear autumn sky after rain",
47: "insects closing up their burrows for winter, autumn leaves on soil",
48: "water draining from rice paddies before harvest, golden fields",
49: "wild geese arriving from the north, flying over autumn marsh",
50: "chrysanthemums in bloom in a traditional garden",
51: "crickets singing near the door of a wooden house at night, autumn",
52: "first frost on fallen leaves and grass",
53: "light cold drizzle in late autumn, wet maple leaves",
54: "maple and ivy leaves turning red and yellow on a mountain",
55: "camellia sasanqua flowers starting to bloom in early winter",
56: "the land beginning to freeze, frost crystals on soil",
57: "daffodils blooming in early winter by the sea",
58: "rainbows hiding, grey winter sky over a quiet field",
59: "north wind blowing leaves off trees, bare branches",
60: "tachibana citrus fruits turning yellow on the tree",
61: "heavy grey winter sky, thick clouds before snow",
62: "bear hibernating in a cave in a snowy forest",
63: "salmon swimming upstream in a cold river",
64: "self-heal sprouting under winter snow, small green shoot",
65: "deer shedding antlers in a winter forest",
66: "wheat sprouting under snow in a winter field",
67: "Japanese parsley (seri) growing thick by a cold stream",
68: "spring water starting to move under ice, winter brook",
69: "pheasant calling in a winter field",
70: "butterbur sprouts (fukinoto) coming up through snow",
71: "thick ice covering a mountain stream, midwinter",
72: "hen starting to lay eggs in a farmyard in late winter",
}
STYLE = ("soft watercolor and gouache illustration, Japanese seasonal atmosphere, gentle muted colors, "
         "simple composition with empty space, no text, no people's faces, wide banner 16:9")
NEG = "text, letters, watermark, logo, signature, photo, photorealistic, people, face, hands, frame, border, lowres, blurry"


def main():
    d = json.load(open(os.path.join(W, "data", "sekki_2027.json"), encoding="utf-8"))
    kou = {}
    for x in d:
        kou.setdefault(x["kou_serial"], x)
    os.makedirs(os.path.join(W, "images"), exist_ok=True)
    rows = []
    for n in range(1, 73):
        x = kou[n]
        rows.append({"file": f"kou-{n:02d}.png", "no": n, "kou": x["kou"], "yomi": x["kou_yomi"], "sekki": x["parent_sekki"],
                     "prompt": f"{SCENE[n]}, {STYLE}", "negative": NEG})
    with open(os.path.join(W, "images", "kou_prompts.csv"), "w", encoding="utf-8-sig", newline="") as fp:
        w = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    md = ["# 七十二候の見出し画像 72枚（ComfyUI 用）", "",
          "- 大きさ：1344×768（横長16:9。サイトでは幅いっぱいの帯にする）。PNG で保存",
          "- ファイル名は下の表のとおり（kou-01.png〜kou-72.png）。できたら `work/images/kou/` にまとめて置くか、フォルダごと渡してください",
          "- 共通のネガティブ：" + NEG, "- 絵柄をそろえるため、シード以外の設定（モデル・サンプラー・ステップ）は72枚とも同じにする", "",
          "| ファイル | 候 | 読み | 指示文 |", "|---|---|---|---|"]
    md += [f"| {r['file']} | {r['kou']} | {r['yomi']} | {r['prompt']} |" for r in rows]
    open(os.path.join(W, "images", "kou_prompts.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("72件 → images/kou_prompts.csv・kou_prompts.md")


if __name__ == "__main__":
    main()
