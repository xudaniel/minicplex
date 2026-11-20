"""入门 A4：重复做事。

运行：python3 python/tutorial/run.py A04
"""
from check import lesson, eq, done


def sum_to(n):
    """1 + 2 + … + n。用 for i in range(1, n + 1)。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def days_to_save(target, per_day):
    """每天存 per_day 元，存够 target 元要几天？用 while：没存够就再存一天。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def count_multiples(n, k):
    """1 到 n 里有几个数是 k 的倍数？（i % k == 0 表示 i 能被 k 整除）"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def first_power_over(limit):
    """2 的几次方第一次超过 limit？例如 limit = 100：2⁷ = 128 > 100，返回 7。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


lesson("入门 A4：重复做事")
eq("1 加到 10 是 55", 55, lambda: sum_to(10))
eq("1 加到 100 是 5050", 5050, lambda: sum_to(100))
eq("1 加到 0 是 0（循环一次都不执行）", 0, lambda: sum_to(0))
eq("每天存 15 元，存 100 元要 7 天", 7, lambda: days_to_save(100, 15))
eq("每天存 20 元，存 100 元正好 5 天", 5, lambda: days_to_save(100, 20))
eq("1～20 里 3 的倍数有 6 个", 6, lambda: count_multiples(20, 3))
eq("2 的 7 次方第一次超过 100", 7, lambda: first_power_over(100))
eq("2 的 10 次方第一次超过 1000", 10, lambda: first_power_over(1000))
done()
