# 第 9 课：异常

> **这一课学：** `throw`、`try / catch / finally`；受检异常和非受检异常；try-with-resources；什么时候该抛、什么时候该接
> **用到的代码：** [`LpReader.java`](../../src/main/java/minicplex/LpReader.java)、[`Model.java`](../../src/main/java/minicplex/Model.java) 的参数检查、[`Main.java`](../../src/main/java/minicplex/Main.java) 的最外层兜底
> **练习：** `java/tutorial/run.sh 09`

[← lambda、比较器和优先队列](08-comparators.md) · [目录](../README.md) · 下一课：[字符串和文本处理 →](10-strings.md)

## 1. 出错了，就抛出去

用户建模时用了一个重复的变量名，`addVar` 不能假装没看见，也不知道该怎么补救，那就**抛出异常**，让调用者知道：

```java
// Model.java
if (index.containsKey(name)) throw new IllegalArgumentException("duplicate variable name: " + name);
```

异常一抛出，当前方法立刻结束，异常沿着调用链一层层往上传，直到某一层用 `try / catch` 接住它；一直没人接，程序就终止并打印出错位置。

Java 标准库里常用的几种：

| 异常 | 什么时候用 |
|---|---|
| `IllegalArgumentException` | 参数不合法（重复的名字、负的长度） |
| `IllegalStateException` | 对象当前的状态不允许这个操作 |
| `NullPointerException` | 用了 `null` |
| `NumberFormatException` | `Integer.parseInt("abc")` 这类转换失败 |
| `UnsupportedOperationException` | 不支持的操作（比如修改只读集合） |

## 2. 报错要说清楚“哪里错了”

读 LP 文件出错时，minicplex 会告诉你是第几行：

```java
// LpReader.java
private RuntimeException fail(String msg) {
    throw new RuntimeException("LP parse error (line " + peek(0).line + "): " + msg);
}
...
case "semi", "semis", "sos" -> throw fail("section '" + a.s + "' is not supported by minicplex");
```

```text
$ cat broken.lp
Minimize
 obj: x +
Subject To
 c: x >= 1
End
$ java -jar java/build/minicplex.jar broken.lp
error: LP parse error (line 3): dangling sign
```

`dangling sign` 的意思是“悬空的符号”：加号后面没有东西。好的错误信息包含三样东西：**哪里**（第几行）、**什么**（出了什么问题）、最好再有**怎么办**（期望的是什么）。

## 3. 接住异常：try / catch

命令行程序的最外层要把所有错误接住，打印一行友好的信息，而不是甩给用户一大串调用栈：

```java
// Main.java
try {
    Model M = LpReader.readFile(path);
    ...
    Result R = Solver.solve(M, P);
    ...
} catch (RuntimeException | IOException e) {     // 一个 catch 可以接住好几种
    System.err.println("error: " + e.getMessage());
    return 2;                                     // 返回非 0 的退出码，脚本能知道出错了
}
```

`System.err` 是“错误输出”，和正常输出 `System.out` 分开，用户重定向输出到文件时，错误信息仍然显示在屏幕上。

## 4. 受检异常和非受检异常

Java 的异常分两类：

- **非受检异常**（`RuntimeException` 及其子类）：通常是程序的 bug 或参数错误，编译器不强制处理。
- **受检异常**（如 `IOException`）：外部环境出问题（文件不存在、网络断了），编译器**强制**你要么 `catch`，要么在方法上声明 `throws IOException`，把责任交给调用者。

`LpReader.readFile` 选择把受检异常包成非受检异常再抛出，这样调用者不用到处写 `throws`：

```java
// LpReader.java
public static Model readFile(String path) {
    try {
        return readString(Files.readString(Path.of(path), StandardCharsets.UTF_8));
    } catch (IOException e) {
        throw new RuntimeException("cannot open file: " + path);
    }
}
```

标准库专门为此提供了 `UncheckedIOException`，包装时最好把原来的异常传进去（`new UncheckedIOException(e)`），排查时能看到根本原因。

## 5. try-with-resources：保证资源被关闭

文件、网络连接用完必须关闭，即使中途出了异常也要关。`try (...)` 括号里打开的资源，离开 try 块时会自动关闭：

```java
// Main.java
try (FileWriter w = new FileWriter(writePath)) {
    M.writeLP(w);
}   // 不管 writeLP 成功还是抛异常，w 都会被关闭
```

在它出现之前，要写 `finally { w.close(); }`，还要处理 `close` 本身抛异常的情况，很啰嗦。

## 6. 常见坑

- **吞掉异常**：`catch (Exception e) {}` 什么都不做，出了错也不知道。至少要打印或者重新抛出。
- **接得太宽**：`catch (Exception e)` 会把 bug（比如 `NullPointerException`）也接住，当成“正常的失败”处理。尽量接具体的类型。
- **用异常控制正常流程**：异常比较慢，也让代码难读。“找不到变量”是正常情况，所以 `findVar` 返回 −1，而不是抛异常；而 `var(name)` 明确要求变量必须存在，找不到才抛。

## 7. 动手

练习 [`L09Exceptions.java`](../exercises/minicplex/tutorial/L09Exceptions.java)：

1. `parseOr`：转换失败时返回默认值；
2. `errorLine`：接住 `LpReader` 的异常，从错误信息里取出行号（用到正则表达式）；
3. `firstLine`：用 try-with-resources 读文件，把 `IOException` 包装成 `UncheckedIOException`。

```bash
java/tutorial/run.sh 09
```

## 8. 想一想

1. `findVar` 找不到返回 −1，`var` 找不到就抛异常。为什么要提供两个？
2. 练习里，模型第 2 行多了一个 `+`，为什么报错说的是第 3 行？

<details>
<summary>参考答案</summary>

1. 调用者的意图不同：“看看有没有这个变量”时，找不到是正常结果，用 `findVar`；“我知道它一定在，给我”时，找不到说明程序有 bug，应该立刻停下来，用 `var`。
2. 读到行末的 `+` 时还不算错，后面可能还有一项。直到读到下一行的 `Subject To`，才发现 `+` 后面没有东西。很多编译器报错的行号也是这样，“发现错误的地方”比“犯错的地方”晚一点。

</details>

[← lambda、比较器和优先队列](08-comparators.md) · [目录](../README.md) · 下一课：[字符串和文本处理 →](10-strings.md)
