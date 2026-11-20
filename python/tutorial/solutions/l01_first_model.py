"""第 1 课：第一个模型。

冰淇淋 3 元一个，你有 25 元，最多买几个？（只能买整个）
运行：python3 python/tutorial/run.py 01
"""
from check import lesson, eq, near, done
from minicplex import INF, Model, ObjSense, Status, VarType, solve


def ice_cream_model():
    """返回冰淇淋问题的模型：一个整数变量 ice_cream，一条限制 money，目标是最大化个数。"""
    # TODO 1. m = Model()  2. add_var 一个整数变量 "ice_cream"（下限 0，上限 INF）
    #      3. 加限制 3 × ice_cream ≤ 25，名字叫 "money"  4. 目标：最大化 ice_cream  5. return m
    # >>>
    m = Model()
    ice = m.add_var(0, INF, VarType.INTEGER, "ice_cream")
    m.add_constr(3 * ice <= 25, "money")
    m.set_objective(ice, ObjSense.MAXIMIZE)
    return m
    # <<<


lesson("第 1 课：第一个模型")
eq("模型里有 1 个变量", 1, lambda: ice_cream_model().num_vars)
eq("模型里有 1 条限制", 1, lambda: ice_cream_model().num_constrs)
eq("变量名叫 ice_cream", 0, lambda: ice_cream_model().find_var("ice_cream"))
eq("求解状态是 Optimal", Status.OPTIMAL, lambda: solve(ice_cream_model()).status)
near("最多买 8 个", 8, lambda: solve(ice_cream_model()).objective)
done()
