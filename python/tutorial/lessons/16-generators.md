# 第 16 课：生成器和迭代器

> **这一课学：** 可迭代对象和迭代器；`yield`；生成器表达式；惰性计算；无穷序列；`itertools`；`yield from` 和递归生成器
> **用到的代码：** [`examples/basics_08_min_max.py`](../../examples/basics_08_min_max.py) 的 `sum(... for ...)`、[`tests/test_solver.py`](../../tests/test_solver.py) 的 `itertools.product`
> **练习：** `python3 python/tutorial/run.py 16`
> **在线做：** [打开网页版，不用安装](https://xudaniel.github.io/minicplex/python/#l16)

[← 装饰器](15-decorators.md) · [目录](../README.md) · 下一课：[文件和数据 →](17-files-data.md)

## 1. for 背后发生了什么

`for x in 东西` 能用在列表、字符串、字典、文件、`range` 上。它们都是**可迭代的**：Python 先调用 `iter(东西)` 拿到一个**迭代器**，
然后不停地 `next(迭代器)` 要下一个，直到它说“没有了”（`StopIteration`）。

```python
it = iter([10, 20])
next(it)    # 10
next(it)    # 20
next(it)    # StopIteration
```

## 2. yield：最简单的造迭代器的办法

```python
def countdown(n):
    while n > 0:
        yield n        # 交出一个值，然后在这里暂停
        n -= 1

for x in countdown(3):
    print(x)           # 3 2 1
```

函数里只要出现 `yield`，调用它就不会立刻执行，而是得到一个**生成器**。每次 `next`，它从上次暂停的地方接着跑，到下一个 `yield` 再停。

## 3. 惰性：要一个算一个

```python
sum(hours[t] * give[t][p] for t in range(tasks))     # basics_08_min_max.py
```

圆括号的推导式是**生成器表达式**：不先造出一个完整的列表，`sum` 要一个它算一个。数据量大时省很多内存。

惰性还意味着可以有**无穷**的序列：

```python
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

list(itertools.islice(fibonacci(), 10))    # 只取前 10 个
```

读一个 10 GB 的文件也是一样：`for line in open(path)` 一次只读一行，而不是一次全读进内存。

## 4. itertools：现成的迭代工具

```python
itertools.product([0, 1], repeat=3)     # 所有 0/1 组合（第 3 课的暴力背包）
itertools.islice(gen, 10)               # 取前 10 个
itertools.count(1)                      # 1, 2, 3, ……
itertools.chain(a, b)                   # 先走完 a 再走 b
itertools.combinations("abcd", 2)       # 所有两两组合
```

## 5. 递归生成器和 yield from

练习里要自己写一个 `product`：`n` 个位置，每个位置取 `values` 里的值，产出所有组合。思路是递归：
第一个位置取 `v`，后面 `n - 1` 个位置的所有组合交给自己去生成。

```python
for rest in assignments(n - 1, values):
    yield (v,) + rest
```

如果只是把另一个生成器的值原样转交，可以写成 `yield from 另一个生成器`。

## 6. 一次性的

生成器走完就空了：

```python
g = (x * x for x in range(3))
list(g)     # [0, 1, 4]
list(g)     # []        ← 已经走完了
```

要用好几遍，就转成列表存起来，或者每次重新调用生成器函数。

## 7. 动手

打开 [`exercises/l16_generators.py`](../exercises/l16_generators.py)：倒计时、无穷斐波那契、分块、一行行清洗数据，最后用你自己写的 `assignments` 做暴力背包，和求解器对答案。运行 `python3 python/tutorial/run.py 16`。

## 8. 想一想

`assignments(20, [0, 1])` 一共产出多少个组合？如果写成“先把所有组合放进一个列表再返回”，会有什么问题？

<details><summary>答案</summary>

2²⁰ ≈ 100 万个。放进列表要先全部造出来，占几百 MB 内存，第一个结果也要等全部算完才拿得到；
生成器一次只存一个组合，而且一边产出一边就能用。暴力搜索、大文件处理、数据流水线，都是生成器的主场。

</details>

[← 装饰器](15-decorators.md) · [目录](../README.md) · 下一课：[文件和数据 →](17-files-data.md)
