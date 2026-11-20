"""Basics A1: Make the program talk.

You only need to change the line under TODO in each function. What a "function" is comes in A5.
Run: python3 python/tutorial/en/run.py A01
"""
from check import lesson, eq, done


def hello():
    """Return a fixed sentence: Hello, Python!"""
    # TODO replace the line below with: return "Hello, Python!"
    # >>>
    return "Hello, Python!"
    # <<<


def greet(name):
    """Say hello: greet("Ming") returns "Hello, Ming!" """
    # TODO join three pieces with +: "Hello, " + name + "!"
    # >>>
    return "Hello, " + name + "!"
    # <<<


def price(item, dollars):
    """A price tag: price("apple", 2) returns "apple: $2". A number must go inside an f-string to join it with text."""
    # TODO use an f-string: f"{item}: ${dollars}"
    # >>>
    return f"{item}: ${dollars}"
    # <<<


lesson("Basics A1: Make the program talk")
print("(The program printed this line itself: Python runs from the top, one line at a time)")
eq("hello() returns Hello, Python!", "Hello, Python!", lambda: hello())
eq('greet("Ming")', "Hello, Ming!", lambda: greet("Ming"))
eq('greet("Mia")', "Hello, Mia!", lambda: greet("Mia"))
eq('price("apple", 2)', "apple: $2", lambda: price("apple", 2))
eq('price("banana", 1)', "banana: $1", lambda: price("banana", 1))
done()
