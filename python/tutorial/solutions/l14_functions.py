"""第 14 课：函数进阶——*args、**kwargs、拆包和闭包。

minicplex 里到处是这些写法：Params(trace=True, cut_rounds=0) 是关键字参数；for k, a in c.coefs.items() 是拆包；
测试里的 itertools.product(*(range(...) for v in M.vars)) 用 * 把一串参数“摊开”。这一课一个个练。
运行：python3 python/tutorial/run.py 14
"""
from check import lesson, eq, near, raises, that, done
from minicplex import Params


def total(*nums):
    """接收任意多个数，返回它们的和：total(1, 2, 3) 是 6，total() 是 0。nums 在函数里是一个元组。"""
    # >>>
    return sum(nums)
    # <<<


def make_params(**changes):
    """在默认参数的基础上改几项：make_params(trace=True) 返回 Params(trace=True)。
    写错参数名（例如 trac=True）时应该报 TypeError——Params 自己会报，你只要把 changes 原样“摊开”传进去。"""
    # >>>
    return Params(**changes)
    # <<<


def first_and_rest(seq):
    """拆包：first_and_rest([1, 2, 3]) 返回 (1, [2, 3])。用一行 first, *rest = seq。"""
    # >>>
    first, *rest = seq
    return first, rest
    # <<<


def swap_pairs(pairs):
    """[(a, b), ...] → [(b, a), ...]。在 for 里直接拆包：for a, b in pairs。"""
    # >>>
    return [(b, a) for a, b in pairs]
    # <<<


def make_counter():
    """闭包：返回一个函数，每调用一次就返回 1、2、3……
    提示：外层函数里放一个变量 count = 0，内层函数用 nonlocal count 修改它。"""
    # >>>
    count = 0

    def counter():
        nonlocal count
        count += 1
        return count
    return counter
    # <<<


def make_adders(n):
    """返回 n 个函数，第 k 个函数把参数加上 k：make_adders(3)[2](10) 是 12。
    小心！[lambda x: x + k for k in range(n)] 是错的：所有函数共用同一个 k（循环结束时的值）。
    解决办法：用默认参数把当时的 k “存下来”：lambda x, k=k: x + k。"""
    # >>>
    return [lambda x, k=k: x + k for k in range(n)]
    # <<<


lesson("第 14 课：函数进阶")
eq("total(1, 2, 3) 是 6", 6, lambda: total(1, 2, 3))
eq("total() 是 0", 0, lambda: total())
eq("total(*[4, 5]) 也行：* 把列表摊开", 9, lambda: total(*[4, 5]))
that("make_params(trace=True, cut_rounds=0)", lambda: make_params(trace=True, cut_rounds=0) == Params(trace=True, cut_rounds=0))
that("make_params() 就是默认参数", lambda: make_params() == Params())
raises("参数名写错时报 TypeError", TypeError, lambda: make_params(trac=True))
near("用字典 ** 摊开：make_params(**{'mip_gap': 0.01}).mip_gap", 0.01, lambda: make_params(**{"mip_gap": 0.01}).mip_gap)
eq("first_and_rest([1, 2, 3])", (1, [2, 3]), lambda: first_and_rest([1, 2, 3]))
eq("first_and_rest('abc')", ("a", ["b", "c"]), lambda: first_and_rest("abc"))
eq("swap_pairs", [(2, 1), ("b", "a")], lambda: swap_pairs([(1, 2), ("a", "b")]))
eq("计数器：1, 2, 3", [1, 2, 3], lambda: (lambda c: [c(), c(), c()])(make_counter()))
eq("两个计数器各数各的", (2, 1), lambda: (lambda a, b: (a(), a(), b())[1:])(make_counter(), make_counter()))
eq("make_adders(3) 分别加 0、1、2", [10, 11, 12], lambda: [f(10) for f in make_adders(3)])
done()
