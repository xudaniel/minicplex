# 第 15 课：装饰器

> **这一课学：** 函数也是对象；装饰器 = 接收函数、返回函数的函数；`@` 语法；`functools.wraps`；带参数的装饰器；`functools.lru_cache`
> **用到的代码：** [`model.py`](../../minicplex/model.py) 的 `@property`、`@staticmethod`、[`solver.py`](../../minicplex/solver.py) 的 `@dataclass`
> **练习：** `python3 python/tutorial/run.py 15`
> **在线做：** [打开网页版，不用安装](https://xudaniel.github.io/minicplex/python/#l15)

[← 函数进阶](14-functions.md) · [目录](../README.md) · 下一课：[生成器和迭代器 →](16-generators.md)

## 1. 你已经用过很多装饰器了

```python
@property
def num_vars(self): ...           # model.py

@staticmethod
def of(v, coef=1.0): ...          # model.py

@dataclass
class Params: ...                 # solver.py
```

`@` 开头的这一行就是**装饰器**。它其实只是一个简写：

```python
@property
def num_vars(self): ...
# 完全等于
def num_vars(self): ...
num_vars = property(num_vars)
```

也就是：定义完函数后，把它交给 `property`，再用返回的东西替换掉原来的名字。`property`、`staticmethod`、`dataclass` 都只是普通的函数（或类），
接收一个函数（或类），返回一个“加了功能”的新版本。

## 2. 自己写一个

函数在 Python 里是普通的对象，可以当参数传、当返回值返回（第 14 课的闭包）。所以：

```python
import functools

def count_calls(func):
    @functools.wraps(func)          # 让 wrapper 看起来像原来的函数（名字、说明）
    def wrapper(*args, **kwargs):   # 不管原函数要什么参数，原样接住
        wrapper.calls += 1
        return func(*args, **kwargs)   # 原样转交
    wrapper.calls = 0
    return wrapper

@count_calls
def greet(name):
    return f"你好，{name}"
```

`*args, **kwargs` 让同一个装饰器能套在任何函数上。不写 `functools.wraps` 的话，`greet.__name__` 会变成 `"wrapper"`，出错信息和文档都会对不上。

## 3. 带参数的装饰器

`@retry(3)` 多了一层：`retry(3)` 先被调用，**返回一个装饰器**，再用它去装饰函数。所以是三层函数：

```python
def retry(times):              # 第 1 层：接收参数
    def deco(func):            # 第 2 层：接收函数
        def wrapper(*args, **kwargs):   # 第 3 层：真正被调用的
            ...
        return wrapper
    return deco
```

## 4. 最有用的一个：lru_cache

递归的斐波那契 `fib(n) = fib(n-1) + fib(n-2)` 会把同一个值算很多很多遍：`fib(25)` 要执行函数体 24 万次。
加一行 `@functools.lru_cache(maxsize=None)`，每个 `n` 只算一次，只要 26 次。

这叫**记忆化**（memoization）。动态规划、搜索里到处在用：分支定界的伪成本（[`solver.py`](../../minicplex/solver.py) 的 `_PseudoCosts`）
其实也是一种“记住算过的结果”：每个变量往上、往下分支让目标变差了多少，算过一次就记下来，下次直接估计，不用再做昂贵的强分支。

## 5. 什么时候该用装饰器

当一件事要**加在很多函数外面**、又和函数本身的逻辑无关时：计时、计数、缓存、重试、权限检查、日志。
写成装饰器，每个函数只要加一行，而不是把同样的代码复制到处都是。反过来，只用一次的逻辑直接写在函数里就好，别为了用而用。

## 6. 动手

打开 [`exercises/l15_decorators.py`](../exercises/l15_decorators.py)：写 `count_calls`、带参数的 `retry`、自己的 `memoize`，再和 `lru_cache` 比一比。运行 `python3 python/tutorial/run.py 15`。

## 7. 想一想

`memoize` 用 `args` 元组当字典的键。如果函数的参数里有列表，会怎样？

<details><summary>答案</summary>

报 `TypeError: unhashable type: 'list'`：列表可以改，不能当字典的键（第 7 课）。`lru_cache` 也一样。
所以要缓存的函数，参数最好是数字、字符串、元组这类不可变的东西。

</details>

[← 函数进阶](14-functions.md) · [目录](../README.md) · 下一课：[生成器和迭代器 →](16-generators.md)
