"""和 Java / C++ 完全一致的取整函数。

Python 的 math.ceil / math.floor 返回整数：遇到无穷大会报错，还会把 -0.0 变成 0。
求解器要和 C++、Java 版算出一模一样的数字（连 0 的正负号都一样），所以统一用这里的版本。
"""
import math


def ceil(v: float) -> float:
    if not math.isfinite(v):
        return v
    r = float(math.ceil(v))
    return math.copysign(0.0, v) if r == 0.0 else r


def floor(v: float) -> float:
    if not math.isfinite(v):
        return v
    r = float(math.floor(v))
    return math.copysign(0.0, v) if r == 0.0 else r


def rint(v: float) -> float:
    """Java 的 Math.rint：四舍六入五取偶。"""
    if not math.isfinite(v):
        return v
    r = float(round(v))
    return math.copysign(0.0, v) if r == 0.0 else r


def cround(v: float) -> float:
    """C++ 的 std::round：正好一半时远离 0。"""
    if not math.isfinite(v):
        return v
    s = 1.0 if v > 0 else -1.0 if v < 0 else v  # Math.signum
    return s * floor(abs(v) + 0.5)


def jmin(a: float, b: float) -> float:
    """Java 的 Math.min：-0.0 比 0.0 小（Python 的 min 遇到相等时返回第一个）。"""
    if a == b == 0.0:
        return a if math.copysign(1.0, a) < 0 else b
    return a if a <= b else b


def neg_zero_first(v: float) -> int:
    """排序用：让 -0.0 排在 0.0 前面（和 Java 的 Double.compare 一样）。"""
    return 0 if v == 0.0 and math.copysign(1.0, v) < 0 else 1
