"""第 10 课：字符串和文本处理。

LP 文件是纯文本。minicplex 先把文本切成一个个“记号”（数字、名字、运算符），再按语法拼成模型；
输出结果时又要把数字排成整齐的表格。这一课把这两件事各做一个迷你版。
运行：python3 python/tutorial/run.py 10
"""
import unicodedata

from check import lesson, eq, raises, done


def tokenize(text):
    """把 "2 x + 3.5 y <= 12" 切成 ["2", "x", "+", "3.5", "y", "<=", "12"]。
    规则：空格跳过；数字由 0-9 和 . 组成；名字由字母、数字和 _ 组成（字母开头）；
    "<=" ">=" 是两个字符的运算符；"+" "-" "=" 是一个字符的。别的字符 raise ValueError。
    提示：用下标 i 一个个往前走，while i < len(text)；ch.isdigit()、ch.isalpha()、ch.isalnum()。"""
    # >>>
    out, i = [], 0
    while i < len(text):
        ch = text[i]
        if ch.isspace():
            i += 1
        elif ch.isdigit() or ch == ".":
            j = i
            while j < len(text) and (text[j].isdigit() or text[j] == "."):
                j += 1
            out.append(text[i:j])
            i = j
        elif ch.isalpha() or ch == "_":
            j = i
            while j < len(text) and (text[j].isalnum() or text[j] == "_"):
                j += 1
            out.append(text[i:j])
            i = j
        elif text[i:i + 2] in ("<=", ">="):
            out.append(text[i:i + 2])
            i += 2
        elif ch in "+-=":
            out.append(ch)
            i += 1
        else:
            raise ValueError(f"不认识的字符：{ch!r}")
    return out
    # <<<


def parse_bound(line):
    """解析一行上下界："x <= 5" → ("x", "<=", 5.0)。用 tokenize，再检查是不是正好 3 个记号。不对就 raise ValueError。"""
    # >>>
    toks = tokenize(line)
    if len(toks) != 3 or toks[1] not in ("<=", ">=", "="):
        raise ValueError(f"看不懂这一行：{line}")
    return (toks[0], toks[1], float(toks[2]))
    # <<<


def format_row(name, value):
    """排成一行表格：名字左对齐占 10 格，数值右对齐占 8 格、保留 2 位小数。
    f-string 的格式：f"{name:<10}{value:>8.2f}"。"""
    # >>>
    return f"{name:<10}{value:>8.2f}"
    # <<<


def display_width(s):
    """字符串在屏幕上占几格：中文（以及全角符号）一个字占 2 格，英文、数字占 1 格。
    提示：unicodedata.east_asian_width(ch) 返回 "W" 或 "F" 时是宽字符（占 2 格）。"""
    # >>>
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in s)
    # <<<


def pad(s, width):
    """在右边补空格，让 s 在屏幕上正好占 width 格（已经够宽就原样返回）。f"{s:<10}" 按字符数补，中文会歪；这里按显示宽度补。"""
    # >>>
    return s + " " * max(0, width - display_width(s))
    # <<<


def report(values):
    """values 是 {名字: 值}。每个值一行（用 format_row），按名字排序，最后一行是 "合计"，用换行 "\\n".join 连起来。"""
    # >>>
    lines = [format_row(k, values[k]) for k in sorted(values)]
    lines.append(format_row("合计", sum(values.values())))
    return "\n".join(lines)
    # <<<


lesson("第 10 课：字符串和文本处理")
eq("切分一条约束", ["2", "x", "+", "3.5", "y", "<=", "12"], lambda: tokenize("2 x + 3.5 y <= 12"))
eq("没有空格也能切", ["x1", ">=", "0.5"], lambda: tokenize("x1>=0.5"))
eq("名字里可以有下划线和数字", ["make_drill_w1", "=", "30"], lambda: tokenize("make_drill_w1 = 30"))
raises("不认识的字符报错", ValueError, lambda: tokenize("x * 2"))
eq('parse_bound("y >= 2.5")', ("y", ">=", 2.5), lambda: parse_bound("y >= 2.5"))
raises("parse_bound 遇到不完整的行报错", ValueError, lambda: parse_bound("x <="))
eq("format_row", "cake          3.00", lambda: format_row("cake", 3))
eq("report", "bread         1.50\ncake          3.00\n合计            4.50", lambda: report({"cake": 3, "bread": 1.5}))
eq('display_width("abc")', 3, lambda: display_width("abc"))
eq('display_width("数据库")：每个汉字占 2 格', 6, lambda: display_width("数据库"))
eq('display_width("Python课")', 8, lambda: display_width("Python课"))
eq('pad("运筹学", 8) 补到 8 格', "运筹学  ", lambda: pad("运筹学", 8))
eq('pad("Python", 8)', "Python  ", lambda: pad("Python", 8))
done()
