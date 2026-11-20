"""Basics A6: Lists, a row of values at once.

Run: python3 python/tutorial/en/run.py A06
"""
from check import lesson, eq, near, done

WEEK = [8200, 6500, 12000, 4300, 9100, 15000, 7600]  # steps walked on each day of a week


def total(steps):
    """Total steps for the week. Add them up with a for loop (without the built-in sum for now)."""
    raise NotImplementedError("TODO")  # ← write your code here


def most(steps):
    """The most steps in one day. Assume the first is the largest, then compare one by one."""
    raise NotImplementedError("TODO")  # ← write your code here


def average(steps):
    """Average steps per day. len(steps) is the length of the list."""
    raise NotImplementedError("TODO")  # ← write your code here


def days_over(steps, goal):
    """On how many days did you reach goal steps (greater than or equal)?"""
    raise NotImplementedError("TODO")  # ← write your code here


def doubled(nums):
    """Return a new list with every number doubled. Start with [] and .append() each value."""
    raise NotImplementedError("TODO")  # ← write your code here


def guess_alias():
    """🤔 Guess, then run: don't run it yet! Read the lines below, guess the result, write your guess after return,
    then run and see if you were right.

        a = [1, 2]
        b = a
        b.append(3)
        what is a now?
    """
    raise NotImplementedError("TODO")  # ← write your code here


lesson("Basics A6: Lists")
eq("62700 steps in the week", 62700, lambda: total(WEEK))
eq("the best day: 15000 steps", 15000, lambda: most(WEEK))
eq("finds the largest even when all are negative", -2, lambda: most([-5, -2, -9]))
near("about 8957 steps a day", 62700 / 7, lambda: average(WEEK))
eq("4 days with at least 8000 steps", 4, lambda: days_over(WEEK, 8000))
eq("doubled([1, 2, 3]) is [2, 4, 6]", [2, 4, 6], lambda: doubled([1, 2, 3]))
eq("doubled([]) is []", [], lambda: doubled([]))
eq("🤔 guess: after b = a, change b: what is a", [1, 2, 3], guess_alias)
done()
