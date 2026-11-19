import hashlib
import unittest
from pathlib import Path

from PIL import Image

from ch4_roster import STARTERS, SUBS, SQUAD_NUMBERS, VETROV_FUTURE_NUMBER
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
