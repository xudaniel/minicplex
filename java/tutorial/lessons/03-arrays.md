# 第 3 课：数组和循环

> **这一课学：** 一维、二维数组；`for` 和增强 `for`；把矩阵存进一维数组；用二进制位枚举所有组合
> **用到的代码：** [`LPEngine.java`](../../src/main/java/minicplex/LPEngine.java) 的矩阵存储、[`Basics08MinMax.java`](../../examples/minicplex/examples/Basics08MinMax.java)、[`Solver.java`](../../src/main/java/minicplex/Solver.java) 的伪成本表
> **练习：** `java/tutorial/run.sh 03`

[← 数字和小数误差](02-numbers.md) · [目录](../README.md) · 下一课：[类和对象 →](04-classes.md)

## 1. 数组：一排同类型的格子

```java
double[] hours = {5, 4, 3, 3, 2, 1};   // 直接写出内容
double[] lb = new double[n];           // 长度 n，元素默认都是 0.0
hours.length                           // 长度 6（注意不是 length()）
hours[0]                               // 第一个是 5；最后一个是 hours[hours.length - 1]
```

数组一旦建好，**长度就不能变**。要能增删元素，用下一课以后的 `ArrayList`。

## 2. 二维数组：数组的数组

例子 08 要把 6 件任务分给 3 个人，变量 `give[t][p]` 表示“任务 t 交给第 p 个人”：

```java
// Basics08MinMax.java
Var[][] give = new Var[tasks][people];
for (int t = 0; t < tasks; ++t)
    for (int p = 0; p < people; ++p)
        give[t][p] = m.addVar(0, 1, VarType.BINARY, "give_" + t + "_" + p);
```

`new Var[6][3]` 其实是“6 个数组，每个装 3 个 `Var`”。所以每一行也可以不一样长，伪成本表就是先建外层、再分别建内层：

```java
// Solver.java 的 PseudoCosts
final double[][] sum = new double[2][];          // 2 行：向下分支、向上分支，每行先空着
for (int d = 0; d < 2; ++d) sum[d] = new double[n];   // 每行 n 个变量
```

## 3. 把矩阵压进一维数组

单纯形法的核心是一张 m 行、N 列的大表。minicplex **没有**用 `double[m][N]`，而是用一个长度 m × N 的一维数组，一行接一行地排：

```java
// LPEngine.java
private final double[] A;  // original constraint matrix, m x n (row major)
...
A = new double[m * n];
for (int i = 0; i < m; ++i)
    for (Map.Entry<Integer, Double> t : con.coefs.entrySet()) A[i * n + t.getKey()] += t.getValue();
...
private double T(int i, int j) { return T[i * N + j]; }   // 第 i 行第 j 列
```

```
二维：  [a b c]      一维：  [a b c d e f]
        [d e f]               0 1 2 3 4 5      第 1 行第 2 列 = 1 × 3 + 2 = 5
```

为什么这样做？Java 的二维数组是“数组的数组”，每一行是一个单独的对象，散落在内存各处；一维数组在内存里是连续的一整块，CPU 读起来快得多（缓存友好），换基时整行整行地更新，速度差别很明显。这是性能敏感代码的常见写法。

## 4. 三种循环

```java
for (int j = 0; j < n; ++j) sum += a[j];        // 普通 for：需要下标时用
for (double h : home) mean += h / home.length;  // 增强 for：只要元素、不要下标时用（Basics09AbsoluteValue）
while (i < n) { ... }                            // while：不知道要转几圈时用（LpReader 扫描字符）
```

`break` 跳出循环，`continue` 跳过这一圈剩下的部分、直接开始下一圈。

## 5. 用二进制位枚举所有选法

n 件物品，每件选或不选，一共 2ⁿ 种选法。一个巧妙的写法：把 0 到 2ⁿ − 1 的每个整数看成一串二进制位，第 k 位是 1 就表示选了第 k 件：

```java
for (int mask = 0; mask < (1 << n); ++mask)     // 1 << n 就是 2 的 n 次方
    for (int k = 0; k < n; ++k)
        if (((mask >> k) & 1) == 1) { /* 选了第 k 件 */ }
```

```
n = 3：mask = 5 = 二进制 101 → 选第 0 件和第 2 件
```

这就是“暴力枚举”。它慢（n = 30 就要试 10 亿次），但**绝对可靠**，所以 minicplex 的测试用它当标准答案，检查求解器算得对不对（第 11 课细讲）。

## 6. 常见坑

- **越界**：下标从 0 开始，最大是 `length - 1`。越界会抛 `ArrayIndexOutOfBoundsException`。
- **数组变量是“引用”**：`double[] b = a;` 不会复制数组，`a` 和 `b` 指向同一块内存，改 `b[0]` 就是改 `a[0]`。要复制，用 `a.clone()`（第 5 课细讲）。
- **`length` 和 `length()`**：数组是 `.length`（字段），字符串是 `.length()`（方法），列表是 `.size()`。

## 7. 动手

练习 [`L03Arrays.java`](../exercises/minicplex/tutorial/L03Arrays.java)：

1. `flatIndex`、`rowSum`：一维数组当矩阵用；
2. `bruteForceKnapsack`：用二进制位暴力解背包；
3. `solverKnapsack`：用 minicplex 解同一个背包。

最后一项检查会生成 20 道随机背包，要求两种解法的答案完全一致。

```bash
java/tutorial/run.sh 03
```

## 8. 想一想

1. 暴力枚举 n = 20 件物品要试多少种？n = 40 呢？
2. 如果把 `LPEngine` 的表换成 `double[][]`，代码哪里要改？

<details>
<summary>参考答案</summary>

1. 2²⁰ ≈ 100 万，一眨眼；2⁴⁰ ≈ 1.1 万亿，要算好几个小时。这就是需要分支定界的原因：它靠“剪枝”跳过绝大部分组合。
2. 所有 `T[i * N + j]` 改成 `T[i][j]`，`new double[m * N]` 改成 `new double[m][N]`，复制时要逐行复制。因为访问都集中在 `T(i, j)` 这个小方法里，大部分代码其实不用动：这也是把访问封装成方法的好处。

</details>

[← 数字和小数误差](02-numbers.md) · [目录](../README.md) · 下一课：[类和对象 →](04-classes.md)
