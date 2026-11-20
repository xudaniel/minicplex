#!/usr/bin/env python3
"""从参考答案生成练习文件。

solutions/ 里的每个文件中，# >>> 和 # <<< 之间是答案。生成练习时把这一段换成
raise NotImplementedError("TODO")，其余内容原样保留；check.py 原样复制。

“找 bug”题：答案后面跟一行 # === 和一段注释掉的“有 bug 的版本”，练习里放的就是这个版本：

    # >>>
    for x in nums:          ← 正确答案
    # ===
    # for x in nums[1:]:    ← 练习里的版本（去掉行首的 "# "）
    # <<<

    python3 python/tutorial/make_exercises.py           # 重新生成 exercises/
    python3 python/tutorial/make_exercises.py --check   # 只检查 exercises/ 是否和答案同步（CI 用）
    python3 python/tutorial/make_exercises.py --lang en [--check]   # 英文版（en/ 目录）
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
LANG = "en" if "--lang" in sys.argv and sys.argv[sys.argv.index("--lang") + 1] == "en" else "zh"
ROOT = HERE / "en" if LANG == "en" else HERE
SRC = ROOT / "solutions"
DST = ROOT / "exercises"
TODO_LINE = {"zh": 'raise NotImplementedError("TODO")  # ← 在这里写你的代码',
             "en": 'raise NotImplementedError("TODO")  # ← write your code here'}[LANG]
BUG_LINE = {"zh": "# 🐞 下面这段有 bug：找出来，改好", "en": "# 🐞 the code below has a bug: find it and fix it"}[LANG]
BLOCK = re.compile(r"^([ \t]*)# >>>\n.*?^[ \t]*# <<<\n", re.S | re.M)


def _replace(m: re.Match) -> str:
    indent, block = m.group(1), m.group(0)
    if "# ===\n" not in block:
        return f"{indent}{TODO_LINE}\n"
    lines = []
    for ln in block.split("# ===\n", 1)[1].splitlines():
        if ln.strip().startswith("# <<<"):
            continue
        body = ln[len(indent):]
        if not body.startswith("#"):
            raise ValueError(f"有 bug 的版本每一行都要注释掉：{ln!r}")
        lines.append(indent + body[2:] if body.startswith("# ") else indent + body[1:])
    return f"{indent}{BUG_LINE}\n" + "\n".join(lines) + "\n"


def make(text: str) -> str:
    return BLOCK.sub(_replace, text)


def blank_names(text: str):
    """练习里每个挖空（或“找 bug”）的地方属于哪个函数，按出现顺序。
    块缩进在函数里面时，属于上面最近的 def；块从行首开始（整个函数都在块里）时，属于块里的第一个 def。"""
    lines = text.splitlines()
    names, cur = [], None
    for i, ln in enumerate(lines):
        m = re.match(r"\s*(?:def|class)\s+(\w+)", ln)
        if m:
            cur = m.group(1)
        if ln.strip() == "# >>>":
            if ln.startswith("#"):
                nxt = next(re.match(r"def\s+(\w+)", x) for x in lines[i + 1:] if re.match(r"def\s+(\w+)", x))
                names.append(nxt.group(1))
            else:
                names.append(cur)
    return names


def check_hints() -> list:
    """每个挖空的函数都要有提示，提示里也不能有多余的函数名。"""
    sys.path.insert(0, str(ROOT))
    from hints import HINTS
    problems = []
    for src in sorted(SRC.glob("[al][0-9][0-9]_*.py")):
        lid = src.name[:3]
        want = blank_names(src.read_text(encoding="utf-8"))
        have = [name for name, *_ in HINTS.get(lid, [])]
        if want != have:
            problems.append(f"{lid}：练习里是 {want}，hints.py 里是 {have}")
        for name, levels in HINTS.get(lid, []):
            if len(levels) < 2:
                problems.append(f"{lid}.{name}：至少要 2 级提示")
    return problems


def main() -> None:
    check = "--check" in sys.argv
    DST.mkdir(parents=True, exist_ok=True)
    stale = []
    files = sorted(SRC.glob("*.py"))
    for src in files:
        out = make(src.read_text(encoding="utf-8"))
        dst = DST / src.name
        if check:
            if not dst.exists() or dst.read_text(encoding="utf-8") != out:
                stale.append(dst.name)
        else:
            dst.write_text(out, encoding="utf-8", newline="\n")
    if check and stale:
        sys.exit("练习文件和答案不同步，请运行 python3 python/tutorial/make_exercises.py"
                 + (" --lang en" if LANG == "en" else "") + "：" + ", ".join(stale))
    problems = check_hints()
    if problems:
        sys.exit("hints.py 和练习对不上：\n  " + "\n  ".join(problems))
    print("练习文件已同步" if check else f"已生成 {len(files)} 个练习文件")


if __name__ == "__main__":
    main()
