# 第 3 课：列表、循环和推导式

> **这一课学：** 一维列表存二维表格；切片；推导式和生成器表达式；`zip`、`enumerate`、`itertools.product`；`[[0] * n] * m` 的坑
> **用到的代码：** [`lp_engine.py`](../../minicplex/lp_engine.py) 的 `T[i * N + j]` 和 `_pivot`、[`basics_08_min_max.py`](../../examples/basics_08_min_max.py)
> **练习：** `python3 python/tutorial/run.py 03`

[← 数字和小数误差](02-numbers.md) · [目录](../README.md) · 下一课：[类和对象 →](04-classes.md)

## 1. 把表格压扁成一行

单纯形表是 m 行 N 列的表格。minicplex 没有用“列表的列表”，而是存成一个长度为 m × N 的一维列表（[`lp_engine.py`](../../minicplex/lp_engine.py)）：

```python
T = [0.0] * (m * N)
for i in range(m):
    base = i * N              # 第 i 行从这里开始
    for j in range(n):
        T[base + j] = -A[i * n + j]
```

第 i 行第 j 列在 `T[i * N + j]`。反过来，第 k 个数在第 `k // N` 行、第 `k % N` 列（A2 学的整除和取余）。

为什么这样存？只有一个列表，复制一次就是 `list(T)`；Java 和 C++ 版也是同样的存法，三个版本可以逐行对照。

## 2. 推导式：一行造一个列表

```python
squares = [x * x for x in range(5)]                    # [0, 1, 4, 9, 16]
evens = [x for x in nums if x % 2 == 0]                 # 带条件
names = [v.name for v in M.vars]                        # minicplex 里到处都是这种写法
grid = [[0] * n for _ in range(m)]                      # m 行 n 列的二维列表
```

换成圆括号就是**生成器表达式**：不先造出整个列表，而是要一个算一个，省内存。传给 `sum`、`max` 时最常用：

```python
sum(hours[t] * give[t][p] for t in range(tasks))        # basics_08_min_max.py：第 p 个人的工作量
```

## 3. zip、enumerate、itertools.product

```python
for w, t in zip(weights, take):        # 两个列表配对走
for i, name in enumerate(names):       # 同时拿到下标和值
for pick in itertools.product([0, 1], repeat=3):   # (0,0,0), (0,0,1), …, (1,1,1)：所有 0/1 组合
```

## 4. 一个经典的坑

```python
grid = [[0] * 3] * 2      # 看起来是 2 行 3 列
grid[0][0] = 99
print(grid)               # [[99, 0, 0], [99, 0, 0]]  ← 两行一起变了！
```

`* 2` 复制的是“指向同一个内层列表的引用”，两行其实是同一个列表（A6 讲过的别名）。
正确写法是推导式：`[[0] * 3 for _ in range(2)]`，每一轮都新建一个内层列表。
`[0] * 3` 本身没问题，因为数字不能改，共用也不怕。

## 5. 优化：把“查表”提到循环外

`_pivot` 是整个求解器最热的地方（每次转轴都要更新整张表）：

```python
prow = [(j, T[pr + j]) for j in nz]     # 先把转轴行里非零的列和值拿出来
for i in range(self.m):
    ...
    for j, t in prow:                   # 每一行只遍历非零的那些列
        T[pi + j] -= f * t
```

在 Python 里，循环次数和“每次循环里查了几次东西”都很要紧。提前把要用的值放进局部列表，比在循环里反复算 `T[pr + j]` 快不少。

## 6. 动手

打开 [`exercises/l03_lists.py`](../exercises/l03_lists.py)：压扁矩阵的取值和行和、正确的二维列表、暴力背包，最后用求解器解同一个背包，两边对答案。运行 `python3 python/tutorial/run.py 03`。

## 7. 想一想

暴力背包试了 2ⁿ 种组合。n = 8 时是 256 种，n = 40 时呢？

<details><summary>答案</summary>

2⁴⁰ ≈ 1.1 万亿种。每秒试一百万种，要将近两个星期。求解器用分支定界，通常只看几十到几千个节点。
这就是为什么暴力法只适合拿来**验证**求解器（第 11 课），而不能拿来解题。

</details>

[← 数字和小数误差](02-numbers.md) · [目录](../README.md) · 下一课：[类和对象 →](04-classes.md)
