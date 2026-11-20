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
    except Exception as e:  # noqa: BLE001  学生代码里出什么错都要接住
        err = f"抛出了异常 {type(e).__name__}: {e}"
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
        return None if ok else f"期望 {expected!r}，实际 {a!r}"
    _run(what, check)


def near(what, expected, actual):
    """检查两个小数足够接近（相对误差 1e-6）。"""
    def check():
        a = actual()
        ok = isinstance(a, (int, float)) and abs(a - expected) <= 1e-6 * (1 + abs(expected))
        return None if ok else f"期望约等于 {expected!r}，实际 {a!r}"
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
        except Exception as e:  # noqa: BLE001
            return None if isinstance(e, error_type) else f"抛出了 {type(e).__name__}：{e}"
        return f"没有抛出 {error_type.__name__}"
    _run(what, check)


def done():
    """打印汇总并退出。有错误时退出码 1，有没写完的退出码 3，全对是 0。"""
    print(f"-- 通过 {_pass}，不对 {_fail}，没写 {_todo}" + ("。全部完成 🎉" if _fail == 0 and _todo == 0 else ""))
    sys.exit(1 if _fail else 3 if _todo else 0)


__all__ = ["lesson", "that", "eq", "near", "raises", "done"]
