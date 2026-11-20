"""Lesson 14: More about functions: *args, **kwargs, unpacking and closures.

minicplex is full of these: Params(trace=True, cut_rounds=0) uses keyword arguments; for k, a in c.coefs.items() unpacks;
the tests' itertools.product(*(range(...) for v in M.vars)) spreads a sequence of arguments with *. You practise each one.
Run: python3 python/tutorial/en/run.py 14
"""
from check import lesson, eq, near, raises, that, done
from minicplex import Params


def total(*nums):
    """Take any number of numbers and return their sum: total(1, 2, 3) is 6, total() is 0. Inside the function, nums is a tuple."""
    # >>>
    return sum(nums)
    # <<<


def make_params(**changes):
    """Change a few settings from the defaults: make_params(trace=True) returns Params(trace=True).
    A misspelt name (say trac=True) should raise TypeError; Params raises it itself, you just pass changes on with ** as they are."""
    # >>>
    return Params(**changes)
    # <<<


def first_and_rest(seq):
    """Unpacking: first_and_rest([1, 2, 3]) returns (1, [2, 3]). One line: first, *rest = seq."""
    # >>>
    first, *rest = seq
    return first, rest
    # <<<


def swap_pairs(pairs):
    """[(a, b), ...] -> [(b, a), ...]. Unpack right in the for: for a, b in pairs."""
    # >>>
    return [(b, a) for a, b in pairs]
    # <<<


def make_counter():
    """A closure: return a function that returns 1, 2, 3, ... on successive calls.
    Hint: put count = 0 in the outer function and change it from the inner one with nonlocal count."""
    # >>>
    count = 0

    def counter():
        nonlocal count
        count += 1
        return count
    return counter
    # <<<


def make_adders(n):
    """Return n functions; function k adds k to its argument: make_adders(3)[2](10) is 12.
    Careful! [lambda x: x + k for k in range(n)] is wrong: all the functions share one k (its value when the loop ends).
    The fix: a default argument captures k at that moment: lambda x, k=k: x + k."""
    # >>>
    return [lambda x, k=k: x + k for k in range(n)]
    # <<<


def guess_late_binding():
    """🤔 Guess, then run: don't run it yet! Read the lines below, guess the result, write your guess after return,
    then run and see if you were right.

        adders = [lambda x: x + k for k in range(3)]
        [f(10) for f in adders]   ← what is the result?
    """
    # >>>
    return [12, 12, 12]
    # <<<


lesson("Lesson 14: More about functions")
eq("total(1, 2, 3) is 6", 6, lambda: total(1, 2, 3))
eq("total() is 0", 0, lambda: total())
eq("total(*[4, 5]) works too: * spreads the list", 9, lambda: total(*[4, 5]))
that("make_params(trace=True, cut_rounds=0)", lambda: make_params(trace=True, cut_rounds=0) == Params(trace=True, cut_rounds=0))
that("make_params() gives the defaults", lambda: make_params() == Params())
raises("a misspelt name raises TypeError", TypeError, lambda: make_params(trac=True))
near("spread a dict with **: make_params(**{'mip_gap': 0.01}).mip_gap", 0.01, lambda: make_params(**{"mip_gap": 0.01}).mip_gap)
eq("first_and_rest([1, 2, 3])", (1, [2, 3]), lambda: first_and_rest([1, 2, 3]))
eq("first_and_rest('abc')", ("a", ["b", "c"]), lambda: first_and_rest("abc"))
eq("swap_pairs", [(2, 1), ("b", "a")], lambda: swap_pairs([(1, 2), ("a", "b")]))
eq("counter: 1, 2, 3", [1, 2, 3], lambda: (lambda c: [c(), c(), c()])(make_counter()))
eq("two counters count separately", (2, 1), lambda: (lambda a, b: (a(), a(), b())[1:])(make_counter(), make_counter()))
eq("make_adders(3) adds 0, 1 and 2", [10, 11, 12], lambda: [f(10) for f in make_adders(3)])
eq("🤔 guess: three lambdas made in a loop", [12, 12, 12], guess_late_binding)
done()
