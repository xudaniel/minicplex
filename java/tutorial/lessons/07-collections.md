# 第 7 课：List 和 Map

> **这一课学：** `ArrayList`、`HashMap`、`TreeMap`；泛型 `<...>`；遍历；`merge`；为什么有时一定要用 `TreeMap`
> **用到的代码：** [`Model.java`](../../src/main/java/minicplex/Model.java) 的变量列表和名字索引、[`LinExpr.java`](../../src/main/java/minicplex/LinExpr.java)、[`Constraint.java`](../../src/main/java/minicplex/Constraint.java)
> **练习：** `java/tutorial/run.sh 07`

[← record 和 enum](06-records-enums.md) · [目录](../README.md) · 下一课：[lambda、比较器和优先队列 →](08-comparators.md)

## 1. List：能变长的数组

模型里有多少变量，事先不知道，数组不合适（长度固定），所以用 `List`：

```java
// Model.java
public final List<VarInfo> vars = new ArrayList<>();
public final List<Constraint> constraints = new ArrayList<>();
```

- `List<VarInfo>`：尖括号里写元素类型，这叫**泛型**。放错类型，编译器就报错。
- 左边写接口 `List`，右边写具体实现 `ArrayList`：以后换实现，只改右边。
- `<>` 里的类型可以省略，编译器从左边推出来。

常用操作：

```java
vars.add(new VarInfo(...));   // 加到末尾
vars.get(j)                   // 第 j 个
vars.size()                   // 有几个
for (VarInfo v : vars) { }    // 遍历
List.of("甲", "乙")           // 造一个不可修改的小列表
```

> 泛型里不能直接放 `int`、`double` 这些基本类型，要写包装类 `Integer`、`Double`：`List<Double>`。
> Java 会自动在 `double` 和 `Double` 之间转换（自动装箱 / 拆箱）。

## 2. HashMap：按名字找编号

LP 文件里的变量用名字表示（`cake`、`bread`），读文件时要能快速知道“`cake` 是第几个变量”。`Model` 里有一张“名字 → 编号”的表：

```java
// Model.java
private final Map<String, Integer> index = new HashMap<>();

public Var addVar(double lb, double ub, VarType type, String name) {
    ...
    if (index.containsKey(name)) throw new IllegalArgumentException("duplicate variable name: " + name);
    index.put(name, vars.size());
    ...
}

public int findVar(String name) {
    Integer j = index.get(name);       // 找不到返回 null
    return j == null ? -1 : j;
}
```

`HashMap` 查找几乎不随数据量变慢：一万个变量和十个变量，查一次都很快。如果改成在 `vars` 列表里一个个比名字，一万个变量的模型读起来会慢很多。

## 3. TreeMap：按 key 排好序的 Map

表达式 `3 x + 2 y` 存成“变量编号 → 系数”：

```java
// LinExpr.java
final TreeMap<Integer, Double> terms = new TreeMap<>();
```

为什么这里用 `TreeMap` 而不用 `HashMap`？`TreeMap` 遍历时**永远按 key 从小到大**，`HashMap` 的遍历顺序则没有保证。这对 minicplex 很重要：

- 写出的 `.lp` 文件里，项的顺序要固定，每次输出一模一样；
- C++ 版用的 `std::map` 也是按 key 排序的，Java 版用 `TreeMap`，两边按同样的顺序做加法，浮点误差才完全相同（第 8 课会讲为什么这很重要）。

**规则：** 只要结果依赖遍历顺序（输出、累加小数），就用有序的容器，`TreeMap` 或 `LinkedHashMap`（按插入顺序）。

## 4. merge：合并同类项

`2x + 5x` 应该合成 `7x`。`plus` 里只有一行：

```java
// LinExpr.java
e.terms.merge(v.id(), coef, Double::sum);
```

`merge(key, value, 合并函数)` 的意思是：key 不在表里，就放进去；已经在了，就用合并函数把旧值和新值合起来。`Double::sum` 是“两个 double 相加”这个函数的写法（方法引用，下一课细讲）。

遍历 Map 时，用 `entrySet()` 同时拿到 key 和 value：

```java
// Constraint.java
for (Map.Entry<Integer, Double> t : d.terms.entrySet())
    if (t.getValue() != 0.0) c.coefs.put(t.getKey(), t.getValue());   // 系数是 0 的项不要
```

## 5. 常见坑

- `map.get(key)` 找不到时返回 `null`，直接当 `int` 用会抛 `NullPointerException`。`findVar` 就是先判断 `null` 再拆箱。
- 一边遍历一边删除元素会抛 `ConcurrentModificationException`。要删，用 `removeIf` 或迭代器的 `remove()`。
- `List.of(...)`、`Map.of(...)` 造出来的集合不能修改，`add` 会抛异常。
- `HashMap` 的遍历顺序看起来“好像固定”，但不同 Java 版本、不同数据下可能变，不能依赖。

## 6. 动手

练习 [`L07Collections.java`](../exercises/minicplex/tutorial/L07Collections.java)：

1. `buildIndex`：名字 → 编号，重名就报错（和 `Model.addVar` 一样）；
2. `mergeTerms`：用 `merge` 合并同类项，再用 `removeIf` 去掉 0；
3. `nonzeroNames`：求解后列出取值不为 0 的变量。

```bash
java/tutorial/run.sh 07
```

## 7. 想一想

1. `Model` 里 `vars` 和 `index` 存的信息有重复，为什么两个都要？
2. 如果 `LinExpr` 用 `HashMap`，Java 版和 C++ 版的结果可能出现什么差别？

<details>
<summary>参考答案</summary>

1. 两个用途不同：`vars` 按编号顺序存所有信息，求解器按编号访问；`index` 只用来“按名字找编号”。用一点额外内存换来两种查询都快，这是很常见的取舍。代价是两者必须保持一致，所以只能通过 `addVar` 一个入口添加变量。
2. 系数加起来的顺序不同，小数的最后一位可能不同；单纯形法在“平局”时就可能选不同的变量，走上另一条路，最后节点数、迭代次数都不一样（最优值通常相同）。写出的 LP 文件里项的顺序也可能不同。

</details>

[← record 和 enum](06-records-enums.md) · [目录](../README.md) · 下一课：[lambda、比较器和优先队列 →](08-comparators.md)
