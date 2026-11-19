# minicplex

A small, dependency-free **LP / MIP solver in C++17**, built as a side project to understand how
solvers like IBM ILOG CPLEX work inside. It reads CPLEX `.lp` files, offers a Concert-style C++
modelling API, and prints a CPLEX-like node log.

> Not affiliated with IBM. It is a learning project, not a replacement for CPLEX: it uses a dense
> tableau, so it is meant for small and medium models (hundreds of rows/columns).

## Features

| Area | What's implemented |
|---|---|
| LP | Two-phase primal simplex (dense tableau), Dantzig pricing with Bland's rule fallback (anti-cycling) |
| Bounds | Lower/upper bounds, free variables, negative bounds, fixed variables |
| Constraints | `<=`, `>=`, `=`, negative right-hand sides, redundant rows |
| MIP | Best-first branch and bound, most-fractional branching, rounding heuristic, integral-objective bound strengthening |
| Controls | Relative MIP gap, node limit, time limit, LP relaxation mode |
| I/O | CPLEX LP format reader (Minimize/Maximize, Subject To, Bounds, General, Binary, End) and writer |
| Status | Optimal, Infeasible, Unbounded, InfeasibleOrUnbounded, NodeLimit, TimeLimit, IterationLimit |

## Build

```bash
cmake -S . -B build
cmake --build build -j
ctest --test-dir build          # or ./build/minicplex_tests
```

## Command line

```bash
./build/minicplex examples/facility.lp
./build/minicplex --relax examples/knapsack.lp      # LP relaxation only
./build/minicplex --gap 1e-4 --time 10 model.lp
```

Example output:

```
minicplex 0.1 | examples/facility.lp
  15 variables (15 integer), 7 constraints, minimize

Status:       Optimal
Objective:    360
Best bound:   360   (gap 0.0000%)
Nodes:        13
```

## C++ API

```cpp
#include "solver.hpp"
using namespace mcplex;

Model m;
Var chairs = m.addVar(0, INF, VarType::Integer, "chairs");
Var tables = m.addVar(0, INF, VarType::Integer, "tables");
m.addConstr(2 * chairs + 5 * tables <= 40, "wood");
m.addConstr(3 * chairs + 2 * tables <= 30, "labor");
m.addConstr(chairs >= tables, "mix");
m.setObjective(30 * chairs + 70 * tables, ObjSense::Maximize);

Result r = solve(m);          // r.status, r.objective, r.x, r.nodes ...
m.writeLP(std::cout);         // export as CPLEX LP format
```

## How it works

1. **Standard form** (`src/simplex.cpp`): each variable is shifted by a finite bound
   (`x = l + y` or `x = u - y`) or split if free (`x = y⁺ - y⁻`); finite ranges become rows;
   slacks, surpluses and artificials are added so that `A y = b, y ≥ 0, b ≥ 0`.
2. **Phase 1** minimises the sum of artificials (feasibility), then drives any leftover
   artificials out of the basis. **Phase 2** optimises the real objective.
3. **Branch and bound** (`src/branch_and_bound.cpp`) solves the LP relaxation at each node,
   prunes by bound, branches on the most fractional integer variable and always explores the
   node with the best bound first. A rounding heuristic finds early incumbents.

## Tests

`tests/test_solver.cpp` checks textbook LPs, infeasible/unbounded detection, free variables,
Beale's cycling example, a knapsack, LP read/write round-trips, and **500 random integer
programs compared against brute-force enumeration**.

## Project layout

```
include/   model.hpp  solver.hpp  lp_reader.hpp
src/       simplex.cpp  branch_and_bound.cpp  lp_reader.cpp  model.cpp  main.cpp
examples/  *.lp  api_demo.cpp
tests/     test_solver.cpp
```

## Ideas for next steps

Revised simplex with LU factorisation, dual simplex for warm-started B&B nodes, cutting planes
(Gomory, cover cuts), presolve, pseudo-cost branching, MPS file support.

## License

MIT
