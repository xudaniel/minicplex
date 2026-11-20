"""Basics A4: Doing things again and again.

Run: python3 python/tutorial/en/run.py A04
"""
from check import lesson, eq, done


def sum_to(n):
    """1 + 2 + ... + n. Use for i in range(1, n + 1)."""
    raise NotImplementedError("TODO")  # ← write your code here


def days_to_save(target, per_day):
    """Saving per_day dollars a day, how many days until you have target? Use while: not enough yet, save one more day."""
    raise NotImplementedError("TODO")  # ← write your code here


def count_multiples(n, k):
    """How many numbers from 1 to n are multiples of k? (i % k == 0 means k divides i)"""
    raise NotImplementedError("TODO")  # ← write your code here


def first_power_over(limit):
    """Which power of 2 is the first to exceed limit? For limit = 100: 2**7 = 128 > 100, so return 7."""
    raise NotImplementedError("TODO")  # ← write your code here


lesson("Basics A4: Doing things again and again")
eq("1 to 10 adds up to 55", 55, lambda: sum_to(10))
eq("1 to 100 adds up to 5050", 5050, lambda: sum_to(100))
eq("1 to 0 is 0 (the loop never runs)", 0, lambda: sum_to(0))
eq("$15 a day, $100 takes 7 days", 7, lambda: days_to_save(100, 15))
eq("$20 a day, $100 takes exactly 5 days", 5, lambda: days_to_save(100, 20))
eq("there are 6 multiples of 3 in 1-20", 6, lambda: count_multiples(20, 3))
eq("2 to the 7th is the first over 100", 7, lambda: first_power_over(100))
eq("2 to the 10th is the first over 1000", 10, lambda: first_power_over(1000))
done()
