"""/omikuji/（WordPress ページ 4194・既存の手作りページ）に入れる広告の部品を作る。2026-10-17 本人「おみくじから」。
既存ページの中身は書き換えない方針で、次の3か所だけを差し替える（差し替えはブラウザから REST で行う）：
1. 結果の画面の商品カード（もともと link: '#' の仮置き）→ 楽天の実際の商品（写真・値段・もしもリンク）
2. 結果の画面の「今すぐ無料相談」ボタン（もともと href="#"）→ A8 電話占いセラ
3. おみくじの箱のすぐ下に、引く前から見える小さな商品ボックス（3つ）
出力：out/omikuji_ads.json"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import goods_media as GM
import aff_extra as AX

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out", "omikuji_ads.json")

CATS = {
    "good": dict(title="✨ この運気を活かすお守りアイテム", desc="いい流れのうちに、行動を後押しするものを手もとに。",
                 items=[("御朱印帳", "御朱印帳", "運のいい日は神社めぐりへ。お参りの記録が残ります。"),
                        ("手帳 2027", "2027年の手帳", "いい運気のうちに、来年の予定と目標を書き出して。"),
                        ("ルチルクォーツ ブレスレット", "ルチルクォーツのブレスレット", "金色の針が入った、仕事運・金運のお守りの石。")]),
    "normal": dict(title="🍀 運気を少し上向きにするアイテム", desc="毎日を整える小さなお守りを。",
                   items=[("小さな鈴のお守り", "鈴のお守り", "澄んだ鈴の音は、昔から魔よけとされてきました。"),
                          ("お香", "お香", "香りで気持ちを切りかえて、落ち着いて過ごせるように。"),
                          ("お守り袋", "お守り袋", "引いたおみくじを入れて持ち歩くのにもちょうどいい大きさ。")]),
    "bad": dict(title="🌟 運気を立て直す厄よけアイテム", desc="悪い結果が出たときこそ、気持ちを切りかえるきっかけに。",
                items=[("勾玉のお守り", "勾玉のお守り", "厄よけの縁起物。お財布に入れておける小ささです。"),
                       ("水晶 天然石", "浄化用の水晶さざれ", "部屋に置いたり、ほかの石の浄化に使ったり。"),
                       ("オニキス ブレスレット", "オニキスのブレスレット", "黒い石は、悪い流れを断ち切るお守りとされます。")]),
}
STATIC = [("御朱印帳", "御朱印帳", "おみくじを引きに神社へ行くなら、お参りの記録に。"),
          ("神社のお守り袋", "お守り袋", "引いたおみくじを入れて、持ち歩くのにちょうどいい大きさ。"),
          ("小さな鈴のキーホルダー", "鈴のお守り", "澄んだ鈴の音は、昔から魔よけとされてきました。")]


def card(q, name, why):
    it = GM.item("rakuten", q)
    h = AX.href("rakuten", q)
    if not (it and it.get("img") and h):
        raise SystemExit(f"商品が無い: {q}")
    at = it["at"]
    return dict(name=name, description=why, img=it["img"], link=h, type="rakuten",
                price=f'楽天 {int(it["price"]):,}円（{int(at[5:7])}月{int(at[8:10])}日時点）',
                imp=AX.tpl()["rakuten"]["impression"])


def main():
    out = {"categories": {}, "phone": {"href": AX.href("phone"), "imp": AX.tpl()["phone"]["impression"]}}
    for k, c in CATS.items():
        out["categories"][k] = dict(title=c["title"], description=c["desc"], products=[card(*x) for x in c["items"]])
    box = AX.goods_box("おみくじと一緒に持ちたい開運アイテム", [x + ("omamori",) for x in STATIC],
                       lead="神社でおみくじを引くときや、引いたあとに。楽天・Yahoo!ショッピングの商品ページへ移ります。")
    out["static_html"] = '<!-- om-ad:start 2026-10-17 -->\n<div class="fh-b27 om-ad">' + AX.CSS + OM_CSS + box + '</div>\n<!-- om-ad:end -->'
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("ok", OUT)


# fh-b27.css を読まないページなので、商品ボックスに必要な最低限の見た目をここで足す
OM_CSS = ("<style>.om-ad{max-width:880px;margin:24px auto;padding:0 16px;box-sizing:border-box;font-family:'Noto Sans JP',sans-serif;color:#2E2A26}"
          ".om-ad *{box-sizing:border-box}.om-ad .fh-b27-adgoods{background:#FFFDF6;border:1px solid #E8DCC0;border-radius:14px;padding:16px}"
          ".om-ad .fh-b27-adgoods-h{display:flex;justify-content:space-between;align-items:center;margin:0 0 6px;font-weight:700;font-size:16px}"
          ".om-ad .fh-b27-pr{font-size:11px;border:1px solid #B9A77A;border-radius:3px;padding:0 5px;color:#7A6E5C;font-weight:400}"
          ".om-ad .fh-b27-adgoods-l{font-size:13px;color:#5E5546;margin:0 0 10px}"
          ".om-ad .fh-b27-shops{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}"
          ".om-ad .fh-b27-shop{display:flex;flex-direction:column;gap:6px;background:#fff;border:1px solid #EEE4CF;border-radius:12px;padding:10px}"
          ".om-ad .fh-b27-shop-pic{width:100%;aspect-ratio:1/1;background:#fff;border-radius:10px;overflow:hidden}"
          ".om-ad .fh-b27-shop-pic a{display:block;width:100%;height:100%}.om-ad img.fh-b27-shop-img{width:100%;height:100%;object-fit:contain;margin:0}"
          ".om-ad .fh-b27-shop-body{display:flex;flex-direction:column;gap:2px}.om-ad .fh-b27-shop-body small{font-size:11px;color:#8A4B12;font-weight:700}"
          ".om-ad .fh-b27-shop-name{font-size:15px}.om-ad .fh-b27-shop-why{font-size:12.5px;line-height:1.6;color:#4A3F30}"
          ".om-ad .fh-b27-shop-prod{display:none}.om-ad .fh-b27-shop-price{font-size:12px;color:#4A3F30}.om-ad .fh-b27-shop-price b{color:#B3261E;font-size:15px;margin:0 2px}"
          ".om-ad .fh-b27-shop-price small{font-size:10.5px;color:#7A6E5C}"
          ".om-ad .fh-b27-shop-btns{display:flex;gap:6px;margin-top:auto}.om-ad a.fh-b27-shopbtn{flex:1 1 0;display:flex;align-items:center;justify-content:center;min-height:40px;border-radius:8px;color:#fff;font-weight:700;font-size:13px;text-decoration:none}"
          ".om-ad .fh-b27-shop-rakuten{background:#BF0000}.om-ad .fh-b27-shop-yahoo{background:#E2195B}.om-ad .fh-b27-shopbtn img{display:none}"
          "@media(max-width:600px){.om-ad .fh-b27-shops{grid-template-columns:minmax(0,1fr)}.om-ad .fh-b27-shop{flex-direction:row;flex-wrap:wrap}.om-ad .fh-b27-shop-pic{width:96px;height:96px;flex:0 0 96px}.om-ad .fh-b27-shop-body{flex:1 1 0;min-width:0}.om-ad .fh-b27-shop-btns{flex-basis:100%}}</style>")

if __name__ == "__main__":
    main()
