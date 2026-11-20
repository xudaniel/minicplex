# Basics A5: Writing functions

> **You learn:** `def`; parameters and return values; default arguments; passing arguments by name; docstrings
> **Time:** about 20 minutes · **Exercise:** `python3 python/tutorial/en/run.py A05`
> **Do it online:** [open the web version, nothing to install](https://xudaniel.github.io/minicplex/python/en/#a05)

[← Repeating things](a4-loops.md) · [Contents](../README.md) · Next: [Lists →](a6-lists.md)

## 1. A function gives a piece of code a name

```python
def c_to_f(c):
    """Convert Celsius to Fahrenheit."""     # ← docstring: says what the function does
    return c * 9 / 5 + 32

print(c_to_f(37))    # 98.6
```

- `c` is a **parameter**: the value passed in when the function is called.
- `return` hands the result back to the caller, and the function ends there.
- A function without `return` returns `None` ("nothing").

Why bother with functions: a name tells the reader what the code does; you write it once and use it everywhere; and a fix only has to be made in one place.

## 2. Default arguments

```python
def discount(price, percent=10):
    return price * (100 - percent) / 100

discount(200)              # 180.0   ← no percent given, so the default 10 is used
discount(200, 25)          # 150.0
discount(80, percent=50)   # 40.0    ← passed by name: obvious what 50 means
```

> **In minicplex:** the function that creates variables is designed exactly like this ([`model.py`](../../../minicplex/model.py)):
>
> ```python
> def add_var(self, lb=0.0, ub=INF, type=VarType.CONTINUOUS, name=""):
> ```
>
> So `m.add_var()` is a continuous variable in `[0, +∞)`, and `m.add_var(name="y")` changes only the name and keeps the other defaults.
> Java has no default arguments, so the same thing takes 4 "overloaded" methods; compare with the [Java version](../../../../java/src/main/java/minicplex/Model.java).

## 3. Common mistakes

- Using `print` instead of `return`: you see the result on screen, but the caller gets nothing.
- A list as a default, `def f(items=[])`: every call shares the same list (lesson 6 explains this trap).
- Arguments in the wrong order: `clamp(x, lo, hi)` written as `clamp(lo, hi, x)`. Passing by name avoids it.

## 4. Your turn

Open [`exercises/a05_functions.py`](../exercises/a05_functions.py) and run `python3 python/tutorial/en/run.py A05`.

## 5. Think about it

Can `clamp(x, lo, hi)` be written in one line?

<details><summary>Answer</summary>

Yes: `return max(lo, min(x, hi))`. First take the smaller of `x` and `hi` (not above the upper limit), then the larger of that and `lo` (not below the lower limit).

</details>

[← Repeating things](a4-loops.md) · [Contents](../README.md) · Next: [Lists →](a6-lists.md)
