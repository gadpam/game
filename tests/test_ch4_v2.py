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
    COACH_ASSESSMENT,
    COACH_INSTRUCTION,
    FINAL_SCORE_STAMP,
    GOAL_MINUTE,
    SUB_MINUTE as LETTERING_SUB_MINUTE,
)
from build_ch4_v2_scroll import (
    OUT_REVIEW_SCROLL,
    OUT_REVIEW_SHEET,
    OUT_SCROLL,
    OUT_SHEET,
    REVIEW_LABEL,
    build as build_scroll,
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
    Path("ch4/v2_10_substitution_65_src.jpg"): "61068917eda283e26653253865dbd0ef97eeca656c38fadd19950929dcf4e42e",
}

QUEST_PANEL = Path("ch4/v2_11_quest.png")
QUEST_PANEL_HASH = "4c5bef3938ae04d0d4a6ab1f487e2338456c77e060db9bb67c6a699f8714d33b"

SECOND_BATCH_SOURCE_HASHES = {
    Path("ch4/v2_12_recovery_one_src.jpg"): "e8878de1e1f30a445b844f3517944af71bf42374ac3c2fa4af9f59a9fc4d4c74",
    Path("ch4/v2_13_recovery_two_src.jpg"): "ade446fbd949f0a8d329c858102c99508e8b0877576da174855e806888525944",
    Path("ch4/v2_14_hold_zone_src.jpg"): "31b794ad8005307bbc4956b5de90fb9711f0d29a9ea51aa13c59904f52e83768",
    Path("ch4/v2_15_recovery_three_src.jpg"): "d84db6011e30d43504fcadac236199288ac48cee7b98b3d9660c234913963752",
    Path("ch4/v2_16_final_whistle_src.jpg"): "8d9853396b90acb1bee1f282e784b37d07da293065af6288c3e1b78c3bb5f325",
    Path("ch4/v2_18_coach_corridor_src.jpg"): "de8a7c0be805c3f158fefe3353b598d2b8aee63991a8da5121049a423614a002",
    Path("ch4/v2_19_protocol_phone_src.jpg"): "4dd810a4a0d91a87120095b290a1066c17663a8485794508dece99dc458a01ae",
    Path("ch4/v2_20_night_bus_src.jpg"): "2eeababb7780669c265ea0b3924a070574810b04f462bf114d411d5d8c6b928e",
}

RESULT_PANEL = Path("ch4/v2_17_result.png")
RESULT_PANEL_HASH = "3e610b98db70d10df7edfdb56ddc0079ee24a4f27a74732925a9531fc37f1f38"


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

    def test_first_review_batch_contains_exactly_ten_ready_frames(self):
        first_ten = CH4_V2_SCORE[:10]
        self.assertEqual([row[1] for row in first_ten], [f"{i:02d}" for i in range(1, 11)])
        self.assertEqual(len({row[0] for row in first_ten}), 10)
        self.assertTrue(all("/v2_" in row[0] for row in first_ten))
        self.assertEqual(CH4_V2_SCORE[9][0], "ch4/v2_10_substitution_65_src.jpg")
        self.assertTrue((ROOT / CH4_V2_SCORE[9][0]).is_file())
        full = ROOT / "CH4_V2_BATCH_01_10_SCROLL.jpg"
        self.assertTrue(full.is_file())
        with Image.open(full) as image:
            self.assertEqual(image.size, (800, 16597))
            self.assertEqual(image.mode, "RGB")
        for index in range(1, 11):
            path = ROOT / f"ch4/v2_lettered_{index:02d}.jpg"
            self.assertTrue(path.is_file(), path)
            with Image.open(path) as image:
                self.assertEqual(image.width, 800)
                self.assertEqual(image.mode, "RGB")

    def test_twenty_frame_candidate_and_second_batch_are_complete(self):
        self.assertEqual(len(CH4_V2_SCORE), 20)
        self.assertEqual([row[1] for row in CH4_V2_SCORE], [f"{i:02d}" for i in range(1, 21)])
        self.assertEqual(len({row[0] for row in CH4_V2_SCORE}), 20)
        self.assertTrue(all("/v2_" in row[0] for row in CH4_V2_SCORE))

        second = ROOT / "CH4_V2_BATCH_11_20_SCROLL.jpg"
        self.assertTrue(second.is_file())
        with Image.open(second) as image:
            self.assertEqual(image.size, (800, 15961))
            self.assertEqual(image.mode, "RGB")
        for index in range(11, 21):
            path = ROOT / f"ch4/v2_lettered_{index:02d}.jpg"
            self.assertTrue(path.is_file(), path)
            with Image.open(path) as image:
                self.assertEqual(image.width, 800)
                self.assertEqual(image.mode, "RGB")
        self.assertFalse((ROOT / "CH4_V2_SCROLL_SL_full.jpg").exists())
        self.assertFalse((ROOT / "CH4_V2_SL_SHEET.jpg").exists())

    def test_full_review_is_marked_and_separate_from_canonical_outputs(self):
        with self.assertRaises(PermissionError):
            build_scroll()
        with self.assertRaises(ValueError):
            build_scroll(approved=True, review=True)

        self.assertEqual(REVIEW_LABEL, "ПРОВЕРОЧНАЯ СБОРКА · НЕ УТВЕРЖДЕНО")
        expected_review = {
            OUT_REVIEW_SCROLL: (800, 32018),
            OUT_REVIEW_SHEET: (1908, 3048),
        }
        for relative, expected_size in expected_review.items():
            with self.subTest(output=relative), Image.open(ROOT / relative) as image:
                self.assertEqual(image.size, expected_size)
                self.assertEqual(image.mode, "RGB")
        self.assertFalse((ROOT / OUT_SCROLL).exists())
        self.assertFalse((ROOT / OUT_SHEET).exists())

    def test_second_batch_sources_and_result_panel_are_byte_locked(self):
        for relative, expected_hash in SECOND_BATCH_SOURCE_HASHES.items():
            with self.subTest(source=relative):
                path = ROOT / relative
                self.assertTrue(path.is_file())
                self.assertEqual(sha256(path), expected_hash)
                with Image.open(path) as image:
                    self.assertGreaterEqual(image.width, 768)
                    self.assertGreaterEqual(image.height, 1200)
                    self.assertEqual(image.mode, "RGB")
        result = ROOT / RESULT_PANEL
        self.assertEqual(sha256(result), RESULT_PANEL_HASH)
        with Image.open(result) as image:
            self.assertEqual(image.size, (800, 1120))
            self.assertEqual(image.mode, "RGB")

    def test_recovery_sequence_is_decision_then_result(self):
        expected = (
            "ch4/v2_11_quest.png",
            "ch4/v2_12_recovery_one_src.jpg",
            "ch4/v2_13_recovery_two_src.jpg",
            "ch4/v2_14_hold_zone_src.jpg",
            "ch4/v2_15_recovery_three_src.jpg",
            "ch4/v2_16_final_whistle_src.jpg",
            "ch4/v2_17_result.png",
        )
        self.assertEqual(tuple(row[0] for row in CH4_V2_SCORE[10:17]), expected)
        self.assertEqual(CH4_V2_SCORE[13][-1]["items"][0]["lines"], ["Не выдёргиваться."])
        self.assertEqual(CH4_V2_SCORE[16][-1]["items"][0]["lines"], ["Двадцать восемь."])

    def test_system_result_and_official_protocol_are_separate(self):
        self.assertEqual(FINAL_SCORE_STAMP, "«ВЕРЕСК» 1:0 «ТОРПЕДО-2»")
        self.assertEqual(
            COACH_ASSESSMENT,
            ("Ветров нормально вошёл.", "Не полез за мячом —", "поэтому успел закрыть зону."),
        )
        system_code = (ROOT / "build_ch4_v2_system.py").read_text(encoding="utf-8")
        lettering = (ROOT / "build_ch4_v2_lettering.py").read_text(encoding="utf-8")
        for forbidden in ("ОТБОРЫ", "6.6", "25 МИНУТ"):
            self.assertNotIn(forbidden, system_code)
        for exact in ("ПРОТОКОЛ МАТЧА", "ВЕРЕСК 1:0", "ТОРПЕДО-2", "25 МИНУТ", "ОТБОРЫ · 2", "ОЦЕНКА · 6.6"):
            self.assertIn(exact, lettering)

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

    def test_batch_builder_rejects_more_than_ten_frames(self):
        over = subprocess.run(
            [sys.executable, "build_ch4_v2_batch.py", "--start", "1", "--end", "11"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(over.returncode, 0)
        self.assertIn("не больше 10", over.stderr)
        crossing = subprocess.run(
            [sys.executable, "build_ch4_v2_batch.py", "--start", "5", "--end", "14"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(crossing.returncode, 0)
        self.assertIn("границу 01–10 / 11–20", crossing.stderr)

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
        self.assertIn("### Кадр 11 · условие", script)
        self.assertIn("### Кадр 17 · результат", script)
        self.assertIn("Никакого `F+`", script)
        self.assertIn("`ПОЗИЦИЯ 70 → 71`", script)
        self.assertNotIn("КВЕСТ · F+", script)


if __name__ == "__main__":
    unittest.main()
