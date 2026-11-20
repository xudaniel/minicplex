# 复杂例子：多产品、多周期生产排程（带换线、批量、加班、仓储限制）
#
# 一家电动工具厂，未来 6 周生产 3 种产品：电钻、角磨机、电锯。
# 每周要决定：
#   * 每种产品生产多少（连续）
#   * 每种产品这周开不开线（0-1）：开线要付换线费，且每周最多开 2 条
#   * 加几个班（整数 0~2）：每个加班多 80 工时，每个班 1,200 元
# 规则：
#   1. 库存平衡：上周库存 + 本周生产 − 本周需求 = 本周库存（不允许缺货）
#   2. 工时：Σ 单位工时 × 产量 ≤ 400 + 80 × 加班数
#   3. 开线才能生产，开线就至少生产一个最小批量
#   4. 每周最多换线 2 次（三种产品不能每周都做 → 必须提前囤货）
#   5. 仓库最多放 250 件
#   6. 第 6 周末要留安全库存
# 目标：总成本（换线 + 库存 + 加班 + 生产）最小。
#
# 规模：60 个变量（18 个 0-1、6 个整数）、约 80 条约束。
# 运行时会把模型写到 hard_production_plan.lp，可用 CPLEX / HiGHS 对照验证。
import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # 不用安装也能运行
from minicplex import *

use_utf8_output()

P, T = 3, 6
pname = ["电钻", "角磨机", "电锯"]
pid = ["drill", "grinder", "saw"]
hours = [2, 3, 4]               # 单位工时
setup_cost = [800, 1000, 1500]  # 换线费
hold_cost = [2, 3, 5]           # 每件每周库存费
unit_cost = [20, 30, 45]        # 单位生产成本
min_lot = [30, 20, 15]          # 最小批量
init_inv = [80, 10, 0]          # 期初库存
end_inv = [20, 15, 10]          # 期末安全库存
demand = [
    [60, 70, 50, 80, 90, 60],  # 电钻
    [40, 30, 50, 40, 60, 50],  # 角磨机
    [20, 30, 25, 35, 20, 40],  # 电锯
]
base_hours, ot_hours, ot_cost = 400, 80, 1200
max_ot, max_setups = 2, 2
warehouse = 250

m = Model()
make = [[None] * T for _ in range(P)]
inv = [[None] * T for _ in range(P)]
setup = [[None] * T for _ in range(P)]
ot = [None] * T
for t in range(T):
    w = f"_w{t + 1}"
    for p in range(P):
        make[p][t] = m.add_var(0, INF, VarType.CONTINUOUS, f"make_{pid[p]}{w}")
        inv[p][t] = m.add_var(end_inv[p] if t == T - 1 else 0, INF, VarType.CONTINUOUS, f"inv_{pid[p]}{w}")
        setup[p][t] = m.add_var(0, 1, VarType.BINARY, f"setup_{pid[p]}{w}")
    ot[t] = m.add_var(0, max_ot, VarType.INTEGER, f"overtime{w}")

cost = LinExpr()
for t in range(T):
    w = f"_w{t + 1}"
    hours_used, setups_used, stock = LinExpr(), LinExpr(), LinExpr()
    for p in range(P):
        # 1. 库存平衡
        prev = LinExpr.const(init_inv[p]) if t == 0 else LinExpr.of(inv[p][t - 1])
        m.add_constr(prev + make[p][t] - inv[p][t] == demand[p][t], f"balance_{pid[p]}{w}")
        # 3. 开线才能生产 / 最小批量（大 M = 本周最多能做多少）
        big_m = (base_hours + max_ot * ot_hours) / hours[p]
        m.add_constr(make[p][t] <= big_m * setup[p][t], f"link_{pid[p]}{w}")
        m.add_constr(make[p][t] >= min_lot[p] * setup[p][t], f"minlot_{pid[p]}{w}")
        hours_used += hours[p] * make[p][t]
        setups_used += setup[p][t]
        stock += inv[p][t]
        cost += setup_cost[p] * setup[p][t] + hold_cost[p] * inv[p][t] + unit_cost[p] * make[p][t]
    m.add_constr(hours_used <= base_hours + ot_hours * ot[t], f"hours{w}")  # 2. 工时
    m.add_constr(setups_used <= max_setups, f"setups{w}")                   # 4. 换线次数
    m.add_constr(stock <= warehouse, f"warehouse{w}")                       # 5. 仓库
    cost += ot_cost * ot[t]
m.set_objective(cost, ObjSense.MINIMIZE)

m.write_lp("hard_production_plan.lp")
print(f"模型：{m.num_vars} 个变量（{m.num_integers} 个整数/0-1），{m.num_constrs} 条约束\n")

r = solve(m, Params(verbose=True, log_every=500))
if not r.has_solution:
    print(f"没有找到可行解：{r.status}")
    sys.exit(1)
val = r.value

print(f"\n状态：{r.status}   总成本：{r.objective:.0f} 元   节点：{r.nodes}   用时：{r.seconds:.2f} 秒\n")
print("生产计划（* = 本周开线）")
# 中文字符显示宽度为 2，这里手工对齐表头
print("周          电钻   角磨机       电锯   加班        工时   库存")
for t in range(T):
    line = f"第{t + 1}周  "
    h = s = 0.0
    for p in range(P):
        on = val(setup[p][t]) > 0.5
        line += f"{val(make[p][t]):7.0f}{'*' if on else ' '}  "
        h += hours[p] * val(make[p][t])
        s += val(inv[p][t])
    print(line + f"{val(ot[t]):3.0f}班  {h:5.0f}/{base_hours + ot_hours * val(ot[t]):<4.0f} {s:6.0f}")

c_setup = c_hold = c_make = c_ot = 0.0
for t in range(T):
    for p in range(P):
        c_setup += setup_cost[p] * val(setup[p][t])
        c_hold += hold_cost[p] * val(inv[p][t])
        c_make += unit_cost[p] * val(make[p][t])
    c_ot += ot_cost * val(ot[t])
print(f"\n成本构成：换线 {c_setup:.0f} + 库存 {c_hold:.0f} + 加班 {c_ot:.0f} + 生产 {c_make:.0f} = "
      f"{c_setup + c_hold + c_ot + c_make:.0f} 元")
print(f"可行性自检：{'通过' if check_feasible(m, r.x) else '失败'}")
