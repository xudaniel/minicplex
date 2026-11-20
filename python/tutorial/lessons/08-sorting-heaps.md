# 第 8 课：排序、lambda 和堆

> **这一课学：** `sorted` 和 `key=`；`lambda`；元组的比较规则；稳定排序；`heapq`（优先队列）
> **用到的代码：** [`solver.py`](../../minicplex/solver.py) 的节点队列 `push` 和强分支候选的排序、[`lp_engine.py`](../../minicplex/lp_engine.py) 的割平面排序
> **练习：** `python3 python/tutorial/run.py 08`
> **在线做：** [打开网页版，不用安装](https://xudaniel.github.io/minicplex/python/#l08)

[← 字典和集合](07-dicts-sets.md) · [目录](../README.md) · 下一课：[异常 →](09-exceptions.md)

## 1. key= 和 lambda

```python
sorted([3, -5, 2], key=abs)                         # [2, 3, -5]：按绝对值排
sorted(students, key=lambda s: s[1])                # 按分数从低到高
sorted(students, key=lambda s: (-s[1], s[0]))       # 分数从高到低，同分按名字
```

`lambda s: s[1]` 是一个没名字的小函数，等于 `def f(s): return s[1]`。只用一次的简单函数用 lambda 写最方便。

**元组按顺序比较**：先比第一项，一样再比第二项……所以“多级排序”只要返回一个元组。想倒序的那一项取负号。

## 2. 稳定排序

Python 的排序是**稳定**的：key 一样的元素，排序后保持原来的先后顺序。求解器依赖这一点（[`lp_engine.py`](../../minicplex/lp_engine.py) 的割平面）：

```python
cands.sort(key=lambda cd: -cd[2])  # 稳定排序：效力相同的保持原来的顺序
```

两个割平面效力一样时，谁排前面决定了加哪一个，进而改变后面整个搜索。移植 Java 版时就踩过这个坑：员工排班例子里有两个效力完全相同的割平面，
C++ 的 `std::sort`（**不**稳定）和 Java 的稳定排序挑了不同的那个，最优值一样，节点数却一个 8 一个 11；换一个 C++ 标准库也可能变。
现在三个版本统一用稳定排序，每一步才都相同。（详见主 README 的[怎么保证两个版本一样](../../../README.md#怎么保证两个版本一样)。）

## 3. 堆：总是先拿出最好的

分支定界有一大堆待处理的节点，每次要取出“界最小”的那个。每次都排序太慢，minicplex 用**堆**（[`solver.py`](../../minicplex/solver.py)）：

```python
def push(self, node):
    # 和 Java 版的比较器一致：界小的先出；界相同时深的先出；再相同时新的先出
    heapq.heappush(self.open, (node.bound, jmath.neg_zero_first(node.bound), -node.depth, -node.seq, node))

self.cur = heapq.heappop(self.open)[-1]    # 取出最小的，拿元组最后一项（节点本身）
self.open[0][0]                           # 不取出，只看最小的那个的界
```

- `heapq` 把一个普通列表维护成“最小的永远在 `[0]`”，放进、取出都只要 O(log n) 步。
- 存进去的是**元组**，比较规则就是第 1 节的元组规则。深度、序号取负号，就变成“越大越先出”。
- 为什么要 `-node.seq`（序号）？如果前几项都一样，Python 会去比较最后的 `node` 对象，而节点没定义 `<`，会报 `TypeError`。序号各不相同，保证比较在这之前就分出了胜负，而且顺序完全确定。
- `neg_zero_first` 是为了和 Java 的 `Double.compare` 一样把 `-0.0` 排在 `0.0` 前面——又是第 2 课的那个负零。

## 4. 常见错误

- `list.sort()` 原地排序、返回 `None`：`x = a.sort()` 得到的是 `None`。要新列表用 `sorted(a)`。
- 堆里放了不能比较的对象，而且没加序号兜底。
- 以为 `heapq` 是“最大堆”：它永远弹出最小的。要最大的就取负号。

## 5. 动手

打开 [`exercises/l08_sorting_heaps.py`](../exercises/l08_sorting_heaps.py)：写节点的排序键、用堆弹出、成绩排名、出现最多的词。运行 `python3 python/tutorial/run.py 08`。

## 6. 想一想

为什么分支定界里“界一样时深的先出”？

<details><summary>答案</summary>

越深的节点，固定了越多的整数变量，离一个完整的整数解越近。尽早找到一个整数解（哪怕不是最好的），就能用它的目标值把很多节点直接剪掉。
这叫“深度优先找解、最优优先证明”，几乎所有 MIP 求解器都是这个思路。

</details>

[← 字典和集合](07-dicts-sets.md) · [目录](../README.md) · 下一课：[异常 →](09-exceptions.md)
