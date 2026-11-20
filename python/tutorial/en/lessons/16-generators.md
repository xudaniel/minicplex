# Lesson 16: Generators and iterators

> **You learn:** iterables and iterators; `yield`; generator expressions; lazy evaluation; infinite sequences; `itertools`; `yield from` and recursive generators
> **Code used:** `sum(... for ...)` in [`examples/basics_08_min_max.py`](../../../examples/basics_08_min_max.py), `itertools.product` in [`tests/test_solver.py`](../../../tests/test_solver.py)
> **Exercise:** `python3 python/tutorial/en/run.py 16`
> **Do it online:** [open the web version, nothing to install](https://xudaniel.github.io/minicplex/python/en/#l16)

[← Decorators](15-decorators.md) · [Contents](../README.md) · Next: [Files and data →](17-files-data.md)

## 1. What happens behind a for loop

`for x in thing` works on lists, strings, dicts, files and `range`. They are all **iterable**: Python first calls `iter(thing)` to get an **iterator**,
then keeps calling `next(iterator)` for the next item until it says "no more" (`StopIteration`).

```python
it = iter([10, 20])
next(it)    # 10
next(it)    # 20
next(it)    # StopIteration
```

## 2. yield: the simplest way to make an iterator

```python
def countdown(n):
    while n > 0:
        yield n        # hand out a value, then pause here
        n -= 1

for x in countdown(3):
    print(x)           # 3 2 1
```

As soon as a function contains `yield`, calling it doesn't run it straight away; you get a **generator**. Each `next` resumes where it last paused and runs to the next `yield`.

## 3. Lazy: compute one when asked

```python
sum(hours[t] * give[t][p] for t in range(tasks))     # basics_08_min_max.py
```

A comprehension in round brackets is a **generator expression**: no complete list is built first; `sum` asks for one value at a time and it computes one. With lots of data that saves a lot of memory.

Laziness also allows **infinite** sequences:

```python
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

list(itertools.islice(fibonacci(), 10))    # take only the first 10
```

Reading a 10 GB file works the same way: `for line in open(path)` reads one line at a time instead of the whole file at once.

## 4. itertools: ready-made iteration tools

```python
itertools.product([0, 1], repeat=3)     # every 0/1 combination (lesson 3's brute-force knapsack)
itertools.islice(gen, 10)               # the first 10
itertools.count(1)                      # 1, 2, 3, ...
itertools.chain(a, b)                   # all of a, then all of b
itertools.combinations("abcd", 2)       # every pair
```

## 5. Recursive generators and yield from

The exercise asks you to write your own `product`: `n` positions, each taking a value from `values`, producing every combination. The idea is recursion:
the first position takes `v`, and every combination of the remaining `n - 1` positions is left to the function itself.

```python
for rest in assignments(n - 1, values):
    yield (v,) + rest
```

If you only pass on another generator's values unchanged, you can write `yield from other_generator`.

## 6. Use once

A generator is empty once it has run through:

```python
g = (x * x for x in range(3))
list(g)     # [0, 1, 4]
list(g)     # []        ← already used up
```

To use the values several times, store them in a list, or call the generator function again each time.

## 7. Your turn

Open [`exercises/l16_generators.py`](../exercises/l16_generators.py): a countdown, an infinite Fibonacci, chunks, cleaning data line by line, and finally a brute-force knapsack using your own `assignments`, checked against the solver. Run `python3 python/tutorial/en/run.py 16`.

The last one is a **🤔 guess, then run**: don't run anything yet. Read the few lines of code in the task, write your guess after `return`, then run and see whether you were right. A wrong guess is fine; working out why is the point.

## 8. Think about it

How many combinations does `assignments(20, [0, 1])` produce? What goes wrong if it "puts every combination in a list, then returns it"?

<details><summary>Answer</summary>

2²⁰ ≈ a million. A list has to build them all first, using hundreds of MB of memory, and you can't have the first result until all of them are done;
a generator holds just one combination at a time, and each can be used as soon as it's produced. Brute-force search, big files and data pipelines are where generators shine.

</details>

[← Decorators](15-decorators.md) · [Contents](../README.md) · Next: [Files and data →](17-files-data.md)
