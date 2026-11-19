# minicplex

一个用 **C++17 编写、零依赖的线性规划 / 混合整数规划（LP / MIP）求解器**。这是一个业余项目，目的是从内部
理解 IBM ILOG CPLEX 这类求解器的工作原理。它能读取 CPLEX `.lp` 文件，提供类似 Concert 的 C++ 建模 API，
并输出类似 CPLEX 的分支定界日志。

> 与 IBM 无关。这是一个学习项目，不是 CPLEX 的替代品：它使用稠密单纯形表，适合中小规模模型
>（几百行 / 几百列）。

产品需求文档见 [docs/PRD.md](docs/PRD.md)。

## 功能一览

| 模块 | 已实现内容 |
|---|---|
| 线性规划 | 两阶段原始单纯形法（稠密单纯形表）；Dantzig 定价规则，出现退化时自动切换 Bland 规则防止循环 |
| 变量边界 | 上下界、自由变量、负边界、固定变量 |
| 约束 | `<=`、`>=`、`=`，右端项为负，冗余约束 |
| 整数规划 | 最优界优先的分支定界、最分数变量分支、取整启发式、整数目标函数的界加强 |
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
| `examples/hard_production_plan.cpp` | 混合整数规划（复杂） | 3 产品 × 6 周生产排程：换线、最小批量、加班、仓储；最低成本 35,615 元（约 5,300 个节点，0.5 秒，与 HiGHS 结果一致） |
| `examples/hard_staff_schedule.cpp` | 0-1 整数规划（复杂） | 餐厅 8 人一周排班：覆盖需求、老员工坐镇、晚班后不接早班、连续上班 ≤ 3 天、新人带教、两人不同班；最低成本 6,571 元（239 个节点，0.8 秒，与 HiGHS 结果一致） |

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

1. **转为标准型**（`src/simplex.cpp`）：每个变量按其有限边界平移（`x = l + y` 或 `x = u - y`），
   自由变量拆分为 `x = y⁺ - y⁻`；有限区间转为额外约束行；再加入松弛、剩余和人工变量，
   得到 `A y = b, y ≥ 0, b ≥ 0`。
2. **第一阶段**最小化人工变量之和（求可行解），再把残留的人工变量换出基；
   **第二阶段**优化真正的目标函数。
3. **分支定界**（`src/branch_and_bound.cpp`）：在每个节点求 LP 松弛，用界剪枝，
   在最“分数”的整数变量上分支，并总是先探索界最好的节点；取整启发式用来尽早找到可行解。

## 测试

`tests/test_solver.cpp` 覆盖：教科书 LP、不可行 / 无界判定、自由变量、Beale 循环反例、背包问题、
LP 文件读写往返，以及 **500 个随机整数规划与暴力枚举结果逐一对比**（全部一致）。

## 目录结构

```
docs/      PRD.md（产品需求文档）
include/   model.hpp  solver.hpp  lp_reader.hpp
src/       simplex.cpp  branch_and_bound.cpp  lp_reader.cpp  model.cpp  main.cpp
examples/  *.lp  api_demo.cpp  easy1/easy2/hard_* 例子
tools/     verify_with_highs.py（用 HiGHS 验算）
tests/     test_solver.cpp
```

## 后续方向

带 LU 分解的修正单纯形法、用对偶单纯形热启动分支定界节点、割平面（Gomory 割、覆盖割）、
预处理（presolve）、伪成本分支、MPS 文件支持。详见 PRD 的路线图。

## 许可证

MIT
