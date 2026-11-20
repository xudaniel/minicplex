# 第 14 课：函数进阶——*args、**kwargs、拆包和闭包

> **这一课学：** 位置参数和关键字参数；`*args` 和 `**kwargs`；调用时用 `*` `**` 摊开；元组拆包和 `*rest`；闭包、`nonlocal`；循环里造 lambda 的坑
> **用到的代码：** [`solver.py`](../../minicplex/solver.py) 的 `Params`、[`tests/test_solver.py`](../../tests/test_solver.py) 的 `itertools.product(*...)`
> **练习：** `python3 python/tutorial/run.py 14`
> **在线做：** [打开网页版，不用安装](https://xudaniel.github.io/minicplex/python/#l14)

[← 读懂报错和调试](13-debugging.md) · [目录](../README.md) · 下一课：[装饰器 →](15-decorators.md)

## 1. 收集任意多个参数

```python
def total(*nums):          # 调用时传几个都行，nums 是一个元组
    return sum(nums)

def show(**info):          # 任意多个关键字参数，info 是一个字典
    for k, v in info.items():
        print(k, "=", v)

show(name="cake", value=3)
```

`args`、`kwargs` 只是习惯的名字，关键是前面的 `*` 和 `**`。

## 2. 调用时“摊开”

反过来，调用函数时 `*` 把一个序列摊成多个位置参数，`**` 把一个字典摊成多个关键字参数：

```python
total(*[4, 5])                       # 等于 total(4, 5)
Params(**{"trace": True})            # 等于 Params(trace=True)
```

minicplex 的测试用它枚举所有整数点：每个变量一个 `range`，有几个变量就有几个 `range`，事先不知道个数，于是

```python
itertools.product(*(range(int(v.lb), U + 1) for v in M.vars))
```

把一串 `range` 摊开交给 `product`。

## 3. 拆包

```python
lb, ub = float(lb), float(ub)              # model.py：一次给两个变量赋值
for k, a in c.coefs.items():               # 每一项是 (编号, 系数)，直接拆开
x4, x5, x6, x7 = (m.add_var() for _ in range(4))   # 测试里一次建 4 个变量
first, *rest = [1, 2, 3]                   # first = 1，rest = [2, 3]
a, b = b, a                                # 交换两个变量，不用临时变量
```

## 4. 只能按名字传的参数

`Params` 有十几个字段，没人记得住顺序，所以大家都按名字写：`Params(relax_integrality=True, cut_rounds=0)`。
想**强制**调用的人按名字传，可以在参数列表里放一个单独的 `*`：

```python
def solve_with(model, *, gap=1e-6, quiet=False):   # gap、quiet 只能写成 gap=...、quiet=...
```

## 5. 闭包：记住外面变量的函数

```python
def make_counter():
    count = 0
    def counter():
        nonlocal count      # 要修改外层的变量，得先声明
        count += 1
        return count
    return counter

c = make_counter()
c(), c(), c()               # 1, 2, 3
```

内层函数“记住”了外层的 `count`，哪怕 `make_counter` 已经返回了。每调用一次 `make_counter`，就有一个新的 `count`。
练习里的 `check.py` 到处是这种用法：`eq("…", 6, lambda: total(1, 2, 3))`，lambda 记住了要调用什么，等到判分时才真正去调用。

## 6. 循环里造函数的坑

```python
adders = [lambda x: x + k for k in range(3)]
[f(10) for f in adders]     # [12, 12, 12]   ← 不是 [10, 11, 12]！
```

闭包记住的是**变量本身**，不是当时的值。三个函数都看着同一个 `k`，调用时循环早已结束，`k` 是 2。
修法是用默认参数把当时的值“拍下来”：`lambda x, k=k: x + k`（默认参数在定义时就算好了——这次正好利用了第 13 课的那个特性）。

## 7. 动手

打开 [`exercises/l14_functions.py`](../exercises/l14_functions.py)，运行 `python3 python/tutorial/run.py 14`。

最后一题是 **🤔 先猜后跑**：先别运行，读题目里那几行代码，把你猜的结果写在 `return` 后面，再运行看看猜得对不对。猜错了也没关系，想明白为什么才是重点。

## 8. 想一想

`print(*["a", "b", "c"], sep="-")` 输出什么？

<details><summary>答案</summary>

`a-b-c`。`*` 把列表摊成三个位置参数，等于 `print("a", "b", "c", sep="-")`。`print` 本身就是用 `*args` 接收任意多个值的。

</details>

[← 读懂报错和调试](13-debugging.md) · [目录](../README.md) · 下一课：[装饰器 →](15-decorators.md)
