# Basics A6: Lists, a whole row of numbers at once

> **You learn:** lists `[...]`; indexes; `len`; `for x in a_list`; `append`; `sum`, `max`
> **Time:** about 20 minutes · **Exercise:** `python3 python/tutorial/en/run.py A06`
> **Do it online:** [open the web version, nothing to install](https://xudaniel.github.io/minicplex/python/en/#a06)

[← Writing functions](a5-functions.md) · [Contents](../README.md) · Next: [Strings →](a7-strings.md)

## 1. Lists

```python
week = [8200, 6500, 12000, 4300, 9100, 15000, 7600]   # steps for each day of a week
week[0]       # 8200   ← indexes start at 0
week[-1]      # 7600   ← negative indexes count from the end
len(week)     # 7
week[2] = 0   # items can be changed
```

## 2. Looping: one item at a time

```python
for x in week:          # x is each day's steps in turn
    if x >= 8000:
        count += 1
```

When you need the index too, use `enumerate`: in `for i, x in enumerate(week):`, `i` is the day number and `x` that day's steps.

## 3. Building a new list

```python
out = []                # an empty list
for x in nums:
    out.append(x * 2)   # add one at the end
```

Once you're comfortable, this fits on one line as a "comprehension": `[x * 2 for x in nums]` (lesson 3 has more).

## 4. Built-in functions

`sum(week)`, `max(week)`, `min(week)` and `sorted(week)` are all ready-made. In the exercise you write them yourself with loops first, to see how they work; afterwards just use the built-ins.

> **In minicplex:** a solution's `r.x` is a list, and `r.x[j]` is the value of variable j.
> The example [`basics_08_min_max.py`](../../../examples/basics_08_min_max.py) keeps "hours per task" in a list and loops to add up the tasks each person gets.

## 5. Common mistakes

- `week[7]`: there are 7 items, so the last is `week[6]`; going past the end raises `IndexError`.
- Starting a "largest" search at `0`: wrong when every number is negative. Start from the first item.
- Averaging an empty list: `len([])` is 0, so you divide by zero.

## 6. Your turn

Open [`exercises/a06_lists.py`](../exercises/a06_lists.py) and run `python3 python/tutorial/en/run.py A06`.

The last one is a **🤔 guess, then run**: don't run anything yet. Read the few lines of code in the task, write your guess after `return`, then run and see whether you were right. A wrong guess is fine; working out why is the point.

## 7. Think about it

`a = [1, 2]`, `b = a`, `b.append(3)`: what is `a` now?

<details><summary>Answer</summary>

`[1, 2, 3]`. `b = a` doesn't copy the list; it gives the **same** list a second name. To copy, write `b = list(a)` or `b = a.copy()`.
This "alias" problem comes back in lessons 3 and 5: it is why the solver copies lists all over the place.

</details>

[← Writing functions](a5-functions.md) · [Contents](../README.md) · Next: [Strings →](a7-strings.md)
