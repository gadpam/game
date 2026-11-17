import unittest

from system_progression import (
    MAX_STAT,
    PROGRESSION_TIERS,
    apply_adaptation,
    effort_required,
    point_cost,
)


class ProgressionCurveTests(unittest.TestCase):
    def test_tier_costs(self):
        self.assertEqual(PROGRESSION_TIERS, (
            (0, 29, 1),
            (30, 39, 2),
            (40, 49, 4),
            (50, 59, 8),
            (60, 69, 16),
        ))
        for value, expected in ((0, 1), (29, 1), (30, 2), (39, 2),
                                (40, 4), (49, 4), (50, 8), (59, 8),
                                (60, 16), (69, 16)):
            with self.subTest(value=value):
                self.assertEqual(point_cost(value), expected)

    def test_author_examples(self):
        self.assertEqual(effort_required(28, 30), 2)
        self.assertEqual(effort_required(45, 47), 8)
        self.assertEqual(effort_required(60, 62), 32)
        self.assertEqual(effort_required(45, 47) // effort_required(28, 30), 4)

    def test_chapter_one_reward_fits_curve(self):
        result = apply_adaptation(26, 2)
        self.assertEqual(result.value, 28)
        self.assertEqual(result.gained, 2)
        self.assertEqual(result.banked, 0)

    def test_same_effort_is_not_an_instant_gain_at_45(self):
        first = apply_adaptation(45, 2)
        self.assertEqual((first.value, first.banked), (45, 2))
        second = apply_adaptation(first.value, 2, banked=first.banked)
        self.assertEqual((second.value, second.banked), (46, 0))

    def test_four_equal_match_confirmations_take_45_to_47(self):
        value = 45
        banked = 0
        for _ in range(4):
            result = apply_adaptation(value, 2, banked=banked)
            value, banked = result.value, result.banked
        self.assertEqual((value, banked), (47, 0))

    def test_crossing_tier_uses_each_point_cost(self):
        self.assertEqual(effort_required(29, 31), 3)
        result = apply_adaptation(29, 3)
        self.assertEqual((result.value, result.banked), (31, 0))

    def test_cap_discards_surplus(self):
        result = apply_adaptation(69, 999)
        self.assertEqual(result.value, MAX_STAT)
        self.assertTrue(result.capped)
        self.assertEqual(result.banked, 0)

    def test_invalid_values_are_rejected(self):
        with self.assertRaises(ValueError):
            point_cost(70)
        with self.assertRaises(ValueError):
            effort_required(30, 29)
        with self.assertRaises(ValueError):
            apply_adaptation(45, -1)
        with self.assertRaises(ValueError):
            apply_adaptation(45, 1, banked=4)


if __name__ == '__main__':
    unittest.main()
