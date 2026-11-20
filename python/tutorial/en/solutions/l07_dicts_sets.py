"""Lesson 7: Dictionaries and sets.

Model looks up a variable's number by name in the dict _index; LinExpr stores {variable number: coefficient} and adds the
coefficients when a variable appears twice. You do both yourself, then use sets to remove duplicates and test membership.
Run: python3 python/tutorial/en/run.py 07
"""
from check import lesson, eq, raises, done


def build_index(names):
    """A name -> position dict: ["x", "y"] -> {"x": 0, "y": 1}. Raise ValueError on a duplicate name (Model.add_var does too).
    Hint: for i, name in enumerate(names); `name in index` tests whether it is there."""
    # >>>
    index = {}
    for i, name in enumerate(names):
        if name in index:
            raise ValueError(f"duplicate variable name: {name}")
        index[name] = i
    return index
    # <<<


def merge_terms(pairs):
    """Combine like terms: [("x", 2), ("y", 3), ("x", -2), ("z", 1)] -> {"y": 3, "z": 1}.
    Add the coefficients, drop terms that end up 0, and sort by name (minicplex sorts by number so every run adds in the same order).
    Hint: d.get(k, 0) gives 0 when k is missing; dict(sorted(d.items())) gives a sorted dict."""
    # >>>
    d = {}
    for name, coef in pairs:
        d[name] = d.get(name, 0) + coef
    return {k: v for k, v in sorted(d.items()) if v != 0}
    # <<<


def first_unique(words):
    """Remove duplicates but keep first-seen order: ["b", "a", "b", "c", "a"] -> ["b", "a", "c"].
    Remember what you have seen in a set (membership tests on a set are very fast)."""
    # >>>
    seen, out = set(), []
    for w in words:
        if w not in seen:
            seen.add(w)
            out.append(w)
    return out
    # <<<


def common_free_days(a, b):
    """The days both people are free, as a sorted list. & on sets is intersection."""
    # >>>
    return sorted(set(a) & set(b))
    # <<<


lesson("Lesson 7: Dictionaries and sets")
eq('build_index(["x", "y", "z"])', {"x": 0, "y": 1, "z": 2}, lambda: build_index(["x", "y", "z"]))
raises("a duplicate name raises ValueError", ValueError, lambda: build_index(["x", "y", "x"]))
eq("combine like terms, drop zeros", {"y": 3, "z": 1}, lambda: merge_terms([("x", 2), ("y", 3), ("x", -2), ("z", 1)]))
eq("the result is sorted by name", ["a", "b", "c"], lambda: list(merge_terms([("c", 1), ("a", 1), ("b", 1)])))
eq("deduplicate, keeping order", ["b", "a", "c"], lambda: first_unique(["b", "a", "b", "c", "a"]))
eq("days both are free", [2, 5], lambda: common_free_days([1, 2, 5, 6], [5, 2, 3]))
done()
