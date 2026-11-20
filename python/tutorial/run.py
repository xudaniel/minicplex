#!/usr/bin/env python3
"""运行教程练习（Windows、macOS、Linux 都一样）。

    python3 python/tutorial/run.py A01             运行入门第 A1 课的练习（零基础，A01～A08）
    python3 python/tutorial/run.py 03              运行第 3 课的练习（你写的代码）
    python3 python/tutorial/run.py 03 --solution   运行第 3 课的参考答案
    python3 python/tutorial/run.py all --solution  运行全部参考答案（CI 用：必须全部通过）
    python3 python/tutorial/run.py all             看看你一共完成了多少
"""
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent


def find(folder: pathlib.Path, lesson: str):
    if lesson[:1] in "aA":
        prefix = "a%02d_" % int(lesson[1:])
    else:
        prefix = "l%02d_" % int(lesson)
    hits = sorted(folder.glob(prefix + "*.py"))
    return hits[0] if hits else None


def run_file(path: pathlib.Path) -> int:
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    return subprocess.call([sys.executable, str(path)], env=env)


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--solution"]
    solution = "--solution" in sys.argv
    folder = HERE / ("solutions" if solution else "exercises")
    if not args:
        print(__doc__.strip())
        return 2
    lesson = args[0]
    if lesson == "all":
        failed = 0
        files = sorted(folder.glob("a*_*.py")) + sorted(folder.glob("l*_*.py"))
        for f in files:
            code = run_file(f)
            if code == 1 or (code != 0 and solution):
                failed = 1
            print()
        return failed
    try:
        f = find(folder, lesson)
    except ValueError:
        f = None
    if f is None:
        print(f"找不到第 {lesson} 课（例如 A01、A1、03 或 3）")
        return 2
    return run_file(f)


if __name__ == "__main__":
    sys.exit(main())
