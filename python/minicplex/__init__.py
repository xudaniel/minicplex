"""minicplex：从零写的迷你 LP / MIP 求解器（纯 Python 版，零依赖）。

和 C++、Java 版是同一个算法，逐行移植，在同一个模型上走完全相同的计算路径::

    from minicplex import Model, VarType, ObjSense, solve

    m = Model()
    x = m.add_var(0, 10, VarType.INTEGER, "x")
    y = m.add_var(name="y")
    m.add_constr(2 * x + 3 * y <= 12, "budget")
    m.set_objective(x + y, ObjSense.MAXIMIZE)
    r = solve(m)
    print(r.status, r.objective, r.value(x))
"""
from .fmt import g, use_utf8_output
from .lp_reader import LpParseError, read_file, read_string
from .model import INF, Constraint, LinExpr, Model, ObjSense, Sense, Var, VarInfo, VarType
from .solver import Branching, Params, Result, Status, check_feasible, eval_objective, solve

__version__ = "1.0"

__all__ = [
    "INF", "Branching", "Constraint", "LinExpr", "LpParseError", "Model", "ObjSense", "Params", "Result",
    "Sense", "Status", "Var", "VarInfo", "VarType", "check_feasible", "eval_objective", "g", "read_file",
    "read_string", "solve", "use_utf8_output",
]
