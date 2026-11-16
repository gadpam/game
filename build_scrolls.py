"""
Сборка вертикальных скроллов глав 1–5 из кадров.
Проверки перед сборкой:
  · все кадры приводятся к 800×1600 (единство масштаба внутри главы);
  · повтор одного и того же файла в главе ловится как ошибка;
  · палитра главы выравнивается по медиане насыщенности (мягко, ±12%);
  · крупные панели обводятся — чтобы читались как панели, а не как кадры.
"""
import sys
from pathlib import Path
sys.path.insert(0, '.')
from grid import *                      # noqa
import numpy as np
from PIL import Image, ImageEnhance

SRC = Path('.')
TOP, BOT, GAP, PAGE = 300, 240, 10, 1600

CHAPTERS = {
    1: ('ПЕРВАЯ НЕДЕЛЯ', 'ТОМ 1 · ГЛАВА 1 · «ПОКА ПОВРЕМЕНИМ»', [
        ('ch1/f02_room.jpg', '01', 3), ('ch1/k1_locker.jpg', '02', 3),
        ('ch1/k2b_bench.jpg', '03', 3), ('ch1/p07_quest.png', '04', 3),
        ('ch1/k17_enter.jpg', '05', 3), ('ch1/n20_firsthalf.jpg', '06', 2),
        ('ch1/n78_press.jpg', '07', 2), ('ch1/n30_goal_rain.jpg', '08', 2),
        ('ch1/p18_enter.png', '09', 3), ('ch1/k3c_loss.jpg', '10', 3),
        ('ch1/p23_fail.png', '11', 3), ('ch1/k4_pass89.jpg', '12', 3),
        ('ch1/f05_hands.jpg', '13', 3), ('ch1/k35_bus.jpg', '14', 3),
        ('ch1/k5_kitchen.jpg', '15', 3), ('ch1/p37_day.png', '16', 3)]),
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
    a = np.asarray(im.resize((80, 140), Image.LANCZOS)).astype(float)
    return a.mean(), (a.max(2) - a.min(2)).mean()


def build(n):
    title, sub, seq = CHAPTERS[n]
    files = [f for f, _, _ in seq]

    dup = len(files) - len(set(files))
    if dup:
        raise ValueError(f'гл. {n}: один файл использован дважды')
    missing = [f for f in files if not (SRC / f).exists()]
    if missing:
        raise ValueError(f'гл. {n}: нет файлов {missing}')

    ims = [cover(Image.open(SRC / f).convert('RGB'), W, PAGE, focus=fc) for f, _, fc in seq]

    # палитра: тянем к медиане мягко, чтобы глава была одной температурой
    sats = [stat(i)[1] for i in ims]
    med = float(np.median(sats))
    for i, (im, s) in enumerate(zip(ims, sats)):
        if s > 1 and (s / med > 1.12 or s / med < 0.88):
            k = float(np.clip(med / s, 0.82, 1.18))
            ims[i] = ImageEnhance.Color(im).enhance(k)

    h = TOP + BOT + len(ims) * PAGE + (len(ims) - 1) * GAP
    sc = Image.new('RGB', (W, h), (8, 10, 14))
    d = ImageDraw.Draw(sc)
    d.text((W // 2, 74), title, font=F('b', 40), fill=(240, 246, 252), anchor='ma')
    d.text((W // 2, 138), sub, font=F('m', 14), fill=(150, 178, 202), anchor='ma')
    d.line([(190, 176), (610, 176)], fill=(90, 120, 150), width=1)
    npn = sum(1 for f, _, _ in seq if '/p' in f)
    d.text((W // 2, 200), f'{len(ims)} кадров · {npn} панели Системы',
           font=F('l', 15), fill=(150, 178, 202), anchor='ma')
    d.text((W // 2, 246), 'язык Solo Leveling · Exo 2', font=F('l', 13), fill=(96, 120, 142), anchor='ma')

    y = TOP
    for (f, num, _), im in zip(seq, ims):
        sc.paste(im, (0, y))
        if '/p' in f:
            d.rectangle([0, y, W - 1, y + PAGE - 1], outline=(58, 110, 150), width=2)
        d.text((W - 26, y + 22), num, font=F('l', 12), fill=(150, 178, 202), anchor='ra')
        y += PAGE + GAP

    fy = y - GAP + 40
    d.line([(60, fy), (740, fy)], fill=(90, 120, 150), width=1)
    d.text((W // 2, fy + 40), sp('ГЛАВА ' + str(n) + ' КОНЧЕНА', 2), font=F('b', 21),
           fill=(240, 246, 252), anchor='ma')
    nxt = f'продолжение в главе {n + 1}' if n < 5 else 'конец первого тома десяти кадров'
    d.text((W // 2, fy + 88), nxt, font=F('l', 15), fill=(150, 178, 202), anchor='ma')

    # ленты длинные: PNG весит 15–21 МБ на главу, JPEG q90 — 3 МБ при том же виде
    out = f'CH{n}_SCROLL_SL_full.jpg'
    sc.save(out, quality=90, optimize=True, progressive=True)

    # контактный лист
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


for k in sorted(CHAPTERS):
    build(k)

print('\nИТОГО')
for r in REPORT:
    print('  ', r)
