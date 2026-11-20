"""入门 A2：变量和计算。

运行：python3 python/tutorial/run.py A02
"""
from check import lesson, eq, near, done


def total(price, count):
    """买 count 个、每个 price 元，一共多少钱？"""
    # >>>
    return price * count
    # <<<


def change(paid, cost):
    """付了 paid 元，东西 cost 元，找回多少？"""
    # >>>
    return paid - cost
    # <<<


def how_many(money, price):
    """money 元最多买几个 price 元的东西？要整数：用 // （整除），不是 /。"""
    # >>>
    return money // price
    # <<<


def leftover(money, price):
    """买完最多的个数之后，还剩几元？用 % （取余数）。"""
    # >>>
    return money % price
    # <<<


def average(a, b, c):
    """三个数的平均数。"""
    # >>>
    return (a + b + c) / 3
    # <<<


def guess_floor_div():
    """🤔 先猜后跑：先别运行！读下面这几行，猜猜结果是什么，把你猜的写在 return 后面，再运行看看猜得对不对。

        -7 // 2
    """
    # >>>
    return -4
    # <<<


lesson("入门 A2：变量和计算")
eq("3 个 4 元的本子：12 元", 12, lambda: total(4, 3))
near("2 杯 6.5 元的奶茶：13 元", 13.0, lambda: total(6.5, 2))
near("付 20 元买 13.5 元的东西，找 6.5 元", 6.5, lambda: change(20, 13.5))
eq("10 元买 3 元的东西：最多 3 个", 3, lambda: how_many(10, 3))
eq("还剩 1 元", 1, lambda: leftover(10, 3))
eq("7 元买 2 元的：3 个，剩 1 元", (3, 1), lambda: (how_many(7, 2), leftover(7, 2)))
near("80、90、95 的平均分是 88.33…", 88.333333, lambda: average(80, 90, 95))
eq("🤔 猜一猜：-7 // 2", -7 // 2, guess_floor_div)
done()
