"""易占い 64卦の文章ファイル（data/eki_texts/NN.json）の形と長さを確かめる。
使い方：python check_eki_texts.py [番号 ...]（省略で全部）"""
import json, sys, pathlib, re
W = pathlib.Path(__file__).resolve().parent.parent
THEMES = ['恋愛', '結婚・縁談', '仕事', 'お金', '健康', '人間関係', '願い事', '待ち人', '失せ物', '試験・勉強', '引っ越し・旅行']
JUDGE = ['大いに進んでよい', '進んでよい', '慎重に進む', '待つ', '守りに徹する']
LEN = {'catch': (8, 24), 'kudashi': (2, 80), 'gua_mean': (30, 90), 'xiang_kudashi': (8, 60), 'shape': (70, 140),
       'overall': (200, 340), 'now': (90, 160), 'advice': (70, 140)}
def chk(n):
    p = W / f'data/eki_texts/{n:02d}.json'
    if not p.exists():
        return [f'{n}: ファイルがない']
    e = []
    try:
        d = json.load(open(p, encoding='utf-8'))
    except Exception as x:
        return [f'{n}: JSONが読めない {x}']
    if d.get('n') != n: e.append(f'{n}: n が違う')
    for k, (a, b) in LEN.items():
        v = d.get(k, '')
        if not isinstance(v, str) or not a <= len(v) <= b: e.append(f'{n}: {k} の長さ {len(v) if isinstance(v, str) else v}（{a}〜{b}）')
    kw = d.get('kw', [])
    if not (isinstance(kw, list) and len(kw) == 3 and all(1 <= len(x) <= 8 for x in kw)): e.append(f'{n}: kw は8字以内を3つ')
    if d.get('judge') not in JUDGE: e.append(f'{n}: judge は {JUDGE} のどれか')
    th = d.get('themes', {})
    for t in THEMES:
        v = th.get(t, '')
        if not 45 <= len(v) <= 95: e.append(f'{n}: themes.{t} の長さ {len(v)}（45〜95）')
    if set(th) - set(THEMES): e.append(f'{n}: themes に余分な項目 {set(th) - set(THEMES)}')
    y = d.get('yao', [])
    if len(y) != 6: e.append(f'{n}: yao は6つ')
    for i, z in enumerate(y):
        for k, (a, b) in {'kudashi': (3, 60), 'mean': (20, 70), 'read': (75, 135)}.items():
            if not a <= len(z.get(k, '')) <= b: e.append(f'{n}: yao[{i}].{k} の長さ {len(z.get(k, ""))}（{a}〜{b}）')
    fq = d.get('faq', [])
    if len(fq) != 2 or not all(10 <= len(q.get('q', '')) <= 40 and 60 <= len(q.get('a', '')) <= 160 for q in fq): e.append(f'{n}: faq は q10〜40字・a60〜160字を2つ')
    if n in (1, 2):
        x = d.get('extra', {})
        if not (x.get('kudashi') and 20 <= len(x.get('mean', '')) <= 90): e.append(f'{n}: extra（用九/用六）が必要')
    txt = json.dumps(d, ensure_ascii=False)
    for bad in ['http', '<', '>', '必ず治', '絶対に', '死']:
        if bad in txt: e.append(f'{n}: 使わない言葉「{bad}」')
    return e
ns = [int(x) for x in sys.argv[1:]] or range(1, 65)
errs = [m for n in ns for m in chk(n)]
print('\n'.join(errs) if errs else f'OK {len(list(ns))}卦')
sys.exit(1 if errs else 0)
