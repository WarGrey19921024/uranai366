"""姉妹サイトの共有画像（OGP 1200x630）。背景（Gemini・文字なし）に、サイト名と説明を重ねる（2026-10-25）。
文字色：濃い背景には明るい文字、淡い背景には濃い文字（本人の絶対ルール）。"""
import sys, json
from PIL import Image, ImageDraw, ImageFont
SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
SANS = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
SITES = {
 "dream": dict(name="夢解き図鑑", sub="夢の意味を、やさしく辞典風に", fg=(240, 236, 224), sub_fg=(196, 210, 200), acc=(214, 190, 120)),
 "kokoro": dict(name="心コンパス", sub="性格を、いくつかの軸で重ねて読む", fg=(234, 246, 255), sub_fg=(147, 182, 203), acc=(111, 211, 255)),
 "enmusubi": dict(name="縁結び診断室", sub="相性・ご縁・縁日の読みもの", fg=(246, 238, 231), sub_fg=(198, 174, 176), acc=(217, 169, 76)),
 "kaiun": dict(name="開運ライフ", sub="風水・暦・暮らしの開運", fg=(21, 37, 64), sub_fg=(90, 80, 64), acc=(178, 58, 72)),
}
def make(site, src, out):
    c = SITES[site]
    im = Image.open(src).convert("RGB")
    W, H = 1200, 630
    r = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    l = (im.width - W) // 2; t = (im.height - H) // 2
    im = im.crop((l, t, l + W, t + H))
    d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype(SERIF, 92, index=0); f2 = ImageFont.truetype(SANS, 34, index=0); f3 = ImageFont.truetype(SANS, 26, index=0)
    x = 84
    d.rectangle([x, 214, x + 56, 218], fill=c["acc"])
    d.text((x, 240), c["name"], font=f1, fill=c["fg"])
    d.text((x, 372), c["sub"], font=f2, fill=c["sub_fg"])
    d.text((x, 540), "人生予報  uranai.epoch-compass.com", font=f3, fill=c["sub_fg"])
    im.save(out, "JPEG", quality=88, optimize=True)
if __name__ == "__main__":
    make(sys.argv[1], sys.argv[2], sys.argv[3])
