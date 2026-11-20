# 第 4 课：类和对象

> **这一课学：** 类、字段、构造方法、`this`、方法重载、复制构造方法、`static`
> **用到的代码：** [`VarInfo.java`](../../src/main/java/minicplex/VarInfo.java)、[`Model.java`](../../src/main/java/minicplex/Model.java) 的 `addVar`、[`LinExpr.java`](../../src/main/java/minicplex/LinExpr.java) 的静态工厂方法
> **练习：** `java/tutorial/run.sh 04`

[← 数组和循环](03-arrays.md) · [目录](../README.md) · 下一课：[封装和不可变对象 →](05-immutable.md)

## 1. 类是图纸，对象是照图纸造出来的东西

`VarInfo` 描述“一个变量的信息”：名字、上下界、类型。

```java
// VarInfo.java
public final class VarInfo {
    public String name;
    public double lb;
    public double ub;
    public VarType type;

    public VarInfo(String name, double lb, double ub, VarType type) {
        this.name = name;
        this.lb = lb;
        this.ub = ub;
        this.type = type;
    }

    public VarInfo(VarInfo o) { this(o.name, o.lb, o.ub, o.type); }
}
```

- **字段**（`name`、`lb`……）：每个对象自己的数据。
- **构造方法**：名字和类名一样、没有返回类型，`new VarInfo(...)` 时执行，负责把对象“装配好”。
- **`this.name = name`**：参数也叫 `name`，用 `this.name` 指“这个对象的字段”，把两者区分开。
- `final class`：不允许别人继承这个类（minicplex 的类几乎都是 `final`，不打算被继承就明说）。

每次 `new` 都造出一个新对象，各有各的字段：

```java
VarInfo a = new VarInfo("cake", 0, 10, VarType.INTEGER);
VarInfo b = new VarInfo("bread", 0, 5, VarType.INTEGER);
a.ub = 20;    // 只改 a，b 不受影响
```

## 2. 复制构造方法和 this(...)

第二个构造方法 `VarInfo(VarInfo o)` 造出一个和 `o` 一模一样的新对象。它用 `this(...)` 调用第一个构造方法，避免把四行赋值再写一遍。`this(...)` 必须写在构造方法的第一行。

`Model` 的复制构造方法就靠它做“深复制”（第 5 课细讲）：

```java
// Model.java
for (VarInfo v : o.vars) vars.add(new VarInfo(v));
```

## 3. 方法重载：同名、不同参数

建变量有好几种写法，都叫 `addVar`：

```java
// Model.java
public Var addVar(double lb, double ub, VarType type, String name) { ... 真正干活的版本 ... }
public Var addVar(double lb, double ub, VarType type) { return addVar(lb, ub, type, ""); }
public Var addVar(double lb, double ub) { return addVar(lb, ub, VarType.CONTINUOUS, ""); }
public Var addVar() { return addVar(0.0, INF, VarType.CONTINUOUS, ""); }
```

Java 根据参数的个数和类型决定调用哪一个，这叫**重载**。好的重载都像这样：只有一个版本真正干活，其余的补上默认值后转过去。以后要改逻辑，只改一处。

## 4. static：属于类，不属于某个对象

```java
public static final double INF = Double.POSITIVE_INFINITY;   // Model.INF：全体共用一个常量
public static LinExpr of(double coef, Var v) { ... }          // LinExpr.of(2, x)：不需要先有一个 LinExpr 对象
public static Result solve(Model M) { ... }                   // Solver.solve(m)
```

`static` 方法通过类名调用。`LinExpr.of(...)` 这种“用静态方法造对象”的写法叫**静态工厂方法**，比 `new` 好在可以起一个说明意图的名字（`of`、`constant`）。

`Solver` 只有静态方法，所以它的构造方法是 `private` 的，谁也 `new` 不出 `Solver` 对象：这是“工具类”的惯用写法。

## 5. 方法里的 return 和参数

```java
public Var addVar(double lb, double ub, VarType type, String name) {
    if (type == VarType.BINARY) {           // 0-1 变量：边界强制收到 [0, 1]
        lb = Math.max(lb, 0.0);
        ub = Math.min(ub, 1.0);
    }
    if (name == null || name.isEmpty()) name = "x" + (vars.size() + 1);   // 没给名字就自动起一个
    ...
    return new Var(vars.size() - 1);
}
```

参数在方法里可以修改（`lb = ...`），但改的是方法自己的副本，不影响调用者传进来的变量。Java 的参数传递永远是**值传递**；对象参数传的是“对象的引用”的副本，所以通过它修改对象的字段，调用者能看到。

## 6. 常见坑

- **忘了 `this.`**：构造方法里写成 `name = name;`，只是把参数赋给参数自己，字段还是 `null`。
- **`==` 比较对象**：`a == b` 比的是“是不是同一个对象”，比内容要用 `equals`（下一课和第 6 课都会用到）。
- **字符串判空**：`name.isEmpty()` 在 `name` 为 `null` 时会抛 `NullPointerException`，所以 `addVar` 先判断 `name == null`，`||` 短路求值保证了后半句不会执行。

## 7. 动手

练习 [`L04Classes.java`](../exercises/minicplex/tutorial/L04Classes.java)：仿照 `VarInfo` 写一个商品类 `Item`，包括三个构造方法（完整版、省略重量、复制）、一个计算性价比的方法，以及一个找最高性价比的静态方法。

```bash
java/tutorial/run.sh 04
```

## 8. 想一想

1. `VarInfo` 的字段都是 `public` 的，`Item` 的字段是 `private` 的。各有什么好处？
2. 为什么 `addVar` 返回一个 `Var`，而不是直接返回 `VarInfo`？

<details>
<summary>参考答案</summary>

1. `public` 字段写起来省事，`Model` 内部和测试可以直接读写（求解器内部用得很频繁）；`private` 字段加上取值方法，外面只能看不能改，对象的状态由类自己掌控，更安全。公开 API 一般用后者，下一课专门讲。
2. `Var` 只是一个编号，很小，传来传去很便宜；它也不暴露内部数据，用户拿着 `Var` 改不了变量的边界。真正的信息存在 `Model` 里，需要时用编号去查。这和数据库里用“主键”引用一行数据是一个道理。

</details>

[← 数组和循环](03-arrays.md) · [目录](../README.md) · 下一课：[封装和不可变对象 →](05-immutable.md)
