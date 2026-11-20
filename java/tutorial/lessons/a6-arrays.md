# 入门 A6：数组

> **这一课学：** 用一个变量存一排数；下标从 0 开始；遍历数组；新建数组
> **大约：** 15 分钟 · **练习：** `java/tutorial/run.sh A06`

[← 自己写方法](a5-methods.md) · [目录](../README.md) · 下一课：[字符串 →](a7-strings.md)

## 1. 一排盒子

一周 5 天的步数，与其写 5 个变量，不如放进一个数组：

```java
int[] steps = {4200, 8100, 6500, 12000, 3000};
steps[0]        // 4200：第一个，下标是 0
steps[4]        // 3000：最后一个，下标是 长度 - 1
steps.length    // 5
steps[1] = 9000;   // 改第二个
```

**下标从 0 开始**，这是新手最容易数错的地方。

## 2. 遍历：一个个看过去

```java
int sum = 0;
for (int i = 0; i < steps.length; i++) {   // 注意是 <，不是 <=
    sum += steps[i];
}
```

只要值、不要下标时，有更短的写法：

```java
for (int s : steps) {   // 读作：对 steps 里的每一个 s
    sum += s;
}
```

## 3. 新建一个数组

```java
int[] r = new int[5];   // 5 个格子，一开始都是 0
```

数组建好后**长度不能变**。需要能变长的，用以后学的 `ArrayList`。

## 4. 常见错误

- `i <= a.length`：最后一圈会访问 `a[5]`，程序报 `ArrayIndexOutOfBoundsException`（下标越界）。
- 平均数写成 `sum / a.length`：两个整数相除，又是 A2 的坑。
- `int[] b = a;` 以为复制了一份：其实 `a`、`b` 是同一排盒子，改一个另一个也变。

## 5. 动手

[`A06Arrays.java`](../exercises/minicplex/tutorial/A06Arrays.java)：总和、最大值、数一数超过多少的有几天、平均数、倒过来。

```bash
java/tutorial/run.sh A06
```

## 6. 想一想

minicplex 里每个变量的下界存在一个数组 `lb` 里，上界存在 `ub` 里。第 3 个变量的上界怎么取？

<details><summary>答案</summary>

`ub[2]`。第 3 个，下标是 2。

</details>

[← 自己写方法](a5-methods.md) · [目录](../README.md) · 下一课：[字符串 →](a7-strings.md)
