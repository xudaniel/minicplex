# 入门例子 04：选或不选（0-1 变量）
#
# 问题：周末有 8 小时空闲，有 4 件想做的事：
#   事情      用时    开心值
#   看电影    3 小时    6
#   爬山      5 小时    9
#   吃大餐    2 小时    4
#   读书      4 小时    5
# 规则：爬山和读书不能都选（太累）。选哪几件最开心？
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # 不用安装也能运行
from minicplex import *

use_utf8_output()
name = ["看电影", "爬山", "吃大餐", "读书"]
hours = [3, 5, 2, 4]
happy = [6, 9, 4, 5]

m = Model()
pick = []
time, fun = LinExpr(), LinExpr()
for i in range(len(name)):
    # VarType.BINARY：只能取 0（不选）或 1（选）
    pick.append(m.add_var(0, 1, VarType.BINARY, f"pick{i}"))
    time += hours[i] * pick[i]  # 总用时 = Σ 用时 × 选没选
    fun += happy[i] * pick[i]   # 总开心值
m.add_constr(time <= 8, "hours")                 # 时间不超过 8 小时
m.add_constr(pick[1] + pick[3] <= 1, "not_both")  # 爬山 + 读书 ≤ 1：最多选其中一个
m.set_objective(fun, ObjSense.MAXIMIZE)

r = solve(m)
print("选：" + "".join(name[i] + " " for i in range(len(name)) if r.value(pick[i]) > 0.5))
print(f"开心值 {g(r.objective)}")
