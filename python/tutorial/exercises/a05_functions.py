"""入门 A5：自己写函数。

运行：python3 python/tutorial/run.py A05
"""
from check import lesson, eq, near, done


def bigger(a, b):
    """返回 a 和 b 里大的那个（先别用内置的 max，自己用 if 写）。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def c_to_f(c):
    """摄氏度换算成华氏度：F = C × 9 / 5 + 32。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def clamp(x, lo, hi):
    """把 x 限制在 [lo, hi] 里：比 lo 小就返回 lo，比 hi 大就返回 hi，否则返回 x。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def discount(price, percent=10):
    """打折后的价格。percent 不写时默认打 9 折（减 10%）。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


lesson("入门 A5：自己写函数")
eq("bigger(3, 8) 是 8", 8, lambda: bigger(3, 8))
eq("bigger(-1, -5) 是 -1", -1, lambda: bigger(-1, -5))
near("0 ℃ = 32 ℉", 32, lambda: c_to_f(0))
near("37 ℃ = 98.6 ℉", 98.6, lambda: c_to_f(37))
eq("clamp(15, 0, 10) 是 10", 10, lambda: clamp(15, 0, 10))
eq("clamp(-3, 0, 10) 是 0", 0, lambda: clamp(-3, 0, 10))
eq("clamp(7, 0, 10) 是 7", 7, lambda: clamp(7, 0, 10))
near("200 元默认打 9 折：180 元", 180, lambda: discount(200))
near("200 元减 25%：150 元", 150, lambda: discount(200, 25))
near("也可以写参数名：discount(80, percent=50)", 40, lambda: discount(80, percent=50))
done()
