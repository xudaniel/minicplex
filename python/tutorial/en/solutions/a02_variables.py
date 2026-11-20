"""Basics A2: Variables and arithmetic.

Run: python3 python/tutorial/en/run.py A02
"""
from check import lesson, eq, near, done


def total(price, count):
    """Buying count items at price dollars each: how much in total?"""
    # >>>
    return price * count
    # <<<


def change(paid, cost):
    """You paid paid dollars for something that costs cost: how much change?"""
    # >>>
    return paid - cost
    # <<<


def how_many(money, price):
    """How many items at price dollars can money dollars buy? It must be a whole number: use // (floor division), not /."""
    # >>>
    return money // price
    # <<<


def leftover(money, price):
    """After buying as many as you can, how much money is left? Use % (remainder)."""
    # >>>
    return money % price
    # <<<


def average(a, b, c):
    """The average of three numbers."""
    # >>>
    return (a + b + c) / 3
    # <<<


def guess_floor_div():
    """🤔 Guess, then run: don't run it yet! Read the line below, guess the result, write your guess after return,
    then run and see if you were right.

        -7 // 2
    """
    # >>>
    return -4
    # <<<


lesson("Basics A2: Variables and arithmetic")
eq("3 notebooks at $4: $12", 12, lambda: total(4, 3))
near("2 bubble teas at $6.50: $13", 13.0, lambda: total(6.5, 2))
near("pay $20 for something at $13.50: $6.50 change", 6.5, lambda: change(20, 13.5))
eq("$10 buys at most 3 items at $3", 3, lambda: how_many(10, 3))
eq("with $1 left", 1, lambda: leftover(10, 3))
eq("$7 at $2 each: 3 items, $1 left", (3, 1), lambda: (how_many(7, 2), leftover(7, 2)))
near("the average of 80, 90 and 95 is 88.33...", 88.333333, lambda: average(80, 90, 95))
eq("🤔 guess: -7 // 2", -7 // 2, guess_floor_div)
done()
