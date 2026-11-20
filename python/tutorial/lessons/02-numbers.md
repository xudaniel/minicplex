# 第 2 课：数字和小数误差

> **这一课学：** `int` 和 `float`；浮点误差；相对误差比较；无穷大和 NaN；三种“四舍五入”；`-0.0`
> **用到的代码：** [`jmath.py`](../../minicplex/jmath.py)、[`lp_engine.py`](../../minicplex/lp_engine.py) 开头的容差常量和 `_is_integral`
> **练习：** `python3 python/tutorial/run.py 02`
> **在线做：** [打开网页版，不用安装](https://xudaniel.github.io/minicplex/python/#l02)

[← 第一个模型](01-first-model.md) · [目录](../README.md) · 下一课：[列表和推导式 →](03-lists.md)

## 1. 0.1 + 0.2 ≠ 0.3

```python
>>> 0.1 + 0.2
0.30000000000000004
```

计算机用二进制存小数，`0.1` 在二进制里是无限循环小数，只能存一个近似值。每次计算都可能带一点点误差。
求解器做上百万次加减乘除，误差会累积，所以**永远不用 `==` 比较两个算出来的小数**，而是问“够不够接近”。

## 2. 容差：多近算“接近”？

[`lp_engine.py`](../../minicplex/lp_engine.py) 开头：

```python
PRIMAL_TOL = 1e-7   # 允许的越界量（按大小缩放）
DUAL_TOL = 1e-9     # 既约成本的容差
PIVOT_TOL = 1e-9    # 能接受的最小转轴元
```

注意“按大小缩放”：

```python
tl = PRIMAL_TOL * (1.0 + abs(lb))
```

同样差 0.5，`1` 和 `1.5` 差得很远，`1000000000` 和 `1000000000.5` 却几乎一样。所以用**相对误差**：
`|a - b| ≤ tol × (1 + |b|)`。加 1 是为了 `b` 接近 0 时不至于要求“完全相等”。
标准库里也有现成的：`math.isclose(a, b, rel_tol=1e-9, abs_tol=0.0)`。

## 3. 无穷大和 NaN

```python
from math import inf, nan, isfinite   # minicplex 的 INF 就是 math.inf，表示“没有上界”：add_var(0, INF)
inf > 1e308             # True
inf - inf               # nan（Not a Number：“算不出来”）
nan == nan              # False！NaN 和谁都不相等，包括它自己
isfinite(3.0), isfinite(inf), isfinite(nan)   # True False False
```

判断“是不是整数”之前，先排除无穷大和 NaN（[`lp_engine.py`](../../minicplex/lp_engine.py)）：

```python
def _is_integral(v):
    return _isfinite(v) and abs(v - jmath.rint(v)) < 1e-9
```

## 4. 三种“四舍五入”

| 写法 | 2.5 | -2.5 | 3.5 | 规则 |
|---|---|---|---|---|
| `round(v)`（Python） | 2 | -2 | 4 | 一半时取**偶数**（银行家舍入） |
| `math.floor(v + 0.5)` | 3 | -2 | 4 | 一半时往上 |
| C++ `std::round` | 3 | -3 | 4 | 一半时**远离 0** |

minicplex 要和 C++ 版每一步都算得一模一样，所以不能用 Python 的 `round`，而是自己写了一个（[`jmath.py`](../../minicplex/jmath.py)）：

```python
def cround(v):
    """C++ 的 std::round：正好一半时远离 0。"""
    s = 1.0 if v > 0 else -1.0 if v < 0 else v
    return s * floor(abs(v) + 0.5)
```

## 5. 连 -0.0 都要管

浮点数里有 `+0.0` 和 `-0.0`，`0.0 == -0.0` 是 `True`，但打印出来不一样（`-0`）。
Python 的 `math.ceil(-0.5)` 返回整数 `0`，丢掉了负号；Java 和 C++ 返回 `-0.0`。
为了三个版本连打印结果都一样，[`jmath.py`](../../minicplex/jmath.py) 里的 `ceil`、`floor` 都用 `math.copysign` 把符号补回来。

这听起来很较真，但正是这种较真，才能在 CI 里要求“Python 版和 C++ 版在 600 道随机题上走完全相同的计算路径”——差一点点，路径就会分叉。

## 6. 常见错误

- `if x == 0.3:` 比较算出来的小数。
- 把“不可行”和“算不出来”混为一谈：NaN 会让所有比较都是 `False`，悄悄跳过检查。
- 以为 `round` 就是小学学的四舍五入。

## 7. 动手

打开 [`exercises/l02_numbers.py`](../exercises/l02_numbers.py)，写 `near`、`is_integral`、`cround`、`fractionality`，运行 `python3 python/tutorial/run.py 02`。

## 8. 想一想

为什么 `1e16 + 1 == 1e16` 是 `True`？

<details><summary>答案</summary>

`float` 只有大约 16 位有效数字。`1e16` 附近，相邻两个能表示的数相差 2，`+1` 被舍掉了。
所以求解器里很大的数和很小的数混在一起时（例如大 M 约束里的 `1000000`），小的那部分会“消失”，这也是进阶例子 07 里大 M 要取得尽量小的原因之一。
Python 的 `int` 没有这个问题：`10**16 + 1` 精确等于 `10000000000000001`。

</details>

[← 第一个模型](01-first-model.md) · [目录](../README.md) · 下一课：[列表和推导式 →](03-lists.md)
