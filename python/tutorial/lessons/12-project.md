# 第 12 课：综合项目——选课助手

> **这一课学：** 把前面的东西串成一个完整的小应用：读文本 → 解析成对象 → 建模型 → 求解 → 出报表
> **用到的代码：** 前面全部；对照 [`hard_staff_schedule.py`](../../examples/hard_staff_schedule.py)（一个更大的同类项目）
> **练习：** `python3 python/tutorial/run.py 12`
> **在线做：** [打开网页版，不用安装](https://xudaniel.github.io/minicplex/python/#l12)

[← 测试](11-testing.md) · [目录](../README.md) · 下一课：[进阶：读懂报错和调试 →](13-debugging.md)

## 1. 题目

```text
# 课程     学分  每周小时  上课日  兴趣
Python     4     6        Mon     9
算法       4     8        Tue     10
数据库     3     5        Mon     7
运筹学     3     6        Wed     10
...
```

在这些限制下选课，让“兴趣分”总和最大：

1. 每周总小时数不超过 `max_hours`；
2. 总学分至少 `min_credits`；
3. 每天最多 2 门课；
4. 选“算法”就必须选“Python”（先修课）。

## 2. 分层：每一层只做一件事

```text
文本 ──parse()──▶ [Course, Course, ...] ──choose()──▶ ["Python", "运筹学", ...] ──report()──▶ 表格
```

- `parse` 只管文本，不知道什么是优化。格式不对就 `raise ValueError`（第 9 课），带上出错的那一行。
- `Course` 是一个 frozen dataclass（第 6 课）：解析完就不再改。
- `choose` 只管建模和求解，不知道数据是从文件来的还是网页来的。
- `report` 只管排版（第 10 课）。

这样每一层都能单独测试，以后要换数据来源（比如读 Excel）只改 `parse`。真实项目几乎都是这个结构，
[`hard_staff_schedule.py`](../../examples/hard_staff_schedule.py)（8 个员工、一周排班、10 条规则）就是一个大一号的版本。

## 3. 建模的几个技巧

```python
take = [m.add_var(0, 1, VarType.BINARY, f"take_{k}") for k in range(len(courses))]   # 每门课选不选
pairs = list(zip(courses, take))

sum((c.hours * t for c, t in pairs), LinExpr()) <= max_hours                          # 总小时
sum((t for c, t in pairs if c.day == day), LinExpr()) <= 2                            # 某一天的课数：生成器里带条件
index["算法"] <= index["Python"]                                                       # 先修课：选了算法(1) 就必须选 Python(1)
```

- `sum(…, LinExpr())`：第二个参数是起点。从 `LinExpr()` 开始加，即使一项都没有（某天没课），得到的也是一个空表达式，而不是整数 `0`。
- “选 A 就必须选 B” 写成 `A <= B`：两个都是 0/1，只有 A=1、B=0 被排除。这是 0-1 建模里最常用的一招（[`easy2_projects.py`](../../examples/easy2_projects.py) 的 `C_needs_D` 也是它）。
- 无解时求解器返回 `Status.INFEASIBLE`，`choose` 把它变成空列表，调用的人不用知道求解器的细节。

## 4. 测试不只看一个答案

练习里除了“这几个参数下应该选哪几门”，还有两条**性质**测试：对 0～40 小时的每一种情况，
“选了算法就一定选了 Python”和“每天最多 2 门”都必须成立。性质测试不需要知道正确答案是什么，却能一次检查几十种情况——
第 11 课对拍思路的又一个应用。

## 5. 动手

打开 [`exercises/l12_project.py`](../exercises/l12_project.py)，写 `parse` 和 `choose`，运行 `python3 python/tutorial/run.py 12`。全部通过后会打印出选课表。

## 6. 接下来

- 继续学[进阶 13～19 课](13-debugging.md)。
- 给选课助手加一条规则：“数据库和写作不能都选”，或者“至少选一门 Wed 的课”。
- 改成从文件读课程表，文件不存在或格式不对时给出友好的提示（第 9 课）。
- 读 minicplex 的源代码。推荐顺序：[`model.py`](../../minicplex/model.py)（建模层）→ [`lp_reader.py`](../../minicplex/lp_reader.py)（读文件）→
  [`solver.py`](../../minicplex/solver.py)（分支定界）→ [`lp_engine.py`](../../minicplex/lp_engine.py)（单纯形法内核）。
  主 README 的[代码解析](../../../README.md#代码解析)一节逐段讲解了算法（用的是 C++ 版，Python 版是逐行对应的）。
- 也想学 Java？同一个求解器的 [Java 版和 20 节 Java 课](../../../java/tutorial/README.md)，可以对照着看同一段算法在两种语言里怎么写。

🎉 恭喜你学完了正式课！还想继续？**进阶 13～19 课**补上真实项目里天天用的几样：读报错和调试、函数进阶、装饰器、生成器、文件和数据、命令行和打包。

[← 测试](11-testing.md) · [目录](../README.md) · 下一课：[进阶：读懂报错和调试 →](13-debugging.md)
