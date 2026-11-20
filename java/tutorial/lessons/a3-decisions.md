# 入门 A3：做判断

> **这一课学：** `if / else if / else`；比较大小；`&&`（并且）和 `||`（或者）；比较文字用 `equals`
> **大约：** 15 分钟 · **练习：** `java/tutorial/run.sh A03`

[← 变量和计算](a2-variables.md) · [目录](../README.md) · 下一课：[重复做事 →](a4-loops.md)

## 1. 如果……就……否则……

```java
if (temp < 10) {
    return "冷";
} else if (temp < 25) {
    return "舒服";
} else {
    return "热";
}
```

从上往下检查，第一个成立的条件被执行，后面的就跳过了。所以 18 度会走第二条，不会走第三条。

## 2. 比较

| 写法 | 意思 |
|---|---|
| `a > b` `a < b` | 大于、小于 |
| `a >= b` `a <= b` | 大于等于、小于等于 |
| `a == b` | 等于（两个等号！） |
| `a != b` | 不等于 |

比较的结果是 `boolean`：`true` 或 `false`。所以“钱够不够”可以直接写成：

```java
return money >= cost;
```

## 3. 并且、或者、不是

```java
total >= 99 && isMember     // 并且：两个都成立
day.equals("Sat") || day.equals("Sun")   // 或者：有一个成立就行
!canAfford(5, 8)            // 不是：把 true 变 false
```

## 4. 比较文字用 equals

```java
day.equals("Sat")    // ✓ 比较内容
day == "Sat"         // ✗ 比较的是“是不是同一个对象”，有时对有时错
```

这是 Java 新手最常踩的坑之一，A7 还会再遇到。

## 5. 常见错误

- `if (x = 5)`：少写一个等号，变成了赋值，编译报错。
- 条件顺序写反：先写 `temp < 25` 再写 `temp < 10`，3 度会被判成“舒服”。
- `if (...) ;` 后面多了个分号，大括号里的代码每次都会执行。

## 6. 动手

[`A03Decisions.java`](../exercises/minicplex/tutorial/A03Decisions.java)：钱够不够、天气建议、满 99 包邮、是不是周末。

```bash
java/tutorial/run.sh A03
```

## 7. 想一想

minicplex 求解时，每一步都要判断一个变量“有没有超出边界”。你觉得这个判断长什么样？

<details><summary>答案</summary>

大致是 `if (x[j] < lb[j] || x[j] > ub[j])`：比下界小**或者**比上界大，就是越界。真实代码还允许一点点误差（第 2 课会讲为什么）。

</details>

[← 变量和计算](a2-variables.md) · [目录](../README.md) · 下一课：[重复做事 →](a4-loops.md)
