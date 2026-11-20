"""有界变量单纯形法（原始 + 对偶），用一张稠密的单纯形表。

计算形式::

    A x - s = 0,    l <= x <= u,    rlo <= s <= rhi

每条约束 i 配一个松弛变量 s_i = a_i x，它的上下界由约束方向决定
（<=: (-inf, b]，>=: [b, inf)，=: [b, b]）。变量的上下界是“隐式”处理的：非基变量
停在下界、上界，或者（自由变量）停在 0。所以上下界不会变成额外的行，也不需要人工变量：
全松弛基永远是一个合法的起点。

单纯形表 T = B^-1 [A | -I]（m 行 n+m 列）和既约成本 d、所有变量的取值 x 一起保存，
满足 x_B = - sum_{j 非基} T[:, j] x_j。

* 原始单纯形：组合式第一阶段（最小化越界量之和），再第二阶段，支持“翻到另一侧边界”。
* 对偶单纯形：只要当前基对偶可行就用它，例如分支定界收紧了某个基变量的界之后。
* 防循环：连续多次退化转轴后改用 Bland 规则；定期从原始矩阵重建单纯形表，防止舍入误差累积。

逐行移植自 Java 版 LPEngine.java（它又逐行移植自 C++ 的 src/simplex.cpp），
所以三个版本每一步都走得一模一样。
"""
from __future__ import annotations

import math
from typing import List, Optional

from . import jmath
from .fmt import g
from .model import INF, Constraint, Model, Sense

PRIMAL_TOL = 1e-7   # 允许的越界量（按大小缩放）
DUAL_TOL = 1e-9     # 既约成本的容差
PIVOT_TOL = 1e-9    # 能接受的最小转轴元
BLAND_AFTER = 50    # 连续这么多次退化转轴后改用 Bland 规则

BASIC, LOWER, UPPER, FREE, FIXED, UNSET = 0, 1, 2, 3, 4, -1

# LP 求解状态
OPTIMAL, INFEASIBLE, UNBOUNDED, ITERATION_LIMIT, CUTOFF = range(5)

_isfinite = math.isfinite


class Basis:
    """可以保存、恢复的单纯形基（热启动用）。"""
    __slots__ = ("head", "stat")

    def __init__(self, head: List[int], stat: List[int]) -> None:
        self.head = head  # 每一行的基变量
        self.stat = stat  # 每个变量（结构变量 + 松弛变量）的状态

    def copy(self) -> "Basis":
        return Basis(list(self.head), list(self.stat))


class LPEngine:
    def __init__(self, M: Model, obj_sign: float) -> None:
        n, m = M.num_vars, M.num_constrs
        N = n + m
        self.n, self.m, self.N = n, m, N
        A = [0.0] * (m * n)
        c = [0.0] * N
        lb = [0.0] * N
        ub = [INF] * N
        for i, con in enumerate(M.constraints):
            for k, v in con.coefs.items():
                A[i * n + k] += v
            s = n + i
            lb[s] = -INF if con.sense == Sense.LE else con.rhs
            ub[s] = INF if con.sense == Sense.GE else con.rhs
        for j, v in enumerate(M.vars):
            lb[j] = v.lb
            ub[j] = v.ub
        for k in sorted(M.objective.terms):
            c[k] += obj_sign * M.objective.terms[k]
        self.A, self.c, self.lb, self.ub = A, c, lb, ub
        self.obj_const = obj_sign * M.objective.constant
        self.obj_sign = obj_sign
        self.names = [v.name for v in M.vars] + [f"s({con.name})" for con in M.constraints]
        self.T: Optional[List[float]] = None
        self.d: List[float] = []
        self.x: List[float] = []
        self.head: Optional[List[int]] = None
        self.stat: List[int] = []
        self.iters = 0
        self.pivots_since_refactor = 0
        self.pivots_since_recompute = 0
        self.values_dirty = True
        self.trace = False
        # 全松弛的初始基
        self.load_basis(Basis([n + i for i in range(m)], [UNSET] * N), True)

    def set_trace(self, on: bool) -> None:
        self.trace = on

    def iterations(self) -> int:
        return self.iters

    def basis(self) -> Basis:
        return Basis(list(self.head), list(self.stat))  # type: ignore[arg-type]

    # ------------------------------------------------------------ 状态

    def _default_status(self, j: int) -> int:
        lb, ub = self.lb[j], self.ub[j]
        lf, uf = _isfinite(lb), _isfinite(ub)
        if lf and uf and lb == ub:
            return FIXED
        if lf and uf:
            return UPPER if self.c[j] < 0 else LOWER  # 选对偶可行的那一侧
        if lf:
            return LOWER
        if uf:
            return UPPER
        return FREE

    def _value_for(self, s: int, j: int) -> float:
        if s == LOWER or s == FIXED:
            return self.lb[j]
        if s == UPPER:
            return self.ub[j]
        return 0.0

    def _nonbasic_value(self, j: int) -> float:
        return self._value_for(self.stat[j], j)

    def _valid_status(self, s: int, j: int) -> bool:
        lb, ub = self.lb[j], self.ub[j]
        return ((s == LOWER and _isfinite(lb)) or (s == UPPER and _isfinite(ub))
                or (s == FREE and not _isfinite(lb) and not _isfinite(ub)) or (s == FIXED and lb == ub))

    def load_basis(self, b: Basis, from_scratch: bool = False) -> None:
        """换到基 b，重新计算 x 和 d。

        默认是增量方式：把缺的列转进当前单纯形表。from_scratch=True：从原始矩阵重建 T（清掉舍入误差）。
        """
        n, m, N = self.n, self.m, self.N
        if (not from_scratch and self.head is not None and len(self.head) == m and self.T is not None
                and self.pivots_since_refactor < max(200, 2 * m)):
            T, stat, head = self.T, self.stat, self.head
            wanted = [False] * N
            for v in b.head:
                wanted[v] = True
            ok = True
            for q in b.head:
                if stat[q] == BASIC:
                    continue
                r = -1
                best = 1e-7
                for i in range(m):
                    if wanted[head[i]]:
                        continue
                    a = abs(T[i * N + q])
                    if a > best:
                        best = a
                        r = i
                if r < 0:
                    ok = False
                    break
                stat[head[r]] = LOWER  # 下面再改成正确的状态
                self._pivot(r, q)
                stat[q] = BASIC
            if ok:
                for j in range(N):
                    if stat[j] == BASIC:
                        continue
                    s = b.stat[j] if j < len(b.stat) else UNSET
                    stat[j] = s if self._valid_status(s, j) else self._default_status(j)
                self._recompute_values()
                self._recompute_reduced_costs()
                return
        A = self.A
        T = [0.0] * (m * N)
        for i in range(m):
            base = i * N
            for j in range(n):
                T[base + j] = -A[i * n + j]
            T[base + n + i] = 1.0
        self.T = T
        head = [n + i for i in range(m)]
        self.head = head
        stat = [LOWER] * N
        for i in range(m):
            stat[n + i] = BASIC
        self.stat = stat

        wanted = [False] * N
        for v in b.head:
            wanted[v] = True
        self.d = [0.0] * N  # _pivot() 会更新 d，先让它有定义
        for q in b.head:
            if q >= n:
                continue  # 松弛变量本来就在基里
            r = -1
            best = PIVOT_TOL
            for i in range(m):
                h = head[i]
                if h < n or wanted[h]:
                    continue  # 这一行已经放着一个想要的变量
                a = abs(T[i * N + q])
                if a > best:
                    best = a
                    r = i
            if r >= 0:
                stat[head[r]] = LOWER  # 占位，下面再改
                self._pivot(r, q)
                stat[q] = BASIC
        # 非基变量的状态：保存的状态仍然合法就沿用
        for j in range(N):
            if stat[j] == BASIC:
                continue
            s = b.stat[j] if j < len(b.stat) else UNSET
            stat[j] = s if self._valid_status(s, j) else self._default_status(j)
        self.x = [0.0] * N
        self._recompute_values()
        self._recompute_reduced_costs()
        self.pivots_since_refactor = 0

    def _recompute_values(self) -> None:
        self.values_dirty = False
        self.pivots_since_recompute = 0
        N, x, stat, T = self.N, self.x, self.stat, self.T
        nb = []
        for j in range(N):
            if stat[j] != BASIC:
                x[j] = self._nonbasic_value(j)
                if x[j] != 0.0:
                    nb.append(j)
        for i in range(self.m):
            v = 0.0
            row = i * N
            for j in nb:
                v -= T[row + j] * x[j]
            x[self.head[i]] = v

    def _recompute_reduced_costs(self) -> None:
        N, T, c = self.N, self.T, self.c
        d = list(c)
        for i in range(self.m):
            cb = c[self.head[i]]
            if cb == 0.0:
                continue
            row = i * N
            for j in range(N):
                d[j] -= cb * T[row + j]
        for i in range(self.m):
            d[self.head[i]] = 0.0
        self.d = d

    def _pivot(self, r: int, q: int) -> None:
        N, T = self.N, self.T
        pr = r * N
        inv = 1.0 / T[pr + q]
        nz = []
        for j in range(N):
            if T[pr + j] == 0.0:
                continue
            T[pr + j] *= inv
            nz.append(j)
        T[pr + q] = 1.0
        prow = [(j, T[pr + j]) for j in nz]
        for i in range(self.m):
            if i == r:
                continue
            pi = i * N
            f = T[pi + q]
            if f == 0.0:
                continue
            for j, t in prow:
                T[pi + j] -= f * t
            T[pi + q] = 0.0
        d = self.d
        f = d[q]
        if f != 0.0:
            for j, t in prow:
                d[j] -= f * t
            d[q] = 0.0
        self.head[r] = q  # type: ignore[index]
        self.pivots_since_refactor += 1
        self.pivots_since_recompute += 1

    def set_col_bounds(self, j: int, l: float, u: float) -> None:
        self.lb[j] = l
        self.ub[j] = u
        if self.stat[j] == BASIC:
            return  # 可能变成原始不可行：交给对偶单纯形
        old = self.x[j]
        if not self._valid_status(self.stat[j], j):
            self.stat[j] = self._default_status(j)
        if l == u:
            self.stat[j] = FIXED
        self.x[j] = self._nonbasic_value(j)
        delta = self.x[j] - old
        if delta != 0.0:
            N, T, x, head = self.N, self.T, self.x, self.head
            for i in range(self.m):
                x[head[i]] -= T[i * N + j] * delta

    def set_all_col_bounds(self, l: List[float], u: List[float]) -> None:
        for j in range(self.n):
            self.lb[j] = l[j]
            self.ub[j] = u[j]
        self.values_dirty = True

    def objective(self) -> float:
        """obj_sign * (c'x + c0)，也就是内部（最小化）的目标值。"""
        v = self.obj_const
        c, x = self.c, self.x
        for j in range(self.n):
            v += c[j] * x[j]
        return v

    def _real_objective(self) -> float:
        return self.obj_sign * self.objective()

    def col_values(self) -> List[float]:
        return self.x[:self.n]

    def row_duals(self) -> List[float]:
        """影子价格（按模型自己的优化方向；用 T 重新算松弛变量的既约成本）。"""
        n, m, N, T, c, head = self.n, self.m, self.N, self.T, self.c, self.head
        y = [0.0] * m
        for k in range(m):
            j = n + k
            if self.stat[j] == BASIC:
                continue  # 不起作用的约束：价格是 0
            dj = c[j]
            for i in range(m):
                dj -= c[head[i]] * T[i * N + j]
            y[k] = 0.0 if abs(dj) < 1e-12 else self.obj_sign * dj
        return y

    def col_reduced_costs(self) -> List[float]:
        """结构变量的既约成本（按模型自己的优化方向）。"""
        n, m, N, T, c, head = self.n, self.m, self.N, self.T, self.c, self.head
        r = [0.0] * n
        for j in range(n):
            if self.stat[j] == BASIC:
                continue
            dj = c[j]
            for i in range(m):
                dj -= c[head[i]] * T[i * N + j]
            r[j] = 0.0 if abs(dj) < 1e-12 else self.obj_sign * dj
        return r

    def _infeasibility(self, v: int) -> float:
        """> 0：变量 v 越界了多少。"""
        lb, ub, xv = self.lb[v], self.ub[v], self.x[v]
        tl = PRIMAL_TOL * (1.0 + abs(lb))
        tu = PRIMAL_TOL * (1.0 + abs(ub))
        if xv < lb - tl:
            return lb - xv
        if xv > ub + tu:
            return xv - ub
        return 0.0

    def _make_dual_feasible(self) -> bool:
        """把有上下界的非基变量放到和既约成本符号相符的那一侧。做不到时返回 False。"""
        ok = True
        N, m, T, x, head, stat, d = self.N, self.m, self.T, self.x, self.head, self.stat, self.d
        for j in range(N):
            s = stat[j]
            if s == BASIC or s == FIXED:
                continue
            dj = d[j]
            want = s
            if s == LOWER and dj < -DUAL_TOL:
                want = UPPER
            elif s == UPPER and dj > DUAL_TOL:
                want = LOWER
            elif s == FREE and abs(dj) > DUAL_TOL:
                ok = False
                continue
            if want == s:
                continue
            if (want == UPPER and not _isfinite(self.ub[j])) or (want == LOWER and not _isfinite(self.lb[j])):
                ok = False
                continue
            old = x[j]
            stat[j] = want
            x[j] = self._nonbasic_value(j)
            delta = x[j] - old
            for i in range(m):
                x[head[i]] -= T[i * N + j] * delta
        return ok

    # ------------------------------------------------------------ 原始单纯形

    def _primal(self, max_iters: int) -> int:
        degenerate = 0
        N, m = self.N, self.m
        dd = [0.0] * N
        row_cost = [0.0] * m
        while True:
            if self.iters >= max_iters:
                return ITERATION_LIMIT
            if self.pivots_since_refactor > max(200, 2 * m):
                self.load_basis(self.basis(), True)
            T, x, lb, ub, head, stat = self.T, self.x, self.lb, self.ub, self.head, self.stat

            # 第一阶段的成本：低于下界的基变量 -1，高于上界的 +1
            phase1 = False
            for i in range(m):
                v = head[i]
                row_cost[i] = 0.0
                if self._infeasibility(v) > 0.0:
                    row_cost[i] = -1.0 if x[v] < lb[v] else 1.0
                    phase1 = True
            if phase1:
                for j in range(N):
                    dd[j] = 0.0
                for i in range(m):
                    rc = row_cost[i]
                    if rc == 0.0:
                        continue
                    row = i * N
                    for j in range(N):
                        dd[j] -= rc * T[row + j]
            price = dd if phase1 else self.d

            # 定价：选进基变量
            bland = degenerate > BLAND_AFTER
            q, direction, best = -1, 0, 0.0
            for j in range(N):
                s = stat[j]
                if s == BASIC or s == FIXED:
                    continue
                dj = price[j]
                dj_dir = 0
                if (s == LOWER or s == FREE) and dj < -DUAL_TOL:
                    dj_dir = 1
                elif (s == UPPER or s == FREE) and dj > DUAL_TOL:
                    dj_dir = -1
                if dj_dir == 0:
                    continue
                if abs(dj) > best:
                    best = abs(dj)
                    q = j
                    direction = dj_dir
                    if bland:
                        break
            if q < 0:
                return INFEASIBLE if phase1 else OPTIMAL

            # 比值检验。alpha_i = x_q 每走一个单位，第 i 个基变量的变化量
            t_max = ub[q] - lb[q] if _isfinite(lb[q]) and _isfinite(ub[q]) else INF
            r = -1
            t_best, a_best, target = INF, 0.0, 0.0
            for i in range(m):
                alpha = -T[i * N + q] * direction
                if abs(alpha) < PIVOT_TOL:
                    continue
                v = head[i]
                xv = x[v]
                inf = self._infeasibility(v) if phase1 else 0.0
                if inf > 0.0 and xv < lb[v]:      # 在下界以下：碰到下界时停
                    if alpha <= 0:
                        continue
                    t = (lb[v] - xv) / alpha
                    tg = lb[v]
                elif inf > 0.0:                   # 在上界以上：碰到上界时停
                    if alpha >= 0:
                        continue
                    t = (ub[v] - xv) / alpha
                    tg = ub[v]
                elif alpha > 0:
                    if not _isfinite(ub[v]):
                        continue
                    t = (ub[v] - xv) / alpha
                    tg = ub[v]
                else:
                    if not _isfinite(lb[v]):
                        continue
                    t = (lb[v] - xv) / alpha
                    tg = lb[v]
                if t < 0:
                    t = 0.0
                take = r < 0 or t < t_best - 1e-12
                if not take and t <= t_best + 1e-12:
                    take = v < head[r] if bland else abs(alpha) > a_best
                if take:
                    r = i
                    t_best = t
                    a_best = abs(alpha)
                    target = tg
            if r < 0 and not _isfinite(t_max):
                return ITERATION_LIMIT if phase1 else UNBOUNDED  # 第一阶段不可能无界

            flip = t_max <= t_best
            t = t_max if flip else t_best
            if self.trace:
                line = (f"    第 {self.iters + 1} 步（{'原始单纯形·第一阶段' if phase1 else '原始单纯形·第二阶段'}）："
                        f"{self.names[q]} 进基（从{'上界' if stat[q] == UPPER else '0' if stat[q] == FREE else '下界'}"
                        f"{'增大' if direction > 0 else '减小'}，既约成本 {g(price[q], 4)}）")
                if flip:
                    print(line + f"，走到另一侧边界（bound flip），步长 {g(t, 4)}")
                else:
                    print(line + f"，{self.names[head[r]]} 离基停在{'下界' if target == lb[head[r]] else '上界'} "
                          f"{g(target, 4)}，步长 {g(t, 4)}")
            if t != 0.0:
                x[q] += direction * t
                for i in range(m):
                    a = T[i * N + q]
                    if a != 0.0:
                        x[head[i]] -= a * direction * t
            self.iters += 1
            degenerate = degenerate + 1 if t <= 1e-12 else 0
            if flip:
                stat[q] = UPPER if direction > 0 else LOWER
                x[q] = self._nonbasic_value(q)
                continue
            leave = head[r]
            x[leave] = target
            stat[leave] = FIXED if lb[leave] == ub[leave] else (LOWER if target == lb[leave] else UPPER)
            self._pivot(r, q)
            stat[q] = BASIC

    # ------------------------------------------------------------ 对偶单纯形

    def _dual(self, max_iters: int, cutoff: float) -> int:
        degenerate = 0
        N, m = self.N, self.m
        while True:
            if self.iters >= max_iters:
                return ITERATION_LIMIT
            if self.pivots_since_refactor > max(200, 2 * m):
                self.load_basis(self.basis(), True)
                if not self._make_dual_feasible():
                    return self._primal(max_iters)
            if _isfinite(cutoff) and self.objective() >= cutoff:
                return CUTOFF
            T, x, lb, ub, head, stat, d = self.T, self.x, self.lb, self.ub, self.head, self.stat, self.d

            # 离基行：越界最多的基变量
            bland = degenerate > BLAND_AFTER
            r = -1
            worst = 0.0
            for i in range(m):
                inf = self._infeasibility(head[i])
                if inf <= 0.0:
                    continue
                if (r < 0 or head[i] < head[r]) if bland else inf > worst:
                    worst = inf
                    r = i
            if r < 0:
                return OPTIMAL

            v = head[r]
            below = x[v] < lb[v]
            target = lb[v] if below else ub[v]

            # 进基列：保持既约成本对偶可行（min |d_j / a_rj|）
            q = -1
            best_ratio, best_a = INF, 0.0
            pr = r * N
            for j in range(N):
                s = stat[j]
                if s == BASIC or s == FIXED:
                    continue
                a = T[pr + j]
                if abs(a) < PIVOT_TOL:
                    continue
                # x_j 每增加 1，x_v 变化 -a
                dir_needed = (1 if a < 0 else -1) if below else (1 if a > 0 else -1)
                if dir_needed > 0 and s == UPPER:
                    continue
                if dir_needed < 0 and s == LOWER:
                    continue
                ratio = abs(d[j]) / abs(a)
                take = q < 0 or ratio < best_ratio - 1e-12
                if not take and ratio <= best_ratio + 1e-12:
                    take = j < q if bland else abs(a) > best_a
                if take:
                    q = j
                    best_ratio = ratio
                    best_a = abs(a)
            if q < 0:
                return INFEASIBLE

            if self.trace:
                print(f"    第 {self.iters + 1} 步（对偶单纯形）：{self.names[v]} = {g(x[v], 4)} 越过"
                      f"{'下界' if below else '上界'} {g(target, 4)}，离基；{self.names[q]} 进基（比值 {g(best_ratio, 4)}）")
            delta = (x[v] - target) / T[pr + q]
            x[q] += delta
            for i in range(m):
                a = T[i * N + q]
                if a != 0.0:
                    x[head[i]] -= a * delta
            x[v] = target
            stat[v] = FIXED if lb[v] == ub[v] else (LOWER if below else UPPER)
            self._pivot(r, q)
            stat[q] = BASIC
            self.iters += 1
            degenerate = degenerate + 1 if best_ratio <= 1e-12 else 0

    # ------------------------------------------------------------ 求解

    def solve(self, max_iters: int, cutoff: float = INF) -> int:
        """最小化 obj_sign * 目标。（对偶）目标值达到 cutoff 时提前以 CUTOFF 结束。"""
        limit = self.iters + max_iters
        n, m, N = self.n, self.m, self.N
        lb, ub, stat, x = self.lb, self.ub, self.stat, self.x
        # 结构变量的界可能整体变了：刷新非基变量的状态
        for j in range(n):
            if stat[j] == BASIC:
                continue
            s = stat[j]
            ns = self._default_status(j) if (not self._valid_status(s, j) or lb[j] == ub[j]) else s
            if ns != s or x[j] != self._value_for(ns, j):
                self.values_dirty = True
            stat[j] = ns
        for j in range(n):
            if lb[j] > ub[j] + 1e-9:
                return INFEASIBLE
        if self.values_dirty:
            self._recompute_values()

        for rnd in range(4):
            dual_ok = self._make_dual_feasible()
            if self.trace:
                print(f"  [LP] 当前基{'对偶可行' if dual_ok else '不是对偶可行'} → 用{'对偶单纯形' if dual_ok else '原始单纯形'}")
            st = self._dual(limit, cutoff) if dual_ok else self._primal(limit)
            if self.trace:
                label = ["最优", "不可行", "无界", "达到迭代上限", "被截断（不可能比已有整数解更好）"][st]
                if st in (OPTIMAL, CUTOFF):
                    label += f"，目标值 {g(self._real_objective(), 6)}"
                print(f"  [LP] 结果：{label}")
            if st != OPTIMAL:
                if st == INFEASIBLE and rnd < 3:
                    # 先用重新算过的数值确认一下，再宣布不可行
                    self._recompute_values()
                    self._recompute_reduced_costs()
                    again = self._dual(limit, INF) if self._make_dual_feasible() else self._primal(limit)
                    if again == INFEASIBLE:
                        return INFEASIBLE
                    continue
                return st
            # 用重新算出的数值确认最优（每隔一段时间也重算既约成本）
            refresh_d = self.pivots_since_refactor > 50
            if self.pivots_since_recompute > 0:
                self._recompute_values()
            if refresh_d:
                self._recompute_reduced_costs()
            x, d, stat, A, head = self.x, self.d, self.stat, self.A, self.head
            clean = True
            for i in range(m):
                if self._infeasibility(head[i]) != 0.0:
                    clean = False
                    break
            # 防止 T 里的舍入误差：松弛变量的值必须和原始的行一致
            if clean:
                for i in range(m):
                    act = 0.0
                    row = i * n
                    for k in range(n):
                        if A[row + k] != 0.0:
                            act += A[row + k] * x[k]
                    if abs(act - x[n + i]) > 1e-9 * (1.0 + abs(act)):
                        clean = False
                        break
            if clean:
                for j in range(N):
                    s = stat[j]
                    if s == BASIC or s == FIXED:
                        continue
                    if (s == LOWER or s == FREE) and d[j] < -1e-7:
                        clean = False
                        break
                    if (s == UPPER or s == FREE) and d[j] > 1e-7:
                        clean = False
                        break
            if clean:
                if _isfinite(cutoff) and self.objective() >= cutoff:
                    return CUTOFF
                return OPTIMAL
            self.load_basis(self.basis(), True)  # 数值有问题：重建单纯形表再继续
        return ITERATION_LIMIT

    # ------------------------------------------------------------ Gomory 割

    def gomory_cuts(self, is_int_col: List[bool], max_cuts: int) -> List[Constraint]:
        """从当前最优单纯形表读出 Gomory 混合整数割（推导见 src/simplex.cpp）。

        返回最多 max_cuts 条 sum(coefs) >= rhs 形式的割，按“效力”排序，并过滤掉几乎平行的和数值跨度太大的。
        """
        n, m, N, A, T, x, lb, ub, stat, head = (self.n, self.m, self.N, self.A, self.T, self.x, self.lb, self.ub,
                                                self.stat, self.head)
        is_int = [False] * N
        for j in range(n):
            is_int[j] = is_int_col[j]
        for i in range(m):
            ok = True
            for j in range(n):
                a = A[i * n + j]
                if a != 0.0 and (not is_int_col[j] or not _is_integral(a)):
                    ok = False
                    break
            is_int[n + i] = ok

        cands = []  # (pi, rhs, eff)
        for r in range(m):
            v = head[r]
            if not is_int[v]:
                continue
            b = x[v]
            f0 = b - jmath.floor(b)
            if f0 < 0.01 or f0 > 0.99:
                continue  # 几乎是整数：数值上不安全

            pi = [0.0] * n  # 结构变量空间里的割：pi x >= rhs
            rhs = 1.0
            ok = True
            for j in range(N):
                s = stat[j]
                if s == BASIC or s == FIXED:
                    continue
                t = T[r * N + j]
                if abs(t) < 1e-11:
                    continue
                if s == FREE:
                    ok = False
                    break
                at_lower = s == LOWER
                a = t if at_lower else -t
                bnd = lb[j] if at_lower else ub[j]
                if is_int[j] and _is_integral(bnd):
                    fj = a - jmath.floor(a)
                    gj = fj / f0 if fj <= f0 else (1.0 - fj) / (1.0 - f0)
                else:
                    gj = a / f0 if a >= 0 else -a / (1.0 - f0)
                if gj == 0.0:
                    continue
                # g * y_j，其中 y_j = x_j - l_j 或 u_j - x_j
                coef = gj if at_lower else -gj
                rhs += gj * bnd if at_lower else -gj * bnd
                if j < n:
                    pi[j] += coef
                else:  # 松弛变量：s_i = a_i x
                    i = j - n
                    for k in range(n):
                        aik = A[i * n + k]
                        if aik != 0.0:
                            pi[k] += coef * aik
            if not ok:
                continue

            # 清理：去掉很小的系数（安全地放松右边），检查数值跨度
            max_abs = 0.0
            for p in pi:
                max_abs = max(max_abs, abs(p))
            if max_abs < 1e-9:
                continue
            min_abs = INF
            for k in range(n):
                p = pi[k]
                if p == 0.0:
                    continue
                if abs(p) < 1e-9 * max_abs:
                    hi = ub[k] if p > 0 else lb[k]  # 从 ">=" 割里去掉 p x_k
                    if not _isfinite(hi):
                        ok = False
                        break
                    rhs -= p * hi
                    pi[k] = 0.0
                    continue
                min_abs = min(min_abs, abs(p))
            if not ok or max_abs / min_abs > 1e6:
                continue

            act = norm2 = 0.0
            for k in range(n):
                act += pi[k] * x[k]
                norm2 += pi[k] * pi[k]
            viol = rhs - act
            eff = viol / math.sqrt(norm2)
            if viol <= 1e-6 * (1.0 + abs(rhs)) or eff < 1e-5:
                continue
            cands.append((pi, rhs, eff))

        cands.sort(key=lambda cd: -cd[2])  # 稳定排序：效力相同的保持原来的顺序
        out: List[Constraint] = []
        kept = []
        for pi, rhs, eff in cands:
            if len(out) >= max_cuts:
                break
            parallel = False
            for kp in kept:
                dot = na = nb = 0.0
                for j in range(n):
                    dot += pi[j] * kp[j]
                    na += pi[j] * pi[j]
                    nb += kp[j] * kp[j]
                if dot / math.sqrt(na * nb) > 0.98:
                    parallel = True
                    break
            if parallel:
                continue
            kept.append(pi)
            con = Constraint()
            for j in range(n):
                if pi[j] != 0.0:
                    con.coefs[j] = pi[j]
            con.sense = Sense.GE
            con.rhs = rhs
            out.append(con)
        return out


def _is_integral(v: float) -> bool:
    return _isfinite(v) and abs(v - jmath.rint(v)) < 1e-9


class LPResult:
    __slots__ = ("status", "objective", "x", "iterations")

    def __init__(self) -> None:
        self.status = INFEASIBLE
        self.objective = 0.0  # obj_sign * (c'x + c0)
        self.x: List[float] = []
        self.iterations = 0


def lp_min(M: Model, l: List[float], u: List[float], obj_sign: float, max_iters: int) -> LPResult:
    """用给定的上下界从头解一个线性规划（不管整数要求）。"""
    E = LPEngine(M, obj_sign)
    E.set_all_col_bounds(l, u)
    res = LPResult()
    res.status = E.solve(max_iters)
    res.iterations = E.iterations()
    if res.status == OPTIMAL:
        res.x = E.col_values()
        res.objective = E.objective()
    return res
