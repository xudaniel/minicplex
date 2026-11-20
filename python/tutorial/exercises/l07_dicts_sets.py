"""第 7 课：字典和集合。

Model 用字典 _index 从变量名查编号；LinExpr 用字典存 {变量编号: 系数}，同一个变量出现两次就把系数加起来。
这一课把这两件事自己做一遍，再用集合做去重和“有没有”的判断。
运行：python3 python/tutorial/run.py 07
"""
from check import lesson, eq, raises, done


def build_index(names):
    """名字 → 位置的字典：["x", "y"] → {"x": 0, "y": 1}。名字重复时 raise ValueError（Model.add_var 也这样）。
    提示：for i, name in enumerate(names)；name in index 判断有没有。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def merge_terms(pairs):
    """合并同类项：[("x", 2), ("y", 3), ("x", -2), ("z", 1)] → {"y": 3, "z": 1}。
    系数相加；加完是 0 的项去掉；结果按变量名排序（minicplex 也按编号排序，好让每次算的顺序都一样）。
    提示：d.get(k, 0) 拿不到时返回 0；dict(sorted(d.items())) 得到排好序的字典。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def first_unique(words):
    """去掉重复，但保留第一次出现的顺序：["b", "a", "b", "c", "a"] → ["b", "a", "c"]。
    用一个集合 seen 记住见过的（集合查“有没有”非常快）。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def common_free_days(a, b):
    """两个人都有空的日子，排好序返回列表。集合的 & 是“交集”。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


lesson("第 7 课：字典和集合")
eq('build_index(["x", "y", "z"])', {"x": 0, "y": 1, "z": 2}, lambda: build_index(["x", "y", "z"]))
raises("名字重复时报 ValueError", ValueError, lambda: build_index(["x", "y", "x"]))
eq("合并同类项，去掉 0", {"y": 3, "z": 1}, lambda: merge_terms([("x", 2), ("y", 3), ("x", -2), ("z", 1)]))
eq("结果按名字排序", ["a", "b", "c"], lambda: list(merge_terms([("c", 1), ("a", 1), ("b", 1)])))
eq("去重并保留顺序", ["b", "a", "c"], lambda: first_unique(["b", "a", "b", "c", "a"]))
eq("共同有空的日子", [2, 5], lambda: common_free_days([1, 2, 5, 6], [5, 2, 3]))
done()
