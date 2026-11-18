import hashlib
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

from build_ch3_v2_bus import SRC as BUS_SRC, build as build_bus
from build_ch3_v2_insets import STARTERS, SUBS
from build_ch3_v2_subbed import SRC as SUBBED_SRC, build as build_subbed
from build_ch3_v2_lettering import (
    CH3_V2_SCORE,
    COACH_AFTER,
    COACH_BRIEFING,
    INNER_CHAIN,
    MATCH_STAMP,
    MINUTE_STAMP,
    OPENING_STAMP,
    SUB_CALL,
)
from build_ch3_v2_scroll import (
    OUT_SCROLL,
    OUT_SHEET,
    build as build_scroll,
)
from build_ch3_v2_system import (
    DONE,
    GOAL,
    QUEST,
    QUEST_RANK,
    TACKLE_AFTER,
    TACKLE_BEFORE,
)


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


LEGACY_LOCKS = {
    "ch3/p09_quest.png": "a151958f3aaf7448df0395d138428aaf983ef72251e2461fd0f7ffb7e929d74d",
    "ch3/p22_done.png": "832a3ea300767a26a623bd1c1ccb3d6c3ac3883ceb40a4230e4203cbe8a7d57b",
    "CH3_SCROLL_SL_full.jpg": "3e2ef5e5c16dc279cda9262b2ffd7d2bb46558b8c5176fbbacbfcff19dee7f22",
    "CH3_SL_SHEET.jpg": "ee4afa53976af68037b7cdd64fce70ee63f0799cf9c3218246ad2a56082f8e5e",
    "ch3/g02_kitchen.jpg": "4b37878d45dd369ffd10b7205600cc7480869ea83d9b62d757f857716ce80bbf",
    "ch3/g03_lineup.jpg": "49a7b33c1653476a895234cd2b2eed573d1d3cbcc92c7a2b94bdd80e86951c32",
    "ch3/g24_bus.jpg": "b16e7afda78abe3d11cf8995533310654aaeb41c003c90f215f3afd731635b14",
}

EXPECTED_INNER_CHAIN = (
    ("Сегодня — с первых минут.",),
    ("Шатского после бедра берегут.",),
    ("В центре — я.",),
    ("Три.",),
    ("Не лезть.",),
    ("Ждать.",),
    ("Ровно час.",),
    ("Все три — чисто.",),
    ("Двадцать восемь.",),
)


class ChapterThreeV2CandidateTests(unittest.TestCase):
    def test_quest_uses_only_f_minus_and_canonical_growth(self):
        self.assertEqual(QUEST_RANK, "F−")
        self.assertEqual(TACKLE_BEFORE, 26)
        self.assertEqual(TACKLE_AFTER, 28)
        self.assertEqual(GOAL, 3)
        self.assertEqual(TACKLE_AFTER - TACKLE_BEFORE, 2)

    def test_fourteen_frame_candidate_is_complete_and_unique(self):
        paths = [path for path, *_ in CH3_V2_SCORE]
        numbers = [number for _, number, *_ in CH3_V2_SCORE]
        self.assertEqual(numbers, [f"{index:02d}" for index in range(1, 15)])
        self.assertEqual(len(paths), 14)
        self.assertEqual(len(set(paths)), 14)
        self.assertTrue(all((ROOT / path).is_file() for path in paths))
        self.assertTrue(all("/v2_" in path for path in paths))

        tackle_paths = (
            "ch3/v2_06_tackle_one.jpg",
            "ch3/v2_07_tackle_two.jpg",
            "ch3/v2_09_tackle_three.jpg",
        )
        self.assertEqual((paths[5], paths[6], paths[8]), tackle_paths)
        self.assertEqual(len({sha256(ROOT / path) for path in tackle_paths}), 3)

    def test_lineup_has_eighteen_unique_players_and_vetrov_starts(self):
        self.assertEqual(len(STARTERS), 11)
        self.assertEqual(len(SUBS), 7)
        self.assertEqual(len(set(STARTERS + SUBS)), 18)
        self.assertIn("ВЕТРОВ", STARTERS)
        self.assertIn("ШАТСКИЙ", SUBS)
        self.assertIn("МЕЛЬНИК", SUBS)

    def test_text_contract_is_concise_and_matches_script(self):
        self.assertEqual(INNER_CHAIN, EXPECTED_INNER_CHAIN)
        self.assertEqual(OPENING_STAMP, "КУБОК · ДЕНЬ МАТЧА")
        self.assertEqual(MATCH_STAMP, "«ГОРЕЦ» — «ТОРПЕДО-2» · КУБОК")
        self.assertEqual(MINUTE_STAMP, "60′")
        self.assertEqual(COACH_BRIEFING, ("Первый час — твой.", "Потом выйдет Мельник."))
        self.assertEqual(SUB_CALL, ("ВЕТРОВ!", "МЕЛЬНИК МЕНЯЕТ!"))
        self.assertEqual(
            COACH_AFTER,
            (("Замена была по плану.", "Не из-за тебя."),
             ("Начал ждать момент.", "Вот это оставь.")),
        )

    def test_new_sources_do_not_restore_legacy_mechanics(self):
        source = "\n".join(
            (ROOT / name).read_text(encoding="utf-8")
            for name in (
                "build_ch3_v2_insets.py",
                "build_ch3_v2_system.py",
                "build_ch3_v2_subbed.py",
                "build_ch3_v2_bus.py",
                "build_ch3_v2_lettering.py",
                "build_ch3_v2_scroll.py",
            )
        )
        for forbidden in (
            'QUEST_RANK = "F+"',
            "ОТБОР 25",
            "60 МИНУТ · БЕЗ ЗАМЕНЫ",
            "НЕ БОЛЬШЕ ТРЁХ ПОТЕРЬ",
            "НАГРАДА ТОЛЬКО ПРИ ВЫПОЛНЕНИИ",
            "ИВ 68",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source.upper())

    def test_panels_and_versioned_clean_art_are_rgb(self):
        expected_sizes = {
            str(QUEST): (800, 920),
            str(DONE): (800, 830),
        }
        for relative, expected in expected_sizes.items():
            with self.subTest(path=relative), Image.open(ROOT / relative) as image:
                self.assertEqual(image.size, expected)
                self.assertEqual(image.mode, "RGB")

        for relative in (path for path, *_ in CH3_V2_SCORE):
            with self.subTest(path=relative), Image.open(ROOT / relative) as image:
                self.assertEqual(image.mode, "RGB")
                self.assertGreaterEqual(image.width, 768)
                self.assertGreaterEqual(image.height, 830)

        self.assertEqual(
            sha256(ROOT / "ch3/v2_04_pitch.jpg"),
            sha256(ROOT / "ch3/g07_pitch.jpg"),
        )
        self.assertEqual(
            sha256(ROOT / "ch3/v2_12_coach.jpg"),
            sha256(ROOT / "ch3/g21_coach.jpg"),
        )

        bus = ROOT / "ch3/v2_14_bus.jpg"
        subbed = ROOT / "ch3/v2_10_subbed.jpg"
        self.assertNotEqual(sha256(bus), sha256(ROOT / BUS_SRC))
        self.assertNotEqual(sha256(subbed), sha256(ROOT / SUBBED_SRC))
        with TemporaryDirectory() as directory:
            rebuilt_bus = Path(directory) / "bus.jpg"
            rebuilt_subbed = Path(directory) / "subbed.jpg"
            build_bus(ROOT / BUS_SRC, rebuilt_bus)
            build_subbed(ROOT / SUBBED_SRC, rebuilt_subbed)
            self.assertEqual(sha256(bus), sha256(rebuilt_bus))
            self.assertEqual(sha256(subbed), sha256(rebuilt_subbed))

    def test_full_scroll_is_intentionally_deferred(self):
        with self.assertRaises(PermissionError):
            build_scroll()
        self.assertFalse((ROOT / OUT_SCROLL).exists())
        self.assertFalse((ROOT / OUT_SHEET).exists())

    def test_legacy_chapter_three_is_byte_locked(self):
        for relative, expected in LEGACY_LOCKS.items():
            with self.subTest(path=relative):
                self.assertEqual(sha256(ROOT / relative), expected)


if __name__ == "__main__":
    unittest.main()
