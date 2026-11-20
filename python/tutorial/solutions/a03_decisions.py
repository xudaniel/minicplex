"""入门 A3：做判断。

运行：python3 python/tutorial/run.py A03
"""
from check import lesson, eq, done


def enough(money, cost):
    """钱够不够？够就返回 True，不够返回 False。"""
    # >>>
    return money >= cost
    # <<<


def shipping(order_total):
    """满 99 元包邮（运费 0），不满 99 元运费 10 元。"""
    # TODO 用 if / else
    # >>>
    if order_total >= 99:
        return 0
    else:
        return 10
    # <<<


def grade(score):
    """90 分及以上 "优秀"，75 及以上 "良好"，60 及以上 "及格"，其余 "不及格"。"""
    # TODO 用 if / elif / else，从高往低判断
    # >>>
    if score >= 90:
        return "优秀"
    elif score >= 75:
        return "良好"
    elif score >= 60:
        return "及格"
    else:
        return "不及格"
    # <<<


def can_ride(age, height):
    """过山车：身高至少 120 厘米，并且年龄在 8 到 60 岁之间（含 8 和 60）。"""
    # TODO and 表示“并且”；Python 可以直接写 8 <= age <= 60
    # >>>
    return height >= 120 and 8 <= age <= 60
    # <<<


lesson("入门 A3：做判断")
eq("10 元买 8 元的东西：够", True, lambda: enough(10, 8))
eq("10 元买 12 元的东西：不够", False, lambda: enough(10, 12))
eq("正好 10 元买 10 元的：够", True, lambda: enough(10, 10))
eq("买了 120 元：包邮", 0, lambda: shipping(120))
eq("正好 99 元：也包邮", 0, lambda: shipping(99))
eq("买了 98.5 元：运费 10 元", 10, lambda: shipping(98.5))
eq("95 分", "优秀", lambda: grade(95))
eq("75 分", "良好", lambda: grade(75))
eq("60 分", "及格", lambda: grade(60))
eq("59 分", "不及格", lambda: grade(59))
eq("10 岁、130 厘米：可以坐", True, lambda: can_ride(10, 130))
eq("6 岁、130 厘米：太小", False, lambda: can_ride(6, 130))
eq("30 岁、110 厘米：不够高", False, lambda: can_ride(30, 110))
done()
