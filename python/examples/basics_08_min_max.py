# 进阶例子 08：最小化最大值——公平分配
#
# 6 件任务分给 3 个人，用时分别是 5、4、3、3、2、1 小时。每件任务只给一个人。
# 目标：让最忙的那个人尽量不忙（所有人尽早一起下班）。
#
# 技巧：“最大值”不能直接写进目标。新建一个变量 T 表示“最忙的人的工作量”，
# 要求每个人的工作量都 ≤ T，然后最小化 T。最优时 T 就等于真正的最大值。
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # 不用安装也能运行
from minicplex import *

use_utf8_output()
hours = [5, 4, 3, 3, 2, 1]
tasks, people = len(hours), 3

m = Model()
# give[t][p] = 1 表示任务 t 交给第 p 个人
give = [[m.add_var(0, 1, VarType.BINARY, f"give_{t}_{p}") for p in range(people)] for t in range(tasks)]
T = m.add_var(0, INF, VarType.CONTINUOUS, "T")  # 最忙的人的工作量

for t in range(tasks):  # 每件任务正好给一个人
    m.add_constr(sum(give[t][p] for p in range(people)) == 1, f"task{t}")
for p in range(people):  # 每个人的工作量 ≤ T
    m.add_constr(sum(hours[t] * give[t][p] for t in range(tasks)) <= T, f"load{p}")
m.set_objective(T, ObjSense.MINIMIZE)

r = solve(m)
print(f"最忙的人工作 {r.objective:.0f} 小时")
for p in range(people):
    mine = [hours[t] for t in range(tasks) if r.value(give[t][p]) > 0.5]
    print(f"第 {p + 1} 个人：" + "".join(f"{h:.0f} 小时任务 " for h in mine) + f"→ 共 {sum(mine):.0f} 小时")
