# Lesson 14: More about functions: *args, **kwargs, unpacking and closures

> **You learn:** positional and keyword arguments; `*args` and `**kwargs`; spreading with `*` and `**` when calling; tuple unpacking and `*rest`; closures and `nonlocal`; the trap of making lambdas in a loop
> **Code used:** `Params` in [`solver.py`](../../../minicplex/solver.py), `itertools.product(*...)` in [`tests/test_solver.py`](../../../tests/test_solver.py)
> **Exercise:** `python3 python/tutorial/en/run.py 14`
> **Do it online:** [open the web version, nothing to install](https://xudaniel.github.io/minicplex/python/en/#l14)

[← Reading errors and debugging](13-debugging.md) · [Contents](../README.md) · Next: [Decorators →](15-decorators.md)

## 1. Collecting any number of arguments

```python
def total(*nums):          # pass as many as you like; nums is a tuple
    return sum(nums)

def show(**info):          # any number of keyword arguments; info is a dict
    for k, v in info.items():
        print(k, "=", v)

show(name="cake", value=3)
```

`args` and `kwargs` are only customary names; what matters is the `*` and `**` in front.

## 2. Spreading when you call

The other way round: when calling, `*` spreads a sequence into several positional arguments, and `**` spreads a dict into several keyword arguments:

```python
total(*[4, 5])                       # same as total(4, 5)
Params(**{"trace": True})            # same as Params(trace=True)
```

minicplex's tests use it to enumerate every integer point: one `range` per variable, as many `range`s as there are variables, a number not known in advance, so

```python
itertools.product(*(range(int(v.lb), U + 1) for v in M.vars))
```

spreads a series of `range`s into `product`.

## 3. Unpacking

```python
lb, ub = float(lb), float(ub)              # model.py: assign two variables at once
for k, a in c.coefs.items():               # each item is (index, coefficient), unpacked directly
x4, x5, x6, x7 = (m.add_var() for _ in range(4))   # in the tests: create 4 variables at once
first, *rest = [1, 2, 3]                   # first = 1, rest = [2, 3]
a, b = b, a                                # swap two variables, no temporary needed
```

## 4. Keyword-only arguments

`Params` has a dozen fields and nobody remembers their order, so everyone writes them by name: `Params(relax_integrality=True, cut_rounds=0)`.
To **force** callers to pass by name, put a lone `*` in the parameter list:

```python
def solve_with(model, *, gap=1e-6, quiet=False):   # gap and quiet can only be written gap=..., quiet=...
```

## 5. Closures: functions that remember outside variables

```python
def make_counter():
    count = 0
    def counter():
        nonlocal count      # declare it before changing the outer variable
        count += 1
        return count
    return counter

c = make_counter()
c(), c(), c()               # 1, 2, 3
```

The inner function "remembers" the outer `count`, even after `make_counter` has returned. Each call to `make_counter` makes a new `count`.
The exercises' `check.py` uses this everywhere: in `eq("…", 6, lambda: total(1, 2, 3))` the lambda remembers what to call, and only calls it when grading.

## 6. The trap of making functions in a loop

```python
adders = [lambda x: x + k for k in range(3)]
[f(10) for f in adders]     # [12, 12, 12]   ← not [10, 11, 12]!
```

A closure remembers the **variable itself**, not its value at the time. All three functions look at the same `k`, and when they're called the loop has long finished, so `k` is 2.
The fix is a default argument to "snapshot" the value at that moment: `lambda x, k=k: x + k` (defaults are evaluated when the function is defined: this time lesson 13's trap is exactly what we want).

## 7. Your turn

Open [`exercises/l14_functions.py`](../exercises/l14_functions.py) and run `python3 python/tutorial/en/run.py 14`.

The last one is a **🤔 guess, then run**: don't run anything yet. Read the few lines of code in the task, write your guess after `return`, then run and see whether you were right. A wrong guess is fine; working out why is the point.

## 8. Think about it

What does `print(*["a", "b", "c"], sep="-")` print?

<details><summary>Answer</summary>

`a-b-c`. `*` spreads the list into three positional arguments, the same as `print("a", "b", "c", sep="-")`. `print` itself takes any number of values with `*args`.

</details>

[← Reading errors and debugging](13-debugging.md) · [Contents](../README.md) · Next: [Decorators →](15-decorators.md)
