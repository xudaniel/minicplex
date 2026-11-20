"""读取 CPLEX LP 文件格式（常用的一部分）。

支持的段：Minimize/Maximize、Subject To、Bounds、General(s)/Integer(s)、Binary/Binaries、End。
注释以 '\\' 开头。逐行移植自 Java 版 LpReader.java。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .model import INF, Constraint, LinExpr, Model, ObjSense, Sense, VarType, _merge

_ID_EXTRA = set("_.!\"#$%&()/,;?@`'{}|~")
_JAVA_WS = set(" \t\n\x0b\x0c\r\x1c\x1d\x1e\x1f")


class LpParseError(ValueError):
    """LP 文件格式错误。"""


def read_string(text: str) -> Model:
    return _Parser(_tokenize(text)).parse()


def read_file(path: str) -> Model:
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        raise LpParseError(f"cannot open file: {path}") from None
    return read_string(text)


# ------------------------------------------------------------ 词法

NUM, ID, OP, END = "NUM", "ID", "OP", "END"


@dataclass
class _Tok:
    kind: str = END
    s: str = ""
    num: float = 0.0
    line: int = 0
    line_start: bool = False


def _is_ws(c: str) -> bool:
    # 和 Java 的 Character.isWhitespace 一致（不把不换行空格当空白）
    return c in _JAVA_WS or (ord(c) > 127 and c.isspace() and c not in "\xa0  ")


def _is_id_char(c: str) -> bool:
    return c.isalnum() or c in _ID_EXTRA or ord(c) > 127


def _is_digit(s: str, k: int) -> bool:
    return k < len(s) and "0" <= s[k] <= "9"


def _tokenize(src: str) -> List[_Tok]:
    out: List[_Tok] = []
    line, ls, i, n = 1, True, 0, len(src)
    while i < n:
        c = src[i]
        if c == "\n":
            line += 1
            ls = True
            i += 1
            continue
        if _is_ws(c):
            i += 1
            continue
        if c == "\\":
            while i < n and src[i] != "\n":
                i += 1
            continue
        t = _Tok(line=line, line_start=ls)
        ls = False
        if _is_digit(src, i) or (c == "." and _is_digit(src, i + 1)):
            j = i
            while _is_digit(src, j):
                j += 1
            if j < n and src[j] == ".":
                j += 1
                while _is_digit(src, j):
                    j += 1
            if j < n and src[j] in "eE":
                k = j + 1
                if k < n and src[k] in "+-":
                    k += 1
                if _is_digit(src, k):
                    j = k
                    while _is_digit(src, j):
                        j += 1
            t.kind, t.s = NUM, src[i:j]
            t.num = float(t.s)
            i = j
        elif c in "<>=":
            op = c
            if i + 1 < n and src[i + 1] in "<>=":
                i += 1
                op += src[i]
            i += 1
            t.kind = OP
            t.s = "<=" if "<" in op else ">=" if ">" in op else "="
        elif c in "+-:":
            t.kind, t.s = OP, c
            i += 1
        elif _is_id_char(c):
            j = i
            while j < n and _is_id_char(src[j]):
                j += 1
            t.kind, t.s = ID, src[i:j]
            i = j
        else:
            raise LpParseError(f"LP parse error (line {line}): unexpected character '{c}'")
        out.append(t)
    out.append(_Tok(line=line))
    return out


# ------------------------------------------------------------ 语法

OBJ, CONS, BNDS, GEN, BIN, FIN = range(6)


class _Parser:
    def __init__(self, toks: List[_Tok]) -> None:
        self.t = toks
        self.p = 0
        self.M = Model()
        self.kw_sec = OBJ
        self.kw_len = 1
        self.kw_max = False

    def parse(self) -> Model:
        if not self.keyword() or self.kw_sec != OBJ:
            self.fail("file must start with Minimize or Maximize")
        while self.peek().kind != END:
            if not self.keyword():
                self.fail(f"unexpected token '{self.peek().s}'")
            self.p += self.kw_len
            sec = self.kw_sec
            if sec == OBJ:
                self.M.obj_sense = ObjSense.MAXIMIZE if self.kw_max else ObjSense.MINIMIZE
                self.parse_objective()
            elif sec == CONS:
                self.parse_constraints()
            elif sec == BNDS:
                self.parse_bounds()
            elif sec == GEN:
                self.parse_names(False)
            elif sec == BIN:
                self.parse_names(True)
            else:
                return self.M
        return self.M

    def peek(self, k: int = 0) -> _Tok:
        return self.t[min(self.p + k, len(self.t) - 1)]

    def fail(self, msg: str) -> "NoReturn":  # type: ignore[name-defined]  # noqa: F821
        raise LpParseError(f"LP parse error (line {self.peek().line}): {msg}")

    def keyword(self) -> bool:
        """当前记号是不是段名（必须在行首）？顺便设置 kw_sec / kw_len / kw_max。"""
        a = self.peek()
        if a.kind != ID or not a.line_start:
            return False
        w = a.s.lower()
        self.kw_len, self.kw_max = 1, False
        if w in ("maximize", "maximise", "maximum", "max"):
            self.kw_sec, self.kw_max = OBJ, True
            return True
        if w in ("minimize", "minimise", "minimum", "min"):
            self.kw_sec = OBJ
            return True
        if w in ("subject", "such") and self.peek(1).kind == ID:
            w2 = self.peek(1).s.lower()
            if (w == "subject" and w2 == "to") or (w == "such" and w2 == "that"):
                self.kw_sec, self.kw_len = CONS, 2
                return True
        table = {"st": CONS, "s.t.": CONS, "st.": CONS, "bounds": BNDS, "bound": BNDS,
                 "general": GEN, "generals": GEN, "gen": GEN, "integer": GEN, "integers": GEN,
                 "binary": BIN, "binaries": BIN, "bin": BIN, "end": FIN}
        if w in table:
            self.kw_sec = table[w]
            return True
        if w in ("semi", "semis", "sos"):
            self.fail(f"section '{a.s}' is not supported by minicplex")
        return False

    def at_stop(self) -> bool:
        if self.peek().kind == END:
            return True
        saved = (self.kw_sec, self.kw_len, self.kw_max)
        k = self.keyword()
        self.kw_sec, self.kw_len, self.kw_max = saved
        return k

    def is_op(self, op: str, k: int = 0) -> bool:
        return self.peek(k).kind == OP and self.peek(k).s == op

    def is_sense(self) -> bool:
        return self.is_op("<=") or self.is_op(">=") or self.is_op("=")

    def is_label(self) -> bool:
        return self.peek().kind == ID and self.is_op(":", 1)

    @staticmethod
    def is_inf_word(s: str) -> bool:
        return s.lower() in ("inf", "infinity")

    def var(self, name: str) -> int:
        j = self.M.find_var(name)
        return j if j >= 0 else self.M.add_var(0.0, INF, VarType.CONTINUOUS, name).id

    def parse_expr(self) -> LinExpr:
        e = LinExpr()
        while not self.at_stop() and not self.is_sense() and not self.is_label():
            sign, any_sign = 1.0, False
            while self.is_op("+") or self.is_op("-"):
                if self.is_op("-"):
                    sign = -sign
                self.p += 1
                any_sign = True
            coef, has_num = 1.0, False
            if self.peek().kind == NUM:
                coef = self.peek().num
                self.p += 1
                has_num = True
            if self.peek().kind == ID and not self.at_stop() and not self.is_label():
                _merge(e.terms, self.var(self.peek().s), sign * coef)
                self.p += 1
            elif has_num:
                e.constant += sign * coef
            elif any_sign:
                self.fail("dangling sign")
            else:
                self.fail(f"unexpected token '{self.peek().s}'")
        return e

    def parse_value(self) -> float:
        sign = 1.0
        while self.is_op("+") or self.is_op("-"):
            if self.is_op("-"):
                sign = -sign
            self.p += 1
        if self.peek().kind == NUM:
            v = self.peek().num
            self.p += 1
            return sign * v
        if self.peek().kind == ID and self.is_inf_word(self.peek().s):
            self.p += 1
            return sign * INF
        self.fail("expected a number")

    def parse_sense(self) -> Sense:
        if not self.is_sense():
            self.fail("expected <=, >= or =")
        s = Sense.LE if self.is_op("<=") else Sense.GE if self.is_op(">=") else Sense.EQ
        self.p += 1
        return s

    def parse_objective(self) -> None:
        if self.is_label():
            self.M.obj_name = self.peek().s
            self.p += 2
        self.M.objective = self.parse_expr()
        if not self.at_stop():
            self.fail(f"unexpected token '{self.peek().s}' in objective")

    def parse_constraints(self) -> None:
        while not self.at_stop():
            name = ""
            if self.is_label():
                name = self.peek().s
                self.p += 2
            lhs = self.parse_expr()
            s = self.parse_sense()
            rhs = self.parse_value()
            self.M.add_constr(Constraint.make(lhs, s, LinExpr.const(rhs)), name)

    def set_bound(self, j: int, s: Sense, v: float) -> None:
        vi = self.M.vars[j]
        if s == Sense.LE:
            vi.ub = v
        elif s == Sense.GE:
            vi.lb = v
        else:
            vi.lb = vi.ub = v

    def parse_bounds(self) -> None:
        while not self.at_stop():
            a = self.peek()
            value_first = a.kind == NUM or self.is_op("+") or self.is_op("-") or (a.kind == ID and self.is_inf_word(a.s))
            if value_first:  # v <= x [<= w]
                v = self.parse_value()
                s = self.parse_sense()
                if self.peek().kind != ID:
                    self.fail("expected a variable name")
                j = self.var(self.peek().s)
                self.p += 1
                # “v <= x” 的意思是 x >= v，反过来也一样
                self.set_bound(j, Sense.GE if s == Sense.LE else Sense.LE if s == Sense.GE else Sense.EQ, v)
                if self.is_sense():
                    s2 = self.parse_sense()
                    self.set_bound(j, s2, self.parse_value())
            elif a.kind == ID:  # x free | x <= v | x >= v | x = v
                j = self.var(a.s)
                self.p += 1
                if self.peek().kind == ID and self.peek().s.lower() == "free":
                    self.p += 1
                    self.M.vars[j].lb = -INF
                    self.M.vars[j].ub = INF
                else:
                    s = self.parse_sense()
                    self.set_bound(j, s, self.parse_value())
            else:
                self.fail(f"unexpected token '{a.s}' in Bounds")

    def parse_names(self, binary: bool) -> None:
        while not self.at_stop():
            if self.peek().kind != ID:
                self.fail("expected a variable name")
            v = self.M.vars[self.var(self.peek().s)]
            self.p += 1
            if binary:
                v.type, v.lb, v.ub = VarType.BINARY, 0.0, 1.0
            else:
                v.type = VarType.INTEGER
