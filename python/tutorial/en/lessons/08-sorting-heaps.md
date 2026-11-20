# Lesson 8: Sorting, lambda and heaps

> **You learn:** `sorted` and `key=`; `lambda`; how tuples compare; stable sorting; `heapq` (priority queues)
> **Code used:** the node queue `push` and the strong-branching candidate sort in [`solver.py`](../../../minicplex/solver.py), the cut sort in [`lp_engine.py`](../../../minicplex/lp_engine.py)
> **Exercise:** `python3 python/tutorial/en/run.py 08`
> **Do it online:** [open the web version, nothing to install](https://xudaniel.github.io/minicplex/python/en/#l08)

[← Dictionaries and sets](07-dicts-sets.md) · [Contents](../README.md) · Next: [Exceptions →](09-exceptions.md)

## 1. key= and lambda

```python
sorted([3, -5, 2], key=abs)                         # [2, 3, -5]: by absolute value
sorted(students, key=lambda s: s[1])                # by score, low to high
sorted(students, key=lambda s: (-s[1], s[0]))       # score high to low, ties by name
```

`lambda s: s[1]` is a small function without a name, the same as `def f(s): return s[1]`. For a simple function used once, a lambda is the handiest.

**Tuples compare in order**: first items first; if equal, the second items; and so on. So a "multi-level sort" just returns a tuple. Negate the item you want in reverse order.

## 2. Stable sorting

Python's sort is **stable**: items with equal keys keep their original order. The solver relies on that (cuts in [`lp_engine.py`](../../../minicplex/lp_engine.py)):

```python
cands.sort(key=lambda cd: -cd[2])  # stable sort: equally strong cuts keep their original order
```

When two cuts are equally strong, the one that comes first is the one added, which changes the whole search that follows. Porting to Java ran straight into this: the staff-rostering example has two equally strong cuts,
and C++'s `std::sort` (**not** stable) and Java's stable sort picked different ones. Same optimum, but 8 nodes in one and 11 in the other; another C++ standard library could change it again.
Now all three versions use a stable sort, so every step is the same. (More in the main README's [Same answers, same path](../../../../README.en.md#same-answers-same-path).)

## 3. Heaps: always take out the best first

Branch and bound has a pile of nodes waiting, and each time it needs the one with the "smallest bound". Sorting every time is too slow, so minicplex uses a **heap** ([`solver.py`](../../../minicplex/solver.py)):

```python
def push(self, node):
    # same as the Java comparator: smaller bound first; on equal bounds deeper first; then newer first
    heapq.heappush(self.open, (node.bound, jmath.neg_zero_first(node.bound), -node.depth, -node.seq, node))

self.cur = heapq.heappop(self.open)[-1]    # take out the smallest; the tuple's last item is the node
self.open[0][0]                           # just look at the smallest bound without taking it out
```

- `heapq` keeps an ordinary list arranged so that "the smallest is always at `[0]`"; pushing and popping take only O(log n) steps.
- What goes in is a **tuple**, so the order is the tuple rule from section 1. Negating depth and sequence number turns them into "larger comes out first".
- Why `-node.seq` (the sequence number)? If all earlier items tie, Python goes on to compare the `node` objects at the end, and nodes don't define `<`, so that would raise `TypeError`. Sequence numbers are all different, so the comparison is decided before that, and the order is completely fixed.
- `neg_zero_first` puts `-0.0` before `0.0`, as Java's `Double.compare` does: lesson 2's negative zero again.

## 4. Common mistakes

- `list.sort()` sorts in place and returns `None`: `x = a.sort()` gives `None`. For a new list use `sorted(a)`.
- Putting objects that can't be compared into a heap without a sequence number as a tie-breaker.
- Thinking `heapq` is a "max-heap": it always pops the smallest. For the largest, negate.

## 5. Your turn

Open [`exercises/l08_sorting_heaps.py`](../exercises/l08_sorting_heaps.py): write the node sort key, pop with a heap, rank exam scores, and find the most common words. Run `python3 python/tutorial/en/run.py 08`.

## 6. Think about it

Why does branch and bound take "deeper first when bounds are equal"?

<details><summary>Answer</summary>

A deeper node has fixed more integer variables, so it's closer to a complete integer solution. Finding any integer solution early (even not the best) lets its objective value prune many nodes at once.
This is "depth-first to find solutions, best-first to prove optimality", the idea behind almost every MIP solver.

</details>

[← Dictionaries and sets](07-dicts-sets.md) · [Contents](../README.md) · Next: [Exceptions →](09-exceptions.md)
