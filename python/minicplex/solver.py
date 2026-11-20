"""求解线性规划 / 混合整数规划：预处理、根节点 Gomory 割，然后在 LPEngine 上做分支定界。

* 下潜：分支后立刻用父节点的单纯形表解其中一个孩子（热启动，对偶单纯形）；另一个孩子带着父节点的基放进队列
* 下潜结束后选节点：LP 界最小的先做
* 可靠性分支：伪成本，开始时用强分支初始化
* LP 里就剪枝：对偶单纯形的界一旦达到已有整数解就停
* 启发式：把 LP 解四舍五入，再“打磨”、检查

逐行移植自 Java 版 Solver.java（C++ 的 src/branch_and_bound.cpp）。
"""
from __future__ import annotations

import heapq
import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Sequence

from . import jmath
from . import lp_engine as lpe
from . import presolve
from .fmt import g
from .model import INF, Model, ObjSense, Sense, Var

_isfinite = math.isfinite
cround = jmath.cround


class Branching(Enum):
    """分支变量的选择规则。"""
    MOST_FRACTIONAL = "frac"  # 选最接近 .5 的变量
    PSEUDO_COST = "pc"        # 选估计能让界提高最多的变量（可靠性分支）


class Status(Enum):
    """求解的最终状态。名字和 C++ 版一样（CSV 输出里用）。"""
    OPTIMAL = "Optimal"
    INFEASIBLE = "Infeasible"
    UNBOUNDED = "Unbounded"
    INFEASIBLE_OR_UNBOUNDED = "InfeasibleOrUnbounded"
    NODE_LIMIT = "NodeLimit"
    TIME_LIMIT = "TimeLimit"
    ITERATION_LIMIT = "IterationLimit"

    def __str__(self) -> str:
        return self.value


@dataclass
class Params:
    """求解参数（默认值和 C++ 版一样）。"""
    relax_integrality: bool = False      # 只解线性松弛
    branching: Branching = Branching.PSEUDO_COST
    cut_rounds: int = 2                  # 根节点 Gomory 割的轮数（0 = 不加）
    presolve: bool = True                # 界传播 + 系数收紧
    int_tol: float = 1e-6                # 整数容差（CPLEX EpInt）
    mip_gap: float = 1e-6                # 相对间隙（CPLEX EpGap）
    mip_abs_gap: float = 1e-6            # 绝对间隙（CPLEX EpAGap）
    node_limit: int = 10_000_000
    time_limit: float = 1e30             # 秒
    verbose: bool = False                # 打印 CPLEX 风格的节点日志
    trace: bool = False                  # 打印每一次单纯形转轴和分支决定
    log_every: int = 100                 # 每 N 个节点打印一行日志


@dataclass
class Result:
    """solve() 的结果。"""
    status: Status = Status.INFEASIBLE
    has_solution: bool = False
    objective: float = math.nan
    best_bound: float = math.nan
    gap: float = math.nan                # 整数解和界的相对间隙
    x: List[float] = field(default_factory=list)            # 变量取值，顺序同 Model.vars
    duals: List[float] = field(default_factory=list)        # 只有 LP：每条约束的影子价格
    reduced_costs: List[float] = field(default_factory=list)  # 只有 LP：每个变量的既约成本
    nodes: int = 0
    lp_iterations: int = 0
    cuts: int = 0                        # 根节点保留下来的 Gomory 割
    seconds: float = 0.0

    def value(self, v: Var) -> float:
        """变量 v 在解里的值。"""
        return self.x[v.id]


def solve(M: Model, P: Optional[Params] = None) -> Result:
    return _Run(M, P if P is not None else Params()).solve()


def eval_objective(M: Model, x: Sequence[float]) -> float:
    """x 处的目标值（按模型自己的方向）。"""
    v = M.objective.constant
    terms = M.objective.terms
    for k in sorted(terms):
        v += terms[k] * x[k]
    return v


def check_feasible(M: Model, x: Sequence[float], tol: float = 1e-6, check_int: bool = True) -> bool:
    """检查上下界、整数要求和每一条约束，容差 tol * (1 + |rhs|)。"""
    for j, v in enumerate(M.vars):
        if x[j] < v.lb - tol or x[j] > v.ub + tol:
            return False
        if check_int and M.is_integer(j) and abs(x[j] - cround(x[j])) > tol:
            return False
    for c in M.constraints:
        lhs = 0.0
        for k, a in c.coefs.items():
            lhs += a * x[k]
        t = tol * (1.0 + abs(c.rhs))
        if c.sense == Sense.LE and lhs > c.rhs + t:
            return False
        if c.sense == Sense.GE and lhs < c.rhs - t:
            return False
        if c.sense == Sense.EQ and abs(lhs - c.rhs) > t:
            return False
    return True


# ------------------------------------------------------------ 搜索状态

class _Node:
    __slots__ = ("lb", "ub", "bound", "depth", "basis", "branch_var", "dir", "dist", "parent_obj", "seq")

    def __init__(self, lb: List[float], ub: List[float], bound: float, depth: int, basis: Optional[lpe.Basis]) -> None:
        self.lb = lb
        self.ub = ub
        self.bound = bound        # 从父节点继承的下界（内部是最小化）
        self.depth = depth
        self.basis = basis        # 父节点的最优基（热启动）
        self.branch_var = -1      # 这个节点是怎么分出来的（学习伪成本用）
        self.dir = 0              # 0 = 向下分支，1 = 向上分支
        self.dist = 0.0           # 变量被挪动的距离
        self.parent_obj = 0.0
        self.seq = 0              # 插入顺序：最后的平局规则，让搜索顺序完全确定


class _PseudoCosts:
    """每单位变化让目标变差多少，向下、向上分开学习。"""

    def __init__(self, n: int) -> None:
        self.sum = [[0.0] * n, [0.0] * n]
        self.cnt = [[0] * n, [0] * n]
        self.tot_sum = [0.0, 0.0]
        self.tot_cnt = [0, 0]

    def update(self, j: int, d: int, gain_per_unit: float) -> None:
        self.sum[d][j] += gain_per_unit
        self.cnt[d][j] += 1
        self.tot_sum[d] += gain_per_unit
        self.tot_cnt[d] += 1

    def get(self, j: int, d: int) -> float:
        if self.cnt[d][j] > 0:
            return self.sum[d][j] / self.cnt[d][j]
        return self.tot_sum[d] / self.tot_cnt[d] if self.tot_cnt[d] > 0 else 1.0  # 还没数据：用全局平均


def _sb_fmt(v: float, huge: float) -> str:
    if v >= huge:
        return "剪掉"
    return ("%f" % v)[:6]


class _Run:
    def __init__(self, M: Model, P: Params) -> None:
        self.M = M
        self.P = P
        self.t0 = time.perf_counter()
        self.R = Result()
        self.nv = M.num_vars
        self.sgn = -1.0 if M.obj_sense == ObjSense.MAXIMIZE else 1.0
        self.max_it = 200000 + 50 * (self.nv + M.num_constrs)
        self.ints: List[int] = []
        self.lb: List[float] = []
        self.ub: List[float] = []
        self.LM: Model = M          # 交给 LP 引擎的模型
        self.E: lpe.LPEngine
        self.obj_integral = True
        self.obj_const = 0.0
        self.inc = INF              # 已有整数解（内部最小化）
        self.inc_x: Optional[List[float]] = None
        self.has_continuous = False
        self.open: list = []        # 堆：(bound, -0.0 在前, -depth, -seq, node)
        self.node_seq = 0
        self.cur: Optional[_Node] = None
        self.have_cur = False

    def elapsed(self) -> float:
        return time.perf_counter() - self.t0

    def strengthen(self, b: float) -> float:
        if not self.obj_integral or not _isfinite(b):
            return b
        return jmath.ceil(b - self.obj_const - 1e-6) + self.obj_const

    def close_enough(self, bound: float, incumbent: float) -> bool:
        P = self.P
        return incumbent - bound <= max(P.mip_abs_gap, P.mip_gap * max(1.0, abs(incumbent)))

    def cutoff(self) -> float:
        if self.inc_x is None:
            return INF
        P, inc = self.P, self.inc
        c = inc - max(P.mip_abs_gap, P.mip_gap * max(1.0, abs(inc)))
        if self.obj_integral:
            c = min(c, inc - 1.0 + 1e-6)
        return c

    def try_incumbent(self, x_in: List[float]) -> int:
        """接受候选解之前先“打磨”：把整数变量固定在四舍五入后的值，用新的 LP 重解连续部分。

        返回 1 = 接受，0 = 不比已有整数解好，-1 = 不可行、放弃。
        """
        M = self.M
        x = list(x_in)
        for j in self.ints:
            x[j] = cround(x[j])
        # 便宜的过滤；有连续变量时由打磨用的 LP 决定可不可行
        if not check_feasible(M, x, 1e-4 if self.has_continuous else 1e-6):
            return -1
        if self.sgn * eval_objective(M, x) >= self.inc + 1e-6 * (1.0 + abs(self.inc)):
            return 0
        if self.has_continuous:
            plb = [v.lb for v in M.vars]
            pub = [v.ub for v in M.vars]
            for j in self.ints:
                plb[j] = pub[j] = x[j]
            pol = lpe.lp_min(M, plb, pub, self.sgn, self.max_it)
            if pol.status != lpe.OPTIMAL:
                return -1
            x = pol.x
            for j in self.ints:
                x[j] = plb[j]
        if not check_feasible(M, x, 1e-7):
            return -1
        v = self.sgn * eval_objective(M, x)
        if v < self.inc - 1e-12:
            self.inc = v
            self.inc_x = x
            return 1
        return 0

    def best_bound(self) -> float:
        b = self.inc
        if self.open:
            b = jmath.jmin(b, self.open[0][0])
        if self.have_cur:
            b = jmath.jmin(b, self.cur.bound)  # type: ignore[union-attr]
        return b

    def log_line(self, mark: str, node_obj: float) -> None:
        bnd = self.best_bound()
        inc = self.inc
        gap = abs(inc - bnd) / max(1e-10, abs(inc)) if _isfinite(inc) else INF
        print("%1s%8d %7d %15s %15s %15s %7.2f%%" % (mark, self.R.nodes, len(self.open), g(self.sgn * node_obj),
                                                   g(self.sgn * inc) if _isfinite(inc) else "nan",
                                                   g(self.sgn * bnd), 100 * gap))

    def new_engine(self, model: Model) -> None:
        self.E = lpe.LPEngine(model, self.sgn)
        self.E.set_all_col_bounds(self.lb, self.ub)
        self.E.set_trace(self.P.trace)

    def push(self, node: _Node) -> None:
        # 和 Java 版的比较器一致：界小的先出；界相同时深的先出；再相同时新的先出
        heapq.heappush(self.open, (node.bound, jmath.neg_zero_first(node.bound), -node.depth, -node.seq, node))

    def solve(self) -> Result:
        M, P, R, nv, sgn = self.M, self.P, self.R, self.nv, self.sgn
        self.lb = [v.lb for v in M.vars]
        self.ub = [v.ub for v in M.vars]
        lb, ub = self.lb, self.ub
        for j in range(nv):
            if not P.relax_integrality and M.is_integer(j):
                self.ints.append(j)
                if _isfinite(lb[j]):
                    lb[j] = jmath.ceil(lb[j] - P.int_tol)
                if _isfinite(ub[j]):
                    ub[j] = jmath.floor(ub[j] + P.int_tol)
        ints = self.ints

        # ---------------- 预处理（只对 MIP） ----------------
        self.LM = M
        if P.presolve and ints:
            is_int_col = [False] * nv
            for j in ints:
                is_int_col[j] = True
            PM = M.copy()
            ps = presolve.Stats()
            feasible = presolve.run(PM, lb, ub, is_int_col, ps)
            if P.verbose or P.trace:
                print(f"Presolve: {ps.bounds_tightened} bounds tightened, {ps.coefs_tightened} coefficients tightened, "
                      f"{ps.rows_removed} rows removed" + ("" if feasible else ", INFEASIBLE"))
            if not feasible:
                R.status = Status.INFEASIBLE
                R.seconds = self.elapsed()
                return R
            self.LM = PM
        self.new_engine(self.LM)

        # ---------------- 纯线性规划 ----------------
        if not ints:
            E = self.E
            st = E.solve(self.max_it)
            R.lp_iterations = E.iterations()
            R.seconds = self.elapsed()
            if st == lpe.OPTIMAL:
                R.status = Status.OPTIMAL
                R.has_solution = True
                R.x = E.col_values()
                R.duals = E.row_duals()
                R.reduced_costs = E.col_reduced_costs()
                R.objective = R.best_bound = sgn * E.objective()
                R.gap = 0.0
            elif st == lpe.INFEASIBLE:
                R.status = Status.INFEASIBLE
            elif st == lpe.UNBOUNDED:
                R.status = Status.UNBOUNDED
            else:
                R.status = Status.ITERATION_LIMIT
            if P.verbose:
                print("LP solved: %s, %d simplex iterations, %.3f s" % (R.status, R.lp_iterations, R.seconds))
            return R

        # ---------------- 整数规划：分支定界 ----------------
        for k in sorted(M.objective.terms):
            c = M.objective.terms[k]
            if c != 0.0 and (not M.is_integer(k) or c != cround(c)):
                self.obj_integral = False
        self.obj_const = sgn * M.objective.constant
        for j in range(nv):
            self.has_continuous |= not M.is_integer(j) or P.relax_integrality

        cut_iters = self.root_cuts()

        pc = _PseudoCosts(nv)
        self.cur = _Node(list(lb), list(ub), -INF, 0, None)
        self.have_cur = True  # 根节点：引擎里已经是这些界和松弛基
        incomplete = False
        stop = Status.OPTIMAL

        if P.verbose:
            print("%9s %7s %15s %15s %15s %8s" % ("Node", "Left", "Objective", "Best Integer", "Best Bound", "Gap"))

        HUGE = 1e12
        while True:
            if not self.have_cur:
                if not self.open:
                    break
                if self.inc_x is not None and self.close_enough(self.open[0][0], self.inc):
                    break
                self.cur = heapq.heappop(self.open)[-1]
                self.have_cur = True
                if P.trace:
                    print("\n（下潜结束，从队列取出界最好的节点，恢复它保存的基）")
                self.E.set_all_col_bounds(self.cur.lb, self.cur.ub)
                self.E.load_basis(self.cur.basis)  # type: ignore[arg-type]
            cur, E = self.cur, self.E
            assert cur is not None
            if R.nodes >= P.node_limit:
                stop = Status.NODE_LIMIT
                break
            if self.elapsed() > P.time_limit:
                stop = Status.TIME_LIMIT
                break
            R.nodes += 1
            if P.trace:
                s = f"\n[节点 {R.nodes}] 深度 {cur.depth}"
                if cur.branch_var >= 0:
                    bvar = cur.branch_var
                    s += (f"，由 {M.vars[bvar].name} "
                          + (f"≥ {int(cur.lb[bvar])}" if cur.dir == 1 else f"≤ {int(cur.ub[bvar])}") + " 分出来")
                print(s)
            st = E.solve(self.max_it, self.cutoff())

            if st == lpe.INFEASIBLE or st == lpe.CUTOFF:
                if P.trace:
                    print("  剪枝：" + ("这种情况不可行" if st == lpe.INFEASIBLE else "这种情况最好也比已有整数解差"))
                self.have_cur = False
                continue
            if st == lpe.UNBOUNDED:
                if R.nodes == 1:
                    R.status = Status.INFEASIBLE_OR_UNBOUNDED
                    R.lp_iterations = E.iterations()
                    R.seconds = self.elapsed()
                    return R
                incomplete = True  # 不该发生：孩子只会更受限
                self.have_cur = False
                continue
            if st == lpe.ITERATION_LIMIT:
                incomplete = True
                self.have_cur = False
                continue

            x = E.col_values()
            lp_obj = E.objective()
            if cur.branch_var >= 0 and cur.dist > 1e-9:
                pc.update(cur.branch_var, cur.dir, max(0.0, lp_obj - cur.parent_obj) / cur.dist)
            node_bound = self.strengthen(lp_obj)
            cur.bound = node_bound
            if self.inc_x is not None and self.close_enough(node_bound, self.inc):
                if P.trace:
                    print(f"  剪枝：界 {g(sgn * node_bound)} 不比已有整数解 {g(sgn * self.inc)} 好")
                self.have_cur = False
                continue

            # 可靠性分支：还没观察过的候选变量，用强分支试算
            sb_gain: List[List[float]] = []
            sb_var: List[int] = []
            prune_node = False
            if P.branching == Branching.PSEUDO_COST:
                unrel = []  # (frac, j)
                for j in ints:
                    f = x[j] - jmath.floor(x[j])
                    frac = min(f, 1.0 - f)
                    if frac > P.int_tol and (pc.cnt[0][j] < 1 or pc.cnt[1][j] < 1):
                        unrel.append((frac, j))
                unrel.sort(key=lambda u: -u[0])  # 稳定排序，和 Java 一样
                unrel = unrel[:8]
                if unrel:
                    B = E.basis()
                    E.set_trace(False)
                    for _, j in unrel:
                        v = x[j]
                        fl, ce = jmath.floor(v), jmath.ceil(v)
                        gains = [0.0, 0.0]
                        for d in range(2):
                            olb, oub = cur.lb[j], cur.ub[j]
                            if d == 0:
                                E.set_col_bounds(j, olb, fl)
                            else:
                                E.set_col_bounds(j, ce, oub)
                            s2 = E.solve(40, self.cutoff())
                            dist = v - fl if d == 0 else ce - v
                            if s2 == lpe.INFEASIBLE:
                                gains[d] = HUGE
                            elif s2 == lpe.CUTOFF:
                                gains[d] = max(self.cutoff() - lp_obj, 1e-6)
                                pc.update(j, d, gains[d] / dist)
                                gains[d] = HUGE  # 这一侧会被马上剪掉
                            else:
                                gains[d] = max(0.0, E.objective() - lp_obj)
                                if s2 == lpe.OPTIMAL:
                                    pc.update(j, d, gains[d] / dist)
                            E.set_col_bounds(j, olb, oub)
                            E.load_basis(B)
                        sb_var.append(j)
                        sb_gain.append(gains)
                        if P.trace:
                            print(f"  强分支试算 {M.vars[j].name} = {g(x[j], 4)}：向下目标变差 {_sb_fmt(gains[0], HUGE)}"
                                  f"，向上变差 {_sb_fmt(gains[1], HUGE)}")
                        if gains[0] >= HUGE and gains[1] >= HUGE:
                            prune_node = True
                            break
            E.set_trace(P.trace)
            if prune_node:  # 两个孩子都不可行或被截断
                if P.trace:
                    print("  剪枝：强分支发现某个变量两侧都不可行或被截断")
                self.have_cur = False
                continue

            # 选分支变量：伪成本乘积打分，或者最接近 .5 的
            bj = -1
            best_score, best_frac = -1.0, 0.0
            for j in ints:
                f = x[j] - jmath.floor(x[j])
                frac = min(f, 1.0 - f)
                if frac <= P.int_tol:
                    continue
                score = frac
                if P.branching == Branching.PSEUDO_COST:
                    down, up = pc.get(j, 0) * f, pc.get(j, 1) * (1.0 - f)
                    for k in range(len(sb_var)):
                        if sb_var[k] == j:
                            down, up = sb_gain[k]
                    score = max(down, 1e-6) * max(up, 1e-6)
                if score > best_score * (1 + 1e-9) or (score >= best_score * (1 - 1e-9) and frac > best_frac):
                    best_score = score
                    best_frac = frac
                    bj = j
            if bj < 0:  # LP 解全是整数
                res = self.try_incumbent(x)
                if P.trace:
                    if res == 1:
                        print(f"  LP 解全是整数，成为新的最优整数解：{g(sgn * self.inc)}")
                    elif res == 0:
                        print("  LP 解全是整数，但不比已有整数解好")
                    else:
                        print("  LP 解全是整数，但严格检查不可行（只在数值误差范围内成立），放弃")
                if res == 1 and P.verbose:
                    self.log_line("*", lp_obj)
                self.have_cur = False
                continue
            if self.try_incumbent(x) == 1:
                if P.trace:
                    parts = [f"{M.vars[j].name} = {g(self.inc_x[j])}" for j in range(nv) if M.is_integer(j)]  # type: ignore[index]
                    print("  取整启发式：把 LP 解四舍五入后得到可行的整数解（" + "，".join(parts)
                          + f"），新的最优整数解：{g(sgn * self.inc)}")
                if P.verbose:
                    self.log_line("H", lp_obj)
                if self.close_enough(node_bound, self.inc):
                    self.have_cur = False
                    continue

            # 分支：沿四舍五入的方向下潜，另一个孩子放进队列
            v = x[bj]
            fl, ce = jmath.floor(v), jmath.ceil(v)
            go_up = (v - fl) >= 0.5
            sib = _Node(list(cur.lb), list(cur.ub), node_bound, cur.depth + 1, E.basis())
            if go_up:
                sib.ub[bj] = fl
            else:
                sib.lb[bj] = ce
            sib.branch_var = bj
            sib.dir = 0 if go_up else 1
            sib.dist = v - fl if go_up else ce - v
            sib.parent_obj = lp_obj
            self.node_seq += 1
            sib.seq = self.node_seq
            self.push(sib)

            if go_up:
                cur.lb[bj] = ce
            else:
                cur.ub[bj] = fl
            cur.depth += 1
            cur.branch_var = bj
            cur.dir = 1 if go_up else 0
            cur.dist = ce - v if go_up else v - fl
            cur.parent_obj = lp_obj
            E.set_col_bounds(bj, cur.lb[bj], cur.ub[bj])  # 热启动：同一张单纯形表

            if P.trace:
                name = M.vars[bj].name
                print(f"  分支：{name} = {g(v, 4)} 不是整数 → 先走 {name}{' ≥ ' if go_up else ' ≤ '}"
                      + "%.0f" % (ce if go_up else fl) + f"（下潜，接着用当前单纯形表），{name}"
                      + (" ≤ " if go_up else " ≥ ") + "%.0f" % (fl if go_up else ce) + " 放进队列")
            if P.verbose and R.nodes % P.log_every == 0:
                self.log_line("", lp_obj)

        R.seconds = self.elapsed()
        R.lp_iterations = self.E.iterations() + cut_iters
        bound = self.best_bound()
        if self.inc_x is None:
            R.status = stop if stop != Status.OPTIMAL else Status.ITERATION_LIMIT if incomplete else Status.INFEASIBLE
        else:
            R.status = stop
            if stop == Status.OPTIMAL and incomplete:
                R.status = Status.ITERATION_LIMIT
            R.has_solution = True
            R.x = self.inc_x
            R.objective = sgn * self.inc
            R.best_bound = sgn * bound
            R.gap = abs(self.inc - bound) / max(1e-10, abs(self.inc))
        if P.verbose:
            print("B&B done: %s, %d nodes, %d simplex iterations, %.3f s" % (R.status, R.nodes, R.lp_iterations, R.seconds))
        return R

    def root_cuts(self) -> int:
        """根节点的几轮 Gomory 混合整数割。

        每一轮的割作为新的行加进去，从上一次的基出发（新松弛变量在基里）用对偶单纯形重新优化。
        最后不起作用的割再去掉。返回花掉的迭代次数。
        """
        P, M, nv, sgn = self.P, self.M, self.nv, self.sgn
        cut_iters = 0
        if P.cut_rounds <= 0 or self.E.solve(self.max_it) != lpe.OPTIMAL:
            return 0
        is_int_col = [False] * nv
        for j in self.ints:
            is_int_col[j] = True
        W = self.LM.copy()
        m0 = W.num_constrs
        obj = self.E.objective()
        for rnd in range(P.cut_rounds):
            x = self.E.col_values()
            fractional = False
            for j in self.ints:
                fractional |= abs(x[j] - cround(x[j])) > P.int_tol
            if not fractional:
                break
            cuts = self.E.gomory_cuts(is_int_col, max(5, min(20, W.num_constrs)))
            if not cuts:
                break
            n_cuts = len(cuts)
            B = self.E.basis()
            head = B.head + [0] * n_cuts
            stat = B.stat + [0] * n_cuts
            for k, c in enumerate(cuts):
                if P.trace:
                    parts = []
                    for i, (j, a) in enumerate(c.coefs.items()):
                        parts.append(("" if i == 0 else (" - " if a < 0 else " + ")) + g(a if i == 0 else abs(a))
                                     + " " + M.vars[j].name)
                    print(f"[割平面] 新割 gmi{W.num_constrs - m0 + 1}：" + "".join(parts) + f" ≥ {g(c.rhs)}")
                head[len(B.head) + k] = nv + W.num_constrs  # 新的松弛变量一开始在基里
                stat[len(B.stat) + k] = lpe.BASIC
                W.add_constr(c, f"gmi{W.num_constrs - m0 + 1}")
            cut_iters += self.E.iterations()
            self.new_engine(W)
            self.E.load_basis(lpe.Basis(head, stat), True)
            if P.trace:
                print(f"[割平面] 第 {rnd + 1} 轮：加入 {n_cuts} 个 Gomory 割，重新求解根节点")
            if self.E.solve(self.max_it) != lpe.OPTIMAL:
                break
            nobj = self.E.objective()
            if P.trace:
                print(f"[割平面] 根节点的界：{g(sgn * obj)} → {g(sgn * nobj)}")
            stalled = nobj - obj < 1e-4 * (1.0 + abs(obj))
            obj = nobj
            if stalled:
                break
        # 只保留在最后的根节点 LP 里起作用的割
        if W.num_constrs > m0:
            x = self.E.col_values()
            K = self.LM.copy()
            for i in range(m0, W.num_constrs):
                c = W.constraints[i]
                act = 0.0
                for k, a in c.coefs.items():
                    act += a * x[k]
                if act <= c.rhs + 1e-6 * (1.0 + abs(c.rhs)):
                    K.add_constr(c.copy())
            self.R.cuts = K.num_constrs - m0
            cut_iters += self.E.iterations()
            self.new_engine(K)
        if P.verbose and self.R.cuts > 0:
            print(f"Root cuts: {self.R.cuts} Gomory cuts kept, root bound {g(sgn * obj)}")
        return cut_iters
