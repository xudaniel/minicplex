# 入门 A4：重复做事

> **这一课学：** `for` 循环（知道要做几次）；`while` 循环（不知道要做几次）；`++` 和 `+=`
> **大约：** 15 分钟 · **练习：** `java/tutorial/run.sh A04`

[← 做判断](a3-decisions.md) · [目录](../README.md) · 下一课：[自己写方法 →](a5-methods.md)

## 1. for：数着做

把 1 到 10 加起来：

```java
int sum = 0;
for (int i = 1; i <= 10; i++) {
    sum = sum + i;
}
// sum 是 55
```

括号里三段，用分号隔开：

| 部分 | 意思 |
|---|---|
| `int i = 1` | 从 1 开始 |
| `i <= 10` | 只要 i 不超过 10 就继续 |
| `i++` | 每做完一次，i 加 1 |

倒着数也可以：`for (int i = 3; i >= 1; i--)` 依次是 3、2、1。

## 2. while：做到条件不成立为止

每天存 15 元，要存几天才够 100 元？事先不知道要几天，就用 `while`：

```java
int saved = 0, days = 0;
while (saved < 100) {
    saved = saved + 15;
    days++;
}
// days 是 7
```

## 3. 简写

| 简写 | 等于 |
|---|---|
| `i++` | `i = i + 1` |
| `i--` | `i = i - 1` |
| `sum += x` | `sum = sum + x` |

## 4. 常见错误

- **死循环**：`while` 里忘了改变条件（比如忘了 `saved = saved + 15`），程序永远停不下来。按 Ctrl + C 结束。
- **差一个**：`i < 10` 和 `i <= 10` 差了最后一次。数不准时，用很小的数（比如 n = 3）在纸上走一遍。
- 在循环里面写 `int sum = 0;`：每一圈都清零了，要写在循环前面。

## 5. 动手

[`A04Loops.java`](../exercises/minicplex/tutorial/A04Loops.java)：1 加到 n、数偶数、倒数“发射！”、攒钱要几天。

```bash
java/tutorial/run.sh A04
```

## 6. 想一想

minicplex 的单纯形法是一个 `while` 循环，为什么不用 `for`？

<details><summary>答案</summary>

因为事先不知道要换几次基才能到最优解：有的题 2 步，有的题 2000 步。只能“没到最优就继续”。为了防止死循环，代码里还有一个迭代次数上限。

</details>

[← 做判断](a3-decisions.md) · [目录](../README.md) · 下一课：[自己写方法 →](a5-methods.md)
