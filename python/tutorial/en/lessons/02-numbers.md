# Lesson 2: Numbers and floating-point error

> **You learn:** `int` and `float`; floating-point error; comparing with a relative tolerance; infinity and NaN; three kinds of "rounding"; `-0.0`
> **Code used:** [`jmath.py`](../../../minicplex/jmath.py), the tolerance constants and `_is_integral` at the top of [`lp_engine.py`](../../../minicplex/lp_engine.py)
> **Exercise:** `python3 python/tutorial/en/run.py 02`
> **Do it online:** [open the web version, nothing to install](https://xudaniel.github.io/minicplex/python/en/#l02)

[← Your first model](01-first-model.md) · [Contents](../README.md) · Next: [Lists and comprehensions →](03-lists.md)

## 1. 0.1 + 0.2 ≠ 0.3

```python
>>> 0.1 + 0.2
0.30000000000000004
```

Computers store decimals in binary, where `0.1` repeats forever, so only an approximation is stored. Every calculation can add a tiny error.
A solver does millions of operations and the errors add up, so **never compare two computed decimals with `==`**; ask whether they are close enough.

## 2. Tolerance: how close counts as "close"?

At the top of [`lp_engine.py`](../../../minicplex/lp_engine.py):

```python
PRIMAL_TOL = 1e-7   # allowed bound violation (scaled by magnitude)
DUAL_TOL = 1e-9     # reduced-cost tolerance
PIVOT_TOL = 1e-9    # smallest acceptable pivot element
```

Note "scaled by magnitude":

```python
tl = PRIMAL_TOL * (1.0 + abs(lb))
```

A difference of 0.5 makes `1` and `1.5` far apart, but `1000000000` and `1000000000.5` almost the same. So use a **relative error**:
`|a - b| ≤ tol × (1 + |b|)`. The 1 is there so that when `b` is near 0 you don't demand an exact match.
The standard library has one ready-made: `math.isclose(a, b, rel_tol=1e-9, abs_tol=0.0)`.

## 3. Infinity and NaN

```python
from math import inf, nan, isfinite   # minicplex's INF is math.inf, meaning "no upper bound": add_var(0, INF)
inf > 1e308             # True
inf - inf               # nan (Not a Number: "can't be worked out")
nan == nan              # False! NaN equals nothing, not even itself
isfinite(3.0), isfinite(inf), isfinite(nan)   # True False False
```

Before asking "is this a whole number", rule out infinity and NaN ([`lp_engine.py`](../../../minicplex/lp_engine.py)):

```python
def _is_integral(v):
    return _isfinite(v) and abs(v - jmath.rint(v)) < 1e-9
```

## 4. Three kinds of "rounding"

| Code | 2.5 | -2.5 | 3.5 | Rule |
|---|---|---|---|---|
| `round(v)` (Python) | 2 | -2 | 4 | halves go to the **even** number (banker's rounding) |
| `math.floor(v + 0.5)` | 3 | -2 | 4 | halves go up |
| C++ `std::round` | 3 | -3 | 4 | halves go **away from 0** |

minicplex has to compute every step exactly as the C++ version does, so it can't use Python's `round`; it has its own ([`jmath.py`](../../../minicplex/jmath.py)):

```python
def cround(v):
    """C++'s std::round: exact halves go away from 0."""
    s = 1.0 if v > 0 else -1.0 if v < 0 else v
    return s * floor(abs(v) + 0.5)
```

## 5. Even -0.0 matters

Floats have both `+0.0` and `-0.0`. `0.0 == -0.0` is `True`, but they print differently (`-0`).
Python's `math.ceil(-0.5)` returns the integer `0` and loses the sign; Java and C++ return `-0.0`.
So that all three versions print exactly the same results, `ceil` and `floor` in [`jmath.py`](../../../minicplex/jmath.py) put the sign back with `math.copysign`.

That sounds fussy, but this fussiness is what lets CI demand that "the Python and C++ versions take exactly the same computational path on 600 random problems". The slightest difference and the paths split.

## 6. Common mistakes

- `if x == 0.3:` comparing a computed decimal.
- Mixing up "infeasible" with "couldn't be computed": NaN makes every comparison `False` and quietly skips checks.
- Assuming `round` is the rounding you learned at school.

## 7. Your turn

Open [`exercises/l02_numbers.py`](../exercises/l02_numbers.py), write `near`, `is_integral`, `cround` and `fractionality`, and run `python3 python/tutorial/en/run.py 02`.

## 8. Think about it

Why is `1e16 + 1 == 1e16` `True`?

<details><summary>Answer</summary>

A `float` has only about 16 significant digits. Around `1e16`, neighbouring representable numbers are 2 apart, so the `+1` is rounded away.
That's why, when very large and very small numbers mix in a solver (say a `1000000` in a big-M constraint), the small part can "vanish"; it's one reason advanced example 07 keeps big M as small as possible.
Python's `int` has no such problem: `10**16 + 1` is exactly `10000000000000001`.

</details>

[← Your first model](01-first-model.md) · [Contents](../README.md) · Next: [Lists and comprehensions →](03-lists.md)
