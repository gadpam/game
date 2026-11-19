"""Собирает первый проверочный пакет Главы 4 максимум по десять фреймов."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw

from build_ch4_v2_lettering import CH4_V2_SCORE, OPENING_GUTTER, TITLE, apply_ch4_v2_frame
from build_ch4_v2_lineup import build as build_lineup
from build_ch4_v2_system import build as build_system
from build_lettering import DARK, PAPER, render_gutter
from grid import F, cover, sp


W = 800
MAX_BATCH_FRAMES = 10


def frame_output(number: str) -> Path:
    return Path(f"ch4/v2_lettered_{number}.jpg")


def batch_output(start: int, end: int) -> Path:
    return Path(f"CH4_V2_BATCH_{start:02d}_{end:02d}_SCROLL.jpg")


def _render_gutter(spec):
    return render_gutter(
        spec["bg"][0],
        spec["bg"][1],
        spec["items"],
        pad_top=spec.get("pad_top", 74),
        pad_bot=spec.get("pad_bot", 78),
        item_gap=spec.get("item_gap", 44),
        min_h=spec.get("min_h", 130),
    )


def _text_count(spec) -> int:
    return sum(1 for item in spec["items"] if item.get("kind", "mono") not in ("space", "fade"))


def _header(start: int, end: int, height: int = 330) -> Image.Image:
    image = Image.new("RGB", (W, height), DARK)
    draw = ImageDraw.Draw(image)
    draw.text((W // 2, 68), sp("ГЛАВА 4", 3), font=F("m", 23), fill=(150, 178, 202), anchor="ma")
    draw.line([(150, 118), (650, 118)], fill=(90, 120, 150), width=1)
    draw.text((W // 2, 145), TITLE, font=F("b", 42), fill=(242, 247, 252), anchor="ma")
    draw.text(
        (W // 2, 224),
        f"ПРОВЕРОЧНЫЙ ПАКЕТ · ФРЕЙМЫ {start:02d}–{end:02d}",
        font=F("m", 19),
        fill=(128, 154, 176),
        anchor="ma",
    )
    draw.text((W // 2, 274), "не финальная лента главы", font=F("l", 17), fill=(105, 129, 150), anchor="ma")
    return image


def _opening_for(score, start: int):
    if start == 1:
        return _render_gutter(OPENING_GUTTER)
    first_mode = score[0][4]
    target = DARK if first_mode == "dark" else PAPER
    return render_gutter(
        DARK,
        target,
        [{"kind": "fade", "h": 180, "pad_after": 72}],
        pad_top=74,
        pad_bot=72,
        item_gap=44,
        min_h=130,
    )


def _refresh_dependencies(numbers: set[str]) -> None:
    if "02" in numbers:
        build_lineup()
    # Панель 11 подготавливается уже сейчас, но в пакет 01–10 не попадает.
    if numbers & {"08", "09", "10"}:
        build_system()


def build(start: int = 1, end: int = 10):
    if start < 1 or end > 10 or start > end:
        raise ValueError("пока разрешён только первый пакет в диапазоне 01–10")
    count = end - start + 1
    if count > MAX_BATCH_FRAMES:
        raise ValueError(f"в одном пакете разрешено не больше {MAX_BATCH_FRAMES} фреймов; запрошено {count}")

    score = CH4_V2_SCORE[start - 1 : end]
    numbers = [number for _, number, *_ in score]
    expected = [f"{index:02d}" for index in range(start, end + 1)]
    if numbers != expected:
        raise ValueError(f"нарушена последовательность пакета: {numbers}")
    if len({path for path, *_ in score}) != count:
        raise ValueError("пакет содержит повтор исходного кадра")
    if not all("/v2_" in path for path, *_ in score):
        raise ValueError("пакет принимает только versioned-пути")

    _refresh_dependencies(set(numbers))
    missing = [path for path, *_ in score if not Path(path).exists()]
    if missing:
        raise FileNotFoundError(f"нет versioned-ресурсов: {missing}")

    images = []
    inside_count = 0
    gutter_count = 0
    for path, number, height, focus, mode, gutter_spec in score:
        raw = Image.open(path).convert("RGB")
        framed = raw if raw.size == (W, height) else cover(raw, W, height, focus=focus)
        lettered, inside = apply_ch4_v2_frame(number, framed)
        inside_count += inside

        if path.lower().endswith((".jpg", ".jpeg")) and mode == "paper":
            edge = ImageDraw.Draw(lettered)
            edge.line([(0, 0), (W, 0)], fill=(30, 34, 40), width=2)
            edge.line([(0, lettered.height - 1), (W, lettered.height - 1)], fill=(30, 34, 40), width=2)

        output = frame_output(number)
        lettered.save(output, quality=93, optimize=True, progressive=True)
        images.append(lettered)
        gutter_count += _text_count(gutter_spec)

    header = _header(start, end)
    opening = _opening_for(score, start)
    gutters = [_render_gutter(spec) for *_, spec in score]
    bottom = Image.new("RGB", (W, 120), score[-1][-1]["bg"][1])
    total_h = header.height + opening.height + sum(im.height for im in images) + sum(g.height for g in gutters) + bottom.height

    scroll = Image.new("RGB", (W, total_h), DARK)
    y = 0
    for segment in (header, opening):
        scroll.paste(segment, (0, y))
        y += segment.height
    for image, gutter in zip(images, gutters):
        scroll.paste(image, (0, y))
        y += image.height
        scroll.paste(gutter, (0, y))
        y += gutter.height
    scroll.paste(bottom, (0, y))

    out = batch_output(start, end)
    scroll.save(out, quality=92, optimize=True, progressive=True)
    print(
        f"гл. 4 · пакет {start:02d}–{end:02d}: {count} фреймов · "
        f"{inside_count} внутрикадровых + {gutter_count} межкадровых блоков"
    )
    print(f"{out}: {W}×{total_h} · финальная лента главы не создавалась")
    return {
        "start": start,
        "end": end,
        "frames": count,
        "inside_blocks": inside_count,
        "gutter_blocks": gutter_count,
        "width": W,
        "height": total_h,
        "output": str(out),
        "frame_outputs": [str(frame_output(number)) for number in numbers],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=10)
    args = parser.parse_args()
    build(args.start, args.end)


if __name__ == "__main__":
    main()
