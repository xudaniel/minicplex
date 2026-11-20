"""Lesson 15: Decorators.

@property, @staticmethod and @dataclass are all decorators: a function that takes a function (or class) and returns a new one.
You write a few, and finally see functools.lru_cache make code ten thousand times faster with one line.
Run: python3 python/tutorial/en/run.py 15
"""
import functools

from check import lesson, eq, raises, that, done


def count_calls(func):
    """A decorator that counts calls, stored in wrapper.calls.
    Use @functools.wraps(func) to keep the original name and docstring."""
    raise NotImplementedError("TODO")  # ← write your code here


def retry(times):
    """A decorator with an argument: retry when the function raises ValueError, at most times attempts in all; if the last one fails too, re-raise.
    Three layers: retry(times) returns the decorator deco(func), and deco returns wrapper(*args, **kwargs)."""
    raise NotImplementedError("TODO")  # ← write your code here


def memoize(func):
    """Write a caching decorator: compute each set of arguments once and keep results in a dict cache (keyed by the args tuple)."""
    raise NotImplementedError("TODO")  # ← write your code here


def make_greet():
    """Decorate a function with @count_calls (inside a function, so this file still runs before count_calls is written)."""
    @count_calls
    def greet(name):
        """Say hello."""
        return f"Hello, {name}"
    return greet


def call_three_times():
    greet = make_greet()
    greet("a"), greet("b"), greet("c")
    return greet.calls


def make_flaky(fail_times):
    """Make a function that fails its first fail_times calls, to test retry."""
    state = {"n": 0}

    def flaky():
        state["n"] += 1
        if state["n"] <= fail_times:
            raise ValueError("network hiccup")
        return "success"
    return flaky


def fib_calls(decorator):
    """Wrap a recursive Fibonacci in the given decorator, compute fib(25) and return (result, how many times the body really ran)."""
    body_runs = [0]

    @decorator
    def fib(n):
        body_runs[0] += 1
        return n if n < 2 else fib(n - 1) + fib(n - 2)
    return fib(25), body_runs[0]


lesson("Lesson 15: Decorators")
eq("the decorated function still works", "Hello, Ming", lambda: make_greet()("Ming"))
eq("called 3 times, so calls is 3", 3, call_three_times)
eq("functools.wraps kept the name", "greet", lambda: make_greet().__name__)
eq("functools.wraps kept the docstring", "Say hello.", lambda: make_greet().__doc__)
eq("fails twice, 3 attempts: success", "success", lambda: retry(3)(make_flaky(2))())
raises("fails 3 times, 3 attempts: the error comes out", ValueError, lambda: retry(3)(make_flaky(3))())
eq("no cache: fib(25) runs its body 242785 times", (75025, 242785), lambda: fib_calls(lambda f: f))
eq("with your memoize: only 26", (75025, 26), lambda: fib_calls(memoize))
eq("the standard functools.lru_cache: also 26", (75025, 26), lambda: fib_calls(functools.lru_cache(maxsize=None)))
done()
