"""模型：变量、线性表达式、约束和 Model 本身（对应 C++ 的 model.hpp / Java 的 Model.java）。

Python 有运算符重载，所以建模可以写得和数学式子一样::

    m = Model()
    x = m.add_var(0, INF, VarType.INTEGER, "x")
    y = m.add_var(name="y")
    m.add_constr(2 * x + 3 * y <= 12, "budget")
    m.set_objective(x + y, ObjSense.MAXIMIZE)

为了让 C++、Java、Python 三个版本算出一模一样的数字，每一次加减乘都按 Java 版的
同一顺序进行；系数字典里的变量总是按编号从小到大排列（相当于 Java 的 TreeMap）。
"""
from __future__ import annotations

import math
from enum import Enum
from typing import Dict, List, Optional, Union

from .fmt import g

INF = math.inf


class VarType(Enum):
    """变量类型。"""
    CONTINUOUS = "Continuous"
    INTEGER = "Integer"
    BINARY = "Binary"


class Sense(Enum):
    """约束方向：<=、>= 或 =。"""
    LE = "<="
    GE = ">="
    EQ = "="


class ObjSense(Enum):
    """优化方向。"""
    MINIMIZE = "Minimize"
    MAXIMIZE = "Maximize"


class Var:
    """模型里一个变量的“把手”：只记着它的编号 id。

    注意：``x == 3`` 得到的是一条约束，不是 True/False（和 C++ 版一样）。
    想比较两个把手是不是同一个变量，请比较 ``x.id == y.id``。
    """
    __slots__ = ("id",)

    def __init__(self, id: int) -> None:
        self.id = id

    def __repr__(self) -> str:
        return f"Var({self.id})"

    def __hash__(self) -> int:
        return hash(("Var", self.id))

    # 变量参与运算时，先变成表达式 1·x
    def _e(self) -> "LinExpr":
        return LinExpr.of(self)

    def __add__(self, o): return self._e() + o
    def __radd__(self, o): return self._e().__radd__(o)
    def __sub__(self, o): return self._e() - o
    def __rsub__(self, o): return self._e().__rsub__(o)
    def __mul__(self, s): return LinExpr.of(self, float(s)) if _is_num(s) else NotImplemented
    def __rmul__(self, s): return self.__mul__(s)
    def __truediv__(self, s): return LinExpr.of(self, 1.0 / s) if _is_num(s) else NotImplemented
    def __neg__(self): return LinExpr.of(self, -1.0)
    def __pos__(self): return self._e()
    def __le__(self, o): return self._e() <= o
    def __ge__(self, o): return self._e() >= o
    def __eq__(self, o):  # type: ignore[override]
        c = self._e() == o
        if isinstance(o, Var):  # 让 dict / in 这类按“相等”查找的写法也能用
            c._same = self.id == o.id
        return c


Operand = Union[float, int, Var, "LinExpr"]


def _is_num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _merge(terms: Dict[int, float], k: int, v: float) -> None:
    """Java 的 terms.merge(k, v, Double::sum)：已有就相加，没有就直接放进去。"""
    terms[k] = terms[k] + v if k in terms else v


class LinExpr:
    """线性表达式：sum(系数 × 变量) + 常数。

    每次运算都返回一个新的表达式，原来的表达式不会被修改。
    """
    __slots__ = ("terms", "constant")

    def __init__(self) -> None:
        self.terms: Dict[int, float] = {}
        self.constant: float = 0.0

    # ---------------------------------------------------- 构造
    @staticmethod
    def of(v: Var, coef: float = 1.0) -> "LinExpr":
        """coef · v"""
        return LinExpr().plus_var(v, coef)

    @staticmethod
    def const(c: float) -> "LinExpr":
        e = LinExpr()
        e.constant = float(c)
        return e

    @staticmethod
    def wrap(o: Operand) -> "LinExpr":
        """数字、变量或表达式 → 表达式。"""
        if isinstance(o, LinExpr):
            return o
        if isinstance(o, Var):
            return LinExpr.of(o)
        if _is_num(o):
            return LinExpr.const(o)
        raise TypeError(f"不能把 {type(o).__name__} 当成线性表达式")

    def copy(self) -> "LinExpr":
        e = LinExpr()
        e.terms = dict(self.terms)
        e.constant = self.constant
        return e

    # ---------------------------------------------------- 基本运算（和 Java 版一一对应）
    def plus_var(self, v: Var, coef: float = 1.0) -> "LinExpr":
        e = self.copy()
        _merge(e.terms, v.id, float(coef))
        return e

    def plus_const(self, c: float) -> "LinExpr":
        e = self.copy()
        e.constant += c
        return e

    def plus_expr(self, o: "LinExpr") -> "LinExpr":
        e = self.copy()
        for k in sorted(o.terms):
            _merge(e.terms, k, o.terms[k])
        e.constant += o.constant
        return e

    def times(self, s: float) -> "LinExpr":
        e = self.copy()
        for k in e.terms:
            e.terms[k] = e.terms[k] * s
        e.constant *= s
        return e

    # ---------------------------------------------------- 运算符
    def __add__(self, o):
        if isinstance(o, Var):
            return self.plus_var(o, 1.0)
        if isinstance(o, LinExpr):
            return self.plus_expr(o)
        if _is_num(o):
            return self.plus_const(float(o))
        return NotImplemented

    def __radd__(self, o):
        if _is_num(o):  # 让 sum([...]) 能用：0 + e
            return self.plus_const(float(o))
        return NotImplemented

    def __sub__(self, o):
        if isinstance(o, Var):
            return self.plus_var(o, -1.0)
        if isinstance(o, LinExpr):
            return self.plus_expr(o.times(-1.0))
        if _is_num(o):
            return self.plus_const(-float(o))
        return NotImplemented

    def __rsub__(self, o):
        if _is_num(o):
            return self.times(-1.0).plus_const(float(o))
        return NotImplemented

    def __mul__(self, s):
        return self.times(float(s)) if _is_num(s) else NotImplemented

    __rmul__ = __mul__

    def __truediv__(self, s):
        return self.times(1.0 / s) if _is_num(s) else NotImplemented

    def __neg__(self):
        return self.times(-1.0)

    def __pos__(self):
        return self

    def __le__(self, o): return Constraint.make(self, Sense.LE, LinExpr.wrap(o))
    def __ge__(self, o): return Constraint.make(self, Sense.GE, LinExpr.wrap(o))
    def __eq__(self, o): return Constraint.make(self, Sense.EQ, LinExpr.wrap(o))  # type: ignore[override]

    __hash__ = None  # type: ignore[assignment]

    def __repr__(self) -> str:
        parts = [f"{g(v)}*x{k}" for k, v in sorted(self.terms.items())]
        if self.constant or not parts:
            parts.append(g(self.constant))
        return "LinExpr(" + " + ".join(parts) + ")"


class Constraint:
    """一条线性约束：sum(coefs) (sense) rhs。coefs 是 {变量编号: 系数}，按编号排序。"""
    __slots__ = ("name", "coefs", "sense", "rhs", "_same")

    def __init__(self, coefs: Optional[Dict[int, float]] = None, sense: Sense = Sense.LE,
                 rhs: float = 0.0, name: str = "") -> None:
        self.name = name
        self.coefs: Dict[int, float] = dict(sorted(coefs.items())) if coefs else {}
        self.sense = sense
        self.rhs = float(rhs)
        self._same: Optional[bool] = None

    def copy(self) -> "Constraint":
        c = Constraint()
        c.name = self.name
        c.coefs = dict(self.coefs)
        c.sense = self.sense
        c.rhs = self.rhs
        return c

    @staticmethod
    def make(lhs: LinExpr, s: Sense, rhs: LinExpr) -> "Constraint":
        """全部移到左边：lhs - rhs (sense) 0，再把常数挪到右边。"""
        d = lhs.plus_expr(rhs.times(-1.0))
        c = Constraint()
        for k in sorted(d.terms):
            if d.terms[k] != 0.0:
                c.coefs[k] = d.terms[k]
        c.sense = s
        c.rhs = -d.constant
        return c

    def __bool__(self) -> bool:
        if self._same is not None:  # x == y 两边都是变量：在 if / dict 里表示“是不是同一个变量”
            return self._same
        raise TypeError("约束不能当成 True/False 用（比较两个变量是否相同，请比较 .id）")

    def __repr__(self) -> str:
        return f"Constraint({self.name!r}, {self.coefs}, {self.sense.value}, {g(self.rhs)})"


class VarInfo:
    """变量的名字、上下界和类型。"""
    __slots__ = ("name", "lb", "ub", "type")

    def __init__(self, name: str, lb: float, ub: float, type: VarType) -> None:
        self.name = name
        self.lb = lb
        self.ub = ub
        self.type = type

    def copy(self) -> "VarInfo":
        return VarInfo(self.name, self.lb, self.ub, self.type)

    def __repr__(self) -> str:
        return f"VarInfo({self.name!r}, {g(self.lb)}, {g(self.ub)}, {self.type.name})"


class Model:
    """一个线性规划 / 混合整数规划模型（相当于 CPLEX Concert 的 IloModel）。"""

    def __init__(self) -> None:
        self.vars: List[VarInfo] = []
        self.constraints: List[Constraint] = []
        self.objective: LinExpr = LinExpr()
        self.obj_sense: ObjSense = ObjSense.MINIMIZE
        self.obj_name: str = "obj"
        self._index: Dict[str, int] = {}

    def copy(self) -> "Model":
        """深拷贝。"""
        m = Model()
        m.vars = [v.copy() for v in self.vars]
        m.constraints = [c.copy() for c in self.constraints]
        m.objective = self.objective.plus_const(0.0)
        m.obj_sense = self.obj_sense
        m.obj_name = self.obj_name
        m._index = dict(self._index)
        return m

    def add_var(self, lb: float = 0.0, ub: float = INF, type: VarType = VarType.CONTINUOUS,
                name: str = "") -> Var:
        lb, ub = float(lb), float(ub)
        if type == VarType.BINARY:
            lb = max(lb, 0.0)
            ub = min(ub, 1.0)
        if not name:
            name = f"x{len(self.vars) + 1}"
        if name in self._index:
            raise ValueError(f"duplicate variable name: {name}")
        self._index[name] = len(self.vars)
        self.vars.append(VarInfo(name, lb, ub, type))
        return Var(len(self.vars) - 1)

    def add_constr(self, c: Constraint, name: str = "") -> int:
        if not isinstance(c, Constraint):
            raise TypeError("add_constr 需要一条约束，例如 2 * x + y <= 10")
        for k in c.coefs:
            if k < 0 or k >= self.num_vars:
                raise ValueError("constraint references unknown variable")
        c.coefs = dict(sorted(c.coefs.items()))
        if name:
            c.name = name
        if not c.name:
            c.name = f"c{len(self.constraints) + 1}"
        self.constraints.append(c)
        return len(self.constraints) - 1

    def set_objective(self, e: Operand, sense: ObjSense = ObjSense.MINIMIZE) -> None:
        self.objective = LinExpr.wrap(e)
        self.obj_sense = sense

    def find_var(self, name: str) -> int:
        return self._index.get(name, -1)

    def var(self, name: str) -> Var:
        j = self.find_var(name)
        if j < 0:
            raise KeyError(f"unknown variable: {name}")
        return Var(j)

    @property
    def num_vars(self) -> int:
        return len(self.vars)

    @property
    def num_constrs(self) -> int:
        return len(self.constraints)

    def is_integer(self, j: int) -> bool:
        return self.vars[j].type != VarType.CONTINUOUS

    @property
    def num_integers(self) -> int:
        return sum(1 for j in range(self.num_vars) if self.is_integer(j))

    # ---------------------------------------------------- LP 文件输出
    def _write_terms(self, out: List[str], terms: Dict[int, float], constant: float) -> None:
        k = 0
        for j in sorted(terms):
            v = terms[j]
            if v == 0.0:
                continue
            if k > 0 and k % 6 == 0:
                out.append("\n  ")
            out.append(" - " if v < 0 else " + ")
            a = abs(v)
            if a != 1.0:
                out.append(_num(a) + " ")
            out.append(self.vars[j].name)
            k += 1
        if constant != 0.0 or k == 0:
            out.append((" - " if constant < 0 else " + ") + _num(abs(constant)))

    def to_lp(self) -> str:
        """模型的 CPLEX LP 格式文本。"""
        out: List[str] = ["\\ Written by minicplex\n"]
        out.append("Maximize\n" if self.obj_sense == ObjSense.MAXIMIZE else "Minimize\n")
        out.append(f" {self.obj_name}:")
        self._write_terms(out, self.objective.terms, self.objective.constant)
        out.append("\nSubject To\n")
        for c in self.constraints:
            out.append(f" {c.name}:")
            self._write_terms(out, c.coefs, 0.0)
            out.append(f" {c.sense.value} {_num(c.rhs)}\n")
        out.append("Bounds\n")
        for v in self.vars:
            if _plain_binary(v) or (v.lb == 0.0 and v.ub == INF):
                continue
            if v.lb == -INF and v.ub == INF:
                out.append(f" {v.name} free\n")
            elif v.lb == v.ub:
                out.append(f" {v.name} = {_num(v.lb)}\n")
            elif v.ub == INF:
                out.append(f" {v.name} >= {_num(v.lb)}\n")
            else:
                out.append(f" {_num(v.lb)} <= {v.name} <= {_num(v.ub)}\n")
        general = [v for v in self.vars if v.type == VarType.INTEGER or (v.type == VarType.BINARY and not _plain_binary(v))]
        if general:
            out.append("General\n")
            out.extend(f" {v.name}\n" for v in general)
        binary = [v for v in self.vars if _plain_binary(v)]
        if binary:
            out.append("Binary\n")
            out.extend(f" {v.name}\n" for v in binary)
        out.append("End\n")
        return "".join(out)

    def write_lp(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_lp())


def _num(v: float) -> str:
    if v == INF:
        return "inf"
    if v == -INF:
        return "-inf"
    return g(v, 15)


def _plain_binary(v: VarInfo) -> bool:
    return v.type == VarType.BINARY and v.lb == 0.0 and v.ub == 1.0
