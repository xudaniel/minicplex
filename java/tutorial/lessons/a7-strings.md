# 入门 A7：字符串

> **这一课学：** 字符串的常用方法；一个个字符地看；`char` 类型；为什么比较文字要用 `equals`
> **大约：** 15 分钟 · **练习：** `java/tutorial/run.sh A07`

[← 数组](a6-arrays.md) · [目录](../README.md) · 下一课：[小项目：挑水果 →](a8-project.md)

## 1. 常用方法

```java
String s = "banana";
s.length()          // 6
s.charAt(0)         // 'b'：第一个字符，下标也从 0 开始
s.toUpperCase()     // "BANANA"
s.contains("nan")   // true
s.equals("banana")  // true
```

注意：数组是 `.length`（没有括号），字符串是 `.length()`（有括号）。

## 2. char：单个字符

单个字符用**单引号**：`'a'`；字符串用**双引号**：`"a"`。两个字符可以用 `==` 比较：

```java
int n = 0;
for (int i = 0; i < s.length(); i++) {
    if (s.charAt(i) == 'a') n++;
}
// "banana" 里 n 是 3
```

`Character.isDigit(ch)` 判断是不是数字，`Character.isLetter(ch)` 判断是不是字母。minicplex 读 `.lp` 模型文件，就是这样一个字符一个字符地扫，分出哪些是数字、哪些是变量名（第 10 课会讲）。

## 3. 比较文字：一定用 equals

```java
String a = "abc";
String b = new String("abc");
a == b          // false！它们是两个不同的对象
a.equals(b)     // true：内容一样
```

`==` 比的是“是不是同一个盒子”，`equals` 比的是“里面的内容一样不一样”。比较文字时，几乎总是想比内容。

## 4. 常见错误

- 用 `==` 比较两个字符串（见上面）。
- `'ab'`：单引号里只能放一个字符。
- 字符串不能改：`s.toUpperCase()` 返回一个新字符串，`s` 本身没变。要写 `s = s.toUpperCase();`。

## 5. 动手

[`A07Strings.java`](../exercises/minicplex/tutorial/A07Strings.java)：变大写加感叹号、名字缩写、数字符、密码里有没有数字、两次密码一样吗。

```bash
java/tutorial/run.sh A07
```

## 6. 想一想

`initials` 里写成 `first.charAt(0) + last.charAt(0) + "."`，`"Daniel", "Xu"` 会得到什么？

<details><summary>答案</summary>

`"156."`。两个 `char` 直接相加，会被当成数字（字符的编码）相加，加完才遇到 `"."` 变成字符串。所以要先放一个字符串在前面：`first.charAt(0) + "." + ...`，后面的 `+` 就都是拼接了。

</details>

[← 数组](a6-arrays.md) · [目录](../README.md) · 下一课：[小项目：挑水果 →](a8-project.md)
