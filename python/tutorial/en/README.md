# Learn Python with minicplex

> A small Python course built on a **real project**: 8 short basics lessons for complete beginners (A1–A8), then 12 main lessons, then 7 advanced ones (13–19).
> Each lesson covers one Python topic with examples taken from the Python source of the minicplex solver, and comes with an auto-graded exercise.
> [中文版](../README.md)

Most Python tutorials use cats and dogs as examples, and when you finish you still don't know what code in a real project looks like. This course works the other way round:
it shows a piece of minicplex (a solver that really solves optimisation problems: about 2,700 lines of pure Python with comments, no dependencies), then explains the Python it uses,
and **why it's written that way**. By the end you know the syntax, and you can read a complete project.

> **🌐 Learn in your browser: [https://xudaniel.github.io/minicplex/python/en/](https://xudaniel.github.io/minicplex/python/en/)**
> Lessons, editor and auto-grading on one page. Python runs inside your browser: nothing to install, no sign-up, works on a phone; your code and progress are saved in this browser.

This Python version isn't a "simplified edition": it matches the C++ version line by line and takes exactly the same computational path on the same problem; CI checks that on more than 600 problems on every commit.
The code you read is the code that really runs.

## Who it's for

- **Never written code?** Start with Basics A1. Each lesson takes 10–20 minutes, teaches one thing, and uses everyday examples like buying fruit and counting steps.
- If you've done a little programming (any language) and know what variables, if and loops are, you can start at lesson 1.
- If you want to know how a "real Python project" is organised: modules, classes, operator overloading, dataclasses, tests...
- You don't need to know optimisation algorithms; wherever they come up they're explained in plain words. For a 5-minute introduction, read
  [How it works](../../../README.en.md#how-it-works) in the main README.

## Getting ready

**With the web version, nothing at all**: just open the link above. You can also work on your own computer (VS Code, PyCharm, ...): the exercise files are exactly the same as on the web.

All you need is Python 3.9 or newer (`python3 --version` to check; on Windows it may be `python` or `py`). No packages, no IDE.

```bash
git clone https://github.com/xudaniel/minicplex.git && cd minicplex
python3 python/tutorial/en/run.py A01     # complete beginner: run the Basics A1 exercise
python3 python/tutorial/en/run.py 01      # done some programming: run the lesson 1 exercise
```

`run.py` is itself written in Python, so it works the same on Windows, macOS and Linux. You can also run the exercise files directly in VS Code or PyCharm.

## How the exercises work

Each lesson's exercise is in [`exercises/`](exercises/), named `a01_…`, `l02_…`.
Open the file, find `TODO`, replace `raise NotImplementedError("TODO")` with your code (mind the indentation), then run:

```text
$ python3 python/tutorial/en/run.py 02
== Lesson 2: Numbers and floating-point error ==
✅ 0.1 + 0.2 and 0.3 are NOT equal under ==
✅ but they are close enough
❌ 2.5 is not whole: the condition is false
⏳ infinity is not whole (not written yet: look for TODO)
-- passed 2, wrong 1, todo 1
```

✅ is right, ❌ is wrong (it shows the expected and actual values), ⏳ is not written yet. All ✅ and the lesson is done.
Common mistakes get one extra line explaining why, for example:

```text
❌ $10 buys at most 3 items at $3: expected 3, got 3.3333333333333335
   💡 Expected a whole number but got a decimal: use // (floor division), not /.
```

**Stuck?** Ask for hints one level at a time (on the web, click **💡 Hint**):

```bash
python3 python/tutorial/en/run.py 02 --hint      # a direction for each function first
python3 python/tutorial/en/run.py 02 --hint 2    # still stuck? something close to the code
```

If you really can't get it, the answers are in [`solutions/`](solutions/); run them with `run.py 02 --solution`. Try it yourself first and compare afterwards: the answer is not the only way to write it.

Some special kinds of task: those marked **🤔 guess, then run** ask you not to run anything yet but to write your guess after `return`, then run to see whether you were right;
lesson 13 is a **🐞 bug hunt**: the code is already written but has mistakes to find and fix.

To see how much you've finished: `python3 python/tutorial/en/run.py all` prints a progress table.

## Contents

### Stage 0: Basics for complete beginners (A1–A8, 10–20 minutes each)

| Lesson | Topic | Exercise |
|---|---|---|
| [A1](lessons/a1-hello.md) | Make the program talk: `print`, strings, f-strings | greetings, prices |
| [A2](lessons/a2-variables.md) | Variables and arithmetic: `int`, `float`, `//` and `%` | totals, change, how many you can buy |
| [A3](lessons/a3-decisions.md) | Making decisions: `if / elif / else`, `and`, `or` | enough money?, free shipping over $99, grades |
| [A4](lessons/a4-loops.md) | Repeating things: `for`, `range`, `while` | 1 + … + n, days to save up |
| [A5](lessons/a5-functions.md) | Writing functions: parameters, return values, defaults | temperature conversion, `clamp`, discounts |
| [A6](lessons/a6-lists.md) | Lists: a whole row of numbers at once | a week of steps: total, best day, average |
| [A7](lessons/a7-strings.md) | Strings: indexes, slices, `split` | initials, masking a phone number |
| [A8](lessons/a8-project.md) | A small project: buying fruit | nested loops try every purchase, then check against the solver |

Run the exercises with `python3 python/tutorial/en/run.py A01` (`A1` works too). After A8 you're ready for the main course.

### Lessons 1–12: Learn Python with minicplex

| Lesson | Topic | minicplex code used | Exercise |
|---|---|---|---|
| [01](lessons/01-first-model.md) | Your first model: modules, `import`, `python -m` | `examples/basics_01_one_variable.py`, `__init__.py` | build an ice-cream model |
| [02](lessons/02-numbers.md) | Numbers and floating-point error: tolerances, `inf`, three kinds of rounding, `-0.0` | `jmath.py`, tolerances in `lp_engine.py` | write `near`, `is_integral`, `cround` |
| [03](lessons/03-lists.md) | Lists, comprehensions, `zip`, `itertools` | the flat matrix `T[i * N + j]` in `lp_engine.py` | brute-force knapsack vs the solver |
| [04](lessons/04-classes.md) | Classes and objects: `__init__`, `@property`, `__repr__` | `VarInfo`, `Model.add_var` | write a product class |
| [05](lessons/05-operators.md) | **Operator overloading** and immutable objects | `LinExpr`: how `2 * x + 3 * y <= 12` works | write a mini expression class |
| [06](lessons/06-dataclass-enum.md) | dataclass and enum, the mutable-default trap | `Params`, `Result`, `Status` | a weather enum, a frozen point, a shopping cart |
| [07](lessons/07-dicts-sets.md) | Dictionaries and sets | `Model._index`, combining like terms, why sort | build an index, combine like terms |
| [08](lessons/08-sorting-heaps.md) | Sorting, `lambda`, `heapq` | the branch-and-bound node queue, the story of stable sorting | implement the node ordering rule |
| [09](lessons/09-exceptions.md) | Exceptions, `with`, `raise … from None` | `LpParseError`, the command line's safety net | safe parsing, reading LP files |
| [10](lessons/10-text.md) | Strings, text processing, format specs | the tokenizer in `lp_reader.py`, `to_lp` | a mini tokenizer, a report |
| [11](lessons/11-testing.md) | Testing: `unittest`, random differential testing | `tests/test_solver.py`, three versions checking each other | random problems + brute-force checks |
| [12](lessons/12-project.md) | Project: a course planner | everything so far | from text to model to report |

### Advanced lessons 13–19: what real projects use every day

| Lesson | Topic | minicplex code used | Exercise |
|---|---|---|---|
| [13](lessons/13-debugging.md) | Reading errors, debugging and `assert` | the `assert` and `check_feasible` self-check in `solver.py` | 🐞 **bug hunt**: five functions that run but give wrong answers |
| [14](lessons/14-functions.md) | More about functions: `*args`, `**kwargs`, unpacking, closures | `Params(**...)`, `product(*...)` in the tests | a counter, the lambdas-in-a-loop trap |
| [15](lessons/15-decorators.md) | Decorators: what `@property` and `@dataclass` really are | decorators in `model.py` and `solver.py` | `count_calls`, `retry`, `memoize` vs `lru_cache` |
| [16](lessons/16-generators.md) | Generators and iterators: `yield`, `itertools` | `sum(... for ...)`, `itertools.product` | infinite Fibonacci, recursively generating every combination |
| [17](lessons/17-files-data.md) | Files and data: `pathlib`, CSV, JSON | encodings in `read_file`, CSV in the comparison script, JSON in `make_web.py` | CSV → choose products with a model → JSON |
| [18](lessons/18-cli-packaging.md) | Command-line programs and packaging: `argparse`, `python -m`, `pip`, virtual environments | `__main__.py`, `pyproject.toml` | a mini minicplex command line |
| [19](lessons/19-optimality.md) | How do we know it's optimal? Dual certificates, the gap, a game's floor and cap | `Result.duals`, `best_bound`, the gap test in `solver.py` | check certificates by hand, prove a penalty-kick game optimal |

Basics lessons take 10–20 minutes each; main and advanced lessons about 30–60 minutes. 01–06 are the language basics, 07–10 the standard library, 11–12 engineering practice, 13–19 advanced.

## What you'll be able to do

- Read all of minicplex's Python code ([`python/minicplex/`](../../minicplex/));
- Write a small Python application that goes "read data → model → solve → report";
- Write reproducible automated tests for your own code;
- Keep going: read [`lp_engine.py`](../../minicplex/lp_engine.py) (the simplex core), or compare with the [Java course](../../../java/tutorial/README.md) (in Chinese) to see the same algorithm in another language.

## For teachers

- Each exercise is a standalone `.py` file using only the standard library; it runs and grades itself on any machine with Python 3.9+.
- CI runs the answers on Python 3.9 and 3.13, so they always pass; the exercise files are generated from the answers by
  [`make_exercises.py`](../make_exercises.py) with `--lang en` (the part between `# >>>` and `# <<<` in an answer is blanked out;
  a "bug hunt" task adds `# ===` and a commented-out buggy version after the answer, and the exercise gets that version).
- To add a task: write the answer in `solutions/`, mark the part to blank with `# >>>` and `# <<<`, give the function two levels of hints in [`hints.py`](hints.py),
  then run `python3 python/tutorial/make_exercises.py --lang en`. CI checks that every blanked function has hints.
- The web version is generated by [`make_web.py`](../make_web.py) from the same lessons and exercises. On every push, GitHub Actions first runs all 27 lessons' answers and exercises in a real browser ([`web/test_site.py`](../web/test_site.py)), in both languages, and only publishes if they pass. The Python runtime (Pyodide) is hosted with the site, so it works even where public CDNs are blocked.
- The grading framework [`check.py`](solutions/check.py) is only about 100 lines, readable by students; exit code 0 = all right, 1 = something wrong, 3 = not finished, handy for collecting homework in bulk.
