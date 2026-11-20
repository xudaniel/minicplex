# 进阶例子 10：题目无解怎么办？
#
# 复习计划：数学至少 6 小时，英语至少 5 小时，但这周总共只有 8 小时。
# 显然做不到，求解器会报 Infeasible（不可行）。可是到底差多少？先放弃哪一条？
#
# 技巧（弹性约束）：给每条“至少”加一个“缺口”变量（≥ 0），允许不满足，
# 但缺口要付代价，然后最小化总代价。代价越高，表示越不愿意放弃这一条。
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # 不用安装也能运行
from minicplex import *

use_utf8_output()
# 1. 原始问题：无解
m = Model()
math_ = m.add_var(0, INF, VarType.CONTINUOUS, "math")
eng = m.add_var(0, INF, VarType.CONTINUOUS, "english")
m.add_constr(math_ >= 6, "math_min")
m.add_constr(eng >= 5, "english_min")
m.add_constr(math_ + eng <= 8, "time")
m.set_objective(math_ + eng, ObjSense.MINIMIZE)
print(f"原始问题：{solve(m).status}\n")

# 2. 弹性版本：缺口可以存在，但要付代价
for math_weight in (1.0, 3.0):
    m = Model()
    math_ = m.add_var(0, INF, VarType.CONTINUOUS, "math")
    eng = m.add_var(0, INF, VarType.CONTINUOUS, "english")
    short_math = m.add_var(0, INF, VarType.CONTINUOUS, "short_math")  # 数学缺了几小时
    short_eng = m.add_var(0, INF, VarType.CONTINUOUS, "short_english")
    m.add_constr(math_ + short_math >= 6, "math_min")
    m.add_constr(eng + short_eng >= 5, "english_min")
    m.add_constr(math_ + eng <= 8, "time")  # 时间是硬限制，不能放宽
    m.set_objective(math_weight * short_math + 1.0 * short_eng, ObjSense.MINIMIZE)
    r = solve(m)
    sm, se = r.value(short_math), r.value(short_eng)
    print(f"数学缺口代价 {math_weight:.0f}、英语缺口代价 1：数学 {r.value(math_):.0f} 小时，英语 {r.value(eng):.0f} 小时；"
          f"数学缺 {sm:.0f}，英语缺 {se:.0f}，一共缺 {sm + se:.0f} 小时")

print("\n结论：不管怎么分，总共都要缺 3 小时；代价决定缺口落在哪一科。")
