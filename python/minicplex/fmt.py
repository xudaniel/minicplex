"""数字格式：和 C 的 printf("%.Ng") 完全一样（Python 的 % 格式化本来就是这样）。"""
import sys


def g(v: float, precision: int = 6) -> str:
    """相当于 C 的 printf("%.{precision}g", v)。"""
    return "%.*g" % (precision, v)


def use_utf8_output() -> None:
    """让中文在任何系统上都能正常输出（Windows 的控制台默认不是 UTF-8）。"""
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
        except (AttributeError, ValueError):
            pass
