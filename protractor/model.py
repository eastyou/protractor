"""量角器：角度分类、读数与画角练习。"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, List, Optional, Sequence, Tuple

KINDS: Tuple[str, ...] = ("read", "draw")
SCALES: Tuple[str, ...] = ("inner", "outer", "both")
DIRECTIONS: Tuple[str, ...] = ("right", "left")


class ProtractorError(ValueError):
    """量角器相关的输入错误。"""


def check_angle(value: Any, name: str = "角度") -> int:
    """校验角度是 0–180 的整数，返回原值。"""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ProtractorError("%s必须是整数" % name)
    if value < 0 or value > 180:
        raise ProtractorError("%s必须在 0–180 之间：%d" % (name, value))
    return value


def classify(value: int) -> str:
    """按度数判断角的类型。"""
    check_angle(value)
    if value == 0:
        return "零角"
    if value < 90:
        return "锐角"
    if value == 90:
        return "直角"
    if value < 180:
        return "钝角"
    return "平角"


def display_angle(value: int) -> str:
    """格式化为“45°”。"""
    return "%d°" % check_angle(value)


@dataclass(frozen=True)
class AngleProblem:
    """一道读角或画角题。"""

    value: int
    kind: str
    direction: str = "right"

    def __post_init__(self) -> None:
        check_angle(self.value)
        if self.value < 1 or self.value > 179:
            raise ProtractorError("练习题角度应在 1–179 之间：%d" % self.value)
        if self.kind not in KINDS:
            raise ProtractorError("未知题型：%s" % self.kind)
        if self.direction not in DIRECTIONS:
            raise ProtractorError("未知方向：%s" % self.direction)

    @property
    def prompt(self) -> str:
        """题目说明文字。"""
        if self.kind == "read":
            return "读出量角器上角的度数"
        return "用量角器画出 %d° 的角" % self.value

    @property
    def answer(self) -> str:
        """参考答案文字。"""
        return "%d°（%s）" % (self.value, classify(self.value))


def generate_problems(
    count: int = 8,
    min_angle: int = 10,
    max_angle: int = 170,
    kinds: Sequence[str] = KINDS,
    seed: Optional[int] = None,
) -> List[AngleProblem]:
    """生成不重复的读角 / 画角题。"""
    if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
        raise ProtractorError("题目数量必须是正整数")
    if count > 60:
        raise ProtractorError("题目数量不能超过 60")
    check_angle(min_angle, "最小角度")
    check_angle(max_angle, "最大角度")
    if min_angle < 1 or max_angle > 179:
        raise ProtractorError("练习角度应在 1–179 之间")
    if min_angle >= max_angle:
        raise ProtractorError("最小角度必须小于最大角度")
    chosen = tuple(kinds)
    if not chosen:
        raise ProtractorError("至少需要一种题型")
    for kind in chosen:
        if kind not in KINDS:
            raise ProtractorError("未知题型：%s" % kind)

    rng = random.Random(seed)
    seen = set()
    result: List[AngleProblem] = []
    attempts = 0
    limit = count * (max_angle - min_angle + 1) * len(chosen) * len(DIRECTIONS)
    while len(result) < count and attempts < limit:
        attempts += 1
        value = rng.randint(min_angle, max_angle)
        kind = rng.choice(chosen)
        direction = rng.choice(DIRECTIONS)
        key = (value, kind, direction)
        if key in seen:
            continue
        seen.add(key)
        result.append(AngleProblem(value, kind, direction))
    if len(result) < count:
        raise ProtractorError("可用的角度组合不足 %d 道" % count)
    return result
