# Basics A4: Repeating things

> **You learn:** `for` and `range`; `while`; accumulators; `break`
> **Time:** about 20 minutes · **Exercise:** `python3 python/tutorial/en/run.py A04`
> **Do it online:** [open the web version, nothing to install](https://xudaniel.github.io/minicplex/python/en/#a04)

[← Making decisions](a3-decisions.md) · [Contents](../README.md) · Next: [Writing functions →](a5-functions.md)

## 1. for: a fixed number of times

```python
for i in range(5):        # i is 0, 1, 2, 3, 4 in turn
    print(i)

for i in range(1, 11):    # 1 to 10 (11 not included)
    total += i
```

`range(a, b)` starts at `a` and **does not include** `b`. So "1 to n" is `range(1, n + 1)`.

## 2. Accumulators: building up a result as you loop

```python
total = 0                 # first get an empty "basket" ready
for i in range(1, n + 1):
    total += i            # add a bit each time round
return total              # hand it back once the loop is over
```

Counting works the same way: `count = 0`, then `count += 1` whenever the condition holds.

## 3. while: keep going until the condition fails

When you don't know how many times, use `while`:

```python
saved, days = 0, 0
while saved < target:     # not enough yet, so keep going
    saved += per_day
    days += 1
```

Something inside the loop must change, or the condition stays true forever and the program "hangs" (press Ctrl+C to stop it).

> **In minicplex:** the simplex method is a `while True:` loop ([`lp_engine.py`](../../../minicplex/lp_engine.py), `_primal`):
> each round improves things a little, until no direction improves any more and it does `return OPTIMAL`. To avoid looping forever it also counts its steps and does `return ITERATION_LIMIT` past a limit.

## 4. Common mistakes

- `range(1, n)` misses the last number (it should be `range(1, n + 1)`).
- The accumulator inside the loop: `total = 0` gets reset every round.
- `return` indented into the loop: it returns in the first round.

## 5. Your turn

Open [`exercises/a04_loops.py`](../exercises/a04_loops.py) and run `python3 python/tutorial/en/run.py A04`.

## 6. Think about it

Which numbers does `for i in range(10, 0, -2)` give?

<details><summary>Answer</summary>

`10, 8, 6, 4, 2`. The third argument is the "step", and it can be negative to count backwards. The end point `0` is still not included.

</details>

[← Making decisions](a3-decisions.md) · [Contents](../README.md) · Next: [Writing functions →](a5-functions.md)
