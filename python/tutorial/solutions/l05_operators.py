"""第 5 课：运算符重载和不可变对象。

在 minicplex 里可以写 2 * x + 3 * y <= 12，因为 LinExpr 定义了 __add__、__mul__、__le__ 这些“魔法方法”。
这一课自己写一个迷你的线性表达式 Expr：支持 +、*、sum()，而且每次运算都返回新对象，不改原来的。
运行：python3 python/tutorial/run.py 05
"""
from check import lesson, eq, near, raises, that, done


class Expr:
    """sum(系数 × 变量) + 常数。terms 是 {变量名: 系数}。"""

    def __init__(self, terms=None, constant=0.0):
        self.terms = dict(terms) if terms else {}  # 复制一份：外面的字典以后再改也影响不到这里
        self.constant = constant

    @staticmethod
    def var(name):
        """一个变量：系数 1。"""
        return Expr({name: 1.0})

    def __add__(self, other):
        """self + other。other 可以是 Expr 或数字；别的类型返回 NotImplemented（Python 会接着报 TypeError）。
        一定要返回一个新的 Expr，不能改 self。"""
        # TODO 数字：常数相加；Expr：系数按变量名相加（新字典！），常数相加
        # >>>
        if isinstance(other, (int, float)):
            return Expr(self.terms, self.constant + other)
        if isinstance(other, Expr):
            terms = dict(self.terms)
            for name, coef in other.terms.items():
                terms[name] = terms.get(name, 0.0) + coef
            return Expr(terms, self.constant + other.constant)
        return NotImplemented
        # <<<

    def __radd__(self, other):
        """other + self，other 在左边时 Python 会来调用它。sum() 从 0 开始加，所以必须有它。"""
        # >>>
        return self.__add__(other)
        # <<<

    def __mul__(self, k):
        """self * 数字：每个系数和常数都乘 k。不是数字就返回 NotImplemented。"""
        # >>>
        if not isinstance(k, (int, float)):
            return NotImplemented
        return Expr({name: coef * k for name, coef in self.terms.items()}, self.constant * k)
        # <<<

    def __rmul__(self, k):
        """数字 * self（例如 2 * x）。"""
        # >>>
        return self.__mul__(k)
        # <<<

    def value(self, assignment):
        """代入变量的值算出结果。assignment 是 {变量名: 值}。"""
        # >>>
        return self.constant + sum(coef * assignment[name] for name, coef in self.terms.items())
        # <<<


x, y = Expr.var("x"), Expr.var("y")


def immutable():
    e = 2 * x
    f = e + 1
    g = e * 3
    return e.terms == {"x": 2.0} and e.constant == 0 and f.constant == 1 and g.terms == {"x": 6.0}


lesson("第 5 课：运算符重载和不可变对象")
near("2x + 3y + 1 在 x=1, y=2 时是 9", 9, lambda: (2 * x + 3 * y + 1).value({"x": 1, "y": 2}))
eq("x + x 合并成 2x", {"x": 2.0}, lambda: (x + x).terms)
eq("sum([x, y, x]) 能用（靠 __radd__）", {"x": 2.0, "y": 1.0}, lambda: sum([x, y, x]).terms)
eq("5 + x 的常数是 5", 5, lambda: (5 + x).constant)
that("运算不改原来的对象", immutable)
raises('x * "abc" 报 TypeError（因为返回了 NotImplemented）', TypeError, lambda: x * "abc")
raises('x + "abc" 也报 TypeError', TypeError, lambda: x + "abc")
done()
