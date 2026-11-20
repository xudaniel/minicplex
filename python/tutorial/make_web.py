#!/usr/bin/env python3
"""生成网页版 Python 课（GitHub Pages 用）：课文 + 编辑器 + 在浏览器里运行判分（Pyodide）。
中文版在 python/，英文版（来自 en/）在 python/en/，两个版本共用一份 Pyodide。

    pip install markdown
    python3 python/tutorial/make_web.py                    # 输出到 python/tutorial/web/_site/
    python3 python/tutorial/make_web.py --out DIR [--pyodide DIR]

--pyodide 指向解压后的 Pyodide npm 包（package/ 目录）时，会把 Python 运行时一起放进网站，
这样打不开 CDN 的地方也能用；不给的话，网页从 jsDelivr / unpkg 加载。
"""
import argparse
import importlib.util
import json
import pathlib
import re
import shutil
import subprocess

import markdown

HERE = pathlib.Path(__file__).resolve().parent          # python/tutorial
REPO = HERE.parents[1]
GITHUB = "https://github.com/xudaniel/minicplex"
WEB = HERE / "web"
PYODIDE_FILES = ["pyodide.mjs", "pyodide.asm.mjs", "pyodide.asm.wasm", "python_stdlib.zip", "pyodide-lock.json"]


LANGS = {
    "zh": {"root": HERE, "out": "python", "nav": r"\s*\[(目录|←)", "online": "**在线做：**",
           "exercise": (r"\*\*练习：\*\* `python3 python/tutorial/run.py \w+`", "**练习：** 就在本页的编辑器里"),
           "do_it": r"(## \d+\. 动手\n\n)"},
    "en": {"root": HERE / "en", "out": "python/en", "nav": r"\s*\[(Contents|←)", "online": "**Do it online:**",
           "exercise": (r"\*\*Exercise:\*\* `python3 python/tutorial/en/run.py \w+`", "**Exercise:** right here in the editor on this page"),
           "do_it": r"(## \d+\. Your turn\n\n)"},
}


def load_hints(root):
    spec = importlib.util.spec_from_file_location("hints_" + root.name, root / "hints.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.HINTS


def lesson_files(root):
    """课文 .md 和练习 .py 一一对应：a1-hello.md ↔ a01_hello.py，03-lists.md ↔ l03_lists.py。"""
    out = []
    for md in sorted((root / "lessons").glob("*.md"), key=lambda p: (p.name[0] != "a", p.name)):
        m = re.match(r"(a)?(\d+)-", md.name)
        lid = ("a" if m.group(1) else "l") + "%02d" % int(m.group(2))
        ex = next((root / "exercises").glob(lid + "_*.py"))
        out.append((lid, md, ex))
    return out


def rewrite_links(text, md_path, ids_by_file):
    def fix(m):
        target = m.group(1)
        if target.startswith(("http://", "https://", "#", "mailto:")):
            return m.group(0)
        path, _, frag = target.partition("#")
        name = pathlib.PurePosixPath(path).name
        if path in ("../README.md", "README.md"):
            return "](#)"
        if name in ids_by_file and "/" not in path:
            return f"](#{ids_by_file[name]})"
        full = (md_path.parent / path).resolve()
        rel = full.relative_to(REPO).as_posix()
        kind = "tree" if full.is_dir() else "blob"
        return f"]({GITHUB}/{kind}/main/{rel}" + (f"#{frag}" if frag else "") + ")"
    return re.sub(r"\]\(([^)\s]+)\)", fix, text)


DO_IT = {"zh": """在本页的编辑器里，把每个 `raise NotImplementedError("TODO")` 换成你的代码（注意保持缩进），
然后点 **▶ 运行判分**（或按 Ctrl + Enter）。✅ 是对了，❌ 是不对（会告诉你期望什么、实际得到什么，常见错误还会给一句 💡 原因），⏳ 是还没写。
卡住了就点 **💡 提示**：每个函数有两级提示，先给方向，再给接近代码的写法。
标着 **🤔 先猜后跑** 的题：先别运行，把你猜的结果写在 `return` 后面，再运行看看猜得对不对。
你写的代码会自动保存在这个浏览器里，下次打开还在。
""", "en": """In the editor on this page, replace each `raise NotImplementedError("TODO")` with your code (keep the indentation),
then click **▶ Run & check** (or press Ctrl + Enter). ✅ means right, ❌ means wrong (it shows what was expected and what you got, and common mistakes get a 💡 explanation), ⏳ means not written yet.
Stuck? Click **💡 Hint**: each function has two levels of hints, first a direction, then something close to the code.
Tasks marked **🤔 guess, then run**: don't run anything yet; write your guess after `return`, then run and see whether you were right.
Your code is saved in this browser automatically and will still be here next time.
"""}


def lesson_html(md_path, ids_by_file, lang):
    L = LANGS[lang]
    text = md_path.read_text(encoding="utf-8")
    title = re.match(r"#\s*(.+)", text).group(1).strip()
    lines = [ln for ln in text.splitlines()
             if not re.match(L["nav"], ln) and L["online"] not in ln]          # 去掉上下导航和指向自己的链接
    text = "\n".join(lines[1:]) + "\n"                                              # 去掉 H1，网页自己显示标题
    text = re.sub(L["exercise"][0], L["exercise"][1], text)
    # “动手”一节换成网页版的说法
    text = re.sub(L["do_it"] + r".*?(?=\n## |\Z)", lambda m: m.group(1) + DO_IT[lang], text, flags=re.S)
    text = re.sub(r"^(> \*\*.*)\n(?=> \*\*)", r"\1  \n", text, flags=re.M)              # 课首说明框：每项单独一行
    text = rewrite_links(text, md_path, ids_by_file)
    text = text.replace("<details>", '<details markdown="1">')
    html = markdown.markdown(text, extensions=["fenced_code", "tables", "md_in_html"])
    html = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', html)
    return title, html


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(WEB / "_site"))
    ap.add_argument("--pyodide", help="解压后的 pyodide npm 包目录（可选）")
    args = ap.parse_args()
    out = pathlib.Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    site = out / "python"

    try:
        version = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO, capture_output=True,
                                 text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        version = "dev"
    pkg = {f"minicplex/{p.name}": p.read_text(encoding="utf-8") for p in sorted((REPO / "python/minicplex").glob("*.py"))}
    counts = []
    for lang, L in LANGS.items():
        root = L["root"]
        dst = out / L["out"]
        dst.mkdir(parents=True, exist_ok=True)
        hints = load_hints(root)
        files = lesson_files(root)
        ids_by_file = {md.name: lid for lid, md, _ in files}
        lessons = []
        for lid, md, ex in files:
            title, html = lesson_html(md, ids_by_file, lang)
            sol = root / "solutions" / ex.name
            lessons.append({"id": lid, "title": title, "html": html,
                            "exercise": ex.read_text(encoding="utf-8"),
                            "solution": sol.read_text(encoding="utf-8"),
                            "file": ex.name, "hints": hints.get(lid, [])})
        files_ = dict(pkg)
        files_["tutorial/lib/check.py"] = (root / "solutions/check.py").read_text(encoding="utf-8")
        course = {"version": version, "lang": lang, "github": GITHUB, "lessons": lessons, "files": files_,
                  "selfHostedPyodide": bool(args.pyodide), "pyodidePath": "./pyodide/" if lang == "zh" else "../pyodide/"}
        (dst / "course.json").write_text(json.dumps(course, ensure_ascii=False), encoding="utf-8")
        for name in ("index.html", "app.js", "app.css", "worker.mjs"):
            src = WEB / ("index.en.html" if lang == "en" and name == "index.html" else name)
            (dst / name).write_text(src.read_text(encoding="utf-8").replace("__VERSION__", version), encoding="utf-8")
        counts.append(f"{lang} {len(lessons)} 课")
    (out / "index.html").write_text(
        '<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=python/">'
        '<title>minicplex</title><a href="python/">用 minicplex 学 Python</a> · <a href="python/en/">Learn Python with minicplex</a>\n', encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    if args.pyodide:
        want = re.search(r'const VERSION = "([^"]+)"', (WEB / "worker.mjs").read_text(encoding="utf-8")).group(1)
        have = json.loads((pathlib.Path(args.pyodide) / "package.json").read_text(encoding="utf-8"))["version"]
        if have != want:
            raise SystemExit(f"Pyodide 版本不一致：worker.mjs 要 {want}，--pyodide 给的是 {have}")
        dst = site / "pyodide"
        dst.mkdir()
        for name in PYODIDE_FILES:
            shutil.copy(pathlib.Path(args.pyodide) / name, dst / name)
    size = sum(p.stat().st_size for p in out.rglob("*") if p.is_file())
    print(f"网站已生成：{out}（{'，'.join(counts)}，{size / 1e6:.1f} MB）")


if __name__ == "__main__":
    main()
