import hashlib
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

from build_ch3_v2_batch import (
    MAX_BATCH_FRAMES,
    batch_output,
    build as build_batch,
    frame_output,
)
from build_ch3_v2_bus import SRC as BUS_SRC, build as build_bus
from build_ch3_v2_epilogue import (
    BUS_WINDOW_OUT,
    EMPTY_OUT,
    REACTION_OUT,
    REACTION_SRC,
    build as build_epilogue,
)
from build_ch3_v2_numbers import (
    BACK_PLACEMENTS,
    SHORTS_PLACEMENTS,
    TEAMMATE_BACK_PLACEMENTS,
    TEAMMATE_SHORTS_PLACEMENTS,
)
from build_ch3_v2_revisions import (
    AWAY_SCORE,
    AWAY_TEAM,
    FINAL_SCORE,
    HOME_SCORE,
    HOME_TEAM,
    SCOREBOARD_OUT,
    SCORE_MINUTE,
    TACKLE_OUT,
    WHISTLE_OUT,
    WHISTLE_SRC,
    build as build_revisions,
)
from build_ch3_v2_subbed import SRC as SUBBED_SRC, build as build_subbed
from build_ch3_v2_lettering import (
    CH3_V2_SCORE,
    COACH_AFTER,
    COACH_AFTER_RENDER,
    COACH_BRIEFING,
    FINAL_WHISTLE_SFX,
    INNER_CHAIN,
    MATCH_STAMP,
    MINUTE_STAMP,
    OPENING_STAMP,
    SUB_CALL,
    VETROV_REPLY,
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
from ch3_roster import (
    SQUAD_NUMBERS,
    STARTERS,
    SUBS,
    VETROV_FUTURE_NUMBER,
    VETROV_NUMBER,
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
    ("Шатского после травмы берегут.",),
    ("В центре — я.",),
    ("Три.",),
    ("Не лезть.",),
    ("Ждать.",),
    ("Ровно час.",),
    ("Три чистых.",),
    ("Двадцать восемь.",),
    ("Квест сработал.",),
)

EXPECTED_SQUAD_NUMBERS = {
    "ГРОМОВ": 1,
    "САВЕЛЬЕВ": 2,
    "АНДРЕЕВ": 3,
    "КАРИМОВ": 4,
    "ЛЕВЧУК": 5,
    "ТКАЧЁВ": 6,
    "ВЕТРОВ": 19,
    "ГОНЧАР": 7,
    "НОВИК": 9,
    "МАРЧЕНКО": 10,
    "ДЕНИСОВ": 11,
    "БОБРОВ": 12,
    "МЕЛЬНИК": 14,
    "КИСЕЛЁВ": 13,
    "ШАТСКИЙ": 16,
    "КОВАЛЁВ": 17,
    "РОМАНОВ": 18,
    "ЮРЧЕНКО": 21,
}


class ChapterThreeV2CandidateTests(unittest.TestCase):
    def test_quest_uses_only_f_minus_and_canonical_growth(self):
        self.assertEqual(QUEST_RANK, "F−")
        self.assertEqual(TACKLE_BEFORE, 26)
        self.assertEqual(TACKLE_AFTER, 28)
        self.assertEqual(GOAL, 3)
        self.assertEqual(TACKLE_AFTER - TACKLE_BEFORE, 2)

    def test_twenty_frame_candidate_is_complete_and_unique(self):
        paths = [path for path, *_ in CH3_V2_SCORE]
        numbers = [number for _, number, *_ in CH3_V2_SCORE]
        self.assertEqual(numbers, [f"{index:02d}" for index in range(1, 21)])
        self.assertEqual(len(paths), 20)
        self.assertEqual(len(set(paths)), 20)
        self.assertTrue(all((ROOT / path).is_file() for path in paths))
        self.assertTrue(all("/v2_" in path for path in paths))

        tackle_paths = (
            "ch3/v2_06_tackle_one.jpg",
            "ch3/v2_07_tackle_two.jpg",
            "ch3/v2_09_tackle_three.jpg",
        )
        self.assertEqual((paths[5], paths[6], paths[8]), tackle_paths)
        self.assertEqual(len({sha256(ROOT / path) for path in tackle_paths}), 3)

    def test_first_review_batch_contains_exactly_ten_finalized_frames(self):
        self.assertEqual(MAX_BATCH_FRAMES, 10)
        with self.assertRaises(ValueError):
            build_batch(1, 11)

        output = ROOT / batch_output(1, 10)
        self.assertTrue(output.is_file())
        with Image.open(output) as image:
            self.assertEqual(image.width, 800)
            self.assertEqual(image.height, 15478)

        hashes = set()
        for index, (_, number, height, *_rest) in enumerate(CH3_V2_SCORE[:10], start=1):
            self.assertEqual(number, f"{index:02d}")
            path = ROOT / frame_output(number)
            self.assertTrue(path.is_file())
            with Image.open(path) as image:
                self.assertEqual(image.size, (800, height))
                self.assertEqual(image.mode, "RGB")
            hashes.add(sha256(path))
        self.assertEqual(len(hashes), 10)

    def test_second_review_batch_contains_exactly_ten_finalized_frames(self):
        with self.assertRaises(ValueError):
            build_batch(10, 20)

        output = ROOT / batch_output(11, 20)
        self.assertTrue(output.is_file())
        with Image.open(output) as image:
            self.assertEqual(image.size, (800, 15953))

        hashes = set()
        for index, (_, number, height, *_rest) in enumerate(
            CH3_V2_SCORE[10:], start=11
        ):
            self.assertEqual(number, f"{index:02d}")
            path = ROOT / frame_output(number)
            self.assertTrue(path.is_file())
            with Image.open(path) as image:
                self.assertEqual(image.size, (800, height))
                self.assertEqual(image.mode, "RGB")
            hashes.add(sha256(path))
        self.assertEqual(len(hashes), 10)
        self.assertNotEqual(
            sha256(ROOT / batch_output(1, 10)),
            sha256(output),
        )

    def test_lineup_has_eighteen_unique_players_and_vetrov_starts(self):
        self.assertEqual(len(STARTERS), 11)
        self.assertEqual(len(SUBS), 7)
        self.assertEqual(len(set(STARTERS + SUBS)), 18)
        self.assertIn("ВЕТРОВ", STARTERS)
        self.assertIn("ШАТСКИЙ", SUBS)
        self.assertIn("МЕЛЬНИК", SUBS)
        self.assertEqual(SQUAD_NUMBERS, EXPECTED_SQUAD_NUMBERS)
        self.assertEqual(len(set(SQUAD_NUMBERS.values())), 18)
        self.assertEqual(VETROV_NUMBER, 19)
        self.assertEqual(VETROV_FUTURE_NUMBER, 8)
        self.assertNotIn(VETROV_FUTURE_NUMBER, SQUAD_NUMBERS.values())
        self.assertEqual(
            set(SHORTS_PLACEMENTS),
            {"03", "06", "07", "08", "09", "10", "11"},
        )
        self.assertEqual(set(BACK_PLACEMENTS), {"14", "17"})
        self.assertEqual(set(TEAMMATE_SHORTS_PLACEMENTS), {"13"})
        self.assertEqual(set(TEAMMATE_BACK_PLACEMENTS), {"14"})
        visible_numbers = {
            number
            for placements in (
                TEAMMATE_SHORTS_PLACEMENTS,
                TEAMMATE_BACK_PLACEMENTS,
            )
            for rows in placements.values()
            for number, *_ in rows
        }
        self.assertEqual(visible_numbers, {2, 7, 9, 14})

    def test_text_contract_is_concise_and_matches_script(self):
        self.assertEqual(INNER_CHAIN, EXPECTED_INNER_CHAIN)
        self.assertEqual(OPENING_STAMP, "КУБОК · ДЕНЬ МАТЧА")
        self.assertEqual(MATCH_STAMP, "«ГОРЕЦ» — «ТОРПЕДО-2» · КУБОК")
        self.assertEqual(MINUTE_STAMP, "60′")
        self.assertEqual(FINAL_WHISTLE_SFX, "ФЬЮ-ИТЬ!")
        self.assertEqual(
            (HOME_TEAM, HOME_SCORE, AWAY_SCORE, AWAY_TEAM, SCORE_MINUTE, FINAL_SCORE),
            ("ГОРЕЦ", 0, 1, "ТОРПЕДО-2", "89′", "ГОРЕЦ 0:1 ТОРПЕДО-2"),
        )
        self.assertEqual(COACH_BRIEFING, ("Первый час играешь.", "Потом выйдет Мельник."))
        self.assertEqual(SUB_CALL, ("ВЕТРОВ УХОДИТ!", "МЕЛЬНИК ВЫХОДИТ!"))
        self.assertEqual(
            COACH_AFTER,
            (("Замена была по плану.", "К твоей игре вопросов нет."),
             ("Начал ждать момент.", "Так и играй.")),
        )
        self.assertEqual(
            " ".join(COACH_AFTER_RENDER[0]),
            "Замена была по плану. К твоей игре вопросов нет.",
        )
        self.assertEqual(COACH_AFTER_RENDER[1], COACH_AFTER[1])

        script = (ROOT / "docs/CH3_SCRIPT_CANDIDATE.md").read_text(encoding="utf-8").casefold()
        exact_lines = [line for group in INNER_CHAIN for line in group]
        exact_lines += list(COACH_BRIEFING + VETROV_REPLY + SUB_CALL)
        exact_lines += [line for group in COACH_AFTER for line in group]
        exact_lines += [OPENING_STAMP, MATCH_STAMP, MINUTE_STAMP, FINAL_WHISTLE_SFX]
        for line in exact_lines:
            with self.subTest(script_line=line):
                self.assertIn(line.casefold(), script)
        self.assertIn(FINAL_SCORE.casefold(), script)
        for obsolete in (
            "Мельник меняет",
            "Все три — чисто",
            "Вот это оставь",
            "После бедра",
            "Не из-за тебя",
        ):
            with self.subTest(obsolete=obsolete):
                self.assertNotIn(obsolete.casefold(), script)

    def test_new_sources_do_not_restore_legacy_mechanics(self):
        source = "\n".join(
            (ROOT / name).read_text(encoding="utf-8")
            for name in (
                "ch3_roster.py",
                "build_ch3_v2_insets.py",
                "build_ch3_v2_numbers.py",
                "build_ch3_v2_revisions.py",
                "build_ch3_v2_epilogue.py",
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
            "МЕЛЬНИК МЕНЯЕТ",
            "ВСЕ ТРИ — ЧИСТО",
            "ВОТ ЭТО ОСТАВЬ",
            "ПОСЛЕ БЕДРА",
            "НЕ ИЗ-ЗА ТЕБЯ",
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
            sha256(ROOT / "ch3/v2_17_coach.jpg"),
            sha256(ROOT / "ch3/g21_coach.jpg"),
        )

        bus = ROOT / "ch3/v2_20_bus.jpg"
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

        revision_outputs = tuple(ROOT / path for path in (
            TACKLE_OUT, SCOREBOARD_OUT, WHISTLE_OUT
        ))
        before = tuple(sha256(path) for path in revision_outputs)
        build_revisions()
        self.assertEqual(before, tuple(sha256(path) for path in revision_outputs))
        self.assertNotEqual(sha256(ROOT / WHISTLE_SRC), sha256(ROOT / WHISTLE_OUT))
        with Image.open(ROOT / SCOREBOARD_OUT) as scoreboard:
            self.assertEqual(scoreboard.size, (800, 1320))
        self.assertNotIn("ch3/v2_12_bench_detail.jpg", [path for path, *_ in CH3_V2_SCORE])

        epilogue_outputs = tuple(ROOT / path for path in (
            REACTION_OUT, EMPTY_OUT, BUS_WINDOW_OUT
        ))
        before = tuple(sha256(path) for path in epilogue_outputs)
        build_epilogue()
        self.assertEqual(before, tuple(sha256(path) for path in epilogue_outputs))
        self.assertTrue(str(REACTION_SRC).startswith("ch3/v2_"))
        self.assertFalse(str(REACTION_SRC).startswith("ch1/"))

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
