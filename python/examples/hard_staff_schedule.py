# 复杂例子 2：餐厅一周员工排班（0-1 整数规划）
#
# 8 名员工（4 名全职、4 名兼职），一周 7 天，每天早班、晚班各一个（每班 8 小时）。
# 决策：x[员工][天][班] = 1 表示该员工这天上这个班。
# 规则：
#   1. 每个班的人数 ≥ 需求（周末和周五晚上更忙）
#   2. 每个班至少 1 名老员工坐镇
#   3. 每人每天最多上 1 个班
#   4. 上完晚班，第二天不能接早班（保证休息）
#   5. 全职每周 4~5 天，兼职每周 2~4 天
#   6. 员工请假 / 不可用的日子不排班（例如兼职小刘只有周五到周日有空）
#   7. 全职员工周末两天最多上 1 天（轮流休周末）——店长除外；兼职可两天都上
#   8. 每人连续上班不超过 3 天（任意连续 4 天里至少休 1 天）
#   9. 新人小刘、小孙上班时，同一班必须有师傅（小李或小陈）带
#  10. 小王和小张合不来，不排在同一个班
# 目标：工资 + 员工偏好惩罚（不喜欢的班次）总和最小。
#
# 规模：112 个 0-1 变量（其中 21 个因不可用被固定为 0），183 条约束。
# 运行时会把模型写到 hard_staff_schedule.lp，可用 CPLEX / HiGHS 对照验证。
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # 不用安装也能运行
from minicplex import *

use_utf8_output()
from dataclasses import dataclass, field


@dataclass
class Staff:
    name: str
    id: str
    full_time: bool
    senior: bool
    manager: bool
    wage: float                 # 时薪（元）
    min_days: int
    max_days: int
    unavailable: list = field(default_factory=list)  # 不可用的日子（0 = 周一）
    no_morning: bool = False    # 不能上早班
    penalty_evening: float = 0  # 每上一个晚班的“不喜欢”惩罚
    penalty_weekend: float = 0  # 每上一个周末班的惩罚


D, S = 7, 2  # 7 天，早 / 晚两班
day_name = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
shift_name = ["早", "晚"]
hours_per_shift = 8
# 每班需求人数 need[天][班]
need = [[2, 2], [2, 2], [2, 2], [2, 2], [2, 3], [3, 3], [3, 3]]

staff = [
    #     姓名    id       全职   老员工 店长   时薪 天数   不可用        不上早 晚班罚 周末罚
    Staff("小王", "wang",  True,  True,  True,  32, 4, 5, [],           False, 0,  40),
    Staff("小李", "li",    True,  True,  False, 28, 4, 5, [],           False, 0,  0),
    Staff("小张", "zhang", True,  True,  False, 26, 4, 5, [2],          False, 30, 0),
    Staff("小陈", "chen",  True,  True,  False, 26, 4, 5, [],           False, 0,  20),
    Staff("小刘", "liu",   False, False, False, 20, 2, 4, [0, 1, 2, 3], False, 0,  0),
    Staff("小赵", "zhao",  False, False, False, 20, 2, 4, [],           True,  0,  0),
    Staff("小周", "zhou",  False, False, False, 21, 2, 4, [2, 3],       False, 15, 0),
    Staff("小孙", "sun",   False, False, False, 19, 2, 4, [0],          False, 0,  25),
]
E = len(staff)

m = Model()
x = [[[None] * S for _ in range(D)] for _ in range(E)]
cost = LinExpr()
for e, st in enumerate(staff):
    for d in range(D):
        for s in range(S):
            off = d in st.unavailable or (st.no_morning and s == 0)
            # 规则 6：不可用 → 上界设为 0（变量被固定，求解时自动去掉）
            x[e][d][s] = m.add_var(0, 0 if off else 1, VarType.BINARY, f"{st.id}_d{d + 1}{'_am' if s == 0 else '_pm'}")
            c = st.wage * hours_per_shift
            if s == 1:
                c += st.penalty_evening
            if d >= 5:
                c += st.penalty_weekend
            cost += c * x[e][d][s]

for d in range(D):
    for s in range(S):
        tag = f"_d{d + 1}{'_am' if s == 0 else '_pm'}"
        everyone, seniors = LinExpr(), LinExpr()
        for e in range(E):
            everyone += x[e][d][s]
            if staff[e].senior:
                seniors += x[e][d][s]
        m.add_constr(everyone >= need[d][s], "cover" + tag)  # 规则 1
        m.add_constr(seniors >= 1, "senior" + tag)           # 规则 2

for e, st in enumerate(staff):
    days, weekend = LinExpr(), LinExpr()
    for d in range(D):
        m.add_constr(x[e][d][0] + x[e][d][1] <= 1, f"{st.id}_one_d{d + 1}")  # 规则 3
        if d + 1 < D:  # 规则 4：晚班后不接早班
            m.add_constr(x[e][d][1] + x[e][d + 1][0] <= 1, f"{st.id}_rest_d{d + 1}")
        days += x[e][d][0] + x[e][d][1]
        if d >= 5:
            weekend += x[e][d][0] + x[e][d][1]
    for d in range(D - 3):  # 规则 8：连续 4 天最多上 3 天
        window = LinExpr()
        for k in range(d, d + 4):
            window += x[e][k][0] + x[e][k][1]
        m.add_constr(window <= 3, f"{st.id}_streak_d{d + 1}")
    m.add_constr(days >= st.min_days, f"{st.id}_mindays")  # 规则 5
    m.add_constr(days <= st.max_days, f"{st.id}_maxdays")
    if st.full_time and not st.manager:
        m.add_constr(weekend <= 1, f"{st.id}_weekend")  # 规则 7

# 规则 9：新人（小刘=4、小孙=7）上班时必须有师傅（小李=1 或小陈=3）在同一班
for rookie in (4, 7):
    for d in range(D):
        for s in range(S):
            m.add_constr(x[rookie][d][s] <= x[1][d][s] + x[3][d][s],
                         f"{staff[rookie].id}_mentor_d{d + 1}{'_pm' if s else '_am'}")
# 规则 10：小王（0）和小张（2）不排同一个班
for d in range(D):
    for s in range(S):
        m.add_constr(x[0][d][s] + x[2][d][s] <= 1, f"apart_d{d + 1}{'_pm' if s else '_am'}")

m.set_objective(cost, ObjSense.MINIMIZE)
m.write_lp("hard_staff_schedule.lp")
print(f"模型：{m.num_vars} 个变量（{m.num_integers} 个 0-1），{m.num_constrs} 条约束\n")

r = solve(m, Params(verbose=True, log_every=200))
if not r.has_solution:
    print(f"没有找到可行解：{r.status}")
    sys.exit(1)


def on(e, d, s):
    return r.x[x[e][d][s].id] > 0.5


print(f"\n状态：{r.status}   总成本：{r.objective:.0f} 元   节点：{r.nodes}   用时：{r.seconds:.2f} 秒\n")
print("排班表（早 / 晚 / 休）")
print("员工     " + "".join(f"{n}  " for n in day_name) + "天数   工资")
wages = 0.0
for e, st in enumerate(staff):
    line = f"{st.name}{'★' if st.senior else '  '}  "
    days = 0
    for d in range(D):
        c = "休"
        for s in range(S):
            if on(e, d, s):
                c = shift_name[s]
                days += 1
        line += f"  {c}  "
    w = days * hours_per_shift * st.wage
    wages += w
    print(line + f"{days:4d} {w:6.0f}")

print("\n每班人数（实际/需求）")
for s in range(S):
    line = f"{shift_name[s]}班      "
    for d in range(D):
        k = sum(on(e, d, s) for e in range(E))
        line += f" {k}/{need[d][s]}  "
    print(line)
print(f"\n工资 {wages:.0f} 元 + 偏好惩罚 {r.objective - wages:.0f} = 目标值 {r.objective:.0f}")
print(f"★ = 老员工    可行性自检：{'通过' if check_feasible(m, r.x) else '失败'}")
