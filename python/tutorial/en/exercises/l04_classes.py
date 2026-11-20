"""Lesson 4: Classes and objects.

minicplex's VarInfo and Model are classes. In this lesson you write a product class: attributes, methods,
default arguments, @property and __repr__.
Run: python3 python/tutorial/en/run.py 04
"""
from check import lesson, eq, near, that, done


class Product:
    """A product: name, unit price, stock."""

    def __init__(self, name, price, stock=0):
        """stock defaults to 0. Store the three arguments as attributes of the same name: self.name, self.price, self.stock."""
        raise NotImplementedError("TODO")  # ← write your code here

    def total_value(self):
        """The value of the stock = price * stock."""
        raise NotImplementedError("TODO")  # ← write your code here

    def sell(self, n):
        """Sell n: if there is enough stock, subtract it and return True; otherwise change nothing and return False."""
        raise NotImplementedError("TODO")  # ← write your code here

    @property
    def in_stock(self):
        """Is there any stock? @property makes it read like an attribute: p.in_stock (no parentheses)."""
        raise NotImplementedError("TODO")  # ← write your code here

    def __repr__(self):
        """How the object prints: Product('apple', 2.5, stock=10). Hint: {self.name!r} adds the quotes."""
        raise NotImplementedError("TODO")  # ← write your code here


def sold_out_after():
    p = Product("yogurt", 6, 3)
    ok1, ok2, ok3 = p.sell(2), p.sell(2), p.sell(1)
    return (ok1, ok2, ok3, p.stock, p.in_stock)


lesson("Lesson 4: Classes and objects")
eq("name", "apple", lambda: Product("apple", 2.5, 10).name)
eq("stock defaults to 0", 0, lambda: Product("pear", 3).stock)
near("stock value 2.5 * 10 = 25", 25, lambda: Product("apple", 2.5, 10).total_value())
eq("sell 2, then 2 (not enough), then 1: (True, False, True, 0, False)", (True, False, True, 0, False), sold_out_after)
that("in_stock is True when there is stock", lambda: Product("apple", 2.5, 1).in_stock is True)
eq("repr", "Product('apple', 2.5, stock=10)", lambda: repr(Product("apple", 2.5, 10)))
that("each object has its own stock", lambda: (lambda a, b: (a.sell(1), a.stock, b.stock))(Product("a", 1, 5), Product("b", 1, 5))[1:] == (4, 5))
done()
