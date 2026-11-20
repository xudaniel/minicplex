# Lesson 5: Operator overloading and immutable objects

> **You learn:** "magic methods" such as `__add__`, `__radd__`, `__mul__` and `__le__`; `NotImplemented`; why `sum()` needs `__radd__`; immutable objects; copying
> **Code used:** `LinExpr` and `Var` in [`model.py`](../../../minicplex/model.py)
> **Exercise:** `python3 python/tutorial/en/run.py 05`
> **Do it online:** [open the web version, nothing to install](https://xudaniel.github.io/minicplex/python/en/#l05)

[← Classes and objects](04-classes.md) · [Contents](../README.md) · Next: [dataclass and enum →](06-dataclass-enum.md)

## 1. How does 2 * x + 3 * y <= 12 become a constraint?

When Python sees `a + b` it actually calls `a.__add__(b)`; for `a <= b` it calls `a.__le__(b)`. Define these methods in a class
and your own objects can use operators. That's what `LinExpr` (a linear expression) does ([`model.py`](../../../minicplex/model.py)):

```python
class LinExpr:
    def __add__(self, o):
        if isinstance(o, Var):
            return self.plus_var(o, 1.0)
        if isinstance(o, LinExpr):
            return self.plus_expr(o)
        if _is_num(o):
            return self.plus_const(float(o))
        return NotImplemented          # a type we don't know: let Python handle it

    def __le__(self, o):
        return Constraint.make(self, Sense.LE, LinExpr.wrap(o))
```

Step by step, `2 * x + 3 * y <= 12` is: `x.__rmul__(2)` → the expression `2x`; `2x.__add__(3y)` → `2x + 3y`; `.__le__(12)` → a constraint.

## 2. What if the number is on the left? __radd__

`2 * x` first tries `int.__mul__(2, x)`: integers don't know `Var`, so it returns `NotImplemented`. Python then tries it **the other way round**: `x.__rmul__(2)`.
Methods starting with r are the "when I'm on the right of the operator" versions.

`sum([x, y, x])` needs it too: `sum` starts from `0`, so the first step is `0 + x`, which only `x.__radd__(0)` can handle.

```python
def __radd__(self, o):
    if _is_num(o):          # makes sum([...]) work: 0 + e
        return self.plus_const(float(o))
    return NotImplemented
```

**`NotImplemented` is not `NotImplementedError`.** The first is a special value meaning "I don't handle this combination, ask the other side"; only when neither side handles it does Python raise `TypeError`.
The second is an exception (the TODO in the exercises uses it).

## 3. Immutable: every operation returns a new object

```python
def plus_const(self, c):
    e = self.copy()         # copy first
    e.constant += c         # change only the copy
    return e                # self is untouched
```

If `+` changed the object itself, this would happen:

```python
cost = 5 * cake
with_bread = cost + 4 * bread    # meant to be a new expression
m.set_objective(cost)            # meant 5 cake, but cost has already become 5 cake + 4 bread
```

Immutable objects can be passed around and shared in several places without anyone secretly changing them. Python's `str`, `tuple` and `int` are all immutable.

Note that `copy()` copies the dictionary: `e.terms = dict(self.terms)`. Writing `e.terms = self.terms` would make two expressions share one dictionary (an alias again).

## 4. == returns a constraint, not True / False

In minicplex, `x == 3` is an equality constraint. The price: `Var` can no longer use a plain `==` to ask "is this the same variable".
minicplex's compromise: when both sides are variables, the constraint acts as "same index?" inside an `if` (`Constraint.__bool__`),
so `x in [x, y]` and `{x: 1}[x]` still work; in every other case, using a constraint as True/False raises an error, to stop code like `if 2 * x <= 3:` that looks right but means nothing.

## 5. Common mistakes

- Writing `__add__` without `__radd__`: `x + 1` works, but `1 + x` and `sum(...)` raise `TypeError`.
- `raise TypeError` on an unknown type instead of `return NotImplemented`: it takes away Python's chance to ask the other side.
- Changing `self` inside an operator method.

## 6. Your turn

Open [`exercises/l05_operators.py`](../exercises/l05_operators.py) and write a mini expression class `Expr`: `+`, `*` and `sum()`, all immutable. Run `python3 python/tutorial/en/run.py 05`.

## 7. Think about it

Which method does `x += 1` call? `Expr` has no `__iadd__`; does it still work?

<details><summary>Answer</summary>

Python looks for `__iadd__` (in-place add) first; if there isn't one it falls back to `x = x + 1`, i.e. `__add__`, and assigns the new object to `x`. So it works, and the original object is untouched, which is exactly what an immutable object wants.
Lists are different: `list.__iadd__` changes the list in place, so `a += [1]` affects every name pointing at that list.

</details>

[← Classes and objects](04-classes.md) · [Contents](../README.md) · Next: [dataclass and enum →](06-dataclass-enum.md)
