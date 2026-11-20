# Lesson 3: Lists, loops and comprehensions

> **You learn:** a 2-D table in a 1-D list; slices; comprehensions and generator expressions; `zip`, `enumerate`, `itertools.product`; the `[[0] * n] * m` trap
> **Code used:** `T[i * N + j]` and `_pivot` in [`lp_engine.py`](../../../minicplex/lp_engine.py), [`basics_08_min_max.py`](../../../examples/basics_08_min_max.py)
> **Exercise:** `python3 python/tutorial/en/run.py 03`
> **Do it online:** [open the web version, nothing to install](https://xudaniel.github.io/minicplex/python/en/#l03)

[← Numbers and floating-point error](02-numbers.md) · [Contents](../README.md) · Next: [Classes and objects →](04-classes.md)

## 1. Flattening a table into one row

The simplex tableau is a table with m rows and N columns. minicplex doesn't use a "list of lists"; it stores a 1-D list of length m × N ([`lp_engine.py`](../../../minicplex/lp_engine.py)):

```python
T = [0.0] * (m * N)
for i in range(m):
    base = i * N              # row i starts here
    for j in range(n):
        T[base + j] = -A[i * n + j]
```

Row i, column j is at `T[i * N + j]`. The other way round, number k is in row `k // N`, column `k % N` (the floor division and remainder from A2).

Why store it like this? There's only one list, so a copy is just `list(T)`; and the Java and C++ versions store it the same way, so the three can be compared line by line.

## 2. Comprehensions: a list in one line

```python
squares = [x * x for x in range(5)]                    # [0, 1, 4, 9, 16]
evens = [x for x in nums if x % 2 == 0]                 # with a condition
names = [v.name for v in M.vars]                        # you'll see this all over minicplex
grid = [[0] * n for _ in range(m)]                      # a 2-D list with m rows and n columns
```

With round brackets it's a **generator expression**: instead of building the whole list first, it produces one value at a time and saves memory. It's most common as the argument to `sum` or `max`:

```python
sum(hours[t] * give[t][p] for t in range(tasks))        # basics_08_min_max.py: person p's workload
```

## 3. zip, enumerate, itertools.product

```python
for w, t in zip(weights, take):        # walk two lists in pairs
for i, name in enumerate(names):       # get the index and the value together
for pick in itertools.product([0, 1], repeat=3):   # (0,0,0), (0,0,1), …, (1,1,1): every 0/1 combination
```

## 4. A classic trap

```python
grid = [[0] * 3] * 2      # looks like 2 rows, 3 columns
grid[0][0] = 99
print(grid)               # [[99, 0, 0], [99, 0, 0]]  ← both rows changed!
```

`* 2` copies "a reference to the same inner list", so both rows are really one list (the alias from A6).
The right way is a comprehension: `[[0] * 3 for _ in range(2)]` builds a new inner list each round.
`[0] * 3` itself is fine: numbers can't be changed, so sharing them does no harm.

## 5. Speed: moving look-ups out of the loop

`_pivot` is the hottest spot in the whole solver (every pivot updates the entire table):

```python
prow = [(j, T[pr + j]) for j in nz]     # first pull out the nonzero columns and values of the pivot row
for i in range(self.m):
    ...
    for j, t in prow:                   # each row only visits those nonzero columns
        T[pi + j] -= f * t
```

In Python, both the number of loop rounds and "how many look-ups happen per round" matter. Putting the values you need into a local list first is noticeably faster than recomputing `T[pr + j]` inside the loop.

## 6. Your turn

Open [`exercises/l03_lists.py`](../exercises/l03_lists.py): look-ups and row sums in a flattened matrix, a correct 2-D list, a brute-force knapsack, and finally the same knapsack with the solver, checking that both agree. Run `python3 python/tutorial/en/run.py 03`.

The last one is a **🤔 guess, then run**: don't run anything yet. Read the few lines of code in the task, write your guess after `return`, then run and see whether you were right. A wrong guess is fine; working out why is the point.

## 7. Think about it

The brute-force knapsack tries 2ⁿ combinations. That's 256 for n = 8. What about n = 40?

<details><summary>Answer</summary>

2⁴⁰ ≈ 1.1 trillion. At a million per second that's nearly two weeks. With branch and bound, the solver usually looks at tens to thousands of nodes.
That's why brute force is only good for **checking** a solver (lesson 11), not for solving problems.

</details>

[← Numbers and floating-point error](02-numbers.md) · [Contents](../README.md) · Next: [Classes and objects →](04-classes.md)
