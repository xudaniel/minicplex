# Lesson 7: Dictionaries and sets

> **You learn:** adding, removing and looking up in a `dict`; `in`, `get`; dictionary order; sorting by key; `set` for de-duplication and intersection; `Counter` and `defaultdict`
> **Code used:** `Model._index` and `_merge`, `Constraint.make` in [`model.py`](../../../minicplex/model.py)
> **Exercise:** `python3 python/tutorial/en/run.py 07`
> **Do it online:** [open the web version, nothing to install](https://xudaniel.github.io/minicplex/python/en/#l07)

[← dataclass and enum](06-dataclass-enum.md) · [Contents](../README.md) · Next: [Sorting, lambda and heaps →](08-sorting-heaps.md)

## 1. Name → index: a dictionary

When reading an LP file, every variable name met has to be turned into "which variable is this". Searching a list one by one is too slow, so minicplex uses a dictionary ([`model.py`](../../../minicplex/model.py)):

```python
self._index = {}                       # {variable name: index}

def find_var(self, name):
    return self._index.get(name, -1)   # -1 when missing, no error
```

```python
d = {"x": 0, "y": 1}
d["z"] = 2          # add an entry
d["x"]              # 0
d["w"]              # ✗ KeyError
d.get("w", -1)      # -1
"x" in d            # True   ← "is this key there?" is very fast (however big the dict)
del d["y"]
for k, v in d.items(): ...
```

## 2. Combining like terms

In `2x + 3y - 2x`, `x` appears twice. An expression is stored as `{variable index: coefficient}`, and coefficients for the same key must be added up:

```python
def _merge(terms, k, v):
    """Java's terms.merge(k, v, Double::sum): add if present, otherwise just store."""
    terms[k] = terms[k] + v if k in terms else v
```

Why not the shorter `terms.get(k, 0.0) + v`? Because `0.0 + (-0.0)` is `+0.0`, which loses the sign of negative zero (lesson 2).
To match the C++ and Java versions exactly, even that matters. In the exercise you needn't be so strict: `get` is fine.

Terms that add up to 0 are dropped, which is what building a constraint does:

```python
for k in sorted(d.terms):
    if d.terms[k] != 0.0:
        c.coefs[k] = d.terms[k]
```

## 3. Dictionary order

Since Python 3.7, dictionaries are guaranteed to iterate in **insertion order**. But minicplex needs "by variable index, smallest first",
because the result of adding decimals depends on the order (`(a + b) + c` is not always `a + (b + c)`), so all three versions must add in the same order.
So wherever values are summed, minicplex first does `sorted(terms)`, or sorts when storing: `dict(sorted(d.items()))`.

## 4. Sets: only "is it there?"

```python
seen = set()
seen.add("x")
"x" in seen               # True, as fast as a dict
{1, 2, 5} & {2, 3, 5}     # {2, 5}  intersection
{1, 2} | {2, 3}           # {1, 2, 3}  union
{1, 2, 3} - {2}           # {1, 3}  difference
set(["b", "a", "b"])      # {'a', 'b'}  de-duplicated (but the order is gone)
```

## 5. Two handy tools

```python
from collections import Counter, defaultdict
Counter("the cat and the dog".split()).most_common(1)   # [('the', 2)]
groups = defaultdict(list)       # a missing key gets an empty list automatically
groups["Mon"].append("Python")
```

## 6. Your turn

Open [`exercises/l07_dicts_sets.py`](../exercises/l07_dicts_sets.py): build a name index (an error on duplicates), combine like terms, de-duplicate keeping order, and intersect. Run `python3 python/tutorial/en/run.py 07`.

## 7. Think about it

Can a list `[x, y]` be a dictionary key? What about a tuple `(x, y)`?

<details><summary>Answer</summary>

A list can't (`TypeError: unhashable type: 'list'`); a tuple can. A dictionary computes a "hash" of each key for fast lookup, and the key must not change after it's stored,
so only unchangeable things (numbers, strings, tuples, frozen dataclasses) can be keys. Lesson 6's `Point` has `frozen=True` precisely so it can go into a set.

</details>

[← dataclass and enum](06-dataclass-enum.md) · [Contents](../README.md) · Next: [Sorting, lambda and heaps →](08-sorting-heaps.md)
