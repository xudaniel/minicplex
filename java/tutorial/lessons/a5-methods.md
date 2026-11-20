# 入门 A5：自己写方法

> **这一课学：** 方法是“有名字的一段代码”；参数和返回值；方法调用方法
> **大约：** 15 分钟 · **练习：** `java/tutorial/run.sh A05`

[← 重复做事](a4-loops.md) · [目录](../README.md) · 下一课：[数组 →](a6-arrays.md)

## 1. 方法长什么样

```java
static int max(int a, int b) {
    if (a > b) return a;
    return b;
}
```

| 部分 | 意思 |
|---|---|
| `static` | 先照写，第 4 课讲它是什么意思 |
| `int`（前面那个） | 返回值的类型：这个方法交回一个整数 |
| `max` | 方法的名字 |
| `(int a, int b)` | 参数：调用时要给它两个整数 |
| `return a;` | 把结果交回去，方法到这里就结束了 |

调用：`max(3, 9)` 得到 `9`。

不返回任何东西的方法，类型写 `void`，比如 `main`。

## 2. 为什么要写方法

**写一次，到处用。** 有了 `max`，求三个数的最大值就不用再写一遍比较：

```java
static int maxOfThree(int a, int b, int c) {
    return max(max(a, b), c);
}
```

好的方法名本身就是说明：读到 `clamp(v, lo, hi)`，就知道“把 v 夹在 lo 和 hi 之间”。minicplex 里每个变量都有下界和上界，求解器里到处是这种“别越界”的小方法。

## 3. 常见错误

- 声明了返回 `int`，却有一条路径没有 `return`：编译器会报 *missing return statement*。
- 参数顺序弄反：`clamp(v, lo, hi)` 写成 `clamp(lo, hi, v)`，编译能过，结果却是错的。所以参数名要起得清楚。
- 在方法里改了参数，以为外面的变量也变了：不会，方法拿到的是一份副本。

## 4. 动手

[`A05Methods.java`](../exercises/minicplex/tutorial/A05Methods.java)：面积、两个数和三个数的最大值、摄氏转华氏、`clamp`。

```bash
java/tutorial/run.sh A05
```

## 5. 想一想

`fahrenheit` 里写成 `celsius * (9 / 5) + 32`，100 度会算成多少？为什么？

<details><summary>答案</summary>

132。`9 / 5` 是整数除法，结果是 1，变成了 `100 * 1 + 32`。A2 的坑又出现了。写成 `celsius * 9 / 5` 就对了：`celsius` 是 `double`，从左往右算时一直是小数。

</details>

[← 重复做事](a4-loops.md) · [目录](../README.md) · 下一课：[数组 →](a6-arrays.md)
