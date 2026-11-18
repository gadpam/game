import hashlib
import unittest
from pathlib import Path

from PIL import Image

from build_ch2_v3_lettering import CH2_V3_SCORE, V3_INNER_CHAIN, apply_ch2_v3_frame
from build_ch2_v3_system import (
    FIRST_TOUCH,
    PROFILE_07_V3,
    PROFILE_12_V3,
    STAT_NAME,
    STATS,
    WELCOME_14_V3,
)
from grid import cover


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# Опубликованная v2 — контрольная группа; v3 не имеет права её перезаписать.
V2_LOCKS = {
    "CH2_V2_SCROLL_SL_full.jpg": "82299d0fc3f5d823edb4eb9c8158c7d2e2aae02ab5d250146991146ac764c10a",
    "CH2_V2_SL_SHEET.jpg": "60ddadd9a8c77cc44bf3c0a2afcf951d181b3ffb67eafe99423d8bc180eb85e1",
}

EXPECTED_INNER_CHAIN = (
    ("Луке пока не написал.",),
    ("По воскресеньям после четырёх", "здесь обычно пусто."),
    ("Вчера оно видело матч.",),
    ("А тренировку увидит?",),
    ("Сорок два.",),
    ("Мягче.",),
    ("Ещё.",),
    ("Хватит. Проверю.",),
    ("Снова сорок два.",),
    ("Тренировку не считает?",),
)


class ChapterTwoV3ReaderRevisionTests(unittest.TestCase):
    def test_sequence_has_two_explicit_profile_calls(self):
        paths = [path for path, *_ in CH2_V3_SCORE]
        numbers = [number for _, number, *_ in CH2_V3_SCORE]
        self.assertEqual(numbers, [f"{index:02d}" for index in range(1, 16)])
        self.assertEqual(len(paths), 15)
        self.assertEqual(len(set(paths)), 15)
        self.assertTrue(all((ROOT / path).is_file() for path in paths))

        self.assertEqual(paths[5], "ch2/v2_06_profile_call.jpg")
        self.assertEqual(paths[6], "ch2/v3_07_profile.png")
        self.assertEqual(paths[10], "ch2/v3_11_profile_recall.jpg")
        self.assertEqual(paths[11], "ch2/v3_12_profile.png")
        self.assertNotEqual((ROOT / paths[5]).read_bytes(), (ROOT / paths[10]).read_bytes())

    def test_concise_inner_chain_is_exact_and_complete(self):
        self.assertEqual(V3_INNER_CHAIN, EXPECTED_INNER_CHAIN)
        self.assertEqual(len(V3_INNER_CHAIN), 10)

        # «Здесь» появляется после изображения двери, а не после кадра с детьми
        # у гаражей; затем три коротких команды размечают длительную тренировку.
        self.assertEqual(CH2_V3_SCORE[1][-1]["items"], [])
        self.assertEqual(CH2_V3_SCORE[2][-1]["items"][0]["lines"], V3_INNER_CHAIN[1])
        self.assertEqual(CH2_V3_SCORE[7][-1]["items"][0]["lines"], V3_INNER_CHAIN[5])
        self.assertEqual(CH2_V3_SCORE[8][-1]["items"][0]["lines"], V3_INNER_CHAIN[6])
        self.assertEqual(CH2_V3_SCORE[9][-1]["items"][0]["lines"], V3_INNER_CHAIN[7])

    def test_door_has_only_one_physical_text_block(self):
        raw = Image.open(ROOT / "ch2/v3_03_door.jpg").convert("RGB")
        framed = cover(raw, 800, 1420, focus=3)
        _, block_count = apply_ch2_v3_frame("03", framed)
        self.assertEqual(block_count, 1)

    def test_profile_contract_and_identical_before_after_values(self):
        self.assertEqual(STAT_NAME, "ПЕРВОЕ КАСАНИЕ")
        self.assertEqual(FIRST_TOUCH, 42)
        self.assertEqual(STATS[0], ("ПЕРВОЕ КАСАНИЕ", 42))
        self.assertEqual(len(STATS), 12)
        self.assertEqual((ROOT / PROFILE_07_V3).read_bytes(), (ROOT / PROFILE_12_V3).read_bytes())
        for path, expected_size in (
            (PROFILE_07_V3, (800, 1100)),
            (PROFILE_12_V3, (800, 1100)),
            (WELCOME_14_V3, (800, 760)),
        ):
            with self.subTest(path=path), Image.open(ROOT / path) as image:
                self.assertEqual(image.size, expected_size)
                self.assertEqual(image.mode, "RGB")

    def test_removed_mechanics_and_fake_schedule_do_not_return(self):
        source = "\n".join(
            (ROOT / name).read_text(encoding="utf-8")
            for name in (
                "build_ch2_v3_system.py",
                "build_ch2_v3_lettering.py",
                "build_ch2_v3_scroll.py",
            )
        )
        for forbidden in (
            "СВОБОДНОЕ ВРЕМЯ",
            "16:00–17:00",
            "20 МИНУТ",
            "300/300",
            "БЕЗ ИЗМЕНЕНИЙ",
            "Завтра после школы — сюда.",
            "Только теперь сложнее.",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)

    def test_v3_outputs_are_versioned_and_mobile_width(self):
        with Image.open(ROOT / "CH2_V3_SCROLL_SL_full.jpg") as scroll:
            self.assertEqual(scroll.size, (800, 23837))
            self.assertEqual(scroll.mode, "RGB")
        with Image.open(ROOT / "CH2_V3_SL_SHEET.jpg") as sheet:
            self.assertGreater(sheet.width, 1600)
            self.assertGreater(sheet.height, 1800)
            self.assertEqual(sheet.mode, "RGB")

    def test_published_v2_remains_byte_locked(self):
        for relative, expected in V2_LOCKS.items():
            with self.subTest(path=relative):
                self.assertEqual(sha256(ROOT / relative), expected)


if __name__ == "__main__":
    unittest.main()
