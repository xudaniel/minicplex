"""入门 A8：小项目——挑水果。

苹果 2 元一个、3 分；香蕉 1 元一根、2 分。你有 10 元，袋子最多装 7 个。怎么买，分数最高？
先用前面学的循环把所有买法都试一遍；最后看看 minicplex 求解器是不是也得到同一个答案。

运行：python3 python/tutorial/run.py A08
"""
from check import lesson, eq, near, that, done
from minicplex import INF, Model, ObjSense, VarType, solve


def fits(apples, bananas):
    """这样买钱够不够、袋子装不装得下？钱：2 × 苹果 + 1 × 香蕉 ≤ 10；袋子：苹果 + 香蕉 ≤ 7。"""
    # TODO 两个条件都要满足，用 and
    # >>>
    return 2 * apples + bananas <= 10 and apples + bananas <= 7
    # <<<


def score(apples, bananas):
    """这样买得几分？3 × 苹果 + 2 × 香蕉。"""
    # >>>
    return 3 * apples + 2 * bananas
    # <<<


def best():
    """试遍所有买法，返回最好的一种：(苹果数, 香蕉数, 分数)。
    苹果最多 5 个（10 元 ÷ 2 元），香蕉最多 10 根，用两层 for 循环。"""
    # TODO best = (0, 0, 0)
    #      for a in range(6):
    #          for b in range(11):
    #              如果 fits(a, b) 并且 score(a, b) > best[2]，就记下 (a, b, score(a, b))
    # >>>
    best = (0, 0, 0)
    for a in range(6):
        for b in range(11):
            if fits(a, b) and score(a, b) > best[2]:
                best = (a, b, score(a, b))
    return best
    # <<<


def solver_score():
    """同一道题交给 minicplex（这段不用你写，看看就好；第 1 课会详细讲）。"""
    m = Model()
    apple = m.add_var(0, INF, VarType.INTEGER, "apple")
    banana = m.add_var(0, INF, VarType.INTEGER, "banana")
    m.add_constr(2 * apple + 1 * banana <= 10, "money")
    m.add_constr(apple + banana <= 7, "bag")
    m.set_objective(3 * apple + 2 * banana, ObjSense.MAXIMIZE)
    return solve(m).objective


lesson("入门 A8：挑水果")
that("3 苹果 + 4 香蕉：钱和袋子都够", lambda: fits(3, 4))
that("5 苹果 + 1 香蕉：钱不够（11 元）", lambda: not fits(5, 1))
that("0 苹果 + 8 香蕉：袋子装不下", lambda: not fits(0, 8))
eq("3 苹果 + 4 香蕉得 17 分", 17, lambda: score(3, 4))
eq("最好的买法：3 个苹果、4 根香蕉、17 分", (3, 4, 17), lambda: best())
near("minicplex 求解器也得到 17 分", 17, lambda: solver_score())
print()
print("你用两层循环试了 6 × 11 = 66 种买法。变量一多，试遍所有组合就太慢了，")
print("这时就轮到求解器出场。下一步：第 1 课，自己用 minicplex 建模型。")
done()
