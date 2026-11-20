# 第 4 课：类和对象

> **这一课学：** `class`、`__init__`、`self`；属性和方法；默认参数代替“重载”；`@property`；`__repr__`；`__slots__`
> **用到的代码：** [`model.py`](../../minicplex/model.py) 的 `VarInfo`、`Model.add_var`、`Model.num_vars`
> **练习：** `python3 python/tutorial/run.py 04`
> **在线做：** [打开网页版，不用安装](https://xudaniel.github.io/minicplex/python/#l04)

[← 列表和推导式](03-lists.md) · [目录](../README.md) · 下一课：[运算符重载和不可变对象 →](05-operators.md)

## 1. 类：把数据和操作放在一起

一个变量有名字、上下界、类型。minicplex 用一个类把它们装在一起（[`model.py`](../../minicplex/model.py)）：

```python
class VarInfo:
    """变量的名字、上下界和类型。"""
    __slots__ = ("name", "lb", "ub", "type")

    def __init__(self, name, lb, ub, type):
        self.name = name
        self.lb = lb
        self.ub = ub
        self.type = type

    def copy(self):
        return VarInfo(self.name, self.lb, self.ub, self.type)
```

- `class VarInfo:` 定义一种新类型；`VarInfo("x", 0, 10, VarType.INTEGER)` 造出一个**对象**。
- `__init__` 在造对象时自动运行，负责把属性存好。
- `self` 是“这个对象自己”。每个方法的第一个参数都是它，调用时不用写：`v.copy()`。
- `__slots__`（可选）事先声明只有这几个属性：省内存，而且写错属性名（`v.nmae = ...`）会直接报错。

## 2. 方法：对象能做的事

```python
class Model:
    def add_var(self, lb=0.0, ub=INF, type=VarType.CONTINUOUS, name=""):
        lb, ub = float(lb), float(ub)
        if type == VarType.BINARY:
            lb = max(lb, 0.0)
            ub = min(ub, 1.0)
        if not name:
            name = f"x{len(self.vars) + 1}"
        if name in self._index:
            raise ValueError(f"duplicate variable name: {name}")
        self._index[name] = len(self.vars)
        self.vars.append(VarInfo(name, lb, ub, type))
        return Var(len(self.vars) - 1)
```

方法既读又改对象的状态（`self.vars`），再把一个小小的 `Var` 把手交回去。
`_index` 前面的下划线是约定：“这是内部用的，外面别碰”。Python 不强制，但大家都遵守。

## 3. @property：像属性一样用的方法

```python
@property
def num_vars(self):
    return len(self.vars)

m.num_vars      # 不加括号
```

值是算出来的，但用起来像普通属性。好处是：以后改了内部存法，外面的代码一行都不用改。

## 4. __repr__：打印时长什么样

```python
>>> VarInfo("x", 0.0, 10.0, VarType.INTEGER)
VarInfo('x', 0, 10, INTEGER)
```

没写 `__repr__` 时只会看到 `<minicplex.model.VarInfo object at 0x7f…>`，调试时毫无用处。
`__repr__` 的习惯是：长得像“能造出这个对象的代码”。

## 5. 每个对象有自己的一份数据

```python
a, b = Product("苹果", 2.5, 5), Product("梨", 3, 5)
a.sell(1)
a.stock, b.stock     # (4, 5)
```

`self.stock` 存在各自的对象里，互不影响。但如果在类里（不在 `__init__` 里）写 `stock = []`，那就是所有对象共用的“类属性”了，第 6 课还会遇到这个坑。

## 6. 动手

打开 [`exercises/l04_classes.py`](../exercises/l04_classes.py)，写一个商品类 `Product`：库存默认 0、库存总价值、卖货、`in_stock` 属性、`__repr__`。运行 `python3 python/tutorial/run.py 04`。

## 7. 想一想

`m.add_var(0, 1, VarType.BINARY)` 和 `m.add_var(type=VarType.BINARY, ub=1)` 有区别吗？

<details><summary>答案</summary>

没区别。按位置传参要记住顺序，按名字传参可以任意顺序，也更好读。参数多、而且大多有默认值时，按名字传是好习惯。
`Params(relax_integrality=True, cut_rounds=0)` 就是这样用的（第 6 课）。

</details>

[← 列表和推导式](03-lists.md) · [目录](../README.md) · 下一课：[运算符重载和不可变对象 →](05-operators.md)
