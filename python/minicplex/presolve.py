"""混合整数规划的预处理：界传播、系数收紧、删掉多余的行。

变量永远不删，所以预处理后模型的解直接就是原模型的解。逐行移植自 Java 版 Presolve.java。
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List

from . import jmath
from .model import INF, Constraint, Model, Sense


@dataclass
class Stats:
    bounds_tightened: int = 0
    coefs_tightened: int = 0
    rows_removed: int = 0


class _Activity:
    __slots__ = ("fin", "inf")

    def __init__(self) -> None:
        self.fin = 0.0  # 有限的部分
        self.inf = 0    # 无穷大项的个数

    def as_min(self) -> float:
        return -INF if self.inf > 0 else self.fin

    def as_max(self) -> float:
        return INF if self.inf > 0 else self.fin


def _finite(v: float) -> bool:
    return math.isfinite(v)


def _min_activity(row: Dict[int, float], lb: List[float], ub: List[float]) -> _Activity:
    a = _Activity()
    for k, c in row.items():
        t = c * lb[k] if c > 0 else c * ub[k]
        if _finite(t):
            a.fin += t
        else:
            a.inf += 1
    return a


def _max_activity(row: Dict[int, float], lb: List[float], ub: List[float]) -> _Activity:
    a = _Activity()
    for k, c in row.items():
        t = c * ub[k] if c > 0 else c * lb[k]
        if _finite(t):
            a.fin += t
        else:
            a.inf += 1
    return a


def _rest(a: _Activity, term: float) -> float:
    """去掉自己那一项之后，这一行其余部分的活动量。"""
    if not _finite(term):
        return a.fin if a.inf == 1 else math.nan
    return a.fin - term if a.inf == 0 else math.nan


def run(W: Model, lb: List[float], ub: List[float], is_int: List[bool], st: Stats) -> bool:
    """证明不可行时返回 False。会修改 W.constraints、lb 和 ub。"""
    feas_tol = 1e-6
    for _ in range(20):
        changed = False
        kept: List[Constraint] = []
        for c in W.constraints:
            if not c.coefs:
                ok = ((c.sense == Sense.LE and 0 <= c.rhs + feas_tol)
                      or (c.sense == Sense.GE and 0 >= c.rhs - feas_tol)
                      or (c.sense == Sense.EQ and abs(c.rhs) <= feas_tol))
                if not ok:
                    return False
                st.rows_removed += 1
                changed = True
                continue
            tol = feas_tol * (1.0 + abs(c.rhs))
            mn, mx = _min_activity(c.coefs, lb, ub), _max_activity(c.coefs, lb, ub)
            le, ge = c.sense != Sense.GE, c.sense != Sense.LE
            if le and mn.as_min() > c.rhs + tol:
                return False
            if ge and mx.as_max() < c.rhs - tol:
                return False
            # 多余的行？
            if c.sense == Sense.LE and mx.as_max() <= c.rhs + 1e-9:
                st.rows_removed += 1
                changed = True
                continue
            if c.sense == Sense.GE and mn.as_min() >= c.rhs - 1e-9:
                st.rows_removed += 1
                changed = True
                continue

            # 界传播
            for k, a in c.coefs.items():
                if abs(a) < 1e-9:
                    continue
                if le:
                    r = _rest(mn, a * lb[k] if a > 0 else a * ub[k])
                    if _finite(r):
                        v = (c.rhs - r) / a
                        changed |= _tighten_ub(k, v, lb, ub, is_int, st) if a > 0 else _tighten_lb(k, v, lb, ub, is_int, st)
                if ge:
                    r = _rest(mx, a * ub[k] if a > 0 else a * lb[k])
                    if _finite(r):
                        v = (c.rhs - r) / a
                        changed |= _tighten_lb(k, v, lb, ub, is_int, st) if a > 0 else _tighten_ub(k, v, lb, ub, is_int, st)
                if lb[k] > ub[k] + 1e-6:
                    return False
                mn = _min_activity(c.coefs, lb, ub)
                mx = _max_activity(c.coefs, lb, ub)

            # 0-1 变量的系数收紧（统一写成 s * row <= s * rhs）
            if c.sense != Sense.EQ:
                s = 1.0 if c.sense == Sense.LE else -1.0
                for k in list(c.coefs):
                    if not is_int[k] or lb[k] != 0.0 or ub[k] != 1.0:
                        continue
                    if s > 0:  # s*row 的最大值
                        U = _max_activity(c.coefs, lb, ub)
                    else:
                        U = _min_activity(c.coefs, lb, ub)
                        U.fin = -U.fin
                    if U.inf > 0:
                        break
                    ck, b = s * c.coefs[k], s * c.rhs
                    d = b - (U.fin - ck) if ck > 0 else b - (U.fin + ck)
                    if d <= 1e-6 * (1.0 + abs(b)):
                        continue
                    if ck > 0:
                        c.coefs[k] = s * (ck - d)
                        c.rhs = s * (b - d)
                    else:
                        c.coefs[k] = s * (ck + d)
                    st.coefs_tightened += 1
                    changed = True
            kept.append(c)
        W.constraints = kept
        if not changed:
            break
    return True


def _tighten_lb(k: int, v: float, lb: List[float], ub: List[float], is_int: List[bool], st: Stats) -> bool:
    if is_int[k]:
        v = jmath.ceil(v - 1e-6)
    else:
        v -= 1e-9 * (1.0 + abs(v))  # 离舍入误差远一点
    rng = ub[k] - lb[k] if _finite(ub[k]) and _finite(lb[k]) else INF
    if v > lb[k] + 1e-6 * (1.0 + abs(v)) and (is_int[k] or not _finite(lb[k]) or v - lb[k] > 1e-3 * max(1.0, rng)):
        lb[k] = v
        st.bounds_tightened += 1
        return True
    return False


def _tighten_ub(k: int, v: float, lb: List[float], ub: List[float], is_int: List[bool], st: Stats) -> bool:
    if is_int[k]:
        v = jmath.floor(v + 1e-6)
    else:
        v += 1e-9 * (1.0 + abs(v))
    rng = ub[k] - lb[k] if _finite(ub[k]) and _finite(lb[k]) else INF
    if v < ub[k] - 1e-6 * (1.0 + abs(v)) and (is_int[k] or not _finite(ub[k]) or ub[k] - v > 1e-3 * max(1.0, rng)):
        ub[k] = v
        st.bounds_tightened += 1
        return True
    return False
