"""量角器 SVG 与 A4 练习纸渲染。"""

from __future__ import annotations

import html
import math
from typing import List, Optional, Sequence

from .model import AngleProblem, ProtractorError, SCALES

_CSS = """
@page { size: A4; margin: 12mm; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
       color: #1f2933; background: #fff; }
.sheet { padding: 4mm; }
h1 { margin: 0 0 2mm; font-size: 22px; text-align: center; letter-spacing: 2px; }
.meta { margin: 0 0 5mm; text-align: center; color: #616e7c; font-size: 12px; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; }
.card { border: 1px solid #cbd2d9; border-radius: 3mm; padding: 3mm; page-break-inside: avoid; }
.prompt { font-size: 13px; margin: 0 0 2mm; color: #323f4b; }
.prompt b { color: #b02a37; }
.answer-line { margin-top: 2mm; border-bottom: 1px dashed #9aa5b1; height: 22px; }
.answers { page-break-before: always; margin-top: 6mm; }
.answers h2 { font-size: 18px; border-left: 4px solid #b02a37; padding-left: 3mm; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th, td { border: 1px solid #cbd2d9; padding: 2mm 3mm; text-align: left; }
th { background: #f5f7fa; }
@media print { .sheet { padding: 0; } }
""".strip()


def _polar(cx: float, cy: float, radius: float, degrees: float) -> tuple:
    """把数学角度（逆时针、0° 指向右）换成 SVG 坐标。"""
    radians = math.radians(degrees)
    return cx + radius * math.cos(radians), cy - radius * math.sin(radians)


def _fmt(value: float) -> str:
    return ("%.2f" % value).rstrip("0").rstrip(".")


def render_protractor(
    value: Optional[int] = None,
    direction: str = "right",
    scale: str = "both",
    size: int = 340,
    with_ray: bool = True,
    show_value: bool = False,
) -> str:
    """绘制半圆量角器；给定角度时画出角的终边。"""
    if isinstance(size, bool) or not isinstance(size, int) or size < 180:
        raise ProtractorError("量角器尺寸必须是至少 180 的整数")
    if scale not in SCALES:
        raise ProtractorError("未知刻度模式：%s" % scale)
    if direction not in ("right", "left"):
        raise ProtractorError("未知方向：%s" % direction)
    if value is not None and (value < 0 or value > 180):
        raise ProtractorError("角度必须在 0–180 之间：%d" % value)

    width = float(size)
    height = round(size * 0.62, 2)
    cx = width / 2.0
    cy = height - size * 0.06
    radius = size * 0.43

    parts: List[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s" width="%s" '
        'height="%s" role="img" aria-label="量角器">' % (_fmt(width), _fmt(height), _fmt(width), _fmt(height)),
        "<title>半圆量角器</title>",
        '<path d="M %s %s A %s %s 0 0 1 %s %s Z" fill="#fffdf5" stroke="#323f4b" '
        'stroke-width="1.6"/>'
        % (
            _fmt(cx - radius),
            _fmt(cy),
            _fmt(radius),
            _fmt(radius),
            _fmt(cx + radius),
            _fmt(cy),
        ),
    ]

    # 刻度线：每 1° 短线，5° 中线，10° 长线。
    ticks: List[str] = ['<g stroke="#52606d" stroke-linecap="round">']
    for degree in range(0, 181):
        if degree % 10 == 0:
            length, stroke_width = radius * 0.13, 1.1
        elif degree % 5 == 0:
            length, stroke_width = radius * 0.08, 0.8
        else:
            length, stroke_width = radius * 0.05, 0.5
        x1, y1 = _polar(cx, cy, radius, degree)
        x2, y2 = _polar(cx, cy, radius - length, degree)
        ticks.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke-width="%s"/>'
            % (_fmt(x1), _fmt(y1), _fmt(x2), _fmt(y2), stroke_width)
        )
    ticks.append("</g>")
    parts.extend(ticks)

    # 刻度数字：外圈从右向左 0→180，内圈从左向右 0→180。
    labels: List[str] = ['<g font-size="%s" fill="#3e4c59" text-anchor="middle">' % _fmt(max(7.0, size * 0.030))]
    for degree in range(0, 181, 10):
        if scale in ("outer", "both"):
            lx, ly = _polar(cx, cy, radius - radius * 0.24, degree)
            labels.append('<text x="%s" y="%s">%d</text>' % (_fmt(lx), _fmt(ly + size * 0.011), degree))
        if scale in ("inner", "both"):
            lx, ly = _polar(cx, cy, radius - radius * 0.41, degree)
            labels.append('<text x="%s" y="%s">%d</text>' % (_fmt(lx), _fmt(ly + size * 0.011), 180 - degree))
    labels.append("</g>")
    parts.extend(labels)

    # 中心十字与底边。
    parts.append(
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#323f4b" stroke-width="1.4"/>'
        % (_fmt(cx - radius), _fmt(cy), _fmt(cx + radius), _fmt(cy))
    )
    parts.append(
        '<circle cx="%s" cy="%s" r="2.2" fill="#323f4b"/>' % (_fmt(cx), _fmt(cy))
    )

    if value is not None and with_ray:
        degrees = value if direction == "right" else 180 - value
        ex, ey = _polar(cx, cy, radius - 4, degrees)
        parts.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#b02a37" stroke-width="2.4" '
            'stroke-linecap="round"/>' % (_fmt(cx), _fmt(cy), _fmt(ex), _fmt(ey))
        )
        parts.append('<circle cx="%s" cy="%s" r="3" fill="#b02a37"/>' % (_fmt(ex), _fmt(ey)))
        if show_value:
            tx, ty = _polar(cx, cy, radius * 0.55, degrees)
            parts.append(
                '<text x="%s" y="%s" font-size="%s" fill="#b02a37" text-anchor="middle">%d°</text>'
                % (_fmt(tx), _fmt(ty), _fmt(max(11.0, size * 0.042)), value)
            )

    parts.append("</svg>")
    return "\n".join(parts)


def render_worksheet(
    problems: Sequence[AngleProblem],
    title: str = "量角器练习",
    answers: bool = False,
    scale: str = "both",
) -> str:
    """生成可打印的 A4 练习纸。"""
    items = list(problems)
    if not items:
        raise ProtractorError("至少需要一道题")
    for item in items:
        if not isinstance(item, AngleProblem):
            raise ProtractorError("题目必须是 AngleProblem")
    if scale not in SCALES:
        raise ProtractorError("未知刻度模式：%s" % scale)

    cards: List[str] = []
    for index, item in enumerate(items, 1):
        if item.kind == "read":
            figure = render_protractor(item.value, item.direction, scale, with_ray=True)
        else:
            figure = render_protractor(None, item.direction, scale, with_ray=False)
        cards.append(
            '<div class="card">\n<p class="prompt">%d. %s</p>\n%s\n'
            '<div class="answer-line"></div>\n</div>'
            % (index, html.escape(item.prompt), figure)
        )

    sections = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % html.escape(title),
        "<style>%s</style></head><body>" % _CSS,
        '<main class="sheet">',
        "<h1>%s</h1>" % html.escape(title),
        '<p class="meta">姓名：__________　班级：__________　日期：__________</p>',
        '<section class="grid">',
        "\n".join(cards),
        "</section>",
    ]

    if answers:
        rows = []
        for index, item in enumerate(items, 1):
            rows.append(
                "<tr><td>%d</td><td>%s</td><td>%s</td></tr>"
                % (index, html.escape(item.prompt), html.escape(item.answer))
            )
        sections.append(
            '<section class="answers"><h2>参考答案</h2>'
            "<table><thead><tr><th>题号</th><th>题目</th><th>答案</th></tr></thead>"
            "<tbody>%s</tbody></table></section>" % "\n".join(rows)
        )

    sections.append("</main></body></html>")
    return "\n".join(sections)
