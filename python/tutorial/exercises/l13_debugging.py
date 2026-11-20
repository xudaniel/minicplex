"""第 13 课：读懂报错、调试和 assert。

这一课的练习换个玩法：下面几个函数都**已经写好了，但有 bug**。运行一下，看 ❌ 那几行，读报错、找原因、改好。
最后一题再用 assert 给函数加一道“自检”。
运行：python3 python/tutorial/run.py 13
"""
import math

from check import lesson, eq, near, raises, done


def average(nums):
    """平均数。average([2, 4, 6]) 应该是 4。"""
    # 🐞 下面这段有 bug：找出来，改好
    total = 0
    for i in range(1, len(nums)):
        total += nums[i]
    return total / len(nums)


def is_leap(year):
    """闰年：能被 4 整除但不能被 100 整除，或者能被 400 整除。2000 是闰年，1900 不是。"""
    # 🐞 下面这段有 bug：找出来，改好
    return year % 4 == 0 and year % 100 != 0


def count_words(text):
    """数单词个数，多个空格、换行都算一个分隔。"""
    # 🐞 下面这段有 bug：找出来，改好
    return len(text.split(" "))


# 🐞 下面这段有 bug：找出来，改好
def add_item(item, cart=[]):
    """把 item 放进购物车并返回购物车。不传 cart 时，每次都应该是一个新的空购物车。"""
    cart.append(item)
    return cart


def best_price(prices):
    """最低价。prices 是 {商品: 价格}，返回 (商品, 价格)。"""
    # 🐞 下面这段有 bug：找出来，改好
    name = min(prices)
    return name, prices[name]


def safe_sqrt(x):
    """平方根。x 是负数时不应该悄悄算出 nan，而是用 assert 立即报错，信息写 "x 不能是负数"。"""
    # TODO 第一行写 assert 条件, "信息"；然后 return math.sqrt(x)
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


lesson("第 13 课：读懂报错、调试和 assert")
near("average([2, 4, 6]) 是 4", 4, lambda: average([2, 4, 6]))
near("average([10]) 是 10", 10, lambda: average([10]))
eq("2024 是闰年", True, lambda: is_leap(2024))
eq("1900 不是闰年", False, lambda: is_leap(1900))
eq("2000 是闰年", True, lambda: is_leap(2000))
eq('"one  two  three\\nfour" 有 4 个单词', 4, lambda: count_words("one  two  three\nfour"))
eq("第一次 add_item：['书']", ["书"], lambda: add_item("书"))
eq("第二次 add_item 也应该是一个新购物车：['笔']", ["笔"], lambda: add_item("笔"))
eq("最便宜的是香蕉", ("香蕉", 3), lambda: best_price({"苹果": 5, "香蕉": 3, "梨": 4}))
near("safe_sqrt(9) 是 3", 3, lambda: safe_sqrt(9))
raises("safe_sqrt(-1) 触发 AssertionError", AssertionError, lambda: safe_sqrt(-1))
done()
