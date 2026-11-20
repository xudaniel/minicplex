// 在 Web Worker 里运行 Python（Pyodide）。放在 Worker 里，学生写出死循环时网页也不会卡住：主页面直接结束这个 Worker 就行。
const VERSION = "314.0.8";
const CDNS = [
  `https://cdn.jsdelivr.net/pyodide/v${VERSION}/full/`,
  `https://fastly.jsdelivr.net/npm/pyodide@${VERSION}/`,
  `https://unpkg.com/pyodide@${VERSION}/`,
];

let pyodide = null;

// pyodidePath：和网站放在一起的那一份（打不开 CDN 时也能用）；英文版在 /python/en/，共用 /python/pyodide/
async function boot(files, selfHosted, pyodidePath, override) {
  const sources = override ? [override] : selfHosted ? [pyodidePath || "./pyodide/", ...CDNS] : CDNS;
  let lastError = null;
  for (const base of sources) {
    try {
      const url = new URL(base, self.location.href).href;
      const { loadPyodide } = await import(url + "pyodide.mjs");
      pyodide = await loadPyodide({ indexURL: url });
      break;
    } catch (e) {
      lastError = e;
    }
  }
  if (!pyodide) throw lastError || new Error("Pyodide failed to load");
  pyodide.setStdout({ batched: (s) => postMessage({ type: "out", text: s }) });
  pyodide.setStderr({ batched: (s) => postMessage({ type: "out", text: s }) });
  for (const [path, text] of Object.entries(files)) {
    const full = "/course/python/" + path;
    pyodide.FS.mkdirTree(full.slice(0, full.lastIndexOf("/")));
    pyodide.FS.writeFile(full, text);
  }
  pyodide.runPython(`
import sys
sys.path[:0] = ["/course/python", "/course/python/tutorial/lib"]
sys.dont_write_bytecode = True
`);
}

const RUNNER = `
import sys, traceback

HINTS_ZH = {
    "IndentationError": "缩进不对：同一段代码要对齐，函数、if、for 里面的代码要多缩进 4 个空格。",
    "TabError": "缩进里混用了 Tab 和空格，统一用空格。",
    "SyntaxError": "语法写错了：检查括号和引号是否配对、冒号有没有漏、是不是用了中文标点。",
    "NameError": "用到了一个没定义的名字：是不是拼错了，或者忘了加引号？",
    "TypeError": "类型不对：比如文字和数字直接用 + 拼接，或者函数的参数个数不对。",
    "ZeroDivisionError": "除以 0 了。",
    "IndexError": "下标越界了：列表有 n 个元素时，最后一个是 [n - 1]。",
    "KeyError": "字典里没有这个键：可以先用 in 判断，或者用 .get()。",
    "AttributeError": "这个对象没有这个属性或方法：是不是拼错了？",
    "RecursionError": "函数无限地调用自己了。",
}

HINTS_EN = {
    "IndentationError": "Wrong indentation: lines in the same block must line up, and code inside a function, if or for is indented 4 more spaces.",
    "TabError": "Tabs and spaces are mixed in the indentation; use spaces only.",
    "SyntaxError": "Something is written wrong: check that brackets and quotes are paired, no colon is missing, and no curly quotes slipped in.",
    "NameError": "A name is used that was never defined: is it misspelt, or did you forget the quotes?",
    "TypeError": "The wrong type: for example joining text and a number with +, or calling a function with the wrong number of arguments.",
    "ZeroDivisionError": "Division by 0.",
    "IndexError": "Index out of range: in a list of n items, the last one is [n - 1].",
    "KeyError": "That key isn't in the dictionary: check with in first, or use .get().",
    "AttributeError": "This object has no such attribute or method: is it misspelt?",
    "RecursionError": "A function keeps calling itself forever.",
}

LANG = "zh"
FILE = "练习.py"

def _report(e):
    name = type(e).__name__
    en = LANG == "en"
    print()
    if isinstance(e, SyntaxError) and e.filename == FILE:
        if en:
            print(f"❗ {'Indentation' if isinstance(e, IndentationError) else 'Syntax'} error on line {e.lineno}: {e.msg}")
        else:
            print(f"❗ 第 {e.lineno} 行有{ '缩进' if isinstance(e, IndentationError) else '语法' }错误：{e.msg}")
        if e.text:
            print("    " + e.text.rstrip("\\n"))
            if e.offset:
                print("    " + " " * (e.offset - 1) + "^")
    else:
        frames = [f for f in traceback.extract_tb(e.__traceback__) if f.filename == FILE]
        if en:
            where = f"on line {frames[-1].lineno}" if frames else "while running"
            print(f"❗ Error {where}: {name}: {e}")
        else:
            where = f"第 {frames[-1].lineno} 行" if frames else "运行时"
            print(f"❗ {where}出错：{name}: {e}")
        if frames and frames[-1].line:
            print("    " + frames[-1].line)
    hints = HINTS_EN if en else HINTS_ZH
    if name in hints:
        print("💡 " + hints[name])

def _run(code):
    for mod in [m for m in sys.modules if m == "check"]:
        del sys.modules[mod]
    g = {"__name__": "__main__"}
    try:
        exec(compile(code, FILE, "exec"), g)
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 0
    except BaseException as e:
        _report(e)
        return 2
    return 0
`;

self.onmessage = async (ev) => {
  const msg = ev.data;
  try {
    if (msg.type === "boot") {
      await boot(msg.files, msg.selfHosted, msg.pyodidePath, msg.override);
      pyodide.runPython(RUNNER);
      if (msg.lang === "en") pyodide.runPython('LANG = "en"\nFILE = "exercise.py"');
      postMessage({ type: "ready" });
    } else if (msg.type === "run") {
      const run = pyodide.globals.get("_run");
      const code = run(msg.code);
      run.destroy();
      postMessage({ type: "done", code });
    }
  } catch (e) {
    postMessage({ type: "error", text: String(e && e.message ? e.message : e) });
  }
};
