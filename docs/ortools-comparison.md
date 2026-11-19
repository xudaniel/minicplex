# 与 Google OR-Tools 对拍记录（2026-11-19）

**结论：** 1,030 道随机题（混合整数 1,000、纯 LP 30），minicplex 与 OR-Tools 的结论全部一致。纯 LP 上，minicplex 的单纯形迭代次数中位数是 GLOP 的 1.15 倍（总计 3,226 对 2,893）。

**最大收获：** OR-Tools 的 MPSolver 会把 GLOP 的“不可行或无界”报成“不可行”，第一组 500 道题中有 69 道受影响；LP 松弛无界的整数题，SCIP 会一直搜索下去。两处都已在 `tools/verify_with_ortools.py` 里处理。

## 1. 对拍结果

| 批次 | 题数 | 一致 | OR-Tools 给出的状态分布 |
|---|---|---|---|
| 混合整数，种子 42 | 500 | 500 | SCIP 最优 375、SCIP 不可行 36、SCIP 不可行或无界 73、GLOP 最优 13、GLOP 不可行 3 |
| 混合整数，种子 7 | 500 | 500 | SCIP 最优 372、SCIP 不可行 38、SCIP 不可行或无界 72、GLOP 最优 15、GLOP（关预处理）无界 3 |
| 纯 LP，种子 5（60 变量 × 50 约束） | 30 | 30 | GLOP 最优 30 |

- **判定规则：** 沿用 `tools/fuzz_vs_highs.py` 的 `agree()`。最优要求目标值相对误差 ≤ 1e-6；minicplex 报“不可行或无界”时，对方报不可行、无界或二者之一都算一致；minicplex 触到节点上限时，只要当前解等于对方的最优值也算一致。
- **裁判：** 与 OR-Tools 不一致时，脚本再调用 HiGHS，标注“OR-Tools 与 HiGHS 一致 → 多半是 minicplex 的问题”或“三方不一致 → 需要人工判断”。本次没有触发。
- **耗时：** 种子 42 那组 500 题，修复前因为 SCIP 卡住，超过 10 分钟仍未结束；修复后 3.6 秒。

## 2. 案例：同一道 LP，GLOP 说不可行，HiGHS 说无界

题目 `mixed_s42_0313.lp`（12 个变量、3 条约束，最大化），minicplex 报“不可行或无界”。

| 求解器与设置 | LP 松弛的结论 |
|---|---|
| HiGHS | 无界；只求可行解时能找到可行点，说明它不是不可行 |
| GLOP，开预处理（默认） | 不可行 |
| GLOP，关预处理 | 无界 |

**原因（读源码确认）：** `ortools/linear_solver/glop_utils.cc` 里的 `GlopToMPSolverResultStatus` 把 GLOP 的 `InfeasibleOrUnbounded` 映射成 `MPSolver::INFEASIBLE`。源码注释说明这是刻意的：MPSolver 没有“不可行或无界”这个状态，团队认为实际应用里很少遇到无界；历史上报过 ABNORMAL，觉得更难懂，所以改报 INFEASIBLE。GLOP 的预处理只能判断到“二者之一”时，就会走到这一支。

GLOP 状态到 MPSolver 状态的完整映射（同一函数）：

| GLOP 状态 | MPSolver 报告 |
|---|---|
| Optimal | OPTIMAL |
| PrimalInfeasible | INFEASIBLE |
| DualInfeasible | UNBOUNDED |
| InfeasibleOrUnbounded | **INFEASIBLE**（坑） |
| PrimalUnbounded | UNBOUNDED |
| DualUnbounded | INFEASIBLE |
| PrimalFeasible | FEASIBLE |
| DualFeasible、Init | NOT_SOLVED |
| Imprecise、Abnormal、InvalidProblem | ABNORMAL |

**影响面：** 种子 42 那组里，脚本判为“不可行或无界”的 73 道整数题中，有 69 道的 LP 松弛被 GLOP（开预处理）报成不可行；关掉预处理后都是无界，HiGHS 也都判无界。另外 4 道两种设置都直接报无界。

**处理：** GLOP 报不可行时，关掉预处理再解一次，以第二次的结论为准。

**启示：** 看到“不可行”不能直接下结论，要问清是哪一层、在什么设置下得出的。minicplex 自己区分了 `Infeasible` 和 `InfeasibleOrUnbounded`，在这一点上比 MPSolver 的接口更诚实。

<details>
<summary>mixed_s42_0313.lp 原文</summary>

```
\ Written by minicplex
Maximize
 obj: - 3 x1 + x3 - 2 x4 + x5 + 4 x6 + 5 x8
   - 2 x9 + 2 x10 - 3 x11 - 3 x12
Subject To
 c1: + 3 x1 + 0.5 x2 - 2.5 x4 - 6 x5 - 2 x6 + 2 x7
   + 5 x9 + 6 x11 + 5 x12 = 109.470909355155
 c2: - 3.5 x3 - 5 x4 + 5 x7 + 6 x8 + 3 x9 + 3 x10
   - 4 x12 <= 41
 c3: - 4 x3 + 2.5 x8 + 2 x9 - 5 x10 >= 31
Bounds
 0 <= x1 <= 9
 0 <= x2 <= 5
 0 <= x3 <= 9
 -inf <= x5 <= 3
 -3 <= x6 <= -2
 -inf <= x7 <= 8
 -inf <= x8 <= 4
 -inf <= x9 <= 10
 x10 free
 0 <= x11 <= 8
General
 x2
 x5
 x6
 x7
 x9
Binary
 x4
 x12
End
```

</details>

## 3. 案例：LP 松弛无界的整数题，SCIP 停不下来

- **现象：** `mixed_s42_0079.lp` 和 `mixed_s42_0313.lp` 单独交给 SCIP，5 秒内都不返回。minicplex 都在 1 个节点内报“不可行或无界”，HiGHS 判无界。
- **原理：** Meyer 定理（数据为有理数）：整数规划可行且 LP 松弛无界 ⇒ 整数规划无界。所以松弛无界时，原题只能是“不可行或无界”，不必再搜索。
- **处理：** 整数题先用 GLOP 解 LP 松弛（含上面的关预处理复核），无界就直接返回“不可行或无界”；另外给 SCIP 设了 10 秒时间上限。

## 4. 纯 LP 迭代次数对比（30 题，60 变量 × 50 约束）

- **汇总：** minicplex 共 3,226 次换基，GLOP 共 2,893 次；比值中位数 1.15，最低 0.72，最高 1.92。minicplex 每题耗时 0.5–1.2 毫秒。
- **口径：** GLOP 默认先做预处理，迭代次数是在预处理后的模型上数的；minicplex 用稠密单纯形表、每行一个松弛变量。两者不是在同一规模的模型上比较，只作参考。

| 模型 | 最优目标值（两边一致） | minicplex 迭代 | GLOP 迭代 |
|---|---|---|---|
| lp_s5_0000 | 3774.52 | 76 | 105 |
| lp_s5_0001 | 2457.93 | 121 | 83 |
| lp_s5_0002 | -1200.26 | 116 | 97 |
| lp_s5_0003 | 2104.12 | 182 | 122 |
| lp_s5_0004 | -2076.3 | 99 | 96 |
| lp_s5_0005 | -613.656 | 123 | 88 |
| lp_s5_0006 | 1770.05 | 121 | 96 |
| lp_s5_0007 | 2640.43 | 77 | 95 |
| lp_s5_0008 | 2871.43 | 85 | 96 |
| lp_s5_0009 | -2451.81 | 116 | 102 |
| lp_s5_0010 | 1680.16 | 89 | 101 |
| lp_s5_0011 | 897.883 | 102 | 88 |
| lp_s5_0012 | -1177.75 | 79 | 100 |
| lp_s5_0013 | 2965.38 | 94 | 97 |
| lp_s5_0014 | -1548.66 | 125 | 83 |
| lp_s5_0015 | -1143.95 | 115 | 102 |
| lp_s5_0016 | -1386.01 | 112 | 92 |
| lp_s5_0017 | -2439.57 | 129 | 106 |
| lp_s5_0018 | -2206.58 | 105 | 73 |
| lp_s5_0019 | -1969.4 | 125 | 111 |
| lp_s5_0020 | -2579.31 | 137 | 106 |
| lp_s5_0021 | -2261.09 | 106 | 91 |
| lp_s5_0022 | 3069.85 | 115 | 94 |
| lp_s5_0023 | 2211.96 | 121 | 63 |
| lp_s5_0024 | 2333.76 | 106 | 90 |
| lp_s5_0025 | 883.734 | 89 | 91 |
| lp_s5_0026 | -1768.02 | 75 | 96 |
| lp_s5_0027 | 2778.71 | 97 | 102 |
| lp_s5_0028 | -1690.88 | 105 | 127 |
| lp_s5_0029 | 2034.94 | 84 | 100 |

**待追问：** `lp_s5_0023` 上 minicplex 多用了将近一倍的迭代（121 对 63）。是 GLOP 的预处理删掉了行列，还是它的定价规则（对偶 steepest edge）选得更好？关掉 GLOP 的预处理再比一次就能区分。

## 5. 复现

```bash
pip install ortools numpy scipy
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build -j

# 混合整数 500 题
./build/minicplex_gen --kind mixed --count 500 --seed 42 --out fuzz
./build/minicplex_bench fuzz --gap 1e-9 --nodes 200000 --quiet --csv fuzz/ours.csv
python3 tools/fuzz_vs_ortools.py fuzz fuzz/ours.csv

# 纯 LP 30 题
./build/minicplex_gen --kind lp --count 30 --seed 5 --vars 60 --cons 50 --out fuzz_lp
./build/minicplex_bench fuzz_lp --quiet --csv fuzz_lp/ours.csv
python3 tools/fuzz_vs_ortools.py fuzz_lp fuzz_lp/ours.csv

# 单题验算
python3 tools/verify_with_ortools.py examples/*.lp
```

环境：OR-Tools Python 包 9.15.6755、SciPy 1.18.1；minicplex 基于提交 e801bcf；OR-Tools 源码为 google/or-tools main 分支提交 604c374。
