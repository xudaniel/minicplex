# minicplex · Python 版

纯 Python、零依赖的 minicplex：单纯形法、分支定界、Gomory 割、预处理，逐行移植自 C++ 版。
在同一道题上，三个版本（C++ / Java / Python）走**完全相同**的计算路径：同样的节点数、同样的单纯形迭代次数、逐字相同的输出。

A pure-Python, zero-dependency port of minicplex (simplex, branch and bound, Gomory cuts, presolve). It is a line-by-line port
of the C++ solver and follows the exact same search path: same node count, same simplex iterations, byte-identical output.

```python
from minicplex import Model, VarType, ObjSense, INF, solve

m = Model()
cake = m.add_var(0, INF, VarType.INTEGER, "cake")
bread = m.add_var(0, INF, VarType.INTEGER, "bread")
m.add_constr(6 * cake + 4 * bread <= 24, "flour")
m.add_constr(1 * cake + 2 * bread <= 6, "labor")
m.set_objective(5 * cake + 4 * bread, ObjSense.MAXIMIZE)

r = solve(m)
print(r.status, r.objective, r.value(cake), r.value(bread))   # Optimal 20.0 4.0 0.0
```

## 运行 / Run

```bash
python3 python/examples/easy1_bakery.py                 # 15 个例子，和 C++ 版一一对应
cd python && python3 -m minicplex ../examples/bakery.lp # 命令行求解器（选项和 C++ 版相同，加 --trace 看每一步）
python3 -m unittest discover -s python/tests -v         # 测试（只用标准库）
pip install ./python                                    # 可选：安装后任何地方都能 import minicplex
```

需要 Python 3.9+。Requires Python 3.9+.

## 用它学 Python / Learn Python with it

[`tutorial/`](tutorial/README.md)：20 节中文 Python 课（8 节零基础 + 12 节读真实代码），每节一道自动判分的练习。

## 目录 / Layout

| 文件 | 内容 |
|---|---|
| [`minicplex/model.py`](minicplex/model.py) | `Model`、`Var`、`LinExpr`（运算符重载）、`Constraint`、LP 文件输出 |
| [`minicplex/lp_reader.py`](minicplex/lp_reader.py) | CPLEX LP 格式读取 |
| [`minicplex/presolve.py`](minicplex/presolve.py) | 界传播、系数收紧 |
| [`minicplex/lp_engine.py`](minicplex/lp_engine.py) | 有界变量单纯形法（原始 + 对偶）、Gomory 割 |
| [`minicplex/solver.py`](minicplex/solver.py) | 分支定界、`solve()`、`Params`、`Result` |
| [`minicplex/jmath.py`](minicplex/jmath.py) | 和 C++ / Java 逐位一致的取整函数 |
| [`minicplex/__main__.py`](minicplex/__main__.py)、[`bench.py`](minicplex/bench.py) | 命令行求解器、批量求解（CSV 和 C++ 版同格式） |
| [`examples/`](examples/) | 15 个例子 |
| [`tests/`](tests/test_solver.py) | 20 个测试：已知答案、Gomory 割有效性、影子价格有限差分、500 道随机题和暴力枚举对拍 |
| [`tutorial/`](tutorial/README.md) | Python 课 |

速度：纯 Python 解释执行，比 C++ 版慢几十倍，教学和中小模型够用（13 个基准模型约 20 秒，C++ 版 0.4 秒）。
Speed: pure interpreted Python, a few dozen times slower than C++; fine for teaching and small models.
