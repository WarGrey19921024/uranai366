"""タロットの本格スプレッド2ページ（WordPress 固定ページ・/tarot/ の子ページ）
- /tarot/hexagram/ ヘキサグラム（7枚）
- /tarot/celtic/   ケルト十字（10枚）
旧 /number-fortune/tarot/hexagram/・celtic/（静的ページ）から 301 で移す（2026-10-17 本人の決定）。
カードを引く仕組み・78枚の文章・相談の読み取りは build_tarot.py と同じものを使う（data-fix で引き方を固定）。
  python work/scripts/build_tarot_spread.py [更新日]
"""
import datetime as dt, html, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_tarot as BT  # noqa: E402
from build_hub import OUT, WORK, shell  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def esc(s):
    return html.escape(str(s), quote=True)


PAGES = {
    "hexagram": dict(
        url="/tarot/hexagram/", fix="hex", n=7, name="ヘキサグラム", en="HEXAGRAM", sym="✡︎",
        title="ヘキサグラム（7枚引き）タロット占い【無料】相談に答える六芒星スプレッド｜相手の気持ち・対策・結論",
        desc="無料のヘキサグラム（7枚引き）タロット占い。相談を選んで組み立てると、過去・現在・未来に、対策・周りの状況・本心・結論の7枚で答えます。7つの位置の意味と読み方、向いている質問も解説。",
        lead="7枚のカードを六芒星の形に並べて、流れ（過去・現在・未来）に加えて「周りの状況」「あなたの本心」「どうすればいいか」まで読むスプレッドです。人間関係や、続いている悩みの原因を知りたいときに向いています。",
        keys=["PAST", "PRESENT", "FUTURE", "MEASURE", "AROUND", "HEART", "RESULT"],
        know=("ヘキサグラムでわかること",
              ["3枚引き（過去・現在・未来）が「流れ」を見るのに対して、ヘキサグラムは流れに「まわり」と「自分の内側」を足して読みます。",
               "上向きの三角形（過去・現在・未来）が時間の流れ、下向きの三角形（対策・周りの状況・本心）がその流れに影響しているもの、真ん中の1枚が全体の答えです。2つの三角形が重なる形なので、「起きていること」と「その理由」を一度に見比べられます。"]),
        order=["まず真ん中の「結論」を見て、全体の方向をつかみます。",
               "次に上向きの三角形（1 過去 → 2 現在 → 3 未来）で、時間の流れを追います。",
               "下向きの三角形の「周りの状況」と「本心」を見て、流れの理由を考えます。表と裏で食い違っていたら、そこが悩みの核心です。",
               "最後に「対策」のカードで、今日からできることを1つ決めます。"],
        good=["相手の気持ちと、2人の関係のこれから", "職場や友人関係のすれ違いの原因", "長く続いている悩みを、どうほどけばいいか", "迷っていることの結論と、そのための一歩"],
        faq=[("3枚引きとの違いは何ですか。", "3枚引きは過去・現在・未来の流れだけを見ます。ヘキサグラムはそこに「周りの状況」「本心」「対策」と「結論」を加えるので、なぜそうなっているのか、どうすればいいのかまで読めます。"),
             ("相手の気持ちはどのカードで見ますか。", "「周りの状況」のカードが、相手や周りの人の様子を表します。あなた自身の気持ちは「本心」のカードです。2枚を並べて読むと、気持ちのずれが見えてきます。"),
             ("結論が逆位置でした。悪い結果ですか。", "逆位置は「悪い」という意味ではなく、そのカードの力がまだ十分に出ていない状態です。「対策」のカードを手がかりに、やり方や時期を少し変えると流れが変わります。"),
             ("同じ質問で何度も引いてもいいですか。", "引き直すと迷いが増えやすいので、同じ質問は日をあけるのがおすすめです。状況が変わったときや、対策を試したあとにもう一度引くと、変化がわかります。")]),
    "celtic": dict(
        url="/tarot/celtic/", fix="celtic", n=10, name="ケルト十字", en="CELTIC CROSS", sym="☩︎",
        title="ケルト十字（10枚引き）タロット占い【無料】相談に答える本格スプレッド｜現状・障害・未来・結末",
        desc="無料のケルト十字（10枚引き）タロット占い。相談を選んで組み立てると、現状・障害・心の奥・過去・近い未来・周りの環境・願いと不安・結末の10枚で答えます。10の位置の意味と読む順番も解説。",
        lead="10枚で状況をひとつの物語のように読む、タロットでいちばんよく知られた本格スプレッドです。今の状況と壁、心の奥、過去と近い未来、周りの影響、願いと不安、そして結末までを一度に見渡せます。",
        keys=["NOW", "BLOCK", "DEEP", "AWARE", "PAST", "NEAR", "SELF", "ENV", "HOPE", "END"],
        know=("ケルト十字でわかること",
              ["中央の十字（1〜6）は「今この問題がどうなっているか」、右に縦に並ぶ4枚（7〜10）は「あなたと周り、そして行き着く先」を表します。",
               "1枚目の上に横向きに重ねる2枚目は、行く手をふさぐもの。この2枚の組み合わせが、相談の中心になります。時間がかかってもじっくり考えたいこと、いくつもの事情がからんだ悩みに向いています。"]),
        order=["1 現状と、横に重なる 2 障害を一緒に読み、悩みの中心をつかみます。",
               "3 心の奥と 4 意識していることを比べます。ずれがあれば、そこに本当の答えが隠れています。",
               "5 過去 → 1 現状 → 6 近い未来と、時間の流れを追います。",
               "7 あなたの立場と 8 周りの環境で、自分と周りの関係を見ます。",
               "9 願いと不安を確かめてから、10 結末を読みます。結末が気になる形でも、ほかの9枚に流れを変えるヒントがあります。"],
        good=["転職・引っ越し・結婚など、人生の大きな選択", "いくつもの事情がからんで整理できない悩み", "長い付き合いの相手との関係のこれから", "何が本当の壁になっているのかを知りたいとき"],
        faq=[("初心者でも読めますか。", "読めます。このページでは、引いた10枚を位置ごとに説明し、最初に全体の答えを1行で出します。まず答えと「現状」「障害」「結末」の3枚を読み、慣れてきたらほかの位置も見てください。"),
             ("2枚目のカードが横向きなのはなぜですか。", "2枚目は1枚目（現状）に重なって行く手をふさぐもの、という意味なので、十字に交差させて置きます。このページでは、2枚目も上下の向きで正位置・逆位置を決めています。"),
             ("9番目の「願いと不安」はどう読みますか。", "期待していることと恐れていることは、表と裏の関係です。良いカードなら期待、厳しいカードなら不安として読むのが基本ですが、自分の気持ちに近いほうで読んでかまいません。"),
             ("ヘキサグラムとどちらを使えばいいですか。", "相手の気持ちや人間関係を知りたいときはヘキサグラム、事情がいくつもからんだ悩みや人生の大きな選択はケルト十字が向いています。")]),
}


def play_html(parts1, p):
    """/tarot/ の「カードを引いて占う」と同じ部品から、引き方を固定した版を作る"""
    m = re.search(r'<div id="fh-b27-tr" class="fh-b27-tr-felt">.*?<div class="fh-b27-tr-res" id="fh-b27-tr-res" aria-live="polite"></div>', parts1, re.S)
    h = m.group(0)
    h = h.replace('<div id="fh-b27-tr" class="fh-b27-tr-felt">', f'<div id="fh-b27-tr" class="fh-b27-tr-felt" data-fix="{p["fix"]}" data-base="/tarot/">')
    h = re.sub(r'<button type="button" data-pick="want" data-v="(when|choice)">.*?</button>', "", h)
    h = re.sub(r'<div class="fh-b27-tr-ab".*?</div>', "", h, flags=re.S)
    h = re.sub(r'<details class="fh-b27-tr-more">.*?</details>\s*', "", h, flags=re.S)
    h = h.replace("シャッフルして引く", f"シャッフルして{p['n']}枚引く")
    return h + f'\n    <p class="fh-b27-small">相談の言葉から、どのテーマ（片思い・恋人・復縁・相手の気持ち・結婚・仕事・人間関係・お金）かを読み取り、カードの読み方を変えます。「うまくいく？」と聞くと、結論のカードで「はい・いいえ」も答えます。78枚から{p["n"]}枚を選び、上下（正位置・逆位置）も半分ずつの確率で決めます。入力した文は送信も保存もしません。</p>\n  </div>'


def build(key, sample, updated):
    p = PAGES[key]
    parts = open(os.path.join(HERE, "templates", "tarot_parts.html"), encoding="utf-8").read().split("<!--HOW-->")
    cards, minor = BT.load_cards()
    n = [1]

    def h2(t):
        s = f'<h2><span class="fh-b27-n"><span>{BT.ROMAN[n[0]]}</span></span><span>{t}</span></h2>'
        n[0] += 1
        return s
    other = PAGES["celtic" if key == "hexagram" else "hexagram"]
    H = [BT.CSS, '<div class="fh-b27" data-fh-page="tarot">\n<div class="fh-b27-note">']
    a = H.append
    a(f'''<header class="fh-b27-hero">
  <div class="fh-b27-tr-emb" aria-hidden="true"><i></i><i>{p["sym"]}</i><i></i></div>
  <div class="fh-b27-hero-body">
    <span class="fh-b27-tape">TAROT SPREAD</span>
    <h1 class="fh-b27-title"><span class="fh-b27-tr-en">{p["en"]}</span>{p["name"]}<br>{p["n"]}枚引きのタロット占い</h1>
    <p class="fh-b27-lead">{esc(p["lead"])}</p>
  </div>
</header>
<nav class="fh-b27-toc" aria-label="目次"><strong>このページの内容</strong><ol><li><a href="#b27-tr-play">相談してカードを引く</a></li><li><a href="#b27-sp-know">{esc(p["know"][0])}</a></li><li><a href="#b27-sp-pos">{p["n"]}の位置と意味</a></li><li><a href="#b27-sp-order">読む順番</a></li><li><a href="#b27-sp-good">向いている相談</a></li><li><a href="#b27-sp-faq">よくある質問</a></li></ol></nav>''')
    a(f'<section class="fh-b27-sec" id="b27-tr-play">\n  {h2("相談してカードを引く")}\n  {play_html(parts[1], p)}\n</section>')
    a(BT.script(cards, minor))
    a("<!--Ads1-->")
    a(f'<section class="fh-b27-sec" id="b27-sp-know">\n  {h2(esc(p["know"][0]))}\n' + "".join(f"  <p>{esc(x)}</p>\n" for x in p["know"][1]) + "</section>")
    rows = "".join(f'<tr><th scope="row">{i}</th><td><b>{esc(BT.PD_NAME[k])}</b></td><td>{esc(BT.PD[k])}</td></tr>' for i, k in enumerate(p["keys"], 1))
    a(f'''<section class="fh-b27-sec" id="b27-sp-pos">
  {h2(f"{p['n']}の位置と意味")}
  <p>位置の名前や順番は、本や流派によって少しずつ違います。このページでは次の{p["n"]}つで読みます。</p>
  <table class="fh-b27-tr-t"><thead><tr><th scope="col">位置</th><th scope="col">名前</th><th scope="col">見るもの</th></tr></thead><tbody>{rows}</tbody></table>
</section>''')
    a(f'<section class="fh-b27-sec" id="b27-sp-order">\n  {h2("読む順番")}\n  <ol class="fh-b27-tr-steps">' + "".join(f"<li>{esc(x)}</li>" for x in p["order"]) + "</ol>\n</section>")
    a(f'<section class="fh-b27-sec" id="b27-sp-good">\n  {h2("向いている相談")}\n  <ul class="fh-b27-tr-steps">' + "".join(f"<li>{esc(x)}</li>" for x in p["good"]) +
      '</ul>\n  <p>短い問いや今日の過ごし方なら、<a href="/tarot/">1枚引き・3枚引き・Yes/No</a>のほうが答えがはっきりします。</p>\n</section>')
    qa = "".join(f'<details{" open" if i == 0 else ""}><summary>Q. {esc(q)}</summary><p>A. {esc(x)}</p></details>' for i, (q, x) in enumerate(p["faq"]))
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in p["faq"]]}
    a(f'<section class="fh-b27-sec" id="b27-sp-faq">\n  {h2("よくある質問")}\n  <div class="fh-b27-tr-qa">{qa}</div>\n</section>\n'
      f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>')
    a(f'''<section class="fh-b27-sec" id="b27-sp-more">
  <div class="fh-b27-links">
    <a href="/tarot/"><b>タロット占い（1枚・3枚・Yes/No）→</b><small>78枚すべての意味の一覧もこちら</small></a>
    <a href="{other["url"]}"><b>{other["name"]}（{other["n"]}枚）→</b><small>{esc(other["lead"][:38])}…</small></a>
    <a href="/366uranai/"><b>366日の誕生日占い →</b><small>誕生日から性格・相性・2027年の運勢</small></a>
  </div>
</section>''')
    up = dt.date.fromisoformat(updated)
    a(f'<p class="fh-b27-foot">タロット占いは、自分の気持ちや状況を見つめ直すための読み物です。楽しみと気づきのためにお使いください。カードの意味はこのサイトで書き下ろしたものです。<br>'
      f'最終更新日：{up.year}年{up.month}月{up.day}日／<a href="/about/">この記事の作成方針について</a></p>')
    a("</div>\n</div>")
    out = shell(p["title"], p["desc"], p["url"], "\n".join(H), sample)
    assert "！" not in out
    return out


def main():
    updated = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    for key in PAGES:
        for sample, path in ((False, os.path.join(OUT, f"tarot_{key}.html")), (True, os.path.join(OUT, "sample", f"tarot_{key}.html"))):
            with open(path, "w", encoding="utf-8") as fp:
                fp.write(build(key, sample, updated))
            print("→", os.path.relpath(path, WORK))


if __name__ == "__main__":
    main()
