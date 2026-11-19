import hashlib
import subprocess
import sys
import unittest
from pathlib import Path

from PIL import Image

from ch4_roster import STARTERS, SUBS, SQUAD_NUMBERS, VETROV_FUTURE_NUMBER
from build_ch4_v2_lettering import (
    CALL_MINUTE,
    CH4_V2_SCORE,
    COACH_INSTRUCTION,
    GOAL_MINUTE,
    SUB_MINUTE as LETTERING_SUB_MINUTE,
)
from ch4_v2_contract import (
    AWAY_SCORE,
    AWAY_TEAM,
    DECISION_AFTER,
    DECISION_BEFORE,
    FINAL_SCORE,
    HOME_SCORE,
    HOME_TEAM,
    KIT_REFERENCE,
    MATCH_RATING,
    MINUTES_PLAYED,
    OFFICIAL_TACKLES,
    QUEST_RANK,
    RECOVERY_GOAL,
    SHATSKY_NUMBER,
    STADIUM_REFERENCE,
    SUB_MINUTE,
    VERESK_KIT,
    VETROV_NUMBER,
)


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


MASTER_HASHES = {
    STADIUM_REFERENCE: "9f216957e6b95f38f6b3f0dcd97818cada73a4d9676a1a9e53b1f1715ad77e0d",
    KIT_REFERENCE: "43725f3ff8c2c242b91aa0fbb0dba5d03aaa12011dc8ac19c255ba2bb9bb4c91",
}

FIRST_BATCH_SOURCE_HASHES = {
    Path("ch4/v2_01_bus_arrival_src.jpg"): "385400a71f74e83dfdf8dd2d2ba745370a810fa475b9e9ef5251070a27384f6f",
    Path("ch4/v2_02_lineup.jpg"): "551788e4feb8e26718e6227af66fe5c281a71e148da371d48d4af8b71e0708cc",
    STADIUM_REFERENCE: MASTER_HASHES[STADIUM_REFERENCE],
    Path("ch4/v2_04_lockeroom_before_src.jpg"): "0aa53644f338a840d98243c1db61826677acca0c5455492bdff88095fcdba4a9",
    Path("ch4/v2_05_bench_first_half_src.jpg"): "91d27c81819cdab46e2fbc63328317b0e0a5a4c0b0544a4e0d4f29f53453f493",
    Path("ch4/v2_06_veresk_goal_src.jpg"): "6b23e253cccf269e2ac3e0cc014c19ebe41577a208948ea59182869171771cb6",
    Path("ch4/v2_07_halftime_corridor_src.jpg"): "91d2687d46e5f621385813c5716a2811d04ee0ad769fd5cd9918ed8ca9cfb1cb",
    Path("ch4/v2_08_coach_calls_62_src.jpg"): "21acb1593b587b281c911f0eef41d42d13718acf50b9cf333bdefbd6fa7a3d12",
    Path("ch4/v2_09_touchline_instruction_src.jpg"): "cd56753fa444d106e8fdb7adc7285e6b905482eecf916651944a568eeebbd61b",
}

QUEST_PANEL = Path("ch4/v2_11_quest.png")
QUEST_PANEL_HASH = "dcab6a73a275d8baf58c224c1af5753a0dc00834fe58c9841a1f9d6b02c8f6b3"


class ChapterFourV2PlanningTests(unittest.TestCase):
    def test_current_canon_enters_chapter_four_without_rank_skip(self):
        self.assertEqual(QUEST_RANK, "F−")
        self.assertEqual((DECISION_BEFORE, DECISION_AFTER), (26, 28))
        self.assertEqual(DECISION_AFTER - DECISION_BEFORE, 2)
        self.assertEqual(RECOVERY_GOAL, 3)
        self.assertEqual(OFFICIAL_TACKLES, 2)
        self.assertEqual(MATCH_RATING, "6.6")

    def test_match_result_and_substitution_arithmetic_are_exact(self):
        self.assertEqual(
            (HOME_TEAM, HOME_SCORE, AWAY_SCORE, AWAY_TEAM, FINAL_SCORE),
            ("ВЕРЕСК", 1, 0, "ТОРПЕДО-2", "ВЕРЕСК 1:0 ТОРПЕДО-2"),
        )
        self.assertEqual(SUB_MINUTE, "65′")
        self.assertEqual(MINUTES_PLAYED, 25)

    def test_lineup_keeps_eighteen_unique_numbers(self):
        self.assertEqual(len(STARTERS), 11)
        self.assertEqual(len(SUBS), 7)
        self.assertEqual(len(set(STARTERS + SUBS)), 18)
        self.assertEqual(len(set(SQUAD_NUMBERS.values())), 18)
        self.assertIn("ШАТСКИЙ", STARTERS)
        self.assertIn("ВЕТРОВ", SUBS)
        self.assertEqual(SQUAD_NUMBERS["ШАТСКИЙ"], SHATSKY_NUMBER)
        self.assertEqual(SQUAD_NUMBERS["ВЕТРОВ"], VETROV_NUMBER)
        self.assertEqual(VETROV_NUMBER, 19)
        self.assertEqual(VETROV_FUTURE_NUMBER, 8)
        self.assertNotIn(VETROV_FUTURE_NUMBER, SQUAD_NUMBERS.values())

    def test_visual_masters_are_versioned_rgb_and_byte_locked(self):
        for relative, expected_hash in MASTER_HASHES.items():
            path = ROOT / relative
            with self.subTest(master=relative):
                self.assertTrue(path.is_file())
                self.assertEqual(sha256(path), expected_hash)
                with Image.open(path) as image:
                    self.assertEqual(image.size, (768, 1376))
                    self.assertEqual(image.mode, "RGB")
        self.assertEqual(VERESK_KIT["shirt"], "#49365C")
        self.assertNotEqual(VERESK_KIT["shirt"], "#000000")
        self.assertNotEqual(VERESK_KIT["shorts"], "#000000")

    def test_first_review_batch_has_nine_ready_frames_and_waits_for_substitution_art(self):
        first_nine = CH4_V2_SCORE[:9]
        self.assertEqual([row[1] for row in first_nine], [f"{i:02d}" for i in range(1, 10)])
        self.assertEqual(len({row[0] for row in first_nine}), 9)
        self.assertTrue(all("/v2_" in row[0] for row in first_nine))
        self.assertEqual(CH4_V2_SCORE[9][0], "ch4/v2_10_substitution_65_src.jpg")
        self.assertFalse((ROOT / CH4_V2_SCORE[9][0]).exists())
        self.assertFalse((ROOT / "CH4_V2_BATCH_01_10_SCROLL.jpg").exists())
        partial = ROOT / "CH4_V2_BATCH_01_09_SCROLL.jpg"
        self.assertTrue(partial.is_file())
        with Image.open(partial) as image:
            self.assertEqual(image.size, (800, 14873))
            self.assertEqual(image.mode, "RGB")
        for index in range(1, 10):
            path = ROOT / f"ch4/v2_lettered_{index:02d}.jpg"
            self.assertTrue(path.is_file(), path)
            with Image.open(path) as image:
                self.assertEqual(image.width, 800)
                self.assertEqual(image.mode, "RGB")

    def test_first_batch_sources_and_quest_panel_are_byte_locked(self):
        for relative, expected_hash in FIRST_BATCH_SOURCE_HASHES.items():
            with self.subTest(source=relative):
                path = ROOT / relative
                self.assertTrue(path.is_file())
                self.assertEqual(sha256(path), expected_hash)
                with Image.open(path) as image:
                    self.assertEqual(image.mode, "RGB")
        quest = ROOT / QUEST_PANEL
        self.assertEqual(sha256(quest), QUEST_PANEL_HASH)
        with Image.open(quest) as image:
            self.assertEqual(image.size, (800, 1120))
            self.assertEqual(image.mode, "RGB")

    def test_first_batch_lettering_contract_is_exact(self):
        self.assertEqual((GOAL_MINUTE, CALL_MINUTE, LETTERING_SUB_MINUTE), ("38′", "62′", "65′"))
        self.assertEqual(COACH_INSTRUCTION, ("Подбери за Шатским.", "И первый пас — проще."))
        lettering = (ROOT / "build_ch4_v2_lettering.py").read_text(encoding="utf-8")
        for forbidden in ("68′", "F+", "ПОЗИЦИЯ 70 → 71"):
            self.assertNotIn(forbidden, lettering)

    def test_batch_builder_rejects_more_than_ten_or_missing_tenth_frame(self):
        over = subprocess.run(
            [sys.executable, "build_ch4_v2_batch.py", "--start", "1", "--end", "11"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(over.returncode, 0)
        missing = subprocess.run(
            [sys.executable, "build_ch4_v2_batch.py", "--start", "1", "--end", "10"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("v2_10_substitution_65_src.jpg", missing.stderr)

    def test_script_contains_exact_contract_and_production_guards(self):
        script = (ROOT / "docs/CH4_SCRIPT_CANDIDATE.md").read_text(encoding="utf-8")
        for exact in (
            "3 ВОЗВРАТА МЯЧА",
            "ИЗ СВОЕЙ ЗОНЫ",
            "ПРИНЯТИЕ РЕШЕНИЙ 26 → 28",
            "«ВЕРЕСК» 1:0 «ТОРПЕДО-2»",
            "ОТБОРЫ · 2",
            "ОЦЕНКА · 6.6",
            "65′",
            "25 минут",
            "не более `10` кадров",
        ):
            with self.subTest(exact=exact):
                self.assertIn(exact, script)
        self.assertIn("Никакого `F+`", script)
        self.assertIn("`ПОЗИЦИЯ 70 → 71`", script)
        self.assertNotIn("КВЕСТ · F+", script)


if __name__ == "__main__":
    unittest.main()
