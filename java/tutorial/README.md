# 用 minicplex 学 Java

> 一门用**真实项目**学 Java 的中文小课：12 课，每课一个 Java 知识点，例子全部取自 minicplex 求解器的源代码，
> 每课配一道能自动判分的练习。

大多数 Java 教程用“学生类”“动物类”举例，学完了还是不知道真实项目里代码长什么样。这门课反过来：
先摆出 minicplex（一个能真正解优化题的求解器，约 2,600 行 Java）里的一段代码，再讲它用到的 Java 知识，
以及**为什么这样写**。学完你不仅会 Java 语法，还能读懂一个完整的项目。

## 适合谁

- 学过一点编程（任何语言都行），知道变量、if、循环是什么；
- 想系统学 Java，或者想知道“真实的 Java 项目”是怎么组织的；
- 不需要懂优化算法，用到的地方都会用大白话解释。完全没接触过优化，可以先读主 README 的
  [用大白话讲 minicplex](../../README.md#用大白话讲-minicplex先看这里)（5 分钟）。

## 准备

需要 JDK 17 或更新版本（`java -version` 查看）。不需要 Maven，也不需要 IDE，命令行就够了。

```bash
git clone https://github.com/xudaniel/minicplex.git && cd minicplex
java/build.sh                      # 编译求解器（约 10 秒）
java/tutorial/run.sh 01            # 运行第 1 课的练习
```

## 练习怎么做

每课的练习在 [`exercises/minicplex/tutorial/`](exercises/minicplex/tutorial/) 里，文件名是 `L01…`、`L02…`。
打开文件，找到 `TODO`，把 `throw new UnsupportedOperationException("TODO");` 换成你的代码，然后运行：

```text
$ java/tutorial/run.sh 02
== 第 2 课：数字和小数误差 ==
✅ 0.1 + 0.2 和 0.3 用 == 比较居然不相等
✅ 但它们是“足够接近”的
❌ 2.5 不算整数：条件不成立
⏳ 无穷大不算整数（还没写，找 TODO）
-- 通过 2，不对 1，没写 1
```

✅ 对了，❌ 不对（会告诉你期望值和实际值），⏳ 还没写。全部 ✅ 就完成了这一课。

卡住了？参考答案在 [`solutions/`](solutions/minicplex/tutorial/)，用 `run.sh 02 --solution` 运行。
建议先自己写，写完再对照：参考答案不是唯一写法。

## 课程目录

| 课 | 主题 | 用到的 minicplex 代码 | 练习 |
|---|---|---|---|
| [01](lessons/01-first-program.md) | 第一个程序：编译、运行、包 | `examples/Basics01OneVariable`、`build.sh` | 建一个冰淇淋模型 |
| [02](lessons/02-numbers.md) | 基本类型和小数误差 | `Model.INF`、`LPEngine` 的容差、`Solver.cround` | 写 `near`、`isIntegral`、四舍五入 |
| [03](lessons/03-arrays.md) | 数组和循环 | `LPEngine` 的一维矩阵 `A[i * n + j]`、`Basics08MinMax` | 暴力背包 vs 求解器 |
| [04](lessons/04-classes.md) | 类和对象 | `VarInfo`、`Model.addVar` 的重载、复制构造方法 | 写一个商品类 |
| [05](lessons/05-immutable.md) | 封装和不可变对象 | `LinExpr`（每次运算返回新对象）、`Model(Model)` 深复制 | 写一个不可变表达式 |
| [06](lessons/06-records-enums.md) | record 和 enum | `Var`、`Status`、`Main` 的 switch 表达式 | record、带标签的 enum |
| [07](lessons/07-collections.md) | List 和 Map | `Model` 的名字索引、`LinExpr` 的 `TreeMap` 和 `merge` | 建索引、合并同类项 |
| [08](lessons/08-comparators.md) | lambda、比较器、优先队列 | 分支定界的节点队列、稳定排序的故事 | 实现节点排序规则 |
| [09](lessons/09-exceptions.md) | 异常 | `LpReader` 的报错、`Model.addVar` 的检查、`Main` 的兜底 | 安全解析、读文件 |
| [10](lessons/10-strings.md) | 字符串和文本处理 | `LpReader.tokenize`、`Fmt`、`Model.toLP` | 迷你词法分析器 |
| [11](lessons/11-testing.md) | 包、访问控制和测试 | `SolverTest`、包内可见的 `LPEngine` | 随机测试 + 暴力对拍 |
| [12](lessons/12-project.md) | 综合项目：选课助手 | 前面全部 | 从文本到模型到报表 |

每课大约 30～60 分钟。01～06 是语言基础，07～10 是标准库，11～12 是工程实践。

## 学完能做什么

- 读懂 minicplex 的全部 Java 代码（[`java/src/main/java/minicplex/`](../src/main/java/minicplex/)）；
- 用 Java 写一个“读数据 → 建模 → 求解 → 出报表”的小应用；
- 给自己的代码写可复现的自动测试；
- 继续挑战：读 [`LPEngine.java`](../src/main/java/minicplex/LPEngine.java)（单纯形法内核），或者给求解器加一个新功能。

## 给老师

- 每课的练习都是独立的 `main` 程序，不依赖 JUnit 或 IDE，在任何装了 JDK 的机器上都能运行和判分。
- 参考答案由 CI 在 JDK 17 和 21 上自动运行，保证永远能通过；练习文件由
  [`make_exercises.py`](make_exercises.py) 从答案生成（答案里 `// >>>` 和 `// <<<` 之间的部分会被挖空）。
- 想加一道题：在 `solutions/` 里写好答案并用 `// >>>`、`// <<<` 标出要挖空的部分，再运行 `python3 java/tutorial/make_exercises.py`。
