"""第 2 课：数字和小数误差。

求解器天天和小数打交道：0.1 + 0.2 不等于 0.3、无穷大、四舍五入的规则……
这一课把 minicplex 里处理这些问题的几个小函数自己写一遍（真正的代码在 minicplex/jmath.py 和 lp_engine.py）。
运行：python3 python/tutorial/run.py 02
"""
import math

from check import lesson, eq, that, done


def near(a, b, tol=1e-9):
    """a 和 b 是否“足够接近”：|a - b| ≤ tol × (1 + |b|)。（相对误差，大数小数都适用）"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def is_integral(v):
    """v 是不是整数（允许 1e-9 的误差）？无穷大和 NaN 都不算。
    提示：math.isfinite(v)；round(v) 是离 v 最近的整数。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def cround(v):
    """“正好一半时远离 0”的四舍五入（C++ 的 std::round）：2.5 → 3，-2.5 → -3。
    Python 自带的 round(2.5) 是 2（一半时取偶数），所以要自己写：符号 × floor(|v| + 0.5)。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def fractionality(v):
    """v 离最近的整数有多远？3.2 → 0.2，3.9 → 0.1（分支定界用它挑“最不像整数”的变量）。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


lesson("第 2 课：数字和小数误差")
that("0.1 + 0.2 和 0.3 用 == 比较居然不相等", lambda: 0.1 + 0.2 != 0.3)
that("但它们“足够接近”", lambda: near(0.1 + 0.2, 0.3))
that("1 和 1.001 不算接近", lambda: not near(1, 1.001))
that("1e9 和 1e9 + 0.5 却算接近（相对误差只有 5e-10）", lambda: near(1e9, 1e9 + 0.5))
that("3.0000000001 算整数", lambda: is_integral(3.0000000001))
that("2.5 不算整数", lambda: not is_integral(2.5))
that("无穷大不算整数", lambda: not is_integral(math.inf))
that("NaN 不算整数", lambda: not is_integral(math.nan))
eq("Python 的 round(2.5) 是 2（一半取偶数）", 2, lambda: round(2.5))
eq("cround(2.5) 是 3", 3, lambda: cround(2.5))
eq("cround(-2.5) 是 -3", -3, lambda: cround(-2.5))
eq("cround(2.4) 是 2", 2, lambda: cround(2.4))
that("fractionality(3.2) 约等于 0.2", lambda: near(fractionality(3.2), 0.2))
that("fractionality(3.9) 约等于 0.1", lambda: near(fractionality(3.9), 0.1))
that("fractionality(-0.75) 是 0.25", lambda: near(fractionality(-0.75), 0.25))
done()
