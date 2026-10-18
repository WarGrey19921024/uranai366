"""誕生日ページ366本のOGP画像（SNSで共有したときの画像）を作る。2026-10-18 本人の改善依頼書 2-1
（Diver はアイキャッチが無いと本文の最初の画像＝楽天の商品写真をOGPに使うため、各ページに自前のアイキャッチを付ける）
出力：out/ogp/birthday-MMDD.jpg（1200×630）"""
import json, os, random, sys
from PIL import Image, ImageDraw, ImageFont
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = json.load(open(os.path.join(W, "data", "materials_366.json"), encoding="utf-8"))
SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
SANS = "/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc"
HIRA = {"牡羊座": "おひつじ座", "牡牛座": "おうし座", "双子座": "ふたご座", "蟹座": "かに座", "獅子座": "しし座", "乙女座": "おとめ座",
        "天秤座": "てんびん座", "蠍座": "さそり座", "射手座": "いて座", "山羊座": "やぎ座", "水瓶座": "みずがめ座", "魚座": "うお座"}


def f(path, size):
    return ImageFont.truetype(path, size, index=0)


def draw(k):
    e = M[k]
    img = Image.new("RGB", (1200, 630), "#141824")
    d = ImageDraw.Draw(img)
    rnd = random.Random(int(k))
    for _ in range(140):
        x, y, r = rnd.randint(0, 1199), rnd.randint(0, 629), rnd.choice((1, 1, 1, 2))
        c = rnd.choice(("#3A4366", "#4B5580", "#6B76A8", "#C9B27A"))
        d.ellipse((x - r, y - r, x + r, y + r), fill=c)
    d.rounded_rectangle((40, 40, 1160, 590), radius=28, outline="#C9B27A", width=3)
    hx = (e["birthday_color"]["note"].split("／") + ["", ""])[1]
    if len(hx) == 7 and hx.startswith("#"):
        d.ellipse((1010, 90, 1110, 190), fill=hx, outline="#F1E6C8", width=4)
    d.text((100, 80), "2027年版 誕生日占い", font=f(SANS, 34), fill="#C9B27A")
    d.text((96, 140), f'{e["month"]}月{e["day"]}日', font=f(SERIF, 150), fill="#F6E7B8")
    d.text((100, 330), "生まれの性格と2027年の運勢", font=f(SERIF, 58), fill="#FFFFFF")
    chips = [HIRA[e["sign"]], f'誕生花 {e["flower"]["flower"].split("（")[0]}', f'七十二候 {e["kou"]}']
    while sum(d.textlength(c, font=f(SANS, 30)) + 56 for c in chips) > 1040 and len(chips) > 1:
        chips.pop()  # 長いときは後ろから省く
    x = 100
    for c in chips:
        w = d.textlength(c, font=f(SANS, 30)) + 40
        d.rounded_rectangle((x, 440, x + w, 492), radius=26, fill="#232A44", outline="#6B76A8", width=2)
        d.text((x + 20, 446), c, font=f(SANS, 30), fill="#E8ECF8")
        x += w + 16
    d.text((100, 525), "人生予報", font=f(SERIF, 34), fill="#C9B27A")
    d.text((262, 533), "uranai.epoch-compass.com", font=f(SANS, 24), fill="#8E97C2")
    return img


def main():
    out = os.path.join(W, "out", "ogp")
    os.makedirs(out, exist_ok=True)
    ks = sys.argv[1:] or sorted(M)
    for k in ks:
        draw(k).save(os.path.join(out, f"birthday-{k}.jpg"), "JPEG", quality=84, optimize=True, progressive=True)
    print(len(ks), "枚 → out/ogp/")


main()
