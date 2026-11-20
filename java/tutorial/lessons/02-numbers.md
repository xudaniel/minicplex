# 第 2 课：基本类型和小数误差

> **这一课学：** `int`、`long`、`double`、`boolean`；无穷大和 NaN；为什么 `0.1 + 0.2 != 0.3`；怎么比较两个小数
> **用到的代码：** [`Model.java`](../../src/main/java/minicplex/Model.java) 的 `INF`、[`LPEngine.java`](../../src/main/java/minicplex/LPEngine.java) 的容差常量、[`Solver.java`](../../src/main/java/minicplex/Solver.java) 的 `cround`
> **练习：** `java/tutorial/run.sh 02`

[← 第一个程序](01-first-program.md) · [目录](../README.md) · 下一课：[数组和循环 →](03-arrays.md)

## 1. 八种基本类型，常用的四种

| 类型 | 存什么 | minicplex 里的例子 |
|---|---|---|
| `int` | 整数，约 ±21 亿 | 变量编号 `Var(int id)`、行数 `m`、列数 `n` |
| `long` | 更大的整数，约 ±9×10¹⁸ | 节点数 `long nodes`、迭代次数 `long lpIterations`（大题会超过 21 亿） |
| `double` | 小数（双精度浮点数） | 系数、边界、目标值，几乎所有数值 |
| `boolean` | `true` / `false` | `Params.presolve`、`Result.hasSolution` |

另外四种（`byte`、`short`、`char`、`float`）用得少。minicplex 用 `byte` 存每个变量的状态（在下界、在上界、在基里……），因为状态只有几种，`byte` 只占 1 个字节：

```java
// LPEngine.java
static final byte BASIC = 0, LOWER = 1, UPPER = 2, FREE = 3, FIXED = 4, UNSET = -1;
private byte[] stat;   // 每个变量一个状态
```

## 2. 无穷大和 NaN

“变量没有上限”怎么表示？minicplex 用 `double` 自带的无穷大：

```java
// Model.java
public static final double INF = Double.POSITIVE_INFINITY;
```

`static final` 表示“属于类、不能修改的常量”，所以到处都写 `Model.INF`。无穷大可以正常参与比较和运算：`5 < INF` 为真，`INF + 1` 还是 `INF`。

还有一个特殊值 **NaN**（Not a Number，“不是一个数”），比如 `0.0 / 0.0`。`Result.objective` 的初始值就是 NaN，表示“还没有答案”。NaN 有个怪脾气：**它和谁都不相等，包括它自己**。

```java
double v = Double.NaN;
v == v;               // false！
Double.isNaN(v);      // true：判断 NaN 要用这个
Double.isFinite(v);   // false：既不是无穷大也不是 NaN 才算“有限”
```

## 3. 为什么 0.1 + 0.2 != 0.3

`double` 用二进制存小数，就像十进制写不准 1/3（0.333…）一样，二进制也写不准 0.1。所以：

```java
0.1 + 0.2          // 0.30000000000000004
0.1 + 0.2 == 0.3   // false
```

这在求解器里是大事：单纯形法做成千上万次运算，误差一点点积累。**所以 minicplex 从不用 `==` 比较计算出来的小数**，而是规定一个“容差”，差得足够小就算相等：

```java
// LPEngine.java
private static final double PRIMAL_TOL = 1e-7;  // 变量越界多少以内不算越界
private static final double DUAL_TOL = 1e-9;    // 既约成本的容差
private static final double PIVOT_TOL = 1e-9;   // 太小的主元不用
```

`1e-7` 是科学计数法，等于 0.0000001。测试里比较两个数，用的是“相对误差”：

```java
static boolean near(double a, double b, double t) { return Math.abs(a - b) <= t * (1 + Math.abs(b)); }
```

为什么乘 `(1 + |b|)`？比较 1,000,000 和 1,000,000.001 时，差 0.001 已经算非常准了；比较 0.001 和 0.002 时，差 0.001 就是差了一倍。容差跟着数的大小走，大数小数都公平。

## 4. 四舍五入，有两种

分支定界时要判断“这个变量是不是整数”，还要把 2.9999999 当成 3。Java 有好几个取整函数：

| 函数 | 2.5 | −2.5 | 2.7 | −2.7 |
|---|---|---|---|---|
| `Math.floor`（向下） | 2 | −3 | 2 | −3 |
| `Math.ceil`（向上） | 3 | −2 | 3 | −2 |
| `Math.rint`（最近，.5 取偶数） | 2 | −2 | 3 | −3 |
| `Math.round`（最近，.5 向上） | 3 | **−2** | 3 | −3 |
| C++ 的 `std::round`（.5 远离 0） | 3 | **−3** | 3 | −3 |

Java 版是从 C++ 版逐行移植的，要和 C++ 算得一模一样，所以 minicplex 自己写了一个模仿 C++ 的版本：

```java
// Solver.java
/** C++ std::round: halfway cases away from zero (Math.round/rint behave differently). */
static double cround(double v) { return Math.signum(v) * Math.floor(Math.abs(v) + 0.5); }
```

这种差异平时看不出来，一旦出现就很难查。移植代码时，**每一个“看起来一样”的库函数都要核对**。

## 5. 常见坑

- **整数除法**：`7 / 2` 是 3（两个 `int` 相除，小数部分直接丢掉）。要得到 3.5，写 `7.0 / 2`。
- **整数溢出**：`int` 超过 21 亿会“绕回”变成负数，不报错。计数可能很大时用 `long`。
- **用 `==` 比较小数**：除了和 0、无穷大这类“精确值”比较，都要用容差。
- **NaN 会传染**：任何数和 NaN 运算结果都是 NaN，比较结果都是 false，一个 NaN 能让整个计算悄悄出错。

## 6. 动手

练习 [`L02Numbers.java`](../exercises/minicplex/tutorial/L02Numbers.java) 有四个小函数：`near`、`isIntegral`、`fractionalPart`、`roundHalfAway`。它们在 minicplex 里都有对应的实现，写完可以去源代码里对照。

```bash
java/tutorial/run.sh 02
```

## 7. 想一想

1. `fractionalPart(-1.25)` 为什么是 0.75，而不是 0.25？分支定界里用哪个更合适？
2. 节点数为什么用 `long` 而不用 `int`？

<details>
<summary>参考答案</summary>

1. 定义是 `v − floor(v)`，−1.25 向下取整是 −2，所以是 0.75。分支时要分成 `x ≤ −2` 和 `x ≥ −1` 两支，“离下面的整数有多远”正好是 0.75，用这个定义，正数负数的处理就统一了。
2. 大题可以搜索上亿个节点，单纯形迭代次数更多。`int` 最大约 21 亿，溢出后会变成负数而且不报错；`long` 够用到 9×10¹⁸。

</details>

[← 第一个程序](01-first-program.md) · [目录](../README.md) · 下一课：[数组和循环 →](03-arrays.md)
