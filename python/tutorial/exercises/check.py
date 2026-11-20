"""练习用的小小测试框架：每一项检查打印 ✅（通过）、❌（不对）或 ⏳（还没写）。

你不需要修改这个文件，但值得读一读：它用到了 lambda（第 8 课）和异常（第 9 课）。

    from check import lesson, eq, near, that, raises, done

    lesson("入门 A1：让程序说话")
    eq("greet('小明')", "你好，小明！", lambda: greet("小明"))
    done()
"""
import pathlib
import sys

# 不用安装 minicplex 也能 import：把仓库里的 python/ 目录加进搜索路径
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from minicplex import use_utf8_output  # noqa: E402

use_utf8_output()  # 中文在任何系统上都能正常显示

_pass = _fail = _todo = 0


def lesson(title):
    """打印本课标题。"""
    print(f"== {title} ==")


def _is_todo(e):
    return isinstance(e, NotImplementedError) and e.args == ("TODO",)


_PUNCT = str.maketrans("，。：；！？（）“”‘’", ",.:;!?()\"\"''")

_ERROR_HINTS = {
    "TypeError": "类型不对：比如文字和数字直接用 + 拼接、对 None 做运算，或者调用函数时参数个数不对。",
    "NameError": "用到了一个没定义的名字：是不是拼错了，或者忘了加引号？",
    "IndexError": "下标越界了：列表有 n 个元素时，最后一个是 [n - 1]。",
    "KeyError": "字典里没有这个键：可以先用 in 判断，或者用 .get()。",
    "ZeroDivisionError": "除以 0 了：是不是空列表求了平均？",
    "AttributeError": "这个对象没有这个属性或方法：是不是拼错了？如果对象是 None，多半是某个函数忘了 return。",
    "UnboundLocalError": "在给变量赋值之前就用了它：是不是忘了先写 total = 0 这样的初始值？",
    "RecursionError": "函数无限地调用自己了：递归要有一个不再调用自己的“出口”。",
}


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _why(expected, actual):
    """看看答案错在哪里，给一句常见原因（猜不出来就返回 None）。"""
    if actual is None and expected is not None:
        return "函数返回了 None：是不是忘了写 return，或者用 print 代替了 return？"
    if isinstance(expected, bool) and not isinstance(actual, bool):
        return "这里要的是 True 或 False。比较的结果本身就是 True/False，可以直接写 return a >= b。"
    if _num(expected) and _num(actual):
        if isinstance(expected, int) and isinstance(actual, float) and actual != int(actual):
            return "期望整数，你算出了小数：要整数时用 //（整除），不是 /。"
        if abs(expected - actual) == 1:
            return "差了 1：检查 range 的终点（range(1, n) 不包括 n）、< 和 <=，或者计数器的初始值。"
        if actual == -expected:
            return "符号反了：检查减法的顺序或者正负号。"
        if expected != 0 and abs(actual / expected - 1) < 1e-6:
            return "非常接近但不相等：小数有误差（第 2 课），比较小数要看“够不够近”。"
    if isinstance(expected, str) and isinstance(actual, str):
        if actual.strip() == expected.strip():
            return "只差在开头或结尾的空格、换行。"
        if actual.translate(_PUNCT) == expected.translate(_PUNCT):
            return "标点不一样：注意中文标点和英文标点（，和 ,  ：和 :）。"
        if actual.lower() == expected.lower():
            return "只差在大小写。"
        if actual.replace(" ", "") == expected.replace(" ", ""):
            return "只差在中间的空格。"
    if isinstance(expected, (list, tuple)) and isinstance(actual, (list, tuple)) and type(expected) is not type(actual):
        if list(expected) == list(actual):
            return f"内容对了，但类型不对：期望 {type(expected).__name__}，你给的是 {type(actual).__name__}。"
    if isinstance(expected, (list, tuple)) and isinstance(actual, (list, tuple)) and len(expected) == len(actual):
        if sorted(map(repr, expected)) == sorted(map(repr, actual)):
            return "元素都对，但顺序不对。"
    if isinstance(expected, (list, tuple)) and isinstance(actual, (list, tuple)) and abs(len(expected) - len(actual)) == 1:
        return "少了或多了一个元素：检查循环的起点和终点。"
    return None


def _explain(err, expected, actual):
    hint = _why(expected, actual)
    return err + (f"\n   💡 {hint}" if hint else "")


def _run(what, check):
    global _pass, _fail, _todo
    try:
        err = check()
    except NotImplementedError as e:
        if not _is_todo(e):
            err = f"抛出了异常 {type(e).__name__}: {e}"
        else:
            _todo += 1
            print(f"⏳ {what}（还没写，找 TODO）")
            return
    except (Exception, SystemExit) as e:  # noqa: BLE001  学生代码里出什么错都要接住
        err = f"抛出了异常 {type(e).__name__}: {e}"
        if type(e).__name__ in _ERROR_HINTS:
            err += f"\n   💡 {_ERROR_HINTS[type(e).__name__]}"
    if err is None:
        _pass += 1
        print(f"✅ {what}")
    else:
        _fail += 1
        print(f"❌ {what}：{err}")


def that(what, cond):
    """检查一个条件为真。cond 是一个不带参数的函数（通常写成 lambda: ...）。"""
    _run(what, lambda: None if cond() else "条件不成立")


def eq(what, expected, actual):
    """检查 actual() == expected。"""
    def check():
        a = actual()
        if isinstance(expected, bool) or isinstance(a, bool):
            ok = a is expected  # True 和 1 不算一样
        else:
            ok = a == expected
        return None if ok else _explain(f"期望 {expected!r}，实际 {a!r}", expected, a)
    _run(what, check)


def near(what, expected, actual):
    """检查两个小数足够接近（相对误差 1e-6）。"""
    def check():
        a = actual()
        ok = isinstance(a, (int, float)) and abs(a - expected) <= 1e-6 * (1 + abs(expected))
        return None if ok else _explain(f"期望约等于 {expected!r}，实际 {a!r}", expected, a)
    _run(what, check)


def raises(what, error_type, code):
    """检查运行 code() 会抛出 error_type 类型的异常。"""
    def check():
        try:
            code()
        except NotImplementedError as e:
            if _is_todo(e):
                raise
            return None if issubclass(NotImplementedError, error_type) else f"抛出了 {type(e).__name__}"
        except (Exception, SystemExit) as e:  # noqa: BLE001  argparse 出错时用 SystemExit 退出
            return None if isinstance(e, error_type) else f"抛出了 {type(e).__name__}：{e}"
        return f"没有抛出 {error_type.__name__}"
    _run(what, check)


def done():
    """打印汇总并退出。有错误时退出码 1，有没写完的退出码 3，全对是 0。"""
    print(f"-- 通过 {_pass}，不对 {_fail}，没写 {_todo}" + ("。全部完成 🎉" if _fail == 0 and _todo == 0 else ""))
    sys.exit(1 if _fail else 3 if _todo else 0)


__all__ = ["lesson", "that", "eq", "near", "raises", "done"]
