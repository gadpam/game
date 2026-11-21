# -*- coding: utf-8 -*-
"""
Сборка презентации.

    .venv/bin/python presentation/build.py

Результат (в папке «Презентация» в корне репозитория):
    Презентация/Родительское_собрание_3_курс.pptx   — редактируемый файл
    Презентация/Родительское_собрание_3_курс.pdf    — раздаточный вариант
    Презентация/preview/slide_01.png … slide_22.png   — превью 1920x1080
    Презентация/contact_sheet.png                     — все слайды на одном листе
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import content  # noqa: E402
from deck import BODY_BOTTOM, SLIDE_H, render_png, render_pptx  # noqa: E402

# готовые файлы — в папке «Презентация» в корне репозитория, чтобы их
# было легко найти и не искать по вложенным каталогам
OUT = os.path.join(ROOT, "Презентация")
PREVIEW = os.path.join(OUT, "preview")
PPTX_PATH = os.path.join(OUT, "Родительское_собрание_3_курс.pptx")
PDF_PATH = os.path.join(OUT, "Родительское_собрание_3_курс.pdf")
CONTACT_PATH = os.path.join(OUT, "contact_sheet.png")

TOL = 0.03          # допуск наложения, дюймы


def overlaps(canvas, index: int):
    """Проверка наложения текстовых блоков внутри одного слайда."""
    boxes = []
    for el in canvas.els:
        if el["t"] != "text":
            continue
        boxes.append((el["x"], el["y"], el["x"] + el["w"], el["y"] + el["h"]))
    out = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            dx = min(a[2], b[2]) - max(a[0], b[0])
            dy = min(a[3], b[3]) - max(a[1], b[1])
            if dx > TOL and dy > TOL:
                out.append(f"слайд {index}: наложение текста "
                           f"({a[0]:.2f},{a[1]:.2f}) и ({b[0]:.2f},{b[1]:.2f})")
    return out


def contact_sheet(pngs, path: str, cols: int = 4, thumb_w: int = 460):
    """Один лист со всеми слайдами — быстрый взгляд на структуру."""
    from PIL import Image
    if not pngs:
        return
    ims = [Image.open(p).convert("RGB") for p in pngs]
    tw = thumb_w
    th = int(round(tw * SLIDE_H / 13.333))
    pad = 18
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw + pad * (cols + 1),
                              rows * th + pad * (rows + 1)), "#E8E6E1")
    for i, im in enumerate(ims):
        r, c = divmod(i, cols)
        sheet.paste(im.resize((tw, th), Image.LANCZOS),
                    (pad + c * (tw + pad), pad + r * (th + pad)))
    sheet.save(path, "PNG")
    return path


def main() -> int:
    os.makedirs(PREVIEW, exist_ok=True)
    canvases = content.build()

    # убрать превью прошлой сборки (число слайдов могло измениться)
    for name in sorted(os.listdir(PREVIEW)):
        if name.startswith("slide_") and name.endswith(".png"):
            os.remove(os.path.join(PREVIEW, name))

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
        problems.extend(overlaps(c, i))
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

    # общий лист всех слайдов
    contact_sheet(pngs, os.path.join(OUT, "contact_sheet.png"))

    # шрифты рядом с файлом — чтобы показать на чужом компьютере
    fonts_dir = os.path.join(OUT, "Шрифты_Exo_2")
    os.makedirs(fonts_dir, exist_ok=True)
    for f in ("Exo2-Light.ttf", "Exo2-Medium.ttf", "Exo2-Bold.ttf"):
        src = os.path.join(ROOT, f)
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
        print("вёрстка: выходов за края нет, наложений нет")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
