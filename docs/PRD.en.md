# minicplex Product Requirements Document (PRD)

**English** · [简体中文](PRD.md)

| Item | Details |
|---|---|
| Product | minicplex |
| Owner | Daniel Xu |
| Version | v1.0.0 (released) → v1.1 / v2.0 (planned) |
| Status | v1.0.0 released as a GitHub Release; repository `xudaniel/minicplex` |
| Last updated | 2026-11-19 |

## 1. Summary

A "mini CPLEX" built from scratch in C++17. It reads CPLEX `.lp` files, lets you build models in C++, and solves
linear and mixed-integer programs. The code is short and readable, and every step can be matched against a
textbook. Line-by-line ports to Java 17 and pure Python follow exactly the same computation path as the C++ version.

## 2. Background and motivation

- Commercial solvers such as CPLEX and Gurobi are the core tools of operations research, but they are black boxes.
  It is hard to get an intuitive feel for how "simplex + branch-and-bound" actually runs.
- For a product manager in decision automation (business rules), understanding how optimisation solvers work helps
  with product direction and with conversations with customers and engineering teams, for example about how a rules
  engine and an optimisation engine fit together.
- Open-source solvers (HiGHS, CBC, SCIP) are very large and not suited as a first read. There is a gap for a teaching
  solver that stays within a few thousand lines yet solves real models.

## 3. Goals and non-goals

### 3.1 Goals

1. **Useful:** solve small and medium LP / MIP models correctly, with results that can be checked against brute
   force or commercial solvers.
2. **Compatible:** read and write the common subset of the CPLEX LP format, with a command line that feels like
   CPLEX.
3. **Readable:** core algorithms in a handful of files with clear comments, suitable for learning and teaching.
4. **Verifiable:** ship with tests, including automatic comparison of random models against brute-force
   enumeration.

### 3.2 Non-goals

- Competing with CPLEX on speed, or handling models with tens of thousands of variables.
- Quadratic programming (QP), second-order cone programming (SOCP) or constraint programming (CP).
- A graphical interface or commercialisation.

## 4. Target users and scenarios

| User | Scenario |
|---|---|
| Students and engineers learning operations research | Step through the simplex and branch-and-bound code to understand the algorithms |
| Product managers and pre-sales | Demonstrate what an optimisation solver is and how modelling works with small examples |
| C++ developers | Embed a lightweight solver in a small project without a commercial licence |
| Instructors | Use the models in `examples/` for classroom demos (production planning, knapsack, facility location) |

## 5. Functional requirements

Priorities: P0 = must have, P1 = should have, P2 = nice to have.

### 5.1 Modelling (C++ API)

| ID | Requirement | Priority | Status |
|---|---|---|---|
| M-1 | Create continuous, integer and binary variables with bounds and names | P0 | ✅ v0.1 |
| M-2 | Write linear expressions and constraints with operators, e.g. `2*x + 3*y <= 12` | P0 | ✅ v0.1 |
| M-3 | Set a minimisation or maximisation objective, including a constant term | P0 | ✅ v0.1 |
| M-4 | Look up variables by name | P1 | ✅ v0.1 |
| M-5 | Modify existing constraints / delete variables | P2 | ⏳ Not started |
| M-6 | Java modelling API (fluent style `LinExpr.of(2, x).plus(3, y).le(12)`) with the same features as C++ | P1 | ✅ v1.1 |
| M-7 | Python modelling API (operator overloading `2 * x + 3 * y <= 12`, dataclass parameters) with the same features as C++ | P1 | ✅ v1.1 |

### 5.2 Linear programming

| ID | Requirement | Priority | Status |
|---|---|---|---|
| L-1 | Two-phase primal simplex | P0 | ✅ v0.1 (replaced in v1.0 by the bounded simplex with a composite phase 1) |
| L-1b | Bounded-variable simplex: bounds take no rows, no artificial variables | P0 | ✅ v1.0 |
| L-2 | `<=`, `>=`, `=`, negative right-hand sides, free variables, negative bounds | P0 | ✅ v0.1 |
| L-3 | Detect infeasibility and unboundedness | P0 | ✅ v0.1 |
| L-4 | Prevent cycling under degeneracy (Bland's rule) | P0 | ✅ v0.1 |
| L-5 | Report duals (shadow prices) and reduced costs | P1 | ✅ v1.1 |
| L-6 | Revised simplex with LU factorisation and sparse matrices | P1 | ⏳ v2.0 |
| L-7 | Dual simplex | P1 | ✅ v1.0 |

### 5.3 Mixed-integer programming

| ID | Requirement | Priority | Status |
|---|---|---|---|
| I-1 | Branch-and-bound with best-bound node selection | P0 | ✅ v0.1 |
| I-2 | Most-fractional branching | P0 | ✅ v0.1 |
| I-3 | Rounding heuristic to find feasible solutions early; polishing before acceptance (fix integers, re-solve the continuous part) | P1 | ✅ v0.1 (polishing v1.1) |
| I-4 | Bound strengthening for integral objectives | P1 | ✅ v0.1 |
| I-5 | Relative gap, node limit, time limit | P0 | ✅ v0.1 |
| I-6 | Cutting planes: Gomory mixed-integer cuts at the root | P1 | ✅ v1.1 |
| I-6b | Cover cuts, cuts inside the tree | P2 | ⏳ v1.2 |
| I-7 | Presolve: bound propagation, big-M coefficient tightening, redundant-row removal | P1 | ✅ v1.1 |
| I-8 | Pseudo-cost and strong branching (reliability branching) | P2 | ✅ v1.1 |
| I-9 | Warm-started nodes (reuse the parent basis) + plunging + dual cutoff pruning | P1 | ✅ v1.0 |

### 5.4 Files and command line

| ID | Requirement | Priority | Status |
|---|---|---|---|
| F-1 | Read the CPLEX LP format (objective, constraints, Bounds, General, Binary, End, comments) | P0 | ✅ v0.1 |
| F-2 | Write the CPLEX LP format, with identical results after a round trip | P1 | ✅ v0.1 |
| F-3 | CLI options `--relax`, `--gap`, `--nodes`, `--time`, `--quiet`, `--all`, `--write` | P0 | ✅ v0.1 |
| F-4 | CPLEX-style node log (nodes, nodes left, objective, best integer, best bound, gap) | P1 | ✅ v0.1 |
| F-5 | Read the MPS format | P2 | ⏳ v1.1 |
| F-6 | Write solution files (`.sol`) | P2 | ⏳ v1.1 |
| F-7 | Range constraints (`-2 <= x + y <= 5`) | P2 | ⏳ v1.1 |

### 5.5 Engineering quality

| ID | Requirement | Priority | Status |
|---|---|---|---|
| Q-1 | GitHub Actions: build and test on Linux and macOS | P0 | ✅ v1.0 |
| Q-2 | AddressSanitizer + UBSan test run | P1 | ✅ v1.0 |
| Q-3 | Automatic comparison of random MIPs against HiGHS | P0 | ✅ v1.0 |
| Q-4 | Benchmarks compared with a baseline to catch regressions in results and speed | P1 | ✅ v1.0 |

## 6. Non-functional requirements

| Category | Requirement |
|---|---|
| Correctness | 100% agreement with brute force on random integer programs; correct results on textbook examples |
| Performance | Models with a few hundred variables and constraints solve within 1 second (v1.0 dense implementation); thousands from v2.0 |
| Portability | Only the C++17 standard library and CMake; builds on Linux, macOS and Windows |
| Readability | Core code kept to a few thousand lines (currently about 2,200 lines of C++), with commented algorithm steps |
| Numerical stability | Consistent pivot, optimality and integrality tolerances; protection against cycling |

## 7. Success metrics

1. All tests pass, and agreement stays at 100% when random comparisons grow from 500 to 5,000 models.
2. Small MIPLIB instances (such as `p0033` and `flugpl`) solve to their known optimal values.
3. An engineer who has never seen the code can follow the main simplex and branch-and-bound flow within an hour.

## 8. Roadmap

| Version | Main content | Status |
|---|---|---|
| v0.1 | Two-phase simplex, branch-and-bound, LP reader and writer, command line, tests | ✅ Done |
| v1.0 | Bounded simplex, dual simplex warm starts, plunging branch-and-bound, CI / sanitizers / fuzzing / benchmarks (about 4.5× faster in total, 95% fewer iterations) | ✅ Released 2026-11-19 |
| v1.1 | ✅ Done: reliability branching, root Gomory cuts, presolve (28% fewer nodes on the test set, production planning 10× faster), duals (shadow prices), Java and Python ports (identical computation path). To do: MPS input, solution files, range constraints | In progress |
| v2.0 | Revised simplex with sparse LU factorisation; take on small MIPLIB instances | Planned |

## 9. Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Round-off leads to wrong feasibility decisions | Wrong results | Consistent tolerances; random comparison tests; scaling if needed |
| Dense tableau limits model size | Large models are slow or run out of memory | v2.0 moves to revised simplex with sparse LU |
| LP-format details differ from CPLEX | Some files cannot be read | Document the supported subset; report the line and reason when parsing fails |
| Branch-and-bound may not terminate with unbounded integer variables | Optimality cannot be proven; the node limit is reached | Documented as a known limitation; v1.2 plans cuts inside the tree |
| The C++, Java and Python code bases drift apart | Results differ, maintenance multiplies | Keep the code line-for-line aligned; CI compares node and iteration counts model by model on every commit and fails on any difference |
| Limited spare time | Schedule slips | Small, independently releasable versions |

## 10. Appendix: v0.1 acceptance

- Textbook LP (Wyndor Glass): optimum 36 at (2, 6) ✅
- Infeasible and unbounded detection ✅
- Free variables + equality constraints ✅
- Beale's cycling example: optimum −1.25 ✅
- 0-1 knapsack: optimum 21 ✅
- LP write/read round trip gives identical results ✅
- 500 random integer programs agree with brute force, 500/500 ✅

## 11. Appendix: v1.0 acceptance (2026-11-19)

- 26 unit tests, smoke tests of the examples and CLI, benchmark solvability: all pass (Release and ASan/UBSan builds)
- Comparison with HiGHS: about 6,000 random models (MIPs, larger MIPs, pure LPs, multi-knapsack), all agree
- Found one HiGHS error: a MIP with an unbounded LP relaxation was reported as "optimal 41", while the objective
  decreases without limit along the ray (x1 + 7, x4 − 9); minicplex correctly reports "infeasible or unbounded".
  The comparison script now handles this case using Meyer's theorem
- Benchmarks: simplex iterations 777,609 → 40,804, total time 2.78 s → about 0.6 s

## 12. Appendix: v1.1 MIP speed-up acceptance (2026-11-19)

- MIP test set (18 models): nodes 47,304 → 34,034 (−28%), 1.7× faster in total; production planning 7,001 → 419 nodes
- Correctness: 35 unit tests (including the validity of Gomory cuts against 24,532 integer points), ASan/UBSan
  clean; about 4,000 models compared with HiGHS, all agree
- Fuzzing caught and fixed one real bug: tableau drift led to accepting a pseudo-solution violating a constraint by
  3×10⁻⁵; fixed by re-checking rows against the original matrix and polishing solutions
- Trade-off: on small models (such as the staff schedule) strong branching and cuts cost more than they save
  (0.016 s → 0.06 s); on larger models the gains are clear

## 13. Appendix: Java port acceptance (2026-11-19)

- Scope: solver, command line (including `--trace`), benchmark and generator tools, 15 examples and the tests are all
  ported; Java 17 or later, no dependencies; builds with `build.sh` (offline) or Maven
- Consistency: the output of all 15 examples and the `.lp` files they export are byte-for-byte identical; `--trace`
  is identical line for line; on 13 benchmark models and 2,000 random MIPs the status, objective, node count and
  iteration count all match
- Correctness: the Java version's own 40 checks pass (brute force on 500 models × 3 parameter sets, Gomory cut
  validity, finite-difference checks of shadow prices, and more)
- Found and fixed two determinism issues in the C++ version during the port: cuts and strong-branching candidates
  used an unstable sort and the node queue had no final tie-break, so the search path depended on the standard
  library (now a stable sort plus insertion-order tie-breaking); and compilers could fuse `a*b + c` into FMA
  instructions (GCC 15 on CI), changing rounding (now unified with `-ffp-contract=off`)
- Speed: on the benchmark models Java takes about 0.72 s in total and C++ about 0.39 s

## 14. Appendix: Python port acceptance (2026-11-20)

- Scope: the solver, the command line (with `--trace` and `--duals`), the batch tool, all 15 examples and the tests
  are ported; Python 3.9 or later, standard library only; installable with `pip install ./python`
- Parity: the output of the 15 examples and the `.lp` files they export match C++ byte for byte; `--trace` matches
  line for line; on 13 benchmark models and 650 random models (600 MIPs, 40 LPs, 10 multi-knapsacks) the status,
  objective, node count and iteration count all match
- Correctness: the Python version's own 20 tests pass on Python 3.9 and 3.13 (brute force on 500 models × 3
  parameter sets, Gomory cut validity against 21,664 integer points, finite-difference checks of 249 shadow prices,
  operator overloading)
- Bit-level details: C++-style rounding, `ceil`/`floor` that keep the sign of `-0.0`, Java-style `min(0.0, -0.0)`,
  and `-0.0` before `0.0` in the node queue (`python/minicplex/jmath.py`)
- Speed: about 20 s for the benchmark models against about 0.4 s for C++; fine for teaching and small models
- Companion: a 20-lesson Python course in Chinese (`python/tutorial/`); CI runs every reference solution on 3.9 and 3.13
