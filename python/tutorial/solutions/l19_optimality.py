"""第 19 课：为什么知道这是最优解——对偶证书和间隙。

求解器不会试遍所有方案。它同时算两个数：找到的最好答案，和“任何答案都不可能超过”的上限。
两个数碰到一起，就证明了最优。这一课自己写这两种“证明”：线性规划的对偶证书、分支定界的间隙，
最后用同样的道理检查一个点球博弈。
运行：python3 python/tutorial/run.py 19
"""
import math

from check import lesson, eq, near, that, done
from minicplex import LinExpr, Model, ObjSense, VarType, INF, solve

# 例题：最大化 5x + 4y，限制 6x + 4y <= 24，x + 2y <= 6，x、y >= 0
C = [5, 4]                 # 目标系数
A = [[6, 4], [1, 2]]       # 约束系数，一行一条约束
B = [24, 6]                # 约束右边


def demo_model(integer):
    """把例题建成 minicplex 模型；integer=True 时 x、y 只能取整数。（已写好）"""
    m = Model()
    t = VarType.INTEGER if integer else VarType.CONTINUOUS
    x = m.add_var(0, INF, t, "x")
    y = m.add_var(0, INF, t, "y")
    m.add_constr(6 * x + 4 * y <= 24, "c1")
    m.add_constr(x + 2 * y <= 6, "c2")
    m.set_objective(5 * x + 4 * y, ObjSense.MAXIMIZE)
    return m


def dual_bound(b, y):
    """用影子价格 y 给每条约束加权，右边加起来就是上限：sum(b[i] * y[i])。
    例：b = [24, 6]，y = [0.75, 0.5] → 0.75 × 24 + 0.5 × 6 = 21。"""
    # >>>
    return sum(bi * yi for bi, yi in zip(b, y))
    # <<<


def dual_feasible(a, c, y, tol=1e-9):
    """这组影子价格能不能当证据？两个条件都要满足：
    ① 每个 y[i] >= 0（<= 约束只能乘非负数，不等号方向才不变）；
    ② 对每个变量 j，加权后的系数不小于目标系数：sum(a[i][j] * y[i] for i) >= c[j]。
    满足了，就有：目标 <= 加权后的左边 <= 加权后的右边。比较时留一点容差 tol。"""
    # >>>
    if any(yi < -tol for yi in y):
        return False
    for j in range(len(c)):
        if sum(a[i][j] * y[i] for i in range(len(y))) < c[j] - tol:
            return False
    return True
    # <<<


def certify_lp(a, b, c, x, y, tol=1e-6):
    """x 是不是最优解？三件事都成立就“证毕”：
    ① x 可行：每个 x[j] >= 0，每条约束 sum(a[i][j] * x[j]) <= b[i]（留容差 tol）；
    ② y 是合格的证据：dual_feasible(a, c, y)；
    ③ 两头相等：目标值 sum(c[j] * x[j]) 和 dual_bound(b, y) 相等（math.isclose，abs_tol=tol）。"""
    # >>>
    if any(xj < -tol for xj in x):
        return False
    for i in range(len(b)):
        if sum(a[i][j] * x[j] for j in range(len(x))) > b[i] + tol:
            return False
    if not dual_feasible(a, c, y):
        return False
    value = sum(cj * xj for cj, xj in zip(c, x))
    return math.isclose(value, dual_bound(b, y), abs_tol=tol)
    # <<<


def relative_gap(incumbent, bound):
    """日志里的 Gap：|上限 - 最好整数解| / |最好整数解|。分母太小时用 1e-10 兜底，免得除以 0。
    例：最好整数解 18，上限 21 → 3 / 18 ≈ 0.1667（日志显示 16.67%）。"""
    # >>>
    return abs(bound - incumbent) / max(1e-10, abs(incumbent))
    # <<<


def proven_optimal(incumbent, bound, rel=1e-6, absolute=1e-6):
    """两头碰上了吗？（最大化）上限 - 最好整数解 <= max(absolute, rel × max(1, |最好整数解|)) 就算证毕。
    这就是 minicplex solver.py 里的判断，CPLEX 的 EpGap、EpAGap 也是这个意思。"""
    # >>>
    return bound - incumbent <= max(absolute, rel * max(1.0, abs(incumbent)))
    # <<<


def game_bounds(m, p, q):
    """零和博弈 m[i][j] 是行方的收益。行方按概率 p 出招，列方按概率 q 出招。返回两个数：
    ① 行方的保底：列方挑最狠的那一列时，行方还能拿多少 = min(每一列 j 的 sum(p[i] * m[i][j]))；
    ② 列方的封顶：行方挑最好的那一行时，最多被拿走多少 = max(每一行 i 的 sum(m[i][j] * q[j]))。
    保底 == 封顶，就证明了双方都是最优。"""
    # >>>
    rows, cols = len(m), len(m[0])
    floor = min(sum(p[i] * m[i][j] for i in range(rows)) for j in range(cols))
    cap = max(sum(m[i][j] * q[j] for j in range(cols)) for i in range(rows))
    return floor, cap
    # <<<


def guess_after_stop():
    """🤔 先猜后跑：先别运行！一道最大化的整数规划，跑到时间上限停下了，日志最后一行是：

        Best Integer 19    Best Bound 20    Gap 5.26%

    真正的最优值一定落在哪个范围？把 (最小可能, 最大可能) 写在 return 后面。"""
    # >>>
    return (19, 20)
    # <<<


# ---------------------------------------------------------------- 点球博弈（已写好）
PENALTY = [  # 行：射门 左 中 右；列：门将 扑左 扑中 扑右；数字是进球率（虚拟）
    [0.55, 0.85, 0.95],
    [0.90, 0.30, 0.90],
    [0.95, 0.85, 0.60],
]


def solve_penalty():
    """用线性规划解点球：射门方的概率 p 让保底 v 最大；门将的概率就是约束的影子价格。返回 (p, q, v)。"""
    m = Model()
    p = [m.add_var(0, 1, name=f"p{i}") for i in range(3)]
    v = m.add_var(-INF, INF, name="v")
    m.add_constr(sum(p, LinExpr()) == 1, "prob")
    for j in range(3):
        m.add_constr(sum((PENALTY[i][j] * p[i] for i in range(3)), LinExpr()) - v >= 0, f"keeper{j}")
    m.set_objective(v, ObjSense.MAXIMIZE)
    r = solve(m)
    return [r.value(x) for x in p], [abs(d) for d in r.duals[1:]], r.objective


def _lp():
    r = solve(demo_model(False))
    return r.x, r.duals


def _mip():
    return solve(demo_model(True))


lesson("第 19 课：为什么知道这是最优解")
near("影子价格 0.75、0.5 给出的上限是 21", 21, lambda: dual_bound(B, [0.75, 0.5]))
that("0.75、0.5 是合格的证据", lambda: dual_feasible(A, C, [0.75, 0.5]))
that("0.5、0.5 不行：x 那一列 6×0.5 + 1×0.5 = 3.5 < 5", lambda: not dual_feasible(A, C, [0.5, 0.5]))
that("负的影子价格不行", lambda: not dual_feasible(A, C, [1.0, -0.1]))
that("求解器的答案 + 影子价格：证毕", lambda: certify_lp(A, B, C, *_lp()))
that("x=3、y=1 可行但不是最优：证不出来", lambda: not certify_lp(A, B, C, [3, 1], [0.75, 0.5]))
that("x=4、y=1 不可行：证不出来", lambda: not certify_lp(A, B, C, [4, 1], [0.75, 0.5]))
near("日志第一行：18 对 21，差距约 16.67%", 1 / 6, lambda: relative_gap(18, 21))
that("19 对 20 还没证完", lambda: not proven_optimal(19, 20))
that("20 对 20 证毕", lambda: proven_optimal(20, 20))
that("整数版：求解器停下时两头确实碰上了", lambda: proven_optimal(_mip().objective, _mip().best_bound))
near("整数版最优值是 20", 20, lambda: _mip().objective)
that("点球：保底 == 封顶（射门方和门将都是最优）",
     lambda: math.isclose(*game_bounds(PENALTY, *solve_penalty()[:2]), abs_tol=1e-6))
near("点球的进球率约 78.1%", 0.7806, lambda: round(game_bounds(PENALTY, *solve_penalty()[:2])[0], 4))
eq("🤔 猜一猜：停在 19 和 20 之间时，最优值的范围", (19, 20), guess_after_stop)
done()
