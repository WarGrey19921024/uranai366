"""12星座の記事の説明文（メタディスクリプション）を、星座ごとの計算結果から作る。"""
import json
d = json.load(open('data/signs_2027.json', encoding='utf-8'))
meta = json.load(open('out/signs/meta.json', encoding='utf-8'))
KAN = ['牡羊座','牡牛座','双子座','蟹座','獅子座','乙女座','天秤座','蠍座','射手座','山羊座','水瓶座','魚座']
EN = ['aries','taurus','gemini','cancer','leo','virgo','libra','scorpio','sagittarius','capricorn','aquarius','pisces']
out = {}
for kj, en in zip(KAN, EN):
    s = d['signs'][kj]; m = meta[en]
    ja = m['title'].split('の2027年')[0]
    rng = m['desc'].split('（')[1].split('生まれ')[0]
    jup = s['houses']['木星']; sat = s['houses']['土星']
    mo = sorted(s['months'], key=lambda k: -s['months'][k]['総合'])
    best = '・'.join(f'{k}月' for k in sorted(mo[:2], key=int)); low = f'{mo[-1]}月'
    if len(jup) > 1:
        cut = int(jup[1]['from'][5:7])
        j = f'木星は{cut}月ごろまで「{jup[0]["theme"]}」、その後は「{jup[1]["theme"]}」の部屋'
    else:
        j = f'木星は1年を通して「{jup[0]["theme"]}」の部屋'
    st = '・'.join(dict.fromkeys(x['theme'] for x in sat))
    desc = (f'{ja}（{rng}生まれ）の2027年は、{j}に入ります。土星は「{st}」の部屋。運気が高いのは{best}、慎重にいきたいのは{low}。'
            f'月ごとの運勢グラフ、ラッキーデーのカレンダー、12星座の順位、恋愛・仕事・金運まで計算で紹介します。')
    out[en] = {'post': m['post'], 'desc': desc}
    print(len(desc), desc)
json.dump(out, open('out/signs/meta_desc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
