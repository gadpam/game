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


# ── гл. 1 · лист заявки на доске в раздевалке ────────────────────
def build_ch1_locker():
    from collections import deque
    import numpy as np
    im = Image.open('ch1/k1_locker_src.jpg').convert('RGB').resize((768, 1376), Image.LANCZOS)
    a = np.asarray(im)
    hh, ww, _ = a.shape
    vis = np.zeros((hh, ww), dtype=bool)
    q = deque([(325, 620)])
    vis[620, 325] = True
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < ww and 0 <= ny < hh and not vis[ny, nx] and a[ny, nx].mean() > 205:
                vis[ny, nx] = True
                q.append((nx, ny))
    # Отступ 2 px от контура головы/пальца, чтобы буквы естественно уходили под них
    eroded = vis.copy()
    for _ in range(2):
        eroded = eroded & np.roll(eroded, 1, 0) & np.roll(eroded, -1, 0) \
                 & np.roll(eroded, 1, 1) & np.roll(eroded, -1, 1)
    mask = Image.fromarray((eroded * 255).astype('uint8'), 'L')

    lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    ink_h = (42, 50, 66, 200)
    ink_b = (56, 64, 80, 172)
    ink_s = (86, 92, 104, 168)
    d.text((303, 593), 'ЗАЯВКА (18)', font=F('b', 8), fill=ink_h)
    d.text((303, 603), 'РЕЧНИК - ТОРПЕДО-2', font=F('m', 5), fill=ink_s)
    d.line([(303, 612), (362, 612)], fill=(110, 114, 120, 145), width=1)
    # 11 в старте (сжато верхним блоком) + отбивка ЗАПАС (7 человек, Ветров 18-м внизу)
    d.text((303, 614), 'СТАРТ · 1–11', font=F('b', 6), fill=ink_s)
    yy = 622
    for nm in ('ГРОМОВ', 'САВЕЛЬЕВ', 'АНДРЕЕВ', 'ШАТСКИЙ', 'ЛЕВЧУК'):
        d.text((304, yy), nm, font=F('m', 6), fill=ink_b)
        yy += 6
    d.line([(303, yy + 2), (362, yy + 2)], fill=(118, 122, 128, 135), width=1)
    d.text((303, yy + 4), 'ЗАПАС · 12–18', font=F('b', 6), fill=ink_s)
    yy += 12
    for nm in ('БОБРОВ', 'МЕЛЬНИК', 'КИСЕЛЕВ'):
        d.text((304, yy), nm, font=F('m', 6), fill=ink_b)
        yy += 6
    d.text((303, yy + 1), '18. ВЕТРОВ', font=F('b', 7), fill=ink_h)

    # Маскируем по листу, чтобы ни один пиксель не залез на голову или большой палец
    r, g, b, al = lay.split()
    al = Image.fromarray((np.asarray(al, dtype=int) * np.asarray(mask, dtype=int) // 255).astype('uint8'), 'L')
    lay.putalpha(al)
    out = im.convert('RGBA')
    out.paste(lay, (0, 0), lay)
    out.convert('RGB').save('ch1/k1_locker.jpg', quality=95)
    print('k1_locker готово', im.size)


# ── гл. 1 · запись в блокноте на кухне после матча ───────────────
def build_ch1_kitchen():
    im = Image.open('ch1/k5_kitchen_src.jpg').convert('RGB').resize((768, 1376), Image.LANCZOS)

    def persp_line(text, size, weight, xy, alpha=198):
        f = F(weight, size)
        bb = f.getbbox(text)
        pad = 10
        tw, th = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
        lay = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
        ImageDraw.Draw(lay).text((pad - bb[0], pad - bb[1]), text, font=f,
                                 fill=(34, 42, 68, alpha))
        # Лёгкий наклон в перспективе страницы + поворот вдоль разлиновки (-3°)
        shear = -0.32
        nw = tw + int(abs(shear) * th) + 4
        lay = lay.transform((nw, th), Image.AFFINE, (1, shear, 0, 0, 1, 0),
                            resample=Image.BICUBIC)
        lay = lay.rotate(3.0, resample=Image.BICUBIC, expand=True)
        im.paste(lay, xy, lay)

    # Верхняя страница (над пером — ход выезда)
    persp_line('1-я неделя', 12, 'b', (364, 916), alpha=190)
    persp_line('72′ — замена', 11, 'm', (370, 935), alpha=184)
    persp_line('88′ — потеря', 11, 'm', (376, 953), alpha=184)
    # Правая страница (отдельно вынесено число Системы)
    persp_line('отбор: 25', 13, 'b', (536, 1004), alpha=212)

    im.save('ch1/k5_kitchen.jpg', quality=95)
    print('k5_kitchen готово', im.size)


if __name__ == '__main__':
    build_ch1_locker()
    build_ch1_kitchen()
    build_lineup()
    build_note()
    build_protocol()
