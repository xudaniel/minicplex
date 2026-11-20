"""Lesson 8: Sorting, lambdas and heaps.

Branch and bound keeps taking the "best" node out of a big pile. minicplex keeps the nodes in a heapq (heap) and writes the
ordering as a tuple (bound, -depth, -seq): smaller bound first, deeper first on a tie, newer first on a further tie.
Run: python3 python/tutorial/en/run.py 08
"""
import heapq
from dataclasses import dataclass

from check import lesson, eq, done


@dataclass
class Node:
    name: str
    bound: float  # bound: smaller is better
    depth: int    # depth: deeper is better (finds whole-number solutions sooner)
    seq: int      # insertion number: newer is better


def node_key(node):
    """Return the sort key tuple so the "best" node comes first. Tuples compare item by item: first, then second on a tie..."""
    raise NotImplementedError("TODO")  # ← write your code here


def pop_order(nodes):
    """Push every node onto a heap, pop them one by one, and return the names in popping order.
    heapq.heappush(heap, (node_key(n), n.name)); heapq.heappop(heap) pops the smallest."""
    raise NotImplementedError("TODO")  # ← write your code here


def rank(students):
    """students is [(name, score), ...]. Higher scores first; equal scores by name.
    sorted(..., key=lambda s: ...): negate the score to sort from high to low."""
    raise NotImplementedError("TODO")  # ← write your code here


def top_k(words, k):
    """The k most frequent words (ties broken alphabetically). Count with a dict first, then sort and take k."""
    raise NotImplementedError("TODO")  # ← write your code here


NODES = [Node("A", 5.0, 1, 1), Node("B", 3.0, 1, 2), Node("C", 3.0, 4, 3), Node("D", 3.0, 4, 4), Node("E", 9.0, 9, 5)]

lesson("Lesson 8: Sorting, lambdas and heaps")
eq("smaller bound comes out first", True, lambda: node_key(NODES[1]) < node_key(NODES[0]))
eq("equal bound: deeper first", True, lambda: node_key(NODES[2]) < node_key(NODES[1]))
eq("equal bound and depth: newer first", True, lambda: node_key(NODES[3]) < node_key(NODES[2]))
eq("heap pop order", ["D", "C", "B", "A", "E"], lambda: pop_order(NODES))
eq("ranking: higher score first, ties by name", ["Amy", "Bob", "Cara"], lambda: rank([("Bob", 90), ("Cara", 85), ("Amy", 90)]))
eq("the 2 most frequent words", ["the", "a"], lambda: top_k("the cat and the dog and a the a".split(), 2))
done()
