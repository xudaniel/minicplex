# 第 12 课：综合项目——选课助手

> **这一课学：** 把前 11 课串起来，写一个完整的小应用：读文本数据 → 建模型 → 求解 → 出报表
> **用到的代码：** 前面全部，以及 [`HardStaffSchedule.java`](../../examples/minicplex/examples/HardStaffSchedule.java)（一个更大的同类例子）
> **练习：** `java/tutorial/run.sh 12`

[← 包、访问控制和测试](11-testing.md) · [目录](../README.md)

## 1. 需求

学期开始，要从 7 门课里选几门：

```text
# 课程     学分  每周小时  上课日  兴趣
Java       4     6        Mon     9
算法       4     8        Tue     10
数据库     3     5        Mon     7
运筹学     3     6        Wed     10
英语       2     3        Tue     4
体育       1     2        Wed     3
写作       2     4        Mon     5
```

规则：

1. 每周上课总时间不超过 H 小时；
2. 总学分至少 C 分；
3. 每天最多 2 门课；
4. 选“算法”就必须选“Java”（先修课）。

目标：兴趣分总和最高。

## 2. 拆成三步

真实的应用几乎都是这三步，每一步都可以单独测试：

```text
文本  ──parse──▶  List<Course>  ──choose──▶  选中的课  ──format──▶  报表
（第 10 课）     （第 6、7 课）   （第 1、3 课）           （第 10 课）
```

### 第一步：解析（parse）

每一行是一门课。用第 6 课的 record 表示：

```java
record Course(String name, int credits, int hours, String day, int interest) {}
```

解析时要处理：空行和 `#` 开头的注释跳过；每行按空白切成 5 段（`split("\\s+")`）；数字转换失败时，抛出一个说清楚哪一行出错的异常（第 9 课）。

### 第二步：建模求解（choose）

每门课一个 0-1 变量 `take[k]`（选 = 1，不选 = 0），然后把四条规则翻译成约束：

| 规则 | 约束 | 写法 |
|---|---|---|
| 总时间 ≤ H | Σ 小时ₖ × takeₖ ≤ H | 循环累加 `hours = hours.plus(c.hours(), take[k])` |
| 总学分 ≥ C | Σ 学分ₖ × takeₖ ≥ C | 同上，用 `ge` |
| 每天最多 2 门 | 对每一天：Σ（这天的课）takeₖ ≤ 2 | 外层循环遍历三天，内层筛出这天的课 |
| 算法需要 Java | take算法 ≤ takeJava | 选了算法（= 1）时，Java 也必须是 1 |

最后一条就是主 README 建模速查表里的“选了 A 就必须选 B：a ≤ b”。

### 第三步：报表

用 `String.format` 把选中的课排成表，再算出合计。这时你会亲眼看到第 10 课说的问题：中文课名和英文课名混在一起，表格对不齐。可以试着修好它（提示：一个汉字按 2 格算，自己补空格）。

## 3. 一个更大的同类例子

[`HardStaffSchedule.java`](../../examples/minicplex/examples/HardStaffSchedule.java) 是餐厅 8 个员工一周的排班，结构和选课助手完全一样，只是规则多了（10 条）、变量多了（112 个）：

- 用 record `Staff` 存员工信息（时薪、可上班的日子、偏好）；
- 用三维数组 `Var[][][] x = new Var[E][D][S]` 表示“员工 e 在第 d 天上第 s 班”；
- 每条规则一个循环，翻译成约束；
- 结果排成一张排班表。

做完练习后读一读它，你会发现自己已经能看懂每一行了。

## 4. 动手

练习 [`L12Project.java`](../exercises/minicplex/tutorial/L12Project.java)：完成 `parse` 和 `choose`。检查项包括：

- 解析出 7 门课，格式错误的行会报错；
- 每周 20 小时、至少 10 学分时，最优选择是 Java、数据库、运筹学、英语（兴趣 30）；
- 每周 28 小时时，可以加上算法；
- 时间太少、学分要求太高时无解；
- 不管时间给多少，先修课和“每天最多 2 门”这两条规则都不会被违反。

```bash
java/tutorial/run.sh 12
```

全部通过后，程序会打印出选课表。

## 5. 继续挑战

1. **加一条规则：** 体育是必修课，一定要选。（提示：给 `take[体育]` 加一条 `= 1` 的约束，或者直接把它的下限设成 1。）
2. **从文件读：** 把课程表存成 `courses.txt`，用 `Files.readString` 读进来，再交给 `parse`。
3. **做成命令行工具：** `java ... CoursePlanner courses.txt --hours 20 --credits 10`，参考 `Main.java` 怎么解析参数。
4. **看看求解器怎么想的：** 在 `choose` 里打开 `Params.trace`，看分支定界一步步怎么找到答案。
5. **自己出题：** 把排班、排课、配餐、装箱……任何“在限制下选最好的”的问题写成模型。主 README 的[建模技巧速查表](../../../README.md#建模技巧速查表)能帮你把规则翻译成约束。

## 6. 结业

12 课走完，你已经用到了 Java 最常用的大部分东西：类和对象、不可变设计、record 和 enum、集合、lambda、异常、字符串处理、包和测试。更重要的是，你读的不是教学用的玩具代码，而是一个真正能解题、被几千道题检验过的求解器。

接下来可以：

- 从 [`Solver.java`](../../src/main/java/minicplex/Solver.java) 的 `solve()` 开始，读分支定界的完整流程；
- 对照主 README 的[代码解析](../../../README.md#代码解析)（讲的是 C++ 版，Java 版逐行对应）读单纯形内核；
- 给 minicplex 提一个 pull request，流程见 [CONTRIBUTING.md](../../../CONTRIBUTING.md)。

[← 包、访问控制和测试](11-testing.md) · [目录](../README.md)
