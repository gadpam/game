"""
Единая сетка панелей Системы («Пока повременим») — стилизация Solo Leveling (REDICE Studio).
Все панели собираются ТОЛЬКО через этот модуль — чтобы пропорции не плыли.

Визуальный язык Solo Leveling:
  · глубокое сапфирово-кобальтовое голографическое стекло (алое тревожное — для провала,
    изумрудно-бирюзовое — для выполнения) с внутренним свечением по кромке и тонким растром;
  · многоплановая глубина: смещённые задние стёкла, техносетка, частицы, энергетические каналы;
  · фасеточная двойная рамка со ступенчатыми угловыми узлами, боковыми рёбрами и ценовыми чипами;
  · верхняя и нижняя световые проекционные планки шире окна + деликатные искры света;
  · фирменная плашка шапки «[ ! ]  С И С Т Е М А» в рамке и мягкое неоновое свечение заголовков/цифр;
  · шрифт строго Exo 2 (Light / Medium / Bold), стрелки и ромбы — векторной графикой,
    без полос XP и «LEVEL UP» (§3 #9, #14).
"""
import math
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 800, 1600
FONT = {'b': 'fonts/Exo2-Bold.ttf', 'm': 'fonts/Exo2-Medium.ttf', 'l': 'fonts/Exo2-Light.ttf'}
_fcache = {}

# ─── палитра состояний Solo Leveling ────────────────────────────
STATE = {
    'n': dict(
        aura=(18, 122, 245),       # внешний кобальтово-синий ореол SL
        edge=(64, 204, 255),       # яркий электрик-циан рамки
        hot=(222, 249, 255),       # ледяное белое ядро неона
        inner=(132, 224, 255),     # внутренняя тонкая рамка и орнамент
        glass=((7, 20, 46), (13, 42, 84), (5, 14, 34)),   # верх, центр, низ стекла
        ink=(238, 249, 255),
        dim=(144, 196, 232),
    ),
    'g': dict(
        aura=(16, 168, 122),
        edge=(72, 242, 186),
        hot=(224, 255, 244),
        inner=(148, 248, 214),
        glass=((6, 28, 26), (11, 52, 46), (4, 18, 17)),
        ink=(234, 254, 246),
        dim=(142, 212, 186),
    ),
    'f': dict(
        aura=(215, 22, 36),        # тревожный багровый ореол штрафного окна SL
        edge=(255, 76, 82),        # неоново-алый контур
        hot=(255, 228, 226),       # раскалённое светлое ядро
        inner=(255, 152, 152),
        glass=((32, 6, 11), (62, 12, 20), (20, 4, 8)),
        ink=(255, 238, 236),
        dim=(228, 164, 164),
    ),
}
YELLOW = (255, 222, 96)


def F(weight, size):
    key = (weight, size)
    if key not in _fcache:
        _fcache[key] = ImageFont.truetype(FONT[weight], size)
    return _fcache[key]


def sp(text, n=2):
    """Разрядка в ширину — шапка панели и группы."""
    return (' ' * n).join(list(text))


def cover(im, w=W, h=H, focus=3):
    """Кроп с фокусом по вертикали: 0 — верх, 3 — центр, 10 — низ."""
    iw, ih = im.size
    s = max(w / iw, h / ih)
    im = im.resize((int(iw * s + 1), int(ih * s + 1)), Image.LANCZOS)
    iw, ih = im.size
    left = (iw - w) // 2
    top = int((ih - h) * focus / 10)
    return im.crop((left, top, left + w, top + h))


# ─── геометрия ───────────────────────────────────────────────────
PAD_IN = 62
ROW = 34
BARW = 216
GAP_BAR_VAL = 88


def arrow(d, x_head, y, length=22, color=(144, 196, 232), alpha=240, width=2):
    """Стрелка линиями (в Exo 2 символа U+2192 нет)."""
    x0 = x_head - length
    d.line([(x0, y), (x_head - 2, y)], fill=color + (alpha,), width=width)
    d.line([(x_head - 8, y - 5), (x_head - 1, y)], fill=color + (alpha,), width=width)
    d.line([(x_head - 8, y + 5), (x_head - 1, y)], fill=color + (alpha,), width=width)


def glow_text(lay, xy, s, font, fill, glow_col, anchor='ma', radius=8, strength=0.75):
    """Рисует текст с мягким голографическим свечением Solo Leveling."""
    gt = Image.new('RGBA', lay.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(gt)
    gd.text(xy, s, font=font, fill=glow_col[:3] + (int(255 * strength),), anchor=anchor)
    gt = gt.filter(ImageFilter.GaussianBlur(radius))
    lay.alpha_composite(gt)
    d = ImageDraw.Draw(lay)
    d.text(xy, s, font=font, fill=fill, anchor=anchor)
    return d.textbbox(xy, s, font=font, anchor=anchor)


def num_change(p, y, left, right, size=34, color_r=(255, 86, 86), left_w='b', right_w='b', align='right'):
    """«26 → 25» с голографическим свечением цифр и рисованной стрелкой по центру."""
    fl, fr = F(left_w, size), F(right_w, size)
    sl, sr = str(left), str(right)
    wl, wr = p.d.textlength(sl, font=fl), p.d.textlength(sr, font=fr)
    arr_len, pad_l, pad_r = 22, 11, 11
    if align == 'center':
        total = wl + pad_l + arr_len + pad_r + wr
        x_l = p.cx - total / 2
        x_head = x_l + wl + pad_l + arr_len
        x_r = x_head + pad_r
    else:
        x_r = p.g['val'] - wr
        x_head = x_r - pad_r
        x_l = x_head - arr_len - pad_l - wl
    bbl = fl.getbbox(sl)
    ymid = y + (bbl[1] + bbl[3]) / 2
    glow_text(p.lay, (x_l, y), sl, fl, p.st['hot'] + (255,), p.st['edge'], anchor='la', radius=7, strength=0.55)
    glow_text(p.lay, (x_r, y), sr, fr, color_r + (255,), color_r, anchor='la', radius=9, strength=0.72)
    p.d = ImageDraw.Draw(p.lay)
    arrow(p.d, x_head, ymid, length=arr_len, color=p.st['edge'], alpha=240, width=2)
    b1 = p.d.textbbox((x_l, y), sl, font=fl)
    b2 = p.d.textbbox((x_r, y), sr, font=fr)
    return (min(b1[0], b2[0]), min(b1[1], b2[1]), max(b1[2], b2[2]), max(b1[3], b2[3]))


def geometry(x0, x1):
    return dict(
        lbl=x0 + PAD_IN,
        bar0=x1 - PAD_IN - GAP_BAR_VAL - BARW,
        bar1=x1 - PAD_IN - GAP_BAR_VAL,
        val=x1 - PAD_IN,
    )


def void_bg(kind='n', box=(44, 78, 756, 790), w=W, h=868):
    """Тёмное пространство Solo Leveling под голографическое окно Системы."""
    st = STATE[kind]
    base_col = (5, 8, 15)
    im = Image.new('RGBA', (w, h), base_col + (255,))
    x0, y0, x1, y1 = box

    # Широкий глубокий ореол за стеклом
    amb = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ad = ImageDraw.Draw(amb)
    ad.rectangle([x0 - 30, y0 - 20, x1 + 30, y1 + 20], fill=st['aura'] + (108,))
    im = Image.alpha_composite(im, amb.filter(ImageFilter.GaussianBlur(54)))

    # Тонкие световые блики-шлейфы у верхней и нижней проекционных планок (эффект маны SL, не «звёзды»)
    wisps = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wisps)
    cx = (x0 + x1) // 2
    # Горизонтальная световая вспышка вдоль верхней и нижней планок
    wd.ellipse([cx - 290, y0 - 10, cx + 290, y0 + 10], fill=st['aura'] + (140,))
    wd.ellipse([cx - 290, y1 - 10, cx + 290, y1 + 10], fill=st['aura'] + (140,))
    im = Image.alpha_composite(im, wisps.filter(ImageFilter.GaussianBlur(14)))

    streaks = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(streaks)
    for fx, length, al in [(0.08, 26, 95), (0.21, 18, 70), (0.37, 22, 80),
                           (0.63, 24, 85), (0.79, 17, 70), (0.92, 28, 95)]:
        px = int(x0 + (x1 - x0) * fx)
        sd.line([(px, max(4, y0 - length)), (px, y0 - 3)], fill=st['edge'] + (al,), width=1)
        sd.line([(px, y1 + 3), (px, min(h - 4, y1 + length))], fill=st['edge'] + (al,), width=1)
    im = Image.alpha_composite(im, streaks.filter(ImageFilter.GaussianBlur(0.8)))
    return im.convert('RGB')


def subbox(p, x0, y0, x1, y1, alpha=92):
    """Вложенная полупрозрачная подпанель Solo Leveling с тонкими угловыми засечками."""
    st = p.st
    sb = Image.new('RGBA', (p.bw, p.bh), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sb)
    fill_c = {'n': (3, 11, 28, alpha), 'g': (3, 16, 15, alpha), 'f': (18, 3, 6, alpha)}[p.kind]
    sd.rectangle([x0, y0, x1, y1], fill=fill_c, outline=st['edge'] + (96,), width=1)
    # Яркие угловые засечки 9 px
    t = 9
    for cx, cy, dx, dy in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
        sd.line([(cx, cy + dy * t), (cx, cy), (cx + dx * t, cy)], fill=st['hot'] + (205,), width=2)
    p.lay.alpha_composite(sb)
    p.d = ImageDraw.Draw(p.lay)


def depth_bg(kind, box, h, w=800):
    """Многослойное пространство: задние стёкла, техносетка, частицы и лучи глубины."""
    base = void_bg(kind, box, w=w, h=h).convert('RGBA')
    st = STATE[kind]
    x0, y0, x1, y1 = box

    # Матовая тактическая сетка остаётся почти невидимой, пока её не ловит свечение.
    grid = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    for x in range(24, w, 56):
        gd.line([(x, 0), (x, h)], fill=st['inner'] + (11,), width=1)
    for y in range(30, h, 56):
        gd.line([(0, y), (w, y)], fill=st['inner'] + (8,), width=1)
    base = Image.alpha_composite(base, grid)

    # Два смещённых стекла за главным окном создают параллакс и перспективу.
    rear = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rear)
    plates = [
        ([(x0 - 22, y0 + 42), (x1 - 34, y0 + 10),
          (x1 + 4, y1 - 32), (x0 - 38, y1 + 8)], 18, 58),
        ([(x0 + 30, y0 - 18), (x1 + 26, y0 + 24),
          (x1 + 38, y1 + 16), (x0 + 4, y1 - 28)], 12, 42),
    ]
    for poly, fill_a, edge_a in plates:
        rd.polygon(poly, fill=st['aura'] + (fill_a,))
        rd.line(poly + [poly[0]], fill=st['edge'] + (edge_a,), width=2)
    base = Image.alpha_composite(base, rear.filter(ImageFilter.GaussianBlur(1.3)))

    # Наклонные энергетические каналы и узлы ломают плоскую фронтальность.
    energy = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ed = ImageDraw.Draw(energy)
    conduits = [
        ((18, int(h * 0.22)), (x0 - 8, int(h * 0.34))),
        ((w - 18, int(h * 0.28)), (x1 + 8, int(h * 0.39))),
        ((20, int(h * 0.77)), (x0 - 8, int(h * 0.66))),
        ((w - 20, int(h * 0.72)), (x1 + 8, int(h * 0.61))),
    ]
    for a, b in conduits:
        ed.line([a, b], fill=st['edge'] + (80,), width=1)
        for px, py in (a, b):
            ed.polygon([(px, py - 5), (px + 5, py), (px, py + 5), (px - 5, py)],
                       fill=st['hot'] + (155,))
    for i in range(28):
        px = 18 + ((i * 83 + h // 7) % (w - 36))
        py = 22 + ((i * 137 + h // 11) % (h - 44))
        r = 1 + (i % 2)
        ed.ellipse((px - r, py - r, px + r, py + r), fill=st['inner'] + (45 + (i % 3) * 18,))
    base = Image.alpha_composite(base, energy.filter(ImageFilter.GaussianBlur(0.45)))
    return base.convert('RGB')


def decorate_panel(p):
    """Боковые рёбра, глубинные фаски и плавающие узлы поверх основного стекла."""
    st = p.st
    z = Image.new('RGBA', (p.bw, p.bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(z)
    x0, y0, x1, y1 = p.box

    # Полупрозрачные боковые «крылья» уходят от стекла в глубину.
    d.polygon([(x0 + 10, y0 + 74), (x0 + 34, y0 + 48),
               (x0 + 34, y1 - 48), (x0 + 10, y1 - 74)],
              fill=st['aura'] + (24,), outline=st['inner'] + (62,))
    d.polygon([(x1 - 10, y0 + 74), (x1 - 34, y0 + 48),
               (x1 - 34, y1 - 48), (x1 - 10, y1 - 74)],
              fill=st['aura'] + (18,), outline=st['inner'] + (52,))

    # Наклонные блики делят стекло на планы, но не мешают чтению.
    d.polygon([(x0 + 44, y0 + 18), (x0 + 150, y0 + 18),
               (x0 + 88, y1 - 18), (x0 + 24, y1 - 18)], fill=st['edge'] + (10,))
    d.polygon([(x1 - 92, y0 + 18), (x1 - 34, y0 + 18),
               (x1 - 54, y1 - 18), (x1 - 138, y1 - 18)], fill=st['hot'] + (5,))

    for frac in (0.24, 0.50, 0.76):
        yy = int(y0 + (y1 - y0) * frac)
        for xx, side in ((x0 + 18, 1), (x1 - 18, -1)):
            d.line([(xx, yy - 18), (xx + side * 16, yy)], fill=st['edge'] + (92,), width=1)
            d.line([(xx + side * 16, yy), (xx, yy + 18)], fill=st['edge'] + (92,), width=1)
            d.ellipse((xx - 2, yy - 2, xx + 2, yy + 2), fill=st['hot'] + (190,))
    p.lay.alpha_composite(z)
    p.d = ImageDraw.Draw(p.lay)


def holo_card(p, x0, y0, x1, y1, alpha=104, active=False):
    """Объёмная фасеточная карточка вместо плоского прямоугольника."""
    st = p.st
    cut = 12
    poly = [(x0 + cut, y0), (x1 - cut, y0), (x1, y0 + cut),
            (x1, y1 - cut), (x1 - cut, y1), (x0 + cut, y1),
            (x0, y1 - cut), (x0, y0 + cut)]

    shadow = Image.new('RGBA', (p.bw, p.bh), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.polygon([(x + 8, y + 10) for x, y in poly], fill=(0, 0, 0, 118))
    p.lay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(9)))

    glow = Image.new('RGBA', (p.bw, p.bh), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.line(poly + [poly[0]], fill=st['edge'] + (170 if active else 95,), width=5 if active else 3)
    p.lay.alpha_composite(glow.filter(ImageFilter.GaussianBlur(8)))

    d = ImageDraw.Draw(p.lay)
    fill_c = {'n': (3, 12, 31, alpha), 'g': (3, 19, 17, alpha),
              'f': (22, 4, 8, alpha)}[p.kind]
    d.polygon(poly, fill=fill_c)
    d.line(poly + [poly[0]], fill=st['edge'] + (160 if active else 100,), width=2)
    inner = [(x0 + 6 + cut, y0 + 6), (x1 - 6 - cut, y0 + 6),
             (x1 - 6, y0 + 6 + cut), (x1 - 6, y1 - 6 - cut),
             (x1 - 6 - cut, y1 - 6), (x0 + 6 + cut, y1 - 6),
             (x0 + 6, y1 - 6 - cut), (x0 + 6, y0 + 6 + cut)]
    d.line(inner + [inner[0]], fill=st['inner'] + (58,), width=1)
    d.line([(x0 + 28, y0 + 1), (min(x1 - 28, x0 + 156), y0 + 1)],
           fill=st['hot'] + (220,), width=2)
    d.line([(x1 + 1, y0 + 34), (x1 + 1, y1 - 34)], fill=st['edge'] + (62,), width=3)
    node_x, node_y = x0 + 15, (y0 + y1) // 2
    d.polygon([(node_x, node_y - 5), (node_x + 5, node_y),
               (node_x, node_y + 5), (node_x - 5, node_y)], fill=st['hot'] + (190,))
    p.d = d


def rank_crest(p, cx, y0, y1, w_half=82):
    """Гранёный голографический щиток ранга квеста (F− / F / F+) в стиле Solo Leveling."""
    st = p.st
    x0, x1 = cx - w_half, cx + w_half
    ch = 14
    poly = [
        (x0 + ch, y0), (x1 - ch, y0), (x1, y0 + ch),
        (x1, y1 - ch), (x1 - ch, y1), (x0 + ch, y1),
        (x0, y1 - ch), (x0, y0 + ch),
    ]
    gl = Image.new('RGBA', (p.bw, p.bh), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gl)
    gd.polygon(poly, fill=st['aura'] + (75,), outline=st['edge'] + (220,))
    gd.line(poly + [poly[0]], fill=st['edge'] + (220,), width=4)
    p.lay.alpha_composite(gl.filter(ImageFilter.GaussianBlur(7)))

    d = ImageDraw.Draw(p.lay)
    inner_fill = {'n': (8, 30, 66, 175), 'g': (8, 38, 34, 175), 'f': (48, 8, 14, 175)}[p.kind]
    d.polygon(poly, fill=inner_fill)
    d.line(poly + [poly[0]], fill=st['edge'] + (255,), width=3)
    d.line(poly + [poly[0]], fill=st['hot'] + (215,), width=1)
    # Внутренний тонкий контур
    s = 6
    ch2 = 11
    poly2 = [
        (x0 + s + ch2, y0 + s), (x1 - s - ch2, y0 + s), (x1 - s, y0 + s + ch2),
        (x1 - s, y1 - s - ch2), (x1 - s - ch2, y1 - s), (x0 + s + ch2, y1 - s),
        (x0 + s, y1 - s - ch2), (x0 + s, y0 + s + ch2),
    ]
    d.line(poly2 + [poly2[0]], fill=st['inner'] + (115,), width=1)
    p.d = d


class Panel:
    """Голографическое окно Системы в стиле Solo Leveling (REDICE Studio)."""

    def __init__(self, base, box, kind='n', frame_id=None, glow=True, sl_icon=True):
        self.base = base.convert('RGBA')
        self.bw, self.bh = self.base.size
        self.box = box
        self.x0, self.y0, self.x1, self.y1 = box
        self.kind = kind
        self.st = STATE[kind]
        self.cx = (self.x0 + self.x1) // 2
        self.g = geometry(self.x0, self.x1)
        self.lay = Image.new('RGBA', (self.bw, self.bh), (0, 0, 0, 0))
        self._glow(glow)
        self._glass()
        self.header_bbox = None
        self.divs = []
        self._sl_frame()
        self.d = ImageDraw.Draw(self.lay)
        self._header(frame_id, sl_icon=sl_icon)

    def _glow(self, on):
        if not on:
            return
        x0, y0, x1, y1 = self.box
        st = self.st
        # Двухслойный неоновый ореол по контуру и проекционным планкам
        g1 = Image.new('RGBA', (self.bw, self.bh), (0, 0, 0, 0))
        d1 = ImageDraw.Draw(g1)
        d1.rectangle([x0 - 4, y0 - 4, x1 + 4, y1 + 4], outline=st['aura'] + (225,), width=12)
        rail_l, rail_r = max(8, x0 - 16), min(self.bw - 8, x1 + 16)
        d1.line([(rail_l, y0), (rail_r, y0)], fill=st['edge'] + (255,), width=8)
        d1.line([(rail_l, y1), (rail_r, y1)], fill=st['edge'] + (255,), width=8)
        self.lay.alpha_composite(g1.filter(ImageFilter.GaussianBlur(18)))

        g2 = Image.new('RGBA', (self.bw, self.bh), (0, 0, 0, 0))
        d2 = ImageDraw.Draw(g2)
        d2.rectangle([x0, y0, x1, y1], outline=st['edge'] + (245,), width=5)
        d2.line([(rail_l, y0), (rail_r, y0)], fill=st['hot'] + (245,), width=4)
        d2.line([(rail_l, y1), (rail_r, y1)], fill=st['hot'] + (245,), width=4)
        self.lay.alpha_composite(g2.filter(ImageFilter.GaussianBlur(5)))

    def _glass(self):
        x0, y0, x1, y1 = self.box
        c_top, c_mid, c_bot = self.st['glass']
        st = self.st
        w_box, h_box = x1 - x0, y1 - y0
        glass = Image.new('RGBA', (w_box, h_box), (0, 0, 0, 0))
        dg = ImageDraw.Draw(glass)
        for yy in range(h_box):
            t = yy / max(1, h_box - 1)
            # Ярче к центру, глубже к краям + лёгкая голографическая строка через каждые 4 px
            if t < 0.5:
                u = t * 2.0
                c = tuple(int(c_top[j] + (c_mid[j] - c_top[j]) * u) for j in range(3))
            else:
                u = (t - 0.5) * 2.0
                c = tuple(int(c_mid[j] + (c_bot[j] - c_mid[j]) * u) for j in range(3))
            if yy % 4 == 0:
                c = tuple(min(255, c[j] + 4) for j in range(3))
            dg.line([(0, yy), (w_box, yy)], fill=c + (220,))

        # Внутреннее свечение вдоль кромки стекла (характерный эффект голограммы SL)
        rim = Image.new('RGBA', (w_box, h_box), (0, 0, 0, 0))
        rd = ImageDraw.Draw(rim)
        rd.rectangle([0, 0, w_box - 1, h_box - 1], outline=st['aura'] + (145,), width=14)
        rd.line([(0, 0), (w_box, 0)], fill=st['edge'] + (140,), width=8)
        rd.line([(0, h_box - 1), (w_box, h_box - 1)], fill=st['edge'] + (140,), width=8)
        glass = Image.alpha_composite(glass, rim.filter(ImageFilter.GaussianBlur(16)))

        # Тончайший диагональный блик по стеклу
        sheen = Image.new('RGBA', (w_box, h_box), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sheen)
        sd.polygon([
            (int(w_box * 0.14), 0), (int(w_box * 0.42), 0),
            (int(w_box * 0.16), h_box), (0, h_box), (0, int(h_box * 0.45)),
        ], fill=st['edge'] + (14,))
        glass = Image.alpha_composite(glass, sheen)

        self.lay.alpha_composite(glass, (x0, y0))

    def _sl_frame(self):
        """Фирменная двойная архитектурная рамка Solo Leveling со ступенчатыми углами (2× SS)."""
        ss = 2
        fl = Image.new('RGBA', (self.bw * ss, self.bh * ss), (0, 0, 0, 0))
        d = ImageDraw.Draw(fl)
        st = self.st
        e, hot, inn = st['edge'], st['hot'], st['inner']
        x0, y0, x1, y1 = self.x0 * ss, self.y0 * ss, self.x1 * ss, self.y1 * ss
        cx, cy_m = (x0 + x1) // 2, (y0 + y1) // 2

        # 1. Внешний неоновый контур + белое ядро
        d.rectangle([x0, y0, x1, y1], outline=e + (255,), width=6)
        d.rectangle([x0 + 1, y0 + 1, x1 - 1, y1 - 1], outline=hot + (235,), width=2)

        # 2. Верхняя и нижняя проекционные планки Solo Leveling (выступают за края окна)
        ext = min(15 * ss, x0 - 6 * ss, self.bw * ss - x1 - 6 * ss)
        if ext > 4:
            for ry, dy in [(y0, -1), (y1, 1)]:
                rl, rr = x0 - ext, x1 + ext
                pts = [
                    (rl, ry), (rl + 8 * ss, ry + dy * 4 * ss),
                    (rr - 8 * ss, ry + dy * 4 * ss), (rr, ry),
                    (rr - 8 * ss, ry - dy * 2 * ss), (rl + 8 * ss, ry - dy * 2 * ss),
                ]
                d.polygon(pts, fill=e + (245,))
                d.line([(rl + 3 * ss, ry), (rr - 3 * ss, ry)], fill=hot + (255,), width=3)
                # Центральный ромб на планке
                dr = 6 * ss
                d.polygon([(cx, ry - dr), (cx + dr, ry), (cx, ry + dr), (cx - dr, ry)],
                          fill=hot + (255,), outline=e + (255,))

        # 3. Внутренняя тонкая рамка с фирменными ступенчатыми угловыми узлами SL
        ins = 11 * ss
        step_a = 24 * ss
        step_b = 18 * ss
        ix0, iy0, ix1, iy1 = x0 + ins, y0 + ins, x1 - ins, y1 - ins
        # Прямые участки внутренней рамки между угловыми узлами
        d.line([(ix0 + step_a, iy0), (ix1 - step_a, iy0)], fill=inn + (165,), width=2)
        d.line([(ix0 + step_a, iy1), (ix1 - step_a, iy1)], fill=inn + (165,), width=2)
        d.line([(ix0, iy0 + step_a), (ix0, iy1 - step_a)], fill=inn + (165,), width=2)
        d.line([(ix1, iy0 + step_a), (ix1, iy1 - step_a)], fill=inn + (165,), width=2)

        # Четыре угловых орнаментальных узла Solo Leveling (ступенька + квадрат + ромб)
        for ox, oy, dx, dy in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
            jx, jy = ox + dx * ins, oy + dy * ins
            # Ступенчатый излом внутренней линии
            step_pts = [
                (jx + dx * step_a, jy),
                (jx + dx * step_b, jy),
                (jx + dx * step_b, jy + dy * 8 * ss),
                (jx + dx * 8 * ss, jy + dy * 8 * ss),
                (jx + dx * 8 * ss, jy + dy * step_b),
                (jx, jy + dy * step_b),
                (jx, jy + dy * step_a),
            ]
            d.line(step_pts, fill=e + (235,), width=3)
            d.line(step_pts, fill=hot + (175,), width=1)
            # Малый угловой квадрат-узел (визитная карточка рамок SL)
            q0x, q1x = sorted([jx, jx + dx * 12 * ss])
            q0y, q1y = sorted([jy, jy + dy * 12 * ss])
            d.rectangle([q0x, q0y, q1x, q1y], outline=hot + (225,), width=2)
            # Светящаяся точка в центре узла
            mx, my = (q0x + q1x) // 2, (q0y + q1y) // 2
            d.polygon([(mx, my - 3 * ss), (mx + 3 * ss, my), (mx, my + 3 * ss), (mx - 3 * ss, my)],
                      fill=hot + (250,))
            # Усиленный внешний Г-угол
            L = 34 * ss
            d.line([(ox, oy + dy * L), (ox, oy), (ox + dx * L, oy)], fill=hot + (255,), width=5)

        # 4. Боковые симметричные ромбовидные засечки посередине высоты
        if (y1 - y0) > 360 * ss:
            for sx, dx in [(ix0, 1), (ix1, -1)]:
                d.line([(sx, cy_m - 28 * ss), (sx + dx * 5 * ss, cy_m - 20 * ss),
                        (sx + dx * 5 * ss, cy_m + 20 * ss), (sx, cy_m + 28 * ss)],
                       fill=e + (185,), width=2)
                d.polygon([(sx + dx * 2 * ss, cy_m - 5 * ss), (sx + dx * 7 * ss, cy_m),
                           (sx + dx * 2 * ss, cy_m + 5 * ss), (sx - dx * 3 * ss, cy_m)],
                          fill=hot + (225,))

        self.lay.alpha_composite(fl.resize((self.bw, self.bh), Image.LANCZOS))

    def _header(self, frame_id, sl_icon=True):
        """Фирменная шапка Solo Leveling: плашка «[ ! ]  С И С Т Е М А» с боковыми лучами."""
        x0, y0, x1 = self.x0, self.y0, self.x1
        st = self.st
        e, hot, ink, dim = st['edge'], st['hot'], st['ink'], st['dim']

        t = sp('СИСТЕМА', 2)
        f = F('b', 18)
        tw = self.d.textlength(t, font=f)
        icon_w = 34 if sl_icon else 0
        pad_x = 20
        plate_w = int(tw + icon_w + pad_x * 2)
        plate_h = 34
        px0 = self.cx - plate_w // 2
        px1 = px0 + plate_w
        py0 = y0 + 22
        py1 = py0 + plate_h
        ly = (py0 + py1) // 2

        # Мягкое свечение плашки шапки
        hg = Image.new('RGBA', (self.bw, self.bh), (0, 0, 0, 0))
        ImageDraw.Draw(hg).rectangle([px0, py0, px1, py1], outline=e + (210,), width=3)
        self.lay.alpha_composite(hg.filter(ImageFilter.GaussianBlur(5)))

        d = ImageDraw.Draw(self.lay)
        pfill = {'n': (10, 38, 82, 195), 'g': (8, 46, 40, 195), 'f': (68, 10, 18, 195)}[self.kind]
        d.rectangle([px0, py0, px1, py1], fill=pfill, outline=e + (245,), width=2)
        d.rectangle([px0 + 3, py0 + 3, px1 - 3, py1 - 3], outline=hot + (95,), width=1)

        if sl_icon:
            # Кружок с восклицательным знаком [ ! ] — каноничный маркер окон Solo Leveling
            icx = px0 + pad_x + 10
            ir = 10
            d.ellipse([icx - ir, ly - ir, icx + ir, ly + ir], outline=hot + (245,), width=2)
            # Восклицательный знак линиями (чётко на любом кегле)
            d.line([(icx, ly - 6), (icx, ly + 1)], fill=hot + (255,), width=2)
            d.rectangle([icx - 1, ly + 4, icx + 1, ly + 6], fill=hot + (255,))
            tx = px0 + pad_x + icon_w + tw / 2
        else:
            tx = self.cx

        d.text((tx, ly - 1), t, font=f, fill=hot + (252,), anchor='mm')
        self.header_bbox = (px0, py0, px1, py1)

        # Боковые двойные лучи с ромбами
        lx0, lx1 = x0 + 36, px0 - 16
        rx0, rx1 = px1 + 16, x1 - 36
        if lx1 > lx0 + 12:
            d.line([(lx0, ly), (lx1, ly)], fill=e + (175,), width=1)
            d.line([(rx0, ly), (rx1, ly)], fill=e + (175,), width=1)
            for xx in (px0 - 9, px1 + 9):
                d.polygon([(xx, ly - 4), (xx + 4, ly), (xx, ly + 4), (xx - 4, ly)], fill=hot + (235,))

        if frame_id:
            d.text((self.g['val'], y0 + 62), sp(str(frame_id), 1),
                   font=F('l', 11), fill=dim + (140,), anchor='ra')
        self.d = d

    # ─── элементы ────────────────────────────────────────────────
    def div(self, y):
        x0, x1, cx = self.x0, self.x1, self.cx
        e, hot, inn = self.st['edge'], self.st['hot'], self.st['inner']
        self.divs.append(y)
        # Двухступенчатый голографический разделитель с центральным ромбом и микро-ромбами
        self.d.line([(x0 + 38, y), (cx - 18, y)], fill=inn + (125,), width=1)
        self.d.line([(cx + 18, y), (x1 - 38, y)], fill=inn + (125,), width=1)
        self.d.line([(cx - 95, y), (cx - 18, y)], fill=e + (210,), width=2)
        self.d.line([(cx + 18, y), (cx + 95, y)], fill=e + (210,), width=2)
        self.d.polygon([(cx, y - 5), (cx + 6, y), (cx, y + 5), (cx - 6, y)],
                       fill=hot + (245,), outline=e + (255,))
        for xx in (x0 + 38, x1 - 38):
            self.d.polygon([(xx, y - 2), (xx + 2, y), (xx, y + 2), (xx - 2, y)], fill=e + (185,))

    def center(self, y, text, weight='l', size=13, color=None, spacing=None):
        s = sp(text, spacing) if spacing else text
        col = (color if color else self.st['dim']) + (215,)
        self.d.text((self.cx, y), s, font=F(weight, size), fill=col, anchor='ma')

    def left(self, y, text, weight='l', size=15, color=None, alpha=238):
        col = (color if color else self.st['ink'])
        self.d.text((self.g['lbl'], y), text, font=F(weight, size), fill=col + (alpha,))

    def value(self, y, text, weight='m', size=16, color=None):
        col = (color if color else self.st['ink'])
        self.d.text((self.g['val'], y), text, font=F(weight, size), fill=col + (248,), anchor='ra')

    def group(self, y, name):
        gl = sp(name, 3)
        f = F('m', 11)
        self.d.text((self.g['lbl'], y), gl, font=f, fill=self.st['dim'] + (195,))
        gw = self.d.textlength(gl, font=f)
        self.d.line([(self.g['lbl'] + gw + 16, y + 6), (self.g['val'], y + 6)],
                    fill=self.st['edge'] + (75,), width=1)
        return y + 32

    def row(self, y, name, val, color=None, bar=True):
        e = self.st['edge']
        col = (color if color else self.st['ink'])
        self.d.text((self.g['lbl'], y + 3), name, font=F('l', 15), fill=col + (238,))
        if bar:
            by = y + 11
            self.d.line([(self.g['bar0'], by), (self.g['bar1'], by)],
                        fill=(120, 160, 200, 45), width=3)
            self.d.line([(self.g['bar0'], by),
                         (self.g['bar0'] + max(3, int(BARW * val / 100)), by)],
                        fill=e + (210,), width=3)
        hot = val >= 85
        self.d.text((self.g['val'], y + 2), str(val),
                    font=F('b' if hot else 'm', 19 if hot else 16),
                    fill=col + (255,), anchor='ra')
        return y + ROW

    def save(self, path):
        Image.alpha_composite(self.base, self.lay).convert('RGB').save(path)
        return path


def text_h(weight, size):
    f = F(weight, size)
    a, d = f.getmetrics()
    return a + d


class Flow:
    def __init__(self, panel, y_top, y_bottom):
        self.p = panel
        self.top = y_top
        self.bottom = y_bottom
        self.blocks = []

    def add(self, fn, h, weight=1.0):
        self.blocks.append([weight, fn, h])
        return self

    def run(self):
        used = sum(b[2] for b in self.blocks)
        wsum = sum(b[0] for b in self.blocks)
        free = self.bottom - self.top - used
        if free < 0:
            raise ValueError(f'не влезает: нужно {used}, есть {self.bottom - self.top}')
        y = self.top
        for w, fn, h in self.blocks:
            y += free * (w / wsum)
            fn(self.p, int(round(y)))
            y += h
        return y

    def check(self):
        used = sum(b[2] for b in self.blocks)
        free = self.bottom - self.top - used
        y = self.top
        spans = []
        for w, fn, h in self.blocks:
            y += free * (w / sum(b[0] for b in self.blocks))
            spans.append((int(y), int(y + h)))
            y += h
        for i in range(len(spans) - 1):
            if spans[i][1] > spans[i + 1][0]:
                raise ValueError(f'перекрытие блоков {i} и {i + 1}: {spans[i]} / {spans[i + 1]}')
        if spans and spans[-1][1] > self.bottom:
            raise ValueError('последний блок выходит за низ')
        return spans
