# 第 10 课：字符串和文本处理

> **这一课学：** `String` 是不可变的；`charAt`、`substring`；`StringBuilder`；`String.format` 和 `Locale`；手写一个词法分析器
> **用到的代码：** [`LpReader.java`](../../src/main/java/minicplex/LpReader.java) 的 `tokenize`、[`Model.java`](../../src/main/java/minicplex/Model.java) 的 `toLP`、[`Fmt.java`](../../src/main/java/minicplex/Fmt.java)、[`Main.java`](../../src/main/java/minicplex/Main.java)
> **练习：** `java/tutorial/run.sh 10`

[← 异常](09-exceptions.md) · [目录](../README.md) · 下一课：[包、访问控制和测试 →](11-testing.md)

## 1. 字符串是不可变的

和第 5 课的 `LinExpr` 一样，`String` 一旦造出来就不会变。`s.trim()`、`s.toLowerCase()` 都返回新字符串：

```java
String s = "  Maximize ";
s.trim();              // ✗ 结果被扔掉了，s 还是原样
s = s.trim();          // ✓
```

比较内容用 `equals`，不要用 `==`：

```java
a.equals("--relax")                // 比内容
"--relax".equals(a)                // a 可能是 null 时这样写更安全
a.equalsIgnoreCase("MAXIMIZE")     // 不分大小写
```

## 2. 一个字符一个字符地扫：词法分析

读 LP 文件的第一步，是把 `flour: 6 cake + 4 bread <= 24` 切成一个个“词”（记号）：`flour`、`:`、`6`、`cake`、`+`……这一步叫**词法分析**。minicplex 用一个下标 `i` 从左往右扫：

```java
// LpReader.java（简化）
int i = 0;
while (i < n) {
    final char c = src.charAt(i);                         // 第 i 个字符
    if (Character.isWhitespace(c)) { ++i; continue; }     // 空白：跳过
    if (c == '\\') { while (i < n && src.charAt(i) != '\n') ++i; continue; }   // 反斜杠：注释到行尾
    if (isDigit(src, i) || (c == '.' && isDigit(src, i + 1))) {               // 数字
        int j = i;
        while (isDigit(src, j)) ++j;
        if (j < n && src.charAt(j) == '.') { ++j; while (isDigit(src, j)) ++j; }
        ...
        t.s = src.substring(i, j);                         // 截出 [i, j) 这一段
        t.num = Double.parseDouble(t.s);
        i = j;
    } else if (c == '<' || c == '>' || c == '=') { ... }  // 比较符
    ...
}
```

几个要点：

- `char` 是单个字符，用单引号：`'\n'`。`String` 用双引号。
- `substring(i, j)` 包含 i、不包含 j。
- 为什么手工扫数字，不直接交给库函数去试？库函数会接受一些 LP 格式里不该是数字的写法：C++ 的 `strtod` 接受 `0x1` 这样的十六进制（源代码注释里写着这个原因），Java 的 `Double.parseDouble` 接受 `NaN`、`Infinity`、`1f`。自己扫，规则完全掌控在自己手里，扫出来的那一段再交给 `parseDouble` 转换就安全了。

## 3. 拼字符串：StringBuilder

用 `+` 在循环里拼字符串，每拼一次都会造一个新字符串，很慢。要拼很多次时用 `StringBuilder`：

```java
// LpReader.java
StringBuilder op = new StringBuilder().append(c);
if (i + 1 < n && "<>=".indexOf(src.charAt(i + 1)) >= 0) op.append(src.charAt(++i));
String o = op.toString();
```

`Model.toLP()` 写出整个模型文件时也是用 `StringBuilder` 一段段 `append` 上去的。

## 4. 格式化输出：String.format 和 Locale

命令行打印结果表：

```java
// Main.java
System.out.println(String.format(Locale.ROOT, "%-20s %16s", M.vars.get(j).name, Fmt.g(v, 10)));
System.out.println(String.format(Locale.ROOT, "Nodes:        %d\nIterations:   %d\nTime:         %.3f s",
        R.nodes, R.lpIterations, R.seconds));
```

| 格式 | 意思 |
|---|---|
| `%d` | 整数 |
| `%.3f` | 小数，保留 3 位 |
| `%s` | 字符串 |
| `%-20s` | 字符串，占 20 格，左对齐（不写 `-` 就是右对齐） |
| `%16s` | 占 16 格，右对齐 |
| `%%` | 一个百分号 |

**为什么要写 `Locale.ROOT`？** 在德语、法语等系统上，`String.format("%.2f", 3.5)` 会输出 `3,50`（逗号当小数点）。写出的 LP 文件里一旦出现 `3,50`，就读不回来了。所以 minicplex 所有格式化都固定用 `Locale.ROOT`。同理，转小写用 `toLowerCase(Locale.ROOT)`（土耳其语里 `I` 的小写不是 `i`）。

## 5. 让 Java 打印出和 C 一模一样的数字

C/C++ 的 `printf("%g")` 有自己的规则（6 位有效数字、去掉末尾的 0、太大太小时用科学计数法），Java 没有完全相同的格式。为了让 Java 版的输出和 C++ 版逐字相同，minicplex 自己写了一个 `Fmt.g`：

```java
// Fmt.java（节选）
public static String g(double v, int precision) {
    if (Double.isNaN(v)) return "nan";
    if (Double.isInfinite(v)) return v > 0 ? "inf" : "-inf";
    ...
    BigDecimal bd = new BigDecimal(v).round(new MathContext(precision, RoundingMode.HALF_EVEN));
    ...
}
```

`BigDecimal` 能精确表示十进制小数，用来做“按有效数字四舍五入”这类事最稳妥。

## 6. 常见坑

- **中文的显示宽度**：`%-8s` 按“字符个数”占位，但一个汉字在终端里占两格，中英文混排的表格会对不齐（第 12 课的选课表就能看到）。
- **`split` 的参数是正则表达式**：`"a.b".split(".")` 得到空数组，因为 `.` 在正则里表示“任意字符”。要写 `split("\\.")`；按空白切用 `split("\\s+")`。
- **编码**：读写文件时明确写 `StandardCharsets.UTF_8`，不要依赖系统默认编码。

## 7. 动手

练习 [`L10Strings.java`](../exercises/minicplex/tutorial/L10Strings.java)：

1. `tokenize`：迷你词法分析器，把 `3x+2.5y<=10` 切成 7 个记号；
2. `row`：用 `String.format` 排一行表格；
3. `lpLine`：用 `StringBuilder` 把一条约束写成 LP 格式。

```bash
java/tutorial/run.sh 10
```

## 8. 想一想

1. 词法分析器遇到 `x1` 时，怎么知道它是一个名字，而不是名字 `x` 加数字 `1`？
2. 为什么 `Fmt.g` 要先判断 NaN 和无穷大？

<details>
<summary>参考答案</summary>

1. 规则是“名字以字母开头，后面可以跟字母和数字”，扫到字母就进入“读名字”的分支，一直读到不是字母数字为止，所以 `x1` 整个是一个名字。这叫“最长匹配”。
2. `new BigDecimal(v)` 不能表示 NaN 和无穷大，会抛 `NumberFormatException`；而 C 的 `printf` 会把它们打印成 `nan`、`inf`。先单独处理，既避免出错，也和 C++ 版保持一致。

</details>

[← 异常](09-exceptions.md) · [目录](../README.md) · 下一课：[包、访问控制和测试 →](11-testing.md)
