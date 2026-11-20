# 用 minicplex 学 Python

> 一门用**真实项目**学 Python 的中文小课：先是 8 节零基础入门小课（A1～A8），再是 12 课正式课程，最后 7 课进阶（13～19）。
> 每课一个 Python 知识点，例子取自 minicplex 求解器的 Python 源代码，每课配一道能自动判分的练习。
> [English version](en/README.md)：27 课全部有英文版，网页版右上角一键切换。

大多数 Python 教程用“猫和狗”举例，学完了还是不知道真实项目里的代码长什么样。这门课反过来：
先摆出 minicplex（一个能真正解优化题的求解器：约 2,700 行纯 Python，含注释，零依赖）里的一段代码，再讲它用到的 Python 知识，
以及**为什么这样写**。学完你不仅会 Python 语法，还能读懂一个完整的项目。

> **🌐 打开网页就能学：[https://xudaniel.github.io/minicplex/python/](https://xudaniel.github.io/minicplex/python/)**
> 课文、编辑器、自动判分都在一个页面里。Python 在你的浏览器里运行，不用安装任何东西，不用注册，手机也能用；写的代码和进度自动保存在这个浏览器里。

这个 Python 版不是“简化版”：它和 C++ 版逐行对应，在同一道题上走完全相同的计算路径，CI 每次提交都在 600 多道题上核对一遍。
你读到的，就是真正在跑的代码。

## 适合谁

- **完全没写过代码？** 从入门 A1 开始。每节 10～20 分钟，只学一件事，例子都是买水果、算步数这样的日常小事。
- 学过一点编程（任何语言都行），知道变量、if、循环是什么：可以直接从第 1 课开始；
- 想知道“真实的 Python 项目”是怎么组织的：模块、类、运算符重载、dataclass、测试……
- 不需要懂优化算法，用到的地方都会用大白话解释。完全没接触过优化，可以先读主 README 的
  [用大白话讲 minicplex](../../README.md#用大白话讲-minicplex先看这里)（5 分钟）。

## 准备

**用网页版的话，什么都不用准备**，直接打开上面的链接。想在自己电脑上写（用 VS Code、PyCharm 等）也可以：练习文件和网页上的完全一样。

只需要 Python 3.9 或更新版本（`python3 --version` 查看；Windows 上可能是 `python` 或 `py`）。不用安装任何包，不用 IDE。

```bash
git clone https://github.com/xudaniel/minicplex.git && cd minicplex
python3 python/tutorial/run.py A01        # 零基础：运行入门 A1 的练习
python3 python/tutorial/run.py 01         # 学过编程：运行第 1 课的练习
```

`run.py` 本身就是 Python 写的，Windows、macOS、Linux 用法完全一样。也可以在 VS Code、PyCharm 里直接运行练习文件。

## 练习怎么做

每课的练习在 [`exercises/`](exercises/) 里，文件名是 `a01_…`、`l02_…`。
打开文件，找到 `TODO`，把 `raise NotImplementedError("TODO")` 换成你的代码（注意缩进），然后运行：

```text
$ python3 python/tutorial/run.py 02
== 第 2 课：数字和小数误差 ==
✅ 0.1 + 0.2 和 0.3 用 == 比较居然不相等
✅ 但它们“足够接近”
❌ 2.5 不算整数：条件不成立
⏳ 无穷大不算整数（还没写，找 TODO）
-- 通过 2，不对 1，没写 1
```

✅ 对了，❌ 不对（会告诉你期望值和实际值），⏳ 还没写。全部 ✅ 就完成了这一课。
常见的错误还会多给一句原因，比如：

```text
❌ 10 元买 3 元的东西：最多 3 个：期望 3，实际 3.3333333333333335
   💡 期望整数，你算出了小数：要整数时用 //（整除），不是 /。
```

**卡住了？** 一级一级地要提示（网页上点 **💡 提示**）：

```bash
python3 python/tutorial/run.py 02 --hint      # 每个函数先给个方向
python3 python/tutorial/run.py 02 --hint 2    # 还不行？给出接近代码的写法
```

实在想不出来，参考答案在 [`solutions/`](solutions/)，用 `run.py 02 --solution` 运行。建议先自己写，写完再对照：参考答案不是唯一写法。

几种特别的题：标着 **🤔 先猜后跑** 的，先别运行，把你猜的结果写在 `return` 后面，再运行看看猜得对不对；
第 13 课是 **🐞 找 bug**：代码已经写好了，但有错，要找出来改好。

看看一共完成了多少：`python3 python/tutorial/run.py all` 会打印一张进度表。

## 课程目录

### 第 0 阶段：零基础入门（A1～A8，每节 10～20 分钟）

| 课 | 主题 | 练习 |
|---|---|---|
| [A1](lessons/a1-hello.md) | 让程序说话：`print`、字符串、f-string | 打招呼、报价 |
| [A2](lessons/a2-variables.md) | 变量和计算：`int`、`float`、`//` 和 `%` | 总价、找零、最多买几个 |
| [A3](lessons/a3-decisions.md) | 做判断：`if / elif / else`、`and`、`or` | 钱够不够、满 99 包邮、成绩等级 |
| [A4](lessons/a4-loops.md) | 重复做事：`for`、`range`、`while` | 1 加到 n、攒钱要几天 |
| [A5](lessons/a5-functions.md) | 自己写函数：参数、返回值、默认参数 | 温度换算、`clamp`、打折 |
| [A6](lessons/a6-lists.md) | 列表：一次存一排数 | 一周步数的总和、最大值、平均数 |
| [A7](lessons/a7-strings.md) | 字符串：下标、切片、`split` | 名字缩写、手机号打码 |
| [A8](lessons/a8-project.md) | 小项目：挑水果 | 两层循环试遍所有买法，再和求解器对答案 |

练习运行方式：`python3 python/tutorial/run.py A01`（也可以写 `A1`）。A8 做完，就可以进入正式课程了。

### 第 1～12 课：用 minicplex 学 Python

| 课 | 主题 | 用到的 minicplex 代码 | 练习 |
|---|---|---|---|
| [01](lessons/01-first-model.md) | 第一个模型：模块、`import`、`python -m` | `examples/basics_01_one_variable.py`、`__init__.py` | 建一个冰淇淋模型 |
| [02](lessons/02-numbers.md) | 数字和小数误差：容差、`inf`、三种四舍五入、`-0.0` | `jmath.py`、`lp_engine.py` 的容差 | 写 `near`、`is_integral`、`cround` |
| [03](lessons/03-lists.md) | 列表、推导式、`zip`、`itertools` | `lp_engine.py` 的一维矩阵 `T[i * N + j]` | 暴力背包 vs 求解器 |
| [04](lessons/04-classes.md) | 类和对象：`__init__`、`@property`、`__repr__` | `VarInfo`、`Model.add_var` | 写一个商品类 |
| [05](lessons/05-operators.md) | **运算符重载**和不可变对象 | `LinExpr`：`2 * x + 3 * y <= 12` 是怎么工作的 | 写一个迷你表达式类 |
| [06](lessons/06-dataclass-enum.md) | dataclass 和 enum、可变默认值的坑 | `Params`、`Result`、`Status` | 天气 enum、frozen 点、购物车 |
| [07](lessons/07-dicts-sets.md) | 字典和集合 | `Model._index`、合并同类项、为什么要排序 | 建索引、合并同类项 |
| [08](lessons/08-sorting-heaps.md) | 排序、`lambda`、`heapq` | 分支定界的节点队列、稳定排序的故事 | 实现节点排序规则 |
| [09](lessons/09-exceptions.md) | 异常、`with`、`raise … from None` | `LpParseError`、命令行的兜底 | 安全解析、读 LP 文件 |
| [10](lessons/10-text.md) | 字符串和文本处理、格式说明符 | `lp_reader.py` 的词法分析、`to_lp` | 迷你词法分析器、报表 |
| [11](lessons/11-testing.md) | 测试：`unittest`、随机对拍 | `tests/test_solver.py`、三个版本互相对拍 | 随机出题 + 暴力对拍 |
| [12](lessons/12-project.md) | 综合项目：选课助手 | 前面全部 | 从文本到模型到报表 |

### 进阶 13～19 课：真实项目天天用的

| 课 | 主题 | 用到的 minicplex 代码 | 练习 |
|---|---|---|---|
| [13](lessons/13-debugging.md) | 读懂报错、调试和 `assert` | `solver.py` 的 `assert` 和 `check_feasible` 自检 | 🐞 **找 bug**：五个能跑但答案错的函数 |
| [14](lessons/14-functions.md) | 函数进阶：`*args`、`**kwargs`、拆包、闭包 | `Params(**...)`、测试里的 `product(*...)` | 计数器、循环里造 lambda 的坑 |
| [15](lessons/15-decorators.md) | 装饰器：`@property`、`@dataclass` 到底是什么 | `model.py`、`solver.py` 里的装饰器 | `count_calls`、`retry`、`memoize` vs `lru_cache` |
| [16](lessons/16-generators.md) | 生成器和迭代器：`yield`、`itertools` | `sum(... for ...)`、`itertools.product` | 无穷斐波那契、递归生成所有组合 |
| [17](lessons/17-files-data.md) | 文件和数据：`pathlib`、CSV、JSON | `read_file` 的编码、对比脚本读 CSV、`make_web.py` 写 JSON | CSV → 建模选货 → JSON |
| [18](lessons/18-cli-packaging.md) | 命令行程序和打包：`argparse`、`python -m`、`pip`、虚拟环境 | `__main__.py`、`pyproject.toml` | 一个迷你版的 minicplex 命令行 |
| [19](lessons/19-optimality.md) | 为什么知道这是最优解：对偶证书、间隙、博弈的保底和封顶 | `Result.duals`、`best_bound`、`solver.py` 的间隙判断 | 手写证书检查，给点球博弈证明最优 |

入门小课每节 10～20 分钟；正式课和进阶课每课大约 30～60 分钟。01～06 是语言基础，07～10 是标准库，11～12 是工程实践，13～19 是进阶。

## 学完能做什么

- 读懂 minicplex 的全部 Python 代码（[`python/minicplex/`](../minicplex/)）；
- 用 Python 写一个“读数据 → 建模 → 求解 → 出报表”的小应用；
- 给自己的代码写可复现的自动测试；
- 继续挑战：读 [`lp_engine.py`](../minicplex/lp_engine.py)（单纯形法内核），或者对照 [Java 课](../../java/tutorial/README.md) 看同一段算法在另一种语言里的样子。

## 给老师

- 每课的练习都是一个独立的 `.py` 文件，只用标准库，在任何装了 Python 3.9+ 的机器上都能运行和判分。
- 参考答案由 CI 在 Python 3.9 和 3.13 上自动运行，保证永远能通过；练习文件由
  [`make_exercises.py`](make_exercises.py) 从答案生成（答案里 `# >>>` 和 `# <<<` 之间的部分会被挖空；
  “找 bug”题在答案后面加 `# ===` 和一段注释掉的有 bug 的版本，练习里放的就是那个版本）。
- 想加一道题：在 `solutions/` 里写好答案并用 `# >>>`、`# <<<` 标出要挖空的部分，在 [`hints.py`](hints.py) 里给这个函数写两级提示，
  再运行 `python3 python/tutorial/make_exercises.py`。CI 会检查每个挖空的函数都有提示。
- 网页版由 [`make_web.py`](make_web.py) 从同一套课文和练习生成，GitHub Actions 每次先在真浏览器里把 27 课的答案和练习跑一遍（中英文两个版本）（[`web/test_site.py`](web/test_site.py)），通过了才发布。Python 运行时（Pyodide）和网站放在一起，打不开 CDN 的地方也能用。
- 判分框架 [`check.py`](solutions/check.py) 只有 100 来行，学生读得懂；退出码 0 = 全对，1 = 有错，3 = 没写完，方便批量收作业。
