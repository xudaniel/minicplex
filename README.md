# minicplex

[![CI](https://github.com/xudaniel/minicplex/actions/workflows/ci.yml/badge.svg)](https://github.com/xudaniel/minicplex/actions/workflows/ci.yml)
![版本](https://img.shields.io/badge/版本-1.0.0-blue)
![C++17](https://img.shields.io/badge/C%2B%2B-17-informational)
![依赖](https://img.shields.io/badge/依赖-零-success)
![许可证](https://img.shields.io/badge/许可证-MIT-lightgrey)

一个用 **C++17 编写、零依赖的线性规划 / 混合整数规划（LP / MIP）求解器**。这是一个业余项目，目的是从内部
理解 IBM ILOG CPLEX 这类求解器的工作原理。它能读取 CPLEX `.lp` 文件，提供类似 Concert 的 C++ 建模 API，
并输出类似 CPLEX 的分支定界日志。

> 与 IBM 无关。这是一个学习项目，不是 CPLEX 的替代品：它使用稠密单纯形表，适合中小规模模型
>（几百行 / 几百列）。

产品需求文档见 [docs/PRD.md](docs/PRD.md)，版本更新记录见 [CHANGELOG.md](CHANGELOG.md)，发布说明见 [docs/releases](docs/releases/)。

## 功能一览

| 模块 | 已实现内容 |
|---|---|
| 线性规划 | 有界变量单纯形（变量边界不占约束行）：组合式第一阶段 + 原始单纯形，加对偶单纯形；Dantzig 定价，退化时切换 Bland 规则防止循环；定期从原矩阵重建单纯形表，抑制舍入误差 |
| 变量边界 | 上下界、自由变量、负边界、固定变量 |
| 约束 | `<=`、`>=`、`=`，右端项为负，冗余约束 |
| 整数规划 | 分支定界 + 下潜（plunging）：子节点从父节点的单纯形表热启动，用对偶单纯形几步重新求优；兄弟节点保存父节点的基，之后增量恢复；对偶单纯形中途达到截断值即剪枝；最优界优先选点、最分数变量分支、取整启发式、整数目标函数的界加强 |
| 求解参数 | 相对 MIP 间隙、节点上限、时间上限、只求 LP 松弛 |
| 输入输出 | CPLEX LP 格式读取（Minimize/Maximize、Subject To、Bounds、General、Binary、End）与写出 |
| 求解状态 | Optimal（最优）、Infeasible（不可行）、Unbounded（无界）、InfeasibleOrUnbounded、NodeLimit、TimeLimit、IterationLimit |

## 编译

```bash
cmake -S . -B build
cmake --build build -j
ctest --test-dir build          # 或 ./build/minicplex_tests
```

## 命令行用法

```bash
./build/minicplex examples/facility.lp
./build/minicplex --relax examples/knapsack.lp      # 只求 LP 松弛
./build/minicplex --gap 1e-4 --time 10 model.lp     # 设定间隙和时间上限
```

| 参数 | 说明 |
|---|---|
| `--relax` | 忽略整数约束，只求 LP 松弛 |
| `--gap G` | 相对 MIP 间隙（默认 1e-6） |
| `--nodes N` | 分支定界节点上限 |
| `--time T` | 时间上限（秒） |
| `--quiet` | 不打印节点日志 |
| `--all` | 也打印取值为 0 的变量 |
| `--write FILE` | 把读入的模型重新写成 LP 格式 |

输出示例：

```
minicplex 0.1 | examples/facility.lp
  15 variables (15 integer), 7 constraints, minimize

Status:       Optimal
Objective:    360
Best bound:   360   (gap 0.0000%)
Nodes:        13
```

## 例子

| 文件 | 类型 | 内容 |
|---|---|---|
| `examples/easy1_bakery.cpp` | 线性规划 | 面包店生产计划：最大利润 21 元（蛋糕 3 个、面包 1.5 个） |
| `examples/easy2_projects.cpp` | 0-1 整数规划 | 预算 10 万选投资项目：最大收益 16 万（选 A、C、D） |
| `examples/hard_production_plan.cpp` | 混合整数规划（复杂） | 3 产品 × 6 周生产排程：换线、最小批量、加班、仓储；最低成本 35,615 元（约 5,500 个节点，0.3 秒，与 HiGHS 结果一致） |
| `examples/hard_staff_schedule.cpp` | 0-1 整数规划（复杂） | 餐厅 8 人一周排班：覆盖需求、老员工坐镇、晚班后不接早班、连续上班 ≤ 3 天、新人带教、两人不同班；最低成本 6,571 元（19 个节点，0.02 秒，与 HiGHS 结果一致） |

```bash
./build/easy1_bakery
./build/easy2_projects
./build/hard_production_plan
./build/hard_staff_schedule
```

复杂例子运行后会导出 `.lp` 文件，可以用 HiGHS 独立验算（需要 Python + scipy）：

```bash
python3 tools/verify_with_highs.py build/hard_staff_schedule.lp
```

## C++ 建模 API

```cpp
#include "solver.hpp"
using namespace mcplex;

Model m;
Var chairs = m.addVar(0, INF, VarType::Integer, "chairs");   // 椅子（整数）
Var tables = m.addVar(0, INF, VarType::Integer, "tables");   // 桌子（整数）
m.addConstr(2 * chairs + 5 * tables <= 40, "wood");          // 木材
m.addConstr(3 * chairs + 2 * tables <= 30, "labor");         // 工时
m.addConstr(chairs >= tables, "mix");                        // 搭配
m.setObjective(30 * chairs + 70 * tables, ObjSense::Maximize);

Result r = solve(m);          // r.status、r.objective、r.x、r.nodes ……
m.writeLP(std::cout);         // 导出为 CPLEX LP 格式
```

## 工作原理

1. **计算形式**（`src/simplex.cpp`）：每条约束加一个松弛变量 `s = a·x`，得到 `A x − s = 0`，
   变量和松弛变量都带上下界。非基变量停在某个边界上（自由变量停在 0），所以变量边界不需要额外的约束行，
   全松弛变量基总是一个合法的初始基，也不需要人工变量。
2. **原始单纯形**：第一阶段最小化基变量越界量之和（每次迭代重新构造代价），第二阶段优化真正的目标；
   进基变量可以直接跳到另一个边界（bound flip），不必换基。
3. **对偶单纯形**：只要当前基对偶可行就用它。分支只是收紧某个基变量的边界，父节点的最优基对子节点
   仍然对偶可行，所以子节点通常几次主元运算就能重新求优。
4. **分支定界**（`src/branch_and_bound.cpp`）：沿取整方向一路下潜，每层都热启动；另一个子节点连同父节点的基
   放进队列。下潜结束后取界最好的节点，从当前单纯形表增量换到它保存的基，再用对偶单纯形求解。
   对偶目标值单调上升，一旦超过当前最优整数解就立即停止（截断剪枝）。

v1.0 内核与早期 v0.1 内核的对比（`bench/` 中 13 个模型，同一台机器）：

| | v0.1（两阶段稠密单纯形，每个节点从零求解） | v1.0（有界单纯形 + 对偶热启动） |
|---|---|---|
| 单纯形迭代总数 | 777,609 | 40,804（少 95%） |
| 总用时 | 2.78 秒 | 约 0.6 秒（快约 4.5 倍） |
| 员工排班例子 | 239 个节点，1.03 秒 | 19 个节点，0.02 秒 |

## 开发与测试

| 工具 | 作用 |
|---|---|
| `ctest --test-dir build` | 单元测试 + 所有例子 / 命令行冒烟测试 + 基准模型可解性 |
| `-DMINICPLEX_SANITIZE=ON` | 用 AddressSanitizer + UBSan 编译，检查内存越界和未定义行为 |
| `minicplex_gen` | 随机生成模型（`mixed` 混合整数、`mkp` 多维背包、`lp` 线性规划） |
| `minicplex_bench` | 批量求解目录下的 `.lp`，输出结果表 / CSV，并检查解是否可行 |
| `tools/fuzz_vs_highs.py` | 与 HiGHS 逐题对拍（需要 scipy） |
| `tools/bench_compare.py` | 与基线 CSV 对比：结果变了就失败，速度变化只打印 |

对拍示例：

```bash
./build/minicplex_gen --kind mixed --count 400 --seed 1 --out fuzz
./build/minicplex_bench fuzz --gap 1e-9 --quiet --csv fuzz/ours.csv
python3 tools/fuzz_vs_highs.py fuzz fuzz/ours.csv
```

GitHub Actions（`.github/workflows/ci.yml`）在每次提交时自动执行：Linux / macOS 编译与测试、Sanitizer 测试、
500 道随机题与 HiGHS 对拍（每次换随机种子）、基准测试与基线对比。

## 目录结构

```
docs/      PRD.md（产品需求文档）
include/   model.hpp  solver.hpp  lp_reader.hpp
src/       simplex.cpp  branch_and_bound.cpp  lp_reader.cpp  model.cpp  main.cpp
examples/  *.lp  api_demo.cpp  easy1/easy2/hard_* 例子
tools/     gen_random.cpp  bench.cpp  verify_with_highs.py  fuzz_vs_highs.py  bench_compare.py
bench/     models/（基准模型）  baseline.csv  baseline_v0.1.csv
tests/     test_solver.cpp
```

## 后续方向

稀疏 LU 分解的修正单纯形法（扩大到上千规模）、割平面（Gomory 割、覆盖割）、预处理（presolve）、
伪成本分支、MPS 文件支持。详见 PRD 的路线图。

## 许可证

MIT
