"""Lesson 16: Generators and iterators.

The thing inside sum(hours[t] * give[t][p] for t in range(tasks)) is a generator: it computes one value at a time instead of
building a whole list first. You write generators with yield, finishing with one that enumerates every combination, and
redo lesson 3's brute-force knapsack with it.
Run: python3 python/tutorial/en/run.py 16
"""
import itertools

from check import lesson, eq, that, done
from minicplex import LinExpr, Model, ObjSense, VarType, solve


def countdown(n):
    """Yield n, n-1, ..., 1. A function that uses yield becomes a generator."""
    # >>>
    while n > 0:
        yield n
        n -= 1
    # <<<


def fibonacci():
    """The endless Fibonacci sequence: 0, 1, 1, 2, 3, 5, ... (it never stops; the caller decides how many to take)"""
    # >>>
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b
    # <<<


def chunks(seq, k):
    """Cut a sequence into pieces of k: chunks([1,2,3,4,5], 2) yields [1,2], [3,4], [5]."""
    # >>>
    for i in range(0, len(seq), k):
        yield seq[i:i + k]
    # <<<


def clean_numbers(lines):
    """Yield numbers from lines of text: skip blank lines and # comments, convert the rest with float.
    lines may be huge (a big file, say), so use a generator and handle one line at a time."""
    # >>>
    for line in lines:
        s = line.strip()
        if s and not s.startswith("#"):
            yield float(s)
    # <<<


def assignments(n, values):
    """n positions, each taking a value from values: yield every combination (as tuples), in the same order as itertools.product(values, repeat=n).
    Hint: recursion. For n == 0 yield one empty tuple (); otherwise for each value v of the first position,
    for rest in assignments(n - 1, values): yield (v,) + rest."""
    # >>>
    if n == 0:
        yield ()
        return
    for v in values:
        for rest in assignments(n - 1, values):
            yield (v,) + rest
    # <<<


def knapsack_brute(values, weights, capacity):
    """A brute-force knapsack using your assignments (lesson 3 used itertools.product)."""
    best = 0
    for pick in assignments(len(values), [0, 1]):
        if sum(w * p for w, p in zip(weights, pick)) <= capacity:
            best = max(best, sum(v * p for v, p in zip(values, pick)))
    return best


def knapsack_solver(values, weights, capacity):
    m = Model()
    take = [m.add_var(0, 1, VarType.BINARY, f"t{k}") for k in range(len(values))]
    m.add_constr(sum((w * t for w, t in zip(weights, take)), LinExpr()) <= capacity)
    m.set_objective(sum((v * t for v, t in zip(values, take)), LinExpr()), ObjSense.MAXIMIZE)
    return solve(m).objective


def guess_exhausted():
    """🤔 Guess, then run: don't run it yet! Read the lines below, guess the result, write your guess after return,
    then run and see if you were right.

        g = (x * x for x in range(3))
        first = list(g)
        second = list(g)
        what is (first, second)?
    """
    # >>>
    return ([0, 1, 4], [])
    # <<<


lesson("Lesson 16: Generators and iterators")
eq("countdown(3) yields 3, 2, 1", [3, 2, 1], lambda: list(countdown(3)))
that("countdown is a generator (not a list)", lambda: hasattr(countdown(3), "__next__"))
eq("the first 10 Fibonacci numbers (itertools.islice takes the first few)", [0, 1, 1, 2, 3, 5, 8, 13, 21, 34],
   lambda: list(itertools.islice(fibonacci(), 10)))
eq("chunks", [[1, 2], [3, 4], [5]], lambda: list(chunks([1, 2, 3, 4, 5], 2)))
eq("clean_numbers", [1.5, 2.0], lambda: list(clean_numbers(["1.5", "", "# comment", " 2 "])))
eq("clean_numbers works one at a time: taking only the first never touches the bad data after it", 1.0,
   lambda: next(clean_numbers(["1", "this line is not a number"])))
eq("assignments(2, [0, 1])", [(0, 0), (0, 1), (1, 0), (1, 1)], lambda: list(assignments(2, [0, 1])))
that("same result as itertools.product", lambda: list(assignments(3, "ab")) == list(itertools.product("ab", repeat=3)))
that("brute force and the solver agree", lambda: knapsack_brute([10, 13, 7, 8, 6], [5, 6, 4, 3, 2], 12)
     == knapsack_solver([10, 13, 7, 8, 6], [5, 6, 4, 3, 2], 12))
eq("🤔 guess: list() the same generator twice", ([0, 1, 4], []), guess_exhausted)
done()
