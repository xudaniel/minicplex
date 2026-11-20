# 入门 A6：列表——一次存一排数

> **这一课学：** 列表 `[...]`；下标；`len`；`for x in 列表`；`append`；`sum`、`max`
> **大约：** 20 分钟 · **练习：** `python3 python/tutorial/run.py A06`
> **在线做：** [打开网页版，不用安装](https://xudaniel.github.io/minicplex/python/#a06)

[← 自己写函数](a5-functions.md) · [目录](../README.md) · 下一课：[字符串 →](a7-strings.md)

## 1. 列表

```python
week = [8200, 6500, 12000, 4300, 9100, 15000, 7600]   # 一周的步数
week[0]       # 8200   ← 下标从 0 开始
week[-1]      # 7600   ← 负数从后往前数
len(week)     # 7
week[2] = 0   # 可以改
```

## 2. 遍历：一个个看

```python
for x in week:          # x 依次是每一天的步数
    if x >= 8000:
        count += 1
```

需要下标时用 `enumerate`：`for i, x in enumerate(week):`，`i` 是第几天，`x` 是那天的步数。

## 3. 造一个新列表

```python
out = []                # 空列表
for x in nums:
    out.append(x * 2)   # 往后面加一个
```

熟练以后可以写成一行“推导式”：`[x * 2 for x in nums]`（第 3 课细讲）。

## 4. 内置函数

`sum(week)`、`max(week)`、`min(week)`、`sorted(week)` 都是现成的。练习里先自己用循环写一遍，弄懂它们是怎么工作的；以后直接用内置的。

> **minicplex 里的例子：** 求解结果 `r.x` 就是一个列表，`r.x[j]` 是第 j 个变量的值。
> 例子 [`basics_08_min_max.py`](../../examples/basics_08_min_max.py) 用列表存“每个任务要几小时”，再用循环把每个人分到的任务加起来。

## 5. 常见错误

- `week[7]`：一共 7 个，最后一个是 `week[6]`，越界会报 `IndexError`。
- “最大值”的初始值写成 `0`：全是负数时就错了。应该从第一个元素开始比。
- 空列表求平均：`len([])` 是 0，会除以零。

## 6. 动手

打开 [`exercises/a06_lists.py`](../exercises/a06_lists.py)，运行 `python3 python/tutorial/run.py A06`。

## 7. 想一想

`a = [1, 2]`，`b = a`，`b.append(3)`，这时 `a` 是什么？

<details><summary>答案</summary>

`[1, 2, 3]`。`b = a` 没有复制列表，只是给**同一个**列表起了第二个名字。想要复制，写 `b = list(a)` 或 `b = a.copy()`。
这个“别名”问题在第 3 课和第 5 课还会遇到：求解器为什么到处复制列表，就是为了避免它。

</details>

[← 自己写函数](a5-functions.md) · [目录](../README.md) · 下一课：[字符串 →](a7-strings.md)
