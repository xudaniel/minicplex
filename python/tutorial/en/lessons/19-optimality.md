# Lesson 19: How do we know it's optimal?

> **You learn:** dual certificates (how shadow prices prove a ceiling); branch and bound "closing in from both ends" and the gap; the floor and cap of a zero-sum game; tolerances and stopping early
> **Code used:** the gap test in [`solver.py`](../../../minicplex/solver.py), `Result.duals` and `Result.best_bound`; the command line's `--duals` and node log
> **Exercise:** `python3 python/tutorial/en/run.py 19`
> **Do it online:** [open the web version, nothing to install](https://xudaniel.github.io/minicplex/python/en/#l19)

[← Command-line programs and packaging](18-cli-packaging.md) · [Contents](../README.md)

## 1. The solver did not try every option

With a few dozen integer variables there are more combinations than atoms in the universe, so trying them one by one is impossible. A solver can still say "this is optimal" because it tracks two numbers at once:

- **the best answer found** (a lower bound, when maximising): a feasible solution is in hand, so the optimum is at least this good;
- **a ceiling no answer can beat** (an upper bound): there is evidence that even the best possible solution can't get past it.

When the two meet and no gap is left, optimality is **proven**. This lesson is about where the ceiling comes from and how to check it.

## 2. Linear programs: shadow prices are the certificate

The example: maximise 5x + 4y subject to 6x + 4y ≤ 24, x + 2y ≤ 6, x, y ≥ 0.

Write the example as an LP file (`demo_model` in the exercise builds the same model), then solve its linear relaxation on the command line and print the shadow prices:

```bash
cd python && python3 -m minicplex demo.lp --relax --duals
```

The solver gives x = 3, y = 1.5 with objective 21, and also the two constraints' **shadow prices**, 0.75 and 0.5. Use them to weight the constraints:

```text
0.75 × (6x + 4y) + 0.5 × (x + 2y) = 5x + 4y        ← the weighted left-hand side is exactly the objective
0.75 × 24        + 0.5 × 6        = 21             ← the weighted right-hand side
```

So for **any** x, y that satisfy the constraints, 5x + 4y ≤ 21. And x = 3, y = 1.5 reaches 21 exactly. Proven.

For this argument to work, the shadow prices must meet two conditions (`dual_feasible` in the exercise):

- **no negatives:** multiplying both sides of a `<=` constraint by a negative number flips the inequality;
- **each column, weighted, is at least its objective coefficient:** the x column gives 6 × 0.75 + 1 × 0.5 = 5 ≥ 5, the y column 4 × 0.75 + 2 × 0.5 = 4 ≥ 4.

This is the **duality theorem**: an optimal solution of a linear program always comes with such a set of shadow prices that makes the two ends equal. The beauty is that **anyone can check the certificate by hand, without trusting the solver**. In minicplex the shadow prices are in `r.duals`.

## 3. Integer programs: closing in from both ends

Once x and y must be whole numbers, y = 1.5 is no good. Branch and bound splits the problem into y ≤ 1 and y ≥ 2 and solves each half, finding integer solutions while pushing the ceiling down. These are the key columns of a real minicplex node log:

| Node | Best Integer | Best Bound | Gap |
|---|---|---|---|
| 2 | 18 | 21 | 16.67% |
| 3 | 19 | 20 | 5.26% |
| 5 | 20 | 20 | 0.00% |

(The command-line log has these same columns, and so does CPLEX's.)

- **Best Integer** climbs 18 → 19 → 20;
- **Best Bound** comes down 21 → 20. It is the largest LP ceiling among the branches not yet finished, and each branch's ceiling has a certificate like the one in section 2;
- **Gap** = |bound − best integer| / |best integer|; it is 0 once the two ends meet.

The code minicplex uses to decide "they've met" ([`solver.py`](../../../minicplex/solver.py)):

```python
return incumbent - bound <= max(P.mip_abs_gap, P.mip_gap * max(1.0, abs(incumbent)))
```

(Internally minicplex always minimises, hence "best solution − lower bound"; the exercise is written for maximising, so the direction is reversed.)

## 4. Three things to watch

- **"Optimal" means within a tolerance:** by default a relative gap of one in a million is allowed (`Params.mip_gap`, CPLEX's EpGap). Decimal arithmetic carries error anyway (lesson 2); demanding an exact match could mean never stopping.
- **Stopping early gives only a good solution:** with a `time_limit` or `node_limit`, if the gap is still above 0 when it stops, the result is just a good feasible solution. The gap tells you at most how much is missing; that's the 🤔 task in the exercise.
- **Guarding against fake solutions:** every time it finds an integer solution, minicplex re-checks every constraint against the original model (`check_feasible`, lesson 13) and throws the solution away if one fails.

## 5. Games work the same way: floor and cap

A zero-sum game can be proven the same way. The exercise includes a ready-made penalty-kick game (made-up numbers): if the shooter randomises left 41%, centre 13%, right 47%, the scoring rate is **at least** 78.1% wherever the keeper dives (the floor); if the keeper randomises left 37%, centre 20%, right 43%, it is **at most** 78.1% wherever the shooter aims (the cap). Floor = cap, so both are optimal. The keeper's probabilities are exactly the shadow prices of the shooter's linear program, which is why von Neumann's minimax theorem and the duality theorem are the same thing.

## 6. Your turn

Open [`exercises/l19_optimality.py`](../exercises/l19_optimality.py): compute the ceiling, check a certificate, write the gap and the "proven" test, then compute the floor and cap of the penalty-kick game. Run `python3 python/tutorial/en/run.py 19`.

The last one is a **🤔 guess, then run**: don't run anything yet. Read the few lines of code in the task, write your guess after `return`, then run and see whether you were right. A wrong guess is fine; working out why is the point.

## 7. Think about it

What would shadow prices of 1 and 0 in section 2 prove?

<details><summary>Answer</summary>

The x column gives 6 × 1 + 1 × 0 = 6 ≥ 5, the y column 4 × 1 + 2 × 0 = 4 ≥ 4, and neither is negative, so this is valid evidence too, proving 5x + 4y ≤ 1 × 24 + 0 × 6 = 24.
A ceiling of 24 is correct, just looser than 21. **Any** valid set of shadow prices gives a ceiling; the best set gives the tightest one, exactly equal to the optimum. Finding that tightest set is itself a linear program, called the **dual problem**.

</details>

🎉 You've finished all 27 lessons! You can write Python, and you know why a solver is entitled to say "this is the best there is". A few ways to keep going:

- Run lesson 1's example with `--trace` to see every simplex pivot, and compare with where section 2's shadow prices come from;
- Read minicplex's [`lp_engine.py`](../../../minicplex/lp_engine.py) and find the lines that compute the dual prices;
- The main README's [Code tour](../../../../README.en.md#code-tour) walks through the algorithms section by section.

[← Command-line programs and packaging](18-cli-packaging.md) · [Contents](../README.md)
