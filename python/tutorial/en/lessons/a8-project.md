# Basics A8: A small project, buying fruit

> **You learn:** tying the first 7 together: functions, decisions, nested loops, tuples; your first use of the minicplex solver
> **Time:** about 20 minutes · **Exercise:** `python3 python/tutorial/en/run.py A08`
> **Do it online:** [open the web version, nothing to install](https://xudaniel.github.io/minicplex/python/en/#a08)

[← Strings](a7-strings.md) · [Contents](../README.md) · Next: [Lesson 1: Your first model →](01-first-model.md)

## 1. The problem

Apples cost $2 each and score 3 points; bananas cost $1 and score 2. You have $10 and the bag holds at most 7. What should you buy for the highest score?

## 2. Break it into small functions

- `fits(a, b)`: with this purchase, is there enough money, and does it fit in the bag?
- `score(a, b)`: how many points does it score?
- `best()`: try every purchase and keep the best one.

Each function does one thing, and you can check each one as soon as it's written. That's a good habit for any program.

## 3. Nested loops: trying every combination

```python
for a in range(6):          # 0 to 5 apples
    for b in range(11):     # 0 to 10 bananas
        ...                 # 6 × 11 = 66 combinations in all
```

Whenever you find a better one, remember it. To remember three numbers at once, use a **tuple** `(a, b, score)`: like a list, but with round brackets, and it can't be changed once made.
`best[2]` is the third number in the tuple (the score).

## 4. Hand it to the solver

The last function in the exercise, `solver_score()`, is already written. It gives the same problem to minicplex:

```python
m = Model()
apple = m.add_var(0, INF, VarType.INTEGER, "apple")
banana = m.add_var(0, INF, VarType.INTEGER, "banana")
m.add_constr(2 * apple + 1 * banana <= 10, "money")
m.add_constr(apple + banana <= 7, "bag")
m.set_objective(3 * apple + 2 * banana, ObjSense.MAXIMIZE)
solve(m).objective          # 17.0
```

It's almost the problem statement copied out: variables, limits, goal. Finding the answer is the solver's job.

## 5. Why a solver?

66 combinations take a moment to loop through. But with 30 kinds of fruit and up to 10 of each, there are 11³⁰ combinations (about 1.7 × 10³¹): at a hundred million per second, that's tens of millions of billions of years.
A solver doesn't try them one by one; it uses the "simplex method" and "branch and bound" to skip almost all of them cleverly (the main README's
[How it works](../../../../README.en.md#how-it-works) explains the idea in plain words).

## 6. Your turn

Open [`exercises/a08_fruit_project.py`](../exercises/a08_fruit_project.py) and run `python3 python/tutorial/en/run.py A08`.

Once everything is ✅, congratulations: you can write real programs. Next comes the main course, and lesson 1 starts from the modelling code you just saw.

## 7. Think about it

If the bag could hold any number but you still had $10, what would be best to buy? Why?

<details><summary>Answer</summary>

Only bananas: 10 of them, 20 points. Bananas score 2 points per dollar, apples only 1.5; with no bag limit, "points per dollar" is what matters.
Remove the bag condition from `fits` to check.

</details>

[← Strings](a7-strings.md) · [Contents](../README.md) · Next: [Lesson 1: Your first model →](01-first-model.md)
