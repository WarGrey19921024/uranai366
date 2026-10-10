#!/usr/bin/env python3
"""人生予報 2027年版 誕生日占い：自前の小さな絵（SVGアイコン）一式。

どの絵も「丸いバッジ（やわらかい色の円）＋こげ茶の線画＋差し色1〜2個」。
紺の帳面（#1F2638）の上でも、クリーム色（#F7F1E3）の上でも読めるようにしてある。
既存のキャラクター・絵文字・他社の絵は真似していない（すべてこのファイルで手書き）。

使い方:
  python3 work/scripts/icons.py
    → work/scripts/templates/fh-b27-icons.css（共通CSS。data URI の背景画像）
    → work/out/sample/icons_preview.html（一覧の確認ページ）
ページ側: <i class="fh-b27-ic fh-b27-ic-aries" aria-hidden="true"></i>
  大きさは font-size（1em 四方）か width/height で決める。
注意: 生成するCSSにはバックスラッシュを一切入れない（取り込み工程で消されるため）。
"""
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CSS_PATH = os.path.join(HERE, 'templates', 'fh-b27-icons.css')
PREVIEW_PATH = os.path.join(HERE, '..', 'out', 'sample', 'icons_preview.html')

# ---- 色（「夜の帳面」の配色だけを使う） ----
K = '#2E2A26'      # 線（こげ茶）
CREAM = '#F7F1E3'
YEL = '#E8D9A8'    # 付箋の黄
SKY = '#B9CDE0'    # 薄い青
SAGE = '#BFD8C2'   # セージ
PEACH = '#F2C9B0'  # ピーチ
LAV = '#D9CCF0'    # ラベンダー
GOLD = '#E3C77E'
ROSE = '#E9A07A'
BLUE = '#3987e5'
GREEN = '#199e70'
RED = '#C8553D'


def n(v):
    """数値を短く書く（小数1桁、末尾の .0 を落とす）。"""
    s = f'{v:.1f}'
    if s.endswith('.0'):
        s = s[:-2]
    if s == '-0':
        s = '0'
    return s


def badge(bg, body, sw=2.2):
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48'>"
            f"<circle cx='24' cy='24' r='22.5' fill='{bg}'/>"
            f"<g fill='none' stroke='{K}' stroke-width='{sw}' stroke-linecap='round' stroke-linejoin='round'>"
            f"{body}</g></svg>")


def dot(x, y, r=1.5, c=K):
    return f"<circle cx='{n(x)}' cy='{n(y)}' r='{n(r)}' fill='{c}' stroke='none'/>"


def circ(x, y, r, fill='none', extra=''):
    f = '' if fill in ('none', '') else f" fill='{fill}'"
    return f"<circle cx='{n(x)}' cy='{n(y)}' r='{n(r)}'{f}{extra}/>"


def path(d, fill='none', extra=''):
    f = '' if fill in ('none', '') else f" fill='{fill}'"
    return f"<path d='{d}'{f}{extra}/>"


def star_d(cx, cy, R, r, pts=5, rot=-90):
    out = []
    for i in range(pts * 2):
        rad = R if i % 2 == 0 else r
        a = math.radians(rot + i * 180 / pts)
        out.append(f'{n(cx + rad * math.cos(a))} {n(cy + rad * math.sin(a))}')
    return 'M' + ' L'.join(out) + 'Z'


def sparkle_d(cx, cy, R):
    """4方向にのびる小さなきらめき（曲線のひし形）。"""
    q = R * 0.18
    return (f'M{n(cx)} {n(cy - R)} Q{n(cx + q)} {n(cy - q)} {n(cx + R)} {n(cy)} '
            f'Q{n(cx + q)} {n(cy + q)} {n(cx)} {n(cy + R)} Q{n(cx - q)} {n(cy + q)} {n(cx - R)} {n(cy)} '
            f'Q{n(cx - q)} {n(cy - q)} {n(cx)} {n(cy - R)}Z')


def heart_d(cx, cy, s):
    """cx,cy を中心にした幅 2s ほどのハート。"""
    return (f'M{n(cx)} {n(cy + s)} C{n(cx - 1.7 * s)} {n(cy - 0.1 * s)} {n(cx - 0.9 * s)} {n(cy - 1.25 * s)} '
            f'{n(cx)} {n(cy - 0.45 * s)} C{n(cx + 0.9 * s)} {n(cy - 1.25 * s)} {n(cx + 1.7 * s)} {n(cy - 0.1 * s)} '
            f'{n(cx)} {n(cy + s)}Z')


def scallop_d(cx, cy, r, bumps, depth):
    """花びら状に波打つ円（たてがみなど）。"""
    out = []
    for i in range(bumps):
        a0 = 2 * math.pi * i / bumps
        a1 = 2 * math.pi * (i + 0.5) / bumps
        a2 = 2 * math.pi * (i + 1) / bumps
        p0 = (cx + r * math.cos(a0), cy + r * math.sin(a0))
        c = (cx + (r + depth * 2) * math.cos(a1), cy + (r + depth * 2) * math.sin(a1))
        p2 = (cx + r * math.cos(a2), cy + r * math.sin(a2))
        if i == 0:
            out.append(f'M{n(p0[0])} {n(p0[1])}')
        out.append(f'Q{n(c[0])} {n(c[1])} {n(p2[0])} {n(p2[1])}')
    return ' '.join(out) + 'Z'


def rot(x, y, deg, cx=24, cy=24):
    a = math.radians(deg)
    dx, dy = x - cx, y - cy
    return cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a)


def cal(x, y, w, h, head=RED, fill=CREAM):
    """カレンダーの台紙（上の帯つき・リング2つ）。"""
    return (f"<rect x='{n(x)}' y='{n(y)}' width='{n(w)}' height='{n(h)}' rx='2.5' fill='{fill}'/>"
            + path(f'M{n(x)} {n(y + 6)} V{n(y + 2.5)} Q{n(x)} {n(y)} {n(x + 2.5)} {n(y)} H{n(x + w - 2.5)} '
                   f'Q{n(x + w)} {n(y)} {n(x + w)} {n(y + 2.5)} V{n(y + 6)}Z', head)
            + path(f'M{n(x + w * 0.3)} {n(y - 2.5)} V{n(y + 2)} M{n(x + w * 0.7)} {n(y - 2.5)} V{n(y + 2)}'))


# ======================================================================
#  絵の定義
# ======================================================================
ICONS = {}

# ---------- 12星座（火=ピーチ、地=セージ、風=薄い青、水=ラベンダー） ----------
ICONS['aries'] = badge(PEACH,
    path('M19 21 C17 13 8 14 10 21 C11 25 16 25 16 21') +
    path('M29 21 C31 13 40 14 38 21 C37 25 32 25 32 21') +
    path('M17 23 Q17 17 24 17 Q31 17 31 23 L29.5 32 Q24 37.5 18.5 32Z', CREAM) +
    dot(21, 26) + dot(27, 26) + path('M22.5 31.5 Q24 32.8 25.5 31.5') +
    dot(18.5, 29.5, 1.3, ROSE) + dot(29.5, 29.5, 1.3, ROSE))

ICONS['taurus'] = badge(SAGE,
    path('M16.5 21 Q10 19 11 12.5 Q14 17 19 17.5', GOLD) +
    path('M31.5 21 Q38 19 37 12.5 Q34 17 29 17.5', GOLD) +
    path('M15 25 Q15 16 24 16 Q33 16 33 25 Q33 36 24 36 Q15 36 15 25Z', CREAM) +
    path('M18 31 Q18 27 24 27 Q30 27 30 31 Q30 35 24 35 Q18 35 18 31Z', PEACH) +
    dot(20, 22.5) + dot(28, 22.5) + dot(22, 31, 1.1) + dot(26, 31, 1.1))

ICONS['gemini'] = badge(SKY,
    circ(16.5, 27, 7, CREAM) + circ(31.5, 27, 7, GOLD) +
    dot(14.3, 26.5, 1.3) + dot(18.7, 26.5, 1.3) + path('M15 30 Q16.5 31.3 18 30') +
    dot(29.3, 26.5, 1.3) + dot(33.7, 26.5, 1.3) + path('M30 30 Q31.5 31.3 33 30') +
    path(star_d(24, 13, 4.5, 2), CREAM, " stroke-width='1.8'"))

ICONS['cancer'] = badge(LAV,
    path('M17 25 L13.5 19 M31 25 L34.5 19') +
    path('M13.5 19 C8 18 8 11 12 10 L13 14 L16 11.5 C18 14 16.5 18.5 13.5 19Z', ROSE) +
    path('M34.5 19 C40 18 40 11 36 10 L35 14 L32 11.5 C30 14 31.5 18.5 34.5 19Z', ROSE) +
    path('M14 31 L10 33 M15 34 L12 37.5 M34 31 L38 33 M33 34 L36 37.5') +
    path('M14 29 Q14 23 24 23 Q34 23 34 29 Q34 36 24 36 Q14 36 14 29Z', ROSE) +
    dot(21, 28.5) + dot(27, 28.5) + path('M22.5 32 Q24 33.2 25.5 32'))

ICONS['leo'] = badge(PEACH,
    path(scallop_d(24, 24, 12, 10, 1.6), GOLD) +
    circ(18, 17.5, 2.6, CREAM) + circ(30, 17.5, 2.6, CREAM) +
    circ(24, 25, 8, CREAM) +
    dot(21, 24) + dot(27, 24) +
    path('M22.6 27.3 H25.4 L24 28.8Z', K, " stroke-width='1.4'") + path('M21.5 30.3 Q24 32 26.5 30.3'))

ICONS['virgo'] = badge(SAGE,
    path('M14 33 C12 22 15 13 24 13 C33 13 36 22 34 33 Q30 34.5 30 30 L18 30 Q18 34.5 14 33Z', GOLD) +
    circ(24, 25, 7, CREAM) +
    path('M17.5 22 Q22 22 24.5 18 Q27 22 30.5 22') +
    dot(21.5, 26) + dot(26.5, 26) + path('M22.6 29 Q24 30 25.4 29') +
    path('M16 39 Q24 32 32 39') +
    circ(32, 15.5, 3, ROSE) + dot(32, 15.5, 1.1))

ICONS['libra'] = badge(SKY,
    path('M24 13 V34 M18 35 H30 M12 18 H36') + dot(24, 12, 2) +
    path('M12 18 L8.5 27 M12 18 L15.5 27 M36 18 L32.5 27 M36 18 L39.5 27') +
    path('M7.5 27 Q12 33 16.5 27Z', GOLD) + path('M31.5 27 Q36 33 40.5 27Z', GOLD))

ICONS['scorpio'] = badge(LAV,
    path('M14 28 L10 25 M10 25 Q7 21 10 19 L11 22 L13 20 Q14 23 10 25') +
    path('M23 31 Q30 34 34 29 Q38 23 34 17 Q31 13 28 16') +
    path('M28 16 L31.5 14.5 M28 16 L28.5 19.5') +
    path('M15 31 L12 35 M19 33.5 L17.5 37.5 M23 33.5 L24 37.5') +
    path('M12.5 29.5 Q12.5 24 18.5 24 Q25 24 25 29.5 Q25 34 18.5 34 Q12.5 34 12.5 29.5Z', RED) +
    dot(16.5, 28, 1.3, CREAM) + dot(20.5, 28, 1.3, CREAM))

ICONS['sagittarius'] = badge(PEACH,
    path('M12 20 Q30 14 28 36') + path('M12 20 L28 36', '', " stroke-width='1.4'") +
    path('M13 35 L33 15') + path('M27 13 L35 13 L35 21Z', GOLD) +
    path('M13 35 L13 30.5 M13 35 L17.5 35 M16 32 L16 28 M16 32 L20 32'))

ICONS['capricorn'] = badge(SAGE,
    path('M20.5 18 Q16 9 9 11 Q14 12 17 20', GOLD) +
    path('M27.5 18 Q32 9 39 11 Q34 12 31 20', GOLD) +
    path('M17.5 22.5 L12 23.5 Q13 27 18 26 M30.5 22.5 L36 23.5 Q35 27 30 26') +
    path('M17 21 Q17 17 24 17 Q31 17 31 21 Q31 30 24 34 Q17 30 17 21Z', CREAM) +
    dot(21, 24) + dot(27, 24) + path('M22 34 L24 39 L26 34', CREAM))

ICONS['aquarius'] = badge(SKY,
    path('M26 15 Q32.5 18 31 25.5 Q29.5 32 33.5 36.5', '', f" stroke='{BLUE}' stroke-width='2.8'") +
    dot(36.5, 27.5, 1.4, BLUE) + dot(28, 36.5, 1.3, BLUE) +
    "<g transform='rotate(38 18 24)'>" +
    path('M15.5 15 V17.5 C9.5 19.5 9 31 14 34 H22 C27 31 26.5 19.5 20.5 17.5 V15Z', GOLD) +
    "<rect x='13' y='12' width='10' height='3.5' rx='1.5' fill='" + GOLD + "'/>" +
    path('M12 26 Q15 23.5 18 26 T24 26', '', f" stroke='{RED}' stroke-width='1.8'") + "</g>")

ICONS['pisces'] = badge(LAV,
    path('M12 17 Q19 10 27 17 Q19 24 12 17Z', CREAM) + path('M27 17 L33 12.5 V21.5Z', CREAM) + dot(16, 16.3, 1.3) +
    path('M36 31 Q29 24 21 31 Q29 38 36 31Z', ROSE) + path('M21 31 L15 26.5 V35.5Z', ROSE) + dot(32, 30.3, 1.3) +
    path('M33 16 Q38 21 34 25 M15 32 Q10 27 14 23', '', " stroke-width='1.5' stroke-dasharray='1 3'"))

# ---------- 季節 ----------
_petal = 'M24 24 C19.5 19.5 19.5 14 21.5 11.5 L24 13.5 L26.5 11.5 C28.5 14 28.5 19.5 24 24Z'
ICONS['spring'] = badge(PEACH,
    f"<path id='p' d='{_petal}' fill='{CREAM}'/>" +
    ''.join(f"<use href='#p' transform='rotate({i * 72} 24 24)'/>" for i in range(1, 5)) +
    circ(24, 24, 3, ROSE, " stroke-width='1.6'"))

ICONS['summer'] = badge(SKY,
    ''.join(path(f'M{n(rot(24, 13.5, a)[0])} {n(rot(24, 13.5, a)[1])} L{n(rot(24, 9.5, a)[0])} {n(rot(24, 9.5, a)[1])}')
            for a in range(0, 360, 45)) +
    circ(24, 24, 7.5, GOLD) + dot(21.3, 23, 1.2) + dot(26.7, 23, 1.2) + path('M21.5 26.5 Q24 28.5 26.5 26.5', '', " stroke-width='1.8'"))

ICONS['autumn'] = badge(YEL,
    path('M24 9.5 L27 15.5 L31 13.5 L30.5 19.5 L37.5 18.5 L34 24.5 L36.5 27.5 L29 29 L29.5 32.5 L24 30 L18.5 32.5 L19 29 '
         'L11.5 27.5 L14 24.5 L10.5 18.5 L17.5 19.5 L17 13.5 L21 15.5Z', RED) +
    path('M24 38.5 V17 M24 29 L31 22.5 M24 29 L17 22.5', '', f" stroke='{CREAM}' stroke-width='1.6'") +
    path('M24 31 V38.5'))


def _snow():
    out = 'M24 10.5 V37.5 M12.3 17.3 L35.7 30.8 M12.3 30.8 L35.7 17.3'
    br = []
    for a in range(0, 360, 60):
        for d, s in ((7, 3.5),):
            bx, by = rot(24, 24 - d, a)
            l1 = rot(24 - s, 24 - d - s, a)
            l2 = rot(24 + s, 24 - d - s, a)
            br.append(f'M{n(l1[0])} {n(l1[1])} L{n(bx)} {n(by)} L{n(l2[0])} {n(l2[1])}')
    return path(out) + path(' '.join(br), '', " stroke-width='1.9'") + circ(24, 24, 2.6, CREAM)


ICONS['winter'] = badge(LAV, _snow())

# ---------- 占いの種類 ----------
ICONS['kyusei'] = badge(YEL,
    "<rect x='13' y='13' width='22' height='22' rx='3' fill='" + CREAM + "'/>" +
    path('M20.3 13.5 V34.5 M27.7 13.5 V34.5 M13.5 20.3 H34.5 M13.5 27.7 H34.5', '', " stroke-width='1.5'") +
    path(''.join(f'M{x} {y}h0' for x, y in ((16.7, 16.7), (24, 16.7), (31.3, 16.7), (16.7, 24), (31.3, 24),
                                             (16.7, 31.3), (24, 31.3), (31.3, 31.3))), '', " stroke-width='2.8'") +
    path(star_d(24, 24.3, 3.6, 1.6), GOLD, " stroke-width='1.2'"))

ICONS['eto'] = badge(PEACH,
    circ(24, 24, 13, CREAM) +
    path(' '.join(f'M{n(rot(24, 11.5, a)[0])} {n(rot(24, 11.5, a)[1])} L{n(rot(24, 16.5, a)[0])} {n(rot(24, 16.5, a)[1])}'
                  for a in range(0, 360, 30)), '', " stroke-width='1.6'") +
    circ(24, 24, 5.5, GOLD) + dot(24, 11.6, 1.8, RED))

ICONS['shichu'] = badge(SAGE,
    path('M11 14 H37 M12 36.5 H36') +
    ''.join(f"<rect x='{n(x)}' y='17' width='4.6' height='17' rx='1.2' fill='{c}'/>"
            for x, c in ((11.6, CREAM), (18, GOLD), (24.4, CREAM), (30.8, GOLD))))

ICONS['shuku'] = badge(LAV,
    path('M27 11 A13 13 0 1 0 37 30 A10.5 10.5 0 0 1 27 11Z', GOLD) +
    path(star_d(33, 15, 3.2, 1.3), CREAM, " stroke-width='1.3'") +
    dot(37.5, 22, 1.4) + dot(29.5, 21, 1.1))

ICONS['maya'] = badge(YEL,
    circ(24, 12.5, 3.5, GOLD, " stroke-width='1.8'") +
    path('M24 6 V7.5 M17.5 12.5 H19 M29 12.5 H30.5', '', " stroke-width='1.6'") +
    path('M9.5 36 H38.5 V32 H35 V28 H31.5 V24 H28 V20 H20 V24 H16.5 V28 H13 V32 H9.5Z', ROSE) +
    path('M21.5 36 V29 H26.5 V36', CREAM, " stroke-width='1.8'"))

ICONS['suhi'] = badge(SKY,
    "<rect x='10.5' y='13' width='13' height='16' rx='2.5' fill='" + CREAM + "'/>" +
    path('M15 18.5 L17.5 16.5 V25.5') +
    "<rect x='24.5' y='19' width='13' height='16' rx='2.5' fill='" + GOLD + "'/>" +
    path('M28 25 C28.5 21.5 34 21.5 34 25 C34 27.5 29 29.5 28 31.5 H34.2') +
    path(sparkle_d(35.5, 12.5, 3.3), CREAM, " stroke-width='1.3'"))

ICONS['animal'] = badge(PEACH,
    path('M16.5 31 Q16.5 24.5 24 24.5 Q31.5 24.5 31.5 31 Q31.5 36 27.5 36 Q25.5 36 24 35 Q22.5 36 20.5 36 Q16.5 36 16.5 31Z', CREAM) +
    "<ellipse cx='14' cy='22.5' rx='3' ry='3.6' fill='" + RED + "'/>" +
    "<ellipse cx='20' cy='15.5' rx='3' ry='3.8' fill='" + GOLD + "'/>" +
    "<ellipse cx='28' cy='15.5' rx='3' ry='3.8' fill='" + GREEN + "'/>" +
    "<ellipse cx='34' cy='22.5' rx='3' ry='3.6' fill='" + BLUE + "'/>")

ICONS['bio'] = badge(YEL,
    path('M10.5 16 Q13.8 11 17.1 16 T23.7 16 T30.3 16 T36.9 16', '', f" stroke='{RED}' stroke-width='2.6'") +
    path('M10.5 24 Q13.8 19 17.1 24 T23.7 24 T30.3 24 T36.9 24', '', f" stroke='{GREEN}' stroke-width='2.6'") +
    path('M10.5 32 Q13.8 27 17.1 32 T23.7 32 T30.3 32 T36.9 32', '', f" stroke='{BLUE}' stroke-width='2.6'"))

# ---------- 見出し ----------
ICONS['nature'] = badge(PEACH,
    circ(24, 25.5, 11.5, CREAM) +
    path('M18 24 Q20 21.5 22 24 M26 24 Q28 21.5 30 24') +
    path('M20.5 28.5 Q24 32.5 27.5 28.5') +
    dot(17.5, 28.5, 1.7, ROSE) + dot(30.5, 28.5, 1.7, ROSE) +
    path(heart_d(35, 14, 3.6), RED, " stroke-width='1.6'"))

ICONS['koyomi'] = badge(YEL,
    cal(13, 13, 22, 23) +
    path('M18 25 H30 M18 29.5 H30 M18 34 H25', '', " stroke-width='1.7'") +
    dot(31, 34, 1.6, RED))

ICONS['mono'] = badge(LAV,
    ''.join(circ(16 + 4.2 * math.cos(math.radians(a)), 19 + 4.2 * math.sin(math.radians(a)), 3, ROSE, " stroke-width='1.6'")
            for a in range(-90, 270, 72)) + circ(16, 19, 2.4, GOLD, " stroke-width='1.6'") +
    path('M23 29 L26.5 24.5 H34.5 L38 29 L30.5 37.5Z', SKY) +
    path('M23 29 H38 M28.5 24.5 L30.5 29 L32.5 24.5 M30.5 29 V37', '', " stroke-width='1.5'"))

ICONS['compat'] = badge(PEACH,
    path(heart_d(19, 24, 7.5), ROSE) + path(heart_d(29.5, 26, 7.5), RED))

ICONS['famous'] = badge(LAV,
    path(star_d(23, 26, 11, 4.8), GOLD) + path(sparkle_d(35, 13, 4), CREAM, " stroke-width='1.5'") +
    dot(20.5, 26, 1.3) + dot(25.5, 26, 1.3))

ICONS['fate'] = badge(SKY,
    path('M11 33 L23 24.5 M13 26 L22 20.5 M17.5 36.5 L26 28.5', '', " stroke-width='2'") +
    path(star_d(30.5, 18.5, 8, 3.6, rot=-80), GOLD))

ICONS['work'] = badge(SAGE,
    path('M19.5 17.5 V15 Q19.5 13 21.5 13 H26.5 Q28.5 13 28.5 15 V17.5') +
    "<rect x='11' y='17.5' width='26' height='18' rx='3' fill='" + PEACH + "'/>" +
    path('M11.5 25 H36.5') + "<rect x='21.5' y='23' width='5' height='4.5' rx='1' fill='" + GOLD + "' stroke-width='1.6'/>")

ICONS['love'] = badge(PEACH, path(heart_d(24, 24.5, 11), RED) +
                      path('M17 19.5 Q18.5 17 21 17', '', f" stroke='{CREAM}' stroke-width='2'"))

ICONS['money'] = badge(YEL,
    circ(24, 24, 12, GOLD) + circ(24, 24, 9, '', " stroke-width='1.4'") +
    path('M20 18.5 L24 24 L28 18.5 M24 24 V31 M20.5 25.5 H27.5 M20.5 28.5 H27.5', '', " stroke-width='2'"))

ICONS['health'] = badge(SAGE,
    path('M24 19 C20 15.5 12.5 17 12.5 25.5 C12.5 32.5 17.5 37.5 21 36.5 C22.5 36 25.5 36 27 36.5 C30.5 37.5 35.5 32.5 35.5 25.5 '
         'C35.5 17 28 15.5 24 19Z', RED) +
    path('M24 19 Q23.5 14 21.5 11.5') +
    path('M24.5 15.5 Q28 10 34 11.5 Q31 17 24.5 15.5Z', GREEN) +
    path('M17 23.5 Q17.5 21 20 20.5', '', f" stroke='{CREAM}' stroke-width='1.8'"))

ICONS['people'] = badge(SKY,
    circ(30, 17.5, 4.2, GOLD) + path('M22 35 Q22 25 30 25 Q38 25 38 35Z', GOLD) +
    circ(18, 19.5, 4.5, CREAM) + path('M9.5 37 Q9.5 27 18 27 Q26.5 27 26.5 37Z', CREAM))

ICONS['grow'] = badge(YEL,
    path('M12 36 Q24 30 36 36', SAGE, " stroke-width='0'") + path('M12 36 Q24 30 36 36') +
    path('M24 33 V20') +
    path('M24 25 Q14 25 13.5 16.5 Q22.5 16 24 25Z', GREEN) +
    path('M24 21 Q33 20.5 34 12 Q25 12 24 21Z', SAGE))

ICONS['stars'] = badge(LAV,
    "<g transform='rotate(-20 24 25)'>" +
    "<ellipse cx='24' cy='25' rx='15' ry='4.5'/>" + circ(24, 25, 8.5, GOLD) +
    path('M9 25 A15 4.5 0 0 0 39 25') + "</g>" +
    dot(12, 13, 1.4, CREAM) + dot(36, 36, 1.2, CREAM) + path(sparkle_d(36.5, 12.5, 2.8), CREAM, " stroke-width='1.2'"))

ICONS['season'] = badge(YEL,
    path('M24 37 V24 M24 30 L19.5 26 M24 28 L28.5 24.5') +
    path('M15 20.5 Q13 12 21 11.5 Q24 7.5 28 11 Q35.5 11 33.5 19 Q37 24.5 30 26.5 Q24 29.5 18 26.5 Q11.5 25 15 20.5Z', SAGE) +
    dot(20, 17.5, 1.4, RED) + dot(28.5, 16, 1.4, RED) + dot(27, 22.5, 1.4, RED) + path('M18 37 H30'))

ICONS['graph'] = badge(SKY,
    "<rect x='11' y='12' width='26' height='24' rx='3' fill='" + CREAM + "'/>" +
    path('M15 16 V31.5 H33', '', " stroke-width='1.6'") +
    path('M17 28 L22 22 L26.5 25 L32 16.5', '', f" stroke='{BLUE}' stroke-width='2.4'") +
    dot(22, 22, 1.7, BLUE) + dot(26.5, 25, 1.7, BLUE) + dot(32, 16.5, 1.9, RED))

ICONS['month'] = badge(SAGE,
    cal(11.5, 13, 25, 23) +
    path('M17.75 19.5 V35.5 M24 19.5 V35.5 M30.25 19.5 V35.5 M12 24.8 H36 M12 30.2 H36', '', " stroke-width='1.3'") +
    "<rect x='24.6' y='25.4' width='5' height='4.2' fill='" + GOLD + "' stroke='none'/>")

ICONS['action'] = badge(PEACH,
    path('M16 13.5 H34 L29.5 19.5 L34 25.5 H16Z', RED) +
    path('M16 11.5 V37') + dot(16, 11, 1.8) + path('M11 37 H21'))

ICONS['omamori'] = badge(SKY,
    path('M16 19.5 L20.5 15 H27.5 L32 19.5 V35 Q32 37.5 29.5 37.5 H18.5 Q16 37.5 16 35Z', RED) +
    "<rect x='20.5' y='21' width='7' height='12.5' rx='1' fill='" + CREAM + "' stroke-width='1.6'/>" +
    path('M24 24 V30.5', '', " stroke-width='1.6'") +
    path('M24 15 Q19 8 16.5 11 Q16 14.5 24 15 Q32 14.5 31.5 11 Q29 8 24 15Z', GOLD, " stroke-width='1.8'") +
    path('M24 15 L22 19 M24 15 L26 19', '', " stroke-width='1.6'"))

ICONS['gift'] = badge(LAV,
    path('M24 18 C20.5 11 14 13 17 17.5 M24 18 C27.5 11 34 13 31 17.5') +
    "<rect x='13' y='24' width='22' height='13' rx='1.5' fill='" + ROSE + "'/>" +
    "<rect x='11' y='18' width='26' height='6' rx='1.5' fill='" + ROSE + "'/>" +
    path('M24 18 V37', '', f" stroke='{GOLD}' stroke-width='3.4'") + path('M22 18 V37 M26 18 V37', '', " stroke-width='1.2'"))

ICONS['cake'] = badge(PEACH,
    "<rect x='12' y='24' width='24' height='13' rx='2.5' fill='" + CREAM + "'/>" +
    path('M12 28 Q15 32 18 28 T24 28 T30 28 T36 28', '', f" stroke='{ROSE}' stroke-width='2.4'") +
    "<rect x='22.5' y='16' width='3' height='8' rx='1' fill='" + SKY + "' stroke-width='1.6'/>" +
    path('M24 8.5 Q27.5 12.5 24 14.5 Q20.5 12.5 24 8.5Z', GOLD, " stroke-width='1.6'") +
    dot(18, 33, 1.3, RED) + dot(30, 33, 1.3, RED) + dot(24, 33.5, 1.3, RED))

ICONS['year'] = badge(LAV,
    path('M17 12.5 C17 20 22 21 22 24 C22 27 17 28 17 35.5 H31 C31 28 26 27 26 24 C26 21 31 20 31 12.5Z', CREAM) +
    path('M19 15 H29 Q28 20 24 22 Q20 20 19 15Z', GOLD, " stroke='none'") +
    path('M18.5 35 Q19 29.5 24 28.5 Q29 29.5 29.5 35Z', GOLD, " stroke='none'") +
    path('M24 24 V28', '', f" stroke='{GOLD}' stroke-width='1.6'") +
    path('M17 12.5 C17 20 22 21 22 24 C22 27 17 28 17 35.5 M31 12.5 C31 20 26 21 26 24 C26 27 31 28 31 35.5') +
    path('M14 12.5 H34 M14 35.5 H34', '', " stroke-width='2.6'"))

ICONS['next'] = badge(SKY,
    ''.join(path(f'M{n(rot(24, 18.5, a, 24, 30)[0])} {n(rot(24, 18.5, a, 24, 30)[1])} '
                 f'L{n(rot(24, 14.5, a, 24, 30)[0])} {n(rot(24, 14.5, a, 24, 30)[1])}') for a in (-60, -30, 0, 30, 60)) +
    path('M15 30 A9 9 0 0 1 33 30Z', GOLD) +
    path('M10 30 H38') + path('M15 35 H22 M26 35 H33', '', f" stroke='{BLUE}' stroke-width='2'"))

ICONS['letter'] = badge(YEL,
    "<rect x='10.5' y='15' width='27' height='19' rx='2.5' fill='" + CREAM + "'/>" +
    path('M11.5 16.5 L24 26 L36.5 16.5') +
    path(heart_d(24, 26.5, 3.4), RED, " stroke-width='1.5'"))

ICONS['links'] = badge(SAGE,
    path('M24 16 C20 13 14.5 13 10.5 14.5 V33.5 C14.5 32 20 32 24 35 C28 32 33.5 32 37.5 33.5 V14.5 C33.5 13 28 13 24 16Z', CREAM) +
    path('M24 16.5 V34.5') +
    path('M14 19 Q17 18 20.5 19.5 M14 23.5 Q17 22.5 20.5 24 M27.5 19.5 Q31 18 34 19 M27.5 24 Q31 22.5 34 23.5',
         '', " stroke-width='1.5'") +
    path('M30 13.8 V21 L32 19.3 L34 21 V13.3', RED, " stroke-width='1.4'"))

ICONS['about'] = badge(YEL,
    path('M27.5 27.5 L35 35', '', " stroke-width='4.4'") +
    circ(21.5, 21.5, 9, CREAM) + dot(21.5, 17, 1.6) + path('M21.5 20.5 V26.5', '', " stroke-width='2.6'"))

ICONS['today'] = badge(PEACH,
    ''.join(path(f'M{n(rot(32, 9, a, 32, 15)[0])} {n(rot(32, 9, a, 32, 15)[1])} '
                 f'L{n(rot(32, 7, a, 32, 15)[0])} {n(rot(32, 7, a, 32, 15)[1])}', '', " stroke-width='1.8'")
            for a in range(0, 360, 45)) +
    circ(32, 15, 4.6, GOLD) +
    cal(11, 20, 21, 17) + dot(21.5, 31, 2.4, RED))

# ---------- 小さなお店（品物の種類） ----------
ICONS['stationery'] = badge(SKY,
    "<rect x='11.5' y='12' width='17' height='24' rx='2' fill='" + CREAM + "'/>" +
    path('M15.5 18 H24.5 M15.5 22.5 H24.5 M15.5 27 H22', '', " stroke-width='1.5'") +
    "<g transform='rotate(25 32 24)'>" +
    "<rect x='29.5' y='10' width='5' height='20' rx='1.2' fill='" + BLUE + "'/>" +
    path('M29.5 30 L32 35.5 L34.5 30Z', CREAM) + path('M29.5 14 H34.5', '', " stroke-width='1.5'") + "</g>")

ICONS['plant'] = badge(SAGE,
    path('M24 27 V19') +
    path('M24 24 Q14.5 24 14 15.5 Q23 15 24 24Z', GREEN) +
    path('M24 21 Q33.5 20.5 34 12 Q25 12 24 21Z', GREEN) +
    path('M16.5 30 H31.5 L29.5 37.5 H18.5Z', ROSE) +
    "<rect x='15' y='26.5' width='18' height='4' rx='1' fill='" + ROSE + "'/>")

ICONS['flower'] = badge(LAV,
    path('M19 25 L22.5 21 M24 25 V19 M29 25 L25.5 21', '', f" stroke='{GREEN}' stroke-width='2'") +
    circ(17.5, 18, 4.5, ROSE) + circ(30.5, 18, 4.5, GOLD) + circ(24, 14, 4.5, CREAM) +
    dot(17.5, 18, 1.3) + dot(30.5, 18, 1.3) + dot(24, 14, 1.3) +
    path('M15 24 H33 L24 39Z', PEACH) + path('M20.5 30 L24 33 L27.5 30', '', " stroke-width='1.6'"))

ICONS['tableware'] = badge(YEL,
    "<ellipse cx='24' cy='33' rx='14' ry='4.5' fill='" + CREAM + "'/>" +
    path('M31 20 Q36.5 20 36.5 23.5 Q36.5 27.5 30.5 27.5') +
    path('M15 17 H31 V24 Q31 32 23 32 Q15 32 15 24Z', CREAM) +
    path('M15.5 21 H30.5', '', f" stroke='{BLUE}' stroke-width='1.8'") +
    path('M20 13 Q19 11 20.5 9 M25 13 Q24 11 25.5 9', '', " stroke-width='1.6'"))

ICONS['kitchen'] = badge(PEACH,
    path('M13 25 H8.5 M35 25 H39.5') +
    path('M13 21.5 H35 V30 Q35 36 29 36 H19 Q13 36 13 30Z', RED) +
    path('M11 21.5 Q24 12 37 21.5Z', CREAM) + dot(24, 14, 2.2, CREAM) + circ(24, 14.2, 2.2) +
    path('M17.5 27 Q19 26 20.5 27', '', f" stroke='{CREAM}' stroke-width='1.6'"))

ICONS['fashion'] = badge(PEACH,
    path('M18.5 12 L11 16 L8 23 L14 25.5 L16 23 V37 H32 V23 L34 25.5 L40 23 L37 16 L29.5 12 Q24 17.5 18.5 12Z', SKY) +
    path('M16 28 H32', '', f" stroke='{CREAM}' stroke-width='2'") + path('M16.5 31.5 H31.5', '', f" stroke='{BLUE}' stroke-width='1.8'"))

ICONS['shoes'] = badge(SAGE,
    path('M9.5 32 V20.5 Q9.5 18 12 18 H16 Q17 23.5 22 24.5 L31 26.5 Q38.5 28 38.5 32Z', CREAM) +
    path('M9.5 32 H38.5 V34 Q38.5 36 36.5 36 H11.5 Q9.5 36 9.5 34Z', RED) +
    path('M18 21.5 L20.5 19.5 M21 23.5 L23.5 21.5 M24.5 25 L27 23', '', " stroke-width='1.6'") +
    dot(13, 26, 1.3, BLUE))

ICONS['accessory'] = badge(LAV,
    path('M13 12 Q12.5 29 24 29.5 Q35.5 29 35 12', '', " stroke-width='1.8'") +
    ''.join(dot(x, y, 1.6, GOLD) for x, y in ((14, 21), (17.3, 26.3), (30.7, 26.3), (34, 21))) +
    path('M24 29.5 L28.5 33.5 L24 39 L19.5 33.5Z', RED) + path('M21.5 33.5 H26.5', '', f" stroke='{CREAM}' stroke-width='1.3'"))

ICONS['stone'] = badge(SKY,
    path('M11.5 20 L18 12.5 H30 L36.5 20 L24 37Z', LAV) +
    path('M11.5 20 H36.5 M18 12.5 L21 20 L24 37 M30 12.5 L27 20 L24 37 M21 20 L24 12.5 L27 20', '', " stroke-width='1.5'") +
    path('M15 19 L18.5 15', '', f" stroke='{CREAM}' stroke-width='1.8'"))

ICONS['bag'] = badge(YEL,
    path('M19 20 Q19 11.5 24 11.5 Q29 11.5 29 20') +
    path('M12.5 20 H35.5 L33.5 37 H14.5Z', SAGE) +
    path('M19.5 26 H28.5 V32 H19.5Z', CREAM, " stroke-width='1.6'") + dot(24, 29, 1.2, RED))

ICONS['aroma'] = badge(LAV,
    path('M24 18 V21') +
    path('M24 10.5 Q28 14.5 24 17.5 Q20 14.5 24 10.5Z', GOLD, " stroke-width='1.6'") +
    path('M16.5 24 Q16.5 21 19.5 21 H28.5 Q31.5 21 31.5 24 V36.5 H16.5Z', CREAM) +
    "<rect x='16.5' y='30' width='15' height='3' fill='" + ROSE + "' stroke='none'/>" +
    path('M34 15 Q32 12.5 34 10 M13.5 16 Q11.5 13.5 13.5 11', '', " stroke-width='1.5'"))

ICONS['tea'] = badge(SAGE,
    path('M14 27 L9.5 21 L8 21.5') +
    path('M34 24 Q39.5 24 39.5 28.5 Q39.5 32 33 33') +
    path('M14 24.5 H34 Q34.5 36 24 36 Q13.5 36 14 24.5Z', CREAM) +
    path('M16 24.5 Q24 16.5 32 24.5Z', CREAM) + circ(24, 18.5, 2, GOLD, " stroke-width='1.6'") +
    path('M21 30.5 Q24 26 27.5 28.5 Q25 33 21 30.5Z', GREEN, " stroke-width='1.3'"))

ICONS['book'] = badge(PEACH,
    "<rect x='11' y='29' width='26' height='7' rx='1.5' fill='" + RED + "'/>" +
    "<rect x='13' y='22' width='23' height='7' rx='1.5' fill='" + GOLD + "'/>" +
    "<rect x='12' y='15' width='21' height='7' rx='1.5' fill='" + CREAM + "'/>" +
    path('M30 15.5 V21.5 M33 22.5 V28.5 M34 29.5 V35.5', '', " stroke-width='1.4'") +
    path('M17 18.5 H24', '', f" stroke='{BLUE}' stroke-width='1.8'"))

ICONS['interior'] = badge(SKY,
    path('M24 24 V35 M17.5 36 H30.5') +
    path('M17.5 12 H30.5 L35 24 H13Z', GOLD) +
    dot(24, 25.5, 1.4, CREAM))

ICONS['hobby'] = badge(YEL,
    path('M17 18 L19 14 H26 L28 18', CREAM) +
    "<rect x='10.5' y='18' width='27' height='17' rx='3' fill='" + CREAM + "'/>" +
    circ(24, 26.5, 6, SKY) + circ(24, 26.5, 2.4, '', " stroke-width='1.6'") +
    dot(33, 22, 1.4, RED) + path('M13.5 22 H16.5', '', " stroke-width='1.6'"))

ICONS['travel'] = badge(SAGE,
    path('M20 17.5 V14 Q20 12.5 21.5 12.5 H26.5 Q28 12.5 28 14 V17.5') +
    "<rect x='13' y='17.5' width='22' height='17' rx='3' fill='" + GOLD + "'/>" +
    path('M19 18 V34 M29 18 V34', '', f" stroke='{RED}' stroke-width='2.2'") +
    dot(17, 37.5, 1.6) + dot(31, 37.5, 1.6))

ICONS['sweets'] = badge(LAV,
    circ(24, 24, 12, GOLD) +
    path(scallop_d(24, 24, 8.5, 9, 0.9), ROSE, " stroke-width='1.6'") +
    circ(24, 24, 3.5, LAV) +
    path('M18.5 18.5 L19.5 20 M27 17 L28.5 17.5 M30 26 L30 27.5 M19 28.5 L20.5 29.5 M24 30.5 L25.5 30', '',
         f" stroke='{CREAM}' stroke-width='1.6'"))

ICONS['beauty'] = badge(PEACH,
    path('M16.5 11.5 H31.5 L29.5 30 H18.5Z', CREAM) +
    path('M17 14.5 H31', '', " stroke-width='1.4'") +
    "<rect x='19' y='30' width='10' height='6.5' rx='1.5' fill='" + ROSE + "'/>" +
    path('M21 19.5 H27 M21.5 23.5 H26.5', '', f" stroke='{ROSE}' stroke-width='1.8'") +
    path(sparkle_d(35.5, 22, 3.4), GOLD, " stroke-width='1.3'"))

ICONS['goods'] = badge(SKY,
    path('M18 19 Q11.5 25 13.5 32.5 Q15.5 37.5 24 37.5 Q32.5 37.5 34.5 32.5 Q36.5 25 30 19Z', PEACH) +
    path('M18.5 18 L15.5 12.5 Q20 14 24 12 Q28 14 32.5 12.5 L29.5 18', PEACH) +
    path('M17.5 19 Q24 21 30.5 19', '', f" stroke='{RED}' stroke-width='2'") +
    path(star_d(24, 28.5, 4.5, 2), GOLD, " stroke-width='1.4'"))

# ---------- リンクカード ----------
ICONS['compass'] = badge(SKY,
    circ(24, 24, 13, CREAM) +
    path('M24 15 L26.5 24 H21.5Z', RED, " stroke-width='1.6'") + path('M24 33 L26.5 24 H21.5Z', K, " stroke-width='1.6'") +
    path('M15 24 H18 M30 24 H33 M24 11 V12.5 M24 35.5 V37', '', " stroke-width='1.6'") + dot(24, 24, 1.3, CREAM))

ICONS['dream'] = badge(LAV,
    path('M20 9.5 A9 9 0 1 0 30 21 A7 7 0 0 1 20 9.5Z', GOLD) +
    path('M15 35.5 Q10 35.5 10 31.5 Q10 27.5 14.5 27.5 Q15.5 22.5 21 23.5 Q24 19.5 29 22.5 Q33.5 22 34.5 26.5 '
         'Q38.5 27 38.5 31 Q38.5 35.5 34 35.5Z', CREAM) +
    path('M33 11 H37 L33 16 H37', '', " stroke-width='1.6'"))

ICONS['mbti'] = badge(YEL,
    path('M12 16 H18.5 A4 4 0 1 1 25.5 16 H32 V21.5 A4 4 0 1 1 32 28.5 V35 H12 V28.5 A4 4 0 1 0 12 21.5Z', SKY) +
    dot(19, 27, 1.4) + dot(25, 27, 1.4) + path('M20.5 30.5 Q22 31.7 23.5 30.5', '', " stroke-width='1.6'"))

ICONS['kokoro'] = badge(PEACH,
    path(heart_d(24, 24.5, 11.5), ROSE) +
    path('M24 15.5 L27 25 H21Z', RED, " stroke-width='1.6'") + path('M24 33 L27 25 H21Z', CREAM, " stroke-width='1.6'") +
    dot(24, 25, 1.2, K))

ICONS['card'] = badge(SAGE,
    "<g transform='rotate(-8 24 24)'>" +
    "<rect x='12' y='14' width='24' height='21' rx='2' fill='" + CREAM + "'/>" +
    path(star_d(24, 22.5, 5.5, 2.4), GOLD, " stroke-width='1.6'") +
    path('M18 30.5 H30', '', f" stroke='{ROSE}' stroke-width='2'") + "</g>" +
    dot(10, 15, 1.4, RED) + dot(38, 32, 1.4, BLUE) + dot(36.5, 12, 1.3, GOLD))

ICONS['calendar-prev'] = badge(SKY,
    cal(12, 13, 24, 23) + path('M29.5 28.5 H18.5 M22.5 24.5 L18.5 28.5 L22.5 32.5', '', f" stroke='{BLUE}' stroke-width='2.4'"))

ICONS['calendar-next'] = badge(SKY,
    cal(12, 13, 24, 23) + path('M18.5 28.5 H29.5 M25.5 24.5 L29.5 28.5 L25.5 32.5', '', f" stroke='{BLUE}' stroke-width='2.4'"))

ICONS['omikuji'] = badge(YEL,
    "<g transform='rotate(-7 24 24)'>" +
    "<rect x='16.5' y='9.5' width='15' height='29' rx='1.5' fill='" + CREAM + "'/>" +
    "<rect x='20.5' y='13' width='7' height='8' rx='1' fill='" + RED + "' stroke-width='1.6'/>" +
    path('M20.5 24.5 V34.5 M24 24.5 V31 M27.5 24.5 V34.5', '', " stroke-width='1.5'") + "</g>" +
    path(sparkle_d(36.5, 15, 3.4), GOLD, " stroke-width='1.3'"))

# 名前の並び（プレビュー用のまとまり）
GROUPS = [
    ('12星座', ['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 'libra', 'scorpio', 'sagittarius',
              'capricorn', 'aquarius', 'pisces']),
    ('季節', ['spring', 'summer', 'autumn', 'winter']),
    ('占いの種類', ['kyusei', 'eto', 'shichu', 'shuku', 'maya', 'suhi', 'animal', 'bio']),
    ('見出し', ['nature', 'koyomi', 'mono', 'compat', 'famous', 'fate', 'work', 'love', 'money', 'health', 'people',
              'grow', 'stars', 'season', 'graph', 'month', 'action', 'omamori', 'gift', 'cake', 'year', 'next',
              'letter', 'links', 'about', 'today']),
    ('品物', ['stationery', 'plant', 'flower', 'tableware', 'kitchen', 'fashion', 'shoes', 'accessory', 'stone',
            'bag', 'aroma', 'tea', 'book', 'interior', 'hobby', 'travel', 'sweets', 'beauty', 'goods']),
    ('リンクカード', ['compass', 'dream', 'mbti', 'kokoro', 'card', 'calendar-prev', 'calendar-next', 'omikuji']),
]


def data_uri(svg):
    s = ' '.join(svg.split())  # 改行・連続空白をつぶす
    assert '"' not in s and '\\' not in s
    s = s.replace('%', '%25').replace('#', '%23').replace('<', '%3C').replace('>', '%3E')
    return 'data:image/svg+xml,' + s


def css():
    out = ['/* 人生予報 2027年版 誕生日占い：自前アイコン（fh-b27-ic）。生成元: work/scripts/icons.py（手で直さない） */',
           '.fh-b27-ic{display:inline-block;width:1em;height:1em;background:no-repeat center/contain;'
           'vertical-align:middle;flex:0 0 auto}']
    for name, svg in ICONS.items():
        out.append(f'.fh-b27-ic-{name}{{background-image:url("{data_uri(svg)}")}}')
    text = '\n'.join(out) + '\n'
    assert '\\' not in text
    return text


def preview_html():
    def grid():
        parts = []
        for title, names in GROUPS:
            parts.append(f'<h2>{title}（{len(names)}）</h2><div class="g">')
            for nm in names:
                parts.append(f'<div class="c"><i class="fh-b27-ic fh-b27-ic-{nm}" style="font-size:32px"></i>'
                             f'<i class="fh-b27-ic fh-b27-ic-{nm}" style="font-size:64px"></i><span>{nm}</span></div>')
            parts.append('</div>')
        return ''.join(parts)
    g = grid()
    return f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>アイコン一覧</title>
<link rel="stylesheet" href="../../scripts/templates/fh-b27-icons.css">
<style>
body{{margin:0;font-family:sans-serif}}
section{{padding:16px 20px}}
#navy{{background:#1F2638;color:#ECE7DA}}
#cream{{background:#F7F1E3;color:#2E2A26}}
h1{{font-size:18px;margin:0 0 8px}} h2{{font-size:14px;margin:14px 0 6px}}
.g{{display:grid;grid-template-columns:repeat(auto-fill,minmax(118px,1fr));gap:8px}}
.c{{display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-size:11px}}
.c span{{flex-basis:100%}}
.inline{{font-size:16px}}
</style></head><body>
<section id="navy"><h1>紺の背景（#1F2638）</h1>
<p class="inline"><i class="fh-b27-ic fh-b27-ic-love"></i> 恋愛運　<i class="fh-b27-ic fh-b27-ic-work"></i> 仕事運　<i class="fh-b27-ic fh-b27-ic-money"></i> 金運（本文16pxの中に置いた例）</p>
{g}</section>
<section id="cream"><h1>クリームの背景（#F7F1E3）</h1>
<p class="inline"><i class="fh-b27-ic fh-b27-ic-love"></i> 恋愛運　<i class="fh-b27-ic fh-b27-ic-work"></i> 仕事運　<i class="fh-b27-ic fh-b27-ic-money"></i> 金運（本文16pxの中に置いた例）</p>
{g}</section>
</body></html>
'''


def main():
    text = css()
    os.makedirs(os.path.dirname(CSS_PATH), exist_ok=True)
    with open(CSS_PATH, 'w', encoding='utf-8') as f:
        f.write(text)
    os.makedirs(os.path.dirname(PREVIEW_PATH), exist_ok=True)
    with open(PREVIEW_PATH, 'w', encoding='utf-8') as f:
        f.write(preview_html())
    names = [nm for _, g in GROUPS for nm in g]
    missing = [nm for nm in names if nm not in ICONS]
    extra = [nm for nm in ICONS if nm not in names]
    big = [(nm, len(s)) for nm, s in ICONS.items() if len(s) > 900]
    print(f'icons: {len(ICONS)}  css: {len(text.encode("utf-8"))} bytes  -> {CSS_PATH}')
    print(f'preview -> {os.path.normpath(PREVIEW_PATH)}')
    if missing or extra:
        print('missing:', missing, 'extra:', extra)
    if big:
        print('over 900 bytes:', big)


if __name__ == '__main__':
    main()
