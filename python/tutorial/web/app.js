// 网页版 Python 课：目录、课文、编辑器、在 Web Worker 里运行判分。所有进度只存在本机浏览器里（localStorage）。
(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const params = new URLSearchParams(location.search);
  let course = null;
  let current = null;        // 当前课
  let worker = null;         // 运行 Python 的 Worker
  let workerReady = null;    // Promise：Worker 准备好了
  let running = false;
  const LANG = document.documentElement.lang.startsWith("en") ? "en" : "zh";
  const T = {
    zh: {
      start: `从 <a href="#a01">入门 A1</a> 开始；学过编程的话可以直接从 <a href="#l01">第 1 课</a> 开始。`,
      allDone: (n) => `🎉 ${n} 节全部完成！`,
      progress: (n, total, next) => `已完成 ${n} / ${total} 节 · <a href="#${next.id}">继续：${label(next.id)} ${shortTitle(next.title)} →</a>`,
      siteTitle: "用 minicplex 学 Python",
      homeTitle: "用 minicplex 学 Python · 在线练习",
      lessonDone: "✅ 这一课你已经完成了。",
      writeThenRun: "写完点 ▶ 运行判分（Ctrl + Enter）。",
      preparing: "正在准备 Python 运行环境（第一次大约需要 5～15 秒，之后就快了）…",
      workerError: (m) => "Python 运行环境出错了（" + (m || "未知错误") + "）。请刷新页面；如果一直这样，换一个新版浏览器试试。",
      ready: (s) => `Python 准备好了（${s} 秒）。写完点 ▶ 运行判分。`,
      loadFailed: (m) => "Python 运行环境加载失败：" + m + "。请检查网络后刷新页面。",
      running: "运行中…",
      slow: (s) => `运行了 ${s} 秒还没结束……如果是写出了死循环，点 ■ 停止。`,
      passedFirst: "🎉 全部通过，这一课完成了！",
      passed: "🎉 全部通过！",
      nextLesson: (L) => ` 下一课：${label(L.id)} ${shortTitle(L.title)} →`,
      wrong: (f, t) => `有 ${f} 项不对：看看 ❌ 那几行，期望值和实际值差在哪里。` + (t !== "0" ? `另外还有 ${t} 项没写。` : ""),
      todo: (t) => `还有 ${t} 项没写：找到代码里的 TODO。`,
      stopped: "已停止。",
      stoppedOut: "■ 已停止。",
      crashed: "程序没能运行完：看输出里 ❗ 那一行，它会告诉你第几行出了什么错。",
      hintFirst: "看第 1 级提示",
      hintMore: (k) => `再给一点（第 ${k} 级）`,
      courseFailed: "课程加载失败，请刷新页面重试。",
      confirmReset: "恢复成最初的练习？你写的代码会被清掉。",
      confirmAnswer: "先自己试试？看答案之前，至少运行一次、看看哪里不对。\n\n确定要看参考答案吗？",
      confirmUse: "用参考答案替换你的代码？",
    },
    en: {
      start: `Start with <a href="#a01">Basics A1</a>; if you've done some programming, you can start at <a href="#l01">lesson 1</a>.`,
      allDone: (n) => `🎉 All ${n} lessons done!`,
      progress: (n, total, next) => `${n} / ${total} lessons done · <a href="#${next.id}">Continue: ${label(next.id)} ${shortTitle(next.title)} →</a>`,
      siteTitle: "Learn Python with minicplex",
      homeTitle: "Learn Python with minicplex · online exercises",
      lessonDone: "✅ You've already finished this lesson.",
      writeThenRun: "When you're done, click ▶ Run & check (Ctrl + Enter).",
      preparing: "Getting Python ready (about 5–15 seconds the first time, quick after that)…",
      workerError: (m) => "Something went wrong with Python (" + (m || "unknown error") + "). Please reload the page; if it keeps happening, try a recent browser.",
      ready: (s) => `Python is ready (${s} s). When you're done, click ▶ Run & check.`,
      loadFailed: (m) => "Python failed to load: " + m + ". Check your connection and reload the page.",
      running: "Running…",
      slow: (s) => `Still running after ${s} seconds… if you wrote an infinite loop, click ■ Stop.`,
      passedFirst: "🎉 All passed: lesson complete!",
      passed: "🎉 All passed!",
      nextLesson: (L) => ` Next: ${label(L.id)} ${shortTitle(L.title)} →`,
      wrong: (f, t) => `${f} wrong: look at the ❌ lines to see how the expected and actual values differ.` + (t !== "0" ? ` ${t} still to write as well.` : ""),
      todo: (t) => `${t} still to write: find the TODOs in the code.`,
      stopped: "Stopped.",
      stoppedOut: "■ Stopped.",
      crashed: "The program didn't finish: the ❗ line in the output tells you which line went wrong and how.",
      hintFirst: "Show hint 1",
      hintMore: (k) => `A bit more (hint ${k})`,
      courseFailed: "The course failed to load; please reload the page.",
      confirmReset: "Restore the original exercise? Your code will be cleared.",
      confirmAnswer: "Try it yourself first? Before looking at the answer, run your code at least once and see what's wrong.\n\nShow the answer anyway?",
      confirmUse: "Replace your code with the answer?",
    },
  }[LANG];

  // ---------------------------------------------------------------- 本地存储（隐私模式等情况下可能不可用）
  const PREFIX = LANG === "en" ? "mcpy:en:" : "mcpy:";   // 中英文版的代码和进度分开存
  const store = {
    get(k) { try { return localStorage.getItem(PREFIX + k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(PREFIX + k, v); } catch (e) { /* 不保存也能用 */ } },
    del(k) { try { localStorage.removeItem(PREFIX + k); } catch (e) { /* ignore */ } },
  };
  const isDone = (id) => store.get("done:" + id) === "1";

  // ---------------------------------------------------------------- 目录
  function label(id) { return id[0] === "a" ? "A" + Number(id.slice(1)) : String(Number(id.slice(1))).padStart(2, "0"); }
  function shortTitle(t) { return t.replace(/^(入门 A\d+|第 \d+ 课)：|^(Basics A\d+|Lesson \d+): /, ""); }

  function renderHome() {
    const stageOf = (id) => (id[0] === "a" ? 0 : Number(id.slice(1)) <= 12 ? 1 : 2);
    for (const [stage, el] of [[0, $("stage0")], [1, $("stage1")], [2, $("stage2")]]) {
      el.innerHTML = "";
      for (const L of course.lessons.filter((x) => stageOf(x.id) === stage)) {
        const li = document.createElement("li");
        const a = document.createElement("a");
        a.href = "#" + L.id;
        a.innerHTML = `<span class="num"></span><span class="t"></span><span class="done"></span>`;
        a.querySelector(".num").textContent = label(L.id);
        a.querySelector(".t").textContent = shortTitle(L.title);
        a.querySelector(".done").textContent = isDone(L.id) ? "✅" : "";
        li.appendChild(a);
        el.appendChild(li);
      }
    }
    const n = course.lessons.filter((L) => isDone(L.id)).length;
    const next = course.lessons.find((L) => !isDone(L.id));
    $("progress").innerHTML = n === 0 ? T.start
      : n === course.lessons.length ? T.allDone(n)
      : T.progress(n, course.lessons.length, next);
  }

  // ---------------------------------------------------------------- 课文和编辑器
  function showLesson(L) {
    current = L;
    const i = course.lessons.indexOf(L);
    const prev = course.lessons[i - 1], next = course.lessons[i + 1];
    setNav($("navPrev"), prev);
    setNav($("navNext"), next);
    document.title = `${L.title} · ${T.siteTitle}`;
    $("article").innerHTML = `<h1></h1>` + L.html;
    $("article").querySelector("h1").textContent = L.title;
    $("article").scrollTop = 0;
    window.scrollTo(0, 0);
    $("fileName").textContent = L.file;
    setCode(store.get("code:" + L.id) ?? L.exercise);
    $("output").textContent = "";
    $("answerBox").hidden = true;
    $("hintBox").hidden = true;
    $("btnHint").hidden = !(L.hints && L.hints.length);
    setStatus(isDone(L.id) ? T.lessonDone : T.writeThenRun, isDone(L.id));
    ensureWorker();
  }
  function setNav(a, L) {
    if (L) { a.href = "#" + L.id; a.removeAttribute("aria-disabled"); a.title = L.title; }
    else { a.href = "#"; a.setAttribute("aria-disabled", "true"); }
  }

  const code = () => $("code");
  function setCode(text) { code().value = text; updateGutter(); }
  function updateGutter() {
    const n = code().value.split("\n").length;
    let s = "";
    for (let i = 1; i <= n; i++) s += i + "\n";
    $("gutter").textContent = s;
    $("gutter").scrollTop = code().scrollTop;
  }
  let saveTimer = 0;
  function onInput() {
    updateGutter();
    clearTimeout(saveTimer);
    saveTimer = setTimeout(() => store.set("code:" + current.id, code().value), 300);
  }

  // Tab 缩进 4 个空格；回车保持缩进，冒号结尾再多缩进一层；Shift+Tab 减少缩进
  function onKeyDown(e) {
    const ta = code();
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); run(); return; }
    if (e.key === "Tab") {
      e.preventDefault();
      const { selectionStart: s, selectionEnd: t, value: v } = ta;
      const lineStart = v.lastIndexOf("\n", s - 1) + 1;
      if (e.shiftKey) {
        const m = v.slice(lineStart).match(/^ {1,4}/);
        if (m) { ta.setRangeText("", lineStart, lineStart + m[0].length, "end"); ta.setSelectionRange(Math.max(lineStart, s - m[0].length), Math.max(lineStart, t - m[0].length)); }
      } else if (s !== t && v.slice(s, t).includes("\n")) {
        const block = v.slice(lineStart, t).replace(/^/gm, "    ");
        ta.setRangeText(block, lineStart, t, "select");
      } else {
        ta.setRangeText("    ", s, t, "end");
      }
      onInput();
    } else if (e.key === "Enter" && !e.isComposing) {
      e.preventDefault();
      const { selectionStart: s, selectionEnd: t, value: v } = ta;
      const lineStart = v.lastIndexOf("\n", s - 1) + 1;
      const line = v.slice(lineStart, s);
      let indent = line.match(/^ */)[0];
      if (/:\s*(#.*)?$/.test(line)) indent += "    ";
      ta.setRangeText("\n" + indent, s, t, "end");
      onInput();
    }
  }

  // ---------------------------------------------------------------- 运行
  function setStatus(text, ok = false) { $("status").textContent = text; $("status").className = "status" + (ok ? " ok" : ""); }

  function ensureWorker() {
    if (workerReady) return workerReady;
    worker = new Worker("worker.mjs?v=" + course.version, { type: "module" });
    const t0 = performance.now();
    if (!running) setStatus(T.preparing);
    worker.onerror = (e) => {
      setStatus(T.workerError(e.message));
      if (running) finishRun(2);
    };
    workerReady = new Promise((resolve, reject) => {
      worker.onmessage = (ev) => {
        if (ev.data.type === "ready") {
          worker.onmessage = onWorkerMessage;
          if (!running && current) setStatus(isDone(current.id) ? T.lessonDone : T.ready(((performance.now() - t0) / 1000).toFixed(1)), isDone(current.id));
          resolve();
        } else if (ev.data.type === "error") {
          setStatus(T.loadFailed(ev.data.text));
          workerReady = null;
          reject(new Error(ev.data.text));
        }
      };
      worker.postMessage({ type: "boot", files: course.files, selfHosted: course.selfHostedPyodide, pyodidePath: course.pyodidePath,
                          override: params.get("pyodide"), lang: LANG });
    });
    return workerReady;
  }

  function appendOutput(text) {
    const out = $("output");
    for (const line of text.split("\n")) {
      const span = document.createElement("span");
      span.textContent = line + "\n";
      if (line.startsWith("✅")) span.className = "ok";
      else if (line.startsWith("❌")) span.className = "bad";
      else if (line.startsWith("⏳")) span.className = "todo";
      else if (line.startsWith("❗")) span.className = "err";
      else if (line.startsWith("-- ")) span.className = "sum";
      else if (line.trimStart().startsWith("💡")) span.className = "hint";
      out.appendChild(span);
    }
    out.scrollTop = out.scrollHeight;
  }

  let runTimer = 0;
  function onWorkerMessage(ev) {
    const m = ev.data;
    if (m.type === "out") appendOutput(m.text);
    else if (m.type === "done" || m.type === "error") {
      if (m.type === "error") appendOutput("❗ " + m.text);
      finishRun(m.type === "done" ? m.code : 2);
    }
  }

  async function run() {
    if (running || !current) return;
    running = true;
    store.set("code:" + current.id, code().value);
    $("output").textContent = "";
    $("btnRun").hidden = true;
    $("btnStop").hidden = false;
    if (window.matchMedia("(max-width: 860px)").matches) $("output").scrollIntoView({ behavior: "smooth", block: "nearest" });
    try {
      await ensureWorker();
    } catch (e) {
      finishRun(2);
      return;
    }
    setStatus(T.running);
    const t0 = performance.now();
    runTimer = setInterval(() => {
      const s = (performance.now() - t0) / 1000;
      if (s > 5) setStatus(T.slow(s.toFixed(0)));
    }, 1000);
    worker.postMessage({ type: "run", code: code().value });
  }

  function finishRun(exitCode) {
    clearInterval(runTimer);
    running = false;
    $("btnRun").hidden = false;
    $("btnStop").hidden = true;
    const text = $("output").textContent;
    const m = text.match(/-- 通过 (\d+)，不对 (\d+)，没写 (\d+)/) || text.match(/-- passed (\d+), wrong (\d+), todo (\d+)/);
    if (exitCode === 0 && m && m[2] === "0" && m[3] === "0") {
      const first = !isDone(current.id);
      store.set("done:" + current.id, "1");
      const i = course.lessons.indexOf(current);
      const next = course.lessons[i + 1];
      setStatus(first ? T.passedFirst : T.passed, true);
      if (next) {
        const a = document.createElement("a");
        a.href = "#" + next.id;
        a.textContent = T.nextLesson(next);
        $("status").appendChild(a);
      }
    } else if (m) {
      const [_, p, f, t] = m;
      setStatus(f !== "0" ? T.wrong(f, t) : T.todo(t));
    } else if (exitCode === "stopped") {
      setStatus(T.stopped);
    } else {
      setStatus(T.crashed);
    }
  }

  function stop() {
    if (!running) return;
    worker.terminate();
    worker = null;
    workerReady = null;
    appendOutput(T.stoppedOut);
    finishRun("stopped");
    ensureWorker();  // 重新准备一个，下次运行不用等太久
  }

  // ---------------------------------------------------------------- 提示：每个函数一级一级地给
  function renderHints() {
    const box = $("hintList");
    box.innerHTML = "";
    for (const [name, levels] of current.hints) {
      const key = `hint:${current.id}:${name}`;
      const shown = Number(store.get(key) || 0);
      const div = document.createElement("div");
      div.className = "fn";
      div.innerHTML = `<code class="name"></code>`;
      div.querySelector(".name").textContent = name;
      for (let k = 0; k < shown && k < levels.length; k++) {
        const p = document.createElement("div");
        p.className = "lvl";
        p.textContent = `${k + 1}. ${levels[k]}`;
        div.appendChild(p);
      }
      if (shown < levels.length) {
        const b = document.createElement("button");
        b.className = "btn ghost more";
        b.textContent = shown === 0 ? T.hintFirst : T.hintMore(shown + 1);
        b.onclick = () => { store.set(key, String(shown + 1)); renderHints(); };
        div.appendChild(b);
      }
      box.appendChild(div);
    }
  }

  // ---------------------------------------------------------------- 路由
  function route() {
    const id = location.hash.slice(1);
    const L = course.lessons.find((x) => x.id === id);
    $("home").hidden = !!L;
    $("lesson").hidden = !L;
    $("lessonNav").hidden = !L;
    document.body.classList.toggle("in-lesson", !!L);
    if (L) showLesson(L);
    else { current = null; document.title = T.homeTitle; renderHome(); window.scrollTo(0, 0); }
    const other = $("langSwitch");
    if (other) other.href = other.getAttribute("href").split("#")[0] + (L ? "#" + L.id : "");
  }

  function setTab(codeTab) {
    $("lesson").classList.toggle("show-code", codeTab);
    $("tabRead").classList.toggle("active", !codeTab);
    $("tabCode").classList.toggle("active", codeTab);
    window.scrollTo(0, 0);
  }

  async function init() {
    try {
      const res = await fetch("course.json?v=" + (document.querySelector('script[src^="app.js"]').src.split("v=")[1] || ""));
      course = await res.json();
    } catch (e) {
      $("loading").textContent = T.courseFailed;
      return;
    }
    $("loading").hidden = true;
    code().addEventListener("input", onInput);
    code().addEventListener("keydown", onKeyDown);
    code().addEventListener("scroll", () => { $("gutter").scrollTop = code().scrollTop; });
    $("btnRun").onclick = run;
    $("btnStop").onclick = stop;
    $("btnReset").onclick = () => {
      if (confirm(T.confirmReset)) { setCode(current.exercise); store.del("code:" + current.id); $("output").textContent = ""; }
    };
    $("btnAnswer").onclick = () => {
      if (!$("answerBox").hidden) { $("answerBox").hidden = true; return; }
      if (!isDone(current.id) && !confirm(T.confirmAnswer)) return;
      $("answerCode").textContent = current.solution;
      $("answerBox").hidden = false;
      $("answerBox").scrollIntoView({ behavior: "smooth", block: "nearest" });
    };
    $("btnHideAnswer").onclick = () => { $("answerBox").hidden = true; };
    $("btnHint").onclick = () => {
      if (!$("hintBox").hidden) { $("hintBox").hidden = true; return; }
      renderHints();
      $("hintBox").hidden = false;
      $("answerBox").hidden = true;
      $("hintBox").scrollIntoView({ behavior: "smooth", block: "nearest" });
    };
    $("btnHideHint").onclick = () => { $("hintBox").hidden = true; };
    $("btnUseAnswer").onclick = () => {
      if (confirm(T.confirmUse)) { setCode(current.solution); onInput(); $("answerBox").hidden = true; }
    };
    $("tabRead").onclick = () => setTab(false);
    $("tabCode").onclick = () => setTab(true);
    window.addEventListener("hashchange", () => { setTab(false); route(); });
    route();
  }
  init();
})();
