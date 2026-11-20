# 第 11 课：测试——随机对拍

> **这一课学：** `unittest`；`random.Random(seed)` 可复现的随机数；暴力枚举作为“标准答案”；对拍；`itertools.product`；`math.isclose`
> **用到的代码：** [`tests/test_solver.py`](../../tests/test_solver.py)、[`tools/compare_java_cpp.py`](../../../tools/compare_java_cpp.py)
> **练习：** `python3 python/tutorial/run.py 11`
> **在线做：** [打开网页版，不用安装](https://xudaniel.github.io/minicplex/python/#l11)

[← 字符串和文本处理](10-text.md) · [目录](../README.md) · 下一课：[综合项目：选课助手 →](12-project.md)

## 1. 怎么相信一个求解器？

手算几道题对一下答案？太少了。minicplex 的做法是**对拍**：随机出几百道小题，每道题再用一个笨但绝对可靠的方法（暴力枚举）算一遍，两边必须一样。

```python
def test_random_ips(self, instances=500):
    rng = random.Random(12345)
    for t in range(instances):
        ...                               # 随机造一道题
        best = math.nan                   # 暴力枚举
        for pt in itertools.product(*(range(int(v.lb), U + 1) for v in M.vars)):
            ...
        for P in (Params(...), Params(...), Params(...)):   # 三套参数都要对
            r = solve(M, P)
            ...
```

暴力枚举只能解很小的题（3、4 个变量），但小题已经能覆盖绝大多数代码路径：不可行、无界、要分支、要割平面……
这些测试在 [`tests/test_solver.py`](../../tests/test_solver.py) 里，运行：

```bash
python3 -m unittest discover -s python/tests -v
```

## 2. 随机，但要能复现

```python
rng = random.Random(12345)   # 自己的随机数生成器，固定种子
rng.randint(-5, 5)           # 每次运行都得到同一串“随机”数
```

测试失败时，必须能把那道题原样再造出来，否则没法调试。所以**永远给随机数一个种子**，而且用自己的 `random.Random` 对象，
不要用全局的 `random.randint`（别的代码也在用它，序列会被打乱）。

## 3. unittest 的样子

```python
import unittest

class KnownAnswers(unittest.TestCase):
    def test_classic_lp(self):
        ...
        r = solve(m)
        self.assertEqual(r.status, Status.OPTIMAL)
        self.assertTrue(near(r.objective, 36))

if __name__ == "__main__":
    unittest.main()
```

类继承 `unittest.TestCase`，每个 `test_` 开头的方法是一个测试。`assertEqual`、`assertTrue`、`assertRaises` 失败时会打印出期望值和实际值。
它是标准库的一部分，不用装任何东西。（很多项目用第三方的 `pytest`，写法更短，思路一样。）

## 4. 更大的对拍：三个版本互相对

小题用暴力枚举，大题怎么办？minicplex 有 C++、Java、Python 三个版本，它们是逐行移植的，在同一道题上应当走**完全相同**的路：
同样多的分支节点、同样多的单纯形迭代。CI 每次提交都用一个新的随机种子生成 300 道题，三个版本各解一遍，再用
[`compare_java_cpp.py`](../../../tools/compare_java_cpp.py) 比较：

```bash
./build/minicplex_bench fuzz --quiet --csv cpp.csv
(cd python && python3 -m minicplex.bench ../fuzz --quiet --csv ../py.csv)
python3 tools/compare_java_cpp.py cpp.csv py.csv --strict --label Python
# 300 个模型：状态+目标值一致 300/300，节点数+迭代次数一致 300/300
```

任何一处算法细节不同（排序不稳定、四舍五入规则不同、`-0.0`……），节点数就会对不上，CI 立刻变红。
前面几课讲的那些“较真”的地方，都是被这个测试逼出来的。

## 5. 动手

打开 [`exercises/l11_testing.py`](../exercises/l11_testing.py)：写一个按种子造题的函数、一个暴力求解器，再让 100 道随机题和 minicplex 对拍。运行 `python3 python/tutorial/run.py 11`。

## 6. 想一想

如果暴力枚举本身写错了怎么办？

<details><summary>答案</summary>

两边会对不上，测试失败，你去查，发现是暴力法错了——这也是好事。对拍不要求任何一边“一定对”，只要求两个**独立**写出来的方法不会恰好错成一样。
所以暴力法要写得越简单越好，简单到一眼能看出对错。练习里还专门用一道一眼就知道答案的题（最大化 x，x ≤ 4）检查了暴力法本身。

</details>

[← 字符串和文本处理](10-text.md) · [目录](../README.md) · 下一课：[综合项目：选课助手 →](12-project.md)
