# 第 5 课：封装和不可变对象

> **这一课学：** `private` 和 `final`；为什么要“不可变”；引用和别名；浅复制和深复制；只读视图
> **用到的代码：** [`LinExpr.java`](../../src/main/java/minicplex/LinExpr.java)、[`Model.java`](../../src/main/java/minicplex/Model.java) 的复制构造方法、[`Solver.java`](../../src/main/java/minicplex/Solver.java) 的 `clone()`
> **练习：** `java/tutorial/run.sh 05`

[← 类和对象](04-classes.md) · [目录](../README.md) · 下一课：[record 和 enum →](06-records-enums.md)

## 1. 一个会出事的场景

假设 `LinExpr` 是“可变”的，`plus` 直接改自己：

```java
LinExpr cost = LinExpr.of(5, cake);
LinExpr withBread = cost.plus(4, bread);   // 想要一个新表达式 5 cake + 4 bread
m.setObjective(cost, ObjSense.MAXIMIZE);   // 本来想用 5 cake 当目标……
```

如果 `plus` 改的是 `cost` 本身，那 `cost` 已经悄悄变成了 `5 cake + 4 bread`，目标就错了，而且这种错很难发现。

minicplex 的做法是：**表达式一旦造出来就再也不变**，每次运算都返回一个新对象。

```java
// LinExpr.java
private LinExpr copy() {
    LinExpr e = new LinExpr();
    e.terms.putAll(terms);
    e.constant = constant;
    return e;
}

public LinExpr plus(double coef, Var v) {
    LinExpr e = copy();                         // 先复制
    e.terms.merge(v.id(), coef, Double::sum);   // 只改副本
    return e;                                   // 返回副本，原来的不动
}
```

代价是：循环里累加时要写 `e = e.plus(...)`，把新对象接住。忘了接住的话，结果就丢了：

```java
LinExpr total = new LinExpr();
for (Var v : vars) total.plus(v);       // ✗ 每次的新对象都被扔掉了，total 还是空的
for (Var v : vars) total = total.plus(v);   // ✓
```

Java 自己的 `String` 也是这样设计的：`s.toUpperCase()` 不改 `s`，而是返回新字符串。

## 2. 变量里存的是“引用”

对象变量存的不是对象本身，而是指向对象的“地址”。两个变量可以指向同一个对象，这叫**别名**：

```java
double[] a = {1, 2};
double[] b = a;        // b 和 a 指向同一个数组
b[0] = 99;             // a[0] 也变成 99 了
double[] c = a.clone();// c 是一个新数组，内容一样
c[0] = 7;              // a 不受影响
```

分支定界每分一次，就要给新节点一份**自己的**边界数组，所以用 `clone()`：

```java
// Solver.java
Node sib = new Node(cur.lb.clone(), cur.ub.clone(), nodeBound, cur.depth + 1, E.basis());
if (goUp) sib.ub[bj] = fl; else sib.lb[bj] = ce;    // 只改兄弟节点的边界，不影响当前节点
```

如果忘了 `clone()`，两个节点共享一个数组，改一个另一个也跟着变，搜索树就乱了。

## 3. 浅复制和深复制

`Model` 里有一个变量列表、一个约束列表，每个元素又是对象。复制一个模型时：

- **浅复制**：只复制列表，列表里装的还是原来那些对象；改副本里的约束，原模型也跟着改。
- **深复制**：列表要新的，列表里的每个对象也要新的。

```java
// Model.java：深复制
public Model(Model o) {
    for (VarInfo v : o.vars) vars.add(new VarInfo(v));                    // 每个变量复制一份
    for (Constraint c : o.constraints) constraints.add(new Constraint(c));// 每条约束复制一份
    objective = o.objective.plus(0.0);                                     // LinExpr 不可变，加 0 得到一个新对象
    ...
}
```

求解器内部会修改模型（预处理收紧系数、加割平面），所以它先深复制一份再动手，用户手里的模型保持原样。测试里也是这样用的：复制一份模型，把某条约束的右边改大一点，看最优值变多少。

## 4. 封装：private、final 和只读视图

- `private`：只有类自己能访问。外面想改，只能通过类提供的方法，类就能保证数据始终合法。
- `final` 字段：赋值一次后不能再指向别的对象（但对象本身的内容还是可能被改）。

`LinExpr` 的内部数据是一个 `TreeMap`，外面有时需要读它（比如打印）。如果直接把这个 map 交出去，外面就能改它，前面的“不可变”就破功了。所以只交出一个**只读视图**：

```java
// LinExpr.java
/** Read-only view of the terms (variable id → coefficient); modifying it throws. */
public Map<Integer, Double> terms() { return Collections.unmodifiableMap(terms); }
```

只读视图不复制数据（很便宜），但任何修改都会抛 `UnsupportedOperationException`。

> **这里有个真实的小故事：** 写这一课时我们发现，`terms()` 原来是直接 `return terms;`，外面可以改到 `LinExpr` 的内部数据。于是把它改成了只读视图。读真实项目的代码，就会遇到这种“教科书里说不能这样，但项目里确实这样写了”的地方。

## 5. 常见坑

- 不可变类返回新对象，**一定要接住返回值**。
- `final` 不等于不可变：`final List<X> list` 不能指向别的列表，但 `list.add(...)` 照样能加东西。
- 只读视图只挡住“通过这个视图修改”；如果原 map 被类自己改了，视图里也能看到变化。

## 6. 动手

练习 [`L05Immutable.java`](../exercises/minicplex/tutorial/L05Immutable.java)：

1. 写一个不可变的 `Expr`：`plus` 返回新对象，`terms()` 返回只读视图；
2. 写 `deepCopy`，并看测试里浅复制是怎么出事的。

```bash
java/tutorial/run.sh 05
```

## 7. 想一想

1. 不可变对象每次都复制，会不会很慢？minicplex 为什么还是这样做？
2. `Result` 的字段都是 `public` 的、可以改的，这样设计合理吗？

<details>
<summary>参考答案</summary>

1. 建模时每个表达式的项不多，复制很便宜；求解时根本不用 `LinExpr`，而是把模型转成数组（`LPEngine`）。花一点建模时的复制，换来“绝不会被意外修改”的安全，很划算。
2. `Result` 是求解器交给用户的“结果包”，用户拿到后改不改都不影响求解器，所以简单起见用公开字段。它和 `LinExpr` 不同：`LinExpr` 会被多个地方共享（同一个表达式可以用在好几条约束里），共享的东西才必须不可变。

</details>

[← 类和对象](04-classes.md) · [目录](../README.md) · 下一课：[record 和 enum →](06-records-enums.md)
