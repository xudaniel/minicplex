"""用 Google OR-Tools 独立验算 minicplex 导出的 .lp 文件（第二个“标准答案”）。

纯线性规划交给 GLOP（Google 自己的修正单纯形 LP 求解器），含整数变量的交给 OR-Tools 自带的 SCIP。
LP 文件的解析沿用 verify_with_highs.read_lp，两边读到的是同一个模型。

用法：python3 tools/verify_with_ortools.py model.lp [more.lp ...]
也可以作为模块：from verify_with_ortools import solve_with_ortools
需要：pip install ortools numpy scipy
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify_with_highs import read_lp  # noqa: E402

from ortools.linear_solver import pywraplp  # noqa: E402

_STATUS = {
    pywraplp.Solver.OPTIMAL: 'Optimal',
    pywraplp.Solver.INFEASIBLE: 'Infeasible',
    pywraplp.Solver.UNBOUNDED: 'Unbounded',
}


def solve_with_ortools(path, gap=1e-9, relax=False, time_limit_s=10):
    """返回 (状态, 目标值, 求解器名, 单纯形迭代次数)。

    状态为 Optimal / Infeasible / Unbounded / InfeasibleOrUnbounded / Other，与 solve_with_highs 一致。
    relax=True 时忽略整数约束，只求 LP 松弛（一定交给 GLOP）。

    两个已知的坑（2026-11-19 对拍时发现）：
    1. GLOP 预处理只能判断“不可行或无界”时，MPSolver 会把它报成 INFEASIBLE
       （见 ortools/linear_solver/glop_utils.cc 的 GlopToMPSolverResultStatus）。
       所以 GLOP 报不可行时，关掉预处理再解一次，用第二次的结论。
    2. LP 松弛无界的整数规划，SCIP 可能一直搜下去不停。按 Meyer 定理（有理数据），
       这种题只能是“不可行或无界”，所以先用 GLOP 解松弛，无界就直接返回，不再调用 SCIP。
    """
    c, oc, sense, A, lo, hi, lb, ub, integ, _ = read_lp(path)
    is_mip = (not relax) and bool(integ.any())
    if is_mip:
        r_st, _, _, _ = solve_with_ortools(path, gap, relax=True, time_limit_s=time_limit_s)
        if r_st == 'Unbounded':
            return 'InfeasibleOrUnbounded', None, 'SCIP', 0
    st, val, name, it = _solve(c, oc, sense, A, lo, hi, lb, ub, integ, is_mip, gap, time_limit_s)
    if name == 'GLOP' and st == 'Infeasible':
        st2, val2, _, it2 = _solve(c, oc, sense, A, lo, hi, lb, ub, integ, False, gap, time_limit_s,
                                   presolve=False)
        if st2 != 'Infeasible':
            return st2, val2, 'GLOP(no presolve)', it2
    return st, val, name, it


def _solve(c, oc, sense, A, lo, hi, lb, ub, integ, is_mip, gap, time_limit_s, presolve=True):
    name = 'SCIP' if is_mip else 'GLOP'
    s = pywraplp.Solver.CreateSolver(name)
    s.SetTimeLimit(int(time_limit_s * 1000))
    inf = s.infinity()

    def fin(v):
        return v if math.isfinite(v) else (inf if v > 0 else -inf)

    x = []
    for j in range(len(c)):
        if is_mip and integ[j]:
            x.append(s.IntVar(fin(lb[j]), fin(ub[j]), f'x{j}'))
        else:
            x.append(s.NumVar(fin(lb[j]), fin(ub[j]), f'x{j}'))
    for i in range(A.shape[0]):
        ct = s.Constraint(fin(lo[i]), fin(hi[i]))
        for j in range(A.shape[1]):
            if A[i, j]:
                ct.SetCoefficient(x[j], float(A[i, j]))
    obj = s.Objective()
    for j in range(len(c)):
        if c[j]:
            obj.SetCoefficient(x[j], float(c[j]))
    obj.SetOffset(float(oc))
    if sense == -1:
        obj.SetMaximization()
    else:
        obj.SetMinimization()

    params = pywraplp.MPSolverParameters()
    if not presolve:
        params.SetIntegerParam(pywraplp.MPSolverParameters.PRESOLVE,
                               pywraplp.MPSolverParameters.PRESOLVE_OFF)
    if is_mip:
        params.SetDoubleParam(pywraplp.MPSolverParameters.RELATIVE_MIP_GAP, gap)
    st = s.Solve(params)
    status = _STATUS.get(st, 'Other')
    val = obj.Value() if status == 'Optimal' else None
    return status, val, name, s.iterations()


if __name__ == '__main__':
    for p in sys.argv[1:]:
        st, val, name, it = solve_with_ortools(p)
        msg = f'{p}: OR-Tools/{name} {st}'
        if val is not None:
            msg += f', objective = {val:.10g}'
        print(msg + f', iterations = {it}')
