# 入门例子 02：两个变量、两条限制
#
# 问题：去水果店，苹果 2 元一个，香蕉 1 元一个。
#   - 你有 10 元
#   - 袋子最多装 7 个水果
#   - 你给每个苹果打 3 分（好吃），每根香蕉打 2 分
# 怎么买，总分最高？
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # 不用安装也能运行
from minicplex import *

use_utf8_output()
m = Model()
apple = m.add_var(0, INF, VarType.CONTINUOUS, "apple")
banana = m.add_var(0, INF, VarType.CONTINUOUS, "banana")

m.add_constr(2 * apple + 1 * banana <= 10, "money")  # 钱：2×苹果 + 1×香蕉 ≤ 10
m.add_constr(apple + banana <= 7, "bag")              # 袋子：苹果 + 香蕉 ≤ 7

m.set_objective(3 * apple + 2 * banana, ObjSense.MAXIMIZE)  # 总分 = 3×苹果 + 2×香蕉

r = solve(m)
a, b = r.value(apple), r.value(banana)
print(f"苹果 {g(a)} 个，香蕉 {g(b)} 根，总分 {g(r.objective)}")

# 两条限制都刚好用满吗？算一算：
print(f"花钱 {g(2 * a + b)} 元（上限 10），装了 {g(a + b)} 个（上限 7）")
