"""Lesson 19: How do we know it's optimal? Dual certificates and the gap.

A solver doesn't try every option. It tracks two numbers at once: the best answer found so far, and a
ceiling that no answer can beat. When the two meet, optimality is proven. In this lesson you write both
kinds of "proof" yourself: the dual certificate of a linear program and the gap of branch and bound,
then use the same idea to check a penalty-kick game.
Run: python3 python/tutorial/en/run.py 19
"""
import math

from check import lesson, eq, near, that, done
from minicplex import LinExpr, Model, ObjSense, VarType, INF, solve

# The example: maximise 5x + 4y subject to 6x + 4y <= 24, x + 2y <= 6, x, y >= 0
C = [5, 4]                 # objective coefficients
A = [[6, 4], [1, 2]]       # constraint coefficients, one row per constraint
B = [24, 6]                # right-hand sides


def demo_model(integer):
    """Build the example as a minicplex model; with integer=True, x and y must be whole numbers. (Already written.)"""
    m = Model()
    t = VarType.INTEGER if integer else VarType.CONTINUOUS
    x = m.add_var(0, INF, t, "x")
    y = m.add_var(0, INF, t, "y")
    m.add_constr(6 * x + 4 * y <= 24, "c1")
    m.add_constr(x + 2 * y <= 6, "c2")
    m.set_objective(5 * x + 4 * y, ObjSense.MAXIMIZE)
    return m


def dual_bound(b, y):
    """Weight each constraint by its shadow price y; the weighted right-hand sides add up to the ceiling: sum(b[i] * y[i]).
    Example: b = [24, 6], y = [0.75, 0.5] -> 0.75 x 24 + 0.5 x 6 = 21."""
    # >>>
    return sum(bi * yi for bi, yi in zip(b, y))
    # <<<


def dual_feasible(a, c, y, tol=1e-9):
    """Do these shadow prices count as evidence? Both conditions must hold:
    1. every y[i] >= 0 (a <= constraint may only be multiplied by a non-negative number, or the inequality flips);
    2. for every variable j, the weighted coefficient is at least the objective coefficient: sum(a[i][j] * y[i] for i) >= c[j].
    Then: objective <= weighted left-hand side <= weighted right-hand side. Allow a small tolerance tol when comparing."""
    # >>>
    if any(yi < -tol for yi in y):
        return False
    for j in range(len(c)):
        if sum(a[i][j] * y[i] for i in range(len(y))) < c[j] - tol:
            return False
    return True
    # <<<


def certify_lp(a, b, c, x, y, tol=1e-6):
    """Is x optimal? If all three hold, it's proven:
    1. x is feasible: every x[j] >= 0, and every constraint sum(a[i][j] * x[j]) <= b[i] (with tolerance tol);
    2. y is valid evidence: dual_feasible(a, c, y);
    3. the two ends meet: the objective sum(c[j] * x[j]) equals dual_bound(b, y) (math.isclose, abs_tol=tol)."""
    # >>>
    if any(xj < -tol for xj in x):
        return False
    for i in range(len(b)):
        if sum(a[i][j] * x[j] for j in range(len(x))) > b[i] + tol:
            return False
    if not dual_feasible(a, c, y):
        return False
    value = sum(cj * xj for cj, xj in zip(c, x))
    return math.isclose(value, dual_bound(b, y), abs_tol=tol)
    # <<<


def relative_gap(incumbent, bound):
    """The Gap in the log: |bound - best integer| / |best integer|. Use 1e-10 as the floor of the denominator to avoid dividing by 0.
    Example: best integer 18, bound 21 -> 3 / 18 ~ 0.1667 (the log shows 16.67%)."""
    # >>>
    return abs(bound - incumbent) / max(1e-10, abs(incumbent))
    # <<<


def proven_optimal(incumbent, bound, rel=1e-6, absolute=1e-6):
    """Have the two ends met? (Maximising) If bound - best integer <= max(absolute, rel x max(1, |best integer|)), it's proven.
    This is exactly the test in minicplex's solver.py; CPLEX's EpGap and EpAGap mean the same thing."""
    # >>>
    return bound - incumbent <= max(absolute, rel * max(1.0, abs(incumbent)))
    # <<<


def game_bounds(m, p, q):
    """In a zero-sum game, m[i][j] is the row player's payoff. The row player plays with probabilities p, the column player with q. Return two numbers:
    1. the row player's floor: what they still get when the column player picks the harshest column = min over columns j of sum(p[i] * m[i][j]);
    2. the column player's cap: the most they can lose when the row player picks the best row = max over rows i of sum(m[i][j] * q[j]).
    If floor == cap, both players are proven optimal."""
    # >>>
    rows, cols = len(m), len(m[0])
    floor = min(sum(p[i] * m[i][j] for i in range(rows)) for j in range(cols))
    cap = max(sum(m[i][j] * q[j] for j in range(cols)) for i in range(rows))
    return floor, cap
    # <<<


def guess_after_stop():
    """🤔 Guess, then run: don't run anything yet! A maximising integer program hit its time limit; the last log line reads:

        Best Integer 19    Best Bound 20    Gap 5.26%

    In what range must the true optimum lie? Write (smallest possible, largest possible) after return."""
    # >>>
    return (19, 20)
    # <<<


# ---------------------------------------------------------------- the penalty-kick game (already written)
PENALTY = [  # rows: shoot left/centre/right; columns: keeper dives left/centre/right; scoring rates (made up)
    [0.55, 0.85, 0.95],
    [0.90, 0.30, 0.90],
    [0.95, 0.85, 0.60],
]


def solve_penalty():
    """Solve the penalty kick as an LP: the shooter's probabilities p maximise the guaranteed rate v; the keeper's probabilities are the constraints' shadow prices. Return (p, q, v)."""
    m = Model()
    p = [m.add_var(0, 1, name=f"p{i}") for i in range(3)]
    v = m.add_var(-INF, INF, name="v")
    m.add_constr(sum(p, LinExpr()) == 1, "prob")
    for j in range(3):
        m.add_constr(sum((PENALTY[i][j] * p[i] for i in range(3)), LinExpr()) - v >= 0, f"keeper{j}")
    m.set_objective(v, ObjSense.MAXIMIZE)
    r = solve(m)
    return [r.value(x) for x in p], [abs(d) for d in r.duals[1:]], r.objective


def _lp():
    r = solve(demo_model(False))
    return r.x, r.duals


def _mip():
    return solve(demo_model(True))


lesson("Lesson 19: How do we know it's optimal?")
near("shadow prices 0.75 and 0.5 give a ceiling of 21", 21, lambda: dual_bound(B, [0.75, 0.5]))
that("0.75 and 0.5 are valid evidence", lambda: dual_feasible(A, C, [0.75, 0.5]))
that("0.5 and 0.5 are not: the x column gives 6x0.5 + 1x0.5 = 3.5 < 5", lambda: not dual_feasible(A, C, [0.5, 0.5]))
that("a negative shadow price is not allowed", lambda: not dual_feasible(A, C, [1.0, -0.1]))
that("the solver's answer + shadow prices: proven", lambda: certify_lp(A, B, C, *_lp()))
that("x=3, y=1 is feasible but not optimal: no proof", lambda: not certify_lp(A, B, C, [3, 1], [0.75, 0.5]))
that("x=4, y=1 is infeasible: no proof", lambda: not certify_lp(A, B, C, [4, 1], [0.75, 0.5]))
near("first log line: 18 vs 21, a gap of about 16.67%", 1 / 6, lambda: relative_gap(18, 21))
that("19 vs 20 is not proven yet", lambda: not proven_optimal(19, 20))
that("20 vs 20 is proven", lambda: proven_optimal(20, 20))
that("integer version: when the solver stops, the two ends really have met", lambda: proven_optimal(_mip().objective, _mip().best_bound))
near("the integer optimum is 20", 20, lambda: _mip().objective)
that("penalty kick: floor == cap (shooter and keeper are both optimal)",
     lambda: math.isclose(*game_bounds(PENALTY, *solve_penalty()[:2]), abs_tol=1e-6))
near("the scoring rate is about 78.1%", 0.7806, lambda: round(game_bounds(PENALTY, *solve_penalty()[:2])[0], 4))
eq("🤔 guess: the optimum's range when stopped between 19 and 20", (19, 20), guess_after_stop)
done()
