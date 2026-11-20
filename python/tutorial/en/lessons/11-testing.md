# Lesson 11: Testing against a second opinion

> **You learn:** `unittest`; reproducible random numbers with `random.Random(seed)`; brute force as the "answer key"; differential testing; `itertools.product`; `math.isclose`
> **Code used:** [`tests/test_solver.py`](../../../tests/test_solver.py), [`tools/compare_java_cpp.py`](../../../../tools/compare_java_cpp.py)
> **Exercise:** `python3 python/tutorial/en/run.py 11`
> **Do it online:** [open the web version, nothing to install](https://xudaniel.github.io/minicplex/python/en/#l11)

[← Strings and text processing](10-text.md) · [Contents](../README.md) · Next: [Project: a course planner →](12-project.md)

## 1. How can you trust a solver?

Check a few problems worked by hand? Far too few. minicplex uses **differential testing**: generate hundreds of small random problems, solve each one again with a dumb but completely reliable method (brute force), and demand the same answer.

```python
def test_random_ips(self, instances=500):
    rng = random.Random(12345)
    for t in range(instances):
        ...                               # build a random problem
        best = math.nan                   # brute force
        for pt in itertools.product(*(range(int(v.lb), U + 1) for v in M.vars)):
            ...
        for P in (Params(...), Params(...), Params(...)):   # all three parameter sets must be right
            r = solve(M, P)
            ...
```

Brute force only handles tiny problems (3 or 4 variables), but tiny problems already cover most code paths: infeasible, unbounded, branching, cutting planes...
These tests live in [`tests/test_solver.py`](../../../tests/test_solver.py); run them with:

```bash
python3 -m unittest discover -s python/tests -v
```

## 2. Random, but reproducible

```python
rng = random.Random(12345)   # your own random generator with a fixed seed
rng.randint(-5, 5)           # every run gets the same sequence of "random" numbers
```

When a test fails, you must be able to rebuild exactly that problem, or you can't debug it. So **always seed your random numbers**, and use your own `random.Random` object
rather than the global `random.randint` (other code uses that too and would scramble the sequence).

## 3. What unittest looks like

```python
import unittest

class KnownAnswers(unittest.TestCase):
    def test_classic_lp(self):
        ...
        r = solve(m)
        self.assertEqual(r.status, Status.OPTIMAL)
        self.assertTrue(near(r.objective, 36))

if __name__ == "__main__":
    unittest.main()
```

The class inherits from `unittest.TestCase`, and each method starting with `test_` is a test. `assertEqual`, `assertTrue` and `assertRaises` print the expected and actual values when they fail.
It's part of the standard library, nothing to install. (Many projects use the third-party `pytest`, which is shorter to write; the idea is the same.)

## 4. A bigger second opinion: three versions check each other

Brute force covers small problems; what about big ones? minicplex has C++, Java and Python versions, ported line by line, and on the same problem they should take **exactly the same** path:
the same number of branch nodes and the same number of simplex iterations. On every commit, CI generates 300 problems with a fresh random seed, solves them in all three versions, and compares the results with
[`compare_java_cpp.py`](../../../../tools/compare_java_cpp.py):

```bash
./build/minicplex_bench fuzz --quiet --csv cpp.csv
(cd python && python3 -m minicplex.bench ../fuzz --quiet --csv ../py.csv)
python3 tools/compare_java_cpp.py cpp.csv py.csv --strict --label Python
```

The last command reports how many of the 300 models agree on status and objective, and how many agree on node and iteration counts; CI requires 300/300 for both.
Any difference in an algorithmic detail (an unstable sort, a different rounding rule, `-0.0`...) makes the node counts disagree, and CI turns red at once.
All the "fussy" details in earlier lessons were forced on us by this test.

## 5. Your turn

Open [`exercises/l11_testing.py`](../exercises/l11_testing.py): write a function that builds a problem from a seed, a brute-force solver, and then check minicplex against 100 random problems. Run `python3 python/tutorial/en/run.py 11`.

## 6. Think about it

What if the brute force itself is wrong?

<details><summary>Answer</summary>

The two disagree, the test fails, you investigate, and find the brute force was wrong: that's a good outcome too. Differential testing doesn't need either side to be "certainly right"; it only needs two **independently** written methods not to be wrong in exactly the same way.
So keep the brute force as simple as possible, simple enough to see at a glance whether it's right. The exercise also checks the brute force itself on a problem whose answer is obvious (maximise x, x ≤ 4).

</details>

[← Strings and text processing](10-text.md) · [Contents](../README.md) · Next: [Project: a course planner →](12-project.md)
