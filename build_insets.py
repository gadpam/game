"""Врезки с настоящей кириллицей: гл. 3 список состава, гл. 5 запись в блокноте.

Генератор пишет латиницу и псевдобуквы — значит страницу делаем чистой,
а текст кладём сами, по наклону бумаги. Общая функция здесь одна.
"""
import sys
sys.path.insert(0, '.')
from grid import F                      # noqa
from PIL import Image, ImageDraw

INK = (26, 36, 70)


def write(img, text, size, xy, weight='m', ink=INK, tilt=0.0, alpha=245, fit=None):
    """Кладёт строку под наклоном бумаги. fit — максимальная ширина в пикселях."""
    while True:
        f = F(weight, size)
        bb = f.getbbox(text)
        w = bb[2] - bb[0]
        if fit is None or w <= fit or size <= 8:
            break
        size -= 1
    pad = max(14, size // 2)
    tw, th = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
    lay = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((pad - bb[0], pad - bb[1]), text, font=f, fill=ink + (alpha,))
    lay = lay.rotate(-tilt, resample=Image.BICUBIC, expand=True)
    img.paste(lay, xy, lay)
    return (xy[0], xy[1], xy[0] + lay.size[0], xy[1] + lay.size[1]), size


def block(img, items, x, y, gap, tilt, fit=None, inks=None):
    """items: (text, size, weight). Строки не должны перекрываться."""
    boxes, sizes = [], []
    for i, (t, size, w) in enumerate(items):
        ink = (inks or [INK] * len(items))[i]
        b, real = write(img, t, size, (x, y), w, ink=ink, tilt=tilt, fit=fit)
        for ob in boxes:
            if b[1] < ob[3] and ob[1] < b[3]:
                raise ValueError(f'строки наезжают: «{t}»')
        boxes.append(b)
        sizes.append(real)
        y = b[3] + gap
    return y, sizes


# ── гл. 3 · список состава на стене коридора ─────────────────────
def build_lineup():
    im = Image.open('ch3/g03_lineup_src.jpg').convert('RGB').resize((768, 1376), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    X, FIT, TILT = 178, 400, 1.6

    write(im, 'СОСТАВ НА МАТЧ', 30, (X, 250), 'b', tilt=TILT, fit=FIT)
    write(im, 'ТОРПЕДО-2 — ГОРЕЦ · КУБОК', 15, (X + 2, 292), 'm', tilt=TILT, fit=FIT,
          ink=(90, 84, 74))
    d.line([(X + 2, 322), (X + FIT, 322 + FIT * 0.028)], fill=(90, 84, 74), width=2)

    # в заявке он есть — в самом конце, куда свет клуба не достаёт
    names = ['ГРОМОВ', 'САВЕЛЬЕВ', 'АНДРЕЕВ', 'КАРИМОВ', 'ШАТСКИЙ',
             'ЛЕВЧУК', 'БОБРОВ', 'МЕЛЬНИК', 'ГОНЧАР', 'ТКАЧЁВ',
             'КИСЕЛЕВ', 'ВЕТРОВ']
    y = 344
    for i, n in enumerate(names):
        last = (i == len(names) - 1)
        write(im, n, 17, (X + 6, y), 'b' if last else 'm', tilt=TILT,
              ink=(26, 36, 70) if not last else (60, 70, 100),
              alpha=250 if not last else 225)
        d.line([(X + 190, y + 26), (X + 300, y + 26 + 110 * 0.028)],
               fill=(120, 112, 100), width=1)
        y += 40
    im.save('ch3/g03_lineup.jpg')
    print('g03 готово', im.size)


# ── гл. 5 · запись в блокноте на кухне ───────────────────────────
def build_note():
    im = Image.open('ch5/e39_notebook_src.jpg').convert('RGB').resize((768, 1376), Image.LANCZOS)
    TILT = -7.0                      # строки уходят вверх-вправо, как разлиновка
    X, FIT = 292, 186

    block(im, [('Смотр. Замены не просил.', 19, 'b'),
               ('Каримов смотрел на зону,', 14, 'm'),
               ('а не на мяч.', 14, 'm')],
          X, 512, 15, TILT, fit=FIT)
    im.save('ch5/e39_notebook.jpg')
    print('e39 готово', im.size)


# ── гл. 4 · протокол дня: блокнот рядом с телефоном ──────────────
def build_protocol():
    im = Image.open('ch4/h25_protocol_src.jpg').convert('RGB').resize((768, 1376), Image.LANCZOS)
    TILT = -9.0
    X, FIT = 268, 182
    # одна строка: вторая уходила за нижнюю кромку страницы
    block(im, [('форма: стабильная', 19, 'm')], X, 926, 12, TILT, fit=FIT)
    im.save('ch4/h25_protocol.jpg')
    print('h25 готово', im.size)


if __name__ == '__main__':
    build_lineup()
    build_note()
    build_protocol()
