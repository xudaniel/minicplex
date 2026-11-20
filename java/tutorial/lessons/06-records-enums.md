# 第 6 课：record 和 enum

> **这一课学：** `record`（自动生成 equals、hashCode、toString 的数据类）；`enum`（枚举）；带字段的枚举；switch 表达式
> **用到的代码：** [`Var.java`](../../src/main/java/minicplex/Var.java)、[`Status.java`](../../src/main/java/minicplex/Status.java)、[`VarType.java`](../../src/main/java/minicplex/VarType.java)、[`Main.java`](../../src/main/java/minicplex/Main.java)
> **练习：** `java/tutorial/run.sh 06`

[← 封装和不可变对象](05-immutable.md) · [目录](../README.md) · 下一课：[List 和 Map →](07-collections.md)

## 1. record：一行写完一个数据类

minicplex 里最短的文件只有四行：

```java
// Var.java
/** Lightweight handle to a variable inside a {@link Model}: just its index. */
public record Var(int id) {}
```

这一行等于下面这一大段（Java 16 起）：

```java
public final class Var {
    private final int id;
    public Var(int id) { this.id = id; }
    public int id() { return id; }                       // 取值方法叫 id()，不叫 getId()
    public boolean equals(Object o) { return o instanceof Var v && v.id == id; }
    public int hashCode() { return Integer.hashCode(id); }
    public String toString() { return "Var[id=" + id + "]"; }
}
```

record 的字段都是 `final` 的，天生不可变（上一课的好处全都有）。适合“就是一组数据”的类：坐标、区间、一条记录。

- `new Var(3).equals(new Var(3))` 是 `true`：按内容比较。
- 可以放进 `HashMap` 当 key，因为 `hashCode` 也按内容算。
- 可以加自己的方法，也可以在“紧凑构造方法”里检查参数：

```java
record Interval(double lo, double hi) {
    Interval {                                   // 紧凑构造方法：不用写参数列表
        if (lo > hi) throw new IllegalArgumentException("lo > hi");
    }
    double width() { return hi - lo; }
}
```

## 2. enum：只有固定几个取值的类型

变量类型只有三种，用 `enum` 表示：

```java
// VarType.java
public enum VarType { CONTINUOUS, INTEGER, BINARY }
```

为什么不用整数 0、1、2 或者字符串 `"integer"`？

- 写错了编译器直接报错（`VarType.INTERGER` 编不过，`"intergr"` 却能编过）；
- 代码自己说明意思：`type == VarType.BINARY` 比 `type == 2` 清楚得多；
- 可以用 `==` 比较（每个枚举值只有一个对象）。

## 3. 带字段的 enum

求解状态要打印成 `Optimal`、`Infeasible`，和 C++ 版的输出一模一样。于是每个枚举值带一个标签：

```java
// Status.java
public enum Status {
    OPTIMAL("Optimal"),
    INFEASIBLE("Infeasible"),
    UNBOUNDED("Unbounded"),
    INFEASIBLE_OR_UNBOUNDED("InfeasibleOrUnbounded"),
    NODE_LIMIT("NodeLimit"),
    TIME_LIMIT("TimeLimit"),
    ITERATION_LIMIT("IterationLimit");

    private final String label;
    Status(String label) { this.label = label; }
    @Override public String toString() { return label; }
}
```

枚举本质上是一个类，可以有字段、构造方法、方法。`@Override` 表示“这个方法覆盖了父类的同名方法”，写错方法名时编译器会提醒你。

`Status.values()` 返回全部枚举值，`Status.valueOf("OPTIMAL")` 按名字找。

## 4. switch 表达式

命令行解析是一长串“如果参数是 A 就做 X”，minicplex 用 Java 14 起的 switch 写法：

```java
// Main.java
switch (a) {
    case "--relax" -> P.relaxIntegrality = true;
    case "--gap" -> P.mipGap = Double.parseDouble(args[++i]);
    case "--quiet" -> P.verbose = false;
    case "--trace" -> { P.trace = true; P.verbose = false; }   // 多条语句用大括号
    default -> { ... }
}
```

`->` 写法不会“贯穿”到下一个 case（老式 `case X:` 忘写 `break` 是经典 bug）。switch 还能作为**表达式**直接产生一个值：

```java
String text = switch (status) {
    case OPTIMAL -> "找到最优解";
    case INFEASIBLE -> "无解";
    default -> "其他";
};
```

对 enum 做 switch 时，`case` 后面直接写 `OPTIMAL`，不用写 `Status.OPTIMAL`。

## 5. 常见坑

- record 的取值方法是 `id()`，不是 `getId()`，也不是 `.id`（字段是 `private` 的）。
- 枚举值的名字和 `toString()` 可以不一样：`Status.OPTIMAL.name()` 是 `"OPTIMAL"`，`toString()` 是 `"Optimal"`。
- switch 表达式必须覆盖所有情况，否则编译不过，通常加一个 `default`。

## 6. 动手

练习 [`L06RecordsEnums.java`](../exercises/minicplex/tutorial/L06RecordsEnums.java)：给 record 加方法；给 `Grade` 枚举写“分数 → 等级”；用 switch 表达式把 `Status` 翻成中文。

```bash
java/tutorial/run.sh 06
```

## 7. 想一想

1. `Var` 为什么只存一个编号，而不把名字、边界也放进 record？
2. 把 `Status` 的 `toString` 改成返回中文，会影响哪些地方？

<details>
<summary>参考答案</summary>

1. 变量的边界会变（预处理会收紧它们），而 record 是不可变的；名字和边界存在 `Model` 里统一管理，`Var` 只是一个轻量的“把手”。另外两个 `Var` 相等就意味着“同一个变量”，只比编号正好合适。
2. 命令行输出、基准测试写出的 CSV（`tools/compare_java_cpp.py` 要求两边的状态文字完全一样），以及和 C++ 版的逐字对比都会受影响。想显示中文，应该像练习那样另写一个 `describe` 方法，而不是改 `toString`。

</details>

[← 封装和不可变对象](05-immutable.md) · [目录](../README.md) · 下一课：[List 和 Map →](07-collections.md)
