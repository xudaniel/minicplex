# 入门 A4：重复做事

> **这一课学：** `for` 和 `range`；`while`；累加器；`break`
> **大约：** 20 分钟 · **练习：** `python3 python/tutorial/run.py A04`
> **在线做：** [打开网页版，不用安装](https://xudaniel.github.io/minicplex/python/#a04)

[← 做判断](a3-decisions.md) · [目录](../README.md) · 下一课：[自己写函数 →](a5-functions.md)

## 1. for：做固定的次数

```python
for i in range(5):        # i 依次是 0, 1, 2, 3, 4
    print(i)

for i in range(1, 11):    # 1 到 10（不含 11）
    total += i
```

`range(a, b)` 从 `a` 开始，**不包括** `b`。所以“1 到 n”要写 `range(1, n + 1)`。

## 2. 累加器：一边循环一边攒结果

```python
total = 0                 # 先准备一个空的“篮子”
for i in range(1, n + 1):
    total += i            # 每次往里加一点
return total              # 循环结束后再交出去
```

数个数也是一样：`count = 0`，满足条件时 `count += 1`。

## 3. while：做到条件不成立为止

不知道要做几次时，用 `while`：

```python
saved, days = 0, 0
while saved < target:     # 还没存够，就继续
    saved += per_day
    days += 1
```

一定要让循环里的某个东西变化，否则条件永远成立，程序就“死循环”了（按 Ctrl+C 停下来）。

> **minicplex 里的例子：** 单纯形法就是一个 `while True:` 循环（[`lp_engine.py`](../../minicplex/lp_engine.py) 的 `_primal`），
> 每次改进一点，直到找不到能改进的方向就 `return OPTIMAL`。为了防止死循环，它还数着步数，超过上限就 `return ITERATION_LIMIT`。

## 4. 常见错误

- `range(1, n)` 少了最后一个数（应当是 `range(1, n + 1)`）。
- 累加器放进了循环里：`total = 0` 每一轮都被清零。
- `return` 缩进进了循环：第一轮就返回了。

## 5. 动手

打开 [`exercises/a04_loops.py`](../exercises/a04_loops.py)，运行 `python3 python/tutorial/run.py A04`。

## 6. 想一想

`for i in range(10, 0, -2)` 会得到哪些数？

<details><summary>答案</summary>

`10, 8, 6, 4, 2`。第三个参数是“步长”，可以是负数，倒着数。同样不包括终点 `0`。

</details>

[← 做判断](a3-decisions.md) · [目录](../README.md) · 下一课：[自己写函数 →](a5-functions.md)
