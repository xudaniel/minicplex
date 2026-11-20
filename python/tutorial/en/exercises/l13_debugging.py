"""Lesson 13: Reading errors, debugging and assert.

This exercise works differently: the functions below are **already written, but they have bugs**. Run it, look at the ❌ lines,
read the messages, find the causes and fix them. The last one adds a self-check to a function with assert.
Run: python3 python/tutorial/en/run.py 13
"""
import math

from check import lesson, eq, near, raises, done


def average(nums):
    """The average. average([2, 4, 6]) should be 4."""
    # 🐞 the code below has a bug: find it and fix it
    total = 0
    for i in range(1, len(nums)):
        total += nums[i]
    return total / len(nums)


def is_leap(year):
    """Leap years: divisible by 4 but not by 100, or divisible by 400. 2000 is a leap year, 1900 is not."""
    # 🐞 the code below has a bug: find it and fix it
    return year % 4 == 0 and year % 100 != 0


def count_words(text):
    """Count the words; several spaces or a newline count as one separator."""
    # 🐞 the code below has a bug: find it and fix it
    return len(text.split(" "))


# 🐞 the code below has a bug: find it and fix it
def add_item(item, cart=[]):
    """Put item in the cart and return the cart. Without a cart argument, each call should start a fresh empty cart."""
    cart.append(item)
    return cart


def best_price(prices):
    """The cheapest product. prices is {product: price}; return (product, price)."""
    # 🐞 the code below has a bug: find it and fix it
    name = min(prices)
    return name, prices[name]


def safe_sqrt(x):
    """Square root. A negative x should not quietly give nan: fail at once with assert and the message "x must not be negative"."""
    # TODO first line: assert condition, "message"; then return math.sqrt(x)
    raise NotImplementedError("TODO")  # ← write your code here


lesson("Lesson 13: Reading errors, debugging and assert")
near("average([2, 4, 6]) is 4", 4, lambda: average([2, 4, 6]))
near("average([10]) is 10", 10, lambda: average([10]))
eq("2024 is a leap year", True, lambda: is_leap(2024))
eq("1900 is not", False, lambda: is_leap(1900))
eq("2000 is", True, lambda: is_leap(2000))
eq('"one  two  three\\nfour" has 4 words', 4, lambda: count_words("one  two  three\nfour"))
eq("first add_item: ['book']", ["book"], lambda: add_item("book"))
eq("the second add_item gets a fresh cart too: ['pen']", ["pen"], lambda: add_item("pen"))
eq("bananas are cheapest", ("banana", 3), lambda: best_price({"apple": 5, "banana": 3, "pear": 4}))
near("safe_sqrt(9) is 3", 3, lambda: safe_sqrt(9))
raises("safe_sqrt(-1) raises AssertionError", AssertionError, lambda: safe_sqrt(-1))
done()
