"""网页版 Python 课的端到端测试：在真浏览器里把每一课的参考答案和练习各跑一遍，再试语法错误、运行错误、
死循环 + 停止、自动保存、手机布局。

    python python/tutorial/web/test_site.py http://localhost:8765/python/ _site/python/course.json
"""
import json, sys, time
from playwright.sync_api import sync_playwright

BASE = sys.argv[1]
course = json.load(open(sys.argv[2], encoding="utf-8"))
fails = []

def run_code(page, code, timeout=120000):
    page.evaluate("c => { const t = document.getElementById('code'); t.value = c; t.dispatchEvent(new Event('input')); }", code)
    page.click("#btnRun")
    page.wait_for_selector("#btnRun:not([hidden])", timeout=timeout)
    return page.inner_text("#status"), page.inner_text("#output")

with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width": 1280, "height": 860})
    logs = []
    page.on("console", lambda m: logs.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: logs.append(str(e)))
    t0 = time.time()
    page.goto(BASE + "#a01")
    page.wait_for_function("document.getElementById('status').textContent.includes('准备好了')", timeout=120000)
    print(f"pyodide ready in {time.time() - t0:.1f}s")
    for L in course["lessons"]:
        page.goto(BASE + "#" + L["id"])
        t = time.time()
        st, out = run_code(page, L["solution"])
        ok = "全部通过" in st and "❌" not in out
        print(f"{L['id']} solution {'OK ' if ok else 'BAD'} {time.time() - t:5.1f}s  {st[:40]}")
        if not ok: fails.append((L["id"], "solution", st, out[-500:]))
        st, out = run_code(page, L["exercise"])
        ok = ("没写" in st or "不对" in st) and "❗" not in out   # “找 bug”题的练习本来就是 ❌
        if not ok: fails.append((L["id"], "exercise", st, out[-500:]))
    # progress shown on home
    page.goto(BASE + "#")
    print("home:", page.inner_text("#progress"))
    marks = page.locator(".cards .done", has_text="✅").count()
    print("done marks:", marks)
    if marks != len(course["lessons"]): fails.append(("home", f"{marks} done marks", "", ""))
    # syntax error, runtime error, infinite loop + stop
    page.goto(BASE + "#a01")
    st, out_syntax = run_code(page, "from check import *\ndef f(:\n    pass\n")
    print("syntax:", out_syntax.strip().splitlines()[:4])
    st, out_runtime = run_code(page, 'from check import *\nprint("a" + 1)\n')
    print("runtime:", out_runtime.strip().splitlines()[-3:])
    page.evaluate("c => { const t = document.getElementById('code'); t.value = c; }", "while True:\n    pass\n")
    page.click("#btnRun"); page.wait_for_timeout(7000)
    print("while running:", page.inner_text("#status"))
    page.click("#btnStop")
    page.wait_for_timeout(4000)
    st_after_stop, out = run_code(page, course["lessons"][0]["solution"])
    print("after stop, rerun:", st_after_stop[:30])
    # 提示面板：一级一级地给
    page.goto(BASE + "#a02")
    page.click("#btnHint")
    page.locator("#hintList .more").first.click()
    lvl1 = page.locator("#hintList .lvl").count()
    page.locator("#hintList .more").first.click()
    lvl2 = page.locator("#hintList .lvl").count()
    print("hint levels shown:", lvl1, lvl2)
    if (lvl1, lvl2) != (1, 2): fails.append(("hints", f"{lvl1} {lvl2}", "", ""))
    # 常见错误的 💡 说明：A2 里把 // 写成 /
    wrong = [L for L in course["lessons"] if L["id"] == "a02"][0]["solution"].replace("money // price", "money / price")
    st, out = run_code(page, wrong)
    print("mistake hint:", [ln for ln in out.splitlines() if "💡" in ln][:1])
    if "要整数时用 //" not in out: fails.append(("mistake hint", out[-300:], "", ""))
    # saved code persists after reload
    page.evaluate("c => { const t = document.getElementById('code'); t.value = c; t.dispatchEvent(new Event('input')); }", "# my code\n")
    page.wait_for_timeout(500); page.reload(); page.wait_for_selector("#code")
    print("persisted:", page.input_value("#code") == "# my code\n")
    # 手机：目录、课文和练习两个标签页
    m = b.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
    m.goto(BASE + "#"); m.wait_for_selector("#stage0 a")
    m.goto(BASE + "#l05"); m.wait_for_selector("#article h1")
    m.click("#tabCode"); m.wait_for_selector("#code", state="visible")
    if not m.is_hidden("#article"): fails.append(("mobile", "tabs", "", ""))
    print("console errors:", logs[:5])
    b.close()
for name, value, want in [("syntax", out_syntax, "语法错误"), ("runtime", out_runtime, "TypeError"),
                          ("after stop", st_after_stop, "全部通过")]:
    if want not in value: fails.append((name, value, "", ""))
if logs: fails.append(("console", " | ".join(logs[:5]), "", ""))
print("FAILS:", len(fails))
for f in fails: print(f)
sys.exit(1 if fails else 0)
