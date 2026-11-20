# Lesson 1: Your first model

> **You learn:** modules and `import`; the ways to run a Python program; the four steps of modelling with minicplex
> **Code used:** [`examples/basics_01_one_variable.py`](../../../examples/basics_01_one_variable.py), [`minicplex/__init__.py`](../../../minicplex/__init__.py)
> **Exercise:** `python3 python/tutorial/en/run.py 01`
> **Do it online:** [open the web version, nothing to install](https://xudaniel.github.io/minicplex/python/en/#l01)

[← Basics A8](a8-project.md) · [Contents](../README.md) · Next: [Numbers and floating-point error →](02-numbers.md)

## 1. Run it first

```bash
python3 python/examples/basics_01_one_variable.py
```

```text
状态：Optimal
最多买 5 个苹果
```

(The example programs print in Chinese: 状态 means "status", and the second line says "buy at most 5 apples".)

Add `--trace` to watch the solver work step by step:

```bash
python3 python/examples/basics_01_one_variable.py --trace
```

## 2. Four steps

Open [`basics_01_one_variable.py`](../../../examples/basics_01_one_variable.py). Without the comments, this is all there is:

```python
from minicplex import *

m = Model()                                               # 1. an empty model
apples = m.add_var(0, INF, VarType.CONTINUOUS, "apples")  # 2. a variable: 0 ≤ apples < ∞
m.add_constr(2 * apples <= 10, "money")                   # 3. a limit: 2 × apples ≤ 10
m.set_objective(apples, ObjSense.MAXIMIZE)                # 4. the goal: the more apples the better
r = solve(m)
print(r.status, r.value(apples))                          # Optimal 5.0
```

Every optimisation problem has these four steps: **variables** (what to decide), **constraints** (what must not be broken), an **objective** (what counts as best), then solve.

`2 * apples <= 10` looks like maths, but `apples` is a variable object, so this line isn't comparing anything: it **builds a constraint**.
Python lets a class define for itself what `*` and `<=` mean (you'll write one in lesson 5).

## 3. Modules and import

A `.py` file is a **module**; a folder with an `__init__.py` in it is a **package**. minicplex is a package:

```text
python/minicplex/
├── __init__.py      ← runs on import minicplex; decides which names are offered
├── model.py         ← Model, Var, LinExpr, ...
├── lp_engine.py     ← the simplex method
├── solver.py        ← branch and bound, solve()
└── ...
```

Three ways to import:

```python
import minicplex                     # then write minicplex.Model()
from minicplex import Model, solve   # write Model(), solve() directly    ← recommended: name what you use
from minicplex import *              # bring in every name                ← fine in short examples, rare in real code
```

Which names `from minicplex import *` brings in is decided by the `__all__` list in [`__init__.py`](../../../minicplex/__init__.py).

## 4. Ways to run things

```bash
python3 python/examples/easy1_bakery.py         # run a file
cd python && python3 -m minicplex ../examples/bakery.lp   # -m: run a package as a program (runs its __main__.py)
pip install -e python                           # once installed, import minicplex works from any folder
```

`python3 -m minicplex` is minicplex's command-line solver: apart from the version line at the top and the timings, its output matches the C++ `./build/minicplex` character for character.

> The first line of each exercise, `from check import ...`, also adds the repository's `python/` folder to the search path, so `import minicplex` works without installing.

## 5. Common mistakes

- `ModuleNotFoundError: No module named 'minicplex'`: you ran from the wrong folder, or it isn't installed. Running exercises with `run.py` avoids this.
- Naming your own file `minicplex.py` or `random.py`: it hides the real module, and import picks up your file instead.

## 6. Your turn

Open [`exercises/l01_first_model.py`](../exercises/l01_first_model.py): an ice cream costs $3 and you have $25. How many can you buy (whole ones only)?
Build the model with the four steps above and run `python3 python/tutorial/en/run.py 01`.

## 7. Think about it

If you change the variable type from `VarType.INTEGER` to `VarType.CONTINUOUS`, what does the answer become?

<details><summary>Answer</summary>

`8.333…` (25 ÷ 3). If you may buy a third of an ice cream, all the money gets spent. With whole ones only, the answer is 8.
Requiring whole numbers makes the problem much harder: the solver first solves the "decimals allowed" version, then uses branch and bound to squeeze out a whole-number answer bit by bit.

</details>

[← Basics A8](a8-project.md) · [Contents](../README.md) · Next: [Numbers and floating-point error →](02-numbers.md)
