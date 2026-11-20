"""Basics A8: A small project, buying fruit.

Apples cost $2 each and score 3 points; bananas cost $1 and score 2. You have $10 and the bag holds at most 7.
What should you buy for the highest score? First try every option with loops; then see whether the
minicplex solver finds the same answer.

Run: python3 python/tutorial/en/run.py A08
"""
from check import lesson, eq, near, that, done
from minicplex import INF, Model, ObjSense, VarType, solve


def fits(apples, bananas):
    """Is there enough money, and does it fit in the bag? Money: 2 * apples + 1 * bananas <= 10; bag: apples + bananas <= 7."""
    # TODO both conditions must hold: use and
    # >>>
    return 2 * apples + bananas <= 10 and apples + bananas <= 7
    # <<<


def score(apples, bananas):
    """The score: 3 * apples + 2 * bananas."""
    # >>>
    return 3 * apples + 2 * bananas
    # <<<


def best():
    """Try every option and return the best: (apples, bananas, score).
    At most 5 apples ($10 / $2) and 10 bananas: use two nested for loops."""
    # TODO best = (0, 0, 0)
    #      for a in range(6):
    #          for b in range(11):
    #              if fits(a, b) and score(a, b) > best[2], remember (a, b, score(a, b))
    # >>>
    best = (0, 0, 0)
    for a in range(6):
        for b in range(11):
            if fits(a, b) and score(a, b) > best[2]:
                best = (a, b, score(a, b))
    return best
    # <<<


def solver_score():
    """The same problem given to minicplex (nothing to write here, just read it; lesson 1 explains it)."""
    m = Model()
    apple = m.add_var(0, INF, VarType.INTEGER, "apple")
    banana = m.add_var(0, INF, VarType.INTEGER, "banana")
    m.add_constr(2 * apple + 1 * banana <= 10, "money")
    m.add_constr(apple + banana <= 7, "bag")
    m.set_objective(3 * apple + 2 * banana, ObjSense.MAXIMIZE)
    return solve(m).objective


lesson("Basics A8: Buying fruit")
that("3 apples + 4 bananas: enough money and room", lambda: fits(3, 4))
that("5 apples + 1 banana: not enough money ($11)", lambda: not fits(5, 1))
that("0 apples + 8 bananas: the bag is too small", lambda: not fits(0, 8))
eq("3 apples + 4 bananas score 17", 17, lambda: score(3, 4))
eq("the best buy: 3 apples, 4 bananas, 17 points", (3, 4, 17), lambda: best())
near("the minicplex solver also gets 17", 17, lambda: solver_score())
print()
print("Your two loops tried 6 * 11 = 66 options. With many more variables, trying every combination is far too slow;")
print("that is where a solver comes in. Next: lesson 1, building a model with minicplex yourself.")
done()
