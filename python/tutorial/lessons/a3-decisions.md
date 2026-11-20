# 入门 A3：做判断

> **这一课学：** `True` 和 `False`；比较 `== != < <= > >=`；`if / elif / else`；`and`、`or`、`not`
> **大约：** 15 分钟 · **练习：** `python3 python/tutorial/run.py A03`
> **在线做：** [打开网页版，不用安装](https://xudaniel.github.io/minicplex/python/#a03)

[← 变量和计算](a2-variables.md) · [目录](../README.md) · 下一课：[重复做事 →](a4-loops.md)

## 1. 比较的结果是真或假

```python
10 >= 8     # True
10 == 12    # False   ← 两个等号才是“等于”
"a" != "b"  # True    ← != 是“不等于”
```

`True` 和 `False` 是 `bool`（布尔）类型，只有这两个值。函数可以直接 `return money >= cost`，不用写成“如果……就返回 True，否则返回 False”。

## 2. if / elif / else

```python
if score >= 90:
    return "优秀"
elif score >= 75:      # elif = else if：上面的不成立，再看这一条
    return "良好"
else:
    return "不及格"
```

- 条件后面要有冒号 `:`，下面的代码要缩进。
- 从上往下判断，**第一个**成立的那一段被执行，后面的就不看了。所以分数要从高往低判断。

## 3. and、or、not

```python
height >= 120 and age >= 8     # 两个都成立才成立
is_weekend or is_holiday       # 有一个成立就成立
not enough(10, 12)             # 反过来
8 <= age <= 60                 # Python 特有：连着写，等于 8 <= age and age <= 60
```

> **minicplex 里的例子：** 求解器判断一个变量是不是“固定”的：`if lf and uf and lb == ub: return FIXED`
>（[`lp_engine.py`](../../minicplex/lp_engine.py) 的 `_default_status`）——上下界都有限，并且相等。

## 4. 常见错误

- `if score = 90:` 少了一个等号：语法错误。
- 忘了冒号或者缩进不齐：`SyntaxError` / `IndentationError`。
- 顺序写反：先判断 `score >= 60` 的话，95 分也会得到“及格”。

## 5. 动手

打开 [`exercises/a03_decisions.py`](../exercises/a03_decisions.py)，运行 `python3 python/tutorial/run.py A03`。

## 6. 想一想

`0.1 + 0.2 == 0.3` 是 `True` 还是 `False`？

<details><summary>答案</summary>

是 `False`！计算机里的小数有微小误差，`0.1 + 0.2` 实际上是 `0.30000000000000004`。所以比较小数不能用 `==`，
要看两者是否“足够接近”。求解器里到处都是这种判断，第 2 课会专门讲。

</details>

[← 变量和计算](a2-variables.md) · [目录](../README.md) · 下一课：[重复做事 →](a4-loops.md)
