"""Lesson 6: dataclasses and enums.

minicplex's Params and Result are dataclasses (they get __init__, __repr__ and __eq__ for free); Status is an enum.
You write one of each, and meet the famous mutable-default trap on the way.
Run: python3 python/tutorial/en/run.py 06
"""
import dataclasses
import math
from dataclasses import dataclass, field
from enum import Enum

from check import lesson, eq, near, raises, that, done


class Weather(Enum):
    """Weather. Each member's value is its display name."""
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAINY = "rainy"

    def __str__(self):
        """str(Weather.RAINY) returns "rainy" (just as str(Status.OPTIMAL) returns "Optimal")."""
        raise NotImplementedError("TODO")  # ← write your code here

    def need_umbrella(self):
        """You need an umbrella only when it rains. Compare enum members with is."""
        raise NotImplementedError("TODO")  # ← write your code here


@dataclass(frozen=True)
class Point:
    """A point in the plane. frozen=True: it cannot change after creation, so it can go in a set or be a dict key."""
    x: float
    y: float

    def distance_to(self, other):
        """The straight-line distance between two points. math.hypot(dx, dy) = sqrt(dx**2 + dy**2)."""
        raise NotImplementedError("TODO")  # ← write your code here


@dataclass
class Cart:
    """A shopping cart. items is [(product name, price), ...]."""
    owner: str
    # Note: writing the next line as items: list = [] makes dataclass raise an error: every cart would share one list.
    #       field(default_factory=list) means: for every new cart, call list() to make a fresh empty list.
    items: list = field(default_factory=list)

    def add(self, name, price):
        raise NotImplementedError("TODO")  # ← write your code here

    def total(self):
        raise NotImplementedError("TODO")  # ← write your code here


def two_carts():
    a, b = Cart("Ming"), Cart("Hong")
    a.add("book", 30)
    return len(a.items), len(b.items)


def change_frozen_point():
    p = Point(1, 2)
    p.x = 5


lesson("Lesson 6: dataclasses and enums")
eq('str(Weather.RAINY) is "rainy"', "rainy", lambda: str(Weather.RAINY))
eq("rain needs an umbrella", True, lambda: Weather.RAINY.need_umbrella())
eq("sunshine does not", False, lambda: Weather.SUNNY.need_umbrella())
eq('look up a member by value: Weather("cloudy")', Weather.CLOUDY, lambda: Weather("cloudy"))
near("(0,0) to (3,4) is 5", 5, lambda: Point(0, 0).distance_to(Point(3, 4)))
that("dataclass generates ==: Point(1, 2) == Point(1, 2)", lambda: Point(1, 2) == Point(1, 2))
eq("frozen points fit in a set (duplicates count once)", 2, lambda: len({Point(1, 2), Point(1, 2), Point(0, 0)}))
raises("a frozen point cannot change", dataclasses.FrozenInstanceError, change_frozen_point)
eq("two carts do not share a list", (1, 0), two_carts)
eq("total", 42, lambda: (lambda c: (c.add("pen", 12), c.add("book", 30), c.total())[-1])(Cart("Ming")))
done()
