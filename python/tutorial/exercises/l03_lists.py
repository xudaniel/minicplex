"""第 3 课：列表、循环和推导式。

单纯形表在 minicplex 里是一个“压扁”的一维列表：第 i 行第 j 列存在 T[i * N + j]。
这一课练习列表下标、推导式、zip / enumerate，最后写一个暴力背包和求解器对答案。
运行：python3 python/tutorial/run.py 03
"""
import itertools

from check import lesson, eq, near, that, done
from minicplex import LinExpr, Model, ObjSense, VarType, solve


def get(flat, n, i, j):
    """flat 是按行压扁的 m 行 n 列矩阵，返回第 i 行第 j 列（都从 0 开始）。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def row_sums(flat, m, n):
    """每一行的和，返回长度为 m 的列表。试试用推导式写成一行。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def make_grid(m, n):
    """m 行 n 列、全是 0 的二维列表。注意：[[0] * n] * m 是错的（每一行是同一个列表）！"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def knapsack_brute(values, weights, capacity):
    """暴力背包：试遍每件东西“拿 / 不拿”的所有组合，返回不超重时的最大总价值。
    提示：itertools.product([0, 1], repeat=len(values)) 给出所有 0/1 组合；zip 把两个列表配对。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def knapsack_solver(values, weights, capacity):
    """同一道题交给 minicplex：每件东西一个 0-1 变量。返回最优总价值。"""
    # TODO take = [m.add_var(0, 1, VarType.BINARY) for ...]；sum(生成器, LinExpr()) 可以把很多项加起来
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def guess_grid():
    """🤔 先猜后跑：先别运行！读下面这几行，猜猜结果是什么，把你猜的写在 return 后面，再运行看看猜得对不对。

        g = [[0] * 3] * 2
        g[0][0] = 99
        g 现在是什么？
    """
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


A = [1, 2, 3,
     4, 5, 6]  # 2 行 3 列
VALUES, WEIGHTS = [10, 13, 7, 8, 6, 9, 11, 4], [5, 6, 4, 3, 2, 5, 6, 1]

lesson("第 3 课：列表、循环和推导式")
eq("第 1 行第 2 列（从 0 数）是 6", 6, lambda: get(A, 3, 1, 2))
eq("第 0 行第 1 列是 2", 2, lambda: get(A, 3, 0, 1))
eq("每行的和是 [6, 15]", [6, 15], lambda: row_sums(A, 2, 3))
eq("make_grid(2, 3)", [[0, 0, 0], [0, 0, 0]], lambda: make_grid(2, 3))


def grid_rows_are_separate():
    g = make_grid(3, 2)
    g[0][0] = 99
    return g[1][0] == 0


that("改第 0 行不会影响第 1 行", grid_rows_are_separate)
eq("暴力背包（前 4 件，容量 10）：最大价值 21", 21, lambda: knapsack_brute(VALUES[:4], WEIGHTS[:4], 10))
near("求解器也得到 21", 21, lambda: knapsack_solver(VALUES[:4], WEIGHTS[:4], 10))
that("8 件东西、容量 15：两边答案一样", lambda: knapsack_brute(VALUES, WEIGHTS, 15) == knapsack_solver(VALUES, WEIGHTS, 15))
eq("🤔 猜一猜：[[0] * 3] * 2 改了一格之后", [[99, 0, 0], [99, 0, 0]], guess_grid)
done()
