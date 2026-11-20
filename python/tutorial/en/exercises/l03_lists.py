"""Lesson 3: Lists, loops and comprehensions.

In minicplex the simplex tableau is a "flattened" list: row i, column j lives at T[i * N + j].
This lesson practises indexing, comprehensions and zip / enumerate, then a brute-force knapsack checked against the solver.
Run: python3 python/tutorial/en/run.py 03
"""
import itertools

from check import lesson, eq, near, that, done
from minicplex import LinExpr, Model, ObjSense, VarType, solve


def get(flat, n, i, j):
    """flat is an m x n matrix flattened row by row. Return row i, column j (both counted from 0)."""
    raise NotImplementedError("TODO")  # ← write your code here


def row_sums(flat, m, n):
    """The sum of each row, as a list of length m. Try writing it as a one-line comprehension."""
    raise NotImplementedError("TODO")  # ← write your code here


def make_grid(m, n):
    """An m x n list of lists full of 0. Careful: [[0] * n] * m is wrong (every row is the same list)!"""
    raise NotImplementedError("TODO")  # ← write your code here


def knapsack_brute(values, weights, capacity):
    """Brute-force knapsack: try every take / leave combination and return the best total value within the capacity.
    Hint: itertools.product([0, 1], repeat=len(values)) yields every 0/1 combination; zip pairs two lists."""
    raise NotImplementedError("TODO")  # ← write your code here


def knapsack_solver(values, weights, capacity):
    """The same problem for minicplex: one 0-1 variable per item. Return the best total value."""
    # TODO take = [m.add_var(0, 1, VarType.BINARY) for ...]; sum(generator, LinExpr()) adds up many terms
    raise NotImplementedError("TODO")  # ← write your code here


def guess_grid():
    """🤔 Guess, then run: don't run it yet! Read the lines below, guess the result, write your guess after return,
    then run and see if you were right.

        g = [[0] * 3] * 2
        g[0][0] = 99
        what is g now?
    """
    raise NotImplementedError("TODO")  # ← write your code here


A = [1, 2, 3,
     4, 5, 6]  # 2 rows, 3 columns
VALUES, WEIGHTS = [10, 13, 7, 8, 6, 9, 11, 4], [5, 6, 4, 3, 2, 5, 6, 1]

lesson("Lesson 3: Lists, loops and comprehensions")
eq("row 1, column 2 (from 0) is 6", 6, lambda: get(A, 3, 1, 2))
eq("row 0, column 1 is 2", 2, lambda: get(A, 3, 0, 1))
eq("the row sums are [6, 15]", [6, 15], lambda: row_sums(A, 2, 3))
eq("make_grid(2, 3)", [[0, 0, 0], [0, 0, 0]], lambda: make_grid(2, 3))


def grid_rows_are_separate():
    g = make_grid(3, 2)
    g[0][0] = 99
    return g[1][0] == 0


that("changing row 0 leaves row 1 alone", grid_rows_are_separate)
eq("brute force (first 4 items, capacity 10): best value 21", 21, lambda: knapsack_brute(VALUES[:4], WEIGHTS[:4], 10))
near("the solver also gets 21", 21, lambda: knapsack_solver(VALUES[:4], WEIGHTS[:4], 10))
that("8 items, capacity 15: both give the same answer", lambda: knapsack_brute(VALUES, WEIGHTS, 15) == knapsack_solver(VALUES, WEIGHTS, 15))
eq("🤔 guess: [[0] * 3] * 2 after changing one cell", [[99, 0, 0], [99, 0, 0]], guess_grid)
done()
