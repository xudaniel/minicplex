"""Lesson 11: Testing with random cross-checks.

How can you trust a solver? minicplex's tests (python/tests/test_solver.py) build 500 small random integer programs and
solve each one again by brute-force enumeration; both answers must agree. You build that cross-check yourself:
random problems, a brute-force solver, a comparison.
Run: python3 python/tutorial/en/run.py 11
"""
import itertools
import math
import random

from check import lesson, eq, that, done
from minicplex import LinExpr, Model, ObjSense, Status, VarType, check_feasible, eval_objective, solve


def random_model(seed):
    """Build a small problem with random.Random(seed) (the same seed always builds the same problem, so failures can be reproduced):
    3 integer variables in 0-4; 2 <= constraints with coefficients in -3..5 and right-hand sides in 2..12;
    maximise, with objective coefficients in 1..9. rng.randint(a, b) includes both a and b."""
    raise NotImplementedError("TODO")  # ← write your code here


def brute_force(m):
    """Try every integer point (each variable from its lower to its upper bound) and return the best objective among the feasible ones;
    return None if no point is feasible.
    Hint: itertools.product(*(range(int(v.lb), int(v.ub) + 1) for v in m.vars));
          check_feasible(m, point) tests feasibility; eval_objective(m, point) computes the objective."""
    raise NotImplementedError("TODO")  # ← write your code here


def agree(seed):
    """Do the solver and brute force agree? Both finding no solution counts as agreeing. Compare decimals with math.isclose."""
    raise NotImplementedError("TODO")  # ← write your code here


def _one_var_model():
    m = Model()
    x = m.add_var(0, 4, VarType.INTEGER, "x")
    m.set_objective(x, ObjSense.MAXIMIZE)
    return m


lesson("Lesson 11: Testing with random cross-checks")
that("the same seed builds the same problem", lambda: random_model(7).to_lp() == random_model(7).to_lp())
that("different seeds build different problems", lambda: random_model(7).to_lp() != random_model(8).to_lp())
eq("each problem has 3 variables and 2 constraints", (3, 2), lambda: (random_model(1).num_vars, random_model(1).num_constrs))
that("brute force: maximising x with x <= 4 gives 4", lambda: brute_force(_one_var_model()) == 4)
that("100 random problems: the solver and brute force always agree", lambda: all(agree(seed) for seed in range(100)))
done()
