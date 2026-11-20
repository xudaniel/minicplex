#!/usr/bin/env python3
"""从参考答案生成练习文件。

solutions/ 里的每个文件中，// >>> 和 // <<< 之间是答案。生成练习时把这一段换成
throw new UnsupportedOperationException("TODO");，其余内容原样保留。

    python3 java/tutorial/make_exercises.py           # 重新生成 exercises/
    python3 java/tutorial/make_exercises.py --check   # 只检查 exercises/ 是否和答案同步（CI 用）
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "solutions" / "minicplex" / "tutorial"
DST = HERE / "exercises" / "minicplex" / "tutorial"
BLOCK = re.compile(r"^([ \t]*)// >>>\n.*?^[ \t]*// <<<\n", re.S | re.M)


def make(text: str) -> str:
    return BLOCK.sub(lambda m: f'{m.group(1)}throw new UnsupportedOperationException("TODO");  // ← 在这里写你的代码\n', text)


def main() -> None:
    check = "--check" in sys.argv
    DST.mkdir(parents=True, exist_ok=True)
    stale = []
    for src in sorted(SRC.glob("*.java")):
        out = make(src.read_text(encoding="utf-8"))
        dst = DST / src.name
        if check:
            if not dst.exists() or dst.read_text(encoding="utf-8") != out:
                stale.append(dst.name)
        else:
            dst.write_text(out, encoding="utf-8")
    if check and stale:
        sys.exit("练习文件和答案不同步，请运行 python3 java/tutorial/make_exercises.py：" + ", ".join(stale))
    print("练习文件已同步" if check else f"已生成 {len(list(SRC.glob('*.java')))} 个练习文件")


if __name__ == "__main__":
    main()
