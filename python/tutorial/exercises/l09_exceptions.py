"""第 9 课：异常。

minicplex 读 LP 文件时，格式不对会 raise LpParseError（它是 ValueError 的子类），命令行程序再用
try / except 接住，打印 "error: ..."，而不是吐出一大段 Traceback。这一课练习抛出和接住异常。
运行：python3 python/tutorial/run.py 09
"""
import os
import tempfile

from check import lesson, eq, raises, that, done
from minicplex import LpParseError, read_file


def parse_amount(text):
    """把 "12.5元" 或 " 7 " 这样的文字变成数字：去掉两边空格和结尾的“元”，再 float()。
    转不了时 raise ValueError，信息里要带上原文，例如 "不是金额：abc"。"""
    # TODO text.strip()；s.endswith("元") / s[:-1]；try: float(s) except ValueError: raise ValueError(...) from None
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def safe_ratio(a, b):
    """a / b；b 是 0 时返回 None（接住 ZeroDivisionError）。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def try_read(path):
    """用 minicplex 读 LP 文件。成功返回 ("ok", 变量个数)；文件格式错返回 ("bad", 错误信息)；
    其它错误（例如文件不存在）返回 ("missing", 错误信息)。
    提示：read_file 打不开文件时也会抛 LpParseError，信息以 "cannot open file" 开头；可以先用 os.path.exists 判断。"""
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def write_and_read(text):
    """把 text 写进一个临时文件，再用 try_read 读，最后（不管成功还是出错）都把文件删掉。用 try / finally。"""
    fd, path = tempfile.mkstemp(suffix=".lp")
    raise NotImplementedError("TODO")  # ← 在这里写你的代码


def message_of(code):
    """运行 code()，返回它抛出的异常的信息。"""
    try:
        code()
    except ValueError as e:
        return str(e)
    return "（没有抛异常）"


GOOD = "Maximize\n obj: x + y\nSubject To\n c: x + 2 y <= 4\nEnd\n"
BAD = "Maximize\n obj: x +\nSubject To\n c: x >= 1\nEnd\n"

lesson("第 9 课：异常")
eq('parse_amount("12.5元")', 12.5, lambda: parse_amount("12.5元"))
eq('parse_amount(" 7 ")', 7.0, lambda: parse_amount(" 7 "))
raises('parse_amount("abc") 报 ValueError', ValueError, lambda: parse_amount("abc"))
eq("错误信息里带着原文", "不是金额：abc", lambda: message_of(lambda: parse_amount("abc")))
eq("safe_ratio(6, 3)", 2.0, lambda: safe_ratio(6, 3))
eq("safe_ratio(1, 0) 是 None", None, lambda: safe_ratio(1, 0))
eq("读一个正确的模型：2 个变量", ("ok", 2), lambda: write_and_read(GOOD))
eq("读一个写错的模型：bad", "bad", lambda: write_and_read(BAD)[0])
that("错误信息里有行号（LP parse error (line 3): ...）", lambda: "line 3" in write_and_read(BAD)[1])
eq("文件不存在：missing", "missing", lambda: try_read("no-such-file.lp")[0])
done()
