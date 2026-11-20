"""入门 A6：列表——一次存一排数。

运行：python3 python/tutorial/run.py A06
"""
from check import lesson, eq, near, done

WEEK = [8200, 6500, 12000, 4300, 9100, 15000, 7600]  # 一周七天的步数


def total(steps):
    """一周一共走了多少步？用 for 把每个数加起来（先别用内置的 sum）。"""
    # >>>
    s = 0
    for x in steps:
        s += x
    return s
    # <<<


def most(steps):
    """走得最多的一天是多少步？先假设第一个最大，再一个个比。"""
    # >>>
    best = steps[0]
    for x in steps:
        if x > best:
            best = x
    return best
    # <<<


def average(steps):
    """平均每天多少步？len(steps) 是列表的长度。"""
    # >>>
    return total(steps) / len(steps)
    # <<<


def days_over(steps, goal):
    """有几天达到了 goal 步（大于等于）？"""
    # >>>
    count = 0
    for x in steps:
        if x >= goal:
            count += 1
    return count
    # <<<


def doubled(nums):
    """返回一个新列表，每个数都乘 2。先建空列表 []，再用 .append() 一个个放进去。"""
    # >>>
    out = []
    for x in nums:
        out.append(x * 2)
    return out
    # <<<


lesson("入门 A6：列表")
eq("一周一共 62700 步", 62700, lambda: total(WEEK))
eq("最多的一天 15000 步", 15000, lambda: most(WEEK))
eq("全是负数也能找对最大值", -2, lambda: most([-5, -2, -9]))
near("平均每天约 8957 步", 62700 / 7, lambda: average(WEEK))
eq("达到 8000 步的有 4 天", 4, lambda: days_over(WEEK, 8000))
eq("doubled([1, 2, 3]) 是 [2, 4, 6]", [2, 4, 6], lambda: doubled([1, 2, 3]))
eq("doubled([]) 是 []", [], lambda: doubled([]))
done()
