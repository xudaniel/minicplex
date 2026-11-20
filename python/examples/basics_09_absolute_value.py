# 进阶例子 09：绝对值——选址让总距离最短
#
# 一条路上有 5 户人家，位置分别是 1、3、8、10、20（公里）。
# 要在路上建一个快递点，让它到所有人家的距离之和最小。建在哪里？
#
# 技巧：距离是绝对值 |x − 位置|，不能直接写成线性限制。为每户人家新建一个变量 d，
# 要求  d ≥ x − 位置  并且  d ≥ 位置 − x，然后最小化所有 d 的和。
# 求最小时，d 会自动被压到两者中较大的那个，也就是绝对值。
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # 不用安装也能运行
from minicplex import *

use_utf8_output()
home = [1, 3, 8, 10, 20]

m = Model()
x = m.add_var(-INF, INF, VarType.CONTINUOUS, "x")  # 快递点位置
d = []
for i, h in enumerate(home):
    d.append(m.add_var(0, INF, VarType.CONTINUOUS, f"d{i}"))  # 到第 i 户的距离
    m.add_constr(d[i] >= x - h, f"right{i}")
    m.add_constr(d[i] >= h - x, f"left{i}")
m.set_objective(sum(d, LinExpr()), ObjSense.MINIMIZE)

r = solve(m)
print(f"快递点建在 {r.value(x):.0f} 公里处，总距离 {r.objective:.0f} 公里")
for i, h in enumerate(home):
    print(f"  到位置 {h:2.0f} 的人家：{r.value(d[i]):.0f} 公里")

# 对比：如果建在平均位置（很多人的第一反应），总距离是多少？
mean = 0.0
for h in home:
    mean += h / len(home)
dist_mean = 0.0
for h in home:
    dist_mean += abs(h - mean)
print(f"对比：建在平均位置 {mean:.1f}，总距离 {dist_mean:.1f} 公里，反而更远。最优位置是中位数，不是平均数。")
