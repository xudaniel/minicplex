# 第 1 课：第一个模型

> **这一课学：** 模块和 `import`；运行一个 Python 程序的几种方式；用 minicplex 建模的四个步骤
> **用到的代码：** [`examples/basics_01_one_variable.py`](../../examples/basics_01_one_variable.py)、[`minicplex/__init__.py`](../../minicplex/__init__.py)
> **练习：** `python3 python/tutorial/run.py 01`
> **在线做：** [打开网页版，不用安装](https://xudaniel.github.io/minicplex/python/#l01)

[← 入门 A8](a8-project.md) · [目录](../README.md) · 下一课：[数字和小数误差 →](02-numbers.md)

## 1. 先跑起来

```bash
python3 python/examples/basics_01_one_variable.py
```

```text
状态：Optimal
最多买 5 个苹果
```

再加上 `--trace`，看求解器一步步怎么算的：

```bash
python3 python/examples/basics_01_one_variable.py --trace
```

## 2. 四个步骤

打开 [`basics_01_one_variable.py`](../../examples/basics_01_one_variable.py)，去掉注释后只有这些：

```python
from minicplex import *

m = Model()                                               # 1. 空模型
apples = m.add_var(0, INF, VarType.CONTINUOUS, "apples")  # 2. 变量：0 ≤ apples < ∞
m.add_constr(2 * apples <= 10, "money")                   # 3. 限制：2 × apples ≤ 10
m.set_objective(apples, ObjSense.MAXIMIZE)                # 4. 目标：apples 越大越好
r = solve(m)
print(r.status, r.value(apples))                          # Optimal 5.0
```

任何优化题都是这四步：**变量**（要决定什么）、**限制**（不能违反什么）、**目标**（什么最好），然后求解。

`2 * apples <= 10` 看起来像数学式子，但 `apples` 是一个变量对象，这一行并不是在比大小，而是**造出一条约束**。
Python 允许一个类自己定义 `*`、`<=` 是什么意思（第 5 课会自己写一个）。

## 3. 模块和 import

一个 `.py` 文件就是一个**模块**；一个装着 `__init__.py` 的文件夹是一个**包**。minicplex 就是一个包：

```text
python/minicplex/
├── __init__.py      ← import minicplex 时运行它，决定对外提供哪些名字
├── model.py         ← Model、Var、LinExpr……
├── lp_engine.py     ← 单纯形法
├── solver.py        ← 分支定界、solve()
└── ...
```

三种 import 写法：

```python
import minicplex                     # 用的时候写 minicplex.Model()
from minicplex import Model, solve   # 直接写 Model()、solve()      ← 推荐：用到什么写什么
from minicplex import *              # 全部名字都拿进来             ← 例子里为了简短，正式代码少用
```

`from minicplex import *` 拿进来哪些名字，由 [`__init__.py`](../../minicplex/__init__.py) 里的 `__all__` 列表决定。

## 4. 运行的几种方式

```bash
python3 python/examples/easy1_bakery.py         # 运行一个文件
cd python && python3 -m minicplex ../examples/bakery.lp   # -m：把一个包当程序运行（执行它的 __main__.py）
pip install -e python                           # 安装后在任何目录都能 import minicplex
```

`python3 -m minicplex` 就是 minicplex 的命令行求解器：除了第一行的版本说明和用时，输出和 C++ 版的 `./build/minicplex` 一字不差。

> 练习文件第一行 `from check import ...` 会顺便把仓库里的 `python/` 目录加进搜索路径，所以不安装也能 `import minicplex`。

## 5. 常见错误

- `ModuleNotFoundError: No module named 'minicplex'`：在错误的目录运行，或者没装。用 `run.py` 运行练习就不会有这个问题。
- 文件起名叫 `minicplex.py` 或 `random.py`：会挡住真正的模块，import 到你自己的文件。

## 6. 动手

打开 [`exercises/l01_first_model.py`](../exercises/l01_first_model.py)：冰淇淋 3 元一个，你有 25 元，最多买几个（只能买整个）？
照着上面四步建模型，运行 `python3 python/tutorial/run.py 01`。

## 7. 想一想

把变量类型从 `VarType.INTEGER` 改成 `VarType.CONTINUOUS`，答案会变成多少？

<details><summary>答案</summary>

`8.333…`（25 ÷ 3）。允许买“三分之一个”冰淇淋时，钱可以花光。只能买整个时答案是 8。
整数要求让问题难了很多：求解器要先解“允许小数”的版本，再用分支定界一点点逼出整数解。

</details>

[← 入门 A8](a8-project.md) · [目录](../README.md) · 下一课：[数字和小数误差 →](02-numbers.md)
