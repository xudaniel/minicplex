# Lesson 12: Project, a course planner

> **You learn:** tying everything so far into one small application: read text → parse into objects → build a model → solve → print a report
> **Code used:** everything so far; compare with [`hard_staff_schedule.py`](../../../examples/hard_staff_schedule.py) (a bigger project of the same kind)
> **Exercise:** `python3 python/tutorial/en/run.py 12`
> **Do it online:** [open the web version, nothing to install](https://xudaniel.github.io/minicplex/python/en/#l12)

[← Testing](11-testing.md) · [Contents](../README.md) · Next: [Advanced: reading errors and debugging →](13-debugging.md)

## 1. The problem

```text
# course      credits  hours/week  day  interest
Python        4        6           Mon  9
Algorithms    4        8           Tue  10
Databases     3        5           Mon  7
OpsResearch   3        6           Wed  10
...
```

Choose courses to get the highest total "interest" within these limits:

1. total hours per week at most `max_hours`;
2. total credits at least `min_credits`;
3. at most 2 courses per day;
4. taking "Algorithms" requires taking "Python" (a prerequisite).

## 2. Layers: each one does one thing

```text
text ──parse()──▶ [Course, Course, ...] ──choose()──▶ ["Python", "OpsResearch", ...] ──report()──▶ table
```

- `parse` only deals with text and knows nothing about optimisation. On a bad format it does `raise ValueError` (lesson 9), including the offending line.
- `Course` is a frozen dataclass (lesson 6): never changed once parsed.
- `choose` only builds and solves the model, and doesn't know whether the data came from a file or a web page.
- `report` only does layout (lesson 10).

That way each layer can be tested on its own, and switching data source later (say, reading Excel) only changes `parse`. Almost every real project has this structure;
[`hard_staff_schedule.py`](../../../examples/hard_staff_schedule.py) (8 staff, a weekly roster, 10 rules) is a bigger version.

## 3. A few modelling tricks

```python
take = [m.add_var(0, 1, VarType.BINARY, f"take_{k}") for k in range(len(courses))]   # take each course or not
pairs = list(zip(courses, take))

sum((c.hours * t for c, t in pairs), LinExpr()) <= max_hours                          # total hours
sum((t for c, t in pairs if c.day == day), LinExpr()) <= 2                            # courses on one day: a condition in the generator
index["Algorithms"] <= index["Python"]                                                 # prerequisite: Algorithms (1) needs Python (1)
```

- `sum(…, LinExpr())`: the second argument is the starting value. Starting from `LinExpr()`, even with no terms at all (a day without courses) you get an empty expression rather than the integer `0`.
- "Taking A requires B" is written `A <= B`: both are 0/1, so only A=1, B=0 is ruled out. This is the most common trick in 0-1 modelling (`C_needs_D` in [`easy2_projects.py`](../../../examples/easy2_projects.py) is the same).
- When there's no solution the solver returns `Status.INFEASIBLE`, and `choose` turns that into an empty list, so callers needn't know solver details.

## 4. Tests check more than one answer

Besides "with these settings, these courses should be chosen", the exercise has two **property** tests: for every limit from 0 to 40 hours,
"if Algorithms is chosen then Python is chosen" and "at most 2 per day" must both hold. A property test needs no knowledge of the right answer, yet checks dozens of cases at once:
another use of lesson 11's second-opinion idea.

## 5. Your turn

Open [`exercises/l12_project.py`](../exercises/l12_project.py), write `parse` and `choose`, and run `python3 python/tutorial/en/run.py 12`. Once everything passes, it prints the chosen timetable.

## 6. What next

- Carry on with [advanced lessons 13–18](13-debugging.md).
- Add a rule to the planner: "not both Databases and Writing", or "at least one Wed course".
- Read the catalog from a file instead, with a friendly message when the file is missing or malformed (lesson 9).
- Read the minicplex source. Suggested order: [`model.py`](../../../minicplex/model.py) (modelling layer) → [`lp_reader.py`](../../../minicplex/lp_reader.py) (reading files) →
  [`solver.py`](../../../minicplex/solver.py) (branch and bound) → [`lp_engine.py`](../../../minicplex/lp_engine.py) (the simplex core).
  The main README's [Code tour](../../../../README.en.md#code-tour) walks through the algorithms section by section (using the C++ version; the Python version matches it line by line).
- Want to learn Java too? The same solver has a [Java version with a 20-lesson Java course](../../../../java/tutorial/README.md) (in Chinese), where you can compare the same algorithm in two languages.

🎉 Congratulations on finishing the main course! Want more? **Advanced lessons 13–18** cover what real projects use every day: reading errors and debugging, more about functions, decorators, generators, files and data, command-line programs and packaging.

[← Testing](11-testing.md) · [Contents](../README.md) · Next: [Advanced: reading errors and debugging →](13-debugging.md)
