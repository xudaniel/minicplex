# 入门 A8：小项目——挑水果

> **这一课学：** 把 A1～A7 串起来：方法、判断、两层循环、数组，暴力试遍所有组合找最好的；再看求解器怎么做
> **大约：** 20 分钟 · **练习：** `java/tutorial/run.sh A08`

[← 字符串](a7-strings.md) · [目录](../README.md) · 下一课：[第 1 课：第一个模型 →](01-first-program.md)

## 1. 题目

去水果店：

- 苹果 2 元一个，好吃程度 3 分；香蕉 1 元一根，2 分；
- 你有 10 元；
- 袋子最多装 7 个。

怎么买，总分最高？

## 2. 拆成三个小方法

| 方法 | 做什么 | 用到 |
|---|---|---|
| `fits(apples, bananas)` | 钱够不够、袋子装不装得下 | A3：`&&` |
| `score(apples, bananas)` | 这样买得几分 | A2：计算 |
| `best()` | 试遍所有买法，留下最好的 | A4：两层 `for`；A6：数组 |

`best()` 的思路：

```java
int[] best = {0, 0, 0};                 // {苹果, 香蕉, 分数}
for (int a = 0; a <= 5; a++)            // 苹果：0 到 5 个（10 元最多买 5 个）
    for (int b = 0; b <= 10; b++)       // 香蕉：0 到 10 根
        if (fits(a, b) && score(a, b) > best[2])
            best = new int[] {a, b, score(a, b)};
```

外层每转一圈，内层要转一整轮，所以一共试 6 × 11 = 66 种买法。

## 3. 答案

3 个苹果 + 4 根香蕉，17 分。钱刚好花完（2×3 + 4 = 10），袋子刚好装满（3 + 4 = 7）。

## 4. 这和 minicplex 有什么关系？

练习文件最后有一段不用你写的代码，把同一道题交给 minicplex 求解器：

```java
Model m = new Model();
Var apple = m.addVar(0, Model.INF, VarType.INTEGER, "apple");
Var banana = m.addVar(0, Model.INF, VarType.INTEGER, "banana");
m.addConstr(LinExpr.of(2, apple).plus(1, banana).le(10), "money");   // 钱
m.addConstr(LinExpr.of(apple).plus(banana).le(7), "bag");            // 袋子
m.setObjective(LinExpr.of(3, apple).plus(2, banana), ObjSense.MAXIMIZE);
```

求解器也得到 17 分。区别在于：

- **暴力试遍**：两种水果试 66 次很快；但 20 种东西、每种 0 到 10 个，就要试 11²⁰ 次，算到宇宙尽头也算不完。
- **求解器**：你只描述“有什么限制、想要什么”，它用单纯形法和分支定界，跳过绝大多数明显不好的组合。

这就是这门课后半段要学的东西。

## 5. 动手

[`A08FruitProject.java`](../exercises/minicplex/tutorial/A08FruitProject.java)：写完 `fits`、`score` 和 `best`。

```bash
java/tutorial/run.sh A08
```

## 6. 入门毕业 🎉

A1～A8 学完，你已经会写变量、判断、循环、方法、数组和字符串，这些是所有编程语言共通的基础。接下来进入正式课程：

- [第 1 课：第一个程序——编译、运行、包](01-first-program.md)，第一次用 minicplex 自己建模型；
- 想先多看看求解器能解什么题，读主 README 的[入门例子](../../../README.md#入门例子从最简单开始)。

[← 字符串](a7-strings.md) · [目录](../README.md) · 下一课：[第 1 课：第一个模型 →](01-first-program.md)
