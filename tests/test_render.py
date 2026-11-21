"""量角器与练习纸渲染测试。"""

import unittest

from protractor.model import AngleProblem, ProtractorError
from protractor.render import render_protractor, render_worksheet


class ProtractorSvgTest(unittest.TestCase):
    def test_root_svg(self):
        svg = render_protractor()
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.endswith("</svg>"))
        self.assertIn("量角器", svg)

    def test_ticks(self):
        svg = render_protractor()
        self.assertEqual(svg.count("<line"), 182)

    def test_ray_added(self):
        svg = render_protractor(45)
        self.assertEqual(svg.count("<line"), 183)
        self.assertIn("#b02a37", svg)

    def test_ray_hidden(self):
        svg = render_protractor(45, with_ray=False)
        self.assertEqual(svg.count("<line"), 182)

    def test_show_value(self):
        svg = render_protractor(60, show_value=True)
        self.assertIn("60°", svg)

    def test_hide_value(self):
        svg = render_protractor(60, show_value=False)
        self.assertNotIn("60°", svg)

    def test_both_scales(self):
        svg = render_protractor(scale="both")
        self.assertEqual(svg.count("<text"), 38)

    def test_outer_scale_only(self):
        svg = render_protractor(scale="outer")
        self.assertEqual(svg.count("<text"), 19)

    def test_inner_scale_only(self):
        svg = render_protractor(scale="inner")
        self.assertEqual(svg.count("<text"), 19)

    def test_left_direction(self):
        svg = render_protractor(30, direction="left", show_value=True)
        self.assertIn("30°", svg)

    def test_size(self):
        svg = render_protractor(size=400)
        self.assertIn('width="400"', svg)
        self.assertIn('viewBox="0 0 400', svg)

    def test_invalid_size(self):
        with self.assertRaises(ProtractorError):
            render_protractor(size=100)

    def test_invalid_scale(self):
        with self.assertRaises(ProtractorError):
            render_protractor(scale="middle")

    def test_invalid_direction(self):
        with self.assertRaises(ProtractorError):
            render_protractor(45, direction="up")

    def test_invalid_angle(self):
        with self.assertRaises(ProtractorError):
            render_protractor(181)


class WorksheetTest(unittest.TestCase):
    def setUp(self):
        self.problems = [
            AngleProblem(45, "read"),
            AngleProblem(120, "draw"),
            AngleProblem(90, "read", "left"),
        ]

    def test_document(self):
        page = render_worksheet(self.problems)
        self.assertIn("<!DOCTYPE html>", page)
        self.assertIn("量角器练习", page)
        self.assertIn("姓名", page)
        self.assertTrue(page.endswith("</html>"))

    def test_card_count(self):
        page = render_worksheet(self.problems)
        self.assertEqual(page.count('class="card"'), 3)

    def test_read_problem_has_ray(self):
        page = render_worksheet([AngleProblem(45, "read")])
        self.assertIn('stroke="#b02a37"', page)

    def test_draw_problem_has_no_ray(self):
        page = render_worksheet([AngleProblem(45, "draw")])
        self.assertNotIn('stroke="#b02a37"', page)

    def test_answers_included(self):
        page = render_worksheet(self.problems, answers=True)
        self.assertIn("参考答案", page)
        self.assertIn("45°（锐角）", page)

    def test_answers_omitted(self):
        page = render_worksheet(self.problems, answers=False)
        self.assertNotIn("参考答案", page)

    def test_custom_title(self):
        page = render_worksheet(self.problems, title="角的度量")
        self.assertIn("<title>角的度量</title>", page)

    def test_scale_passed(self):
        page = render_worksheet(self.problems, scale="inner")
        self.assertIn("量角器", page)

    def test_empty_rejected(self):
        with self.assertRaises(ProtractorError):
            render_worksheet([])

    def test_bad_item(self):
        with self.assertRaises(ProtractorError):
            render_worksheet([("45", "read")])

    def test_bad_scale(self):
        with self.assertRaises(ProtractorError):
            render_worksheet(self.problems, scale="none")

    def test_escaping(self):
        page = render_worksheet(self.problems, title="<script>")
        self.assertNotIn("<script>", page)
        self.assertIn("&lt;script&gt;", page)


if __name__ == "__main__":
    unittest.main()
