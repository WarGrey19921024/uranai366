"""/star/（星座占いの一覧・ページ 2745・既存の手作りページ）に入れる「2027年の12星座ランキング」のかたまり。2026-10-18 本人「そこから行こう」。
数字は data/signs_2027.json（calc_signs_2027.py）。12星座ページと同じ点。年間の順位は12か月の総合の点の平均。
出力：out/star_ranking.html（<!-- st27:start --> 〜 <!-- st27:end -->）"""
import json, os, statistics as st, html
HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.join(HERE, "..")
from build_signs import EN, JA, GLYPH, ELEM, EC

S = json.load(open(os.path.join(W, "data", "signs_2027.json"), encoding="utf-8"))


def main():
    rows = []
    for sg, en in EN.items():
        M = S["signs"][sg]["months"]
        avg = st.mean(M[str(m)]["総合"] for m in range(1, 13))
        best = max(range(1, 13), key=lambda m: M[str(m)]["総合"])
        love = max(range(1, 13), key=lambda m: M[str(m)]["恋愛"])
        firsts = sum(1 for m in range(1, 13) if S["rank"][str(m)][0] == sg)
        rows.append((avg, sg, en, best, love, firsts))
    rows.sort(key=lambda r: -r[0])
    cards = []
    for i, (avg, sg, en, best, love, firsts) in enumerate(rows):
        c = EC[ELEM[en]]
        cards.append(f'<a class="st27-c" href="/{en}/" style="--c:{c}"><span class="r">{i + 1}<small>位</small></span><span class="g" aria-hidden="true">{GLYPH[en]}&#xFE0E;</span>'
                     f'<span class="b"><b>{JA[en]}</b><small>平均 {avg:.0f}点・いちばんいい月 {best}月・恋愛の山 {love}月' + (f'・1位の月 {firsts}回' if firsts else '') + '</small></span><span class="go">2027年の運勢 →</span></a>')
    hd = "".join(f"<th>{m}月</th>" for m in range(1, 13))
    tr = []
    for r in range(3):
        tds = "".join(f'<td><a href="/{EN[S["rank"][str(m)][r]]}/">{JA[EN[S["rank"][str(m)][r]]][:-1]}</a></td>' for m in range(1, 13))
        tr.append(f"<tr><th>{r + 1}位</th>{tds}</tr>")
    css = """<style>
.st27{max-width:960px;margin:32px auto;padding:22px 18px;border-radius:16px;background:linear-gradient(160deg,#1B2140,#141832);color:#EEF0F7;box-shadow:0 10px 30px rgba(0,0,0,.35);font-family:'Noto Sans JP',sans-serif;box-sizing:border-box}
.st27 *{box-sizing:border-box}.st27 h2{font-size:24px;margin:0 0 6px;color:#F5CF6E;text-align:center}.st27 p{font-size:14.5px;line-height:1.85;color:#D6DAEA;margin:6px 0 14px}
.st27-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.st27 a.st27-c{display:grid;grid-template-columns:48px 44px minmax(0,1fr);grid-template-rows:auto auto;column-gap:10px;align-items:center;padding:10px 12px;border-radius:12px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.12);border-left:6px solid var(--c);text-decoration:none;color:#EEF0F7}
.st27 a.st27-c:hover{background:rgba(255,255,255,.1)}
.st27-c .r{grid-row:1/3;font:800 26px sans-serif;color:#F5CF6E;text-align:center}.st27-c .r small{font-size:12px;margin-left:1px}
.st27-c .g{grid-row:1/3;width:44px;height:44px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:var(--c);color:#10142A;font-size:24px}
.st27-c .b b{display:block;font-size:16.5px;color:#fff}.st27-c .b small{display:block;font-size:12px;color:#C9CDE0;line-height:1.5}
.st27-c .go{grid-column:3;font-size:12px;color:#F5CF6E;font-weight:700}
.st27-t{overflow-x:auto;margin-top:16px}.st27-t table{border-collapse:collapse;min-width:640px;width:100%;font-size:12.5px;text-align:center}
.st27-t th,.st27-t td{border-bottom:1px solid rgba(255,255,255,.12);padding:6px 3px;color:#D6DAEA;background:transparent}
.st27-t thead th{color:#F5CF6E}.st27-t td a{color:#EEF0F7;text-decoration:none;font-weight:700}
.st27 .st27-n{font-size:12px;color:#ADB3CC}
@media(max-width:640px){.st27-list{grid-template-columns:minmax(0,1fr)}.st27 h2{font-size:20px}}
</style>"""
    block = f"""<!-- st27:start 2026-10-18 -->
{css}<section class="st27" id="st27-rank">
<h2>2027年の12星座ランキング</h2>
<p>天体が各星座から数えて何番目の部屋（ハウス）を通るかで、2027年の追い風の強さを月ごとに計算し、1年の平均で並べました。星座名を押すと、月ごとの運勢グラフ・ラッキーデーのカレンダー・恋愛や仕事の流れが見られます。</p>
<div class="st27-list">{"".join(cards)}</div>
<div class="st27-t"><table><caption class="st27-n" style="text-align:left;padding-bottom:4px">月ごとの上位3星座（総合）</caption><thead><tr><th></th>{hd}</tr></thead><tbody>{"".join(tr)}</tbody></table></div>
<p class="st27-n">点は毎日12時（日本時間）の太陽・水星・金星・火星・木星・土星の位置から、このサイトで計算したものです。同じ星座でも誕生日によって運勢はちがうので、くわしくは<a href="/366uranai/" style="color:#F5CF6E">366日の誕生日占い</a>で。</p>
</section>
<!-- st27:end -->"""
    open(os.path.join(W, "out", "star_ranking.html"), "w", encoding="utf-8").write(block)
    for r in rows:
        print(f"{r[1]} {r[0]:.1f} best{r[3]}")


if __name__ == "__main__":
    main()
