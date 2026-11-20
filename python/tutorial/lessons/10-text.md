# 第 10 课：字符串和文本处理

> **这一课学：** 用下标扫描文本（手写词法分析器）；`split`、`strip`、`join`；f-string 的格式说明符；`%` 格式化；拼接大量文本的正确姿势；中文的显示宽度
> **用到的代码：** [`lp_reader.py`](../../minicplex/lp_reader.py) 的 `_tokenize`、[`fmt.py`](../../minicplex/fmt.py)、[`model.py`](../../minicplex/model.py) 的 `to_lp`
> **练习：** `python3 python/tutorial/run.py 10`
> **在线做：** [打开网页版，不用安装](https://xudaniel.github.io/minicplex/python/#l10)

[← 异常](09-exceptions.md) · [目录](../README.md) · 下一课：[测试 →](11-testing.md)

## 1. 先切成记号

`c1: 2 x + 3.5 y <= 12` 对人来说一目了然，对程序来说只是一串字符。读 LP 文件的第一步是把它切成**记号**（token）：
`c1` `:` `2` `x` `+` `3.5` `y` `<=` `12`。[`lp_reader.py`](../../minicplex/lp_reader.py) 的 `_tokenize` 用一个下标 `i` 往前走：

```python
while i < n:
    c = src[i]
    if _is_ws(c):                 # 空白：跳过
        i += 1
        continue
    if _is_digit(src, i) or (c == "." and _is_digit(src, i + 1)):
        j = i
        while _is_digit(src, j):  # 数字：一直读到不是数字为止
            j += 1
        ...
        t.kind, t.s = NUM, src[i:j]
        i = j
    elif c in "<>=":              # <= 和 >= 是两个字符的运算符
        ...
```

这种“看一个字符决定接下来怎么读”的写法，几乎所有编程语言的编译器都在用。切好记号以后，语法分析就简单了：
“名字后面跟 `:` 就是约束名”“数字后面跟名字就是一项”。

## 2. 为什么不直接 split？

`"2 x + 3.5 y <= 12".split()` 看起来也能切，但 `x1>=0.5` 没有空格，`split` 就没办法了。LP 格式允许不写空格，所以要一个字符一个字符地扫。

## 3. 格式说明符

f-string 的大括号里，冒号后面可以写格式：

```python
f"{name:<10}"        # 左对齐，占 10 格
f"{value:>8.2f}"     # 右对齐，占 8 格，2 位小数
f"{n:5d}"            # 整数，占 5 格
f"{x:.6g}"           # 6 位有效数字，自动选择小数或科学计数法：1e-07、21、3.33333
f"{ratio:.1%}"       # 百分比：0.256 → 25.6%
```

minicplex 输出数字时一律用 `%g` 风格（[`fmt.py`](../../minicplex/fmt.py)）：

```python
def g(v, precision=6):
    """相当于 C 的 printf("%.{precision}g", v)。"""
    return "%.*g" % (precision, v)
```

这里用的是老式的 `%` 格式化（和 C 语言的 `printf` 一样），因为它的规则和 C++ 版完全相同，三个版本的输出才能一字不差。
新代码一般用 f-string 就好。

## 4. 拼很多段文字：先放列表，最后 join

[`model.py`](../../minicplex/model.py) 的 `to_lp` 要输出几百行：

```python
out = ["\\ Written by minicplex\n"]
...
out.append(f" {c.name}:")
...
return "".join(out)
```

不要在循环里 `s += "..."`：字符串不能改，每次 `+=` 都要复制一遍整个字符串，越来越慢。往列表里 `append`，最后一次性 `"".join(...)`，又快又清楚。

## 5. 中文和对齐

`f"{name:<6}"` 按**字符数**补空格，而一个汉字在屏幕上占两个英文字母宽，所以中英文混排时表格会歪：

```text
Python 4 学分        ← f"{name:<6}" 的结果
数据库    3 学分     ← 三个字只补了 3 个空格，却占了 6 格宽
```

办法是按**显示宽度**补空格。标准库的 `unicodedata.east_asian_width(ch)` 告诉你一个字符是不是“宽字符”（返回 `"W"` 或 `"F"`），
宽字符算 2 格，其余算 1 格。练习里要写 `display_width` 和 `pad`，第 12 课的选课表就用它对齐。

## 6. 动手

打开 [`exercises/l10_text.py`](../exercises/l10_text.py)：写一个迷你词法分析器、解析一行上下界、排一张小报表，再写按显示宽度对齐的 `pad`。运行 `python3 python/tutorial/run.py 10`。

## 7. 想一想

`tokenize("x2")` 应该得到 `["x2"]` 还是 `["x", "2"]`？`tokenize("2x")` 呢？

<details><summary>答案</summary>

`"x2"` 是一个名字（字母开头，后面可以有数字）；`"2x"` 是 `["2", "x"]`：先读到数字，数字读完了才是名字。
LP 格式正是这样规定的，所以 `2x + 3y` 不写空格也能读。规则要先想清楚，再写代码——这也是为什么一定要有测试（下一课）。

</details>

[← 异常](09-exceptions.md) · [目录](../README.md) · 下一课：[测试 →](11-testing.md)
