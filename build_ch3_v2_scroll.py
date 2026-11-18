"""Финальная изолированная сборка Главы 3 v2 — только после утверждения.

Модуль безопасно импортируется и не создаёт ленту сам. Полный скролл и
монтажный лист можно собрать ровно один раз явной командой
``python build_ch3_v2_scroll.py --approved`` после авторского утверждения
текста и кода. Legacy ``CH3_*`` не перезаписываются.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from build_ch3_v2_bus import build as build_bus
from build_ch3_v2_epilogue import build as build_epilogue
from build_ch3_v2_insets import build as build_lineup
from build_ch3_v2_lettering import (
    CH3_V2_SCORE,
    OPENING_GUTTER,
    apply_ch3_v2_frame,
    build_lettered_previews,
)
from build_ch3_v2_subbed import build as build_subbed
from build_ch3_v2_system import (
    DONE,
    GOAL,
    QUEST,
    QUEST_RANK,
    TACKLE_AFTER,
    TACKLE_BEFORE,
    build as build_system_panels,
)
from build_lettering import DARK, render_gutter
from grid import F, cover, sp


W = 800
OUT_SCROLL = Path("CH3_V2_SCROLL_SL_full.jpg")
OUT_SHEET = Path("CH3_V2_SL_SHEET.jpg")
TITLE = "ИЗ УВАЖЕНИЯ К ТАЙМИНГУ"
SUBTITLE = "ТОМ 1 · ГЛАВА 3 · ПРОИЗВОДСТВЕННАЯ ВЕРСИЯ V2"


def stat(image: Image.Image):
    small_h = max(20, int(80 * image.height / image.width))
    array = np.asarray(
        image.resize((80, small_h), Image.Resampling.LANCZOS)
    ).astype(float)
    return float(array.mean()), float((array.max(2) - array.min(2)).mean())


def _draw_header(draw: ImageDraw.ImageDraw):
    draw.text(
        (W // 2, 84), sp("ГЛАВА 3", 3), font=F("m", 24),
        fill=(150, 178, 202), anchor="ma",
    )
    draw.line([(160, 138), (640, 138)], fill=(90, 120, 150), width=1)
    draw.text(
        (W // 2, 166), TITLE, font=F("b", 38),
        fill=(242, 247, 252), anchor="ma",
    )
    draw.text(
        (W // 2, 244), "ТОМ 1 · «ПОКА ПОВРЕМЕНИМ»", font=F("l", 19),
        fill=(128, 154, 176), anchor="ma",
    )


def _draw_footer(draw: ImageDraw.ImageDraw, y: int):
    draw.line([(80, y), (720, y)], fill=(78, 108, 138), width=1)
    draw.text(
        (W // 2, y + 42), sp("ГЛАВА 3 КОНЧЕНА", 2), font=F("b", 27),
        fill=(240, 246, 252), anchor="ma",
    )


def _gutter(spec):
    return render_gutter(
        spec["bg"][0], spec["bg"][1], spec["items"],
        pad_top=spec.get("pad_top", 74),
        pad_bot=spec.get("pad_bot", 78),
        item_gap=spec.get("item_gap", 44),
        min_h=spec.get("min_h", 130),
    )


def _contact_sheet(scroll: Image.Image, total_h: int, frame_count: int):
    cols = 5
    col_w = 360
    scale = col_w / W
    scaled_h = int(round(total_h * scale))
    reduced = scroll.resize((col_w, scaled_h), Image.Resampling.LANCZOS)
    slice_h = (scaled_h + cols - 1) // cols
    pad = 18
    head_h = 96
    sheet_w = cols * col_w + (cols + 1) * pad
    sheet_h = head_h + slice_h + 2 * pad + 34
    sheet = Image.new("RGB", (sheet_w, sheet_h), (236, 235, 231))
    draw = ImageDraw.Draw(sheet)
    draw.text(
        (pad, 22),
        f"ГЛАВА 3 · «{TITLE}» · v2 ({frame_count} кадров, чтение по колонкам 1–{cols})",
        font=F("b", 22), fill=(22, 26, 32),
    )
    draw.text(
        (pad, 60),
        f"{SUBTITLE}  ·  полный размер: {OUT_SCROLL.name} ({W}×{total_h})",
        font=F("l", 14), fill=(96, 102, 110),
    )
    for column in range(cols):
        y0 = column * slice_h
        y1 = min(scaled_h, y0 + slice_h)
        crop = reduced.crop((0, y0, col_w, y1))
        x = pad + column * (col_w + pad)
        y = head_h + pad
        sheet.paste(crop, (x, y))
        draw.rectangle(
            [x - 1, y - 1, x + col_w, y + crop.height],
            outline=(182, 180, 174), width=1,
        )
        draw.text(
            (x + col_w // 2, y + slice_h + 8),
            f"полоса {column + 1} / {cols}",
            font=F("m", 13), fill=(62, 68, 76), anchor="ma",
        )
    sheet.save(OUT_SHEET, quality=93, optimize=True, progressive=True)


def _qc_strips(scroll: Image.Image):
    out_dir = Path("_backup/ch3_v2_strips")
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.jpg"):
        old.unlink()
    count = 5
    strip_h = (scroll.height + count - 1) // count
    for index in range(count):
        y0 = index * strip_h
        y1 = min(scroll.height, y0 + strip_h)
        scroll.crop((0, y0, W, y1)).save(
            out_dir / f"strip_{index + 1:02d}.jpg",
            quality=93, optimize=True, progressive=True,
        )


def build(*, approved: bool = False):
    if not approved:
        raise PermissionError(
            "Глава 3 ещё не утверждена: финальная лента собирается только "
            "с явным флагом --approved после решения автора"
        )

    build_lineup()
    build_system_panels()
    build_subbed()
    build_bus()
    build_epilogue()
    inside_count, gutter_text_count = build_lettered_previews()

    files = [path for path, *_ in CH3_V2_SCORE]
    numbers = [number for _, number, *_ in CH3_V2_SCORE]
    if len(files) != 20 or len(files) != len(set(files)):
        raise ValueError("гл. 3 v2: нужны ровно 20 уникальных кадров")
    if numbers != [f"{index:02d}" for index in range(1, 21)]:
        raise ValueError(f"гл. 3 v2: нарушена нумерация: {numbers}")
    if not all("/v2_" in path for path in files):
        raise ValueError("гл. 3 v2: финальная сборка принимает только versioned-пути")
    missing = [path for path in files if not Path(path).exists()]
    if missing:
        raise ValueError(f"гл. 3 v2: нет файлов {missing}")
    if (QUEST_RANK, GOAL, TACKLE_BEFORE, TACKLE_AFTER) != ("F−", 3, 26, 28):
        raise ValueError("гл. 3 v2: нарушен контракт F− / 3 / 26→28")
    if QUEST not in map(Path, files) or DONE not in map(Path, files):
        raise ValueError("гл. 3 v2: системные панели отсутствуют в партитуре")

    images = []
    art_saturation = []
    for path, number, height, focus, mode, _ in CH3_V2_SCORE:
        raw = Image.open(path).convert("RGB")
        framed = raw if raw.size == (W, height) else cover(raw, W, height, focus=focus)
        if path.lower().endswith((".jpg", ".jpeg")):
            art_saturation.append(stat(framed)[1])
        lettered, _ = apply_ch3_v2_frame(number, framed)
        if path.lower().endswith((".jpg", ".jpeg")) and mode == "paper":
            edge = ImageDraw.Draw(lettered)
            edge.line([(0, 0), (W, 0)], fill=(30, 34, 40), width=2)
            edge.line(
                [(0, lettered.height - 1), (W, lettered.height - 1)],
                fill=(30, 34, 40), width=2,
            )
        images.append(lettered)

    opening = _gutter(OPENING_GUTTER)
    gutters = [_gutter(spec) for *_, spec in CH3_V2_SCORE]
    top_h = 310
    bottom_h = 190
    total_h = (
        top_h
        + opening.height
        + sum(image.height for image in images)
        + sum(gutter.height for gutter in gutters)
        + bottom_h
    )

    scroll = Image.new("RGB", (W, total_h), DARK)
    draw = ImageDraw.Draw(scroll)
    _draw_header(draw)
    y = top_h
    scroll.paste(opening, (0, y))
    y += opening.height
    for image, gutter in zip(images, gutters):
        scroll.paste(image, (0, y))
        y += image.height
        scroll.paste(gutter, (0, y))
        y += gutter.height

    _draw_footer(draw, y + 36)
    scroll.save(OUT_SCROLL, quality=92, optimize=True, progressive=True)
    _contact_sheet(scroll, total_h, len(images))
    _qc_strips(scroll)

    median_sat = float(np.median(art_saturation))
    mean_sat = float(np.mean(art_saturation))
    print(
        f"гл. 3 v2: {len(images)} кадров · {inside_count} внутрикадровых + "
        f"{gutter_text_count} межкадровых блоков · 0 пересечений"
    )
    print(
        f"скролл {W}×{total_h} · насыщ. clean art: "
        f"медиана {median_sat:.1f}, среднее {mean_sat:.1f}"
    )
    print(f"{OUT_SCROLL} + {OUT_SHEET}")
    return {
        "frames": len(images),
        "inside_blocks": inside_count,
        "gutter_blocks": gutter_text_count,
        "width": W,
        "height": total_h,
        "median_saturation": round(median_sat, 1),
        "mean_saturation": round(mean_sat, 1),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--approved",
        action="store_true",
        help="подтверждает, что автор уже утвердил код и текст Главы 3",
    )
    args = parser.parse_args()
    if not args.approved:
        parser.error("сборка заблокирована до авторского утверждения; нужен --approved")
    build(approved=True)


if __name__ == "__main__":
    main()
