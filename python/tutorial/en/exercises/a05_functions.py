"""Basics A5: Writing your own functions.

Run: python3 python/tutorial/en/run.py A05
"""
from check import lesson, eq, near, done


def bigger(a, b):
    """Return the bigger of a and b (write it with if, without the built-in max)."""
    raise NotImplementedError("TODO")  # ← write your code here


def c_to_f(c):
    """Celsius to Fahrenheit: F = C * 9 / 5 + 32."""
    raise NotImplementedError("TODO")  # ← write your code here


def clamp(x, lo, hi):
    """Keep x inside [lo, hi]: below lo return lo, above hi return hi, otherwise return x."""
    raise NotImplementedError("TODO")  # ← write your code here


def discount(price, percent=10):
    """The price after a discount. Without a percent, take 10% off."""
    raise NotImplementedError("TODO")  # ← write your code here


lesson("Basics A5: Writing your own functions")
eq("bigger(3, 8) is 8", 8, lambda: bigger(3, 8))
eq("bigger(-1, -5) is -1", -1, lambda: bigger(-1, -5))
near("0 °C = 32 °F", 32, lambda: c_to_f(0))
near("37 °C = 98.6 °F", 98.6, lambda: c_to_f(37))
eq("clamp(15, 0, 10) is 10", 10, lambda: clamp(15, 0, 10))
eq("clamp(-3, 0, 10) is 0", 0, lambda: clamp(-3, 0, 10))
eq("clamp(7, 0, 10) is 7", 7, lambda: clamp(7, 0, 10))
near("$200 with the default 10% off: $180", 180, lambda: discount(200))
near("$200 with 25% off: $150", 150, lambda: discount(200, 25))
near("you can name the argument: discount(80, percent=50)", 40, lambda: discount(80, percent=50))
done()
