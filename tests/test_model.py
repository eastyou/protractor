"""角度分类与出题逻辑测试。"""

import unittest
from dataclasses import FrozenInstanceError

from protractor.model import (
    KINDS,
    DIRECTIONS,
    AngleProblem,
    ProtractorError,
    check_angle,
    classify,
    display_angle,
    generate_problems,
)


def expected_class(value):
    if value == 0:
        return "零角"
    if value < 90:
        return "锐角"
    if value == 90:
        return "直角"
    if value < 180:
        return "钝角"
    return "平角"


class GeneratedClassificationTest(unittest.TestCase):
    """用数据驱动覆盖 0–180° 的分类。"""


def _make_classification_test(value):
    def test(self):
        self.assertEqual(classify(value), expected_class(value))

    test.__doc__ = "角度 %d 的分类" % value
    return test


for _value in range(0, 181, 3):
    setattr(
        GeneratedClassificationTest,
        "test_angle_%03d" % _value,
        _make_classification_test(_value),
    )


class CheckAngleTest(unittest.TestCase):
    def test_accepts_bounds(self):
        self.assertEqual(check_angle(0), 0)
        self.assertEqual(check_angle(180), 180)

    def test_negative_rejected(self):
        with self.assertRaises(ProtractorError):
            check_angle(-1)

    def test_too_large_rejected(self):
        with self.assertRaises(ProtractorError):
            check_angle(181)

    def test_bool_rejected(self):
        with self.assertRaises(ProtractorError):
            check_angle(True)

    def test_float_rejected(self):
        with self.assertRaises(ProtractorError):
            check_angle(45.0)

    def test_string_rejected(self):
        with self.assertRaises(ProtractorError):
            check_angle("45")

    def test_custom_name(self):
        with self.assertRaisesRegex(ProtractorError, "起角"):
            check_angle(-5, "起角")


class DisplayTest(unittest.TestCase):
    def test_display(self):
        self.assertEqual(display_angle(45), "45°")
        self.assertEqual(display_angle(180), "180°")

    def test_display_invalid(self):
        with self.assertRaises(ProtractorError):
            display_angle(200)


class AngleProblemTest(unittest.TestCase):
    def test_read_prompt(self):
        problem = AngleProblem(45, "read")
        self.assertEqual(problem.prompt, "读出量角器上角的度数")

    def test_draw_prompt(self):
        problem = AngleProblem(120, "draw")
        self.assertEqual(problem.prompt, "用量角器画出 120° 的角")

    def test_answer(self):
        self.assertEqual(AngleProblem(45, "read").answer, "45°（锐角）")
        self.assertEqual(AngleProblem(90, "draw").answer, "90°（直角）")

    def test_zero_rejected(self):
        with self.assertRaises(ProtractorError):
            AngleProblem(0, "read")

    def test_full_rejected(self):
        with self.assertRaises(ProtractorError):
            AngleProblem(180, "read")

    def test_bad_kind(self):
        with self.assertRaises(ProtractorError):
            AngleProblem(45, "measure")

    def test_bad_direction(self):
        with self.assertRaises(ProtractorError):
            AngleProblem(45, "read", "up")

    def test_frozen(self):
        with self.assertRaises(FrozenInstanceError):
            AngleProblem(45, "read").value = 30


class GenerateTest(unittest.TestCase):
    def test_count(self):
        problems = generate_problems(8, seed=1)
        self.assertEqual(len(problems), 8)

    def test_deterministic(self):
        first = generate_problems(6, seed=42)
        second = generate_problems(6, seed=42)
        self.assertEqual(first, second)

    def test_unique(self):
        problems = generate_problems(12, seed=7)
        keys = {(item.value, item.kind, item.direction) for item in problems}
        self.assertEqual(len(keys), len(problems))

    def test_range(self):
        for item in generate_problems(20, 30, 60, seed=3):
            self.assertGreaterEqual(item.value, 30)
            self.assertLessEqual(item.value, 60)

    def test_single_kind(self):
        for item in generate_problems(10, kinds=("draw",), seed=5):
            self.assertEqual(item.kind, "draw")

    def test_invalid_count(self):
        for bad in (0, -1, 1.5, True, "8"):
            with self.assertRaises(ProtractorError):
                generate_problems(bad)

    def test_too_many(self):
        with self.assertRaises(ProtractorError):
            generate_problems(61)

    def test_invalid_bounds(self):
        with self.assertRaises(ProtractorError):
            generate_problems(5, 0, 30)
        with self.assertRaises(ProtractorError):
            generate_problems(5, 20, 180)
        with self.assertRaises(ProtractorError):
            generate_problems(5, 40, 40)

    def test_empty_kinds(self):
        with self.assertRaises(ProtractorError):
            generate_problems(5, kinds=())

    def test_unknown_kind(self):
        with self.assertRaises(ProtractorError):
            generate_problems(5, kinds=("read", "guess"))

    def test_impossible_count(self):
        with self.assertRaises(ProtractorError):
            generate_problems(10, 30, 30 + 1, kinds=("draw",), seed=1)

    def test_all_directions_known(self):
        for item in generate_problems(20, seed=11):
            self.assertIn(item.direction, DIRECTIONS)


if __name__ == "__main__":
    unittest.main()
