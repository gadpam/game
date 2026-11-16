"""
Манхва-леттеринг и межкадровые реплики («Пока повременим»).
Референсы: Solo Leveling (REDICE Studio) + «Я притворился футбольным гением».

Полноразмерный мобильный масштаб (полоса 800 px → экран телефона ~390 px):
  · Живая речь (say)        — Play Regular 30–33 px, крупные манга-овалы 2×, контур 3.5 px, хвост Безье.
  · Выкрики (shout)         — Oswald Bold курсив 39–41 px, крупные burst-баблы 2× с хвостом-молнией.
  · Укол мысли (thought)    — Exo 2 Medium курсив 33–35 px, овал «уни-флэш» с тушевыми лучами.
  · Монолог героя (gutter)  — Exo 2 Medium/Light курсив 34–37 px, живая речь «здесь и сейчас»,
                              БЕЗ рамок и БЕЗ обводки, в чистом межкадровом поле.
  · Штамп места/минуты      — Oswald Medium 30–32 px, двойная манга-рамка.
  · Карточка соперника      — футбольная плашка игрока с клубной полоской (отделена от Системы).
  · SFX матча и Системы     — Oswald Bold 46–62 px (в т.ч. голубой «ДЗИ-ИНЬ!» открытия окна SL).

Все исходники ch1/* остаются нетронутыми. Автопроверки: глифы, поля, пересечения, запретные зоны.
"""
import math
from pathlib import Path
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W = 800
PAPER = (246, 245, 241)
DARK = (5, 8, 15)

FONTS = {
    'eb': 'fonts/Exo2-Bold.ttf',
    'em': 'fonts/Exo2-Medium.ttf',
    'el': 'fonts/Exo2-Light.ttf',
    'ob': 'fonts/Oswald-Bold.ttf',
    'om': 'fonts/Oswald-Medium.ttf',
    'pr': 'fonts/Play-Regular.ttf',
}
_FC = {}
_CMAPS = {}
for _k, _path in FONTS.items():
    _s = set()
    for _t in TTFont(_path)['cmap'].tables:
        _s |= set(_t.cmap.keys())
    _CMAPS[_k] = _s


def LF(key, size):
    k = (key, size)
    if k not in _FC:
        _FC[k] = ImageFont.truetype(FONTS[key], size)
    return _FC[k]


def check_glyphs(text, fkey):
    cm = _CMAPS[fkey]
    for ch in text:
        if ch not in ' \n' and ord(ch) not in cm:
            raise ValueError(f'глифа {ch!r} (U+{ord(ch):04X}) нет в {FONTS[fkey]}: «{text}»')


def render_italic(lines, fkey='em', size=35, fill=(20, 25, 32, 255),
                  shear=0.14, line_gap=13, stroke_w=0, stroke_col=(0, 0, 0, 255),
                  align='center', ss=2):
    """Рендерит многострочный оптический курсив с 2× суперсэмплингом."""
    for ln in lines:
        check_glyphs(ln, fkey)
    f = LF(fkey, size * ss)
    asc, desc = f.getmetrics()
    lh = asc + desc
    gap = line_gap * ss
    pad = (26 + stroke_w * 3) * ss
    widths = [int(math.ceil(f.getlength(ln))) for ln in lines]
    mw = max(widths) if widths else 10
    th = len(lines) * lh + max(0, len(lines) - 1) * gap
    cw, ch = mw + pad * 2, th + pad * 2

    txt = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
    td = ImageDraw.Draw(txt)
    y = pad
    for ln, lw in zip(lines, widths):
        if align == 'left':
            x = pad
        elif align == 'right':
            x = pad + mw - lw
        else:
            x = pad + (mw - lw) // 2
        td.text((x, y), ln, font=f, fill=fill)
        y += lh + gap

    if abs(shear) > 1e-4:
        shift = int(abs(shear) * ch) + 10
        nw = cw + shift
        txt = txt.transform(
            (nw, ch), Image.AFFINE,
            (1, shear, -shift if shear > 0 else 0, 0, 1, 0),
            resample=Image.BICUBIC,
        )

    if stroke_w > 0:
        _, _, _, a = txt.split()
        k = stroke_w * ss * 2 + 1
        if k % 2 == 0:
            k += 1
        dil = a.filter(ImageFilter.MaxFilter(k)).filter(ImageFilter.GaussianBlur(0.9))
        st = Image.new('RGBA', txt.size, stroke_col[:3] + (0,))
        sa = dil.point(lambda p: min(255, int(p * (stroke_col[3] / 255.0) * 1.18)))
        st.putalpha(sa)
        txt = Image.alpha_composite(st, txt)

    bb = txt.getbbox()
    if bb:
        txt = txt.crop((max(0, bb[0] - 4), max(0, bb[1] - 4),
                        min(txt.width, bb[2] + 4), min(txt.height, bb[3] + 4)))
    return txt.resize((max(1, txt.width // ss), max(1, txt.height // ss)), Image.LANCZOS)


def _quad_pts(p0, p1, p2, n=28):
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        pts.append((u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
                    u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]))
    return pts


def _check_box(tag, box, boxes, keepouts, w, h, margin=10):
    x0, y0, x1, y1 = box
    if x0 < margin or x1 > w - margin or y0 < margin or y1 > h - margin:
        raise ValueError(f'{tag}: блок выходит за поля ({w}×{h}): {box}')
    for otag, ob in boxes:
        if x0 < ob[2] + 4 and ob[0] < x1 + 4 and y0 < ob[3] + 4 and ob[1] < y1 + 4:
            raise ValueError(f'{tag} пересекается с {otag}: {box} / {ob}')
    for kname, kb in keepouts:
        if x0 < kb[2] and kb[0] < x1 and y0 < kb[3] and kb[1] < y1:
            raise ValueError(f'{tag} задевает зону «{kname}»: {box} / {kb}')
    boxes.append((tag, box))


# ══════════════════════════════════════════════════════════════════
# ПРИМИТИВЫ ВНУТРИ КАДРА (1.5× КРУПНЫЙ МАСШТАБ, 2× СУПЕРСЭМПЛИНГ)
# ══════════════════════════════════════════════════════════════════
def stamp(im, xy, text, boxes, keepouts, tag='stamp', size=31, center_x=False):
    ss = 2
    s = ' '.join(list(text)) if len(text) <= 3 else text
    check_glyphs(s, 'om')
    f = LF('om', size * ss)
    bb = f.getbbox(s)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    px, py = 22 * ss, 12 * ss
    bw, bh = tw + px * 2, th + py * 2
    pad = 8 * ss
    lay = Image.new('RGBA', (bw + pad * 2, bh + pad * 2), (0, 0, 0, 0))
    sh = Image.new('RGBA', lay.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([pad + 2, pad + 5, pad + bw + 2, pad + bh + 5], fill=(10, 14, 20, 82))
    lay = Image.alpha_composite(lay, sh.filter(ImageFilter.GaussianBlur(5)))
    d = ImageDraw.Draw(lay)
    d.rectangle([pad, pad, pad + bw, pad + bh], fill=(252, 252, 250, 248), outline=(16, 20, 26, 255), width=5)
    d.rectangle([pad + 9, pad + 9, pad + bw - 9, pad + bh - 9], outline=(16, 20, 26, 125), width=2)
    d.text((pad + px - bb[0], pad + py - bb[1]), s, font=f, fill=(14, 18, 24, 255))
    out = lay.resize((lay.width // ss, lay.height // ss), Image.LANCZOS)
    x = (im.width - out.width) // 2 if center_x else xy[0]
    y = xy[1]
    box = (x, y, x + out.width, y + out.height)
    _check_box(tag, box, boxes, keepouts, im.width, im.height, margin=10)
    im.alpha_composite(out, (x, y))


def player_tag(im, xy, name, role, boxes, keepouts, tag='ptag', accent=(112, 54, 48)):
    """Лаконичная футбольная карточка представления соперника (не путать с окном Системы)."""
    ss = 2
    check_glyphs(name, 'ob')
    check_glyphs(role, 'em')
    fn = LF('ob', 32 * ss)
    fr = LF('em', 21 * ss)
    bn = fn.getbbox(name)
    br = fr.getbbox(role)
    nw, nh = bn[2] - bn[0], bn[3] - bn[1]
    rw, rh = br[2] - br[0], br[3] - br[1]
    bar_w = 10 * ss
    px, py, gap = 18 * ss, 13 * ss, 7 * ss
    bw = bar_w + px * 2 + max(nw, rw)
    bh = py * 2 + nh + gap + rh
    pad = 8 * ss
    lay = Image.new('RGBA', (bw + pad * 2, bh + pad * 2), (0, 0, 0, 0))
    sh = Image.new('RGBA', lay.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([pad + 3, pad + 6, pad + bw + 3, pad + bh + 6], fill=(8, 12, 18, 95))
    lay = Image.alpha_composite(lay, sh.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(lay)
    d.rectangle([pad, pad, pad + bw, pad + bh], fill=(250, 249, 246, 244), outline=(20, 24, 30, 255), width=4)
    d.rectangle([pad + 2, pad + 2, pad + bar_w, pad + bh - 2], fill=accent + (255,))
    tx = pad + bar_w + px
    d.text((tx - bn[0], pad + py - bn[1]), name, font=fn, fill=(16, 20, 26, 255))
    d.text((tx - br[0], pad + py + nh + gap - br[1]), role, font=fr, fill=(68, 72, 80, 255))
    out = lay.resize((lay.width // ss, lay.height // ss), Image.LANCZOS)
    x, y = xy
    box = (x, y, x + out.width, y + out.height)
    _check_box(tag, box, boxes, keepouts, im.width, im.height, margin=10)
    im.alpha_composite(out, (x, y))


def say(im, bubbles, tail_to, boxes, keepouts, tag='say', size=32, bend=0.18, offpanel=False):
    w, h = im.size
    ss = 2
    f = LF('pr', size * ss)
    asc, desc = f.getmetrics()
    lh = asc + desc
    gap = 8 * ss

    geoms = []
    for cx, cy, lines in bubbles:
        for ln in lines:
            check_glyphs(ln, 'pr')
        ws = [int(math.ceil(f.getlength(ln))) for ln in lines]
        tw = max(ws)
        th = len(lines) * lh + max(0, len(lines) - 1) * gap
        rx = int(tw * 0.65) + 34 * ss
        ry = int(th * 0.66) + 30 * ss
        ry = max(ry, int(rx * 0.56))
        geoms.append((cx * ss, cy * ss, rx, ry, lines, ws, th))

    for idx, (cx, cy, rx, ry, _, _, _) in enumerate(geoms):
        box = ((cx - rx) // ss, (cy - ry) // ss, (cx + rx) // ss, (cy + ry) // ss)
        _check_box(f'{tag}_{idx}', box, boxes, keepouts, w, h, margin=10)

    fill_m = Image.new('L', (w * ss, h * ss), 0)
    md = ImageDraw.Draw(fill_m)

    for i in range(len(geoms) - 1):
        ax, ay, _, _, _, _, _ = geoms[i]
        bx, by, _, _, _, _, _ = geoms[i + 1]
        dx, dy = bx - ax, by - ay
        dist = max(1.0, math.hypot(dx, dy))
        nx, ny = -dy / dist, dx / dist
        hw = 15 * ss
        md.polygon([(ax + nx * hw, ay + ny * hw), (ax - nx * hw, ay - ny * hw),
                    (bx - nx * hw, by - ny * hw), (bx + nx * hw, by + ny * hw)], fill=255)

    if tail_to is not None:
        src = geoms[0] if (offpanel and tail_to[1] * ss < geoms[0][1]) else geoms[-1]
        sx, sy, srx, sry, _, _, _ = src
        tx, ty = tail_to[0] * ss, tail_to[1] * ss
        ang = math.atan2(ty - sy, tx - sx)
        bx = sx + math.cos(ang) * srx * 0.72
        by = sy + math.sin(ang) * sry * 0.72
        dx, dy = tx - bx, ty - by
        dist = max(1.0, math.hypot(dx, dy))
        nx, ny = -dy / dist, dx / dist
        bw = 19 * ss
        p_l = (bx + nx * bw, by + ny * bw)
        p_r = (bx - nx * bw, by - ny * bw)
        ctrl = ((bx + tx) * 0.5 + nx * dist * bend, (by + ty) * 0.5 + ny * dist * bend)
        c1 = _quad_pts(p_l, (ctrl[0] + nx * bw * 0.28, ctrl[1] + ny * bw * 0.28), (tx, ty))
        c2 = _quad_pts((tx, ty), (ctrl[0] - nx * bw * 0.28, ctrl[1] - ny * bw * 0.28), p_r)
        md.polygon(c1 + c2, fill=255)

    for cx, cy, rx, ry, _, _, _ in geoms:
        md.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=255)

    outer = fill_m.filter(ImageFilter.MaxFilter(13))
    sh_m = outer.filter(ImageFilter.GaussianBlur(8))

    lay = Image.new('RGBA', (w * ss, h * ss), (0, 0, 0, 0))
    sh = Image.new('RGBA', lay.size, (10, 14, 20, 0))
    sh.putalpha(sh_m.point(lambda p: int(p * 0.20)))
    lay.alpha_composite(sh, (0, 5))

    border = Image.new('RGBA', lay.size, (16, 20, 26, 0))
    border.putalpha(outer)
    lay = Image.alpha_composite(lay, border)

    white = Image.new('RGBA', lay.size, (253, 253, 251, 0))
    white.putalpha(fill_m)
    lay = Image.alpha_composite(lay, white)

    td = ImageDraw.Draw(lay)
    for cx, cy, rx, ry, lines, ws, th in geoms:
        yy = cy - th // 2 - int(desc * 0.14)
        for ln, lw in zip(lines, ws):
            td.text((cx - lw // 2, yy), ln, font=f, fill=(14, 18, 24, 255))
            yy += lh + gap

    im.alpha_composite(lay.resize((w, h), Image.LANCZOS))


def shout(im, center, lines, boxes, keepouts, tail_to=None, tag='shout', size=40, spikes=26):
    w, h = im.size
    ss = 2
    txt = render_italic(lines, fkey='ob', size=size, fill=(14, 16, 20, 255),
                        shear=0.13, line_gap=7, stroke_w=0, align='center', ss=2)
    tw, th = txt.width * ss, txt.height * ss
    cx, cy = center[0] * ss, center[1] * ss
    rx_in = int(tw * 0.62) + 30 * ss
    ry_in = int(th * 0.64) + 26 * ss
    rx_out = rx_in + 32 * ss
    ry_out = ry_in + 28 * ss

    box = ((cx - rx_out) // ss, (cy - ry_out) // ss, (cx + rx_out) // ss, (cy + ry_out) // ss)
    _check_box(tag, box, boxes, keepouts, w, h, margin=8)

    pts = []
    for i in range(spikes):
        a0 = 2 * math.pi * i / spikes
        a1 = 2 * math.pi * (i + 1) / spikes
        k0 = 1.0 + 0.14 * math.sin(i * 2.7 + 0.6)
        k1 = 1.0 + 0.14 * math.sin((i + 1) * 2.7 + 0.6)
        p0 = (cx + math.cos(a0) * rx_out * k0, cy + math.sin(a0) * ry_out * k0)
        p1 = (cx + math.cos(a1) * rx_out * k1, cy + math.sin(a1) * ry_out * k1)
        am = 0.5 * (a0 + a1)
        ctrl = (cx + math.cos(am) * rx_in * 0.88, cy + math.sin(am) * ry_in * 0.88)
        pts.extend(_quad_pts(p0, ctrl, p1, n=8)[:-1])

    fill_m = Image.new('L', (w * ss, h * ss), 0)
    md = ImageDraw.Draw(fill_m)
    md.polygon(pts, fill=255)

    if tail_to is not None:
        tx, ty = tail_to[0] * ss, tail_to[1] * ss
        ang = math.atan2(ty - cy, tx - cx)
        bx = cx + math.cos(ang) * rx_in * 0.84
        by = cy + math.sin(ang) * ry_in * 0.84
        dx, dy = tx - bx, ty - by
        dist = max(1.0, math.hypot(dx, dy))
        nx, ny = -dy / dist, dx / dist
        poly = [
            (bx + nx * 19 * ss, by + ny * 19 * ss),
            (bx + dx * 0.48 + nx * 20 * ss, by + dy * 0.48 + ny * 20 * ss),
            (tx, ty),
            (bx + dx * 0.54 - nx * 15 * ss, by + dy * 0.54 - ny * 15 * ss),
            (bx + dx * 0.36 - nx * 7 * ss, by + dy * 0.36 - ny * 7 * ss),
            (bx - nx * 16 * ss, by - ny * 16 * ss),
        ]
        md.polygon(poly, fill=255)

    outer = fill_m.filter(ImageFilter.MaxFilter(13))
    lay = Image.new('RGBA', (w * ss, h * ss), (0, 0, 0, 0))
    bd = Image.new('RGBA', lay.size, (14, 16, 20, 0))
    bd.putalpha(outer)
    wh = Image.new('RGBA', lay.size, (253, 253, 251, 0))
    wh.putalpha(fill_m)
    lay = Image.alpha_composite(bd, wh)
    im.alpha_composite(lay.resize((w, h), Image.LANCZOS))
    im.alpha_composite(txt, (center[0] - txt.width // 2, center[1] - txt.height // 2))


def thought(im, center, lines, boxes, keepouts, tag='thought', size=34):
    w, h = im.size
    ss = 2
    txt = render_italic(lines, fkey='em', size=size, fill=(16, 20, 26, 255),
                        shear=0.16, line_gap=8, stroke_w=0, align='center', ss=2)
    cx, cy = center[0] * ss, center[1] * ss
    rx = int(txt.width * ss * 0.66) + 32 * ss
    ry = int(txt.height * ss * 0.72) + 28 * ss
    rim = 20 * ss

    box = ((cx - rx - rim) // ss, (cy - ry - rim) // ss,
           (cx + rx + rim) // ss, (cy + ry + rim) // ss)
    _check_box(tag, box, boxes, keepouts, w, h, margin=8)

    lay = Image.new('RGBA', (w * ss, h * ss), (0, 0, 0, 0))
    core = Image.new('RGBA', lay.size, (0, 0, 0, 0))
    ImageDraw.Draw(core).ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(253, 253, 251, 248))
    lay = Image.alpha_composite(lay, core.filter(ImageFilter.GaussianBlur(6)))

    d = ImageDraw.Draw(lay)
    n_rays = 112
    for i in range(n_rays):
        a = 2 * math.pi * i / n_rays
        r0k = 0.88 + 0.05 * math.sin(i * 3.1)
        r1k = 1.0 + 0.06 * math.cos(i * 5.3)
        x0 = cx + math.cos(a) * rx * r0k
        y0 = cy + math.sin(a) * ry * r0k
        x1 = cx + math.cos(a) * (rx + rim * r1k)
        y1 = cy + math.sin(a) * (ry + rim * r1k)
        al = 205 if i % 2 == 0 else 130
        d.line([(x0, y0), (x1, y1)], fill=(18, 22, 28, al), width=3)

    im.alpha_composite(lay.resize((w, h), Image.LANCZOS))
    im.alpha_composite(txt, (center[0] - txt.width // 2, center[1] - txt.height // 2))


def sfx(im, center, text, boxes, keepouts, tag='sfx', size=54, angle=-9.0, mode='light'):
    """Выразительный манга-SFX: 'light' (белый в туши), 'pulse' (глухой пульс), 'system' (циан SL)."""
    if mode == 'system':
        fill, scol = (226, 250, 255, 252), (12, 86, 168, 250)
    elif mode == 'pulse':
        fill, scol = (242, 244, 248, 238), (22, 26, 34, 238)
    else:
        fill, scol = (250, 251, 253, 248), (14, 18, 24, 248)
    art = render_italic([text], fkey='ob', size=size, fill=fill,
                        shear=0.20, stroke_w=5, stroke_col=scol, ss=2)
    if mode == 'system':
        pad = 16
        gl = Image.new('RGBA', (art.width + pad * 2, art.height + pad * 2), (0, 0, 0, 0))
        gl.alpha_composite(art, (pad, pad))
        _, _, _, a = gl.split()
        aura = Image.new('RGBA', gl.size, (48, 196, 255, 0))
        aura.putalpha(a.filter(ImageFilter.GaussianBlur(9)))
        art = Image.alpha_composite(aura, gl)
    if abs(angle) > 0.1:
        art = art.rotate(-angle, resample=Image.BICUBIC, expand=True)
    x = center[0] - art.width // 2
    y = center[1] - art.height // 2
    box = (x, y, x + art.width, y + art.height)
    _check_box(tag, box, boxes, keepouts, im.width, im.height, margin=8)
    im.alpha_composite(art, (x, y))


# ══════════════════════════════════════════════════════════════════
# КАРТА РЕПЛИК, КАРТОЧЕК СОПЕРНИКОВ И SFX ВНУТРИ КАДРОВ ГЛ. 1
# ══════════════════════════════════════════════════════════════════
def apply_ch1_frame(num, im_rgb):
    im = im_rgb.convert('RGBA')
    boxes = []

    if num == '02':  # утренний двор у базы, автобус, трое старших со стаканчиками
        keep = [('ветров', (120, 530, 415, 1340)), ('старшие', (445, 600, 765, 1100))]
        say(im, [
            (462, 152, ['А это чей', 'малой?']),
            (592, 378, ['С шестнадцатых', 'взяли. Людей', 'не хватает.']),
        ], tail_to=(620, 588), boxes=boxes, keepouts=keep, tag='02_older', size=31, bend=-0.14)

    elif num == '03':  # утренний автобус на выезд
        keep = [('ветров', (95, 510, 620, 1330)), ('соседи', (460, 520, 795, 1280))]
        stamp(im, (30, 32), 'ВТОРАЯ ЛИГА · 22-Й ТУР', boxes, keep, '03_st', size=31)

    elif num == '04':  # гостевая раздевалка, лист ЗАЯВКА (18) / РЕЧНИК - ТОРПЕДО-2 / 18. ВЕТРОВ
        keep = [('доска и герой', (215, 515, 580, 1185))]
        stamp(im, (30, 32), 'ГОСТЕВАЯ РАЗДЕВАЛКА', boxes, keep, '04_st', size=31)

    elif num == '05':  # скамейка до матча, запасные в олимпийках смотрят на соперника
        keep = [('ветров', (55, 520, 495, 1270)), ('запасные', (300, 595, 600, 1060)),
                ('разминка', (590, 620, 795, 860))]
        say(im, [
            (435, 148, ['Корнеев в старте.', 'И Жук с ним.']),
            (555, 386, ['Блин… Опять', 'весь тайм без мяча', 'бегать.']),
        ], tail_to=(485, 584), boxes=boxes, keepouts=keep, tag='05_sub', size=29, bend=0.15)

    elif num == '06':  # ПРЕДСТАВЛЕНИЕ СОПЕРНИКОВ: пара центральных «Речника» Корнеев и Жук
        keep = [('корнеев_голова', (245, 360, 415, 565)), ('жук_голова', (515, 425, 665, 610))]
        say(im, [
            (345, 186, ['Пацанов привезли.', 'Сразу накрываем — голову', 'поднять не даём!']),
        ], tail_to=(332, 354), boxes=boxes, keepouts=keep, tag='06_cap', size=30, bend=-0.12)
        player_tag(im, (26, 1188), 'КОРНЕЕВ', 'опорник «Речника» · 27 лет',
                   boxes, keep, tag='06_p1')
        player_tag(im, (382, 1296), 'ЖУК', 'полузащитник «Речника» · 22 года',
                   boxes, keep, tag='06_p2')

    elif num == '07':  # чистая скамейка, начало 1-го тайма (Системы ЕЩЁ НЕТ!)
        keep = [('ветров', (100, 520, 550, 1280))]
        stamp(im, (30, 32), '1-Й ТАЙМ', boxes, keep, '07_st', size=31)

    elif num == '08':  # 20′ Корнеев продавливает середину поля
        keep = [('единоборство', (110, 465, 740, 1065))]
        stamp(im, (30, 32), '20′', boxes, keep, '08_st', size=32)
        shout(im, (475, 1228), ['БЛИЖЕ К НЕМУ!', 'НЕ ПЯТЬСЯ!'],
              boxes, keep, tail_to=(215, 1185), tag='08_sh', size=39)

    elif num == '09':  # 30′ · 1:0 вратарь в отчаянном прыжке тянется за мячом в нижний угол
        keep = [('ворота и прыжок', (85, 455, 710, 880)), ('защитник', (470, 405, 798, 1370))]
        stamp(im, (30, 32), '30′ · 1 : 0', boxes, keep, '09_st', size=32)
        sfx(im, (182, 955), 'ВШХ!', boxes, keep, tag='09_sfx', size=54, angle=-9.0)

    elif num == '10':  # 58′ · 2:0 второй пропущенный гол под ливнем, наши выдохлись
        keep = [('левый_игрок', (25, 520, 225, 980)), ('соперники', (205, 535, 420, 815)),
                ('ворота', (415, 515, 790, 725)), ('шатский', (510, 505, 785, 1215)),
                ('мачта', (650, 70, 785, 515))]
        stamp(im, (30, 32), '58′ · 2 : 0', boxes, keep, '10_st', size=32)
        say(im, [
            (412, 292, ['Не успеваем…', 'Совсем сели.']),
        ], tail_to=(568, 498), boxes=boxes, keepouts=keep, tag='10_shat', size=31, bend=-0.12)

    elif num == '11':  # 71′ полузащитник Шатский почувствовал дискомфорт в задней поверхности бедра
        keep = [('скамейка_тренер', (10, 320, 345, 710)), ('шатский', (300, 340, 695, 1100))]
        stamp(im, (28, 28), '71′', boxes, keep, '11_st', size=32)
        say(im, [
            (504, 152, ['Тренер, заднюю тянет!', 'Рывок не сделаю!']),
        ], tail_to=(452, 336), boxes=boxes, keepouts=keep, tag='11_inj', size=30, bend=0.14)

    elif num == '12':  # 72′ выход на замену вместо Шатского
        keep = [('ветров', (275, 480, 520, 1270)), ('тренер и лавка', (10, 535, 355, 900))]
        stamp(im, (28, 28), '72′', boxes, keep, '12_st', size=32)
        sfx(im, (654, 84), 'ФЬЮ-ИТЬ!', boxes, keep, tag='12_sfx', size=45, angle=-7.0)
        say(im, [
            (320, 106, ['Ветров! Вместо', 'Шатского!']),
            (524, 342, ['Играй просто: принял —', 'сразу в пас! Под', 'Корнеева не лезь!']),
        ], tail_to=(258, 524), boxes=boxes, keepouts=keep, tag='12_coach', size=29, bend=0.14)

    elif num == '13':  # 72′ ВЫШЕЛ НА ПОЛЕ: сильное волнение, пульс — и вспышка Системы!
        keep = [('ветров_голова', (270, 225, 555, 560)), ('ветров_тело', (215, 560, 620, 1390)),
                ('вспышка', (35, 365, 390, 445))]
        thought(im, (252, 118), ['Выдохни. Только', 'не привезти…'], boxes, keep, tag='13_th', size=31)
        sfx(im, (654, 152), 'ТУК-ТУК…', boxes, keep, tag='13_hb', size=42, angle=-6.0, mode='pulse')
        sfx(im, (132, 302), 'ДЗИ-ИНЬ!', boxes, keep, tag='13_sys', size=42, angle=-8.0, mode='system')

    elif num == '15':  # крупный план лица Ветрова под дождём: окно Системы отражается в глазах
        keep = [('лицо', (275, 175, 798, 1210)), ('партнёр', (10, 420, 320, 1120))]
        thought(im, (142, 108), ['Чего?..'], boxes, keep, tag='15_th', size=35)

    elif num == '16':  # 78′ подкат Ветрова в луже у бровки
        keep = [('подкат', (10, 725, 690, 1140)), ('соперник', (620, 515, 798, 1110))]
        stamp(im, (30, 32), '78′', boxes, keep, '16_st', size=32)
        sfx(im, (475, 622), 'ШХХХ!', boxes, keep, tag='16_sfx', size=54, angle=-10.0)
        shout(im, (475, 1274), ['ВО, ХОРОШ!', 'ТАК И ИГРАЙ!'],
              boxes, keep, tail_to=(320, 1146), tag='16_sh', size=40)

    elif num == '17':  # 88′ Жук и Корнеев вдвоём зажимают Ветрова
        keep = [('ветров', (10, 355, 440, 1210)), ('прессинг', (380, 445, 795, 1020))]
        stamp(im, (28, 28), '88′', boxes, keep, '17_st', size=32)
        thought(im, (202, 224), ['Чёрт, двое!'], boxes, keep, tag='17_th', size=34)
        shout(im, (574, 212), ['ГОРИШЬ!', 'ОТДАВАЙ!'],
              boxes, keep, tail_to=None, tag='17_sh', size=40)

    elif num == '18':  # 88′ крупный удар: бутса Жука вытыкает мяч
        keep = [('мяч и бутса', (215, 245, 535, 455))]
        sfx(im, (318, 162), 'ТК!', boxes, keep, tag='18_sfx', size=62, angle=-11.0)

    elif num == '20':  # 89′ пас низом в одно касание между Корнеевым и Жуком
        keep = [('ветров', (120, 330, 560, 1205)), ('мяч', (195, 1035, 355, 1208)),
                ('корнеев_голова', (70, 370, 270, 610)), ('жук_голова', (590, 350, 798, 620))]
        stamp(im, (30, 32), '89′', boxes, keep, '20_st', size=32)
        say(im, [
            (235, 214, ['В касание?!']),
        ], tail_to=(174, 414), boxes=boxes, keepouts=keep, tag='20_kor', size=31, bend=-0.12)
        sfx(im, (285, 1286), 'ТУК!', boxes, keep, tag='20_sfx', size=54, angle=-7.0)

    elif num == '21':  # раздевалка после матча, руки и бутылка воды
        keep = [('руки и бутылка', (10, 355, 790, 1060))]
        say(im, [
            (488, 182, ['Моемся быстро.', 'Через двадцать минут', 'выезжаем.']),
        ], tail_to=(432, 6), boxes=boxes, keepouts=keep, tag='21_coach',
            size=31, bend=-0.15, offpanel=True)

    return im.convert('RGB'), len(boxes)


# ══════════════════════════════════════════════════════════════════
# МЕЖКАДРОВЫЙ МОНОЛОГ (1.5× КРУПНЫЙ КЕГЛЬ 34–37 px, ЖИВАЯ РЕЧЬ)
# ══════════════════════════════════════════════════════════════════
def _make_fade(c0, c1, h):
    im = Image.new('RGB', (W, h), c0)
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / max(1, h - 1)
        s = t * t * (3.0 - 2.0 * t)
        c = tuple(int(round(c0[j] + (c1[j] - c0[j]) * s)) for j in range(3))
        d.line([(0, y), (W, y)], fill=c)
    return im


def render_gutter(bg_top, bg_bot, items, pad_top=74, pad_bot=78, item_gap=44, min_h=130):
    if not items:
        return _make_fade(bg_top, bg_bot, min_h) if bg_top != bg_bot else Image.new('RGB', (W, min_h), bg_top)

    seq = list(items)
    if bg_top != bg_bot and not any(it.get('kind') == 'fade' for it in seq):
        seq = [{'kind': 'fade', 'h': 160, 'pad_after': 56}] + seq

    cur_bg = bg_top
    segs = []

    def add_solid(h, col):
        if h > 0:
            segs.append(Image.new('RGB', (W, h), col))

    if seq[0].get('kind') != 'fade':
        add_solid(pad_top, cur_bg)

    for idx, it in enumerate(seq):
        kind = it.get('kind', 'mono')
        if kind == 'fade':
            add_solid(it.get('pad_before', 0), cur_bg)
            segs.append(_make_fade(cur_bg, bg_bot, it.get('h', 160)))
            cur_bg = bg_bot
            if idx < len(seq) - 1:
                add_solid(it.get('pad_after', 58), cur_bg)
            continue
        if kind == 'space':
            add_solid(it['h'], cur_bg)
            continue

        pos = it.get('pos', 'center')
        is_light = (0.299 * cur_bg[0] + 0.587 * cur_bg[1] + 0.114 * cur_bg[2]) > 128
        if kind == 'stamp':
            s = it['text']
            check_glyphs(s, 'om')
            ss = 2
            f = LF('om', 32 * ss)
            bb = f.getbbox(s)
            tw, th = bb[2] - bb[0], bb[3] - bb[1]
            px, py = 26 * ss, 13 * ss
            bw, bh = tw + px * 2, th + py * 2
            lay = Image.new('RGBA', (bw + 10, bh + 10), (0, 0, 0, 0))
            d = ImageDraw.Draw(lay)
            d.rectangle([5, 5, 5 + bw, 5 + bh], fill=(252, 252, 250, 255),
                        outline=(20, 24, 30, 255), width=5)
            d.rectangle([14, 14, 5 + bw - 9, 5 + bh - 9], outline=(20, 24, 30, 120), width=2)
            d.text((5 + px - bb[0], 5 + py - bb[1]), s, font=f, fill=(16, 20, 26, 255))
            art = lay.resize((lay.width // ss, lay.height // ss), Image.LANCZOS)
        elif kind == 'accent':
            raw = render_italic(it['lines'] if 'lines' in it else [it['text']],
                                fkey='eb', size=it.get('size', 42),
                                fill=(224, 249, 255, 255), shear=0.0, line_gap=12, ss=2)
            pad = 16
            art = Image.new('RGBA', (raw.width + pad * 2, raw.height + pad * 2), (0, 0, 0, 0))
            art.alpha_composite(raw, (pad, pad))
            _, _, _, a = art.split()
            gl = Image.new('RGBA', art.size, (52, 198, 255, 0))
            gl.putalpha(a.filter(ImageFilter.GaussianBlur(10)))
            art = Image.alpha_composite(gl, art)
        else:
            wkey = it.get('w', 'em')
            if is_light:
                ink = (18, 23, 30, 250) if wkey != 'el' else (48, 56, 68, 246)
            else:
                ink = (238, 246, 255, 250) if wkey != 'el' else (182, 204, 224, 245)
            align = {'left': 'left', 'right': 'right'}.get(pos, 'center')
            art = render_italic(it['lines'], fkey=wkey, size=it.get('size', 35),
                                fill=ink, shear=0.13, line_gap=13, stroke_w=0,
                                align=align, ss=2)

        if art.width > W - 64:
            raise ValueError(f'строка шире полосы ({art.width}px > {W - 64}px): {it}')
        row = Image.new('RGBA', (W, art.height), cur_bg + (255,))
        x = 56 if pos == 'left' else (W - 56 - art.width if pos == 'right' else (W - art.width) // 2)
        row.alpha_composite(art, (x, 0))
        segs.append(row.convert('RGB'))

        if idx < len(seq) - 1 and seq[idx + 1].get('kind') != 'fade':
            add_solid(item_gap, cur_bg)

    if seq[-1].get('kind') != 'fade':
        add_solid(pad_bot, cur_bg)

    total_h = sum(s.height for s in segs)
    if total_h < min_h:
        add_solid(min_h - total_h, cur_bg)
        total_h = min_h

    out = Image.new('RGB', (W, total_h), bg_top)
    yy = 0
    for s in segs:
        out.paste(s, (0, yy))
        yy += s.height
    return out


# ══════════════════════════════════════════════════════════════════
# ПАРТИТУРА ГЛАВЫ 1 (24 кадра: первый выезд, «Речник» и пара
# Корнеев–Жук, пробуждение Системы ТОЛЬКО на 72′ в момент сильного
# волнения, окна в стиле Solo Leveling, живая разговорная речь)
# ══════════════════════════════════════════════════════════════════
CH1_OPENING_GUTTER = dict(
    bg=(DARK, PAPER), pad_bot=84, item_gap=38, items=[
        {'kind': 'fade', 'h': 160, 'pad_after': 56},
        {'kind': 'stamp', 'text': 'ВИТЕБСК · НОЯБРЬ'},
        {'lines': ['Суббота, девять утра.', 'Первый выезд со взрослой командой.'], 'pos': 'center', 'size': 35, 'w': 'em'},
    ],
)

CH1_SCORE = [
    ('ch1/f02_room.jpg', '01', 1360, 3, 'paper', dict(
        bg=(PAPER, PAPER), pad_top=82, pad_bot=86, item_gap=42, items=[
            {'lines': ['В «Торпедо-2» меня подняли', 'только в среду — двое на карточках,', 'ещё один сломался.'], 'pos': 'left', 'size': 34, 'w': 'el'},
            {'lines': ['В пятнадцать лет туда просто так', 'не зовут. Дёрнули из юношей,', 'чтобы заявку закрыть.'], 'pos': 'right', 'size': 35, 'w': 'em'},
        ])),

    ('ch1/a02_yard.jpg', '02', 1420, 3, 'paper', dict(
        bg=(PAPER, PAPER), pad_top=82, pad_bot=86, item_gap=42, items=[
            {'lines': ['За три тренировки почти ни с кем', 'и не разговорился.'], 'pos': 'left', 'size': 34, 'w': 'el'},
            {'lines': ['Да и понятно — привезли пацана', 'на один тур, через неделю', 'вернут обратно.'], 'pos': 'right', 'size': 34, 'w': 'em'},
        ])),

    ('ch1/a03_bus_day.jpg', '03', 1340, 3, 'paper', dict(
        bg=(PAPER, PAPER), pad_top=84, pad_bot=88, item_gap=42, items=[
            {'lines': ['По юношам успеваешь принять,', 'поднять голову, выбрать пас.'], 'pos': 'left', 'size': 34, 'w': 'el'},
            {'lines': ['А тут мяч ещё катится —', 'в тебя уже летят плечом.'], 'pos': 'right', 'size': 35, 'w': 'em'},
        ])),

    ('ch1/k1_locker.jpg', '04', 1380, 3, 'paper', dict(
        bg=(PAPER, PAPER), pad_top=82, pad_bot=86, item_gap=40, items=[
            {'lines': ['Восемнадцатый. Самый последний.'], 'pos': 'left', 'size': 35, 'w': 'em'},
            {'lines': ['Понятно, что просижу в запасе —', 'а всё равно внутри потряхивает.'], 'pos': 'right', 'size': 34, 'w': 'el'},
        ])),

    ('ch1/a05_warmup.jpg', '05', 1380, 3, 'paper', dict(
        bg=(PAPER, PAPER), pad_top=82, pad_bot=80, item_gap=40, items=[
            {'kind': 'stamp', 'text': '«РЕЧНИК» — «ТОРПЕДО-2»'},
            {'lines': ['«Речник» идёт в тройке — дома у них', 'почти никто очки не забирает.'], 'pos': 'center', 'size': 34, 'w': 'em'},
        ])),

    ('ch1/a06_opponent.jpg', '06', 1420, 3, 'paper', dict(
        bg=(PAPER, PAPER), pad_top=84, pad_bot=88, item_gap=42, items=[
            {'lines': ['Тренер на разборе полчаса', 'про этих двоих говорил.'], 'pos': 'center', 'size': 34, 'w': 'el'},
            {'lines': ['Корнеев поиграл в первой лиге —', 'здоровый, от мяча не отодвинешь.'], 'pos': 'left', 'size': 34, 'w': 'em'},
            {'lines': ['А Жук носится весь матч', 'и сразу бросается в ноги.'], 'pos': 'right', 'size': 34, 'w': 'el'},
        ])),

    ('ch1/k2b_bench.jpg', '07', 1360, 3, 'paper', dict(
        bg=(PAPER, PAPER), pad_top=80, pad_bot=82, item_gap=38, items=[
            {'lines': ['Начали.'], 'pos': 'center', 'size': 36, 'w': 'em'},
            {'lines': ['С бровки всё ещё быстрее,', 'чем казалось на тренировке.'], 'pos': 'center', 'size': 34, 'w': 'el'},
        ])),

    ('ch1/n20_firsthalf.jpg', '08', 1380, 3, 'paper', dict(
        bg=(PAPER, PAPER), pad_top=80, pad_bot=84, item_gap=38, items=[
            {'lines': ['Двадцать минут — а мы центр поля', 'раза два перешли.'], 'pos': 'left', 'size': 35, 'w': 'em'},
            {'lines': ['Корнеев снимает почти всё,', 'что летит в центр.'], 'pos': 'right', 'size': 34, 'w': 'el'},
        ])),

    ('ch1/n30_goal_rain.jpg', '09', 1380, 3, 'paper', dict(
        bg=(PAPER, PAPER), pad_top=84, pad_bot=86, item_gap=42, items=[
            {'lines': ['Ну вот, доигрались.', 'Дали пробить вторым темпом —', 'по мокрой траве такой не вытащишь.'], 'pos': 'left', 'size': 34, 'w': 'em'},
            {'lines': ['До свистка кое-как дотерпели,', 'ушли на перерыв при 0:1.'], 'pos': 'right', 'size': 34, 'w': 'el'},
            {'kind': 'stamp', 'text': '2-Й ТАЙМ'},
            {'lines': ['В раздевалке тренер напихал за центр,', 'но после перерыва нас прижали', 'ещё сильнее.'], 'pos': 'center', 'size': 34, 'w': 'el'},
        ])),

    # 58′ · 2:0 и 71′ — дискомфорт у Шатского: живая подводка и причина выхода Ветрова
    ('ch1/a10_goal2.jpg', '10', 1380, 3, 'paper', dict(
        bg=(PAPER, PAPER), pad_top=84, pad_bot=88, item_gap=42, items=[
            {'lines': ['После перерыва нас растянули по ширине.', 'В центре всё время оставалась дыра.'], 'pos': 'left', 'size': 34, 'w': 'em'},
            {'lines': ['К семидесятой тренер бросил двоих вперёд.', 'Я так и сижу в олимпийке:', 'при 0:2 пацана точно не тронут.'], 'pos': 'right', 'size': 34, 'w': 'el'},
        ])),

    ('ch1/a11_discomfort.jpg', '11', 1260, 3, 'paper', dict(
        bg=(PAPER, PAPER), pad_top=84, pad_bot=88, item_gap=42, items=[
            {'lines': ['При 0:2 рисковать Шатским незачем —', 'впереди ещё два тура.'], 'pos': 'left', 'size': 34, 'w': 'el'},
            {'lines': ['В центр на лавке больше никого.', 'Тренер смотрит прямо на меня.'], 'pos': 'right', 'size': 36, 'w': 'em'},
        ])),

    # 72′ — ВЫХОД НА ЗАМЕНУ И ПЕРВОЕ ПРОБУЖДЕНИЕ СИСТЕМЫ НА ПИКЕ ВОЛНЕНИЯ
    ('ch1/k17_enter.jpg', '12', 1420, 3, 'paper', dict(
        bg=(PAPER, PAPER), pad_top=82, pad_bot=86, item_gap=42, items=[
            {'lines': ['Даже размяться не успел — скинул', 'олимпийку и сразу к боковой.'], 'pos': 'left', 'size': 35, 'w': 'em'},
            {'lines': ['Ноги деревянные от холода, горим 0:2,', 'а играть почти двадцать минут.'], 'pos': 'right', 'size': 34, 'w': 'el'},
        ])),

    ('ch1/a11_awakening.jpg', '13', 1400, 2, 'paper', dict(
        bg=(PAPER, DARK), pad_bot=88, item_gap=44, items=[
            {'kind': 'fade', 'h': 160, 'pad_after': 60},
            {'lines': ['Пульс стучит прямо в ушах.', 'Пальцы не слушаются.'], 'pos': 'center', 'size': 35, 'w': 'el'},
            {'lines': ['Шаг на поле — и прямо перед лицом', 'вспыхивает тонкая синяя щель.'], 'pos': 'center', 'size': 36, 'w': 'em'},
        ])),

    ('ch1/p07_quest.png', '14', 900, 3, 'dark', dict(
        bg=(DARK, DARK), min_h=104, items=[])),

    ('ch1/a13_eyes_rain.jpg', '15', 1240, 2, 'dark', dict(
        bg=(DARK, PAPER), pad_top=88, pad_bot=84, item_gap=44, items=[
            {'lines': ['Это ещё что такое?', 'Переволновался, что ли?'], 'pos': 'center', 'size': 36, 'w': 'em'},
            {'lines': ['Моргаю раз, другой — висит.', 'Парни бегут по местам,', 'никто ничего не видит.'], 'pos': 'center', 'size': 34, 'w': 'el'},
            {'kind': 'fade', 'h': 160, 'pad_before': 56, 'pad_after': 56},
            {'lines': ['Свисток — мяч уже в игре!', 'Потом разберусь, мне и без этого', 'сейчас ошибаться нельзя.'], 'pos': 'center', 'size': 35, 'w': 'em'},
        ])),

    ('ch1/n78_press.jpg', '16', 1420, 3, 'paper', dict(
        bg=(PAPER, PAPER), pad_top=82, pad_bot=86, item_gap=40, items=[
            {'lines': ['Фух… Есть первый отбор.', 'Сразу полегче стало.'], 'pos': 'left', 'size': 35, 'w': 'em'},
            {'lines': ['При 2:0 «Речник» уже не несётся', 'вперёд, но в центре всё равно', 'накрывают каждый приём.'], 'pos': 'right', 'size': 34, 'w': 'el'},
            {'lines': ['Ещё минут десять дотерпеть.', 'Принял — отдал, ничего лишнего.'], 'pos': 'center', 'size': 34, 'w': 'em'},
        ])),

    ('ch1/k3c_loss.jpg', '17', 1320, 3, 'paper', dict(
        bg=(PAPER, PAPER), min_h=60, items=[])),

    ('ch1/a14_poke.jpg', '18', 492, 5, 'paper', dict(
        bg=(PAPER, DARK), pad_bot=88, item_gap=44, items=[
            {'kind': 'fade', 'h': 155, 'pad_after': 58},
            {'lines': ['Принял перед своей штрафной — и затянул.', 'Лишние полсекунды искал,', 'кому отдать вперёд.'], 'pos': 'center', 'size': 35, 'w': 'em'},
            {'lines': ['Жук сразу ткнул носком,', 'а Корнеев оттёр корпусом.'], 'pos': 'center', 'size': 34, 'w': 'el'},
        ])),

    ('ch1/p23_fail.png', '19', 616, 3, 'dark', dict(
        bg=(DARK, PAPER), pad_top=88, item_gap=42, items=[
            {'lines': ['Пронесло — защитник успел вынести', 'за лицевую, третий не пустили.'], 'pos': 'center', 'size': 34, 'w': 'el'},
            {'lines': ['А перед глазами красным:', 'двадцать пять. Сняли единицу.'], 'pos': 'center', 'size': 35, 'w': 'em'},
            {'kind': 'fade', 'h': 160, 'pad_before': 58, 'pad_after': 0},
        ])),

    ('ch1/k4_pass89.jpg', '20', 1400, 3, 'paper', dict(
        bg=(PAPER, PAPER), pad_top=84, pad_bot=88, item_gap=42, items=[
            {'lines': ['Через минуту опять летят вдвоём.', 'Теперь не жду — сразу в касание', 'между ними.'], 'pos': 'left', 'size': 34, 'w': 'em'},
            {'lines': ['Пас прошёл. Смотрю вверх… Пусто.', 'За него ничего не вернули.'], 'pos': 'right', 'size': 34, 'w': 'el'},
        ])),

    ('ch1/f05_hands.jpg', '21', 1180, 3, 'paper', dict(
        bg=(PAPER, DARK), pad_bot=90, item_gap=42, items=[
            {'kind': 'fade', 'h': 160, 'pad_after': 58},
            {'lines': ['Так 0:2 и закончили.'], 'pos': 'center', 'size': 36, 'w': 'em'},
            {'lines': ['Шатскому примотали лёд к бедру,', 'остальные молча собираются.'], 'pos': 'center', 'size': 34, 'w': 'el'},
            {'lines': ['Мне тренер так ничего и не сказал —', 'ни напихал за потерю, ни похвалил.'], 'pos': 'center', 'size': 34, 'w': 'el'},
        ])),

    ('ch1/k35_bus.jpg', '22', 1380, 3, 'dark', dict(
        bg=(DARK, DARK), pad_top=92, pad_bot=94, item_gap=46, items=[
            {'lines': ['В автобусе все сразу вырубились,', 'а я вообще уснуть не могу.'], 'pos': 'left', 'size': 34, 'w': 'el'},
            {'lines': ['В протоколе про меня одна строчка:', 'вышел на 72-й. Ни голов, ни карточек.'], 'pos': 'right', 'size': 34, 'w': 'el'},
            {'lines': ['Про ту потерю там ни слова.', 'А это окно её посчитало.'], 'pos': 'center', 'size': 35, 'w': 'em'},
        ])),

    ('ch1/k5_kitchen.jpg', '23', 1380, 3, 'dark', dict(
        bg=(DARK, DARK), pad_top=90, pad_bot=90, item_gap=44, items=[
            {'lines': ['В автобусе нацарапал всё по памяти.', 'Дома переписал начисто — вдруг утром', 'решу, что просто перенервничал.'], 'pos': 'center', 'size': 34, 'w': 'el'},
            {'lines': ['Поднимаю глаза — а над столом', 'опять горит синяя рамка.'], 'pos': 'center', 'size': 36, 'w': 'em'},
        ])),

    ('ch1/p37_day.png', '24', 734, 3, 'dark', dict(
        bg=(DARK, DARK), pad_top=94, pad_bot=82, item_gap=44, items=[
            {'lines': ['Отбор — двадцать пять.', 'С этим понятно.'], 'pos': 'center', 'size': 35, 'w': 'el'},
            {'lines': ['Но «ИВ» — шестьдесят восемь.', 'Откуда столько, если квест я завалил?'], 'pos': 'center', 'size': 37, 'w': 'em'},
        ])),
]


def apply_lettering(ch, num, im_rgb):
    if ch != 1:
        return im_rgb
    out, _ = apply_ch1_frame(num, im_rgb)
    return out


if __name__ == '__main__':
    from grid import cover
    out_dir = Path('_backup/ch1_lettered')
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob('*.jpg'):
        old.unlink()
    total_b = 0
    for fpath, num, fh, fc, _, gspec in CH1_SCORE:
        raw = Image.open(fpath).convert('RGB')
        im = raw if raw.size == (W, fh) else cover(raw, W, fh, focus=fc)
        let, nb = apply_ch1_frame(num, im)
        let.save(out_dir / f'{num}.jpg', quality=92)
        total_b += nb
        _ = render_gutter(gspec['bg'][0], gspec['bg'][1], gspec['items'],
                          pad_top=gspec.get('pad_top', 74), pad_bot=gspec.get('pad_bot', 78),
                          item_gap=gspec.get('item_gap', 44), min_h=gspec.get('min_h', 130))
    _ = render_gutter(CH1_OPENING_GUTTER['bg'][0], CH1_OPENING_GUTTER['bg'][1],
                      CH1_OPENING_GUTTER['items'],
                      pad_top=CH1_OPENING_GUTTER.get('pad_top', 74),
                      pad_bot=CH1_OPENING_GUTTER.get('pad_bot', 78),
                      item_gap=CH1_OPENING_GUTTER.get('item_gap', 44),
                      min_h=CH1_OPENING_GUTTER.get('min_h', 130))
    n_mono = sum(sum(1 for it in g['items'] if it.get('kind', 'mono') not in ('space', 'fade'))
                 for *_, g in CH1_SCORE) + 2
    print(f'гл. 1: вебтун-леттеринг v6 готов · {len(CH1_SCORE)} кадров · '
          f'{total_b} внутрикадровых + {n_mono} межкадровых блоков · 0 пересечений')
