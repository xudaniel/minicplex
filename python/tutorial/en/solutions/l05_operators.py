"""Lesson 5: Operator overloading and immutable objects.

In minicplex you can write 2 * x + 3 * y <= 12 because LinExpr defines "magic methods" such as __add__, __mul__ and __le__.
In this lesson you write a mini linear expression Expr: it supports +, * and sum(), and every operation returns a new object
instead of changing the old one.
Run: python3 python/tutorial/en/run.py 05
"""
from check import lesson, eq, near, raises, that, done


class Expr:
    """sum(coefficient * variable) + constant. terms is {variable name: coefficient}."""

    def __init__(self, terms=None, constant=0.0):
        self.terms = dict(terms) if terms else {}  # copy it: later changes to the caller's dict cannot reach in here
        self.constant = constant

    @staticmethod
    def var(name):
        """One variable with coefficient 1."""
        return Expr({name: 1.0})

    def __add__(self, other):
        """self + other. other may be an Expr or a number; for anything else return NotImplemented (Python then raises TypeError).
        Always return a new Expr; never change self."""
        # TODO a number: add the constants; an Expr: add coefficients by name (in a new dict!) and add the constants
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
        """other + self: Python calls this when other is on the left. sum() starts from 0, so it needs this."""
        # >>>
        return self.__add__(other)
        # <<<

    def __mul__(self, k):
        """self * number: multiply every coefficient and the constant by k. Not a number? Return NotImplemented."""
        # >>>
        if not isinstance(k, (int, float)):
            return NotImplemented
        return Expr({name: coef * k for name, coef in self.terms.items()}, self.constant * k)
        # <<<

    def __rmul__(self, k):
        """number * self (for example 2 * x)."""
        # >>>
        return self.__mul__(k)
        # <<<

    def value(self, assignment):
        """Plug in values for the variables. assignment is {variable name: value}."""
        # >>>
        return self.constant + sum(coef * assignment[name] for name, coef in self.terms.items())
        # <<<


x, y = Expr.var("x"), Expr.var("y")


def immutable():
    e = 2 * x
    f = e + 1
    g = e * 3
    return e.terms == {"x": 2.0} and e.constant == 0 and f.constant == 1 and g.terms == {"x": 6.0}


lesson("Lesson 5: Operator overloading and immutable objects")
near("2x + 3y + 1 is 9 at x=1, y=2", 9, lambda: (2 * x + 3 * y + 1).value({"x": 1, "y": 2}))
eq("x + x merges into 2x", {"x": 2.0}, lambda: (x + x).terms)
eq("sum([x, y, x]) works (thanks to __radd__)", {"x": 2.0, "y": 1.0}, lambda: sum([x, y, x]).terms)
eq("the constant of 5 + x is 5", 5, lambda: (5 + x).constant)
that("operations do not change the original objects", immutable)
raises('x * "abc" raises TypeError (because NotImplemented was returned)', TypeError, lambda: x * "abc")
raises('x + "abc" also raises TypeError', TypeError, lambda: x + "abc")
done()
