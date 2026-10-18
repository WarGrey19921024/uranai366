"""易占い：64卦の形・名前・之卦・綜卦・錯卦・互卦を計算し、周易の本文（卦辞・爻辞・大象）を添えて data/eki_64.json に出す。
本文の出典：周易（古典・パブリックドメイン）の簡体字テキスト。npm パッケージ c_yijing 0.0.6（ISC）の data/yijing.json を source/eki/zhouyi_text.json に保存。
卦の名前・形は八卦の組み合わせから計算し、出典の「○下○上」と一致することを確かめる。"""
import json, re, pathlib
W = pathlib.Path(__file__).resolve().parent.parent
SRC = json.load(open(W / 'source/eki/zhouyi_text.json', encoding='utf-8'))
# 八卦：下から上への陰陽（1=陽）
TRI = {'乾': ([1,1,1], '天', 'けん', '健やか・力強く進む'), '兌': ([1,1,0], '沢', 'だ', '喜び・話す'),
       '離': ([1,0,1], '火', 'り', '明るさ・つながる'), '震': ([1,0,0], '雷', 'しん', '動き出す・驚き'),
       '巽': ([0,1,1], '風', 'そん', '入りこむ・従う'), '坎': ([0,1,0], '水', 'かん', '困難・深さ'),
       '艮': ([0,0,1], '山', 'ごん', '止まる・積み上げる'), '坤': ([0,0,0], '地', 'こん', '受け入れる・育てる')}
S2J = {'讼':'訟','师':'師','谦':'謙','随':'随','蛊':'蠱','临':'臨','观':'観','贲':'賁','剥':'剥','复':'復','无妄':'无妄','颐':'頤','大过':'大過',
       '离':'離','损':'損','渐':'漸','归妹':'帰妹','丰':'豊','兑':'兌','涣':'渙','节':'節','小过':'小過','既济':'既済','未济':'未済','晋':'晋','大壮':'大壮'}
TS2J = {'离':'離','兑':'兌'}
YOMI = """けんいてん こんいち すいらいちゅん さんすいもう すいてんじゅ てんすいしょう ちすいし すいちひ ふうてんしょうちく てんたくり
ちてんたい てんちひ てんかどうじん かてんたいゆう ちざんけん らいちよ たくらいずい さんぷうこ ちたくりん ふうちかん
からいぜいこう さんかひ さんちはく ちらいふく てんらいむぼう さんてんたいちく さんらいい たくふうたいか かんいすい りいか
たくざんかん らいふうこう てんざんとん らいてんたいそう かちしん ちかめいい ふうかかじん かたくけい すいざんけん らいすいかい
さんたくそん ふうらいえき たくてんかい てんぷうこう たくちすい ちふうしょう たくすいこん すいふうせい たくかかく かふうてい
しんいらい ごんいさん ふうざんぜん らいたくきまい らいかほう かざんりょ そんいふう だいたく ふうすいかん すいたくせつ
ふうたくちゅうふ らいざんしょうか すいかきせい かすいびせい""".split()
NAMES = """乾為天 坤為地 水雷屯 山水蒙 水天需 天水訟 地水師 水地比 風天小畜 天沢履 地天泰 天地否 天火同人 火天大有 地山謙 雷地豫 沢雷随 山風蠱 地沢臨 風地観
火雷噬嗑 山火賁 山地剥 地雷復 天雷无妄 山天大畜 山雷頤 沢風大過 坎為水 離為火 沢山咸 雷風恒 天山遯 雷天大壮 火地晋 地火明夷 風火家人 火沢睽 水山蹇 雷水解
山沢損 風雷益 沢天夬 天風姤 沢地萃 地風升 沢水困 水風井 沢火革 火風鼎 震為雷 艮為山 風山漸 雷沢帰妹 雷火豊 火山旅 巽為風 兌為沢 風水渙 水沢節
風沢中孚 雷山小過 水火既済 火水未済""".split()
POS = ['初', '二', '三', '四', '五', '上']
FIX = []
KANA = dict(zip('あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんがぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ',
  'a i u e o ka ki ku ke ko sa shi su se so ta chi tsu te to na ni nu ne no ha hi fu he ho ma mi mu me mo ya yu yo ra ri ru re ro wa wo n ga gi gu ge go za ji zu ze zo da ji zu de do ba bi bu be bo pa pi pu pe po'.split()))
def romaji(k):
    k = k.replace('りょ', '%').replace('ちゅ', '@').replace('しょ', '#').replace('じゅ', '$')
    s = ''.join({'@': 'chu', '#': 'sho', '$': 'ju', '%': 'ryo'}.get(c) or KANA[c] for c in k)
    return s.replace('ou', 'o').replace('uu', 'u')

def clean(s):
    s = s.strip().replace('<', '').replace('>', '')
    return re.sub(r'臲\W*觯\W*', '臲卼，', s)  # 出典の文字化け（困の上六「臲卼」）を直す

def main():
    hexes = []
    for x in SRC:
        lo, up = x['g'][0], x['g'][2] if len(x['g']) == 4 else None
        lo, up = (TS2J.get(lo, lo), TS2J.get(x['g'][2], x['g'][2]))
        lines = TRI[lo][0] + TRI[up][0]
        n = int(x['i']); short = S2J.get(x['n'], x['n'])
        name = (short + '為' + TRI[up][1]) if lo == up else (TRI[up][1] + TRI[lo][1] + short)
        assert name == NAMES[n - 1], (n, name, NAMES[n - 1])
        c = [l.strip() for l in x['content'].split('\n') if l.strip()]
        gua = c[2].split(':', 1)[-1].split('：', 1)[-1].strip()
        yao = []
        for l in c[3:]:
            m = re.match(r'^(初[九六]|[九六][二三四五]|上[九六])[：:，,](.*)$', l)
            if m and len(yao) < 6:
                yao.append([m.group(1), clean(m.group(2).split('象曰')[0].split('<象>')[0])])
        assert len(yao) == 6, n
        for i, (lab, t) in enumerate(yao):
            right = (POS[i] + ('九' if lines[i] else '六')) if i in (0, 5) else (('九' if lines[i] else '六') + POS[i])
            if lab != right:  # 出典の誤記（例：家人の六四が「九四」）は卦の形から直して記録
                FIX.append(f'{n} {lab}→{right}'); yao[i] = [right, t]
            yao[i][1] = yao[i][1].replace('々', yao[i][1][yao[i][1].index('々') - 1] if '々' in yao[i][1] else '')
        xiang = next(l for l in c if l.startswith('<象>曰') or l.startswith('象曰'))
        xiang = re.sub(r'[“”](\w{1,3})[“”]\.', r'\1。', xiang.split('曰', 1)[1].lstrip('：:'))
        xiang = clean(xiang.split('“')[0])
        hexes.append({'n': n, 'short': short, 'name': name, 'yomi': YOMI[n - 1], 'slug': f'{n:02d}-{romaji(YOMI[n - 1])}',
                      'lower': lo, 'upper': up, 'lines': lines, 'gua_src': clean(gua), 'yao_src': yao, 'xiang_src': xiang,
                      'extra_src': clean(next((l for l in c[3:] if l.startswith('用九') or l.startswith('用六')), ''))[3:]})
    key = {tuple(h['lines']): h['n'] for h in hexes}
    assert len(key) == 64
    for h in hexes:
        L = h['lines']
        h['zhi'] = [key[tuple(L[:i] + [1 - L[i]] + L[i + 1:])] for i in range(6)]  # 之卦（その爻が変わったとき）
        h['zong'] = key[tuple(L[::-1])]            # 綜卦（上下さかさま）
        h['cuo'] = key[tuple(1 - v for v in L)]    # 錯卦（陰陽反対）
        h['hu'] = key[tuple(L[1:4] + L[2:5])]      # 互卦
    # 序卦の対：奇数番と次の番は、さかさまか陰陽反対
    for k in range(0, 64, 2):
        a, b = hexes[k], hexes[k + 1]
        assert b['n'] in (a['zong'], a['cuo']), a['n']
    json.dump({'note': '計算：scripts/calc_eki.py。本文は周易（パブリックドメイン）。卦の並びは序卦（文王の順）。lines は下から上、1=陽',
               'fixes': FIX, 'trigrams': {k: {'lines': v[0], 'nature': v[1], 'yomi': v[2], 'mean': v[3]} for k, v in TRI.items()},
               'hexagrams': hexes}, open(W / 'data/eki_64.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('出典の直し:', FIX)
    print('ok', len(hexes), hexes[2]['slug'], hexes[10]['zhi'], hexes[0]['xiang_src'], hexes[1]['extra_src'])

main()
