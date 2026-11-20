"""Lesson 2: Numbers and floating-point error.

A solver lives with decimals every day: 0.1 + 0.2 is not 0.3, infinity, rounding rules...
In this lesson you write the small helpers minicplex uses for them (the real ones are in minicplex/jmath.py and lp_engine.py).
Run: python3 python/tutorial/en/run.py 02
"""
import math

from check import lesson, eq, that, done


def near(a, b, tol=1e-9):
    """Are a and b "close enough": |a - b| <= tol * (1 + |b|)? (A relative error, fine for large and small numbers.)"""
    raise NotImplementedError("TODO")  # ← write your code here


def is_integral(v):
    """Is v a whole number (within 1e-9)? Infinity and NaN are not.
    Hint: math.isfinite(v); round(v) is the whole number nearest to v."""
    raise NotImplementedError("TODO")  # ← write your code here


def cround(v):
    """Rounding with halves away from zero (C++'s std::round): 2.5 -> 3, -2.5 -> -3.
    Python's own round(2.5) is 2 (halves go to the even number), so write it yourself: sign * floor(|v| + 0.5)."""
    raise NotImplementedError("TODO")  # ← write your code here


def fractionality(v):
    """How far is v from the nearest whole number? 3.2 -> 0.2, 3.9 -> 0.1 (branch and bound uses it to pick the "least whole" variable)."""
    raise NotImplementedError("TODO")  # ← write your code here


lesson("Lesson 2: Numbers and floating-point error")
that("0.1 + 0.2 and 0.3 are NOT equal under ==", lambda: 0.1 + 0.2 != 0.3)
that("but they are close enough", lambda: near(0.1 + 0.2, 0.3))
that("1 and 1.001 are not close", lambda: not near(1, 1.001))
that("but 1e9 and 1e9 + 0.5 are (relative error only 5e-10)", lambda: near(1e9, 1e9 + 0.5))
that("3.0000000001 counts as whole", lambda: is_integral(3.0000000001))
that("2.5 is not whole", lambda: not is_integral(2.5))
that("infinity is not whole", lambda: not is_integral(math.inf))
that("NaN is not whole", lambda: not is_integral(math.nan))
eq("Python's round(2.5) is 2 (halves to even)", 2, lambda: round(2.5))
eq("cround(2.5) is 3", 3, lambda: cround(2.5))
eq("cround(-2.5) is -3", -3, lambda: cround(-2.5))
eq("cround(2.4) is 2", 2, lambda: cround(2.4))
that("fractionality(3.2) is about 0.2", lambda: near(fractionality(3.2), 0.2))
that("fractionality(3.9) is about 0.1", lambda: near(fractionality(3.9), 0.1))
that("fractionality(-0.75) is 0.25", lambda: near(fractionality(-0.75), 0.25))
done()
