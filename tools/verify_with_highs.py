"""用 scipy 自带的 HiGHS 求解器独立验算 minicplex 导出的 .lp 文件。

用法：python3 tools/verify_with_highs.py model.lp [more.lp ...]
也可以作为模块：from verify_with_highs import solve_with_highs

只支持 minicplex 自己写出的 LP 格式（Model::writeLP）。需要 numpy + scipy。
"""
import re
import sys

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

_NUM = r'(?:\d+\.?\d*(?:e[+-]?\d+)?|\.\d+(?:e[+-]?\d+)?)'
_TERM = re.compile(r'([+-])\s*(' + _NUM + r')?\s*([A-Za-z_][\w.]*)?')


def _num(s):
    s = s.lower()
    return {'inf': np.inf, '+inf': np.inf, '-inf': -np.inf}.get(s) if 'inf' in s else float(s)


def read_lp(path):
    """解析 LP 文件，返回 (c, const, sense, A, lo, hi, lb, ub, integrality, names)。"""
    text = open(path).read()
    sec, obj, cons, cur = None, '', [], ''
    bounds, gen, binv, sense = [], [], [], 1
    for raw in text.splitlines():
        s = raw.split('\\')[0].strip()
        low = s.lower()
        if low in ('minimize', 'maximize'):
            sec, sense = 'obj', (-1 if low == 'maximize' else 1)
            continue
        if low in ('subject to', 'bounds', 'general', 'binary', 'end'):
            sec = low
            if low == 'end':
                break
            continue
        if not s:
            continue
        if sec == 'obj':
            obj += ' ' + s
        elif sec == 'subject to':
            cur += ' ' + s
            if re.search(r'(<=|>=|=)\s*-?' + _NUM + r'\s*$', cur):
                cons.append(cur)
                cur = ''
        elif sec == 'bounds':
            bounds.append(s.split())
        elif sec == 'general':
            gen += s.split()
        elif sec == 'binary':
            binv += s.split()

    names = {}

    def terms(expr):
        out, const = {}, 0.0
        expr = expr.strip()
        if expr and expr[0] not in '+-':
            expr = '+ ' + expr
        for sign, coef, var in _TERM.findall(expr):
            if not coef and not var:
                continue
            c = float(coef) if coef else 1.0
            c = -c if sign == '-' else c
            if var:
                names.setdefault(var, len(names))
                out[var] = out.get(var, 0.0) + c
            else:
                const += c
        return out, const

    o, oc = terms(obj.split(':', 1)[1])
    rows = []
    for c in cons:
        body = c.split(':', 1)[1]
        m = re.match(r'(.*?)(<=|>=|=)\s*(-?' + _NUM + r')\s*$', body)
        t, _ = terms(m.group(1))
        rows.append((t, m.group(2), float(m.group(3))))
    for p in bounds:
        for tok in p:
            if re.match(r'^[A-Za-z_]', tok) and tok.lower() not in ('free', 'inf', 'infinity'):
                names.setdefault(tok, len(names))
    for v in gen + binv:
        names.setdefault(v, len(names))

    n = len(names)
    lb, ub = np.zeros(n), np.full(n, np.inf)
    for p in bounds:
        if len(p) == 5:
            lb[names[p[2]]], ub[names[p[2]]] = _num(p[0]), _num(p[4])
        elif p[1].lower() == 'free':
            lb[names[p[0]]], ub[names[p[0]]] = -np.inf, np.inf
        elif p[1] == '=':
            lb[names[p[0]]] = ub[names[p[0]]] = _num(p[2])
        elif p[1] == '>=':
            lb[names[p[0]]] = _num(p[2])
        elif p[1] == '<=':
            ub[names[p[0]]] = _num(p[2])
    for v in binv:
        lb[names[v]], ub[names[v]] = 0, 1

    c = np.zeros(n)
    for v, k in o.items():
        c[names[v]] = k
    A = np.zeros((len(rows), n))
    lo, hi = np.full(len(rows), -np.inf), np.full(len(rows), np.inf)
    for i, (t, s, r) in enumerate(rows):
        for v, k in t.items():
            A[i, names[v]] = k
        if s in ('<=', '='):
            hi[i] = r
        if s in ('>=', '='):
            lo[i] = r
    integ = np.zeros(n)
    for v in gen + binv:
        integ[names[v]] = 1
    return c, oc, sense, A, lo, hi, lb, ub, integ, names


def solve_with_highs(path, gap=1e-9, relax=False, presolve=True):
    """返回 (状态, 目标值)。

    状态为 Optimal / Infeasible / Unbounded / InfeasibleOrUnbounded / Other。
    relax=True 时忽略整数约束，只求 LP 松弛；presolve=False 时关闭 HiGHS 的预处理。
    """
    c, oc, sense, A, lo, hi, lb, ub, integ, _ = read_lp(path)
    if relax:
        integ = np.zeros_like(integ)
    cons = [LinearConstraint(A, lo, hi)] if A.shape[0] else []
    res = milp(sense * c, constraints=cons, bounds=Bounds(lb, ub), integrality=integ,
               options={'mip_rel_gap': gap, 'presolve': presolve})
    if res.status == 0:
        return 'Optimal', sense * res.fun + oc
    msg = (res.message or '').lower()
    if 'infeasible' in msg and 'unbounded' in msg:
        return 'InfeasibleOrUnbounded', None
    if res.status == 2 or 'infeasible' in msg:
        return 'Infeasible', None
    if res.status == 3 or 'unbounded' in msg:
        return 'Unbounded', None
    return 'Other', None


if __name__ == '__main__':
    for p in sys.argv[1:]:
        st, val = solve_with_highs(p)
        print(f'{p}: HiGHS {st}' + (f', objective = {val:.10g}' if val is not None else ''))
