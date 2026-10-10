"""動物×色占い（サイト独自・60タイプ）。source/animal-color/計算方法.md（現行 /animal-color/ の calculateAnimal）をそのまま再現。"""
ANIMALS = [("wolf", "狼"), ("monkey", "猿"), ("tiger", "虎"), ("lion", "ライオン"), ("cheetah", "チーター"),
           ("bear", "熊"), ("elephant", "象"), ("koala", "コアラ"), ("sheep", "ひつじ"), ("pegasus", "ペガサス"),
           ("panther", "黒ひょう"), ("tanuki", "たぬき")]
COLORS = [("red", "レッド"), ("gold", "ゴールド"), ("green", "グリーン"), ("blue", "ブルー"), ("purple", "パープル")]


def animal_color(year: int, month: int, day: int) -> dict:
    base = (year + month * 12 + day) % 60
    a, c = ANIMALS[base % 12], COLORS[(base // 12) % 5]
    return {"base": base, "animal_key": a[0], "animal": a[1], "color_key": c[0], "color": c[1],
            "label": f"{a[1]}・{c[1]}"}


if __name__ == "__main__":
    r = animal_color(1990, 1, 1)
    assert r["label"] == "たぬき・ゴールド", r
    types = {animal_color(y, m, d)["label"] for y in range(1930, 2021) for m in range(1, 13) for d in range(1, 32)}
    print(r, "出現タイプ数", len(types))
