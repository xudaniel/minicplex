# 第 5 课：运算符重载和不可变对象

> **这一课学：** `__add__`、`__radd__`、`__mul__`、`__le__` 等“魔法方法”；`NotImplemented`；为什么 `sum()` 需要 `__radd__`；不可变对象；复制
> **用到的代码：** [`model.py`](../../minicplex/model.py) 的 `LinExpr` 和 `Var`
> **练习：** `python3 python/tutorial/run.py 05`

[← 类和对象](04-classes.md) · [目录](../README.md) · 下一课：[dataclass 和 enum →](06-dataclass-enum.md)

## 1. 2 * x + 3 * y <= 12 是怎么变成约束的？

Python 看到 `a + b`，其实是调用 `a.__add__(b)`；看到 `a <= b`，调用 `a.__le__(b)`。只要类里定义了这些方法，
自己的对象就能用运算符。`LinExpr`（线性表达式）就是这么做的（[`model.py`](../../minicplex/model.py)）：

```python
class LinExpr:
    def __add__(self, o):
        if isinstance(o, Var):
            return self.plus_var(o, 1.0)
        if isinstance(o, LinExpr):
            return self.plus_expr(o)
        if _is_num(o):
            return self.plus_const(float(o))
        return NotImplemented          # 不认识的类型：交给 Python 处理

    def __le__(self, o):
        return Constraint.make(self, Sense.LE, LinExpr.wrap(o))
```

`2 * x + 3 * y <= 12` 一步步是：`x.__rmul__(2)` → 表达式 `2x`；`2x.__add__(3y)` → `2x + 3y`；`.__le__(12)` → 一条约束。

## 2. 左边是数字怎么办？__radd__

`2 * x` 先试 `int.__mul__(2, x)`：整数不认识 `Var`，返回 `NotImplemented`。Python 于是**反过来**试 `x.__rmul__(2)`。
r 开头的方法就是“我在运算符右边时”的版本。

`sum([x, y, x])` 也需要它：`sum` 从 `0` 开始加，第一步是 `0 + x`，只能靠 `x.__radd__(0)`。

```python
def __radd__(self, o):
    if _is_num(o):          # 让 sum([...]) 能用：0 + e
        return self.plus_const(float(o))
    return NotImplemented
```

**`NotImplemented` 不是 `NotImplementedError`。** 前者是一个特殊的值，意思是“这个组合我不管，问问对方”；两边都不管时，Python 才报 `TypeError`。
后者是一个异常（练习里的 TODO 用的就是它）。

## 3. 不可变：每次运算都返回新对象

```python
def plus_const(self, c):
    e = self.copy()         # 先复制
    e.constant += c         # 只改副本
    return e                # 原来的 self 一点没动
```

如果 `+` 直接改自己，会出这种事：

```python
cost = 5 * cake
with_bread = cost + 4 * bread    # 想要一个新表达式
m.set_objective(cost)            # 本来想要 5 cake，结果 cost 已经被改成 5 cake + 4 bread 了
```

不可变对象可以放心地传来传去、在好几个地方共用，不用担心被谁偷偷改掉。Python 的 `str`、`tuple`、`int` 都是不可变的。

注意 `copy()` 里复制的是字典：`e.terms = dict(self.terms)`。如果写成 `e.terms = self.terms`，两个表达式就共用一个字典了（又是别名）。

## 4. == 返回约束，不返回 True / False

`x == 3` 在 minicplex 里是一条等式约束。代价是：`Var` 不能再用普通的 `==` 判断“是不是同一个变量”。
minicplex 的折中办法是：两边都是变量时，这条约束在 `if` 里会当成“编号是否相同”（`Constraint.__bool__`），
所以 `x in [x, y]`、`{x: 1}[x]` 照样能用；其它情况下把约束当 True/False 用会直接报错，免得写出 `if 2 * x <= 3:` 这种看起来对、其实没意义的代码。

## 5. 常见错误

- 只写了 `__add__` 没写 `__radd__`：`x + 1` 能用，`1 + x` 和 `sum(...)` 报 `TypeError`。
- 不认识的类型 `raise TypeError` 而不是 `return NotImplemented`：断了 Python 去问对方的机会。
- 在运算符方法里修改 `self`。

## 6. 动手

打开 [`exercises/l05_operators.py`](../exercises/l05_operators.py)，写一个迷你表达式类 `Expr`：`+`、`*`、`sum()`，而且不可变。运行 `python3 python/tutorial/run.py 05`。

## 7. 想一想

`x += 1` 会调用哪个方法？`Expr` 没写 `__iadd__`，它还能用吗？

<details><summary>答案</summary>

Python 先找 `__iadd__`（原地加）；找不到就退回 `x = x + 1`，也就是 `__add__`，再把新对象赋给 `x`。所以能用，而且原来的对象没被改，这正是不可变对象想要的。
列表就不一样：`list.__iadd__` 是原地修改，`a += [1]` 会影响所有指向这个列表的名字。

</details>

[← 类和对象](04-classes.md) · [目录](../README.md) · 下一课：[dataclass 和 enum →](06-dataclass-enum.md)
