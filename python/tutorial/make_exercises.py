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
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "solutions"
DST = HERE / "exercises"
BLOCK = re.compile(r"^([ \t]*)# >>>\n.*?^[ \t]*# <<<\n", re.S | re.M)


def _replace(m: re.Match) -> str:
    indent, block = m.group(1), m.group(0)
    if "# ===\n" not in block:
        return f'{indent}raise NotImplementedError("TODO")  # ← 在这里写你的代码\n'
    lines = []
    for ln in block.split("# ===\n", 1)[1].splitlines():
        if ln.strip().startswith("# <<<"):
            continue
        body = ln[len(indent):]
        if not body.startswith("#"):
            raise ValueError(f"有 bug 的版本每一行都要注释掉：{ln!r}")
        lines.append(indent + body[2:] if body.startswith("# ") else indent + body[1:])
    return f"{indent}# 🐞 下面这段有 bug：找出来，改好\n" + "\n".join(lines) + "\n"


def make(text: str) -> str:
    return BLOCK.sub(_replace, text)


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
        sys.exit("练习文件和答案不同步，请运行 python3 python/tutorial/make_exercises.py：" + ", ".join(stale))
    print("练习文件已同步" if check else f"已生成 {len(files)} 个练习文件")


if __name__ == "__main__":
    main()
