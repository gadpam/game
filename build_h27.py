"""Кадр 11 гл. 4: страница блокнота с настоящей рукописью по-русски.

Генератор пишет латиницу и псевдописьмо — значит, текст кладём сами,
по перспективе страницы. Это центральная фраза главы:
    Протокол: отборы 2
    Панель: 3
    Протокол не видит один.
    Я вижу его.
         6.6   ← подчёркнуто дважды
"""
import sys
sys.path.insert(0, '.')
from grid import *                     # noqa
from PIL import Image, ImageDraw, ImageFilter

base = Image.open('ch4/h27_notebook_src.jpg').convert('RGB').resize((768, 1376), Image.LANCZOS)
INK = (26, 36, 70)
TILT = 4.2          # страница чуть повёрнута: строки идут вниз-вправо


def line(img, text, size, xy, weight='m', alpha=245, tilt=TILT):
    f = F(weight, size)
    bb = f.getbbox(text)                      # чернильный габарит
    pad = max(12, size // 3)
    tw, th = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
    lay = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((pad - bb[0], pad - bb[1]), text, font=f,
                             fill=INK + (alpha,))
    lay = lay.rotate(-tilt, resample=Image.BICUBIC, expand=True)
    img.paste(lay, xy, lay)
    return (xy[0], xy[1], xy[0] + lay.size[0], xy[1] + lay.size[1])


def block(img, items, x, y, gap, size, weight='m'):
    boxes = []
    for t in items:
        b = line(img, t, size, (x, y), weight)
        for ob in boxes:
            if b[1] < ob[3] and ob[1] < b[3]:
                raise ValueError(f'строки наезжают: «{t}»')
        boxes.append(b)
        y = b[3] + gap
    return boxes


d = ImageDraw.Draw(base)

# ── три записи ───────────────────────────────────────────────────
block(base, ['Протокол: отборы 2', 'Панель: 3'], 150, 330, 16, 34)
d.line([(170, 452), (560, 484)], fill=INK + (105,), width=2)
block(base, ['Протокол не видит один.', 'Я вижу его.'], 176, 500, 12, 30)

# ── «6.6» и двойное подчёркивание ────────────────────────────────
line(base, '6.6', 108, (206, 640), 'b')
# двойная черта под цифрами, с наклоном страницы
X0, X1 = 212, 470
K = 0.073
for yy, w, a in ((766, 5, 250), (788, 4, 225)):
    d.line([(X0, yy), (X1, yy + (X1 - X0) * K)], fill=INK + (a,), width=w)
    d.line([(X0, yy), (X1, yy + (X1 - X0) * K)], fill=(255, 255, 255, 26), width=1)

base.save('ch4/h27_notebook.jpg')
print('готово', base.size)
