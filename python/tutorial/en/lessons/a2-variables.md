# Basics A2: Variables and arithmetic

> **You learn:** variables; whole numbers (`int`) and decimals (`float`); `+ - * /`; floor division `//` and remainder `%`
> **Time:** about 15 minutes · **Exercise:** `python3 python/tutorial/en/run.py A02`
> **Do it online:** [open the web version, nothing to install](https://xudaniel.github.io/minicplex/python/en/#a02)

[← Make the program talk](a1-hello.md) · [Contents](../README.md) · Next: [Making decisions →](a3-decisions.md)

## 1. Variables: giving a value a name

```python
price = 4        # a notebook costs $4
count = 3
total = price * count
print(total)     # 12
```

`=` does not mean "equals"; it means "put the value on the right into the name on the left". So `count = count + 1` is perfectly fine: work out the right side first, then store it.
It can be shortened to `count += 1`.

Variable names use letters, digits and underscores, and can't start with a digit. The Python habit is all lower case with underscores between words: `order_total`, `max_steps`.

## 2. Two kinds of number

| Written | Type | Examples |
|---|---|---|
| no decimal point | `int` (whole number) | `3`, `-7`, `2026` |
| with a decimal point | `float` (decimal) | `6.5`, `0.1`, `3.0` |

Python's integers have no size limit: even `2 ** 100` (2 to the power 100) is computed exactly. Decimals aren't so perfect; lesson 2 explains why `0.1 + 0.2` is not `0.3`.

## 3. Three kinds of division

```python
10 / 3     # 3.3333333333333335   ordinary division, always gives a decimal
10 // 3    # 3                    floor division: the whole part only (rounded down)
10 % 3     # 1                    the remainder
```

"How many $3 items can $10 buy" uses `//`; "how much is left over" uses `%`.

> **In minicplex:** the solver stores a table with m rows and n columns as one long row of numbers; number k is in row `k // n`, column `k % n` (lesson 3 explains).

## 4. Common mistakes

- Using `=` to compare: testing whether two values are equal needs `==` (A3).
- Using `/` when you want a whole number: `10 / 2` is `5.0` (a decimal), not `5`.
- Parentheses: `(a + b + c) / 3` and `a + b + c / 3` are different, because multiplication and division come first.

## 5. Your turn

Open [`exercises/a02_variables.py`](../exercises/a02_variables.py), fill in the five functions and run `python3 python/tutorial/en/run.py A02`.

The last one is a **🤔 guess, then run**: don't run anything yet. Read the few lines of code in the task, write your guess after `return`, then run and see whether you were right. A wrong guess is fine; working out why is the point.

## 6. Think about it

What is `-7 // 2`? Is it `-3` or `-4`?

<details><summary>Answer</summary>

It's `-4`. `//` rounds **down** (towards minus infinity); it doesn't just chop off the decimals. `-3.5` rounded down is `-4`.
Likewise `-7 % 2` is `1`, because `-4 × 2 + 1 = -7`. Many other languages (C, Java) give `-3` and `-1` here, so take care when switching languages.

</details>

[← Make the program talk](a1-hello.md) · [Contents](../README.md) · Next: [Making decisions →](a3-decisions.md)
