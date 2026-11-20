# 入门 A5：自己写函数

> **这一课学：** `def`；参数和返回值；默认参数；按名字传参；文档字符串
> **大约：** 20 分钟 · **练习：** `python3 python/tutorial/run.py A05`

[← 重复做事](a4-loops.md) · [目录](../README.md) · 下一课：[列表 →](a6-lists.md)

## 1. 函数：给一段代码起名字

```python
def c_to_f(c):
    """摄氏度换算成华氏度。"""      # ← 文档字符串：说明这个函数做什么
    return c * 9 / 5 + 32

print(c_to_f(37))    # 98.6
```

- `c` 是**参数**：调用时传进来的值。
- `return` 把结果交回给调用的人，函数到这里就结束了。
- 没写 `return` 的函数会返回 `None`（“什么都没有”）。

写成函数的好处：起了名字，读的人一看就懂；写一次，到处用；出错了只需要改一个地方。

## 2. 默认参数

```python
def discount(price, percent=10):
    return price * (100 - percent) / 100

discount(200)              # 180.0   ← percent 没写，用默认值 10
discount(200, 25)          # 150.0
discount(80, percent=50)   # 40.0    ← 按名字传，一看就知道 50 是什么
```

> **minicplex 里的例子：** 建变量的函数就是这样设计的（[`model.py`](../../minicplex/model.py)）：
>
> ```python
> def add_var(self, lb=0.0, ub=INF, type=VarType.CONTINUOUS, name=""):
> ```
>
> 所以 `m.add_var()` 就是一个 `[0, +∞)` 的连续变量，`m.add_var(name="y")` 只改名字，其它用默认值。
> Java 没有默认参数，同样的功能要写 4 个“重载”方法；对比一下 [Java 版](../../../java/src/main/java/minicplex/Model.java) 就能体会。

## 3. 常见错误

- 用了 `print` 代替 `return`：屏幕上看到了结果，但调用的人拿不到。
- 默认参数用了列表 `def f(items=[])`：所有调用共用同一个列表（第 6 课会讲这个坑）。
- 参数顺序搞反：`clamp(x, lo, hi)` 写成 `clamp(lo, hi, x)`。按名字传参能避免。

## 4. 动手

打开 [`exercises/a05_functions.py`](../exercises/a05_functions.py)，运行 `python3 python/tutorial/run.py A05`。

## 5. 想一想

`clamp(x, lo, hi)` 能不能只用一行写完？

<details><summary>答案</summary>

可以：`return max(lo, min(x, hi))`。先和 `hi` 比取小的（不超过上限），再和 `lo` 比取大的（不低于下限）。

</details>

[← 重复做事](a4-loops.md) · [目录](../README.md) · 下一课：[列表 →](a6-lists.md)
