"""命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .model import (
    KINDS,
    SCALES,
    ProtractorError,
    classify,
    display_angle,
    generate_problems,
)
from .render import render_protractor, render_worksheet


def build_parser() -> argparse.ArgumentParser:
    """构造命令行解析器。"""
    parser = argparse.ArgumentParser(
        prog="protractor",
        description="量角器：0–180° 半圆量角器、内外圈读数与读角画角练习纸",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    sheet = subparsers.add_parser("sheet", help="生成 A4 练习纸 HTML")
    sheet.add_argument("--count", type=int, default=8, help="题目数量，默认 8")
    sheet.add_argument("--min", dest="min_angle", type=int, default=10, help="最小角度，默认 10")
    sheet.add_argument("--max", dest="max_angle", type=int, default=170, help="最大角度，默认 170")
    sheet.add_argument("--seed", type=int, default=None, help="随机种子")
    sheet.add_argument(
        "--kinds",
        default=",".join(KINDS),
        help="题型，用逗号分隔：read（读角）、draw（画角）",
    )
    sheet.add_argument(
        "--scale", default="both", choices=SCALES, help="刻度模式，默认 both"
    )
    sheet.add_argument("--title", default="量角器练习", help="练习纸标题")
    sheet.add_argument("--answers", action="store_true", help="追加参考答案")
    sheet.add_argument("-o", "--output", default=None, help="输出文件")

    single = subparsers.add_parser("draw", help="输出单个量角器 SVG")
    single.add_argument("angle", type=int, help="角度（0–180）")
    single.add_argument("--direction", default="right", choices=("right", "left"))
    single.add_argument("--scale", default="both", choices=SCALES)
    single.add_argument("--size", type=int, default=340)
    single.add_argument("--hide-ray", action="store_true", help="不画角的终边")
    single.add_argument("-o", "--output", default=None, help="输出文件")

    classify_parser = subparsers.add_parser("classify", help="判断角的类型")
    classify_parser.add_argument("angle", type=int, help="角度（0–180）")
    return parser


def _write_output(text: str, output: Optional[str]) -> None:
    if not output:
        print(text)
        return
    path = Path(output)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("已写入 %s" % path)


def _parse_kinds(text: str) -> List[str]:
    parts = [part.strip() for part in text.split(",") if part.strip()]
    if not parts:
        raise ProtractorError("至少需要一种题型")
    return parts


def main(argv: Optional[List[str]] = None) -> int:
    """命令行主函数，返回进程退出码。"""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "classify":
            print("%s 是%s" % (display_angle(args.angle), classify(args.angle)))
            return 0
        if args.command == "draw":
            svg = render_protractor(
                args.angle,
                args.direction,
                args.scale,
                args.size,
                with_ray=not args.hide_ray,
                show_value=True,
            )
            _write_output(svg, args.output)
            return 0
        kinds = _parse_kinds(args.kinds)
        problems = generate_problems(
            args.count, args.min_angle, args.max_angle, kinds, args.seed
        )
        _write_output(
            render_worksheet(problems, args.title, args.answers, args.scale),
            args.output,
        )
        return 0
    except ProtractorError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("写入失败：%s" % exc, file=sys.stderr)
        return 1
