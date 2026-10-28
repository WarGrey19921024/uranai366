"""誕生日相性占い（/compatibility/）に足す、検索向けの固定の解説（2026-10-15 本人の決定「課題4」）。
build_compatibility.py から呼ぶ。計算に頼らず読める文章と表（検索エンジンにも読める）。
- 12星座×12星座の相性早見表（星座どうしの角度＝366日の相性と同じ考え方の大まかな目安）
- 星座別・相性がいい星座
- 関係の型（6つ）の説明
- 誕生日の数のグループの組み合わせ
- 誕生日から相性の良い日を探す（366日のページへのリンク）
- よくある質問（FAQPage の構造化データつき）
"""
import json
import os

COMPAT = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'compat_366.json'), encoding='utf-8'))

SIGNS = ["牡羊座", "牡牛座", "双子座", "蟹座", "獅子座", "乙女座", "天秤座", "蠍座", "射手座", "山羊座", "水瓶座", "魚座"]
ELEM = ["火", "地", "風", "水"] * 3
PERIOD = ["3/21〜4/19", "4/20〜5/20", "5/21〜6/21", "6/22〜7/22", "7/23〜8/22", "8/23〜9/22", "9/23〜10/23",
          "10/24〜11/22", "11/23〜12/21", "12/22〜1/19", "1/20〜2/18", "2/19〜3/20"]
# 星座どうしの距離（0〜6）→ 関係の型・印
REL = {0: ("似た者どうし", "○", "r0"), 1: ("おだやか", "◇", "r1"), 2: ("協力", "○", "r2"), 3: ("刺激し合う", "▽", "r3"),
       4: ("調和", "◎", "r4"), 5: ("おだやか", "◇", "r1"), 6: ("向かい合う", "△", "r6")}
TYPES = [
    ("調和", "◎", "r4", "120度前後",
     "同じエレメント（火・地・風・水）の星座どうしで、考え方の土台や大切にするものが近い組み合わせです。説明しなくても通じ合える場面が多く、出会ってすぐに打ち解けやすいでしょう。居心地がよいぶん、お互いに甘えて同じところで立ち止まりやすいので、ときどき新しい場所や目標を2人で選ぶと関係が育ちます。"),
    ("協力", "○", "r2", "60度前後",
     "火と風、地と水のように、性質が違っても力を貸し合える星座どうしです。片方が持っていないものを、もう片方が自然に補ってくれる関係で、一緒に何かを作ったり進めたりするときに相性のよさが出ます。役割を言葉で分けておくと、それぞれの得意がさらに生きます。"),
    ("似た者どうし", "○", "r0", "0度前後",
     "同じ星座、または太陽の位置が近い2人です。感じ方やペースが似ているので、気をつかわずに一緒にいられます。一方で、苦手なことや弱点まで似やすいため、同じところでつまずくことも。2人とも苦手な家事や手続きは、早めに分担を決めておくと安心です。"),
    ("おだやか", "◇", "r1", "角度の決まりに当たらない",
     "強く引き合うことも、ぶつかることも少ない、穏やかな関係です。最初の印象は控えめでも、時間をかけて少しずつ信頼が積み上がっていく組み合わせです。相手の考えを知る機会を自分からつくると、思っていた以上に話が合うことに気づくかもしれません。"),
    ("向かい合う", "△", "r6", "180度前後",
     "星座の輪の正反対にいる2人で、自分にないものを相手が持っているため、強く惹かれ合いやすい組み合わせです。見ている方向が逆なぶん、意見が分かれやすい面もあります。相手のやり方を「反対」ではなく「もう半分」と受け取れると、補い合える心強いペアになります。"),
    ("刺激し合う", "▽", "r3", "90度前後",
     "ペースや大事にするものが違い、ぶつかりやすい角度です。ただ、そのぶん相手から受ける刺激が大きく、一緒にいると成長しやすい組み合わせでもあります。決めごとは急がず、お互いの理由を最後まで聞いてから選ぶと、摩擦が前に進む力に変わります。"),
]
SCENES = [  # 関係の型 × 恋愛・友人・仕事（2026-10-15 検索で「恋愛」「友達」を含む言葉が多いため追加）
    ("調和", "◎", "r4",
     "好きなものや生活のリズムが近く、付き合い始めから自然体でいられます。マンネリを防ぐには、年に一度は2人とも初めての場所へ。",
     "何年会わなくても、会えばすぐ昔の空気に戻れる友人になりやすい2人。誘うのはどちらからでも気負いがありません。",
     "説明が少なくても意図が伝わるので、段取りが早く進みます。似た発想に偏らないよう、外の意見を一度はさむと安心です。"),
    ("協力", "○", "r2",
     "相手の足りないところを、責めずに埋められる関係。記念日の準備や旅行の計画など、2人で役割を分けると距離が縮まります。",
     "困ったときに頼りやすく、頼まれても負担に感じにくい間柄。得意分野を教え合うと、付き合いがさらに長く続きます。",
     "企画する人と仕上げる人のように、役割が自然に分かれるペア。担当をはっきり決めると、お互いの力がいちばん生きます。"),
    ("似た者どうし", "○", "r0",
     "感覚が近いぶん、一緒にいて疲れにくいカップル。2人とも同じ場面で迷いやすいので、決める係を交代制にしておくと楽です。",
     "趣味や笑いのツボが合い、気づけば一緒にいる友人に。同じことで落ち込みやすいので、励まし役を順番に引き受けましょう。",
     "仕事の進め方が似ていて、引き継ぎがスムーズな相手。苦手な作業がかぶりやすいので、早めに外の人の手を借りる準備を。"),
    ("おだやか", "◇", "r1",
     "派手な盛り上がりは少なくても、けんかの少ない落ち着いた恋になりやすい2人。気持ちは言葉にして伝えるほど深まります。",
     "ほどよい距離感で、相手の領域に踏み込みすぎない友人関係。たまに長く話す時間をつくると、意外な共通点が見つかります。",
     "感情的なぶつかり合いが起きにくく、淡々と仕事を進められる相手。考えを共有する場を意識してつくると連携が強まります。"),
    ("向かい合う", "△", "r6",
     "自分にない魅力に強く惹かれる、ドラマのある恋になりやすい組み合わせ。意見が割れたら、まず相手の言い分を最後まで聞いて。",
     "見ている世界が違うので、話すたびに新しい発見がある友人。どちらかに合わせ続けず、交互に相手の好きな場所へ行くと長続きします。",
     "反対側から物事を見られるため、計画の穴に気づきやすいペア。対立ではなく点検役と割り切ると、心強い仕事相手になります。"),
    ("刺激し合う", "▽", "r3",
     "ペースの違いから小さな衝突が起きやすい一方、相手のおかげで視野が広がる恋。話し合いは疲れていない時間帯を選んで。",
     "考え方の違いを面白がれると、刺激をくれる大切な友人に。合わないところは無理にそろえず、会う頻度で調整するのも手です。",
     "締め切りや手順の感覚が違いやすい相手。最初にゴールと期限を紙に書いて共有しておくと、摩擦が前に進む力に変わります。"),
]
NUMG = [("行動派", "1・5・7", "自分で道を切り開く"), ("堅実派", "2・4・8", "足元を固める"), ("表現派", "3・6・9", "気持ちを伝える")]
NUM_PAIR = {
    ("行動派", "行動派"): "決めるのも動くのも早い2人。勢いが合う反面、休むタイミングも一緒に決めておくと長続きします。",
    ("堅実派", "堅実派"): "約束や段取りを大切にする2人。安心感は抜群なので、ときどき新しいことを1つ足すと関係に彩りが出ます。",
    ("表現派", "表現派"): "気持ちを言葉や形にするのが得意な2人。会話がはずみやすく、楽しい時間を自然に増やしていけます。",
    ("行動派", "堅実派"): "急ぎたい人と確かめたい人の組み合わせで、歩く速さが違いやすいペア。先に締め切りと手順を決めると噛み合います。",
    ("行動派", "表現派"): "動く人と盛り上げる人の組み合わせ。思いつきを形にしやすく、2人で始めたことが周りを巻き込んでいきます。",
    ("堅実派", "表現派"): "支える人と伝える人の組み合わせ。表現派の思いを堅実派が形にしやすく、役割が自然に分かれます。",
}
FAQ = [
    ("誕生日だけで相性はわかりますか。",
     "このページでは、2人の誕生日の太陽の位置がつくる角度と、誕生日の数のグループから、関係の型と5段階の目安を出します。月と日だけで占え、生まれた年を入れると九星気学の相性も加わります。"),
    ("星座の相性と、誕生日の相性はどう違いますか。",
     "星座の相性は12星座どうしの大まかな傾向です。誕生日の相性は、同じ星座の中でも生まれた日によって変わる太陽の位置まで見るので、星座の境目に近い人ほど結果が変わることがあります。"),
    ("相性がいちばんいいのはどの組み合わせですか。",
     "太陽の位置が120度前後の「調和」で、さらに誕生日の数のグループが同じ組み合わせが、いちばん点が高くなります。各誕生日のページの「相性の良い誕生日」に、その日と特に相性のよい5つの誕生日を載せています。"),
    ("相性が「刺激し合う」だと、うまくいきませんか。",
     "うまくいかないという意味ではありません。違いが大きいぶんぶつかりやすい一方で、お互いを成長させやすい組み合わせです。結果の「うまくいくコツ」を参考に、話し合いの時間を多めにとってみてください。"),
    ("恋愛の相性も、友達や職場の相性も占えますか。",
     "占えます。恋人や好きな人はもちろん、友人、職場の人、家族など、どんな相手でも2人の誕生日を選ぶだけで、関係の型とうまくいくコツを表示します。このページの「恋愛・友達・仕事での相性」では、関係の型ごとの付き合い方も紹介しています。"),
    ("同じ誕生日の2人の相性はどうなりますか。",
     "同じ誕生日どうしは太陽の位置が重なるので「似た者どうし」になり、誕生日の数も同じため、このページの決め方では最も高い◎になります。考え方や感じ方が近いぶん、苦手なことまで似やすい点にだけ気をつけてください。"),
    ("誕生日が1日違いだと相性はどうですか。",
     "1日違いでは太陽の位置が約1度しか離れないため「似た者どうし」になります。ただし誕生日の数は別のグループになることがほとんどなので、目安は◎ではなく○です。誕生日が前後1週間ほど離れていても、多くは同じ「似た者どうし」になります。"),
    ("自分と相性のいい誕生日の一覧はありますか。",
     "あります。このページの「誕生日別・相性のいい誕生日一覧」で、366日それぞれと特に相性のよい誕生日を月ごとにまとめています。くわしい理由は、各誕生日のページの「相性の良い誕生日」で読めます。"),
    ("入力した生年月日は保存されますか。",
     "送信も保存もしません。計算はこのページの中だけで行います。"),
]


def dist(i, j):
    d = abs(i - j) % 12
    return min(d, 12 - d)


def mmdd_url(m, d):
    return f"/366uranai/{m:02d}-{d:02d}/"


def css():
    return """<style id="fh-b27-cpx-css">
.fh-b27-cpx-wrap{overflow-x:auto;border:1.5px dashed var(--line);border-radius:8px;background:var(--deep)}
.fh-b27-cpx-t{border-collapse:collapse;min-width:680px;width:100%;font-size:13px;line-height:1.4}
.fh-b27-cpx-t caption{position:absolute;left:-9999px}
.fh-b27-cpx-t th,.fh-b27-cpx-t td{border:1px solid var(--line);padding:5px 2px;text-align:center}
.fh-b27-cpx-t thead th{font-size:11.5px;color:var(--sub);background:var(--paper)}
.fh-b27-cpx-t th.c0{position:sticky;left:0;z-index:1;background:var(--paper);text-align:left;padding:4px 8px;white-space:nowrap;font-size:13px}
.fh-b27-cpx-t td{font-size:15px;font-weight:700}
.fh-b27-cpx-t td.r4{background:#2F5848}.fh-b27-cpx-t td.r2{background:#2C4A57}.fh-b27-cpx-t td.r0{background:#3B4A6B}
.fh-b27-cpx-t td.r1{background:transparent;color:var(--sub)}.fh-b27-cpx-t td.r6{background:#5A4630}.fh-b27-cpx-t td.r3{background:#5C3838}
.fh-b27-cpx-key{display:flex;flex-wrap:wrap;gap:6px;font-size:13px}
.fh-b27-cpx-key span{border:1px solid var(--line);border-radius:999px;padding:1px 10px}
.fh-b27-cpx-key .r4{background:#2F5848}.fh-b27-cpx-key .r2{background:#2C4A57}.fh-b27-cpx-key .r0{background:#3B4A6B}.fh-b27-cpx-key .r6{background:#5A4630}.fh-b27-cpx-key .r3{background:#5C3838}
.fh-b27-cpx-types{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.fh-b27-cpx-types div{border:1.5px dashed var(--line);border-radius:10px;padding:12px 14px;background:var(--deep)}
.fh-b27-cpx-types h3{font-family:'Klee One',cursive;font-size:18px;display:flex;align-items:center;gap:8px;margin-bottom:4px}
.fh-b27-cpx-types h3 b{display:inline-flex;width:30px;height:30px;border-radius:50%;align-items:center;justify-content:center;font-size:16px}
.fh-b27-cpx-types small{color:var(--mute);font-size:12px}
.fh-b27-cpx-types p{font-size:14.5px;line-height:1.85}
.fh-b27-cpx-best{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;list-style:none;margin:0;padding:0}
.fh-b27-cpx-best li{border-bottom:1px dashed var(--line);padding:6px 2px;font-size:14px;line-height:1.7}
.fh-b27-cpx-best b{color:var(--gold)}
.fh-b27-cpx-num{width:100%;border-collapse:collapse;font-size:14px;line-height:1.7}
.fh-b27-cpx-num th,.fh-b27-cpx-num td{border-bottom:1px dashed var(--line);padding:8px 6px;text-align:left;vertical-align:top}
.fh-b27-cpx-num th{white-space:nowrap;color:var(--gold);font-weight:700}
.fh-b27-cpx-cal{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
.fh-b27-cpx-cal details{border:1.5px dashed var(--line);border-radius:8px;background:var(--deep);padding:6px 10px}
.fh-b27-cpx-cal summary{cursor:pointer;font-family:'Klee One',cursive;font-size:16px;color:var(--gold)}
.fh-b27-cpx-cal p{display:flex;flex-wrap:wrap;gap:4px 8px;font-size:13px;margin-top:6px}
.fh-b27-cpx-sc{border-collapse:collapse;min-width:640px;width:100%;font-size:13.5px;line-height:1.75}
.fh-b27-cpx-sc caption{position:absolute;left:-9999px}
.fh-b27-cpx-sc th,.fh-b27-cpx-sc td{border-bottom:1px dashed var(--line);padding:10px 8px;text-align:left;vertical-align:top}
.fh-b27-cpx-sc thead th{color:var(--gold);font-size:13px;background:var(--paper)}
.fh-b27-cpx-sc tbody th{white-space:nowrap;font-weight:700}
.fh-b27-cpx-sc tbody th b{display:inline-flex;width:24px;height:24px;border-radius:50%;align-items:center;justify-content:center;margin-right:6px;font-size:13px}
.fh-b27-cpx-sc b.r4{background:#2F5848}.fh-b27-cpx-sc b.r2{background:#2C4A57}.fh-b27-cpx-sc b.r0{background:#3B4A6B}.fh-b27-cpx-sc b.r6{background:#5A4630}.fh-b27-cpx-sc b.r3{background:#5C3838}.fh-b27-cpx-sc b.r1{border:1px solid var(--line)}
.fh-b27-cpx-list{display:flex;flex-direction:column;gap:8px}
.fh-b27-cpx-list details{border:1.5px dashed var(--line);border-radius:8px;background:var(--deep);padding:6px 12px}
.fh-b27-cpx-list summary{cursor:pointer;font-family:'Klee One',cursive;font-size:16px;color:var(--gold)}
.fh-b27 .fh-b27-cpx-list ul{list-style:none;margin:6px 0 4px;padding:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 18px}
.fh-b27 .fh-b27-cpx-list li{display:flex;gap:10px;font-size:13.5px;line-height:1.7;padding:3px 0;border-bottom:1px dotted var(--line);margin:0}
.fh-b27-cpx-list li::before{content:none}
.fh-b27-cpx-list li a{flex:0 0 4.6em;font-weight:700}
.fh-b27-cpx-list li span{color:var(--sub)}
.fh-b27-cpx-qa details{border-bottom:1px dashed var(--line);padding:8px 2px}
.fh-b27-cpx-qa summary{cursor:pointer;font-weight:700}
.fh-b27-cpx-qa p{margin-top:6px;font-size:14.5px}
@media (max-width:640px){.fh-b27 .fh-b27-cpx-list ul{grid-template-columns:1fr}.fh-b27-cpx-types,.fh-b27-cpx-best{grid-template-columns:1fr}.fh-b27-cpx-cal{grid-template-columns:repeat(2,minmax(0,1fr))}}
</style>"""


def sections(start_no):
    n = start_no
    out = [css()]
    sym = {t[0]: t for t in TYPES}
    # 1) 12星座×12星座
    head = '<tr><th scope="col" class="c0">星座</th>' + "".join(f'<th scope="col">{s.replace("座", "")}</th>' for s in SIGNS) + "</tr>"
    rows = ""
    for i, a in enumerate(SIGNS):
        rows += f'<tr><th scope="row" class="c0">{a}</th>'
        for j, b in enumerate(SIGNS):
            name, mk, cls = REL[dist(i, j)]
            rows += f'<td class="{cls}" title="{a}と{b}：{name}">{mk}</td>'
        rows += "</tr>"
    key = "".join(f'<span class="{t[2]}">{t[1]} {t[0]}</span>' for t in TYPES)
    out.append(f'''<section class="fh-b27-sec" id="b27-cp-signs">
  <h2><span class="fh-b27-n">{n}</span>星座どうしの相性早見表</h2>
  <p>12星座どうしの相性を、星座の輪の上での位置関係（角度）から一覧にしました。366日の誕生日占いと同じ考え方で、印は「関係の型」を表します。実際の相性は、同じ星座でも生まれた日の太陽の位置で変わるので、くわしくは上の診断で2人の誕生日を選んでください。</p>
  <p class="fh-b27-cpx-key">{key}</p>
  <div class="fh-b27-cpx-wrap" tabindex="0" role="region" aria-label="星座どうしの相性早見表（横にスクロールできます）"><table class="fh-b27-cpx-t"><caption>12星座どうしの相性早見表（行と列の星座の関係の型）</caption><thead>{head}</thead><tbody>{rows}</tbody></table></div>
</section>''')
    n += 1
    # 2) 星座別・相性がいい星座
    lis = ""
    for i, a in enumerate(SIGNS):
        tri = [SIGNS[(i + 4) % 12], SIGNS[(i + 8) % 12]]
        sex = [SIGNS[(i + 2) % 12], SIGNS[(i + 10) % 12]]
        opp = SIGNS[(i + 6) % 12]
        EL = {"火": "fire", "地": "earth", "風": "air", "水": "water"}
        chip = lambda xs: "".join(f'<span class="fh-b27-cpx-chip fh-b27-el-{EL[ELEM[SIGNS.index(x)]]}">{x}</span>' for x in xs)
        lis += (f'<li class="fh-b27-el-{EL[ELEM[i]]}"><p class="fh-b27-cpx-sn"><b>{a}</b><small>{PERIOD[i]}・{ELEM[i]}のエレメント</small></p>'
                f'<p><em>調和</em>{chip(tri)}</p><p><em>協力</em>{chip(sex)}</p><p><em>惹かれ合う</em>{chip([opp])}</p></li>')
    out.append(f'''<section class="fh-b27-sec" id="b27-cp-best">
  <h2><span class="fh-b27-n">{n}</span>星座別・相性がいい星座</h2>
  <p>それぞれの星座から見て、「調和」（同じエレメント）と「協力」（力を貸し合えるエレメント）に当たる星座、正反対で惹かれ合いやすい星座です。星座の期間は目安で、境目の日は年によって変わります。</p>
  <ul class="fh-b27-cpx-best fh-b27-cpx-signs">{lis}</ul>
</section>''')
    n += 1
    # 3) 関係の型
    cards = "".join(f'<div class="fh-b27-cpx-ty{i % 6}"><h3><b class="{t[2]}" style="background:var(--paper);border:1.5px solid var(--line)">{t[1]}</b>{t[0]}</h3><small>太陽の位置の角度：{t[3]}</small><p>{t[4]}</p></div>' for i, t in enumerate(TYPES))
    out.append(f'''<section class="fh-b27-sec" id="b27-cp-types">
  <h2><span class="fh-b27-n">{n}</span>関係の型と、それぞれの付き合い方</h2>
  <p>2人の誕生日の太陽の位置がつくる角度から、関係を6つの型に分けています。どの型にも、よいところと気をつけたいところがあります。</p>
  <div class="fh-b27-cpx-types">{cards}</div>
</section>''')
    n += 1
    # 3.5) 恋愛・友達・仕事
    trs = "".join(f'<tr><th scope="row"><b class="{c}">{m}</b>{t}</th><td>{l}</td><td>{f}</td><td>{w}</td></tr>' for t, m, c, l, f, w in SCENES)
    out.append(f'''<section class="fh-b27-sec" id="b27-cp-scene">
  <h2><span class="fh-b27-n">{n}</span>恋愛・友達・仕事での相性</h2>
  <p>同じ関係の型でも、恋人どうし、友人どうし、仕事仲間どうしでは、よさの出方と気をつけたい点が少しずつ変わります。上の診断で出た型の行を読んでみてください。</p>
  <div class="fh-b27-cpx-wrap" tabindex="0" role="region" aria-label="関係の型ごとの恋愛・友達・仕事での相性（横にスクロールできます）"><table class="fh-b27-cpx-sc"><caption>関係の型ごとの、恋愛・友達・仕事での付き合い方</caption><thead><tr><th scope="col">関係の型</th><th scope="col">恋愛</th><th scope="col">友達</th><th scope="col">仕事</th></tr></thead><tbody>{trs}</tbody></table></div>
</section>''')
    n += 1
    # 4) 誕生日の数
    g = "".join(f'<li class="fh-b27-cpx-g{i}"><b>{a}</b><small>誕生日の数 {b}</small><span>{c}タイプ</span></li>' for i, (a, b, c) in enumerate(NUMG))
    tr = "".join(f'<tr><th scope="row">{a}×{b}</th><td>{t}</td></tr>' for (a, b), t in NUM_PAIR.items())
    out.append(f'''<section class="fh-b27-sec" id="b27-cp-num">
  <h2><span class="fh-b27-n">{n}</span>誕生日の数のグループと相性</h2>
  <p>誕生日の数は、生まれた日の数字を1けたになるまで足した数です（例：29日生まれ→2＋9＝11→2）。11は2、22は4として、3つのグループに分けます。</p>
  <ul class="fh-b27-cpx-best fh-b27-cpx-groups">{g}</ul>
  <table class="fh-b27-cpx-num"><caption style="text-align:left;font-size:13px;color:var(--sub);padding-bottom:4px">グループの組み合わせと、2人の傾向</caption><tbody>{tr}</tbody></table>
</section>''')
    n += 1
    # 5) 誕生日別・相性のいい誕生日一覧（compat_366.json＝各誕生日ページの「相性の良い誕生日」と同じ）
    days = {1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
    md = lambda k: f"{int(k[:2])}/{int(k[2:])}"
    cal = ""
    for m in range(1, 13):
        lis = ""
        for d in range(1, days[m] + 1):
            k = f"{m:02d}{d:02d}"
            good = "・".join(md(x["mmdd"]) for x in COMPAT[k]["good"])
            lis += f'<li><a href="{mmdd_url(m, d)}">{m}月{d}日</a><span>{good}</span></li>'
        cal += f'<details{" open" if m == 1 else ""}><summary>{m}月生まれ</summary><ul>{lis}</ul></details>'
    out.append(f'''<section class="fh-b27-sec" id="b27-cp-find">
  <h2><span class="fh-b27-n">{n}</span>誕生日別・相性のいい誕生日一覧</h2>
  <p>366日それぞれについて、特に相性のよい誕生日を5つずつ並べました。各誕生日のページの「相性の良い誕生日」と同じ選び方で、ページを開くと選んだ理由と、気をつけたい誕生日3つも読めます。気になる相手が一覧にいなくても、相性が悪いという意味ではありません。</p>
  <div class="fh-b27-cpx-list">{cal}</div>
</section>''')
    n += 1
    # 6) FAQ
    qa = "".join(f'<details{" open" if i == 0 else ""}><summary>Q. {q}</summary><p>A. {a}</p></details>' for i, (q, a) in enumerate(FAQ))
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    out.append(f'''<section class="fh-b27-sec" id="b27-cp-faq">
  <h2><span class="fh-b27-n">{n}</span>よくある質問</h2>
  <div class="fh-b27-cpx-qa">{qa}</div>
</section>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>''')
    n += 1
    return "\n".join(out), n


def theme_css():
    """相性ページだけの色と飾り（誕生日ページの「紺のノート」と見分けがつくように。2026-10-15 本人の希望）。
    共通CSSは変えず、data-fh-page="compatibility" のときだけ上書きする。"""
    P = '.fh-b27[data-fh-page="compatibility"]'
    return f"""<style id="fh-b27-cpt-css">
{P}{{--ink:#F3E9EC;--sub:#DCCBD1;--mute:#B9A3AC;--paper:#2B1F30;--deep:#23192A;--line:#5E4768;--gold:#F2B8A6;--teal:#9ED5CA;--cream:#FCF1EF;--cream-ink:#3A2630}}
{P} a:hover{{color:#FFD6C9}}
{P} .fh-b27-note{{border-left:0;border-radius:22px;background-color:var(--paper);
  background-image:radial-gradient(circle at 8% 0%,rgba(242,184,166,.20),transparent 38%),radial-gradient(circle at 100% 30%,rgba(158,213,202,.13),transparent 34%),radial-gradient(rgba(255,255,255,.07) 1px,transparent 1.4px);
  background-size:auto,auto,26px 26px;box-shadow:0 14px 40px rgba(0,0,0,.45),inset 0 0 0 1px rgba(242,184,166,.18)}}
{P} .fh-b27-hero{{align-items:center}}
.fh-b27-cpt-emb{{position:relative;flex:0 0 150px;height:110px}}
.fh-b27-cpt-emb i{{position:absolute;top:5px;width:100px;height:100px;border-radius:50%;mix-blend-mode:screen}}
.fh-b27-cpt-emb i:first-child{{left:0;background:radial-gradient(circle at 35% 35%,#FFD3C4,#E0877A 70%);opacity:.85;animation:fh-b27-cpt-a 4s ease-in-out infinite alternate}}
.fh-b27-cpt-emb i:nth-child(2){{right:0;background:radial-gradient(circle at 60% 35%,#D2F2EA,#5FAFA2 70%);opacity:.85;animation:fh-b27-cpt-b 4s ease-in-out infinite alternate}}
.fh-b27-cpt-emb b{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-family:'Shippori Mincho',serif;font-size:22px;font-weight:800;color:#2B1F30;letter-spacing:.08em}}
@keyframes fh-b27-cpt-a{{to{{transform:translateX(8px)}}}}@keyframes fh-b27-cpt-b{{to{{transform:translateX(-8px)}}}}
@media (prefers-reduced-motion:reduce){{.fh-b27-cpt-emb i{{animation:none}}}}
{P} .fh-b27-tape{{transform:none;border-radius:999px;background:linear-gradient(90deg,var(--gold),var(--teal));color:#2B1F30}}
{P} .fh-b27-title{{font-family:'Shippori Mincho',serif;font-weight:800;font-size:31px;letter-spacing:.02em}}
{P} h2{{font-family:'Shippori Mincho',serif;font-weight:800;font-size:24px}}
{P} h2 .fh-b27-n{{border:0;background:linear-gradient(135deg,var(--gold),var(--teal));color:#2B1F30;font-weight:800;border-radius:10px 50% 50% 50%}}
{P} h3{{border-bottom:0;background:linear-gradient(90deg,var(--gold),var(--teal)) left bottom/100% 2px no-repeat}}
{P} .fh-b27-cp-person{{border-color:var(--gold);border-radius:16px}}
{P} .fh-b27-cp-person-b{{border-color:var(--teal)}}
{P} .fh-b27-cp-person-b legend{{color:var(--teal)}}
{P} .fh-b27-toc{{border-style:solid;border-color:rgba(242,184,166,.28);border-radius:16px}}
{P} .fh-b27-toc ol{{columns:2;column-gap:28px;list-style:none;padding-left:0}}
@media (max-width:640px){{{P} .fh-b27-toc ol{{columns:1}}}}
{P} .fh-b27-cp-bar i.fh-b27-cp-on{{background:#D9788A}}
{P} .fh-b27-cp-paper:before{{background:linear-gradient(90deg,var(--gold),var(--teal))}}
{P} .fh-b27-btn{{background:linear-gradient(90deg,#F2B8A6,#E8A3B4);color:#2B1F30}}
{P} .fh-b27-cpx-t td.r4,{P} .fh-b27-cpx-key .r4,{P} .fh-b27-cpx-sc b.r4{{background:#7A3E55}}
{P} .fh-b27-cpx-t td.r2,{P} .fh-b27-cpx-key .r2,{P} .fh-b27-cpx-sc b.r2{{background:#2E5A55}}
{P} .fh-b27-cpx-t td.r0,{P} .fh-b27-cpx-key .r0,{P} .fh-b27-cpx-sc b.r0{{background:#463E6A}}
{P} .fh-b27-cpx-t td.r6,{P} .fh-b27-cpx-key .r6,{P} .fh-b27-cpx-sc b.r6{{background:#5E4A30}}
{P} .fh-b27-cpx-t td.r3,{P} .fh-b27-cpx-key .r3,{P} .fh-b27-cpx-sc b.r3{{background:#3B3F4F}}
{P} .fh-b27-cpx-types div,{P} .fh-b27-cpx-list details{{border-style:solid;border-color:rgba(242,184,166,.28);border-radius:16px}}
{P} .fh-b27-cpx-list summary{{font-family:'Shippori Mincho',serif;font-weight:700}}
@media (max-width:640px){{.fh-b27-cpt-emb{{flex-basis:130px;height:96px}}.fh-b27-cpt-emb i{{width:86px;height:86px}}{P} .fh-b27-title{{font-size:25px}}}}
/* 2026-10-16 メリハリ（本人の感想「ずっと同じ色の文字が続くと読むのが苦痛」「表の白背景に淡い文字が見にくい」への対応） */
{P} .fh-b27-cpx-signs{{gap:12px}}
{P} .fh-b27-cpx-signs li{{border:0;border-radius:14px;padding:12px 14px;background:var(--elbg);color:#2B1F30;border-top:6px solid var(--el);box-shadow:0 4px 12px rgba(0,0,0,.25)}}
{P} .fh-b27-cpx-signs li p{{margin:3px 0;color:#2B1F30;font-size:13.5px;display:flex;flex-wrap:wrap;gap:4px;align-items:center}}
{P} .fh-b27-cpx-signs .fh-b27-cpx-sn b{{font:800 18px 'Shippori Mincho',serif;color:#2B1F30;margin-right:6px}}
{P} .fh-b27-cpx-signs .fh-b27-cpx-sn small{{color:#5E4A55;font-size:12px}}
{P} .fh-b27-cpx-signs em{{font-style:normal;font-weight:800;font-size:12px;color:#5E4A55;min-width:5.2em}}
{P} .fh-b27-cpx-chip{{display:inline-block;border-radius:999px;padding:1px 10px;font-weight:700;font-size:13px;background:var(--elc);color:#fff}}
{P} .fh-b27-el-fire{{--el:#D9654E;--elbg:#FCE6DF;--elc:#B5452F}}{P} .fh-b27-el-earth{{--el:#5E9A55;--elbg:#E5F1DD;--elc:#3F7A37}}{P} .fh-b27-el-air{{--el:#C99A1E;--elbg:#FBF1D2;--elc:#86650F}}{P} .fh-b27-el-water{{--el:#3F7CC0;--elbg:#DDEBF8;--elc:#2F65A6}}
{P} .fh-b27-cpx-types div{{border:0;color:#2B1F30;box-shadow:0 4px 12px rgba(0,0,0,.25)}}
{P} .fh-b27-cpx-types div p,{P} .fh-b27-cpx-types div h3{{color:#2B1F30}}{P} .fh-b27-cpx-types h3 b{{color:#F3E9EC}}{P} .fh-b27-cpx-types small{{color:#6A5560}}
{P} .fh-b27-cpx-ty0{{background:#FCF1EF}}{P} .fh-b27-cpx-ty1{{background:#E3F2EE}}{P} .fh-b27-cpx-ty2{{background:#ECE6F7}}{P} .fh-b27-cpx-ty3{{background:#FBF3DC}}{P} .fh-b27-cpx-ty4{{background:#F9E1E4}}{P} .fh-b27-cpx-ty5{{background:#E2ECF7}}
{P} .fh-b27-cpx-groups li{{border:0;border-radius:14px;padding:10px 14px;display:flex;flex-direction:column;gap:2px;color:#2B1F30}}
{P} .fh-b27-cpx-groups li b{{font:800 17px 'Shippori Mincho',serif;color:#2B1F30}}{P} .fh-b27-cpx-groups li small{{color:#6A5560}}
{P} .fh-b27-cpx-g0{{background:#FCE6DF}}{P} .fh-b27-cpx-g1{{background:#E5F1DD}}{P} .fh-b27-cpx-g2{{background:#FBF1D2}}
{P} table th,{P} table td{{background-color:transparent;color:var(--ink)}}
{P} .fh-b27-cpx-sc tbody tr:nth-child(odd) td,{P} .fh-b27-cpx-sc tbody tr:nth-child(odd) th{{background:rgba(255,255,255,.04)}}
{P} .fh-b27-cpx-sc th[scope=row]{{color:#FFD6C9}}
{P} .fh-b27-cpx-sc td:nth-child(2){{background:rgba(242,150,170,.10)!important;border-left:3px solid rgba(242,150,170,.5)}}
{P} .fh-b27-cpx-sc td:nth-child(3){{background:rgba(158,213,202,.10)!important;border-left:3px solid rgba(158,213,202,.5)}}
{P} .fh-b27-cpx-sc td:nth-child(4){{background:rgba(140,170,230,.10)!important;border-left:3px solid rgba(140,170,230,.5)}}
{P} .fh-b27-cpx-sc thead th:nth-child(2){{color:#F7A9BA}}{P} .fh-b27-cpx-sc thead th:nth-child(3){{color:#9ED5CA}}{P} .fh-b27-cpx-sc thead th:nth-child(4){{color:#A9C2F0}}
{P} .fh-b27-cpx-num th{{color:#FFD6C9;white-space:nowrap}}
/* 2026-10-16 結果が出る瞬間の演出（本人の感想「ワクワクしない」への対応） */
{P} .fh-b27-cp-paper{{position:relative;animation:fh-b27-cpt-drop .8s cubic-bezier(.2,1.3,.4,1) both}}
@keyframes fh-b27-cpt-drop{{from{{opacity:0;transform:translateY(-30px) rotate(-6deg) scale(.92)}}to{{opacity:1}}}}
{P} .fh-b27-cp-paper::after{{content:"♡︎ ♡︎ ♡︎";position:absolute;left:0;right:0;top:-6px;text-align:center;color:#E07A8C;font-size:20px;letter-spacing:.4em;pointer-events:none;animation:fh-b27-cpt-float 1.8s ease-out .5s both}}
@keyframes fh-b27-cpt-float{{0%{{opacity:0;transform:translateY(20px) scale(.6)}}40%{{opacity:1}}100%{{opacity:0;transform:translateY(-36px) scale(1.2)}}}}
{P} .fh-b27-cp-bar i{{transition:background .35s ease,transform .35s ease}}
{P} .fh-b27-cp-bar i.fh-b27-cp-on{{transform:scaleY(1.25)}}
{P} .fh-b27-cp-bar i:nth-child(1){{transition-delay:.9s}}{P} .fh-b27-cp-bar i:nth-child(2){{transition-delay:1.1s}}{P} .fh-b27-cp-bar i:nth-child(3){{transition-delay:1.3s}}{P} .fh-b27-cp-bar i:nth-child(4){{transition-delay:1.5s}}{P} .fh-b27-cp-bar i:nth-child(5){{transition-delay:1.7s}}
{P} .fh-b27-cp-tips,{P} .fh-b27-cp-person,{P} .fh-b27-cp-link{{animation:fh-b27-cpt-up .6s ease 1.2s both}}
@keyframes fh-b27-cpt-up{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}
@media (prefers-reduced-motion:reduce){{{P} .fh-b27-cp-paper,{P} .fh-b27-cp-paper::after,{P} .fh-b27-cp-tips,{P} .fh-b27-cp-person,{P} .fh-b27-cp-link{{animation:none}}{P} .fh-b27-cp-bar i{{transition:none}}}}
</style>"""
