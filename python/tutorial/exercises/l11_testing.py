"""第 11 课：测试——随机对拍。

怎么相信一个求解器算得对？minicplex 的测试（python/tests/test_solver.py）造了 500 道随机的小整数规划，
每道都用“暴力枚举”再算一遍，两边答案必须一样。这一课自己写这套对拍：随机出题、暴力求解、比较。
运行：python3 python/tutorial/run.py 11
"""
import itertools
import math
import random

from check import lesson, eq, that, done
from minicplex import LinExpr, Model, ObjSense, Status, VarType, check_feasible, eval_objective, solve


def random_model(seed):
    """用 random.Random(seed) 造一道小题（同一个 seed 永远造出同一道题，出错时才能复现）：
    3 个整数变量，范围 0～4；2 条 <= 约束，系数在 -3～5 之间，右边在 2～12 之间；
    目标：最大化，系数在 1～9 之间。rng.randint(a, b) 包含 a 和 b。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def brute_force(m):
    """试遍所有整数点（每个变量从下界到上界），返回可行点里最大的目标值；一个可行点都没有时返回 None。
    提示：itertools.product(*(range(int(v.lb), int(v.ub) + 1) for v in m.vars))；
         check_feasible(m, 点) 判断可不可行；eval_objective(m, 点) 算目标值。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def agree(seed):
    """求解器和暴力枚举的答案一样吗？都无解也算一样。小数比较用 math.isclose。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def _one_var_model():
    m = Model()
    x = m.add_var(0, 4, VarType.INTEGER, "x")
    m.set_objective(x, ObjSense.MAXIMIZE)
    return m


lesson("第 11 课：测试——随机对拍")
that("同一个 seed 造出同一道题", lambda: random_model(7).to_lp() == random_model(7).to_lp())
that("不同的 seed 造出不同的题", lambda: random_model(7).to_lp() != random_model(8).to_lp())
eq("每道题 3 个变量、2 条约束", (3, 2), lambda: (random_model(1).num_vars, random_model(1).num_constrs))
that("暴力枚举：x ≤ 4 时最大化 x 得 4", lambda: brute_force(_one_var_model()) == 4)
that("100 道随机题，求解器和暴力枚举全部一致", lambda: all(agree(seed) for seed in range(100)))
done()
