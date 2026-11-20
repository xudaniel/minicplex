#!/usr/bin/env python3
"""Run the course exercises (works the same on Windows, macOS and Linux).

    python3 python/tutorial/en/run.py A01             run the exercise for basics lesson A1 (A01-A08: no experience needed)
    python3 python/tutorial/en/run.py 03              run the exercise for lesson 3 (your code)
    python3 python/tutorial/en/run.py 03 --hint       stuck? hints for lesson 3 (--hint 2 for more detail)
    python3 python/tutorial/en/run.py 03 --solution   run the reference solution for lesson 3
    python3 python/tutorial/en/run.py all             progress table: which lessons are done
    python3 python/tutorial/en/run.py all --verbose   run everything and print every lesson's details
    python3 python/tutorial/en/run.py all --solution  run every reference solution (used by CI: all must pass)
"""
import os
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
SUMMARY = re.compile(r"^-- passed (\d+), wrong (\d+), todo (\d+)", re.M)


def lesson_prefix(lesson: str) -> str:
    return ("a%02d" % int(lesson[1:])) if lesson[:1] in "aA" else ("l%02d" % int(lesson))


def find(folder: pathlib.Path, lesson: str):
    hits = sorted(folder.glob(lesson_prefix(lesson) + "_*.py"))
    return hits[0] if hits else None


def run_file(path: pathlib.Path, capture: bool = False):
    """Run one exercise file. With capture=True return (exit code, output); no grading summary means it crashed: code 2."""
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
        print(f"no hints for lesson {lesson}")
        return 2
    print(f"== Hints for lesson {lesson} (level {'1' if level == 1 else f'1-{level}'}) ==\n")
    for name, levels in HINTS[lid]:
        print(f"💡 {name}")
        for k, text in enumerate(levels[:level], 1):
            print(f"  {k}. " + text.replace("\n", "\n     "))
        print()
    more = max(len(levels) for _, levels in HINTS[lid]) > level
    print(f"Still stuck? Try --hint {level + 1}." if more else "That is every hint. If you are still stuck, --solution shows the reference answer.")
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
            failed, mark = 2, "💥 does not run (open it to see the error)"
        else:
            if code == 1 or (code != 0 and solution):
                failed = max(failed, 1)
            p, f_, t = (int(x) for x in m.groups())
            if f_ == 0 and t == 0:
                done += 1
                mark = "✅ done"
            else:
                bar = "█" * p + "░" * (f_ + t)
                mark = f"{bar}  {p}/{p + f_ + t}" + (f", {f_} wrong" if f_ else "") + (f", {t} to write" if t else "")
        lid = f.name[:3]
        name = ("A" + str(int(lid[1:]))) if lid[0] == "a" else lid[1:]
        rows.append(f"  {name:>3}  {f.stem[4:]:<18} {mark}")
    print("\n".join(rows))
    print(f"\nDone: {done} / {len(files)} lessons" + (". All done 🎉" if done == len(files) else ""))
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
        print(f"no lesson {lesson} (try A01, A1, 03 or 3)")
        return 2
    if hint_level:
        return show_hints(lesson, hint_level)
    return run_file(f)[0]


if __name__ == "__main__":
    sys.exit(main())
