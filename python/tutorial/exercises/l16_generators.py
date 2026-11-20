"""第 16 课：生成器和迭代器。

sum(hours[t] * give[t][p] for t in range(tasks)) 里的那串东西就是生成器：要一个算一个，不先造出整个列表。
这一课用 yield 自己写生成器，最后写一个“枚举所有组合”的生成器，把第 3 课的暴力背包重写一遍。
运行：python3 python/tutorial/run.py 16
"""
import itertools

from check import lesson, eq, that, done
from minicplex import LinExpr, Model, ObjSense, VarType, solve


def countdown(n):
    """依次产出 n, n-1, ..., 1。函数里用 yield，它就变成了生成器。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def fibonacci():
    """无穷的斐波那契数列：0, 1, 1, 2, 3, 5, ……（永远不结束，用的人自己决定取几个）"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def chunks(seq, k):
    """把序列切成每段 k 个：chunks([1,2,3,4,5], 2) 产出 [1,2]、[3,4]、[5]。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def clean_numbers(lines):
    """从一行行文字里产出数字：跳过空行和 # 开头的注释，其余的转成 float。
    lines 可能非常大（比如一个大文件），所以要用生成器，一行一行地处理。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def assignments(n, values):
    """n 个位置、每个位置可以取 values 里的值，产出所有组合（元组），顺序和 itertools.product(values, repeat=n) 一样。
    提示：递归。n == 0 时产出一个空元组 ()；否则对第一个位置的每个值 v，
    用 for rest in assignments(n - 1, values): yield (v,) + rest。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def knapsack_brute(values, weights, capacity):
    """用你写的 assignments 做暴力背包（第 3 课用的是 itertools.product）。"""
    best = 0
    for pick in assignments(len(values), [0, 1]):
        if sum(w * p for w, p in zip(weights, pick)) <= capacity:
            best = max(best, sum(v * p for v, p in zip(values, pick)))
    return best


def knapsack_solver(values, weights, capacity):
    m = Model()
    take = [m.add_var(0, 1, VarType.BINARY, f"t{k}") for k in range(len(values))]
    m.add_constr(sum((w * t for w, t in zip(weights, take)), LinExpr()) <= capacity)
    m.set_objective(sum((v * t for v, t in zip(values, take)), LinExpr()), ObjSense.MAXIMIZE)
    return solve(m).objective


lesson("第 16 课：生成器和迭代器")
eq("countdown(3) 产出 3, 2, 1", [3, 2, 1], lambda: list(countdown(3)))
that("countdown 是生成器（不是列表）", lambda: hasattr(countdown(3), "__next__"))
eq("斐波那契前 10 个（用 itertools.islice 取前几个）", [0, 1, 1, 2, 3, 5, 8, 13, 21, 34],
   lambda: list(itertools.islice(fibonacci(), 10)))
eq("chunks", [[1, 2], [3, 4], [5]], lambda: list(chunks([1, 2, 3, 4, 5], 2)))
eq("clean_numbers", [1.5, 2.0], lambda: list(clean_numbers(["1.5", "", "# 注释", " 2 "])))
eq("clean_numbers 是一个一个处理的：只取第一个时，后面的坏数据不会被碰到", 1.0,
   lambda: next(clean_numbers(["1", "这一行不是数字"])))
eq("assignments(2, [0, 1])", [(0, 0), (0, 1), (1, 0), (1, 1)], lambda: list(assignments(2, [0, 1])))
that("和 itertools.product 的结果一样", lambda: list(assignments(3, "ab")) == list(itertools.product("ab", repeat=3)))
that("暴力背包和求解器答案一样", lambda: knapsack_brute([10, 13, 7, 8, 6], [5, 6, 4, 3, 2], 12)
     == knapsack_solver([10, 13, 7, 8, 6], [5, 6, 4, 3, 2], 12))
done()
