import hashlib
import unittest
from pathlib import Path

from PIL import Image

from build_ch2_lettering import CH2_SCORE
from build_ch2_system import (
    FIRST_TOUCH,
    PROFILE_07,
    PROFILE_11,
    PROFILE_TITLE,
    STAT_NAME,
    WELCOME_TEXT,
)


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


LEGACY_HASHES = {
    "CH2_SCROLL_SL_full.jpg": "44de2df3d961dad9288e19f7080691b4666640d2b8447ca6b0938dd1101850ec",
    "CH2_SL_SHEET.jpg": "4afebd00ad281da211afe65936b062ef948881dc6092e70aec6583a52a406073",
    "ch2/c_room.jpg": "4a09c7f27fb66999606eb496abbb58d19f061c6dafd903c9c16cb7cb96655e73",
    "ch2/c_garage.jpg": "904aefd8dcd54c2b37e53c8a1dd062391eb56ac9a53ecb14cdba931b636ed12a",
    "ch2/c_door.jpg": "6172e59feb3a505e29b4648f5437d5c6ade6ca291c8f5207192febca1bf56c96",
    "ch2/c_locker_empty.jpg": "5506238201d0ebabfe52693b27128a3e4134b0c81755dfbd0823302ca327b0a5",
    "ch2/c_notebook.jpg": "54ae51ad6c66ad1f4a95e36d6b23daa56a14a4bc160e11aa55cc0308265483fa",
    "ch2/c_manege.jpg": "2f6f0b3123ff3a4cab501c2c30cf9601229fabf4a6606abef79c54ced0f335bf",
    "ch2/p14_quest.png": "2ae78b49e567887d590c635a3860beec401f10d2a4c93801b5fa39a00ad8ef2b",
    "ch2/c_touch.jpg": "453120cac88342ce442c1606ca5895bcaca4ab4b09baa20be8795d4a9cc69089",
    "ch2/c_loss_ball.jpg": "e728cec71c38682a07fa0b78234a7275a0e32ca113cedaca91a86c2624cabc91",
    "ch2/p22_done.png": "08ae143559689afc457ce35c93f885273d8f4f8eec876edffcd2dc0806f662c3",
    "ch2/c_guard.jpg": "e618155c305c8439eaa03732b6d44f40786bc5ae22ebfa99959d7021752fa1c3",
    "ch2/p24_total.png": "da040e81f789ef49c8e18637a36b396a40da9137fdd88a5f01d9f42b6852290a",
    "ch2/c_lamp_off.jpg": "0b0e92720a93ac1521f1e9a9d7ce8a55d8a4cd8464bf39552b8b8840e3e6156f",
}


class ChapterTwoV2Tests(unittest.TestCase):
    def test_sequence_is_fourteen_unique_versioned_frames(self):
        paths = [path for path, *_ in CH2_SCORE]
        numbers = [number for _, number, *_ in CH2_SCORE]
        self.assertEqual(numbers, [f"{index:02d}" for index in range(1, 15)])
        self.assertEqual(len(paths), 14)
        self.assertEqual(len(set(paths)), 14)
        self.assertTrue(all("/v2_" in path for path in paths))
        self.assertTrue(all((ROOT / path).is_file() for path in paths))

    def test_system_contract_and_identical_profiles(self):
        self.assertEqual(PROFILE_TITLE, "ПРОФИЛЬ")
        self.assertEqual(STAT_NAME, "ПЕРВОЕ КАСАНИЕ")
        self.assertEqual(FIRST_TOUCH, 42)
        self.assertEqual(WELCOME_TEXT, "ДОБРО ПОЖАЛОВАТЬ, ИГРОК")
        self.assertEqual((ROOT / PROFILE_07).read_bytes(), (ROOT / PROFILE_11).read_bytes())
        with Image.open(ROOT / PROFILE_07) as profile:
            self.assertEqual(profile.size, (800, 1100))
            self.assertEqual(profile.mode, "RGB")

    def test_final_room_preserves_legacy_art_byte_for_byte(self):
        self.assertEqual(
            (ROOT / "ch2/v2_14_room_night.jpg").read_bytes(),
            (ROOT / "ch2/c_lamp_off.jpg").read_bytes(),
        )

    def test_versioned_scroll_outputs(self):
        with Image.open(ROOT / "CH2_V2_SCROLL_SL_full.jpg") as scroll:
            self.assertEqual(scroll.size, (800, 21856))
            self.assertEqual(scroll.mode, "RGB")
        with Image.open(ROOT / "CH2_V2_SL_SHEET.jpg") as sheet:
            self.assertGreater(sheet.width, 1600)
            self.assertGreater(sheet.height, 1800)
            self.assertEqual(sheet.mode, "RGB")

    def test_legacy_chapter_two_assets_are_locked(self):
        for relative, expected in LEGACY_HASHES.items():
            with self.subTest(path=relative):
                self.assertEqual(sha256(ROOT / relative), expected)


if __name__ == "__main__":
    unittest.main()
