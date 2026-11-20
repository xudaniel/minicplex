# 第 6 课：dataclass 和 enum

> **这一课学：** `@dataclass` 自动生成 `__init__`/`__repr__`/`__eq__`；默认值；`field(default_factory=list)`；`frozen=True`；`Enum`；类型标注
> **用到的代码：** [`solver.py`](../../minicplex/solver.py) 的 `Params`、`Result`、`Status`、`Branching`
> **练习：** `python3 python/tutorial/run.py 06`

[← 运算符重载和不可变对象](05-operators.md) · [目录](../README.md) · 下一课：[字典和集合 →](07-dicts-sets.md)

## 1. dataclass：只写字段，其余自动生成

求解参数有十几个，大多数时候用默认值（[`solver.py`](../../minicplex/solver.py)）：

```python
@dataclass
class Params:
    """求解参数（默认值和 C++ 版一样）。"""
    relax_integrality: bool = False      # 只解线性松弛
    branching: Branching = Branching.PSEUDO_COST
    cut_rounds: int = 2                  # 根节点 Gomory 割的轮数（0 = 不加）
    presolve: bool = True                # 界传播 + 系数收紧
    ...
    verbose: bool = False                # 打印 CPLEX 风格的节点日志
    trace: bool = False                  # 打印每一次单纯形转轴和分支决定
```

`@dataclass` 根据这些字段自动写好 `__init__`、`__repr__` 和 `__eq__`，所以可以直接：

```python
Params(trace=True)
Params(relax_integrality=True, presolve=False, cut_rounds=0)   # basics_07_fixed_cost.py
```

冒号后面的 `bool`、`int` 是**类型标注**：Python 运行时不检查，但编辑器和 `mypy` 会用它帮你找错，读代码的人也一看就懂。

## 2. 可变默认值的坑

`Result` 里有几个列表字段：

```python
@dataclass
class Result:
    status: Status = Status.INFEASIBLE
    objective: float = math.nan
    x: List[float] = field(default_factory=list)       # ← 不能写成 x: list = []
    duals: List[float] = field(default_factory=list)
```

为什么不能写 `= []`？默认值只在定义类的时候算**一次**，所有对象会共用同一个列表——改一个，全变。
dataclass 干脆不让你这么写（会报错）。`field(default_factory=list)` 的意思是“每造一个对象，就调用一次 `list()` 新建一个”。

普通函数也有同样的坑：`def f(items=[])` 也会在多次调用之间共用那一个列表。习惯写法是 `def f(items=None)`，然后在函数里 `if items is None: items = []`。

## 3. frozen=True：造出来就不能改

```python
@dataclass(frozen=True)
class Point:
    x: float
    y: float
```

不能改的对象可以放进 `set`、当 `dict` 的键（dataclass 会顺便生成 `__hash__`），也可以放心共用（第 5 课的道理）。第 12 课的 `Course` 就是这样定义的。

## 4. Enum：一组有名字的常量

```python
class Status(Enum):
    OPTIMAL = "Optimal"
    INFEASIBLE = "Infeasible"
    UNBOUNDED = "Unbounded"
    ...
    def __str__(self):
        return self.value
```

为什么不直接用字符串 `"Optimal"`？写错一个字母 `"Optimla"` 不会报错，只会悄悄地永远不相等；写错 `Status.OPTIMLA` 立刻报 `AttributeError`。
另外，`print(r.status)` 打印 `Optimal`（靠 `__str__`），和 C++ 版输出一致；比较时用 `r.status is Status.OPTIMAL` 或 `==`。
`Status("Optimal")` 可以按值反查成员，读 CSV 时用得上。

## 5. 动手

打开 [`exercises/l06_dataclass_enum.py`](../exercises/l06_dataclass_enum.py)：一个天气 enum、一个 frozen 的点、一个购物车 dataclass。运行 `python3 python/tutorial/run.py 06`。

## 6. 想一想

`Result` 为什么没有用 `frozen=True`？

<details><summary>答案</summary>

因为求解器是一边算一边填结果的：`R.nodes += 1`、`R.status = ...`。如果想要“交出去以后就不能改”，可以在最后用 `dataclasses.replace` 生成一个 frozen 的副本，
但对这个小项目来说不值得。设计时要权衡：不可变更安全，可变更方便。

</details>

[← 运算符重载和不可变对象](05-operators.md) · [目录](../README.md) · 下一课：[字典和集合 →](07-dicts-sets.md)
