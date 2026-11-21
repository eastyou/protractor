"""命令行行为测试。"""

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from protractor.cli import main


def run(args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(args)
    return code, out.getvalue(), err.getvalue()


class CliTest(unittest.TestCase):
    def test_help(self):
        with self.assertRaises(SystemExit) as ctx:
            main(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_classify_acute(self):
        code, out, _ = run(["classify", "45"])
        self.assertEqual(code, 0)
        self.assertIn("锐角", out)

    def test_classify_right(self):
        code, out, _ = run(["classify", "90"])
        self.assertEqual(code, 0)
        self.assertIn("直角", out)

    def test_classify_invalid(self):
        code, _, err = run(["classify", "190"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_draw_stdout(self):
        code, out, _ = run(["draw", "60"])
        self.assertEqual(code, 0)
        self.assertIn("<svg", out)

    def test_draw_to_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "angle.html"
            code, out, _ = run(["draw", "75", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertTrue(target.exists())
            self.assertIn("已写入", out)

    def test_sheet_stdout(self):
        code, out, _ = run(["sheet", "--count", "2", "--seed", "1"])
        self.assertEqual(code, 0)
        self.assertIn("<!DOCTYPE html>", out)

    def test_sheet_answers(self):
        code, out, _ = run(["sheet", "--count", "2", "--seed", "1", "--answers"])
        self.assertEqual(code, 0)
        self.assertIn("参考答案", out)

    def test_sheet_to_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "sheet.html"
            code, _, _ = run(["sheet", "--count", "3", "--seed", "2", "-o", str(target)])
            self.assertEqual(code, 0)
            text = target.read_text(encoding="utf-8")
            self.assertEqual(text.count('class="card"'), 3)

    def test_sheet_bad_kind(self):
        code, _, err = run(["sheet", "--kinds", "read,guess"])
        self.assertEqual(code, 2)
        self.assertIn("题型", err)

    def test_sheet_empty_kind(self):
        code, _, err = run(["sheet", "--kinds", " , "])
        self.assertEqual(code, 2)
        self.assertIn("题型", err)

    def test_sheet_impossible(self):
        code, _, err = run(["sheet", "--count", "50", "--min", "10", "--max", "11"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_sheet_output_dir_created(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "nested" / "out.html"
            code, _, _ = run(["sheet", "--count", "1", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertTrue(target.exists())


if __name__ == "__main__":
    unittest.main()
