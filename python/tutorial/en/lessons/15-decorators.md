# Lesson 15: Decorators

> **You learn:** functions are objects; a decorator = a function that takes a function and returns a function; the `@` syntax; `functools.wraps`; decorators with arguments; `functools.lru_cache`
> **Code used:** `@property` and `@staticmethod` in [`model.py`](../../../minicplex/model.py), `@dataclass` in [`solver.py`](../../../minicplex/solver.py)
> **Exercise:** `python3 python/tutorial/en/run.py 15`
> **Do it online:** [open the web version, nothing to install](https://xudaniel.github.io/minicplex/python/en/#l15)

[← More about functions](14-functions.md) · [Contents](../README.md) · Next: [Generators and iterators →](16-generators.md)

## 1. You've already used plenty of decorators

```python
@property
def num_vars(self): ...           # model.py

@staticmethod
def of(v, coef=1.0): ...          # model.py

@dataclass
class Params: ...                 # solver.py
```

The line starting with `@` is a **decorator**. It's really just shorthand:

```python
@property
def num_vars(self): ...
# is exactly the same as
def num_vars(self): ...
num_vars = property(num_vars)
```

That is: once the function is defined, hand it to `property` and replace the original name with whatever comes back. `property`, `staticmethod` and `dataclass` are all ordinary functions (or classes)
that take a function (or class) and return a new version "with something added".

## 2. Writing your own

Functions in Python are ordinary objects: they can be passed as arguments and returned as values (lesson 14's closures). So:

```python
import functools

def count_calls(func):
    @functools.wraps(func)          # make wrapper look like the original function (name, docstring)
    def wrapper(*args, **kwargs):   # accept whatever arguments the original takes
        wrapper.calls += 1
        return func(*args, **kwargs)   # and pass them straight on
    wrapper.calls = 0
    return wrapper

@count_calls
def greet(name):
    return f"Hello, {name}"
```

`*args, **kwargs` let one decorator wrap any function. Without `functools.wraps`, `greet.__name__` would become `"wrapper"`, and error messages and docs would be wrong.

## 3. Decorators with arguments

`@retry(3)` adds a layer: `retry(3)` is called first and **returns a decorator**, which then decorates the function. So there are three levels of function:

```python
def retry(times):              # level 1: takes the argument
    def deco(func):            # level 2: takes the function
        def wrapper(*args, **kwargs):   # level 3: what actually gets called
            ...
        return wrapper
    return deco
```

## 4. The most useful one: lru_cache

A recursive Fibonacci `fib(n) = fib(n-1) + fib(n-2)` computes the same values over and over: `fib(25)` runs the function body about 240,000 times.
Add one line, `@functools.lru_cache(maxsize=None)`, and each `n` is computed once: just 26 times.

This is **memoization**. Dynamic programming and search use it everywhere: branch and bound's pseudo-costs (`_PseudoCosts` in [`solver.py`](../../../minicplex/solver.py))
are a kind of "remembering what was computed" too: how much branching up or down on each variable worsened the objective is recorded once, so next time it can be estimated without expensive strong branching.

## 5. When to use a decorator

When something has to **wrap many functions** but has nothing to do with their own logic: timing, counting, caching, retrying, permission checks, logging.
As a decorator, each function needs just one extra line instead of the same code copied everywhere. Conversely, logic used once belongs directly in the function; don't use decorators for their own sake.

## 6. Your turn

Open [`exercises/l15_decorators.py`](../exercises/l15_decorators.py): write `count_calls`, a `retry` that takes an argument, and your own `memoize`, then compare it with `lru_cache`. Run `python3 python/tutorial/en/run.py 15`.

## 7. Think about it

`memoize` uses the `args` tuple as a dictionary key. What happens if one of the arguments is a list?

<details><summary>Answer</summary>

`TypeError: unhashable type: 'list'`: lists can change, so they can't be dictionary keys (lesson 7). `lru_cache` is the same.
So a function you want to cache should take unchangeable arguments such as numbers, strings and tuples.

</details>

[← More about functions](14-functions.md) · [Contents](../README.md) · Next: [Generators and iterators →](16-generators.md)
