# 第 1 课：第一个程序——编译、运行、包

> **这一课学：** Java 程序的基本结构、`javac` 和 `java` 两条命令、包（package）和 import
> **用到的代码：** [`Basics01OneVariable.java`](../../examples/minicplex/examples/Basics01OneVariable.java)、[`build.sh`](../../build.sh)
> **练习：** `java/tutorial/run.sh 01`

[目录](../README.md) · 下一课：[数字和小数误差 →](02-numbers.md)

## 1. 一个完整的 Java 程序

minicplex 最简单的例子只解一个问题：你有 10 元，苹果 2 元一个，最多买几个？去掉注释，它长这样：

```java
package minicplex.examples;

import minicplex.*;

public class Basics01OneVariable {
    public static void main(String[] args) {
        Fmt.useUtf8Output();

        Model m = new Model();                                            // 第 1 步：建模型
        Var apples = m.addVar(0, Model.INF, VarType.CONTINUOUS, "apples"); // 第 2 步：建变量
        m.addConstr(LinExpr.of(2, apples).le(10), "money");               // 第 3 步：加限制 2 × 苹果 ≤ 10
        m.setObjective(LinExpr.of(apples), ObjSense.MAXIMIZE);            // 第 4 步：定目标

        Params p = new Params();
        p.trace = args.length > 0 && args[0].equals("--trace");
        Result r = Solver.solve(m, p);

        System.out.println("状态：" + r.status);
        System.out.println("最多买 " + Fmt.g(r.value(apples)) + " 个苹果");
    }
}
```

逐行看：

| 代码 | 意思 |
|---|---|
| `package minicplex.examples;` | 这个类属于 `minicplex.examples` 包。包就是“文件夹 + 名字空间”，所以文件必须放在 `minicplex/examples/` 目录下 |
| `import minicplex.*;` | 用到 `minicplex` 包里的类（`Model`、`Var`……）时，不用写全名 `minicplex.Model` |
| `public class Basics01OneVariable` | 一个公开的类。**类名必须和文件名一样**：`Basics01OneVariable.java` |
| `public static void main(String[] args)` | 程序入口。`java` 命令会找到它并从这里开始执行；`args` 是命令行参数 |
| `Model m = new Model();` | 创建一个 `Model` 类型的对象，起名叫 `m`（第 4 课细讲） |
| `System.out.println(...)` | 打印一行。`+` 可以把字符串和别的东西拼起来 |

> **Java 规则：** 每条语句以分号结束；大括号 `{ }` 圈出代码块；大小写敏感，`model` 和 `Model` 是两个东西。

## 2. 两条命令：javac 编译，java 运行

Java 程序要先**编译**成字节码（`.class` 文件），再由 JVM（Java 虚拟机）**运行**。打开 [`build.sh`](../../build.sh)，去掉检查选项后，核心只有这两行：

```bash
javac --release 17 -d build/classes $(find src/main/java -name '*.java')   # 编译：.java → .class
jar --create --file build/minicplex.jar --main-class minicplex.Main -C build/classes .   # 打包成一个 jar
```

- `javac`：Java 编译器。`--release 17` 表示按 Java 17 的标准编译；`-d` 指定 `.class` 放在哪里。
- `jar`：把一堆 `.class` 打包成一个文件，`--main-class` 记下“默认从哪个类的 main 开始”。

然后就可以运行了：

```bash
java -jar java/build/minicplex.jar examples/bakery.lp                       # 运行 jar 里的默认入口（命令行求解器）
java -cp java/build/minicplex.jar minicplex.examples.Basics01OneVariable    # 运行指定的类
java -cp java/build/minicplex.jar minicplex.examples.Basics01OneVariable --trace   # 带参数：args[0] 就是 "--trace"
```

`-cp`（classpath）告诉 JVM 去哪里找类，后面跟的是**类的全名**（包名 + 类名）。

## 3. 四步建模

所有 minicplex 程序都是这四步，练习也一样：

1. `new Model()`：一个空模型；
2. `addVar(下限, 上限, 类型, 名字)`：建变量，`Model.INF` 表示没有上限；类型有 `CONTINUOUS`（可以是小数）、`INTEGER`（整数）、`BINARY`（0 或 1）；
3. `addConstr(表达式.le(数), 名字)`：加限制，`le` 是 ≤，`ge` 是 ≥，`eq` 是 =；
4. `setObjective(表达式, ObjSense.MAXIMIZE 或 MINIMIZE)`：定目标。

`Solver.solve(m)` 返回一个 `Result`：`r.status` 是状态，`r.objective` 是目标值，`r.value(变量)` 是变量的取值。

## 4. 常见坑

- **类名和文件名不一致**：`class Hello` 写在 `hello.java` 里会编译失败（大小写也要一致）。
- **包和目录不一致**：`package minicplex.tutorial;` 的文件必须在 `minicplex/tutorial/` 目录下。
- **中文乱码**：Windows 控制台默认不是 UTF-8。minicplex 用 `Fmt.useUtf8Output()` 强制按 UTF-8 输出，你的程序也可以这样做。
- **`java Basics01OneVariable.java`**：Java 11 起可以直接运行单个源文件，但它依赖别的类（`Model` 等）时要加 `-cp`。

## 5. 动手

打开 [`exercises/minicplex/tutorial/L01FirstModel.java`](../exercises/minicplex/tutorial/L01FirstModel.java)，
在 `iceCreamModel()` 里建出这个模型：

> 你有 25 元，冰淇淋 3 元一个，只能买整数个。最多买几个？

```bash
java/tutorial/run.sh 01
```

做完后试试：把 `Solver.solve(m)` 换成带 `--trace` 的版本（`Params p = new Params(); p.trace = true;`），看求解器怎么一步步算出 8。

## 6. 想一想

1. 为什么 Java 要先编译再运行，而不是像 Python 那样直接运行源代码？
2. 把 `VarType.INTEGER` 改成 `VarType.CONTINUOUS`，答案会变成多少？

<details>
<summary>参考答案</summary>

1. 编译时就能发现很多错误（类型不对、拼错名字），运行前就挡住；编译成的字节码可以在任何装了 JVM 的系统上运行（“一次编写，到处运行”）；JVM 运行时还会把常用的代码再编译成机器码（JIT），所以跑得快。
2. 25 / 3 ≈ 8.333。允许买小数个时，钱可以正好花完。

</details>

[目录](../README.md) · 下一课：[数字和小数误差 →](02-numbers.md)
