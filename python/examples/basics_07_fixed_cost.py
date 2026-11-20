# 进阶例子 07：固定费用（大 M）——要生产，先付开工费
#
# 面包店（必须整数）：蛋糕赚 5 元，面包赚 4 元；面粉 24 公斤，人工 6 小时。
# 新情况：做蛋糕要先买模具（12 元），做面包要先开烤箱（2 元）。只要做了，不管做多少，
# 这笔钱都要付；一个都不做就不用付。
#
# 技巧：给每种产品加一个 0-1 变量 open（做不做），再加一条“开关”限制：
#      数量 ≤ M × open
# open = 0 时数量只能是 0；open = 1 时数量最多是 M，相当于没有限制。
# M 要取“这种产品最多可能做多少”：太小会切掉合法方案，太大会让计算变慢。
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # 不用安装也能运行
from minicplex import *

use_utf8_output()

def solve_with_m(m_cake, m_bread, relax):
    """返回 (结果, 蛋糕数, 面包数)。"""
    m = Model()
    c = m.add_var(0, INF, VarType.INTEGER, "cake")
    b = m.add_var(0, INF, VarType.INTEGER, "bread")
    open_cake = m.add_var(0, 1, VarType.BINARY, "open_cake")
    open_bread = m.add_var(0, 1, VarType.BINARY, "open_bread")
    m.add_constr(6 * c + 4 * b <= 24, "flour")
    m.add_constr(1 * c + 2 * b <= 6, "labor")
    m.add_constr(c <= m_cake * open_cake, "cake_switch")     # 不开工就不能做蛋糕
    m.add_constr(b <= m_bread * open_bread, "bread_switch")  # 不开工就不能做面包
    m.set_objective(5 * c + 4 * b - 12 * open_cake - 2 * open_bread, ObjSense.MAXIMIZE)
    # 关掉预处理和割平面，才能看清 M 取值本身的影响
    r = solve(m, Params(relax_integrality=relax, presolve=False, cut_rounds=0))
    return r, r.value(c), r.value(b)


r, c, b = solve_with_m(4, 3, False)  # M：面粉最多够做 4 个蛋糕，人工最多够做 3 个面包
print(f"最优方案：蛋糕 {c:.0f} 个，面包 {b:.0f} 个，净赚 {r.objective:.0f} 元")
print("（没有开工费时最优是只做 4 个蛋糕赚 20 元；现在模具太贵，改成只做面包更划算）\n")

# 同样的模型，M 取得很大：答案不变，但“先允许小数”时的估算（界）宽松得多。
# 这道小题两种取法搜索的节点数一样；题目一大，宽松的界会让分支定界多搜很多节点。
tight = solve_with_m(4, 3, True)[0]
loose = solve_with_m(1000, 1000, True)[0]
loose_int = solve_with_m(1000, 1000, False)[0]
print(f"M 取 4 和 3：  允许小数时估算最多赚 {tight.objective:.2f} 元，整数最优 {r.objective:.0f} 元，搜索 {r.nodes} 个节点")
print(f"M 取 1000：    允许小数时估算最多赚 {loose.objective:.2f} 元，整数最优 {loose_int.objective:.0f} 元，"
      f"搜索 {loose_int.nodes} 个节点")
print("（估算越接近真实答案 10 元越好：M 取得准，估算是 11；M 取得大，估算是 20.96）")
