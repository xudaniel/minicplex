# 入门 A1：让程序说话

> **这一课学：** 一个 Java 程序长什么样；打印一行字；字符串和 `+` 拼接；注释
> **大约：** 10 分钟 · **练习：** `java/tutorial/run.sh A01`

[目录](../README.md) · 下一课：[变量和计算 →](a2-variables.md)

## 1. 最小的 Java 程序

```java
public class Hello {
    public static void main(String[] args) {
        System.out.println("Hello, Java!");
    }
}
```

先别管 `public static void` 这些词（A5 会讲），记住三件事就够了：

- 程序从 `main` 开始运行，一行一行往下执行。
- `System.out.println(...)` 打印一行字，`println` 就是 print line（打印一行）。
- 每句话以分号 `;` 结尾，大括号 `{ }` 把一段代码包起来。

## 2. 字符串：用双引号包起来的文字

```java
System.out.println("你好");               // 你好
System.out.println("你好，" + "小明");     // 你好，小明    ← + 把两段文字接起来
System.out.println("苹果：" + 2 + " 元");  // 苹果：2 元    ← 数字也能接上去
```

`//` 后面是**注释**，写给人看的，程序会跳过它。

## 3. 返回一个值

练习里的代码不是直接打印，而是把结果“交回去”（`return`），这样检查程序才能比对你的答案：

```java
static String greet(String name) {
    return "你好，" + name + "！";
}
```

调用 `greet("小明")`，得到的就是 `"你好，小明！"`。`name` 是从外面传进来的名字。

## 4. 常见错误

- 忘了分号，或者引号、括号没配对：编译时就会报错，按报错的行号去找。
- 中文标点：`；` `（` `“` 是中文符号，Java 不认。代码里的符号都要用英文输入法打，文字内容可以是中文。
- 大小写：`system.out.println` 不对，必须是 `System`。

## 5. 动手

打开 [`exercises/minicplex/tutorial/A01Hello.java`](../exercises/minicplex/tutorial/A01Hello.java)。每个方法里有一行：

```java
throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码
```

它的意思是“这里还没写”。把这一行**删掉**，换成你的代码，然后运行：

```bash
java/tutorial/run.sh A01
```

✅ 是对了，❌ 是不对（会告诉你期望什么、实际得到什么），⏳ 是还没写。

## 6. 想一想

`"1" + 2` 和 `1 + 2` 分别是什么？

<details><summary>答案</summary>

`"1" + 2` 是字符串 `"12"`（只要有一边是文字，`+` 就是拼接）；`1 + 2` 是数字 `3`。

</details>

[目录](../README.md) · 下一课：[变量和计算 →](a2-variables.md)
