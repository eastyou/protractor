# protractor

[![CI](https://github.com/eastyou/protractor/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/protractor/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

把半圆量角器画成 SVG，内外圈刻度一应俱全：可以出“读角度”和“画角度”两类题，直接生成可打印的 A4 练习纸，答案另起一页。

## 安装

```bash
pip install -e .
```

只需要 Python 3.9+，零第三方依赖。

## 用法

```bash
# 生成 8 道读角 / 画角混合练习，附答案
protractor sheet --count 8 --answers -o sheet.html

# 只出读角题，角度限定在 30–150 度
protractor sheet --kinds read --min 30 --max 150 -o read.html

# 输出单个 60° 的量角器 SVG
protractor draw 60 -o angle.svg

# 判断角的类型
protractor classify 120
# 120° 是钝角
```

## 功能

- 0–180° 半圆量角器，1°/5°/10° 三级刻度线
- 内外双圈读数，可单独输出内圈或外圈
- 读角题自动画出角的终边，画角题只给空白量角器
- 角度分类：零角、锐角、直角、钝角、平角
- 题目去重、支持随机种子复现
- 输出 A4 打印样式，题目卡片自动分栏，答案单独一页

## 测试

```bash
python -m unittest discover -s tests -v
```

## 许可

[MIT](LICENSE) © 2026 eastyou
