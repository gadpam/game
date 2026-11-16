"""
Сборка вертикальных скроллов глав 1–5.
Для гл. 1 включена полноценная вебтун-вёрстка по языку Solo Leveling:
  · режиссёрские межкадровые паузы («белая страница» днём ↔ тёмный вакуум на Системе и ночью)
    с плавными градиентами и парящим внутренним монологом без рамок;
  · разная высота кадров по ритму сцены (крупные планы, горизонтальный удар, окна Системы);
  · ни одного кадра-дубля и никакой служебной нумерации на самой ленте;
  · выравнивание насыщенности только по рисованным кадрам (окна Системы не трогаются);
  · титры по канону §3 п. 12: «ГЛАВА N» в начале, «ГЛАВА N КОНЧЕНА» + «продолжение…» + стрелка вниз.
Главы 2–5 пока собираются в прежнем режиме до своей очереди выверки.
"""
import sys
from pathlib import Path
sys.path.insert(0, '.')
from grid import *                      # noqa
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance
from build_lettering import (
    CH1_OPENING_GUTTER, CH1_SCORE, DARK, PAPER,
    apply_ch1_frame, apply_lettering, render_gutter,
)

SRC = Path('.')
TOP, BOT, GAP, PAGE = 300, 240, 10, 1600

CHAPTERS = {
    1: ('ПЕРВАЯ НЕДЕЛЯ', 'ТОМ 1 · ГЛАВА 1 · «ПОКА ПОВРЕМЕНИМ»',
        [(f, num, fc) for f, num, _, fc, _, _ in CH1_SCORE]),
    2: ('ДОБРО ПОЖАЛОВАТЬ, ИГРОК', 'ТОМ 1 · ГЛАВА 2 · «ДОБРО ПОЖАЛОВАТЬ, ИГРОК»', [
        ('ch2/c_room.jpg', '01', 3), ('ch2/c_garage.jpg', '02', 3),
        ('ch2/c_door.jpg', '03', 3), ('ch2/c_locker_empty.jpg', '04', 3),
        ('ch2/c_notebook.jpg', '05', 3), ('ch2/c_manege.jpg', '06', 3),
        ('ch2/p14_quest.png', '07', 3), ('ch2/c_touch.jpg', '08', 3),
        ('ch2/c_loss_ball.jpg', '09', 3), ('ch2/p22_done.png', '10', 3),
        ('ch2/c_guard.jpg', '11', 3), ('ch2/p24_total.png', '12', 3),
        ('ch2/c_lamp_off.jpg', '13', 3)]),
    3: ('ИЗ УВАЖЕНИЯ К ТАЙМИНГУ', 'ТОМ 1 · ГЛАВА 3 · «ИЗ УВАЖЕНИЯ К ТАЙМИНГУ»', [
        ('ch3/g02_kitchen.jpg', '01', 3), ('ch3/g03_lineup.jpg', '02', 3),
        ('ch3/g07_pitch.jpg', '03', 2), ('ch3/p09_quest.png', '04', 3),
        ('ch3/g12_press.jpg', '05', 2), ('ch3/g16_rollback.jpg', '06', 2),
        ('ch3/g17_subbed.jpg', '07', 2), ('ch3/g18_bench.jpg', '08', 3),
        ('ch3/g21_coach.jpg', '09', 3), ('ch3/p22_done.png', '10', 3),
        ('ch3/g23_empty.jpg', '11', 3), ('ch3/g24_bus.jpg', '12', 3)]),
    4: ('ПРОТОКОЛ 1:0', 'ТОМ 1 · ГЛАВА 4 · «ПРОТОКОЛ 1:0»', [
        ('ch4/h03_lineup.jpg', '01', 3), ('ch4/h08_bench_cold.jpg', '02', 3),
        ('ch4/p09_quest.png', '03', 3), ('ch4/h07_goal_conceded.jpg', '04', 3),
        ('ch4/h12_enter.jpg', '05', 3), ('ch4/h13_tackle.jpg', '06', 3),
        ('ch4/h14b_gap.jpg', '07', 3), ('ch4/h22_press.jpg', '08', 3),
        ('ch4/h25_protocol.jpg', '09', 3), ('ch4/p28_done.png', '10', 3),
        ('ch4/h27_notebook.jpg', '11', 3)]),
    5: ('У ТЕБЯ В ГОЛОВЕ СЛИШКОМ ТИХО', 'ТОМ 1 · ГЛАВА 5 · «У ТЕБЯ В ГОЛОВЕ СЛИШКОМ ТИХО»', [
        ('ch5/e03_note.jpg', '01', 3), ('ch5/e09_lines.jpg', '02', 3),
        ('ch5/e07_phone.jpg', '03', 3), ('ch5/e14_bench_edge.jpg', '04', 3),
        ('ch5/p15_choice.png', '05', 3), ('ch5/e13_pitch.jpg', '06', 2),
        ('ch5/e23_zone.jpg', '07', 3), ('ch5/e27_walk.jpg', '08', 3),
        ('ch5/e32_talk.jpg', '09', 3), ('ch5/p25_done.png', '10', 3),
        ('ch5/e39_notebook.jpg', '11', 3)]),
}

REPORT = []


def stat(im):
    a = np.asarray(im.resize((80, max(20, int(80 * im.height / im.width))), Image.LANCZOS)).astype(float)
    return a.mean(), (a.max(2) - a.min(2)).mean()


def _draw_header(d, n, title):
    d.text((W // 2, 84), sp(f'ГЛАВА {n}', 3), font=F('m', 24), fill=(150, 178, 202), anchor='ma')
    d.line([(200, 138), (600, 138)], fill=(90, 120, 150), width=1)
    d.text((W // 2, 166), title, font=F('b', 48), fill=(242, 247, 252), anchor='ma')
    d.text((W // 2, 248), 'ТОМ 1 · «ПОКА ПОВРЕМЕНИМ»', font=F('l', 19), fill=(128, 154, 176), anchor='ma')


def _draw_footer(d, n, fy):
    d.line([(80, fy), (720, fy)], fill=(78, 108, 138), width=1)
    d.text((W // 2, fy + 40), sp(f'ГЛАВА {n} КОНЧЕНА', 2), font=F('b', 27),
           fill=(240, 246, 252), anchor='ma')
    nxt = f'продолжение в главе {n + 1}' if n < 5 else 'продолжение следует'
    d.text((W // 2, fy + 96), nxt, font=F('l', 20), fill=(150, 178, 202), anchor='ma')
    ax, ay0, ay1 = W // 2, fy + 142, fy + 184
    d.line([(ax, ay0), (ax, ay1)], fill=(150, 178, 202), width=2)
    d.line([(ax - 8, ay1 - 9), (ax, ay1), (ax + 8, ay1 - 9)], fill=(150, 178, 202), width=2)


def build_ch1():
    title, sub, _ = CHAPTERS[1]
    files = [f for f, *_ in CH1_SCORE]
    if len(files) != len(set(files)):
        raise ValueError('гл. 1: один файл использован дважды')
    missing = [f for f in files if not (SRC / f).exists()]
    if missing:
        raise ValueError(f'гл. 1: нет файлов {missing}')

    # Загружаем каждый кадр в его режиссёрской высоте
    raw_ims = []
    for f, num, fh, fc, mode, _ in CH1_SCORE:
        im = Image.open(SRC / f).convert('RGB')
        im = im if im.size == (W, fh) else cover(im, W, fh, focus=fc)
        raw_ims.append(im)

    # Мягко выравниваем насыщенность только рисованных кадров (окна Системы /p*.png не трогаем)
    art_idx = [i for i, (f, *_) in enumerate(CH1_SCORE) if '/p' not in f]
    sats = [stat(raw_ims[i])[1] for i in art_idx]
    med = float(np.median(sats))
    for i, s in zip(art_idx, sats):
        if s > 1 and (s / med > 1.12 or s / med < 0.88):
            k = float(np.clip(med / s, 0.84, 1.16))
            raw_ims[i] = ImageEnhance.Color(raw_ims[i]).enhance(k)

    # Накладываем манга-баблы, штампы и сухие SFX (неразрушающе)
    ims = []
    for (f, num, fh, fc, mode, _), im in zip(CH1_SCORE, raw_ims):
        let, _ = apply_ch1_frame(num, im)
        # На светлых кадрах — тонкая перовая отбивка верхнего и нижнего обреза, как в манхве
        if '/p' not in f and mode == 'paper':
            dd = ImageDraw.Draw(let)
            dd.line([(0, 0), (W, 0)], fill=(30, 34, 40), width=2)
            dd.line([(0, let.height - 1), (W, let.height - 1)], fill=(30, 34, 40), width=2)
        ims.append(let)

    # Собираем межкадровые участки с парящим монологом и градиентами PAPER ↔ DARK
    open_g = render_gutter(
        CH1_OPENING_GUTTER['bg'][0], CH1_OPENING_GUTTER['bg'][1], CH1_OPENING_GUTTER['items'],
        pad_top=CH1_OPENING_GUTTER.get('pad_top', 56), pad_bot=CH1_OPENING_GUTTER.get('pad_bot', 56),
        item_gap=CH1_OPENING_GUTTER.get('item_gap', 34), min_h=CH1_OPENING_GUTTER.get('min_h', 120),
    )
    gutters = []
    for *_, gspec in CH1_SCORE:
        g = render_gutter(
            gspec['bg'][0], gspec['bg'][1], gspec['items'],
            pad_top=gspec.get('pad_top', 56), pad_bot=gspec.get('pad_bot', 56),
            item_gap=gspec.get('item_gap', 34), min_h=gspec.get('min_h', 120),
        )
        gutters.append(g)

    top_h, bot_h = 310, 260
    total_h = top_h + open_g.height + sum(i.height for i in ims) + sum(g.height for g in gutters) + bot_h
    sc = Image.new('RGB', (W, total_h), DARK)
    d = ImageDraw.Draw(sc)
    _draw_header(d, 1, title)

    y = top_h
    sc.paste(open_g, (0, y))
    y += open_g.height
    for im, g in zip(ims, gutters):
        sc.paste(im, (0, y))
        y += im.height
        sc.paste(g, (0, y))
        y += g.height

    _draw_footer(d, 1, y + 36)

    out = 'CH1_SCROLL_SL_full.jpg'
    sc.save(out, quality=90, optimize=True, progressive=True)

    # Нарезка на 5 удобных вертикальных полос (как реальная прокрутка на телефоне) — для просмотра с межкадровыми полями
    sdir = Path('_backup/ch1_strips')
    sdir.mkdir(parents=True, exist_ok=True)
    for old in sdir.glob('*.jpg'):
        old.unlink()

    # Контактный лист гл. 1: показывает реальную вебтун-ленту 6 колонками сверху вниз (видны и кадры, и паузы, и монолог!)
    COLS = 6
    col_w = 340
    scale = col_w / W
    scaled_h = int(round(total_h * scale))
    sc_small = sc.resize((col_w, scaled_h), Image.LANCZOS)
    slice_h = (scaled_h + COLS - 1) // COLS
    pad = 18
    head_h = 92
    sw = COLS * col_w + (COLS + 1) * pad
    sh = head_h + slice_h + 2 * pad + 34
    sheet = Image.new('RGB', (sw, sh), (236, 235, 231))
    sd = ImageDraw.Draw(sheet)
    sd.text((pad, 22), f'ГЛАВА 1 · «{title}» · вебтун-лента целиком ({len(ims)} кадров, чтение по колонкам 1 - 6)',
            font=F('b', 22), fill=(22, 26, 32))
    sd.text((pad, 58), f'{sub}  ·  полный размер для телефона: CH1_SCROLL_SL_full.jpg ({W}x{total_h})',
            font=F('l', 14), fill=(96, 102, 110))
    for c in range(COLS):
        y0 = c * slice_h
        y1 = min(scaled_h, y0 + slice_h)
        crop = sc_small.crop((0, y0, col_w, y1))
        x = pad + c * (col_w + pad)
        yy = head_h + pad
        sheet.paste(crop, (x, yy))
        sd.rectangle([x - 1, yy - 1, x + col_w, yy + crop.height], outline=(182, 180, 174), width=1)
        sd.text((x + col_w // 2, yy + slice_h + 8), f'полоса {c + 1} / {COLS}',
                font=F('m', 13), fill=(62, 68, 76), anchor='ma')
    sheet.save('CH1_SL_SHEET.jpg', quality=92, optimize=True, progressive=True)

    REPORT.append((1, out, 'CH1_SL_SHEET.jpg', len(ims), round(med, 1), round(float(np.mean(sats)), 1)))
    print(f'гл. 1: {len(ims)} кадров · скролл {W}×{total_h} · насыщ. медиана {med:.1f} · {out} + CH1_SL_SHEET.jpg')


def build(n):
    if n == 1:
        return build_ch1()
    title, sub, seq = CHAPTERS[n]
    files = [f for f, _, _ in seq]

    if len(files) != len(set(files)):
        raise ValueError(f'гл. {n}: один файл использован дважды')
    missing = [f for f in files if not (SRC / f).exists()]
    if missing:
        raise ValueError(f'гл. {n}: нет файлов {missing}')

    ims = [cover(Image.open(SRC / f).convert('RGB'), W, PAGE, focus=fc) for f, _, fc in seq]
    art_idx = [i for i, (f, _, _) in enumerate(seq) if not f.endswith('.png')]
    sats = [stat(ims[i])[1] for i in art_idx]
    med = float(np.median(sats))
    for i in art_idx:
        s = stat(ims[i])[1]
        if s > 1 and (s / med > 1.12 or s / med < 0.88):
            k = float(np.clip(med / s, 0.82, 1.18))
            ims[i] = ImageEnhance.Color(ims[i]).enhance(k)

    ims = [apply_lettering(n, num, im) for (_, num, _), im in zip(seq, ims)]

    h = TOP + BOT + len(ims) * PAGE + (len(ims) - 1) * GAP
    sc = Image.new('RGB', (W, h), (8, 10, 14))
    d = ImageDraw.Draw(sc)
    d.text((W // 2, 68), sp(f'ГЛАВА {n}', 3), font=F('m', 18), fill=(150, 178, 202), anchor='ma')
    d.line([(240, 110), (560, 110)], fill=(90, 120, 150), width=1)
    d.text((W // 2, 134), title, font=F('b', 38), fill=(240, 246, 252), anchor='ma')
    d.text((W // 2, 202), 'ТОМ 1 · «ПОКА ПОВРЕМЕНИМ»', font=F('l', 14), fill=(120, 146, 168), anchor='ma')

    y = TOP
    for (f, num, _), im in zip(seq, ims):
        sc.paste(im, (0, y))
        if '/p' in f:
            d.rectangle([0, y, W - 1, y + PAGE - 1], outline=(58, 110, 150), width=2)
        d.text((W - 26, y + 22), num, font=F('l', 12), fill=(150, 178, 202), anchor='ra')
        y += PAGE + GAP

    _draw_footer(d, n, y - GAP + 36)

    out = f'CH{n}_SCROLL_SL_full.jpg'
    sc.save(out, quality=90, optimize=True, progressive=True)

    CW, CH, COLS, pad, caph = 330, 660, 4, 18, 50
    rows = (len(ims) + COLS - 1) // COLS
    sw = COLS * CW + (COLS + 1) * pad
    sh = rows * (CH + caph) + (rows + 1) * pad + 92
    s2 = Image.new('RGB', (sw, sh), (247, 246, 243))
    dd = ImageDraw.Draw(s2)
    dd.text((pad, 24), f'ГЛАВА {n} · «{title}» · {len(ims)} кадров', font=F('b', 23), fill=(24, 28, 34))
    dd.text((pad, 62), sub, font=F('l', 13), fill=(118, 124, 130))
    for i, im in enumerate(ims):
        r, c = divmod(i, COLS)
        x = pad + c * (CW + pad)
        yy = 92 + pad + r * (CH + caph + pad)
        s2.paste(im.resize((CW, CH), Image.LANCZOS), (x, yy))
        dd.rectangle([x, yy, x + CW, yy + CH], outline=(206, 204, 198))
        dd.text((x + 2, yy + CH + 10), seq[i][1], font=F('b', 15), fill=(24, 28, 34))
    s2.save(f'CH{n}_SL_SHEET.jpg', quality=92, optimize=True, progressive=True)

    REPORT.append((n, out, f'CH{n}_SL_SHEET.jpg', len(ims), round(med, 1), round(float(np.mean(sats)), 1)))
    print(f'гл. {n}: {len(ims)} кадров · насыщ. медиана {med:.1f} · {out} + CH{n}_SL_SHEET.jpg')


if __name__ == '__main__':
    for k in sorted(CHAPTERS):
        build(k)

    print('\nИТОГО')
    for r in REPORT:
        print('  ', r)
