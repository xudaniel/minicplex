# 第 7 课：字典和集合

> **这一课学：** `dict` 的增删查；`in`、`get`；字典的顺序；按键排序；`set` 去重、交集；`Counter` 和 `defaultdict`
> **用到的代码：** [`model.py`](../../minicplex/model.py) 的 `Model._index` 和 `_merge`、`Constraint.make`
> **练习：** `python3 python/tutorial/run.py 07`
> **在线做：** [打开网页版，不用安装](https://xudaniel.github.io/minicplex/python/#l07)

[← dataclass 和 enum](06-dataclass-enum.md) · [目录](../README.md) · 下一课：[排序、lambda 和堆 →](08-sorting-heaps.md)

## 1. 名字 → 编号：字典

读 LP 文件时，每遇到一个变量名，都要知道它是第几个变量。在列表里一个个找太慢，minicplex 用一个字典（[`model.py`](../../minicplex/model.py)）：

```python
self._index = {}                       # {变量名: 编号}

def find_var(self, name):
    return self._index.get(name, -1)   # 找不到就返回 -1，不报错
```

```python
d = {"x": 0, "y": 1}
d["z"] = 2          # 加一项
d["x"]              # 0
d["w"]              # ✗ KeyError
d.get("w", -1)      # -1
"x" in d            # True   ← 查“有没有键”，非常快（不管字典多大）
del d["y"]
for k, v in d.items(): ...
```

## 2. 合并同类项

`2x + 3y - 2x` 里 `x` 出现了两次。表达式用 `{变量编号: 系数}` 存，同一个键的系数要加起来：

```python
def _merge(terms, k, v):
    """Java 的 terms.merge(k, v, Double::sum)：已有就相加，没有就直接放进去。"""
    terms[k] = terms[k] + v if k in terms else v
```

为什么不写成更短的 `terms.get(k, 0.0) + v`？因为 `0.0 + (-0.0)` 是 `+0.0`，会丢掉负零的符号（第 2 课）。
为了和 C++、Java 版一模一样，连这都要照顾到。练习里不用这么较真，`get` 就行。

加完是 0 的项要去掉，造约束时就是这么做的：

```python
for k in sorted(d.terms):
    if d.terms[k] != 0.0:
        c.coefs[k] = d.terms[k]
```

## 3. 字典的顺序

从 Python 3.7 起，字典保证按**插入顺序**遍历。但 minicplex 需要的是“按变量编号从小到大”——
因为小数加法的结果和顺序有关（`(a + b) + c` 不一定等于 `a + (b + c)`），三个版本必须按同样的顺序加。
所以凡是要累加的地方，都先 `sorted(terms)`，或者在放进去的时候就排好序：`dict(sorted(d.items()))`。

## 4. 集合：只关心“有没有”

```python
seen = set()
seen.add("x")
"x" in seen               # True，和字典一样快
{1, 2, 5} & {2, 3, 5}     # {2, 5}  交集
{1, 2} | {2, 3}           # {1, 2, 3}  并集
{1, 2, 3} - {2}           # {1, 3}  差集
set(["b", "a", "b"])      # {'a', 'b'}  去重（但顺序没了）
```

## 5. 两个好用的工具

```python
from collections import Counter, defaultdict
Counter("the cat and the dog".split()).most_common(1)   # [('the', 2)]
groups = defaultdict(list)       # 拿不存在的键时自动建一个空列表
groups["Mon"].append("Python")
```

## 6. 动手

打开 [`exercises/l07_dicts_sets.py`](../exercises/l07_dicts_sets.py)：建名字索引（重复时报错）、合并同类项、保序去重、求交集。运行 `python3 python/tutorial/run.py 07`。

## 7. 想一想

能不能用一个列表 `[x, y]` 当字典的键？元组 `(x, y)` 呢？

<details><summary>答案</summary>

列表不行（`TypeError: unhashable type: 'list'`），元组可以。字典要根据键算一个“哈希值”来快速查找，键在存进去以后不能变，
所以只有不可变的东西（数字、字符串、元组、frozen dataclass）才能当键。第 6 课的 `Point` 加了 `frozen=True`，就是为了能放进集合。

</details>

[← dataclass 和 enum](06-dataclass-enum.md) · [目录](../README.md) · 下一课：[排序、lambda 和堆 →](08-sorting-heaps.md)
