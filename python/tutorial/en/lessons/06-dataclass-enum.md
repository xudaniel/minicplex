# Lesson 6: dataclass and enum

> **You learn:** `@dataclass` generating `__init__`/`__repr__`/`__eq__`; defaults; `field(default_factory=list)`; `frozen=True`; `Enum`; type annotations
> **Code used:** `Params`, `Result`, `Status` and `Branching` in [`solver.py`](../../../minicplex/solver.py)
> **Exercise:** `python3 python/tutorial/en/run.py 06`
> **Do it online:** [open the web version, nothing to install](https://xudaniel.github.io/minicplex/python/en/#l06)

[← Operator overloading and immutable objects](05-operators.md) · [Contents](../README.md) · Next: [Dictionaries and sets →](07-dicts-sets.md)

## 1. dataclass: write the fields, get the rest for free

There are a dozen or so solver parameters, mostly left at their defaults ([`solver.py`](../../../minicplex/solver.py)):

```python
@dataclass
class Params:
    """Solver parameters (same defaults as the C++ version)."""
    relax_integrality: bool = False      # solve only the linear relaxation
    branching: Branching = Branching.PSEUDO_COST
    cut_rounds: int = 2                  # rounds of Gomory cuts at the root (0 = none)
    presolve: bool = True                # bound propagation + coefficient tightening
    ...
    verbose: bool = False                # print a CPLEX-style node log
    trace: bool = False                  # print every simplex pivot and branching decision
```

From these fields `@dataclass` writes `__init__`, `__repr__` and `__eq__` for you, so you can simply write:

```python
Params(trace=True)
Params(relax_integrality=True, presolve=False, cut_rounds=0)   # basics_07_fixed_cost.py
```

The `bool` and `int` after the colons are **type annotations**: Python doesn't check them at run time, but editors and `mypy` use them to find mistakes, and readers understand the code at a glance.

## 2. The mutable-default trap

`Result` has a few list fields:

```python
@dataclass
class Result:
    status: Status = Status.INFEASIBLE
    objective: float = math.nan
    x: List[float] = field(default_factory=list)       # ← can't be x: list = []
    duals: List[float] = field(default_factory=list)
```

Why not `= []`? A default is evaluated **once**, when the class is defined, so every object would share one list: change one and they all change.
dataclass simply refuses (it raises an error). `field(default_factory=list)` means "call `list()` to make a fresh one for each new object".

Plain functions have the same trap: with `def f(items=[])`, calls share that one list. The usual pattern is `def f(items=None)`, then `if items is None: items = []` inside.

## 3. frozen=True: can't be changed once made

```python
@dataclass(frozen=True)
class Point:
    x: float
    y: float
```

Unchangeable objects can go into a `set` or be `dict` keys (the dataclass also generates `__hash__`), and they can be shared safely (the lesson 5 argument). Lesson 12's `Course` is defined this way.

## 4. Enum: a set of named constants

```python
class Status(Enum):
    OPTIMAL = "Optimal"
    INFEASIBLE = "Infeasible"
    UNBOUNDED = "Unbounded"
    ...
    def __str__(self):
        return self.value
```

Why not just use the string `"Optimal"`? A typo like `"Optimla"` raises no error; it just silently never matches. A typo like `Status.OPTIMLA` raises `AttributeError` at once.
Also, `print(r.status)` prints `Optimal` (thanks to `__str__`), matching the C++ output; compare with `r.status is Status.OPTIMAL` or `==`.
`Status("Optimal")` looks a member up by value, which is handy when reading a CSV.

## 5. Your turn

Open [`exercises/l06_dataclass_enum.py`](../exercises/l06_dataclass_enum.py): a weather enum, a frozen point, and a shopping-cart dataclass. Run `python3 python/tutorial/en/run.py 06`.

## 6. Think about it

Why isn't `Result` `frozen=True`?

<details><summary>Answer</summary>

Because the solver fills in the result as it goes: `R.nodes += 1`, `R.status = ...`. If you wanted "no changes once handed over", you could make a frozen copy at the end with `dataclasses.replace`,
but for a small project it isn't worth it. Design is a trade-off: immutable is safer, mutable is more convenient.

</details>

[← Operator overloading and immutable objects](05-operators.md) · [Contents](../README.md) · Next: [Dictionaries and sets →](07-dicts-sets.md)
