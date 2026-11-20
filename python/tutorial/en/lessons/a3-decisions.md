# Basics A3: Making decisions

> **You learn:** `True` and `False`; comparisons `== != < <= > >=`; `if / elif / else`; `and`, `or`, `not`
> **Time:** about 15 minutes · **Exercise:** `python3 python/tutorial/en/run.py A03`
> **Do it online:** [open the web version, nothing to install](https://xudaniel.github.io/minicplex/python/en/#a03)

[← Variables and arithmetic](a2-variables.md) · [Contents](../README.md) · Next: [Repeating things →](a4-loops.md)

## 1. A comparison is either true or false

```python
10 >= 8     # True
10 == 12    # False   ← two equals signs mean "is equal to"
"a" != "b"  # True    ← != means "is not equal to"
```

`True` and `False` are the only two values of type `bool` (boolean). A function can simply `return money >= cost`; there's no need for "if this, return True, otherwise return False".

## 2. if / elif / else

```python
if score >= 90:
    return "excellent"
elif score >= 75:      # elif = else if: when the line above fails, try this one
    return "good"
else:
    return "fail"
```

- The condition ends with a colon `:` and the code below it is indented.
- Conditions are checked from the top, and only the **first** one that holds runs; the rest are skipped. That's why the scores go from high to low.

## 3. and, or, not

```python
height >= 120 and age >= 8     # true only when both hold
is_weekend or is_holiday       # true when at least one holds
not enough(10, 12)             # the opposite
8 <= age <= 60                 # a Python special: chained, same as 8 <= age and age <= 60
```

> **In minicplex:** the solver decides whether a variable is "fixed" with `if lf and uf and lb == ub: return FIXED`
> ([`lp_engine.py`](../../../minicplex/lp_engine.py), `_default_status`): both bounds are finite, and they are equal.

## 4. Common mistakes

- `if score = 90:` is missing an equals sign: a syntax error.
- A missing colon or uneven indentation: `SyntaxError` / `IndentationError`.
- The wrong order: if you test `score >= 60` first, 95 also gets "pass".

## 5. Your turn

Open [`exercises/a03_decisions.py`](../exercises/a03_decisions.py) and run `python3 python/tutorial/en/run.py A03`.

## 6. Think about it

Is `0.1 + 0.2 == 0.3` `True` or `False`?

<details><summary>Answer</summary>

It's `False`! Decimals in a computer carry tiny errors, and `0.1 + 0.2` is really `0.30000000000000004`. So you can't compare decimals with `==`;
you check whether they are "close enough". The solver does this everywhere; lesson 2 is all about it.

</details>

[← Variables and arithmetic](a2-variables.md) · [Contents](../README.md) · Next: [Repeating things →](a4-loops.md)
