# -*- coding: utf-8 -*-
"""
Сборка презентации.

    .venv/bin/python presentation/build.py

Результат:
    presentation/out/Родительское_собрание_3_курс.pptx   — редактируемый файл
    presentation/out/preview/slide_01.png … slide_20.png   — превью 1920x1080
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import content  # noqa: E402
from deck import BODY_BOTTOM, SLIDE_H, render_png, render_pptx  # noqa: E402

OUT = os.path.join(HERE, "out")
PREVIEW = os.path.join(OUT, "preview")
PPTX_PATH = os.path.join(OUT, "Родительское_собрание_3_курс.pptx")
PDF_PATH = os.path.join(OUT, "Родительское_собрание_3_курс.pdf")


def main() -> int:
    os.makedirs(PREVIEW, exist_ok=True)
    canvases = content.build()

    problems = []
    pngs = []
    for i, c in enumerate(canvases, 1):
        for el in c.els:
            if el["t"] != "text":
                continue
            bottom = el["y"] + el["h"]
            if bottom > SLIDE_H - 0.12:
                problems.append(f"слайд {i}: текст выходит за нижний край ({bottom:.2f}\")")
            if el["y"] < 0.10:
                problems.append(f"слайд {i}: текст выше верхнего края ({el['y']:.2f}\")")
        path = os.path.join(PREVIEW, f"slide_{i:02d}.png")
        render_png(c, path)
        pngs.append(path)

    render_pptx(canvases, PPTX_PATH,
                title="Родительское собрание · 3 курс программистов",
                author="Преподаватель курса")

    # PDF для раздаточных материалов (из превью — точная копия вёрстки)
    from PIL import Image
    pages = [Image.open(p).convert("RGB") for p in pngs]
    pages[0].save(PDF_PATH, "PDF", resolution=144.0, save_all=True, append_images=pages[1:])

    # шрифты рядом с файлом — чтобы показать на чужом компьютере
    fonts_dir = os.path.join(OUT, "Шрифты_Exo_2")
    os.makedirs(fonts_dir, exist_ok=True)
    for f in ("Exo2-Light.ttf", "Exo2-Medium.ttf", "Exo2-Bold.ttf"):
        src = os.path.join(os.path.dirname(HERE), f)
        dst = os.path.join(fonts_dir, f)
        if not os.path.exists(dst):
            with open(src, "rb") as a, open(dst, "wb") as b:
                b.write(a.read())

    print(f"слайдов: {len(canvases)}")
    print(f"pptx:    {PPTX_PATH}")
    print(f"pdf:     {PDF_PATH}")
    print(f"preview: {PREVIEW}")
    if problems:
        print("\nПРЕДУПРЕЖДЕНИЯ ВЁРСТКИ:")
        for p in problems:
            print("  -", p)
    else:
        print("вёрстка: выходов за края нет")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
