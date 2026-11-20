#!/usr/bin/env python3
"""运行教程练习（Windows、macOS、Linux 都一样）。

    python3 python/tutorial/run.py A01             运行入门第 A1 课的练习（零基础，A01～A08）
    python3 python/tutorial/run.py 03              运行第 3 课的练习（你写的代码）
    python3 python/tutorial/run.py 03 --hint       卡住了？看第 3 课的提示（--hint 2 看更具体的）
    python3 python/tutorial/run.py 03 --solution   运行第 3 课的参考答案
    python3 python/tutorial/run.py all             进度表：每一课完成了没有
    python3 python/tutorial/run.py all --verbose   全部运行，并打印每一课的详细结果
    python3 python/tutorial/run.py all --solution  运行全部参考答案（CI 用：必须全部通过）
"""
import os
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
SUMMARY = re.compile(r"^-- 通过 (\d+)，不对 (\d+)，没写 (\d+)", re.M)


def lesson_prefix(lesson: str) -> str:
    return ("a%02d" % int(lesson[1:])) if lesson[:1] in "aA" else ("l%02d" % int(lesson))


def find(folder: pathlib.Path, lesson: str):
    hits = sorted(folder.glob(lesson_prefix(lesson) + "_*.py"))
    return hits[0] if hits else None


def run_file(path: pathlib.Path, capture: bool = False):
    """运行一个练习文件。capture=True 时返回 (退出码, 输出)；没有打印出判分汇总就算“跑不起来”，退出码记为 2。"""
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    if not capture:
        return subprocess.call([sys.executable, str(path)], env=env), ""
    p = subprocess.run([sys.executable, str(path)], env=env, capture_output=True, text=True, encoding="utf-8")
    out = p.stdout + p.stderr
    return (p.returncode if SUMMARY.search(p.stdout) else 2), out


def show_hints(lesson: str, level: int) -> int:
    sys.path.insert(0, str(HERE))
    from hints import HINTS
    lid = lesson_prefix(lesson)
    if lid not in HINTS:
        print(f"第 {lesson} 课没有提示")
        return 2
    print(f"== 第 {lesson} 课的提示（第 {'1' if level == 1 else f'1～{level}'} 级）==\n")
    for name, levels in HINTS[lid]:
        print(f"💡 {name}")
        for k, text in enumerate(levels[:level], 1):
            print(f"  {k}. " + text.replace("\n", "\n     "))
        print()
    more = max(len(levels) for _, levels in HINTS[lid]) > level
    print(f"还卡着？试试 --hint {level + 1}。" if more else "提示都给完了。实在想不出来，可以用 --solution 看参考答案。")
    return 0


def progress(folder: pathlib.Path, solution: bool, verbose: bool) -> int:
    files = sorted(folder.glob("a[0-9][0-9]_*.py")) + sorted(folder.glob("l[0-9][0-9]_*.py"))
    failed, done, rows = 0, 0, []
    for f in files:
        code, out = run_file(f, capture=True)
        if verbose:
            print(out)
        m = SUMMARY.search(out)
        if code not in (0, 1, 3):
            failed, mark = 2, "💥 跑不起来（打开看看报错）"
        else:
            if code == 1 or (code != 0 and solution):
                failed = max(failed, 1)
            p, f_, t = (int(x) for x in m.groups())
            if f_ == 0 and t == 0:
                done += 1
                mark = "✅ 完成"
            else:
                bar = "█" * p + "░" * (f_ + t)
                mark = f"{bar}  {p}/{p + f_ + t}" + (f"，{f_} 项不对" if f_ else "") + (f"，{t} 项没写" if t else "")
        lid = f.name[:3]
        name = ("A" + str(int(lid[1:]))) if lid[0] == "a" else lid[1:]
        rows.append(f"  {name:>3}  {f.stem[4:]:<18} {mark}")
    print("\n".join(rows))
    print(f"\n已完成 {done} / {len(files)} 课" + ("。全部完成 🎉" if done == len(files) else ""))
    return failed


def main() -> int:
    argv = sys.argv[1:]
    solution = "--solution" in argv
    verbose = "--verbose" in argv
    hint_level = 0
    if "--hint" in argv:
        k = argv.index("--hint")
        hint_level = 1
        if k + 1 < len(argv) and argv[k + 1].isdigit():
            hint_level = int(argv[k + 1])
            del argv[k + 1]
    args = [a for a in argv if not a.startswith("--")]
    folder = HERE / ("solutions" if solution else "exercises")
    if not args:
        print(__doc__.strip())
        return 2
    lesson = args[0]
    if lesson == "all":
        return progress(folder, solution, verbose)
    try:
        f = find(folder, lesson)
    except ValueError:
        f = None
    if f is None:
        print(f"找不到第 {lesson} 课（例如 A01、A1、03 或 3）")
        return 2
    if hint_level:
        return show_hints(lesson, hint_level)
    return run_file(f)[0]


if __name__ == "__main__":
    sys.exit(main())
