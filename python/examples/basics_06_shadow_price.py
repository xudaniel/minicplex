# 进阶例子 06：影子价格——多一份资源值多少钱？
#
# 还是面包店（允许做半个）：蛋糕赚 5 元，面包赚 4 元；面粉 24 公斤，人工 6 小时。
# 老板想知道：如果能多买 1 公斤面粉，或者多请 1 小时人工，最多值得花多少钱？
#
# 答案就是每条限制的“影子价格”（对偶值）：右边多 1 个单位，最优利润能多多少。
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # 不用安装也能运行
from minicplex import *

use_utf8_output()

def bakery(flour, labor):
    m = Model()
    cake = m.add_var(0, INF, VarType.CONTINUOUS, "cake")
    bread = m.add_var(0, INF, VarType.CONTINUOUS, "bread")
    m.add_constr(6 * cake + 4 * bread <= flour, "flour")
    m.add_constr(1 * cake + 2 * bread <= labor, "labor")
    m.set_objective(5 * cake + 4 * bread, ObjSense.MAXIMIZE)
    return m


def best_profit(flour, labor):
    return solve(bakery(flour, labor)).objective


r = solve(bakery(24, 6))

# r.duals[i] 就是第 i 条限制的影子价格（只有线性规划才有）
print(f"最大利润 {r.objective:.2f} 元")
print(f"面粉的影子价格：{r.duals[0]:.2f} 元/公斤")
print(f"人工的影子价格：{r.duals[1]:.2f} 元/小时\n")

# 验证：真的多给 1 份资源，重新算一遍
print(f"面粉 25 公斤：利润 {best_profit(25, 6):.2f} 元（多了 {best_profit(25, 6) - r.objective:.2f}）")
print(f"人工 7 小时： 利润 {best_profit(24, 7):.2f} 元（多了 {best_profit(24, 7) - r.objective:.2f}）\n")

# 注意：影子价格只在一定范围内有效。多 20 公斤面粉，并不能多赚 20 × 0.75 = 15 元，
# 因为人工很快变成瓶颈了。
print(f"面粉 44 公斤：利润 {best_profit(44, 6):.2f} 元（按影子价格估算是 {r.objective + 20 * r.duals[0]:.2f}）")
