# 第 11 课：包、访问控制和测试

> **这一课学：** `public`、包内可见、`private` 四种访问级别；怎么设计“对外的接口”；不用框架写测试；随机测试和“标准答案”
> **用到的代码：** [`LPEngine.java`](../../src/main/java/minicplex/LPEngine.java)、[`Presolve.java`](../../src/main/java/minicplex/Presolve.java)、[`SolverTest.java`](../../src/test/java/minicplex/SolverTest.java)
> **练习：** `java/tutorial/run.sh 11`

[← 字符串和文本处理](10-strings.md) · [目录](../README.md) · 下一课：[综合项目：选课助手 →](12-project.md)

## 1. 四种访问级别

| 写法 | 谁能访问 | minicplex 里的例子 |
|---|---|---|
| `public` | 所有人 | `Model`、`Solver.solve`、`Result`：用户要用的东西 |
| `protected` | 同一个包 + 子类 | 没用到（minicplex 不用继承） |
| （什么都不写） | 只有同一个包 | `LPEngine`、`Presolve`：求解器内部零件 |
| `private` | 只有这个类自己 | `Model.index`、`LinExpr.copy()` |

```java
// LPEngine.java
final class LPEngine {          // 没写 public：包外的代码根本看不到这个类
    ...
}
```

用户写 `import minicplex.*;` 也用不了 `LPEngine`。这是有意的：**对外公开的东西越少，以后改内部实现越自由**。单纯形内核哪天换成更快的算法，只要 `Solver.solve` 的用法不变，用户的代码一行都不用改。

> 练习都在 `minicplex.tutorial` 包里，所以只能用 `public` 的部分。这正好模拟了“普通用户”的视角。

## 2. 测试放在同一个包里

测试要检查内部零件（比如每个割平面是否有效），需要访问 `LPEngine`。办法是把测试类也放在 `minicplex` 包里，只是放在另一个目录：

```text
java/src/main/java/minicplex/LPEngine.java       ← 产品代码
java/src/test/java/minicplex/SolverTest.java     ← 测试代码，同一个包
```

包看的是 `package` 声明，不是目录，所以测试能访问包内可见的类，打包发布时又可以不带上测试。Maven 等工具都按这个约定组织项目。

## 3. 不用框架也能写测试

业界常用 JUnit 写测试。minicplex 为了零依赖，自己写了一个二十几行的小框架：

```java
// SolverTest.java
private static int passes = 0, fails = 0;

private static void check(boolean cond, String what) {
    if (cond) ++passes;
    else {
        ++fails;
        System.err.println("FAIL: " + what);
    }
}

static void testClassicLP() {
    Model m = new Model();
    Var x = m.addVar(), y = m.addVar();
    m.addConstr(x(x).le(4));
    m.addConstr(x(2, y).le(12));
    m.addConstr(x(3, x).plus(2, y).le(18));
    m.setObjective(x(3, x).plus(5, y), ObjSense.MAXIMIZE);
    Result r = Solver.solve(m);
    check(r.status == Status.OPTIMAL, "classic LP status");
    check(near(r.objective, 36), "classic LP objective");
}
```

教科书例题的答案是已知的（最优值 36），直接核对。练习用的 `Check` 类是同一个思路，只是多了 ✅❌⏳ 的显示。

## 4. 随机测试：让暴力枚举当裁判

几道手写的例题远远不够，真正的 bug 藏在你想不到的情况里。minicplex 最有力的测试是：**随机生成 500 道小题，每道都用暴力枚举算出标准答案，再和求解器比**。

```java
// SolverTest.java（简化）
Random rng = new Random(12345);                 // 固定种子
for (int t = 0; t < instances; ++t) {
    Model M = ...随机生成...;
    double best = ...逐点枚举所有整数点，找最好的可行点...;
    for (int cfg = 0; cfg < 3; ++cfg) {         // 三套参数各解一遍
        Result r = Solver.solve(M, P);
        ok = ok && (Double.isNaN(best) ? r.status == Status.INFEASIBLE
                                       : r.status == Status.OPTIMAL && near(r.objective, best));
    }
}
```

几个关键设计：

- **固定随机种子**：`new Random(12345)` 每次生成的“随机数”都一样，测试失败时能稳定复现，不会“偶尔失败一次再也找不到”。
- **暴力枚举当裁判**：它慢，但简单到几乎不可能写错。用简单可靠的方法检查复杂的方法，是测试的核心思想。
- **多套参数**：同一道题，开关预处理、割平面、不同分支规则都要得到同一个答案。

minicplex 在更大的范围上也是这么做的：用 HiGHS、OR-Tools 当裁判对比上万道题；Java 版和 C++ 版互相当裁判，要求每一步都一样。

## 5. 常见坑

- **测试依赖执行顺序**：每个测试应该自己建自己的数据，不要依赖上一个测试留下的状态。
- **随机测试不固定种子**：失败了却复现不出来，等于没测。
- **只测“正常情况”**：无解、无界、空模型、所有变量都固定……边界情况最容易出 bug。`SolverTest` 里专门有一组 `testEngineEdgeCases`。

## 6. 动手

练习 [`L11Testing.java`](../exercises/minicplex/tutorial/L11Testing.java)：

1. `bruteForce`：用 `Solver.checkFeasible` 和 `Solver.evalObjective` 暴力求解全是 0-1 变量的模型；
2. `agreeCount`：跑 200 道随机题，统计求解器和暴力答案一致的题数，要求 200 道全对。

```bash
java/tutorial/run.sh 11
```

## 7. 想一想

1. 如果暴力枚举本身写错了，测试还有意义吗？怎么降低这种风险？
2. `LPEngine` 为什么不做成 `public`，方便高级用户直接调用？

<details>
<summary>参考答案</summary>

1. 如果两边错得一样，测试会漏掉 bug；但两边独立写、方法完全不同，恰好错成一样的概率很小。再加上几道手算答案的例题检查暴力枚举本身，风险就更低了。minicplex 还用了第三方求解器当裁判，相当于“三方会审”。
2. 一旦公开，就要对它的用法长期负责，以后想改内部结构（比如换成稀疏矩阵）就会破坏用户的代码。真有需要，可以只公开一个小而稳定的接口，而不是整个内部零件。

</details>

[← 字符串和文本处理](10-strings.md) · [目录](../README.md) · 下一课：[综合项目：选课助手 →](12-project.md)
