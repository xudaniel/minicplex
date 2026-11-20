# Lesson 13: Reading errors, debugging and assert

> **You learn:** reading a traceback from the bottom up; what the common exceptions mean; finding bugs with print and breakpoint(); adding "self-checks" with assert
> **Code used:** the `assert` and `check_feasible` in [`solver.py`](../../../minicplex/solver.py), how [`__main__.py`](../../../minicplex/__main__.py) reports errors
> **Exercise:** `python3 python/tutorial/en/run.py 13` (this lesson is a "bug hunt": the code is already written, but wrong)
> **Do it online:** [open the web version, nothing to install](https://xudaniel.github.io/minicplex/python/en/#l13)

[← Project: a course planner](12-project.md) · [Contents](../README.md) · Next: [More about functions →](14-functions.md)

## 1. Tracebacks: read from the bottom up

When a program fails, Python prints a **traceback** (the call stack). Beginners often find it scary, but it's the best clue you have:

```text
Traceback (most recent call last):
  File "plan.py", line 12, in <module>
    print(report(load("menu.txt")))
  File "plan.py", line 8, in report
    return "Total: " + total
TypeError: can only concatenate str (not "float") to str
```

- The **last line** matters most: the kind of error (`TypeError`) and why (a string can't be `+`-ed with a float).
- The line above it is **where it happened**: line 8 of `plan.py`, in the function `report`, which reads `return "Total: " + total`.
- Further up is "who called it": line 12 called `report`. All the way up is how the program got here, step by step.

So read a traceback like this: **the last line tells you what went wrong; the line above tells you where**.

## 2. The common errors

| Error | Usually because |
|---|---|
| `SyntaxError` / `IndentationError` | unmatched brackets, a missing colon, uneven indentation, curly quotes. Not a single line has run yet |
| `NameError` | a misspelt name, or used before it was defined |
| `TypeError` | the wrong type: text + number, the wrong number of arguments, calling a method on `None` |
| `AttributeError: 'NoneType' object has no attribute ...` | a function forgot to `return`, so you got `None` |
| `IndexError` / `KeyError` | an index out of range / a key not in the dictionary |
| `ValueError` | the right type but a bad value: `int("abc")`, `math.sqrt(-1)` |

When an exercise fails in the web version, it tells you the line, the error, and its usual cause.

## 3. The hardest bugs don't raise errors

The errors above at least make themselves known. The nastiest bugs are when **the program runs fine but the answer is wrong**: a number left out of a sum, a condition the wrong way round, two variables sharing one list... This lesson's exercise is full of them.

How to find them:

1. **Find the smallest example whose answer you know.** `average([2, 4, 6])` should be 4 but you get 3.33: good, the problem is in these few lines.
2. **Print the intermediate results**: `print(i, total)` inside the loop, and check each value is what you think it is.
3. **Step through with a debugger**: put a line `breakpoint()` in your code and, when run on your own computer, the program stops there; type `p total` to see a variable, `n` for the next step, `c` to continue. Clicking left of a line number in VS Code or PyCharm sets a breakpoint the same way. (The web version has no debugger; use print.)

## 4. Mutable defaults: a classic silent bug

```python
def add_item(item, cart=[]):
    cart.append(item)
    return cart

add_item("book")   # ['book']
add_item("pen")    # ['book', 'pen']   ← huh?
```

The default `[]` is created **once**, when the function is defined, and every later call gets that same list. Lesson 6 showed another face of it in dataclasses. The right way:

```python
def add_item(item, cart=None):
    if cart is None:
        cart = []
```

## 5. assert: make mistakes show up early

```python
assert x >= 0, "x must not be negative"
```

When the condition is false it raises `AssertionError` at once, with your message. Its job is to **write down "what I believe must be true" and have the program check it for you**.
The earlier a mistake shows up, the easier it is to find: `math.sqrt(-1)` raising an error is fine, but quietly producing a `nan` can surface as a baffling result somewhere else much later.

minicplex has them too: the branch-and-bound main loop contains `assert cur is not None`. A bigger "self-check" is `check_feasible`:
every time the solver finds an integer solution, it re-checks every constraint against the original model (`try_incumbent` in [`solver.py`](../../../minicplex/solver.py))
and throws the solution away if one fails. That very check once caught a "fake solution" caused by rounding error in the simplex tableau.

Note: `assert` is a check for **programmers**, and it is skipped when running with `python -O`. To check user input (such as a file format), use `if ...: raise ValueError(...)` (lesson 9).

## 6. Your turn

Open [`exercises/l13_debugging.py`](../exercises/l13_debugging.py). The first five functions are marked 🐞: the code runs, but has a bug. Run it, start from the ❌ lines and fix them one by one; write the last function with `assert`. Run `python3 python/tutorial/en/run.py 13`.

## 7. Think about it

Why does the `best_price` bug (`min(prices)`) raise no error, yet return "apple"?

<details><summary>Answer</summary>

Looping over a dictionary gives its **keys** (the product names), so `min` compares strings and returns the alphabetically first name, which has nothing to do with the prices.
To compare by price, tell `min` what to compare: `min(prices, key=prices.get)` (the `key=` from lesson 8).

</details>

[← Project: a course planner](12-project.md) · [Contents](../README.md) · Next: [More about functions →](14-functions.md)
