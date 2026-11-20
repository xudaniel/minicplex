"""Basics A3: Making decisions.

Run: python3 python/tutorial/en/run.py A03
"""
from check import lesson, eq, done


def enough(money, cost):
    """Is the money enough? Return True if it is, False if it is not."""
    # >>>
    return money >= cost
    # <<<


def shipping(order_total):
    """Free shipping (0) from $99 up; below $99 shipping costs $10."""
    # TODO use if / else
    # >>>
    if order_total >= 99:
        return 0
    else:
        return 10
    # <<<


def grade(score):
    """90 or more "excellent", 75 or more "good", 60 or more "pass", otherwise "fail"."""
    # TODO use if / elif / else, checking from the top down
    # >>>
    if score >= 90:
        return "excellent"
    elif score >= 75:
        return "good"
    elif score >= 60:
        return "pass"
    else:
        return "fail"
    # <<<


def can_ride(age, height):
    """Roller coaster: at least 120 cm tall and aged 8 to 60 (8 and 60 included)."""
    # TODO `and` means "both"; Python lets you write 8 <= age <= 60 directly
    # >>>
    return height >= 120 and 8 <= age <= 60
    # <<<


lesson("Basics A3: Making decisions")
eq("$10 for something at $8: enough", True, lambda: enough(10, 8))
eq("$10 for something at $12: not enough", False, lambda: enough(10, 12))
eq("exactly $10 for $10: enough", True, lambda: enough(10, 10))
eq("$120 order: free shipping", 0, lambda: shipping(120))
eq("exactly $99: also free", 0, lambda: shipping(99))
eq("$98.50 order: $10 shipping", 10, lambda: shipping(98.5))
eq("95 points", "excellent", lambda: grade(95))
eq("75 points", "good", lambda: grade(75))
eq("60 points", "pass", lambda: grade(60))
eq("59 points", "fail", lambda: grade(59))
eq("10 years, 130 cm: can ride", True, lambda: can_ride(10, 130))
eq("6 years, 130 cm: too young", False, lambda: can_ride(6, 130))
eq("30 years, 110 cm: too short", False, lambda: can_ride(30, 110))
done()
