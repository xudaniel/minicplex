# 简单例子 2：0-1 整数规划（MIP）—— 投资项目选择
#
# 预算 10 万元，有 4 个项目，每个要么投、要么不投：
#   项目   投入(万)   收益(万)
#    A       5         8
#    B       4         7
#    C       3         4
#    D       2         4
# 额外规则：投 C 的前提是也投 D（C <= D）
# 问：投哪几个，总收益最大？
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # 不用安装也能运行
from minicplex import *

use_utf8_output()
name = ["A", "B", "C", "D"]
cost = [5, 4, 3, 2]
gain = [8, 7, 4, 4]

m = Model()
# 0-1 变量：1 = 投，0 = 不投
pick = [m.add_var(0, 1, VarType.BINARY, n) for n in name]
total_cost = sum((cost[i] * pick[i] for i in range(len(name))), LinExpr())
total_gain = sum((gain[i] * pick[i] for i in range(len(name))), LinExpr())

m.add_constr(total_cost <= 10, "budget")       # 预算
m.add_constr(pick[2] <= pick[3], "C_needs_D")  # 投 C 必须投 D
m.set_objective(total_gain, ObjSense.MAXIMIZE)

r = solve(m)
print(f"状态：{r.status}")
print(f"最大收益：{g(r.objective)} 万")
print("投资项目：" + "".join(name[i] + " " for i in range(len(name)) if r.value(pick[i]) > 0.5))
print(f"分支定界节点数：{r.nodes}")
